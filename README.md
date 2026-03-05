# 💧 Soil Moisture Monitor

IoT system for automated soil moisture monitoring using computer vision and a cloud dashboard.

## How it works

Edge devices (Mac/Linux) capture soil images at regular intervals, send them to a remote VM via SCP, where a lightweight ML model estimates moisture. Results are published via MQTT to a ThingsBoard dashboard for real-time monitoring and alerts.

```
[Edge Camera] → SCP → [VM Inference] → MQTT → [ThingsBoard Dashboard]
```

## Features

- **Non-invasive** — no sensors in the soil, just a camera
- **Cross-platform** — Mac and Linux supported
- **Real-time** — moisture trends and alerts on ThingsBoard
- **Uncertainty-aware** — every prediction includes a 95% confidence interval

## Project Structure

```
soil-moisture-monitor/
├── edge/
│   ├── captures/          # Raw images (local)
│   └── src/capture/       # Capture scripts (Mac/Linux)
├── scripts/
│   └── experiences/
│       ├── Experience_A.sh   # One-shot pipeline test
│       ├── Experience_B.sh   # Stable interval (2 min)
│       └── Experience_C.sh   # Burst stress test (5 sec)
├── src/
│   ├── predict_moisture.py
│   └── resnet_feature_extractor.py
├── models/
│   └── ridge_regressor_resnet.joblib
└── logs/predictions/
```

## Quick Start

**1. Clone the repo**
```bash
git clone https://github.com/DalleAntoine-99/soil-moisture-monitor.git
cd soil-moisture-monitor
```

**2. Install dependencies (edge)**
```bash
poetry install
```

**3. Install dependencies (VM)**
```bash
python3 -m venv venv
source venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers pillow scikit-learn joblib paho-mqtt
```

**4. Run the pipeline**
```bash
# Single shot (Experiment A)
bash scripts/experiences/Experience_A.sh

# Stable interval test (Experiment B)
bash scripts/experiences/Experience_B.sh

# Burst stress test (Experiment C)
bash scripts/experiences/Experience_C.sh
```

## Requirements

- Python 3.11+
- SSH access to remote VM
- ThingsBoard account + device access token
- `imagesnap` (macOS) or `fswebcam` (Linux)

## Authors

Antoine Dalle & Guy Rostan NANA — Télécom Paris, IoT Course, 2026