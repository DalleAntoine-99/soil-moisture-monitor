cat > scripts/auto_capture_loop.sh << 'EOF'
#!/bin/bash

VM="tp-hadoop-12"
LOCAL_PROJECT="/Users/antoinedalle/Desktop/Period_2/IOT/Projet/soil-moisture-monitor"
INTERVAL=3600  # 1 heure (3600 secondes)

echo "=========================================="
echo "🔄 PIPELINE AUTOMATIQUE EN BOUCLE"
echo "=========================================="
echo ""
echo "⏱️  Intervalle: ${INTERVAL}s ($(($INTERVAL / 60)) minutes)"
echo "🛑 Arrêter avec Ctrl+C"
echo ""

COUNTER=1

while true; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔄 ITERATION #${COUNTER} - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Capture
    echo "📸 Capture..."
    cd $LOCAL_PROJECT
    poetry run python edge/src/capture/mac_capture.py
    
    LATEST_IMG=$(ls -t edge/captures/soil_image_*.jpg 2>/dev/null | head -1)
    
    if [ -n "$LATEST_IMG" ]; then
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        
        # Envoi
        echo "📤 Envoi vers VM..."
        scp "$LATEST_IMG" $VM:~/soil_moisture/incoming/soil_${TIMESTAMP}.jpg
        
        # Prédiction
        echo "🤖 Prédiction..."
        ssh $VM << REMOTE
cd ~/soil_moisture
source venv/bin/activate
python src/predict_moisture.py incoming/soil_${TIMESTAMP}.jpg
REMOTE
        
        echo "✅ Iteration #${COUNTER} terminée"
    else
        echo "❌ Échec de la capture"
    fi
    
    ((COUNTER++))
    
    echo ""
    echo "⏳ Attente de ${INTERVAL}s avant la prochaine capture..."
    echo "   (Prochaine capture: $(date -v+${INTERVAL}S '+%H:%M:%S'))"
    sleep $INTERVAL
done
EOF

chmod +x scripts/auto_capture_loop.sh
