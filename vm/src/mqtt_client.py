import cv2
import time
import json
import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from glob import glob
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

# load environment from .env (if present)
load_dotenv()

# =========================
# CONFIGURATION (from env)
# =========================
THINGSBOARD_HOST = os.getenv("THINGSBOARD_HOST", "eu.thingsboard.cloud")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "YOUR_DEVICE_ACCESS_TOKEN")

# capture interval and save dir
CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", "5"))  # seconds
SAVE_DIR = os.getenv("SAVE_DIR", "plant_images")

# MQTT
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "v1/devices/me/telemetry")

# (image HTTP upload disabled - sending telemetry only)

# =========================
# SETUP
# =========================
os.makedirs(SAVE_DIR, exist_ok=True)

# MQTT client
client = mqtt.Client(callback_api_version=2)
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, MQTT_PORT, 60)
client.loop_start()


def get_predictions(path="logs/predictions"):
    json_paths = os.path.join(path, "*.json")
    json_files = glob(pathname=json_paths)
    telemetries = []
    
    for path in json_files:
        with open(path, 'r') as f:
            prediction_data = json.load(f)
            telemetry = {
                "moisture": prediction_data['prediction']['moisture_percent'],
                "uncertainty": prediction_data['prediction'].get('uncertainty'),
                "lower": prediction_data['prediction'].get('lower_bound'),
                "upper": prediction_data['prediction'].get('upper_bound'),
                "ts": prediction_data.get('timestamp_unix')
            }
            telemetries.append(telemetry)
    return telemetries

def send_telemetries():
    telemetries = get_predictions()
    for telemetry in telemetries:
        client.publish(MQTT_TOPIC, json.dumps(telemetry), qos=1)
        print(f"📡 Sent telemetry: {telemetry}")
    print(f"\nIn summary: {len(telemetries)} telemetry data sent.")

def send(path="logs/predictions"):
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    # process any existing files once
    processed_results = []
    for file in sorted(p.glob('*.json')):
        processed_results.append(_process_file(str(file), move_processed=True))
    print("\n === Files processing END ===")
    print(f"Number of files processed: {len(processed_results)}")
    print(f"And {sum(processed_results)} files successfully processed!")
    

def _process_file(path: str, move_processed: bool = True) -> bool:
    p = Path(path)
    try:
        with open(p, 'r') as f:
            prediction_data = json.load(f)
    except Exception as e:
        print(f"Failed to read {p}: {e}")
        return False

    telemetry = {
        "moisture": prediction_data['prediction']['moisture_percent'],
        "uncertainty": prediction_data['prediction'].get('uncertainty'),
        "lower": prediction_data['prediction'].get('lower_bound'),
        "upper": prediction_data['prediction'].get('upper_bound'),
        "ts": prediction_data.get('timestamp_unix')
    }

    try:
        info = client.publish(MQTT_TOPIC, json.dumps(telemetry), qos=1)
        if hasattr(info, 'wait_for_publish'):
            info.wait_for_publish(timeout=2)
        print(f"📡 Sent telemetry from {p.name}: {telemetry}")

        if move_processed:
            processed_dir = Path(p.parent) / 'processed'
            processed_dir.mkdir(parents=True, exist_ok=True)
            dest = processed_dir / p.name
            # avoid overwrite
            if dest.exists():
                dest = processed_dir / f"{p.stem}_{int(time.time())}{p.suffix}"
            shutil.move(str(p), str(dest))
            print(f"Moved {p.name} -> {dest}")

        return True
    except Exception as e:
        print(f"Failed to publish {p}: {e}")
        return False


class PredictionHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        p = Path(event.src_path)
        if p.suffix.lower() != '.json':
            return
        # Small delay to allow file writer to finish
        time.sleep(0.2)
        _process_file(str(p), move_processed=True)


def watch_and_send(path: str = 'logs/predictions'):
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    # process any existing files once
    for file in sorted(p.glob('*.json')):
        _process_file(str(file), move_processed=True)

    observer = Observer()
    handler = PredictionHandler()
    observer.schedule(handler, str(p), recursive=False)
    observer.start()
    print(f"Watching {p} for new prediction JSON files...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# =========================
# MAIN (run loop)
# =========================
if __name__ == '__main__':
    try:
        send()
        # watch_and_send('logs/predictions')
    finally:
        client.loop_stop()
        client.disconnect()
        print("👋 Shutdown complete")
