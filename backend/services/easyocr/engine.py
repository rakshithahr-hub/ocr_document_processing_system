import easyocr
import numpy as np
import cv2
from PIL import Image
import time
import os

class EasyOCRService:
    """
    EasyOCR Service with support for multiple languages and confidence calculation.
    """
    
    # Language mapping for EasyOCR
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
    
    # EasyOCR uses different codes for some languages
    EASYOCR_LANG_MAP = {
        'eng': 'en',
        'kan': 'kn',      # Kannada
        'hin': 'hi',      # Hindi
        'tam': 'ta',      # Tamil
        'tel': 'te',      # Telugu
        'mal': 'ml',      # Malayalam
        'ben': 'bn',      # Bengali
        'guj': 'gu',      # Gujarati
        'mar': 'mr',      # Marathi
        'ori': 'or',      # Odia
        'pan': 'pa',      # Punjabi
        'urd': 'ur',      # Urdu
        'fra': 'fr',      # French
        'deu': 'de',      # German
        'spa': 'es',      # Spanish
        'ita': 'it',      # Italian
        'por': 'pt',      # Portuguese
        'rus': 'ru',      # Russian
        'jpn': 'ja',      # Japanese
        'kor': 'ko',      # Korean
        'chi_sim': 'ch_sim',  # Chinese Simplified
        'chi_tra': 'ch_tra'   # Chinese Traditional
    }
    
    def __init__(self, languages=None, gpu=False):
        """
        Initialize EasyOCR reader.
        
        Args:
            languages: List of language codes (e.g., ['en', 'kn'])
            gpu: Use GPU if available
        """
        self.languages = languages or ['en']
        self.gpu = gpu
        self.reader = None
        self._initialize_reader()
    
    def _initialize_reader(self):
        """Initialize the EasyOCR reader with specified languages."""
        try:
            # Convert to EasyOCR language codes
            easyocr_langs = []
            for lang in self.languages:
                if lang in self.EASYOCR_LANG_MAP:
                    easyocr_langs.append(self.EASYOCR_LANG_MAP[lang])
                else:
                    easyocr_langs.append(lang)
            
            print(f"🔍 Initializing EasyOCR with languages: {easyocr_langs}")
            
            # Create models directory if it doesn't exist
            os.makedirs('./models', exist_ok=True)
            
            self.reader = easyocr.Reader(
                easyocr_langs,
                gpu=self.gpu,
                model_storage_directory='./models',
                user_network_directory='./models',
                recog_network='standard'
            )
            print("✅ EasyOCR initialized successfully!")
            
        except Exception as e:
            print(f"❌ EasyOCR initialization failed: {str(e)}")
            raise
    
    def extract_text(self, image_data):
        """
        Extract text from image using EasyOCR.
        
        Args:
            image_data: PIL Image, numpy array, or file path
            
        Returns:
            Dictionary with extracted text and confidence
        """
        try:
            # Convert input to numpy array if needed
            if isinstance(image_data, Image.Image):
                image = np.array(image_data)
            elif isinstance(image_data, str):
                image = cv2.imread(image_data)
            else:
                image = image_data
            
            # Run EasyOCR
            result = self.reader.readtext(image)
            
            # Extract text and confidence
            extracted_text = ""
            confidences = []
            word_details = []
            
            for detection in result:
                bbox, text, confidence = detection
                extracted_text += text + "\n"
                confidences.append(confidence)
                word_details.append({
                    'text': text,
                    'confidence': round(confidence * 100, 2),
                    'bbox': bbox.tolist() if hasattr(bbox, 'tolist') else bbox
                })
            
            # Calculate average confidence
            avg_confidence = 0
            if confidences:
                avg_confidence = round((sum(confidences) / len(confidences)) * 100, 2)
            
            return {
                'text': extracted_text.strip(),
                'confidence': avg_confidence,
                'word_count': len(confidences),
                'word_details': word_details,
                'all_confidences': [round(c * 100, 2) for c in confidences],
                'status': 'success'
            }
            
        except Exception as e:
            print(f"❌ EasyOCR extraction error: {str(e)}")
            return {
                'text': '',
                'confidence': 0,
                'word_count': 0,
                'word_details': [],
                'error': str(e),
                'status': 'error'
            }
    
    def extract_text_from_pdf(self, pdf_images):
        """
        Extract text from PDF pages using EasyOCR.
        
        Args:
            pdf_images: List of PIL Images (each page)
            
        Returns:
            Dictionary with extracted text and confidence per page
        """
        results = []
        all_text = ""
        all_confidences = []
        
        for i, image in enumerate(pdf_images):
            print(f"📄 Processing PDF page {i+1} with EasyOCR...")
            
            # Convert PIL to numpy
            img_array = np.array(image)
            
            # Extract text from page
            page_result = self.extract_text(img_array)
            
            if page_result['status'] == 'success':
                all_text += f"\n--- Page {i+1} ---\n"
                all_text += page_result['text'] + "\n"
                all_confidences.append(page_result['confidence'])
                
                results.append({
                    'page': i + 1,
                    'text': page_result['text'],
                    'confidence': page_result['confidence'],
                    'word_count': page_result['word_count'],
                    'word_details': page_result['word_details']
                })
            else:
                results.append({
                    'page': i + 1,
                    'text': '',
                    'confidence': 0,
                    'error': page_result.get('error', 'Unknown error')
                })
        
        # Calculate overall confidence
        overall_confidence = 0
        if all_confidences:
            overall_confidence = round(sum(all_confidences) / len(all_confidences), 2)
        
        return {
            'pages': results,
            'full_text': all_text.strip(),
            'overall_confidence': overall_confidence,
            'total_pages': len(pdf_images),
            'status': 'success'
        }
    
    def get_supported_languages(self):
        """Get list of supported languages."""
        return [
            {'code': code, 'name': name, 'easyocr_code': self.EASYOCR_LANG_MAP.get(code, code)}
            for code, name in self.LANGUAGE_MAP.items()
        ]


# ===============================
# Singleton instance for reuse
# ===============================
_easyocr_instance = None

def get_easyocr_service(languages=None, gpu=False):
    """
    Get or create EasyOCR service instance.
    
    Args:
        languages: List of language codes
        gpu: Use GPU if available
        
    Returns:
        EasyOCRService instance
    """
    global _easyocr_instance
    
    # If languages is a string, convert to list
    if isinstance(languages, str):
        if '+' in languages:
            languages = languages.split('+')
        else:
            languages = [languages]
    
    # If instance doesn't exist or languages changed, create new instance
    if _easyocr_instance is None or _easyocr_instance.languages != languages:
        _easyocr_instance = EasyOCRService(languages, gpu)
    
    return _easyocr_instance


# ===============================
# Test function
# ===============================
if __name__ == "__main__":
    # Test the EasyOCR service
    service = get_easyocr_service(['en', 'kn'])
    print("✅ EasyOCR service is ready!")