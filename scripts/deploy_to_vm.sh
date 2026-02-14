#!/bin/bash

# Variables
VM="tp-hadoop-12"
VM_DIR="~/soil_moisture"
LOCAL_PROJECT="/Users/antoinedalle/Desktop/Period_2/IOT/Projet/soil-moisture-monitor"

echo "=========================================="
echo "🚀 DÉPLOIEMENT RESNET-50 SUR LA VM"
echo "=========================================="

# Créer les __init__.py localement
echo ""
echo "📝 Création des __init__.py..."
touch $LOCAL_PROJECT/ml/src/__init__.py
touch $LOCAL_PROJECT/ml/src/models/__init__.py
touch $LOCAL_PROJECT/ml/src/inference/__init__.py

# Créer un dossier temporaire pour les fichiers adaptés
TEMP_DIR="$LOCAL_PROJECT/vm_deployment_temp"
mkdir -p $TEMP_DIR

# ===========================================================
# ADAPTATION AUTOMATIQUE DU DEVICE POUR LA VM (CPU-ONLY)
# ===========================================================

echo ""
echo "🔧 Adaptation des scripts pour CPU..."

# 1. Copier et adapter resnet_feature_extractor.py
cp $LOCAL_PROJECT/ml/src/models/resnet_feature_extractor.py $TEMP_DIR/
# Remplacer "auto" et "mps" par "cpu"
sed -i '' 's/device: str = "auto"/device: str = "cpu"/g' $TEMP_DIR/resnet_feature_extractor.py
sed -i '' 's/device="auto"/device="cpu"/g' $TEMP_DIR/resnet_feature_extractor.py
sed -i '' 's/device="mps"/device="cpu"/g' $TEMP_DIR/resnet_feature_extractor.py

# 2. Copier et adapter predict_moisture.py
cp $LOCAL_PROJECT/ml/src/inference/predict_moisture.py $TEMP_DIR/
# Forcer device="cpu" dans la config
sed -i '' 's/device=config\["model"\]\["device"\]/device="cpu"/g' $TEMP_DIR/predict_moisture.py

echo "✅ Scripts adaptés pour CPU dans: $TEMP_DIR"

# ===========================================================
# TRANSFERT VERS LA VM
# ===========================================================

# Créer la structure sur la VM
echo ""
echo "📁 Création de la structure sur la VM..."
ssh $VM "mkdir -p $VM_DIR/{models,src,incoming,processed,logs}"

# Copier le modèle
echo ""
echo "📤 Copie du modèle ResNet-50 + Ridge..."
scp $LOCAL_PROJECT/ml/models/ridge_regressor_resnet_mapie.joblib \
    $VM:$VM_DIR/models/ridge_regressor_resnet.joblib

# Copier les scripts ADAPTÉS
echo ""
echo "📤 Copie des scripts adaptés CPU..."
scp $TEMP_DIR/resnet_feature_extractor.py $VM:$VM_DIR/src/
scp $TEMP_DIR/predict_moisture.py $VM:$VM_DIR/src/

# Copier les __init__.py
echo ""
echo "📤 Copie des __init__.py..."
scp $LOCAL_PROJECT/ml/src/__init__.py $VM:$VM_DIR/src/

# Créer le script shell de prédiction
echo ""
echo "📜 Création du script predict.sh..."
ssh $VM "cat > $VM_DIR/predict.sh << 'SCRIPT'
#!/bin/bash
if [ -z \"\$1\" ]; then
    echo \"Usage: ./predict.sh <image_path>\"
    exit 1
fi
cd ~/soil_moisture
source venv/bin/activate
python src/predict_moisture.py \"\$1\" --log
SCRIPT
chmod +x $VM_DIR/predict.sh"

# Nettoyer le dossier temporaire
echo ""
echo "🧹 Nettoyage..."
rm -rf $TEMP_DIR

echo ""
echo "=========================================="
echo "✅ DÉPLOIEMENT TERMINÉ !"
echo "=========================================="
echo ""
echo "📋 Résumé des adaptations:"
echo "   ✓ device='auto' → device='cpu'"
echo "   ✓ device='mps' → device='cpu'"
echo "   ✓ Scripts optimisés pour CPU-only"
echo ""
echo "�� Sur la VM, il suffit de:"
echo "   1. ssh $VM"
echo "   2. cd $VM_DIR"
echo "   3. source venv/bin/activate"
echo "   4. ./predict.sh incoming/test.jpg"
echo ""
