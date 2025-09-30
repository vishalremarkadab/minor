#!/bin/bash
# Upgrade pip first
pip install --upgrade pip

# Install Tesseract OCR
apt-get update
apt-get install -y tesseract-ocr

# Install Python dependencies
pip install -r requirements.txt

# Download SpaCy English model
python -m spacy download en_core_web_sm

# Start Flask app
gunicorn app:app --bind 0.0.0.0:$PORT
