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
import traceback

# Import sanitizer
from utils.file_sanitizer import file_sanitizer

# Poppler path for Windows
POPPLER_PATH = Config.POPPLER_PATH

# ===============================
# Language mapping
# ===============================
LANGUAGE_MAP = {
    'eng': 'English',
    'kan': 'Kannada',
    'hin': 'Hindi',
    'tam': 'Tamil',
    'tel': 'Telugu',
    'mal': 'Malayalam',
    'ben': 'Bengali',
    'guj': 'Gujarati',
    'mar': 'Marathi',
    'ori': 'Odia',
    'pan': 'Punjabi',
    'urd': 'Urdu',
    'fra': 'French',
    'deu': 'German',
    'spa': 'Spanish',
    'ita': 'Italian',
    'por': 'Portuguese',
    'rus': 'Russian',
    'jpn': 'Japanese',
    'kor': 'Korean',
    'chi_sim': 'Chinese (Simplified)',
    'chi_tra': 'Chinese (Traditional)'
}

DEFAULT_LANGUAGES = [
    {'code': 'eng', 'name': 'English'},
    {'code': 'kan', 'name': 'Kannada'},
    {'code': 'hin', 'name': 'Hindi'},
    {'code': 'tam', 'name': 'Tamil'},
    {'code': 'tel', 'name': 'Telugu'},
    {'code': 'mal', 'name': 'Malayalam'},
    {'code': 'ben', 'name': 'Bengali'},
    {'code': 'guj', 'name': 'Gujarati'},
    {'code': 'mar', 'name': 'Marathi'},
    {'code': 'ori', 'name': 'Odia'},
    {'code': 'pan', 'name': 'Punjabi'},
    {'code': 'urd', 'name': 'Urdu'},
    {'code': 'fra', 'name': 'French'},
    {'code': 'deu', 'name': 'German'},
    {'code': 'spa', 'name': 'Spanish'},
    {'code': 'ita', 'name': 'Italian'},
    {'code': 'por', 'name': 'Portuguese'},
    {'code': 'rus', 'name': 'Russian'},
    {'code': 'jpn', 'name': 'Japanese'},
    {'code': 'kor', 'name': 'Korean'},
    {'code': 'chi_sim', 'name': 'Chinese (Simplified)'},
    {'code': 'chi_tra', 'name': 'Chinese (Traditional)'}
]

INDIC_LANGUAGES = ['kan', 'hin', 'tam', 'tel', 'mal', 'ben', 'guj', 'mar', 'ori', 'pan', 'urd']

# ===============================
# HELPER FUNCTIONS
# ===============================

