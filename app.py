from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import re
import io
import spacy

app = Flask(__name__)

# ----------------- SpaCy model -----------------
nlp = spacy.load("en_core_web_sm")

# ----------------- OCR + correction API -----------------
def process_and_correct_data(raw_text):
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

# ----------------- SpaCy text extraction API -----------------
def extract_any_category(text):
    numbers = re.findall(r"\d+(?:\.\d+)?", text)
    amount = float(numbers[0]) if numbers else None

    doc = nlp(text.lower())

    cat = None
    for token in doc:
        if token.text == "for" and token.i < len(doc)-1:
            phrase = []
            for t in doc[token.i+1:]:
                if t.is_punct:
                    break
                phrase.append(t.text)
            if phrase:
                cat = " ".join(phrase)
                break

    if not cat:
        noun_chunks = [chunk.text for chunk in doc.noun_chunks if chunk.text.strip()]
        if noun_chunks:
            cat = max(noun_chunks, key=len)

    return cat, amount

@app.route('/extract', methods=['POST'])
def extract():
    data = request.json
    texts = data.get("texts")
    if not texts or not isinstance(texts, list):
        return jsonify({"error": "Please provide a list of texts"}), 400

    results = {}
    for s in texts:
        cat, amt = extract_any_category(s)
        if cat is None:
            cat = s
        if amt is None or amt == 0:
            continue
        results[cat] = results.get(cat, 0) + amt

    return jsonify(results)

# ----------------- Run Flask -----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
