import cv2
import time
import json
import os
from dotenv import load_dotenv
import requests
import paho.mqtt.client as mqtt
from datetime import datetime
import random

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

# HTTP image upload
IMAGE_UPLOAD_URL = f"https://{THINGSBOARD_HOST}/api/v1/{ACCESS_TOKEN}/attributes"

# =========================
# SETUP
# =========================
os.makedirs(SAVE_DIR, exist_ok=True)

# MQTT client
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, MQTT_PORT, 60)
client.loop_start()

# Webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open webcam")
    exit()

print("📷 Webcam + IoT pipeline started")

last_capture_time = time.time()

# =========================
# DUMMY HUMIDITY PREDICTOR
# =========================
def predict_humidity(image):
    """
    Replace this with your real ML model inference
    """
    return round(random.uniform(30, 90), 2)

# =========================
# MAIN LOOP
# =========================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Plant Monitoring", frame)

    current_time = time.time()

    if current_time - last_capture_time >= CAPTURE_INTERVAL:
        timestamp = datetime.utcnow().isoformat()

        # Save image locally
        filename = f"plant_{timestamp}.jpg"
        filepath = os.path.join(SAVE_DIR, filename)
        cv2.imwrite(filepath, frame)

        # Predict humidity
        humidity = predict_humidity(frame)

        # =========================
        # SEND TELEMETRY (MQTT)
        # =========================
        telemetry = {
            "humidity_percent": humidity,
            "prediction_time": timestamp
        }

        client.publish(MQTT_TOPIC, json.dumps(telemetry), qos=1)
        print(f"📡 Sent telemetry: {telemetry}")

        # =========================
        # SEND IMAGE (HTTP)
        # =========================
        with open(filepath, "rb") as image_file:
            files = {
                "plant_image": image_file
            }
            response = requests.post(IMAGE_UPLOAD_URL, files=files)

            if response.status_code == 200:
                print("🖼️ Image uploaded to ThingsBoard")
            else:
                print("⚠️ Image upload failed:", response.text)

        last_capture_time = current_time

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# =========================
# CLEANUP
# =========================
cap.release()
cv2.destroyAllWindows()
client.loop_stop()
client.disconnect()
print("👋 Shutdown complete")
