"""
Predict soil moisture from image with confidence intervals
"""
import sys
from pathlib import Path
import joblib
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
from models.resnet_feature_extractor import ResNetFeatureExtractor

def predict_moisture(image_path: str, model_path: str = "ml/models/ridge_regressor_resnet_mapie.joblib"):
    """
    Predict moisture with confidence interval
    """
    # Load model
    print(f"�� Loading model from {model_path}...")
    model_data = joblib.load(model_path)
    ridge = model_data['ridge_regressor']
    quantile = model_data['confidence_quantile']
    config = model_data['config']
    
    # Extract features
    print(f"🔧 Extracting features from {image_path}...")
    extractor = ResNetFeatureExtractor(
        model_name=config['model']['name'],
        device=config['model']['device']
    )
    
    features = extractor.extract_features(image_path)
    features = np.array([features])
    
    # Predict
    print("🤖 Predicting...")
    prediction = ridge.predict(features)[0]
    lower = prediction - quantile
    upper = prediction + quantile
    
    return prediction, lower, upper

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", help="Path to soil image")
    args = parser.parse_args()
    
    pred, lower, upper = predict_moisture(args.image_path)
    
    print("\n" + "="*60)
    print("🌱 SOIL MOISTURE PREDICTION")
    print("="*60)
    print(f"📊 Prediction:    {pred:.1f}%")
    print(f"📈 95% CI:        [{lower:.1f}%, {upper:.1f}%]")
    print(f"⚠️  Uncertainty:   ±{(upper-lower)/2:.1f}%")
    print("="*60)
