#!/usr/bin/env python3
import cv2
import face_recognition
import easyocr
import requests
import os
import time
import logging
from ultralytics import YOLO
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load models
model = YOLO('yolov8n.pt')
reader = easyocr.Reader(['en'], gpu=False)

# Environment variables
CAMERA_URL = os.getenv("CAMERA_URL", "0") # Default to local camera if not set
WHATSAPP_TO = os.getenv("WHATSAPP_TO")
CALLMEBOT_KEY = os.getenv("CALLMEBOT_KEY")

def send_alert(message, image_path=None):
    logger.info(f"Sending alert: {message}")
    if not WHATSAPP_TO or not CALLMEBOT_KEY:
        logger.warning("WhatsApp credentials not set. Skipping alert.")
        return

    params = {
        "phone": WHATSAPP_TO,
        "text": message,
        "apikey": CALLMEBOT_KEY
    }
    try:
        res = requests.post("https://api.callmebot.com/whatsapp.php", params=params)
        if res.status_code == 200:
            logger.info("Alert sent successfully")
        else:
            logger.error(f"Failed to send alert: {res.text}")
    except Exception as e:
        logger.error(f"Error sending alert: {e}")

def process_frame(frame):
    # Detect persons
    results = model(frame, classes=[0], verbose=False)

    for result in results:
        if len(result.boxes) > 0:
            logger.info("Person detected!")

            # Here we would normally do face recognition and OCR
            # For now, we'll simulate finding a person
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            send_alert(f"SECUREEYE ALERT: Person detected at {timestamp} on camera {CAMERA_URL}")

            # Rate limit alerts
            time.sleep(10)

def main():
    logger.info(f"Starting detector on {CAMERA_URL}")

    # Try to open the camera
    cap = cv2.VideoCapture(CAMERA_URL if CAMERA_URL != "0" else 0)

    if not cap.isOpened():
        logger.error(f"Could not open camera: {CAMERA_URL}")
        return

    last_process_time = 0
    process_interval = 2 # Process every 2 seconds to save CPU

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to grab frame. Retrying...")
                time.sleep(5)
                cap = cv2.VideoCapture(CAMERA_URL if CAMERA_URL != "0" else 0)
                continue

            current_time = time.time()
            if current_time - last_process_time > process_interval:
                process_frame(frame)
                last_process_time = current_time

            # Small sleep to prevent 100% CPU usage if everything is fast
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("Detector stopping...")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
