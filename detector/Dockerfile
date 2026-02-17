FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y     libgl1-mesa-glx     libglib2.0-0     libsm6     libxext6     libxrender1     && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir     ultralytics     easyocr     opencv-python-headless     face_recognition     requests

COPY enhanced.py .

CMD ["python", "enhanced.py"]
