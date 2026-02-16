# 🏗️ **Architecture globale du projet IoT - Soil Moisture Monitor**

---

## 📊 **Vue d'ensemble de l'architecture complète**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ARCHITECTURE COMPLÈTE                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  EDGE DEVICE     │  HTTP   │   VM CLOUD       │  MQTT   │  THINGSBOARD    │
│  (Mac/RPi)       │────────▶│  tp-hadoop-12    │────────▶│  (Guy)          │
│                  │         │                  │         │                 │
│  TON TRAVAIL ✅  │         │  TON TRAVAIL ✅  │         │  TRAVAIL GUY ⏳ │
└──────────────────┘         └──────────────────┘         └─────────────────┘
```

---

## 🎯 **PARTIE 1 : TON TRAVAIL (Antoine) ✅**

### **A. Edge Device (Mac avec webcam)**

#### **Localisation :**
```
~/Desktop/Period_2/IOT/Projet/soil-moisture-monitor/
├── edge/
│   ├── src/capture/
│   │   └── mac_capture.py          ✅ Capture depuis webcam
│   └── captures/                    ✅ Images capturées localement
```

#### **Fonctionnalités implémentées :**
- ✅ **Capture d'images** depuis webcam (imagesnap)
- ✅ **Script automatisé** : capture_and_predict.sh
- ✅ **Envoi vers VM** : `scripts/test_vm_inference.sh`

---

### **B. ML Pipeline (Entraînement local)**

#### **Localisation :**
```
ml/
├── data/raw/Soil_Moisture_Dataset/  ✅ Dataset (12,634 images)
├── configs/
│   └── resnet_config.yaml           ✅ Configuration ResNet-50
├── src/
│   ├── models/
│   │   └── resnet_feature_extractor.py  ✅ Extracteur ResNet-50
│   ├── training/
│   │   └── train_resnet_regressor.py    ✅ Entraînement Ridge
│   └── inference/
│       └── predict_moisture.py          ✅ Script d'inférence
└── models/
    └── ridge_regressor_resnet_mapie.joblib  ✅ Modèle entraîné
```

#### **Résultats du modèle :**
- **RMSE** : 14.79%
- **MAE** : 11.23%
- **R²** : 0.7296
- **Intervalle de confiance** : ±30.7% (95% CI)

---

### **C. VM Cloud (Déploiement)**

#### **Localisation sur VM :**
```
ubuntu@tp-hadoop-12:~/soil_moisture/
├── models/
│   └── ridge_regressor_resnet.joblib    ✅ Modèle déployé
├── src/
│   ├── resnet_feature_extractor.py      ✅ Adapté pour CPU
│   ├── predict_moisture.py              ✅ Adapté pour CPU
│   └── __init__.py                      ✅
├── incoming/                            ✅ Images reçues du Mac
├── processed/                           ✅ Images traitées + résultats
├── logs/                                ✅ Logs des prédictions
│   └── prediction_YYYYMMDD_HHMMSS.txt
├── requirements.txt                     ✅ CPU-only (torch, transformers...)
├── venv/                                ✅ Python 3.11+ avec PyTorch CPU
└── predict.sh                           ✅ Script CLI pour tests
```

#### **Fonctionnalités implémentées :**
- ✅ **Réception d'images** via SCP
- ✅ **Inférence CPU-only** (ResNet-50 + Ridge)
- ✅ **Stockage des résultats** en `.txt` dans `logs/`
- ✅ **Archivage** des images dans `processed/`

#### **Scripts de déploiement :**
```bash
scripts/
├── deploy_to_vm.sh              ✅ Déploie modèle + code sur VM
├── test_vm_inference.sh         ✅ Test avec image du dataset
└── capture_and_predict.sh       ✅ Pipeline complète (capture → VM)
```

---

## 🔄 **PARTIE 2 : TRAVAIL DE GUY (À FAIRE) ⏳**

### **Interface Guy ↔ Ton travail**

#### **1. Point d'entrée pour Guy : Fichiers JSON**

**Proposition : Modifier `predict_moisture.py` pour exporter en JSON**

````python
# Sur la VM : ~/soil_moisture/src/predict_moisture.py
# Ajouter une fonction pour sauvegarder en JSON

import json
from datetime import datetime

def save_prediction_json(image_path, prediction, lower, upper):
    """Sauvegarde la prédiction au format JSON pour ThingsBoard"""
    timestamp = datetime.now()
    
    result = {
        "timestamp": timestamp.isoformat(),
        "timestamp_unix": int(timestamp.timestamp() * 1000),  # Pour ThingsBoard
        "image_path": str(image_path),
        "prediction": {
            "moisture_percent": round(float(prediction), 2),
            "lower_bound": round(float(lower), 2),
            "upper_bound": round(float(upper), 2),
            "uncertainty": round(float((upper - lower) / 2), 2)
        },
        "model_info": {
            "name": "ResNet-50 + Ridge Regression",
            "confidence_level": 0.95
        }
    }
    
    # Sauvegarder dans logs/predictions/
    json_dir = Path("logs/predictions")
    json_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = json_dir / f"prediction_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    return json_path
````

---

### **2. Architecture pour Guy**

```
~/soil_moisture/
├── logs/predictions/                    ⏳ Guy lira ces fichiers JSON
│   ├── prediction_20260214_153000.json
│   ├── prediction_20260214_154500.json
│   └── ...
└── api/                                 ⏳ À créer par Guy
    ├── mqtt_client.py                   ⏳ Client MQTT vers ThingsBoard
    ├── thingsboard_config.yaml          ⏳ Config ThingsBoard
    └── send_to_thingsboard.py           ⏳ Envoie les JSON vers TB
