import torch
import numpy as np
from PIL import Image
import joblib
from transformers import AutoImageProcessor, AutoModel

# ========= CONFIG =========
MODEL_NAME = "facebook/dinov3-vits16-pretrain-lvd1689m"
REGRESSOR_PATH = "ml/models/ridge_regressor.joblib"

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

# Mapping regression -> % humidity
def prediction_to_humidity(pred):
    humidity = 32.5 * pred + 15
    return float(np.clip(humidity, 0, 100))

# ========= LOAD MODELS =========
print("Loading DINOv3...")
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
vision_model = AutoModel.from_pretrained(MODEL_NAME).to(DEVICE)
vision_model.eval()

print("Loading regressor...")
regressor = joblib.load(REGRESSOR_PATH)

# ========= PREDICT FUNCTION =========
def predict_image(image_path: str) -> float:
    image = Image.open(image_path).convert("RGB")

    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = vision_model(**inputs)
        features = outputs.last_hidden_state.mean(dim=1).cpu().numpy()

    pred = regressor.predict(features)[0]
    humidity = prediction_to_humidity(pred)

    return humidity

# ========= CLI TEST =========
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python predict_humidity.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    humidity = predict_image(image_path)

    print(f"Predicted soil humidity: {humidity:.1f}%")
