#!/bin/bash

VM="tp-hadoop-12"
LOCAL_PROJECT="/Users/antoinedalle/Desktop/Period_2/IOT/Projet/soil-moisture-monitor"

echo "=========================================="
echo "🧪 TEST DE L'EXPORT JSON"
echo "=========================================="

# Prendre une image test
TEST_IMG=$(find $LOCAL_PROJECT/ml/data/raw/Soil_Moisture_Dataset -name "*.jpg" | shuf -n 1)

echo ""
echo "📸 Image: $(basename $TEST_IMG)"

# Envoyer sur la VM
echo ""
echo "📤 Envoi vers la VM..."
scp "$TEST_IMG" $VM:~/soil_moisture/incoming/test.jpg

# Tester la prédiction avec JSON
echo ""
echo "🤖 Prédiction avec export JSON..."
ssh $VM << 'REMOTE'
cd ~/soil_moisture
source venv/bin/activate
python src/predict_moisture.py incoming/test.jpg
REMOTE

# Récupérer et afficher le JSON
echo ""
echo "📄 Contenu du JSON généré:"
echo "=========================================="
ssh $VM "cat \$(ls -t ~/soil_moisture/logs/predictions/*.json | head -1)"

echo ""
echo "=========================================="
echo "✅ TEST TERMINÉ !"
echo "=========================================="
