# 🚀 Guide: Créer le Repository GitHub - Étape par Étape
## Version: Soil Moisture Monitoring

---

## 📋 Checklist Complète

### **Étape 1: Créer le Repository sur GitHub**

1. **Aller sur GitHub** : https://github.com
2. **Click "New repository"** (bouton vert en haut à droite)
3. **Remplir le formulaire** :
   ```
   Repository name: soil-moisture-monitor
   Description: IoT system for automated soil moisture monitoring (Edge → VM → ThingsBoard)
   Visibility: ✅ Private (ou Public si vous voulez)
   ❌ NE PAS cocher "Initialize with README" (on va le faire localement)
   ❌ NE PAS ajouter .gitignore encore
   ❌ NE PAS choisir license (optionnel)
   ```
4. **Click "Create repository"**

---

### **Étape 2: Ajouter Collaborateur**

1. **Dans le repo** → Aller sur **Settings** (en haut)
2. **Sidebar gauche** → Click **Collaborators** (ou **Manage access**)
3. **Click "Add people"**
4. **Entrer le username GitHub de Guy** (ou son email)
5. **Select "Write" access** (il peut push directement)
6. **Send invitation**
7. ✅ Guy doit accepter l'email d'invitation

---

### **Étape 3: Créer Structure Locale**

**Sur votre Mac, dans Terminal** :

```bash
# Créer dossier projet
mkdir soil-moisture-monitor
cd soil-moisture-monitor

# Initialiser Git
git init

# Créer structure de dossiers
mkdir -p edge/src/capture
mkdir -p edge/config
mkdir -p edge/tests
mkdir -p vm/src
mkdir -p vm/config
mkdir -p vm/tests
mkdir -p models
mkdir -p docs
mkdir -p scripts

# Créer fichiers vides de base
touch edge/src/__init__.py
touch edge/src/capture/__init__.py
touch edge/src/capture/base.py
touch edge/src/capture/mac_capture.py
touch vm/src/__init__.py
touch vm/src/inference.py
touch vm/src/mqtt_client.py
touch README.md
touch requirements.txt
```

---

### **Étape 4: Créer `.gitignore`**

**Créer le fichier** :
```bash
touch .gitignore
```

**Contenu à copier dans `.gitignore`** :

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Secrets & Config
.env
*.pem
*.key
config/secrets.yaml
*_token.txt

