from flask import Blueprint, request, jsonify
import os
import time
from werkzeug.utils import secure_filename
from config import Config
import pytesseract
from PIL import Image
import pdf2image
import docx
import cv2
import numpy as np

ocr_bp = Blueprint('ocr', __name__, url_prefix='/api')

# ✅ Ensure upload folder exists before saving
def ensure_upload_folder():
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    return Config.UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@ocr_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        start_time = time.time()
        
        # Check if file exists
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # ✅ Ensure upload directory exists
        upload_folder = ensure_upload_folder()
        output_folder = Config.OUTPUT_FOLDER
        os.makedirs(output_folder, exist_ok=True)
        
        # ✅ Save file with secure filename
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        
        # ✅ Handle duplicate filenames
        counter = 1
        base, ext = os.path.splitext(filename)
        while os.path.exists(filepath):
            filename = f"{base}_{counter}{ext}"
            filepath = os.path.join(upload_folder, filename)
            counter += 1
        
        file.save(filepath)
        
        # ✅ Verify file was saved
        if not os.path.exists(filepath):
            return jsonify({'error': 'Failed to save file'}), 500
        
        file_size = os.path.getsize(filepath)
        print(f"✅ File saved: {filepath} ({file_size} bytes)")
        
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
        
        # Get parameters
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
        print(f"🔍 File: {filepath}")
        
        # ===============================
        # PROCESS THE FILE
        # ===============================
        extracted_text = ""
        exact_confidence = 0
        confidence_data = {}
        
        if filename.lower().endswith('.pdf'):
            try:
                progress['stage'] = 'converting'
                progress['message'] = 'Converting PDF to images...'
                
                images = pdf2image.convert_from_path(
                    filepath,
                    poppler_path=Config.POPPLER_PATH,
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
                    
                    # Process image
                    if any(lang in ['kan', 'hin', 'tam', 'tel', 'mal', 'ben', 'guj', 'mar', 'ori', 'pan', 'urd'] for lang in languages):
                        # Indic language preprocessing
                        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                        temp_path = os.path.join(Config.TEMP_FOLDER, f"temp_page_{i}.png")
                        cv2.imwrite(temp_path, img_cv)
                        # Preprocess for indic languages
                        processed_img = preprocess_for_indic_languages(temp_path)
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
                    
                    # Calculate confidence
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
                    'languages': languages
                }
                
                progress['percentage'] = 100
                progress['message'] = 'Complete!'
                
                print(f"📊 Overall Confidence: {exact_confidence}%")
                
            except Exception as e:
                print(f"❌ PDF processing error: {str(e)}")
                return jsonify({'error': f'PDF processing failed: {str(e)}'}), 500
        
        # Save output
        base_name = os.path.splitext(filename)[0]
        output_file = f"{base_name}_output"
        output_path = os.path.join(Config.OUTPUT_FOLDER, output_file)
        
        with open(f"{output_path}.txt", 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        
        processing_time = round(time.time() - start_time, 2)
        
        return jsonify({
            'success': True,
            'extracted_text': extracted_text,
            'filename': output_file,
            'engine': engine,
            'languages': languages,
            'exact_confidence': exact_confidence,
            'confidence_details': confidence_data,
            'processing_time': processing_time,
            'progress': progress
        })
        
    except Exception as e:
        print(f"❌ OCR Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Helper functions
def preprocess_for_indic_languages(image_path):
    # Your preprocessing function here
    pass

def calculate_tesseract_confidence(image, lang):
    # Your confidence calculation here
    pass