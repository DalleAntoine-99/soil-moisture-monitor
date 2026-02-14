"""
Feature extraction avec ResNet-50
"""
import torch
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import numpy as np
from typing import Union, List

class ResNetFeatureExtractor:
    def __init__(self, model_name: str = "microsoft/resnet-50", device: str = "auto"):
        """
        Initialize ResNet-50 feature extractor
        
        Args:
            model_name: HuggingFace model identifier
            device: Device to use (auto, cpu, mps, cuda)
        """
        self.model_name = model_name
        
        # Auto-detect device
        if device == "auto":
            if torch.backends.mps.is_available():
                self.device = "mps"
            elif torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
        else:
            self.device = device
        
        print(f"Loading ResNet-50 on device: {self.device}")
        
        # Load processor and model
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        
        print("ResNet-50 loaded successfully!")
    
    def extract_features(self, image: Union[str, Image.Image]) -> np.ndarray:
        """
        Extract features from an image
        
        Args:
            image: Image path or PIL Image object
            
        Returns:
            Feature vector (numpy array)
        """
        # Load image if path
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        
        # Preprocess
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Extract features
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Global average pooling
            features = outputs.pooler_output.cpu().numpy()
        
        return features.flatten()
    
    def extract_batch_features(self, images: List[Union[str, Image.Image]]) -> np.ndarray:
        """
        Extract features from multiple images
        
        Args:
            images: List of image paths or PIL Images
            
        Returns:
            Feature matrix (num_images, feature_dim)
        """
        features_list = []
        
        for i, img in enumerate(images):
            if i % 100 == 0:
                print(f"Extracting features: {i}/{len(images)}")
            features = self.extract_features(img)
            features_list.append(features)
        
        return np.array(features_list)


if __name__ == "__main__":
    extractor = ResNetFeatureExtractor()
    print(f"✓ ResNet-50 Feature Extractor ready on {extractor.device}")