# ML Models (use Git LFS instead)
models/*.pt
models/*.pth
models/*.onnx

# Data & Logs
data/
logs/
*.log
captures/
*.jpg
*.png
*.jpeg

# SQLite
*.db
*.sqlite
*.sqlite3

# Temporary files
*.tmp
*.bak
*.swp
temp/
tmp/

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Jupyter Notebooks
.ipynb_checkpoints/
*.ipynb

# Distribution
*.tar.gz
*.zip
```

---

### **Étape 5: Créer README Initial**

**Éditer `README.md`** :

```markdown
# 💧 Soil Moisture Monitor

IoT system for automated soil moisture monitoring using computer vision and cloud analytics.

## 📐 Architecture

```
Edge Devices (Mac/Linux) → VM (Image Analysis) → ThingsBoard (Dashboard)
```

## 🎯 Project Overview

This system monitors soil moisture levels through automated image capture and ML-based analysis:
- **Captures** soil images from multiple locations
- **Analyzes** images on VM to extract:
  - Moisture percentage (0-100%)
  - Humidity classification (3-level scale: Dry/Optimal/Wet)
  - Visual soil condition assessment
- **Visualizes** real-time data on ThingsBoard dashboard

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Webcam/Camera
- VM access (for image analysis)
- ThingsBoard account

### Installation

**Local Machine (Edge):**
```bash
cd edge
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

**VM (Analysis Server):**
```bash
cd vm
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 Output Data

The ML model produces three key metrics:
- **Moisture Percentage**: Quantitative moisture level (0-100%)
- **Humidity Label**: Classification on 3-level scale
  - `DRY` (0-33%): Irrigation needed
  - `OPTIMAL` (34-66%): Good condition
  - `WET` (67-100%): Potential overwatering
- **Soil Image**: Visual reference with timestamp

## 📂 Project Structure

```
soil-moisture-monitor/
├── edge/               # Local capture devices
│   ├── src/
│   │   └── capture/   # OS-specific capture modules
│   ├── config/
│   └── tests/
├── vm/                 # VM analysis server
│   ├── src/
│   │   ├── inference.py      # ML model inference
│   │   ├── mqtt_client.py    # ThingsBoard communication
│   │   └── image_analyzer.py # Soil moisture extraction
│   ├── config/
│   └── tests/
├── models/             # ML models (Git LFS)
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
flake8 .
black .
```

## 📊 Dashboard

Access ThingsBoard dashboard: [Link TBD]

**Dashboard Widgets:**
- Time-series moisture percentage chart
- Current humidity classification gauge
- Latest soil image display
- Alert status (if dry condition detected)

## 🔬 ML Model Details

**Input:** RGB soil image (224x224 pixels)  
**Output:** 
- Moisture percentage (float, 0-100)
- Humidity class (string: DRY/OPTIMAL/WET)
- Confidence score (float, 0-1)

**Model Architecture:** [TBD - e.g., ResNet50, MobileNetV3]  
**Training Dataset:** [TBD - soil moisture images with ground truth]

## 👥 Team

- **Antoine** (Mac) - Edge capture + ML integration
- **Guy** (Linux) - Edge capture + ThingsBoard setup

## 📄 License

[TBD]

---

## 🚧 Development Roadmap

### Phase 1 (Current)
- [x] Project structure setup
- [ ] Image capture modules (Mac/Linux)
- [ ] VM image upload pipeline
- [ ] ML model integration
- [ ] ThingsBoard connection

### Phase 2 (Future)
- [ ] Multi-location monitoring (>2 devices)
- [ ] Historical trend analysis
- [ ] Automated irrigation alerts
- [ ] Mobile app dashboard

---

**Last Updated:** January 2026  
**Status:** In Development
```

---

### **Étape 6: Créer `requirements.txt` Initial**

**Créer fichier** :
```bash
touch requirements.txt
```

**Contenu** :
```txt
# Core dependencies
torch>=2.0.0
torchvision>=0.15.0
opencv-python>=4.8.0
Pillow>=10.0.0
paho-mqtt>=1.6.1
PyYAML>=6.0
APScheduler>=3.10.0
numpy>=1.24.0

# Image processing (for moisture analysis)
scikit-image>=0.21.0

# API (VM only)
Flask>=3.0.0
# or
fastapi>=0.104.0
uvicorn>=0.24.0

# Database
# pymongo>=4.0.0  # If using MongoDB

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
requests>=2.31.0

# Code quality
flake8>=6.1.0
black>=23.10.0

# Utils
python-dotenv>=1.0.0
watchdog>=3.0.0  # File watcher for VM
paramiko>=3.3.0  # SFTP if needed
```

---

### **Étape 7: Premier Commit**

```bash
# Vérifier les fichiers
git status

# Ajouter tout
git add .

# Premier commit
git commit -m "Initial project structure for soil moisture monitoring

- Add edge and VM folder structure
- Add .gitignore (Python, secrets, models)
- Add README with architecture overview
- Add requirements.txt with core dependencies
- Configure for 3-output ML model (moisture %, humidity label, image)"

# Définir branche principale
git branch -M main
```

---

### **Étape 8: Connecter au Repository GitHub**

**Remplacer `YOUR_USERNAME`** par votre nom GitHub :

```bash
# Ajouter remote
git remote add origin https://github.com/YOUR_USERNAME/soil-moisture-monitor.git

# Vérifier
git remote -v

# Push initial
git push -u origin main
```

---

### **Étape 9: Vérification**

1. **Aller sur GitHub** → Rafraîchir la page du repo
2. **Vérifier que vous voyez** :
   - ✅ Dossiers `edge/`, `vm/`, `models/`, `docs/`
   - ✅ Fichiers `.gitignore`, `README.md`, `requirements.txt`
   - ✅ Commit "Initial project structure for soil moisture monitoring"

---

### **Étape 10: Configuration Protection Branches (Optionnel mais Recommandé)**

1. **Settings** → **Branches**
2. **Add branch protection rule**
3. **Branch name pattern**: `main`
4. **Cocher** :
   - ✅ Require a pull request before merging
   - ✅ Require approvals (1)
5. **Save changes**

---

## ✅ Vérification Finale

**Checklist** :
- [ ] Repository créé sur GitHub (nom: `soil-moisture-monitor`)
- [ ] Guy ajouté comme collaborateur (invitation envoyée)
- [ ] Structure de dossiers créée localement
- [ ] `.gitignore` configuré (Python, secrets, models)
- [ ] README initial écrit (soil moisture monitoring focus)
- [ ] `requirements.txt` créé avec scikit-image
- [ ] Premier commit pushé
- [ ] Visible sur GitHub

---

## 🔄 Workflow pour Guy (Linux)

**Une fois invitation acceptée** :

```bash
# Cloner le repo
git clone https://github.com/YOUR_USERNAME/soil-moisture-monitor.git
cd soil-moisture-monitor

# Créer branche pour son travail
git checkout -b feature/linux-capture

# Créer son fichier
touch edge/src/capture/linux_capture.py

# Travailler...
# (éditer linux_capture.py)

# Commit et push
git add edge/src/capture/linux_capture.py
git commit -m "feat: add Linux soil image capture module"
git push origin feature/linux-capture

# Créer Pull Request sur GitHub
```

---

## 📝 Conventions Git (À Suivre)

### **Format Commits** :
```
<type>: <description>

[optional body]
```

**Types** :
- `feat:` Nouvelle fonctionnalité
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Refactoring
- `chore:` Maintenance

**Exemples** :
```bash
git commit -m "feat: add Mac soil camera capture module"
git commit -m "fix: handle camera permission denied on macOS"
git commit -m "feat: add moisture percentage extraction from ML model"
git commit -m "docs: update README with humidity classification scale"
git commit -m "test: add unit tests for 3-output inference pipeline"
```

---

## 🎯 Prochaines Étapes

Après setup Git :
1. ✅ **Antoine** : Créer `edge/src/capture/mac_capture.py`
2. ✅ **Guy** : Créer `edge/src/capture/linux_capture.py`
3. ✅ **Antoine** : Définir format de sortie ML (moisture %, label, image path)
4. ✅ **Guy** : Configurer ThingsBoard pour accepter 3 champs de données
5. ✅ **Les deux** : Créer branches `feature/mac-capture` et `feature/linux-capture`
6. ✅ **Merge** dans `main` via Pull Requests

---

**Temps estimé** : 15-20 minutes  
**Focus nouveau** : Soil moisture monitoring (au lieu de plant disease)  
**Outputs ML** : Moisture %, Humidity label (3 classes), Image reference

Besoin d'aide pour configurer SSH keys ? 🔑