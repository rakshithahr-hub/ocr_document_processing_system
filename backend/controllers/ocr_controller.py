from flask import request, jsonify
import os
import pytesseract
from PIL import Image
import pdf2image
import docx
import json
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from config import Config
import time

# Import EasyOCR service
from services.easyocr import get_easyocr_service, EasyOCRService

# ✅ Import OCR Factory
from services.ocr_factory import OCRFactory

# Import sanitizer
from utils.file_sanitizer import file_sanitizer

# Poppler path for Windows
POPPLER_PATH = r"C:\poppler\bin"

# ===============================
# Language mapping
# ===============================
LANGUAGE_MAP = EasyOCRService.LANGUAGE_MAP

DEFAULT_LANGUAGES = [
    {'code': 'eng', 'name': 'English'},
    {'code': 'kan', 'name': 'Kannada'},
    # ... rest of languages
]

INDIC_LANGUAGES = ['kan', 'hin', 'tam', 'tel', 'mal', 'ben', 'guj', 'mar', 'ori', 'pan', 'urd']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def extract_text_from_docx(filepath):
    try:
        doc = docx.Document(filepath)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return '\n'.join(full_text)
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")

def is_indic_language(languages):
    for lang in languages:
        if lang in INDIC_LANGUAGES:
            return True
    return False

def get_language_names(language_codes):
    names = []
    for code in language_codes:
        if code in LANGUAGE_MAP:
            names.append(LANGUAGE_MAP[code])
        else:
            names.append(code)
    return names

def get_language_display(language_codes):
    names = get_language_names(language_codes)
    return ' + '.join(names)

# ===============================
# Image Preprocessor Class
# ===============================
class ImagePreprocessor:
    @staticmethod
    def grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def resize(image, scale=1.5):
        height, width = image.shape[:2]
        return cv2.resize(
            image,
            (int(width * scale), int(height * scale)),
            interpolation=cv2.INTER_CUBIC
        )

    @staticmethod
    def median_denoise(image):
        return cv2.medianBlur(image, 3)

    @staticmethod
    def preprocess(image_path):
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        image = ImagePreprocessor.resize(image)
        image = ImagePreprocessor.grayscale(image)
        image = ImagePreprocessor.median_denoise(image)
        image = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
        )
        return image

    @staticmethod
    def preprocess_for_indic_languages(image_path):
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        height, width = denoised.shape
        resized = cv2.resize(
            denoised,
            (int(width * 1.5), int(height * 1.5)),
            interpolation=cv2.INTER_CUBIC
        )
        
        _, thresh = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

# ===============================
# GET LANGUAGES
# ===============================
def get_languages():
    try:
        try:
            tesseract_langs = pytesseract.get_languages()
            available_languages = []
            
            for lang_code in tesseract_langs:
                if lang_code in LANGUAGE_MAP:
                    available_languages.append({
                        'code': lang_code,
                        'name': LANGUAGE_MAP[lang_code]
                    })
            
            if available_languages:
                return jsonify({
                    'languages': available_languages,
                    'total': len(available_languages),
                    'source': 'tesseract'
                })
        except Exception as e:
            print(f"Tesseract not available: {str(e)}")
        
        return jsonify({
            'languages': DEFAULT_LANGUAGES,
            'total': len(DEFAULT_LANGUAGES),
            'source': 'default'
        })
        
    except Exception as e:
        print(f"Error in get_languages: {str(e)}")
        return jsonify({
            'languages': DEFAULT_LANGUAGES,
            'total': len(DEFAULT_LANGUAGES),
            'source': 'default',
            'error': str(e)
        })

# ===============================
# TESSERACT CONFIDENCE CALCULATION
# ===============================
def calculate_tesseract_confidence(image, lang):
    try:
        data = pytesseract.image_to_data(
            image,
            lang=lang,
            output_type=pytesseract.Output.DICT,
            config='--psm 6 --oem 3'
        )
        
        word_confidences = []
        char_counts = []
        total_chars = 0
        
        for i, text in enumerate(data['text']):
            if text.strip():
                conf = int(data['conf'][i])
                if conf > 0:
                    char_count = len(text)
                    word_confidences.append(conf)
                    char_counts.append(char_count)
                    total_chars += char_count
        
        if not word_confidences or total_chars == 0:
            return {'exact_confidence': 0, 'total_characters': 0}
        
        weighted_sum = sum([conf * count for conf, count in zip(word_confidences, char_counts)])
        exact_confidence = round(weighted_sum / total_chars, 2)
        
        return {
            'exact_confidence': exact_confidence,
            'total_characters': total_chars,
            'total_words': len(word_confidences)
        }
        
    except Exception as e:
        print(f"Error calculating confidence: {e}")
        return {'exact_confidence': 0, 'total_characters': 0}

