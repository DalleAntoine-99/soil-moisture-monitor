import cv2
import time
import json
import os
from dotenv import load_dotenv
import requests
import paho.mqtt.client as mqtt
from datetime import datetime
import random
from glob import glob

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

# =========================
# MAIN (run loop)
# =========================
if __name__ == '__main__':
    try:
        send_telemetries()
    finally:
        client.loop_stop()
        client.disconnect()
        print("👋 Shutdown complete")
