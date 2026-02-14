from flask import Flask, request, jsonify
import os
import sys
from datetime import datetime

# Ajouter le répertoire racine au PYTHONPATH pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ml.src.inference.predict_humidity import predict_image

app = Flask(__name__)

# Dossier pour stocker les images uploadées
UPLOAD_FOLDER = "vm/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/predict", methods=["POST"])
def predict():
    # Vérifier qu'une image est envoyée
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    file = request.files["image"]
    
    # Vérifier que le fichier a un nom
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    
    # Sauvegarder l'image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"soil_{timestamp}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    print(f"Image reçue : {filepath}")
    
    # Faire l'inférence
    try:
        humidity = predict_image(filepath)
        
        # Classification en 3 niveaux
        if humidity < 33:
            label = "DRY"
        elif humidity < 67:
            label = "OPTIMAL"
        else:
            label = "WET"
        
        response = {
            "humidity_percentage": round(humidity, 2),
            "humidity_label": label,
            "timestamp": datetime.now().isoformat(),
            "image_path": filepath
        }
        
        print(f"Prédiction : {response}")
        return jsonify(response), 200
    
    except Exception as e:
        print(f"Erreur lors de l'inférence : {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "API is running"}), 200

if __name__ == "__main__":
    print("🚀 Démarrage de l'API Flask...")
    print("📡 API disponible sur : http://0.0.0.0:8900")
    app.run(host="0.0.0.0", port=8900, debug=True)