# ===============================
# UPLOAD FILE - FIXED
# ===============================
def upload_file():
    """Controller to handle file upload and OCR processing"""
    try:
        start_time = time.time()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # FILE SANITIZATION
        is_safe, sanitize_result = file_sanitizer.sanitize(file)
        if not is_safe:
            return jsonify({'error': sanitize_result}), 400
        
        # PROGRESS TRACKING
        progress = {
            'status': 'processing',
            'total_pages': 0,
            'current_page': 0,
            'percentage': 0,
            'stage': 'starting',
            'message': 'Starting OCR process...'
        }
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # ✅ Get engine from request
        engine = request.form.get('engine', 'tesseract')
        language_param = request.form.get('language', 'eng')
        
        print("=" * 60)
        print(f"🔍 REQUEST RECEIVED:")
        print(f"   Engine: {engine}")
        print(f"   Language: {language_param}")
        print("=" * 60)
        
        if '+' in language_param:
            languages = language_param.split('+')
        elif ',' in language_param:
            languages = language_param.split(',')
        else:
            languages = [language_param]
        
        languages = [lang.strip() for lang in languages if lang.strip()]
        tesseract_langs = '+'.join(languages)
        
        print(f"🔍 Processing with languages: {languages}")
        print(f"🔍 Engine: {engine}")
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        extracted_text = ""
        exact_confidence = 0
        confidence_data = {}
        
        # ===============================
        # ✅ TESSERACT ENGINE
        # ===============================
        if engine == 'tesseract':
            print("🔍 Using Tesseract OCR Engine")
            progress['stage'] = 'ocr'
            progress['message'] = 'Starting Tesseract OCR...'
            
            # ... Tesseract processing code (keep your existing code) ...
            # For brevity, I'm showing the simplified version
            # You should keep your full Tesseract implementation here
            
            try:
                pil_image = Image.open(filepath)
                extracted_text = pytesseract.image_to_string(
                    pil_image,
                    lang=tesseract_langs,
                    config='--psm 6 --oem 3'
                )
                confidence_result = calculate_tesseract_confidence(pil_image, tesseract_langs)
                exact_confidence = confidence_result.get('exact_confidence', 0)
                
                confidence_data = {
                    'exact_confidence': exact_confidence,
                    'engine': 'tesseract',
                    'languages': languages,
                    'language_display': get_language_display(languages)
                }
                
                progress['percentage'] = 100
                progress['message'] = 'Complete!'
                
                print(f"📊 Tesseract Confidence: {exact_confidence}%")
                
            except Exception as e:
                print(f"❌ Tesseract error: {str(e)}")
                return jsonify({'error': f'Tesseract failed: {str(e)}'}), 500
        
        # ===============================
        # ✅ EASYOCR ENGINE
        # ===============================
        elif engine == 'easyocr':
            print("🔍 Using EasyOCR Engine")
            progress['stage'] = 'ocr'
            progress['message'] = 'Starting EasyOCR...'
            
            try:
                easyocr_service = get_easyocr_service(languages, gpu=False)
                pil_image = Image.open(filepath)
                result = easyocr_service.extract_text(pil_image)
                
                if result['status'] == 'success':
                    extracted_text = result['text']
                    exact_confidence = result['confidence']
                    
                    confidence_data = {
                        'exact_confidence': exact_confidence,
                        'engine': 'easyocr',
                        'languages': languages,
                        'language_display': get_language_display(languages)
                    }
                    
                    progress['percentage'] = 100
                    progress['message'] = 'Complete!'
                    
                    print(f"📊 EasyOCR Confidence: {exact_confidence}%")
                else:
                    return jsonify({'error': 'EasyOCR processing failed'}), 500
                
            except Exception as e:
                print(f"❌ EasyOCR error: {str(e)}")
                return jsonify({'error': f'EasyOCR failed: {str(e)}'}), 500
        
        # ===============================
        # ✅ SURYA ENGINE
        # ===============================
        elif engine == 'surya':
            print("=" * 60)
            print("🔍 USING SURYA OCR ENGINE")
            print("=" * 60)
            
            try:
                # ✅ Get Surya engine from factory
                print("🔄 Getting Surya engine from factory...")
                surya_engine = OCRFactory.get_engine('surya')
                print(f"✅ Surya engine obtained: {type(surya_engine).__name__}")
                
                progress['message'] = 'Processing with Surya OCR...'
                progress['percentage'] = 30
                
                # ✅ Extract text with Surya
                print(f"🔄 Calling Surya extract_text for: {filepath}")
                result = surya_engine.extract_text(
                    filepath,
                    languages=languages
                )
                
                print(f"📊 Surya result: {result}")
                
                extracted_text = result.get('text', '')
                exact_confidence = result.get('confidence', 0)
                
                confidence_data = {
                    'exact_confidence': exact_confidence,
                    'engine': 'surya',
                    'languages': languages,
                    'language_display': get_language_display(languages),
                    'word_count': result.get('word_count', 0)
                }
                
                progress['percentage'] = 100
                progress['message'] = 'Complete!'
                
                print(f"📊 Surya Confidence: {exact_confidence}%")
                print(f"📊 Surya Text length: {len(extracted_text)}")
                print("=" * 60)
                
            except ImportError as e:
                print(f"❌ Surya import error: {str(e)}")
                return jsonify({
                    'error': 'Surya OCR is not installed. Please run: pip install surya-ocr'
                }), 500
                
            except Exception as e:
                print(f"❌ Surya OCR error: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'Surya OCR failed: {str(e)}'}), 500
        
        # ===============================
        # ✅ PADDLE ENGINE
        # ===============================
        elif engine == 'paddle':
            print("=" * 60)
            print("🔍 USING PADDLE OCR ENGINE")
            print("=" * 60)
            
            try:
                # ✅ Get Paddle engine from factory
                print("🔄 Getting Paddle engine from factory...")
                paddle_engine = OCRFactory.get_engine('paddle')
                print(f"✅ Paddle engine obtained: {type(paddle_engine).__name__}")
                
                progress['message'] = 'Processing with PaddleOCR...'
                progress['percentage'] = 30
                
                # ✅ Extract text with Paddle
                print(f"🔄 Calling Paddle extract_text for: {filepath}")
                result = paddle_engine.extract_text(
                    filepath,
                    languages=languages
                )
                
                print(f"📊 Paddle result: {result}")
                
                extracted_text = result.get('text', '')
                exact_confidence = result.get('confidence', 0)
                
                confidence_data = {
                    'exact_confidence': exact_confidence,
                    'engine': 'paddle',
                    'languages': languages,
                    'language_display': get_language_display(languages),
                    'word_count': result.get('word_count', 0)
                }
                
                progress['percentage'] = 100
                progress['message'] = 'Complete!'
                
                print(f"📊 Paddle Confidence: {exact_confidence}%")
                print(f"📊 Paddle Text length: {len(extracted_text)}")
                print("=" * 60)
                
            except ImportError as e:
                print(f"❌ Paddle import error: {str(e)}")
                return jsonify({
                    'error': 'PaddleOCR is not installed. Please run: pip install paddlepaddle paddleocr'
                }), 500
                
            except Exception as e:
                print(f"❌ Paddle OCR error: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'PaddleOCR failed: {str(e)}'}), 500
        
        # ===============================
        # UNSUPPORTED ENGINE
        # ===============================
        else:
            print(f"❌ Unsupported engine: {engine}")
            return jsonify({'error': f'Unsupported engine: {engine}'}), 400
        
        # ===============================
        # SAVE OUTPUT
        # ===============================
        base_name = os.path.splitext(filename)[0]
        output_file = f"{base_name}_output"
        output_path = os.path.join(Config.OUTPUT_FOLDER, output_file)
        
        # Save text file
        with open(f"{output_path}.txt", 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        
        processing_time = round(time.time() - start_time, 2)
        
        # ✅ Build response with engine
        response_data = {
            'success': True,
            'extracted_text': extracted_text,
            'text': extracted_text,  # Frontend expects 'text'
            'filename': output_file,
            'engine': engine,  # ✅ THIS IS CRITICAL
            'languages': languages,
            'language_display': get_language_display(languages),
            'confidence': exact_confidence,
            'exact_confidence': exact_confidence,
            'confidence_details': confidence_data,
            'processing_time': processing_time,
            'progress': progress
        }
        
        print("=" * 60)
        print(f"✅ RESPONSE SENT:")
        print(f"   Engine: {response_data['engine']}")
        print(f"   Confidence: {response_data['confidence']}")
        print(f"   Text length: {len(response_data['text'])}")
        print("=" * 60)
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ OCR Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500