def ensure_directories():
    """Ensure all required directories exist"""
    folders = [
        Config.UPLOAD_FOLDER,
        Config.OUTPUT_FOLDER,
        Config.TEMP_FOLDER
    ]
    for folder in folders:
        try:
            os.makedirs(folder, exist_ok=True)
        except Exception as e:
            print(f"⚠️ Could not create directory {folder}: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def extract_text_from_docx(filepath):
    """Extract text from DOCX file using python-docx"""
    try:
        doc = docx.Document(filepath)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return '\n'.join(full_text)
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")

def is_indic_language(languages):
    """Check if any of the languages are Indic languages"""
    for lang in languages:
        if lang in INDIC_LANGUAGES:
            return True
    return False

def get_language_names(language_codes):
    """Convert language codes to display names"""
    names = []
    for code in language_codes:
        if code in LANGUAGE_MAP:
            names.append(LANGUAGE_MAP[code])
        else:
            names.append(code)
    return names

def get_language_display(language_codes):
    """Get display string for languages (e.g., 'English + Kannada')"""
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
# TESSERACT CONFIDENCE CALCULATION
# ===============================
def calculate_tesseract_confidence(image, lang):
    """Calculates confidence for Tesseract OCR"""
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
# GET LANGUAGES
# ===============================
def get_languages():
    """Controller to get available languages for OCR"""
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
# UPLOAD FILE - MAIN CONTROLLER
# ===============================
def upload_file():
    """Controller to handle file upload and OCR processing with sanitization and progress"""
    try:
        start_time = time.time()
        
        # ✅ Ensure directories exist
        ensure_directories()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # ===============================
        # FILE SANITIZATION
        # ===============================
        try:
            is_safe, sanitize_result = file_sanitizer.sanitize(file)
            if not is_safe:
                return jsonify({'error': sanitize_result}), 400
        except Exception as e:
            print(f"⚠️ Sanitization warning: {e}")
            # Continue even if sanitizer fails
        
        # ===============================
        # PROGRESS TRACKING
        # ===============================
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
        
        engine = request.form.get('engine', 'tesseract')
        language_param = request.form.get('language', 'eng')
        
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
        
        # ✅ Save file with secure filename
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # ✅ Handle duplicate filenames
        counter = 1
        base, ext = os.path.splitext(filename)
        while os.path.exists(filepath):
            filename = f"{base}_{counter}{ext}"
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            counter += 1
        
        file.save(filepath)
        
        # ✅ Verify file was saved
        if not os.path.exists(filepath):
            return jsonify({'error': 'Failed to save file'}), 500
        
        file_size = os.path.getsize(filepath)
        print(f"✅ File saved: {filepath} ({file_size} bytes)")
        
        extracted_text = ""
        exact_confidence = 0
        confidence_data = {}
        
        # ===============================
        # PROCESS WITH TESSERACT
        # ===============================
        print("🔍 Using Tesseract OCR Engine")
        progress['stage'] = 'ocr'
        progress['message'] = 'Starting Tesseract OCR...'
        
        if filename.lower().endswith('.pdf'):
            try:
                progress['stage'] = 'converting'
                progress['message'] = 'Converting PDF to images...'
                
                images = pdf2image.convert_from_path(
                    filepath, 
                    poppler_path=POPPLER_PATH,
                    dpi=150
                )
                total_pages = len(images)
                progress['total_pages'] = total_pages
                progress['stage'] = 'ocr'
                
                print(f"✅ Converted {total_pages} PDF pages")
                
                all_confidences = []
                
                for i, image in enumerate(images):
                    current_page = i + 1
                    progress['current_page'] = current_page
                    progress['percentage'] = round((current_page / total_pages) * 100, 1)
                    progress['message'] = f'Processing page {current_page}/{total_pages}...'
                    
                    print(f"📊 Progress: {progress['percentage']:.1f}% - Page {current_page}/{total_pages}")
                    
                    if is_indic_language(languages):
                        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                        temp_path = os.path.join(Config.TEMP_FOLDER, f"temp_page_{i}.png")
                        cv2.imwrite(temp_path, img_cv)
                        processed_img = ImagePreprocessor.preprocess_for_indic_languages(temp_path)
                        pil_image = Image.fromarray(processed_img)
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    else:
                        pil_image = image
                    
                    text = pytesseract.image_to_string(
                        pil_image,
                        lang=tesseract_langs,
                        config='--psm 6 --oem 3'
                    )
                    
                    extracted_text += f"\n--- Page {current_page} ---\n"
                    extracted_text += text + "\n"
                    
                    confidence_result = calculate_tesseract_confidence(pil_image, tesseract_langs)
                    all_confidences.append(confidence_result)
                    
                    print(f"📊 Page {current_page} Confidence: {confidence_result.get('exact_confidence', 0)}%")
                
                # Calculate overall confidence
                total_chars = sum([r.get('total_characters', 0) for r in all_confidences])
                if total_chars > 0:
                    weighted_sum = sum([r.get('exact_confidence', 0) * r.get('total_characters', 0) 
                                      for r in all_confidences])
                    exact_confidence = round(weighted_sum / total_chars, 2)
                
                confidence_data = {
                    'exact_confidence': exact_confidence,
                    'total_pages': total_pages,
                    'pages_processed': len([r for r in all_confidences if r.get('exact_confidence', 0) > 0]),
                    'engine': 'tesseract',
                    'languages': languages,
                    'language_display': get_language_display(languages)
                }
                
                progress['percentage'] = 100
                progress['message'] = 'Complete!'
                
                print(f"📊 Overall Confidence: {exact_confidence}%")
                
            except Exception as e:
                print(f"❌ PDF conversion error: {str(e)}")
                traceback.print_exc()
                return jsonify({'error': f'PDF conversion failed: {str(e)}'}), 500
                
        elif filename.lower().endswith('.docx'):
            try:
                extracted_text = extract_text_from_docx(filepath)
                exact_confidence = 100.0
                confidence_data = {
                    'exact_confidence': 100.0,
                    'total_pages': 1,
                    'engine': 'tesseract',
                    'languages': languages,
                    'language_display': get_language_display(languages)
                }
                progress['percentage'] = 100
                progress['message'] = 'Complete!'
            except Exception as e:
                return jsonify({'error': f'DOCX processing failed: {str(e)}'}), 500
        else:
            try:
                progress['message'] = 'Processing image...'
                progress['percentage'] = 50
                
                if is_indic_language(languages):
                    processed_img = ImagePreprocessor.preprocess_for_indic_languages(filepath)
                    pil_image = Image.fromarray(processed_img)
                else:
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
                    'total_pages': 1,
                    'engine': 'tesseract',
                    'languages': languages,
                    'language_display': get_language_display(languages)
                }
                
                progress['percentage'] = 100
                progress['message'] = 'Complete!'
                
                print(f"📊 Confidence: {exact_confidence}%")
                
            except Exception as e:
                print(f"❌ Image processing error: {str(e)}")
                traceback.print_exc()
                return jsonify({'error': f'Image processing failed: {str(e)}'}), 500
        
        # ===============================
        # SAVE OUTPUT
        # ===============================
        base_name = os.path.splitext(filename)[0]
        output_file = f"{base_name}_output"
        output_path = os.path.join(Config.OUTPUT_FOLDER, output_file)
        
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
        
        with open(f"{output_path}.txt", 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        
        processing_time = round(time.time() - start_time, 2)
        
        json_data = {
            'filename': output_file,
            'text': extracted_text,
            'engine': engine,
            'languages': languages,
            'language_display': get_language_display(languages),
            'exact_confidence': exact_confidence,
            'confidence_details': confidence_data,
            'processing_time': processing_time
        }
        with open(f"{output_path}.json", 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ OCR completed successfully in {processing_time} seconds!")
        
        return jsonify({
            'success': True,
            'extracted_text': extracted_text,
            'filename': output_file,
            'engine': engine,
            'languages': languages,
            'language_display': get_language_display(languages),
            'exact_confidence': exact_confidence,
            'confidence_details': confidence_data,
            'confidence': exact_confidence,
            'processing_time': processing_time,
            'progress': progress
        })
        
    except Exception as e:
        print(f"❌ OCR Error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500