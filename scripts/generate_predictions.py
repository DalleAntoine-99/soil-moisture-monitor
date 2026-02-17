#!/usr/bin/env python3
import json
import os
from datetime import datetime, timedelta

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs', 'predictions')
OUT_DIR = os.path.normpath(OUT_DIR)

os.makedirs(OUT_DIR, exist_ok=True)

start = datetime.now()
count = 100

for i in range(count):
    ts = start + timedelta(minutes=i)
    ts_str = ts.strftime('%Y-%m-%dT%H:%M:%S.%f')
    fname_ts = ts.strftime('%Y%m%d_%H%M%S')
    moisture = float(min(20 + i, 100))
    lower = max(0.0, moisture - 10.0)
    upper = moisture + 10.0
    obj = {
        "timestamp": ts_str,
        "timestamp_unix": int(ts.timestamp() * 1000),
        "image_path": f"incoming/soil_{fname_ts}.jpg",
        "prediction": {
            "moisture_percent": round(moisture, 2),
            "lower_bound": round(lower, 2),
            "upper_bound": round(upper, 2),
            "uncertainty": round(upper - moisture, 2)
        },
        "model_info": {
            "name": "ResNet-50 + Ridge Regression",
            "confidence_level": 0.95
        }
    }

    out_path = os.path.join(OUT_DIR, f"prediction_{fname_ts}.json")
    with open(out_path, 'w') as f:
        json.dump(obj, f, indent=2)

print(f"Wrote {count} prediction files to {OUT_DIR}")
