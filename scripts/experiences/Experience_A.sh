#!/bin/bash

VM="tp-hadoop-12"
LOCAL_PROJECT="/Users/antoinedalle/Desktop/Period_2/IOT/Projet/soil-moisture-monitor"

echo "╔══════════════════════════════════════════╗"
echo "║   🌱 SOIL MOISTURE MONITORING SYSTEM     ║"
echo "║   EXPERIMENT A — ONE-SHOT PIPELINE       ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  Objective : Validate the full end-to-end pipeline"
echo "              in a single execution."
echo "  Pipeline  : Capture → SCP → VM Inference → JSON → Archive"
echo "  Expected  : 1 image, 1 prediction, 1 MQTT publish"
echo ""
echo "  Started   : $(date)"
echo "──────────────────────────────────────────────"

# 1. CAPTURE
echo ""
echo "  [A/1] 📸 CAPTURE"
echo "  ─────────────────"
cd $LOCAL_PROJECT
poetry run python edge/src/capture/mac_capture.py

LATEST_IMG=$(ls -t edge/captures/soil_image_*.jpg 2>/dev/null | head -1)

if [ -z "$LATEST_IMG" ]; then
    echo "  ❌ Capture failed — no image found. Aborting."
    exit 1
fi

echo "  ✅ Image captured : $(basename $LATEST_IMG)"

# 2. SCP TRANSFER
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
echo ""
echo "  [A/2] 📤 SCP TRANSFER → VM"
echo "  ────────────────────────────"
scp "$LATEST_IMG" $VM:~/soil_moisture/incoming/soil_${TIMESTAMP}.jpg
echo "  ✅ Transferred : soil_${TIMESTAMP}.jpg"

# 3. INFERENCE ON VM
echo ""
echo "  [A/3] 🤖 INFERENCE + MQTT PUBLISH (on VM)"
echo "  ────────────────────────────────────────────"
ssh $VM << REMOTE
cd ~/soil_moisture
source venv/bin/activate
python src/predict_moisture.py incoming/soil_${TIMESTAMP}.jpg
REMOTE

# 4. JSON VERIFICATION
echo ""
echo "  [A/4] 📄 JSON VERIFICATION"
echo "  ────────────────────────────"
LATEST_JSON=$(ssh $VM "ls -t ~/soil_moisture/logs/predictions/*.json 2>/dev/null | head -1")

if [ -z "$LATEST_JSON" ]; then
    echo "  ❌ No JSON found — inference may have failed."
    exit 1
fi

echo "  ✅ JSON file : $(basename $LATEST_JSON)"
echo ""
echo "  📋 Prediction output:"
echo "  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄"
ssh $VM "cat $LATEST_JSON" | python3 -m json.tool
echo "  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄"

# 5. ARCHIVE VERIFICATION
echo ""
echo "  [A/5] 📦 ARCHIVE VERIFICATION"
echo "  ────────────────────────────────"
ssh $VM "ls -lh ~/soil_moisture/processed/soil_${TIMESTAMP}.jpg 2>/dev/null"

if [ $? -eq 0 ]; then
    echo "  ✅ Image archived in processed/"
else
    echo "  ⚠️  Image not archived (acceptable for prototype)"
fi

# SUMMARY
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   ✅ EXPERIMENT A — COMPLETED            ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  📊 Summary:"
echo "     • Image captured  : $(basename $LATEST_IMG)"
echo "     • Image on VM     : soil_${TIMESTAMP}.jpg"
echo "     • JSON generated  : $(basename $LATEST_JSON)"
echo "     • Finished        : $(date)"
echo ""
echo "  💡 Next step: run Experiment B (stable interval)"
echo "     bash scripts/experiences/Experience_B.sh"
echo ""