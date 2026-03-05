#!/bin/bash

VM="tp-hadoop-12"
LOCAL_PROJECT="/Users/antoinedalle/Desktop/Period_2/IOT/Projet/soil-moisture-monitor"
INTERVAL_SECONDS=120
DURATION_MINUTES=60
TOTAL_ITERATIONS=$(( DURATION_MINUTES * 60 / INTERVAL_SECONDS ))

SUCCESS_COUNT=0
FAIL_CAPTURE=0
FAIL_SCP=0
FAIL_INFERENCE=0
START_TIME=$(date +%s)

echo "╔══════════════════════════════════════════╗"
echo "║   🌱 SOIL MOISTURE MONITORING SYSTEM     ║"
echo "║   EXPERIMENT B — STABLE INTERVAL TEST    ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  Objective : Verify pipeline stability over repeated"
echo "              executions at a fixed 2-minute interval."
echo "  Pipeline  : Capture → SCP → VM Inference → JSON → Archive"
echo "  Interval  : ${INTERVAL_SECONDS}s (2 min)"
echo "  Duration  : ${DURATION_MINUTES} min"
echo "  Expected  : ${TOTAL_ITERATIONS} iterations"
echo ""
echo "  Started   : $(date)"
echo "──────────────────────────────────────────────"

for i in $(seq 1 $TOTAL_ITERATIONS); do
    ITER_START=$(date +%s)
    echo ""
    echo "  ┌─ Iteration $i / $TOTAL_ITERATIONS  [$(date +%H:%M:%S)] ──────────────"

    # Step 1: Capture
    echo "  │  [B/1] 📸 Capturing..."
    cd $LOCAL_PROJECT
    poetry run python edge/src/capture/mac_capture.py
    LATEST_IMG=$(ls -t edge/captures/soil_image_*.jpg 2>/dev/null | head -1)

    if [ -z "$LATEST_IMG" ]; then
        echo "  │  ❌ Capture failed — skipping iteration"
        FAIL_CAPTURE=$((FAIL_CAPTURE + 1))
        echo "  └──────────────────────────────────────────────"
        sleep $INTERVAL_SECONDS
        continue
    fi
    echo "  │  ✅ Captured : $(basename $LATEST_IMG)"

    # Step 2: SCP Transfer
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    echo "  │  [B/2] 📤 Transferring to VM..."
    scp -o ConnectTimeout=15 "$LATEST_IMG" $VM:~/soil_moisture/incoming/soil_${TIMESTAMP}.jpg

    if [ $? -ne 0 ]; then
        echo "  │  ❌ SCP failed — skipping iteration"
        FAIL_SCP=$((FAIL_SCP + 1))
        echo "  └──────────────────────────────────────────────"
        sleep $INTERVAL_SECONDS
        continue
    fi
    echo "  │  ✅ Transferred : soil_${TIMESTAMP}.jpg"

    # Step 3: Inference + MQTT
    echo "  │  [B/3] 🤖 Running inference on VM..."
    ssh $VM << REMOTE
cd ~/soil_moisture
source venv/bin/activate
python src/predict_moisture.py incoming/soil_${TIMESTAMP}.jpg
REMOTE

    if [ $? -ne 0 ]; then
        echo "  │  ❌ Inference failed"
        FAIL_INFERENCE=$((FAIL_INFERENCE + 1))
        echo "  └──────────────────────────────────────────────"
        sleep $INTERVAL_SECONDS
        continue
    fi

    # Step 4: JSON check
    LATEST_JSON=$(ssh $VM "ls -t ~/soil_moisture/logs/predictions/*.json 2>/dev/null | head -1")
    echo "  │  ✅ JSON : $(basename $LATEST_JSON)"

    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

    # Wait for next interval
    ITER_END=$(date +%s)
    ELAPSED=$(( ITER_END - ITER_START ))
    WAIT=$(( INTERVAL_SECONDS - ELAPSED ))

    echo "  │  ⏱  Iteration time : ${ELAPSED}s"

    if [ $WAIT -gt 0 ]; then
        echo "  │  ⏳ Waiting ${WAIT}s until next capture..."
    else
        echo "  │  ⚠️  Iteration exceeded interval (${ELAPSED}s > ${INTERVAL_SECONDS}s)"
    fi

    echo "  └──────────────────────────────────────────────"

    [ $WAIT -gt 0 ] && sleep $WAIT
done

END_TIME=$(date +%s)
TOTAL_ELAPSED=$(( (END_TIME - START_TIME) / 60 ))

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   ✅ EXPERIMENT B — COMPLETED            ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  📊 Summary:"
echo "     • Expected iterations  : $TOTAL_ITERATIONS"
echo "     • Successes            : $SUCCESS_COUNT"
echo "     • Capture failures     : $FAIL_CAPTURE"
echo "     • SCP failures         : $FAIL_SCP"
echo "     • Inference failures   : $FAIL_INFERENCE"
echo "     • Total duration       : ${TOTAL_ELAPSED} min"
echo "     • Finished             : $(date)"
echo ""
echo "  💡 Next step: run Experiment C (burst stress test)"
echo "     bash scripts/experiences/Experience_C.sh"
echo ""