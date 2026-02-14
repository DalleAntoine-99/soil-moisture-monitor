"""
Prediction avec ResNet-50 + Ridge + MAPIE (intervalles de confiance)
"""
import torch
import numpy as np
from PIL import Image
import joblib
from transformers import AutoImageProcessor, AutoModel
import os
import time

# ========= CONFIG =========
MODEL_NAME = "microsoft/resnet-50"
REGRESSOR_PATH = "ml/models/ridge_regressor_resnet_mapie.joblib"
CONFIDENCE_LEVEL = 0.95

# Auto-detect device
if torch.backends.mps.is_available():
    DEVICE = "mps"
elif torch.cuda.is_available():
    DEVICE = "cuda"
else:
    DEVICE = "cpu"

# ========= LOAD MODELS =========
print(f"Loading ResNet-50 on {DEVICE}...")
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
vision_model = AutoModel.from_pretrained(MODEL_NAME).to(DEVICE)
vision_model.eval()

print("Loading MAPIE regressor...")
if not os.path.exists(REGRESSOR_PATH):
    raise FileNotFoundError(f"Model not found: {REGRESSOR_PATH}")
mapie_regressor = joblib.load(REGRESSOR_PATH)

print("✓ Models loaded successfully!")

# ========= HELPER FUNCTIONS =========
def categorize_humidity(humidity: float) -> str:
    """Categorize humidity level"""
    if humidity < 30:
        return "dry"
    elif humidity < 60:
        return "moderate"
    else:
        return "wet"

# ========= PREDICT FUNCTION =========
def predict_image(image_path: str, confidence_level: float = CONFIDENCE_LEVEL) -> dict:
    """
    Predict soil humidity from image with confidence intervals
    
    Args:
        image_path: Path to image file
        confidence_level: Confidence level for prediction intervals (default: 0.95)
        
    Returns:
        Dictionary with prediction results including confidence intervals
    """
    try:
        start_time = time.time()
        
        # Load image
        image = Image.open(image_path).convert("RGB")
        
        # Preprocess
        inputs = processor(images=image, return_tensors="pt")
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        
        # Extract features
        with torch.no_grad():
            outputs = vision_model(**inputs)
            features = outputs.pooler_output.cpu().numpy()
        
        # Predict with confidence intervals
        alpha = 1 - confidence_level
        y_pred, y_pred_interval = mapie_regressor.predict(features, alpha=alpha)
        
        # Extract values
        humidity = float(np.clip(y_pred[0], 0, 100))
        lower_bound = float(np.clip(y_pred_interval[0, 0, 0], 0, 100))
        upper_bound = float(np.clip(y_pred_interval[0, 1, 0], 0, 100))
        interval_width = upper_bound - lower_bound
        
        # Categorize
        category = categorize_humidity(humidity)
        
        # Inference time
        inference_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "prediction": {
                "humidity": round(humidity, 2),
                "confidence_interval": {
                    "lower": round(lower_bound, 2),
                    "upper": round(upper_bound, 2),
                    "width": round(interval_width, 2)
                },
                "category": category,
                "confidence_level": confidence_level
            },
            "model_info": {
                "feature_extractor": MODEL_NAME,
                "regressor": "ridge-mapie",
                "version": "2.0.0"
            },
            "metadata": {
                "inference_time_ms": inference_time_ms,
                "device": DEVICE
            },
            "status": "success"
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


# ========= CLI TEST =========
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python predict_humidity.py <image_path> [confidence_level]")
        sys.exit(1)

    image_path = sys.argv[1]
    conf_level = float(sys.argv[2]) if len(sys.argv) > 2 else 0.95
    
    result = predict_image(image_path, conf_level)
    
    if result["status"] == "success":
        pred = result["prediction"]
        print(f"\n{'='*60}")
        print(f"✓ Predicted soil humidity: {pred['humidity']:.1f}%")
        print(f"  {int(pred['confidence_level']*100)}% CI: [{pred['confidence_interval']['lower']:.1f}%, {pred['confidence_interval']['upper']:.1f}%]")
        print(f"  Category: {pred['category']}")
        print(f"  Interval width: {pred['confidence_interval']['width']:.1f}%")
        print(f"  Inference time: {result['metadata']['inference_time_ms']} ms")
        print(f"{'='*60}\n")
    else:
        print(f"❌ Error: {result['error']}")
