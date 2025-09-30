
#!/bin/bash
pip install --upgrade pip# Install Tesseract OCR
apt-get update
apt-get install -y tesseract-ocr

# Start Flask app using gunicorn
gunicorn app:app --bind 0.0.0.0:$PORT
