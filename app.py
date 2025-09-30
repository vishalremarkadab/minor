from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import re
import io

app = Flask(__name__)

def process_and_correct_data(raw_text):
    """Parses the text line by line and applies the correction logic."""
    extracted_data = {
        "item": "N/A",
        "amount": "N/A",
        "date": "N/A"
    }

    for line in raw_text.split('\n'):
        line_lower = line.lower().strip()

        if line_lower.startswith("item:"):
            extracted_data["item"] = line.split(":", 1)[-1].strip()
        elif line_lower.startswith("amount:"):
            raw_amount_string = line.split(":", 1)[-1].strip()
            corrected_amount_str = raw_amount_string.replace('/', '7')
            final_amount = re.sub(r'[^\d]', '', corrected_amount_str)
            extracted_data["amount"] = final_amount
        elif line_lower.startswith("date:"):
            extracted_data["date"] = line.split(":", 1)[-1].strip()

    return extracted_data

@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))
        raw_text = pytesseract.image_to_string(img).strip()
        corrected_data = process_and_correct_data(raw_text)
        return jsonify({"raw_text": raw_text, "corrected_data": corrected_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
