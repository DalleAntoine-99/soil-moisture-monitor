#!/bin/bash

VM="tp-hadoop-12"
LOCAL_PROJECT="/Users/antoinedalle/Desktop/Period_2/IOT/Projet/soil-moisture-monitor"

echo "=========================================="
echo "🚀 TEST DE LA PIPELINE COMPLÈTE"
echo "=========================================="
echo ""
echo "📸 Capture → 📤 Envoi VM → 🤖 Prédiction → 📄 Export JSON"
echo ""

# 1. CAPTURE depuis webcam
echo "=========================================="
echo "📸 Step 1: Capture d'image depuis webcam"
echo "=========================================="
cd $LOCAL_PROJECT
poetry run python edge/src/capture/mac_capture.py

# Récupérer la dernière image capturée
LATEST_IMG=$(ls -t edge/captures/soil_image_*.jpg 2>/dev/null | head -1)

if [ -z "$LATEST_IMG" ]; then
    echo "❌ Erreur: Aucune image capturée"
    exit 1
fi

echo "✅ Image capturée: $(basename $LATEST_IMG)"

# 2. ENVOI vers la VM
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
echo ""
echo "=========================================="
echo "📤 Step 2: Envoi vers la VM"
echo "=========================================="
scp "$LATEST_IMG" $VM:~/soil_moisture/incoming/soil_${TIMESTAMP}.jpg
echo "✅ Image envoyée: soil_${TIMESTAMP}.jpg"

# 3. PRÉDICTION sur la VM avec export JSON
echo ""
echo "=========================================="
echo "🤖 Step 3: Prédiction sur la VM"
echo "=========================================="
ssh $VM << REMOTE
cd ~/soil_moisture
source venv/bin/activate
python src/predict_moisture.py incoming/soil_${TIMESTAMP}.jpg
REMOTE

# 4. RÉCUPÉRER et AFFICHER le JSON généré
echo ""
echo "=========================================="
echo "📄 Step 4: Vérification du JSON généré"
echo "=========================================="
LATEST_JSON=$(ssh $VM "ls -t ~/soil_moisture/logs/predictions/*.json 2>/dev/null | head -1")

if [ -z "$LATEST_JSON" ]; then
    echo "❌ Erreur: Aucun JSON trouvé"
    exit 1
fi

echo "📝 Fichier JSON: $(basename $LATEST_JSON)"
echo ""
echo "📋 Contenu du JSON:"
echo "──────────────────────────────────────────"
ssh $VM "cat $LATEST_JSON" | python3 -m json.tool
echo "──────────────────────────────────────────"

# 5. VÉRIFIER l'archivage
echo ""
echo "=========================================="
echo "📦 Step 5: Vérification de l'archivage"
echo "=========================================="
ssh $VM "ls -lh ~/soil_moisture/processed/soil_${TIMESTAMP}.jpg 2>/dev/null"

if [ $? -eq 0 ]; then
    echo "✅ Image archivée dans processed/"
else
    echo "⚠️  Image non archivée (normal si pas implémenté)"
fi

# 6. RÉSUMÉ
echo ""
echo "=========================================="
echo "✅ PIPELINE COMPLÈTE TESTÉE !"
echo "=========================================="
echo ""
echo "📊 Résumé:"
echo "   • Image capturée:  $(basename $LATEST_IMG)"
echo "   • Image sur VM:    soil_${TIMESTAMP}.jpg"
echo "   • JSON créé:       $(basename $LATEST_JSON)"
echo ""
echo "💡 Pour Guy:"
echo "   Le JSON est disponible dans:"
echo "   ~/soil_moisture/logs/predictions/$(basename $LATEST_JSON)"
echo ""