```

---

### **3. Format JSON pour ThingsBoard**

**Exemple de fichier généré par ton code :**

````json
{
  "timestamp": "2026-02-14T15:30:00.123456",
  "timestamp_unix": 1771071000123,
  "image_path": "/home/ubuntu/soil_moisture/processed/soil_20260214_153000.jpg",
  "prediction": {
    "moisture_percent": 48.5,
    "lower_bound": 17.8,
    "upper_bound": 79.2,
    "uncertainty": 30.7
  },
  "model_info": {
    "name": "ResNet-50 + Ridge Regression",
    "confidence_level": 0.95
  }
}
````

---

### **4. Ce que Guy devra faire**

#### **A. Créer un watcher de fichiers JSON**

````python
# api/send_to_thingsboard.py (à créer par Guy)
import time
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PredictionHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.json'):
            with open(event.src_path, 'r') as f:
                data = json.load(f)
            send_to_thingsboard(data)

def send_to_thingsboard(data):
    # Code MQTT de Guy ici
    pass

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(PredictionHandler(), "logs/predictions/", recursive=False)
    observer.start()
    observer.join()
````

---

#### **B. Client MQTT ThingsBoard**

````python
# api/mqtt_client.py (à créer par Guy)
import paho.mqtt.client as mqtt
import json
import yaml

def load_tb_config():
    with open("api/thingsboard_config.yaml", 'r') as f:
        return yaml.safe_load(f)

def send_telemetry(prediction_data):
    config = load_tb_config()
    
    client = mqtt.Client()
    client.username_pw_set(config['access_token'])
    client.connect(config['host'], config['port'])
    
    telemetry = {
        "moisture": prediction_data['prediction']['moisture_percent'],
        "uncertainty": prediction_data['prediction']['uncertainty'],
        "lower": prediction_data['prediction']['lower_bound'],
        "upper": prediction_data['prediction']['upper_bound'],
        "ts": prediction_data['timestamp_unix']
    }
    
    client.publish('v1/devices/me/telemetry', json.dumps(telemetry))
    client.disconnect()
````

---

## 📋 **Script de mise à jour pour ajouter l'export JSON**

````bash
cat > scripts/add_json_export.sh << 'EOF'
#!/bin/bash

VM="tp-hadoop-12"
VM_DIR="~/soil_moisture"

echo "🔧 Ajout de l'export JSON pour ThingsBoard..."

# Créer le nouveau predict_moisture.py avec export JSON
ssh $VM << 'REMOTE'
cd ~/soil_moisture/src

# Backup de l'ancien fichier
cp predict_moisture.py predict_moisture.py.backup

# Ajouter l'import JSON en haut du fichier
cat > predict_moisture_new.py << 'PYTHON'
"""Predict soil moisture - VM version with JSON export"""
import sys
from pathlib import Path
import joblib
import numpy as np
import json
from datetime import datetime
from resnet_feature_extractor import ResNetFeatureExtractor

def save_prediction_json(image_path, prediction, lower, upper):
    """Sauvegarde la prédiction au format JSON pour ThingsBoard"""
    timestamp = datetime.now()
    
    result = {
        "timestamp": timestamp.isoformat(),
        "timestamp_unix": int(timestamp.timestamp() * 1000),
        "image_path": str(image_path),
        "prediction": {
            "moisture_percent": round(float(prediction), 2),
            "lower_bound": round(float(lower), 2),
            "upper_bound": round(float(upper), 2),
            "uncertainty": round(float((upper - lower) / 2), 2)
        },
        "model_info": {
            "name": "ResNet-50 + Ridge Regression",
            "confidence_level": 0.95
        }
    }
    
    json_dir = Path("logs/predictions")
    json_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = json_dir / f"prediction_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    return json_path

def predict_moisture(image_path: str, model_path: str = "models/ridge_regressor_resnet.joblib"):
    model_data = joblib.load(model_path)
    ridge = model_data['ridge_regressor']
    quantile = model_data['confidence_quantile']
    config = model_data['config']
    
    extractor = ResNetFeatureExtractor(
        model_name=config['model']['name'],
        device="cpu"
    )
    
    features = extractor.extract_features(image_path)
    features = np.array([features])
    
    prediction = ridge.predict(features)[0]
    lower = prediction - quantile
    upper = prediction + quantile
    
    return prediction, lower, upper

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path")
    parser.add_argument("--log", action="store_true")
    parser.add_argument("--json", action="store_true", help="Export to JSON for ThingsBoard")
    args = parser.parse_args()
    
    pred, lower, upper = predict_moisture(args.image_path)
    
    result = f"""
============================================================
🌱 SOIL MOISTURE PREDICTION
============================================================
📊 Prediction:    {pred:.1f}%
📈 95% CI:        [{lower:.1f}%, {upper:.1f}%]
⚠️  Uncertainty:   ±{(upper-lower)/2:.1f}%
============================================================
"""
    print(result)
    
    # Export JSON (pour ThingsBoard)
    if args.json or args.log:
        json_path = save_prediction_json(args.image_path, pred, lower, upper)
        print(f"📝 JSON saved: {json_path}")
    
    # Log texte (ancien format)
    if args.log:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = f"logs/prediction_{timestamp}.txt"
        Path("logs").mkdir(exist_ok=True)
        with open(log_path, 'w') as f:
            f.write(f"Image: {args.image_path}\n{result}")
PYTHON

# Remplacer l'ancien fichier
mv predict_moisture_new.py predict_moisture.py

# Créer le dossier predictions
mkdir -p ~/soil_moisture/logs/predictions

echo "✅ Export JSON activé!"
REMOTE

echo ""
echo "✅ Mise à jour terminée!"
echo ""
echo "📋 Nouveau format de sortie:"
echo "   - Logs texte: logs/prediction_*.txt"
echo "   - Logs JSON:  logs/predictions/prediction_*.json"
echo ""
echo "💡 Guy pourra lire les fichiers JSON dans:"
echo "   ~/soil_moisture/logs/predictions/"
EOF

chmod +x scripts/add_json_export.sh
````

---

## 📄 **Documentation pour Guy**

````markdown
# 📘 Guide d'intégration ThingsBoard - Pour Guy

## 📍 Localisation des données

Les prédictions sont sauvegardées dans :
```
~/soil_moisture/logs/predictions/
├── prediction_20260214_153000.json
├── prediction_20260214_154500.json
└── ...
```

## 📊 Format JSON

Chaque prédiction est un fichier JSON avec cette structure :

```json
{
  "timestamp": "2026-02-14T15:30:00.123456",
  "timestamp_unix": 1771071000123,
  "image_path": "/home/ubuntu/soil_moisture/processed/soil_20260214_153000.jpg",
  "prediction": {
    "moisture_percent": 48.5,
    "lower_bound": 17.8,
    "upper_bound": 79.2,
    "uncertainty": 30.7
  },
  "model_info": {
    "name": "ResNet-50 + Ridge Regression",
    "confidence_level": 0.95
  }
}
```

## 🎯 Intégration ThingsBoard

### Option 1 : Watcher de fichiers (recommandé)
Utilise `watchdog` pour détecter les nouveaux fichiers JSON et les envoyer via MQTT.

### Option 2 : Cron job
Script qui s'exécute toutes les X minutes pour envoyer les nouveaux JSON.

### Option 3 : API REST
Créer un endpoint Flask qui reçoit les prédictions et les forward à ThingsBoard.

## 📦 Dépendances à installer

```bash
pip install paho-mqtt watchdog pyyaml
```

## 🔑 Configuration ThingsBoard

Créer `api/thingsboard_config.yaml` :

```yaml
host: "thingsboard.cloud"  # ou ton instance
port: 1883
access_token: "YOUR_DEVICE_ACCESS_TOKEN"
device_name: "soil-moisture-sensor"
```

## 🚀 Exemple de client MQTT

Voir `api/mqtt_client.py` (fichier à créer)
````

---

## 🎯 **Résumé de la séparation des tâches**

| Responsabilité | Personne | Status |
|----------------|----------|--------|
| **Capture d'images** | Antoine | ✅ Fait |
| **Entraînement du modèle** | Antoine | ✅ Fait |
| **Déploiement sur VM** | Antoine | ✅ Fait |
| **Inférence CPU** | Antoine | ✅ Fait |
| **Export JSON** | Antoine | ⏳ À ajouter |
| **Client MQTT** | Guy | ⏳ À faire |
| **Dashboard ThingsBoard** | Guy | ⏳ À faire |
| **Alertes** | Guy | ⏳ À faire |

---

## 🚀 **Prochaines étapes pour TOI (Antoine)**

````bash
# 1. Ajouter l'export JSON
./scripts/add_json_export.sh

# 2. Tester avec une image
ssh tp-hadoop-12
cd ~/soil_moisture
source venv/bin/activate
python src/predict_moisture.py incoming/test.jpg --json

# 3. Vérifier le JSON créé
cat logs/predictions/prediction_*.json
````

---

**Veux-tu que je crée le script `add_json_export.sh` et qu'on le teste ? 🚀**