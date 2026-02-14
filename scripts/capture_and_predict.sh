#!/bin/bash

echo "=========================================="
echo "🌱 SOIL MOISTURE - CAPTURE & PREDICTION"
echo "=========================================="

# 1. Capture de l'image
echo ""
echo "📸 Step 1: Capturing image from webcam..."
echo "------------------------------------------"

poetry run python edge/src/capture/mac_capture.py

# Récupérer la dernière image capturée
LATEST_IMAGE=$(ls -t edge/captures/soil_image_*.jpg 2>/dev/null | head -1)

if [ -z "$LATEST_IMAGE" ]; then
    echo "❌ Error: No image captured"
    exit 1
fi

echo "✅ Image captured: $LATEST_IMAGE"

# 2. Inférence sur l'image
echo ""
echo "🤖 Step 2: Running inference..."
echo "--------------------------------"

poetry run python ml/src/inference/predict_moisture.py "$LATEST_IMAGE"

# 3. Afficher l'image
echo ""
echo "🖼️  Step 3: Opening captured image..."
echo "-------------------------------------"

if command -v open &> /dev/null; then
    open "$LATEST_IMAGE"
    echo "✅ Image opened in default viewer"
else
    echo "ℹ️  Image saved at: $LATEST_IMAGE"
fi

echo ""
echo "=========================================="
echo "✅ PIPELINE COMPLETE!"
echo "=========================================="
