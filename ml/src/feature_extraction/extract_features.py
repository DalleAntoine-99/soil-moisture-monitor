import os
import numpy as np
from PIL import Image
from tqdm import tqdm
import torch
from transformers import AutoImageProcessor, AutoModel

# ========= CONFIG =========
DATASET_ROOT = "ml/data/raw/Soil_Moisture_Dataset/Before Augmentation"
OUTPUT_DIR = "ml/data/processed"
MODEL_NAME = "facebook/dinov3-vits16-pretrain-lvd1689m"

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

LABEL_MAP = {
    "dry": 0,
    "moderate": 1,
    "wet": 2,
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========= LOAD MODEL =========
print("Loading DINOv3...")
processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME).to(DEVICE)
model.eval()

features = []
labels = []

# ========= PROCESS DATASET =========
for class_name, label in LABEL_MAP.items():
    class_dir = os.path.join(DATASET_ROOT, class_name)
    if not os.path.isdir(class_dir):
        raise FileNotFoundError(f"Missing directory: {class_dir}")

    images = [
        f for f in os.listdir(class_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    for img_name in tqdm(images, desc=f"Processing {class_name}"):
        img_path = os.path.join(class_dir, img_name)

        try:
            image = Image.open(img_path).convert("RGB")
        except Exception as e:
            print(f"Skipping {img_path}: {e}")
            continue

        inputs = processor(images=image, return_tensors="pt")
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            feat = outputs.last_hidden_state.mean(dim=1).squeeze(0).cpu().numpy()

        features.append(feat)
        labels.append(label)

# ========= SAVE =========
features = np.stack(features)
labels = np.array(labels)

np.save(os.path.join(OUTPUT_DIR, "features.npy"), features)
np.save(os.path.join(OUTPUT_DIR, "labels.npy"), labels)

print("Done.")
print(f"Features shape: {features.shape}")
print(f"Labels shape: {labels.shape}")
