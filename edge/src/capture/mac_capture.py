import cv2
import os
from datetime import datetime

# Créer le dossier de sauvegarde s'il n'existe pas
CAPTURE_DIR = "edge/captures"
os.makedirs(CAPTURE_DIR, exist_ok=True)

# Générer un nom de fichier avec timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"soil_image_{timestamp}.jpg"
filepath = os.path.join(CAPTURE_DIR, filename)

# Ouvrir la webcam (0 = caméra par défaut)
print("📷 Ouverture de la caméra...")
cap = cv2.VideoCapture(0)

# Vérifier que la caméra est bien ouverte
if not cap.isOpened():
    print("Erreur : impossible d'accéder à la caméra")
    exit(1)

# Capturer une image
ret, frame = cap.read()

if ret:
    cv2.imwrite(filepath, frame)
    print(f"Image capturée avec succès : {filepath}")
else:
    print("Erreur : impossible de capturer l'image")

# Fermer la caméra
cap.release()