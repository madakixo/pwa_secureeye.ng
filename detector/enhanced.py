#!/usr/bin/env python3
import cv2, face_recognition, easyocr, requests, os, time
from ultralytics import YOLO
from datetime import datetime

model = YOLO('yolov8n.pt')
reader = easyocr.Reader(['en'], gpu=False)

def send_alert(name, plate=""):
    msg = f"Person Detected: {name}\nPlate: {plate or 'None'}"
    requests.post("https://api.callmebot.com/whatsapp.php", 
                  params={"phone": os.getenv("WHATSAPP_TO"), "text": msg, "apikey": os.getenv("CALLMEBOT_KEY")})

while True:
    ret, frame = cv2.VideoCapture(0).read()
    if not ret: continue

    results = model(frame, classes=[0])
    if len(results[0].boxes) > 0:
        # Face + Plate logic here (same as v12)
        send_alert("Jay Korrupt", "KJA 123 AB")
        # Upload photo/video
