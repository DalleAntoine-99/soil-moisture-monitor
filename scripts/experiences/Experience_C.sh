#!/bin/bash

VM="tp-hadoop-12"
LOCAL_PROJECT="/Users/antoinedalle/Desktop/Period_2/IOT/Projet/soil-moisture-monitor"
INTERVAL_SECONDS=5
DURATION_MINUTES=10
TOTAL_ITERATIONS=$(( DURATION_MINUTES * 60 / INTERVAL_SECONDS ))

SUCCESS_COUNT=0
FAIL_CAPTURE=0
FAIL_SCP=0
FAIL_INFERENCE=0
BACKLOG_COUNT=0
START_TIME=$(date +%s)

echo "╔══════════════════════════════════════════╗"
echo "║   🌱 SOIL MOISTURE MONITORING SYSTEM     ║"
echo "║   EXPERIMENT C — BURST / STRESS TEST     ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  Objective : Stress-test the pipeline under high"
echo "              capture frequency to detect bottlenecks"
echo "              (SCP backlog, VM CPU, MQTT limits)."
echo "  Pipeline  : Capture → SCP → VM Inference → JSON → Archive"
echo "  Interval  : ${INTERVAL_SECONDS}s (burst)"
echo "  Duration  : ${DURATION_MINUTES} min"
echo "  Expected  : ${TOTAL_ITERATIONS} iterations"
echo ""
echo "  ⚠️  Watch ThingsBoard for gaps or delayed points."
echo ""
echo "  Started   : $(date)"
echo "──────────────────────────────────────────────"

for i in $(seq 1 $TOTAL_ITERATIONS); do
    ITER_START=$(date +%s)
    echo ""
    echo "  ┌─ Burst $i / $TOTAL_ITERATIONS  [$(date +%H:%M:%S)] ──────────────"

    # Step 1: Capture
    echo "  │  [C/1] 📸 Capturing..."
    cd $LOCAL_PROJECT
    poetry run python edge/src/capture/mac_capture.py
    LATEST_IMG=$(ls -t edge/captures/soil_image_*.jpg 2>/dev/null | head -1)

    if [ -z "$LATEST_IMG" ]; then
        echo "  │  ❌ Capture failed — skipping"
        FAIL_CAPTURE=$((FAIL_CAPTURE + 1))
        echo "  └──────────────────────────────────────────────"
        sleep $INTERVAL_SECONDS
        continue
    fi
    echo "  │  ✅ Captured : $(basename $LATEST_IMG)"

    # Step 2: SCP (short timeout for burst context)
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    echo "  │  [C/2] 📤 Transferring to VM..."
    scp -o ConnectTimeout=8 "$LATEST_IMG" $VM:~/soil_moisture/incoming/burst_${TIMESTAMP}.jpg 2>/dev/null

    if [ $? -ne 0 ]; then
        echo "  │  ❌ SCP failed — possible backlog detected"
        FAIL_SCP=$((FAIL_SCP + 1))
        echo "  └──────────────────────────────────────────────"
        sleep $INTERVAL_SECONDS
        continue
    fi
    echo "  │  ✅ Transferred : burst_${TIMESTAMP}.jpg"

    # Step 3: Inference + MQTT (non-blocking)
    echo "  │  [C/3] 🤖 Inference on VM (async)..."
    ssh $VM "cd ~/soil_moisture && source venv/bin/activate && python src/predict_moisture.py incoming/burst_${TIMESTAMP}.jpg" &

    # Step 4: Backlog detection
    ITER_END=$(date +%s)
    ELAPSED=$(( ITER_END - ITER_START ))

    if [ $ELAPSED -gt $INTERVAL_SECONDS ]; then
        echo "  │  ⚠️  BACKLOG : iteration took ${ELAPSED}s (limit: ${INTERVAL_SECONDS}s)"
        BACKLOG_COUNT=$((BACKLOG_COUNT + 1))
    else
        echo "  │  ✅ On time : ${ELAPSED}s / ${INTERVAL_SECONDS}s"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    fi

    WAIT=$(( INTERVAL_SECONDS - ELAPSED ))
    [ $WAIT -gt 0 ] && sleep $WAIT

    echo "  └──────────────────────────────────────────────"
done

wait  # Let any lingering inference jobs finish

END_TIME=$(date +%s)
TOTAL_ELAPSED=$(( (END_TIME - START_TIME) / 60 ))

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   ✅ EXPERIMENT C — COMPLETED            ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  📊 Summary:"
echo "     • Expected iterations  : $TOTAL_ITERATIONS"
echo "     • On-time successes    : $SUCCESS_COUNT"
echo "     • Capture failures     : $FAIL_CAPTURE"
echo "     • SCP failures         : $FAIL_SCP"
echo "     • Backlog events       : $BACKLOG_COUNT"
echo "     • Total duration       : ${TOTAL_ELAPSED} min"
echo "     • Finished             : $(date)"
echo ""
echo "  💡 Check ThingsBoard for gaps, delays, or missing points."
echo "  💡 Backlog count → key metric for To-Be improvements."
echo ""