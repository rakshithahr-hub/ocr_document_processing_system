from flask import Blueprint, request, jsonify
import os
import time
import traceback
import json

import pytesseract
from PIL import Image
import pdf2image
import docx
import cv2
import numpy as np

from werkzeug.utils import secure_filename
from config import Config

ocr_bp = Blueprint('ocr', __name__, url_prefix='/api')


# ===============================
# Ensure folders exist (IMPORTANT for Render)
# ===============================
def ensure_directories():
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(Config.TEMP_FOLDER, exist_ok=True)


# ===============================
# Allowed file check
# ===============================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# ===============================
# DOCX extraction
# ===============================
def extract_docx(filepath):
    doc = docx.Document(filepath)
    return "\n".join([p.text for p in doc.paragraphs])


# ===============================
# Confidence calculation
# ===============================
def calculate_confidence(image, lang):
    try:
        data = pytesseract.image_to_data(
            image,
            lang=lang,
            output_type=pytesseract.Output.DICT,
            config="--psm 6 --oem 3"
        )

        confidences = []
        weights = []

        for i, text in enumerate(data["text"]):
            if text.strip():
                conf = int(data["conf"][i])
                if conf > 0:
                    confidences.append(conf)
                    weights.append(len(text))

        if not confidences:
            return 0

        return round(
            sum(c * w for c, w in zip(confidences, weights)) / sum(weights),
            2
        )

    except:
        return 0


# ===============================
# MAIN OCR ROUTE
# ===============================
@ocr_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        start_time = time.time()

        ensure_directories()

        # -------------------------------
        # Validate file
        # -------------------------------
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        # -------------------------------
        # Save file safely
        # -------------------------------
        filename = secure_filename(file.filename)
        upload_path = os.path.join(Config.UPLOAD_FOLDER, filename)

        counter = 1
        base, ext = os.path.splitext(filename)

        while os.path.exists(upload_path):
            filename = f"{base}_{counter}{ext}"
            upload_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            counter += 1

        file.save(upload_path)

        # -------------------------------
        # Get params
        # -------------------------------
        engine = request.form.get('engine', 'tesseract')
        language_param = request.form.get('language', 'eng')

        languages = language_param.replace("+", ",").split(",")
        languages = [l.strip() for l in languages if l.strip()]
        tesseract_lang = "+".join(languages)

        extracted_text = ""
        confidence = 0

        # -------------------------------
        # IMAGE / PDF / DOCX handling
        # -------------------------------
        if filename.lower().endswith(".pdf"):
            images = pdf2image.convert_from_path(
                upload_path,
                poppler_path=Config.POPPLER_PATH,
                dpi=150
            )

            all_conf = []

            for i, img in enumerate(images):
                page_text = pytesseract.image_to_string(
                    img,
                    lang=tesseract_lang,
                    config="--psm 6 --oem 3"
                )

                extracted_text += f"\n--- Page {i+1} ---\n{page_text}"

                conf = calculate_confidence(img, tesseract_lang)
                all_conf.append(conf)

            confidence = round(sum(all_conf) / len(all_conf), 2) if all_conf else 0

        elif filename.lower().endswith(".docx"):
            extracted_text = extract_docx(upload_path)
            confidence = 100

        else:
            image = Image.open(upload_path)

            extracted_text = pytesseract.image_to_string(
                image,
                lang=tesseract_lang,
                config="--psm 6 --oem 3"
            )

            confidence = calculate_confidence(image, tesseract_lang)

        # -------------------------------
        # Save output
        # -------------------------------
        base_name = os.path.splitext(filename)[0]
        output_file = os.path.join(Config.OUTPUT_FOLDER, base_name)

        with open(output_file + ".txt", "w", encoding="utf-8") as f:
            f.write(extracted_text)

        with open(output_file + ".json", "w", encoding="utf-8") as f:
            json.dump({
                "text": extracted_text,
                "confidence": confidence,
                "engine": engine,
                "languages": languages,
                "processing_time": round(time.time() - start_time, 2)
            }, f, indent=2)

        # -------------------------------
        # Response
        # -------------------------------
        return jsonify({
            "success": True,
            "filename": base_name,
            "text": extracted_text,
            "confidence": confidence,
            "engine": engine,
            "languages": languages,
            "processing_time": round(time.time() - start_time, 2)
        })

    except Exception as e:
        print("OCR ERROR:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500