from flask import Blueprint, request, jsonify, current_app
import os
import time
import traceback
import json
import gc

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pdf2image
from pdf2image import convert_from_path, pdfinfo_from_path
import docx
import cv2
import numpy as np

from werkzeug.utils import secure_filename
from config import Config, POPPLER_PATH

# ✅ Import OCR Factory for all engines
from services.ocr_factory import OCRFactory

ocr_bp = Blueprint('ocr', __name__)


# ===============================
# Ensure folders exist
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
# Tesseract Confidence calculation
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
# Image Preprocessing Function
# ===============================
def preprocess_image_for_ocr(image):
    """
    Preprocess image for better OCR results
    """
    try:
        # Convert PIL to OpenCV
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # 2. Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        # 3. Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # 4. Resize if too small
        height, width = thresh.shape
        if height < 1000 or width < 1000:
            scale = 2.0
            new_width = int(width * scale)
            new_height = int(height * scale)
            thresh = cv2.resize(thresh, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Convert back to PIL
        pil_image = Image.fromarray(thresh)
        
        # Convert to RGB for OCR engines
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        return pil_image
        
    except Exception as e:
        print(f"⚠️ Image preprocessing error: {str(e)}")
        return image


# ===============================
# MAIN OCR ROUTE - FIXED WITH ALL ENGINES
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

        print("=" * 60)
        print(f"📊 REQUEST RECEIVED:")
        print(f"   Engine: {engine}")
        print(f"   Language: {language_param}")
        print("=" * 60)

        languages = language_param.replace("+", ",").split(",")
        languages = [l.strip() for l in languages if l.strip()]
        tesseract_lang = "+".join(languages)

        extracted_text = ""
        confidence = 0
        confidence_details = {}

        # ===============================
        # ✅ TESSERACT ENGINE
        # ===============================
        if engine == 'tesseract':
            print("🔍 Using Tesseract OCR Engine")
            
            if filename.lower().endswith(".pdf"):
                try:
                    info = pdfinfo_from_path(
                        upload_path,
                        poppler_path=POPPLER_PATH if os.name == "nt" else None
                    )

                    total_pages = info["Pages"]
                    print(f"📄 Processing {total_pages} pages with Tesseract")

                    all_conf = []

                    for page in range(1, total_pages + 1):
                        images = None
                        img = None

                        try:
                            # ✅ Increased DPI to 300 for better quality
                            images = convert_from_path(
                                upload_path,
                                first_page=page,
                                last_page=page,
                                dpi=300,  # ✅ Changed from 120 to 300
                                fmt="jpeg",
                                poppler_path=POPPLER_PATH if os.name == "nt" else None
                            )

                            if not images:
                                continue

                            img = images[0]
                            
                            # ✅ Preprocess image for better OCR
                            img = preprocess_image_for_ocr(img)

                            page_text = pytesseract.image_to_string(
                                img,
                                lang=tesseract_lang,
                                config="--psm 6 --oem 3"
                            )

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
                    
                except Exception as e:
                    print(f"❌ PDF processing error: {str(e)}")
                    traceback.print_exc()
                    return jsonify({'error': f'PDF processing failed: {str(e)}'}), 500

            elif filename.lower().endswith(".docx"):
                extracted_text = extract_docx(upload_path)
                confidence = 100

            else:
                try:
                    image = Image.open(upload_path)
                    # ✅ Preprocess image for better OCR
                    image = preprocess_image_for_ocr(image)
                    
                    extracted_text = pytesseract.image_to_string(
                        image,
                        lang=tesseract_lang,
                        config="--psm 6 --oem 3"
                    )
                    confidence = calculate_confidence(image, tesseract_lang)
                    
                except Exception as e:
                    print(f"❌ Image processing error: {str(e)}")
                    return jsonify({'error': f'Image processing failed: {str(e)}'}), 500

        # ===============================
        # ✅ EASYOCR ENGINE
        # ===============================
        elif engine == 'easyocr':
            print("🔍 Using EasyOCR Engine")
            
            try:
                from services.easyocr import get_easyocr_service
                
                easyocr_service = get_easyocr_service(languages, gpu=False)
                
                if filename.lower().endswith('.pdf'):
                    # ✅ Increased DPI to 300
                    images = convert_from_path(
                        upload_path,
                        poppler_path=POPPLER_PATH if os.name == "nt" else None,
                        dpi=300  # ✅ Changed from 150 to 300
                    )
                    
                    # ✅ Preprocess each image
                    preprocessed_images = [preprocess_image_for_ocr(img) for img in images]
                    
                    result = easyocr_service.extract_text_from_pdf(preprocessed_images)
                    
                    if result['status'] == 'success':
                        extracted_text = result['full_text']
                        confidence = result['overall_confidence']
                    else:
                        return jsonify({'error': 'EasyOCR PDF processing failed'}), 500
                        
                elif filename.lower().endswith('.docx'):
                    extracted_text = extract_docx(upload_path)
                    confidence = 100
                    
                else:
                    pil_image = Image.open(upload_path)
                    # ✅ Preprocess image
                    pil_image = preprocess_image_for_ocr(pil_image)
                    
                    result = easyocr_service.extract_text(pil_image)
                    
                    if result['status'] == 'success':
                        extracted_text = result['text']
                        confidence = result['confidence']
                    else:
                        return jsonify({'error': 'EasyOCR processing failed'}), 500
                
                print(f"📊 EasyOCR Confidence: {confidence}%")
                
            except Exception as e:
                print(f"❌ EasyOCR error: {str(e)}")
                traceback.print_exc()
                return jsonify({'error': f'EasyOCR failed: {str(e)}'}), 500

        # ===============================
        # ✅ SURYA ENGINE - FIXED
        # ===============================
        elif engine == 'surya':
            print("=" * 60)
            print("🔍 USING SURYA OCR ENGINE")
            print("=" * 60)
            
            try:
                # Get Surya engine from factory
                surya_engine = OCRFactory.get_engine('surya')
                print(f"✅ Surya engine obtained: {type(surya_engine).__name__}")
                
                if filename.lower().endswith('.pdf'):
                    # ✅ Increased DPI to 300 for better quality
                    images = convert_from_path(
                        upload_path,
                        poppler_path=POPPLER_PATH if os.name == "nt" else None,
                        dpi=300  # ✅ Changed from 150 to 300
                    )
                    
                    total_pages = len(images)
                    print(f"📄 Processing {total_pages} pages with Surya (DPI=300)")
                    
                    texts = []
                    confidences = []
                    
                    for i, image in enumerate(images):
                        current_page = i + 1
                        print(f"📄 Processing page {current_page}/{total_pages}...")
                        
                        # ✅ Preprocess image before saving
                        preprocessed_img = preprocess_image_for_ocr(image)
                        
                        temp_path = os.path.join(Config.TEMP_FOLDER, f"temp_surya_page_{i}.png")
                        preprocessed_img.save(temp_path, quality=95)
                        
                        # ✅ Call Surya with languages parameter
                        result = surya_engine.extract_text(temp_path, languages=languages)
                        
                        page_text = result.get('text', '').strip()
                        texts.append(f"--- Page {current_page} ---\n{page_text}")
                        confidences.append(result.get('confidence', 0))
                        
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        
                        print(f"  Page {current_page}: {len(page_text)} chars, Confidence: {result.get('confidence', 0)}%")
                    
                    extracted_text = "\n\n".join(texts)
                    confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0
                    
                elif filename.lower().endswith('.docx'):
                    extracted_text = extract_docx(upload_path)
                    confidence = 100
                    print("⚠️ DOCX processed with fallback")
                    
                else:
                    # ✅ Preprocess image
                    pil_image = Image.open(upload_path)
                    preprocessed_img = preprocess_image_for_ocr(pil_image)
                    
                    # Save preprocessed image
                    temp_path = os.path.join(Config.TEMP_FOLDER, "temp_surya_image.png")
                    preprocessed_img.save(temp_path, quality=95)
                    
                    result = surya_engine.extract_text(temp_path, languages=languages)
                    
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    extracted_text = result.get('text', '')
                    confidence = result.get('confidence', 0)
                
                print(f"📊 Surya Confidence: {confidence}%")
                print(f"📊 Surya Text length: {len(extracted_text)}")
                print("=" * 60)
                
            except ImportError as e:
                print(f"❌ Surya import error: {str(e)}")
                return jsonify({
                    'error': 'Surya OCR is not installed. Please run: pip install surya-ocr'
                }), 500
                
            except Exception as e:
                print(f"❌ Surya error: {str(e)}")
                traceback.print_exc()
                return jsonify({'error': f'Surya failed: {str(e)}'}), 500

        # ===============================
        # ✅ PADDLE ENGINE - FIXED
        # ===============================
        elif engine == 'paddle':
            print("=" * 60)
            print("🔍 USING PADDLE OCR ENGINE")
            print("=" * 60)
            
            try:
                # Get Paddle engine from factory
                paddle_engine = OCRFactory.get_engine('paddle')
                print(f"✅ Paddle engine obtained: {type(paddle_engine).__name__}")
                
                if filename.lower().endswith('.pdf'):
                    # ✅ Increased DPI to 300
                    images = convert_from_path(
                        upload_path,
                        poppler_path=POPPLER_PATH if os.name == "nt" else None,
                        dpi=300  # ✅ Changed from 150 to 300
                    )
                    
                    print(f"📄 Processing {len(images)} pages with Paddle (DPI=300)")
                    
                    # ✅ Preprocess each image
                    preprocessed_images = [preprocess_image_for_ocr(img) for img in images]
                    
                    # Save preprocessed images and process
                    all_texts = []
                    all_confidences = []
                    
                    for i, img in enumerate(preprocessed_images):
                        current_page = i + 1
                        temp_path = os.path.join(Config.TEMP_FOLDER, f"temp_paddle_page_{i}.png")
                        img.save(temp_path, quality=95)
                        
                        result = paddle_engine.extract_text(temp_path, languages=languages)
                        
                        page_text = result.get('text', '').strip()
                        all_texts.append(f"--- Page {current_page} ---\n{page_text}")
                        all_confidences.append(result.get('confidence', 0))
                        
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        
                        print(f"  Page {current_page}: {len(page_text)} chars, Confidence: {result.get('confidence', 0)}%")
                    
                    extracted_text = "\n\n".join(all_texts)
                    confidence = round(sum(all_confidences) / len(all_confidences), 2) if all_confidences else 0
                    
                elif filename.lower().endswith('.docx'):
                    extracted_text = extract_docx(upload_path)
                    confidence = 100
                    print("⚠️ DOCX processed with fallback")
                    
                else:
                    # ✅ Preprocess image
                    pil_image = Image.open(upload_path)
                    preprocessed_img = preprocess_image_for_ocr(pil_image)
                    
                    temp_path = os.path.join(Config.TEMP_FOLDER, "temp_paddle_image.png")
                    preprocessed_img.save(temp_path, quality=95)
                    
                    result = paddle_engine.extract_text(temp_path, languages=languages)
                    
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    
                    extracted_text = result.get('text', '')
                    confidence = result.get('confidence', 0)
                
                print(f"📊 Paddle Confidence: {confidence}%")
                print(f"📊 Paddle Text length: {len(extracted_text)}")
                print("=" * 60)
                
            except ImportError as e:
                print(f"❌ Paddle import error: {str(e)}")
                return jsonify({
                    'error': 'PaddleOCR is not installed. Please run: pip install paddlepaddle paddleocr'
                }), 500
                
            except Exception as e:
                print(f"❌ Paddle error: {str(e)}")
                traceback.print_exc()
                return jsonify({'error': f'Paddle failed: {str(e)}'}), 500

        # ===============================
        # UNSUPPORTED ENGINE
        # ===============================
        else:
            print(f"❌ Unsupported engine: {engine}")
            return jsonify({'error': f'Unsupported engine: {engine}'}), 400

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

        # DEBUG: Log the response
        print("\n" + "=" * 50)
        print("✅ RESPONSE BEING SENT:")
        print("=" * 50)
        print(f"   Engine: {engine}")
        print(f"   Confidence: {confidence}%")
        print(f"   Text length: {len(extracted_text)}")
        if extracted_text:
            print(f"   First 100 chars: {repr(extracted_text[:100])}")
        else:
            print("   ⚠️ WARNING: No text extracted!")
        print("=" * 50 + "\n")

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