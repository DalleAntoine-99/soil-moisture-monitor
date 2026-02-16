import json
import os
import time
from pathlib import Path
from typing import Any, Dict

import yaml
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# load environment from .env (if present)
load_dotenv()


def _load_config(config_path: str = "vm/api/thingsboard_config.yaml") -> Dict[str, Any]:
    # prefer YAML config if present, otherwise fall back to environment
    p = Path(config_path)
    if p.exists():
        try:
            with open(p, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            pass
    # fallback env
    return {
        "host": os.getenv("THINGSBOARD_HOST", "eu.thingsboard.cloud"),
        "access_token": os.getenv("ACCESS_TOKEN", "YOUR_DEVICE_ACCESS_TOKEN"),
        "port": int(os.getenv("MQTT_PORT", "1883")),
        "topic": os.getenv("MQTT_TOPIC", "v1/devices/me/telemetry"),
    }


# load config and create a global MQTT client
_cfg = _load_config()
THINGSBOARD_HOST = _cfg.get("host", "thingsboard.cloud")
ACCESS_TOKEN = _cfg.get("access_token")
MQTT_PORT = int(_cfg.get("port", 1883))
MQTT_TOPIC = _cfg.get("topic", "v1/devices/me/telemetry")

_client: mqtt.Client = mqtt.Client(callback_api_version=2)
if ACCESS_TOKEN:
    _client.username_pw_set(ACCESS_TOKEN)

try:
    _client.connect(THINGSBOARD_HOST, MQTT_PORT, 60)
    _client.loop_start()
except Exception as e:
    print(f"Warning: failed to connect MQTT client at import time: {e}")


def send_telemetry(prediction_data: Dict[str, Any]) -> bool:
    """Publish telemetry using the module-level MQTT client.

    Returns True on successful publish acknowledgement (or if publish API
    indicates success), False otherwise.
    """
    telemetry = {
        "moisture": prediction_data['prediction']['moisture_percent'],
        "uncertainty": prediction_data['prediction'].get('uncertainty'),
        "lower": prediction_data['prediction'].get('lower_bound'),
        "upper": prediction_data['prediction'].get('upper_bound'),
        "ts": prediction_data.get('timestamp_unix')
    }

    try:
        info = _client.publish(MQTT_TOPIC, json.dumps(telemetry), qos=1)
        # MQTTMessageInfo: wait for publish to complete when available
        if hasattr(info, 'wait_for_publish'):
            info.wait_for_publish(timeout=2)
            ok = getattr(info, 'is_published', lambda: True)()
        else:
            # older paho returns (rc, mid)
            ok = True

        if not ok:
            print("Publish not confirmed")
            return False

        print(f"Telemetry sent to {THINGSBOARD_HOST}:{MQTT_PORT} topic={MQTT_TOPIC}")
        return True
    except Exception as e:
        print(f"Error publishing telemetry: {e}")
        return False


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python mqtt_client.py <prediction_json>")
        raise SystemExit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        raise SystemExit(2)

    with open(path, 'r') as f:
        data = json.load(f)

    print("Sending telemetry...")
    ok = send_telemetry(data)
    print("Publish result:", ok)

    try:
        _client.loop_stop()
        _client.disconnect()
    except Exception:
        pass
    