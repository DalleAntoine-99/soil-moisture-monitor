import requests
import os
import glob

# URL de l'API (local pour le test)
API_URL = "http://localhost:8900/predict"

# Trouver la dernière image capturée
capture_dir = "edge/captures"
images = glob.glob(os.path.join(capture_dir, "*.jpg"))

if not images:
    print(f"Aucune image trouvée dans {capture_dir}")
    print("Lance d'abord : poetry run python edge/src/capture/mac_capture.py")
    exit(1)

# Prendre la plus récente
image_path = max(images, key=os.path.getctime)

# Envoyer l'image à l'API
print(f"📤 Envoi de l'image : {image_path}")
with open(image_path, "rb") as img:
    files = {"image": img}
    response = requests.post(API_URL, files=files)

# Afficher la réponse
if response.status_code == 200:
    print("Prédiction reçue :")
    result = response.json()
    print(f"   • Humidité : {result['humidity_percentage']}%")
    print(f"   • Label : {result['humidity_label']}")
    print(f"   • Timestamp : {result['timestamp']}")
else:
    print(f"Erreur {response.status_code} :")
    print(response.text)