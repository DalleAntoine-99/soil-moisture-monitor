"""
Training pipeline ResNet-50 + Ridge + Manual Confidence Intervals
"""
from pathlib import Path
import os
import yaml
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_predict
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib

# Import custom modules
import sys
sys.path.append(str(Path(__file__).parent.parent))
from models.resnet_feature_extractor import ResNetFeatureExtractor

def load_config(config_path: str = "ml/configs/resnet_config.yaml"):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    print("=" * 60)
    print("TRAINING RESNET-50 + RIDGE + MANUAL CI")
    print("=" * 60)
    
    # Load config
    config = load_config()
    
    # Load dataset
    print("\n📂 Loading dataset...")
    df = pd.read_csv(config['paths']['labels'])
    
    images = []
    labels = []
    
    for _, row in df.iterrows():
        img_path = os.path.join(config['paths']['dataset'], row['image_filename'])
        if os.path.exists(img_path):
            images.append(img_path)
            labels.append(row['humidity'])
    
    print(f"✓ Loaded {len(images)} images with labels")
    
    if len(images) == 0:
        print("❌ No images found! Check your dataset path and labels.csv")
        return
    
    # Extract features
    print("\n🔧 Extracting features with ResNet-50...")
    extractor = ResNetFeatureExtractor(
        model_name=config['model']['name'],
        device=config['model']['device']
    )
    
    features_list = []
    for i, img_path in enumerate(images):
        if i % 100 == 0:
            print(f"Extracting features: {i}/{len(images)}")
        
        feature = extractor.extract_features(img_path)
        features_list.append(feature)
    
    features = np.array(features_list)
    print(f"✓ Features shape: {features.shape}")
    
    # Convert to numpy arrays
    X = features
    y = np.array(labels)
    
    # Split data
    test_size = config['training']['test_size']
    random_state = config['training']['random_state']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    print(f"\n📊 Data split:")
    print(f"  Train: {len(X_train)} samples")
    print(f"  Test:  {len(X_test)} samples")
    
    # Train Ridge Regression
    print("\n🤖 Training Ridge Regression...")
    ridge_alpha = config['training']['ridge_alpha']
    ridge = Ridge(alpha=ridge_alpha, random_state=random_state)
    ridge.fit(X_train, y_train)
    print("✓ Ridge trained!")
    
    # Calibrate confidence intervals
    print("\n🔮 Calibrating confidence intervals (5-fold CV)...")
    y_train_cv = cross_val_predict(ridge, X_train, y_train, cv=5)
    residuals = np.abs(y_train - y_train_cv)
    
    confidence_level = config['training']['confidence_level']
    quantile = np.quantile(residuals, confidence_level)
    
    print(f"✓ {int(confidence_level*100)}% quantile: ±{quantile:.2f}%")
    
    # Evaluate on test set
    print("\n📈 Evaluating on test set...")
    
    y_pred = ridge.predict(X_test)
    y_lower = y_pred - quantile
    y_upper = y_pred + quantile
    
    # Metrics
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Coverage (% of true values within intervals)
    in_interval = (y_test >= y_lower) & (y_test <= y_upper)
    coverage = np.mean(in_interval)
    
    avg_width = quantile * 2
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Test RMSE:          {rmse:.2f}%")
    print(f"Test MAE:           {mae:.2f}%")
    print(f"Test R²:            {r2:.4f}")
    print(f"Coverage (95% CI):  {coverage:.3f} (target: {confidence_level:.3f})")
    print(f"Avg interval width: {avg_width:.2f}%")
    print("=" * 60)
    
    # Save model
    output_path = config['paths']['model_output']
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    joblib.dump({
        'ridge_regressor': ridge,
        'confidence_quantile': float(quantile),
        'config': config,
        'metrics': {
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'coverage': float(coverage),
            'avg_interval_width': float(avg_width)
        }
    }, output_path)
    
    print(f"\n✓ Model saved to: {output_path}")
    print("\n✅ Training completed successfully!")

if __name__ == "__main__":
    main()
