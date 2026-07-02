from flask import Blueprint, request, jsonify, current_app
import os
import time
import traceback
import json
import gc  # ADDED: for garbage collection

import pytesseract
from PIL import Image
import pdf2image
from pdf2image import convert_from_path, pdfinfo_from_path  # ADDED: specific imports
import docx
import cv2
import numpy as np

from werkzeug.utils import secure_filename
from config import Config, POPPLER_PATH

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
        print(f"✅ File saved: {upload_path}")

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
            try:
                # OPTIMIZED: Process one page at a time to save memory
                info = pdfinfo_from_path(
                    upload_path,
                    poppler_path=POPPLER_PATH if os.name == "nt" else None
                )

                total_pages = info["Pages"]

                print(f"📄 Processing {total_pages} pages")

                all_conf = []

                for page in range(1, total_pages + 1):
                    images = None
                    img = None

                    try:
                        images = convert_from_path(
                            upload_path,
                            first_page=page,
                            last_page=page,
                            dpi=120,
                            fmt="jpeg",
                            poppler_path=POPPLER_PATH if os.name == "nt" else None
                        )

                        if not images:
                            continue

                        img = images[0]

                        page_text = pytesseract.image_to_string(
                            img,
                            lang=tesseract_lang,
                            config="--psm 6 --oem 3"
                        )

                        # DEBUG: Print the extracted text for each page
                        print(f"\n===== PAGE {page} OCR =====")
                        print(f"Text length: {len(page_text)}")
                        print(f"First 500 characters:")
                        print(repr(page_text[:500]))
                        print("===========================\n")

                        extracted_text += f"\n--- Page {page} ---\n{page_text}"

                        conf = calculate_confidence(img, tesseract_lang)
                        all_conf.append(conf)

                        print(f"Page {page}/{total_pages} - Confidence: {conf}%")

                    finally:
                        if img:
                            img.close()
                            del img

                        if images:
                            del images

                        gc.collect()

                confidence = round(sum(all_conf)/len(all_conf),2) if all_conf else 0
                
                # DEBUG: Print final extracted text before returning
                print("\n" + "="*50)
                print("FINAL EXTRACTED TEXT SUMMARY:")
                print("="*50)
                print(f"TOTAL TEXT LENGTH: {len(extracted_text)}")
                print(f"FIRST 500 CHARACTERS:")
                print(repr(extracted_text[:500]))
                print(f"LAST 500 CHARACTERS:")
                print(repr(extracted_text[-500:]))
                print(f"CONFIDENCE: {confidence}%")
                print("="*50 + "\n")
                
            except Exception as e:
                print(f"❌ PDF processing error: {str(e)}")
                traceback.print_exc()
                return jsonify({'error': f'PDF processing failed: {str(e)}'}), 500

        elif filename.lower().endswith(".docx"):
            extracted_text = extract_docx(upload_path)
            confidence = 100

        else:
            # Image processing
            try:
                image = Image.open(upload_path)
                
                extracted_text = pytesseract.image_to_string(
                    image,
                    lang=tesseract_lang,
                    config="--psm 6 --oem 3"
                )

                confidence = calculate_confidence(image, tesseract_lang)
                
            except Exception as e:
                print(f"❌ Image processing error: {str(e)}")
                return jsonify({'error': f'Image processing failed: {str(e)}'}), 500

        # -------------------------------
        # Save output
        # -------------------------------
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(Config.OUTPUT_FOLDER, base_name)

        with open(output_path + ".txt", "w", encoding="utf-8") as f:
            f.write(extracted_text)

        with open(output_path + ".json", "w", encoding="utf-8") as f:
            json.dump({
                "text": extracted_text,
                "confidence": confidence,
                "engine": engine,
                "languages": languages,
                "processing_time": round(time.time() - start_time, 2)
            }, f, indent=2)

        # DEBUG: Log the response being sent to frontend
        print("\n" + "="*50)
        print("RESPONSE BEING SENT TO FRONTEND:")
        print("="*50)
        print(f"Success: True")
        print(f"Filename: {base_name}")
        print(f"Text length: {len(extracted_text)}")
        print(f"Text empty? {not extracted_text}")
        print(f"First 100 chars: {repr(extracted_text[:100])}")
        print(f"Confidence: {confidence}%")
        print("="*50 + "\n")

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
        print("❌ OCR ERROR:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500