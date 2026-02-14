#!/bin/bash

# Variables
VM="tp-hadoop-12"
VM_DIR="~/soil_monitor"
LOCAL_PROJECT="/Users/antoinedalle/Desktop/Period_2/IOT/Projet/soil-moisture-monitor"

echo "🚀 Déploiement sur la VM via bastion..."

# Créer les __init__.py s'ils n'existent pas
touch $LOCAL_PROJECT/ml/src/__init__.py
touch $LOCAL_PROJECT/ml/src/inference/__init__.py

# Créer la structure sur la VM
echo "📁 Création de la structure..."
ssh $VM "mkdir -p $VM_DIR/{vm/{uploads,processed,src},ml/{models,src/inference},config}"

# Copier les fichiers
echo "📤 Copie de l'API Flask..."
scp $LOCAL_PROJECT/vm/src/api.py $VM:$VM_DIR/vm/src/

echo "📤 Copie du script d'inférence..."
scp $LOCAL_PROJECT/ml/src/inference/predict_humidity.py $VM:$VM_DIR/ml/src/inference/

echo "📤 Copie du modèle ML..."
scp $LOCAL_PROJECT/ml/models/ridge_regressor.joblib $VM:$VM_DIR/ml/models/

echo "📤 Copie des __init__.py..."
scp $LOCAL_PROJECT/vm/src/__init__.py $VM:$VM_DIR/vm/src/
scp $LOCAL_PROJECT/ml/src/__init__.py $VM:$VM_DIR/ml/src/
scp $LOCAL_PROJECT/ml/src/inference/__init__.py $VM:$VM_DIR/ml/src/inference/

echo "📤 Copie de requirements.txt..."
scp $LOCAL_PROJECT/requirements.txt $VM:$VM_DIR/

echo "✅ Déploiement terminé !"
echo ""
echo "💡 Prochaines étapes :"
echo "   1. SSH dans la VM : ssh $VM"
echo "   2. cd $VM_DIR"
echo "   3. python3 -m venv venv && source venv/bin/activate"
echo "   4. pip install -r requirements.txt"
echo "   5. python vm/src/api.py"python3 -m venv venv
source venv/bin/activate# 1. Installer python3-venv
sudo apt update
sudo apt install python3.12-venv -y

# 2. Nettoyer le venv incomplet
cd ~/soil_monitor
rm -rf venv

# 3. Recréer le venv avec python3
python3 -m venv venv

# 4. Activer le venv
source venv/bin/activate

# 5. Vérifier que tu es dans le venv
which python
# Devrait afficher : /home/ubuntu/soil_monitor/venv/bin/python

# 6. Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 7. Lancer l'API
python vm/src/api.py