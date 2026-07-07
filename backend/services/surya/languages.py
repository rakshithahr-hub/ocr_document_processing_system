# services/surya/languages.py

class SuryaLanguages:
    """
    Language support for Surya OCR - 90+ languages
    """
    
    # Mapping from Tesseract/EasyOCR codes to Surya codes
    LANGUAGE_MAP = {
        'eng': 'en',
        'kan': 'kn',
        'hin': 'hi',
        'tam': 'ta',
        'tel': 'te',
        'mal': 'ml',
        'ben': 'bn',
        'guj': 'gu',
        'mar': 'mr',
        'ori': 'or',
        'pan': 'pa',
        'urd': 'ur',
        'san': 'sa',
        'asm': 'as',
        'nep': 'ne',
        'fra': 'fr',
        'deu': 'de',
        'spa': 'es',
        'ita': 'it',
        'por': 'pt',
        'rus': 'ru',
        'nld': 'nl',
        'swe': 'sv',
        'dan': 'da',
        'nor': 'no',
        'fin': 'fi',
        'ell': 'el',
        'ces': 'cs',
        'hun': 'hu',
        'ron': 'ro',
        'bul': 'bg',
        'srp': 'sr',
        'hrv': 'hr',
        'jpn': 'ja',
        'kor': 'ko',
        'chi_sim': 'zh',
        'chi_tra': 'zh',
        'tha': 'th',
        'vie': 'vi',
        'ind': 'id',
        'msa': 'ms',
        'khm': 'km',
        'lao': 'lo',
        'mya': 'my',
        'ara': 'ar',
        'fas': 'fa',
        'heb': 'he',
        'swa': 'sw',
        'afr': 'af',
        'amh': 'am',
        'hau': 'ha',
        'ibo': 'ig',
        'yor': 'yo',
        'zul': 'zu'
    }
    
    # Reverse mapping
    REVERSE_MAP = {v: k for k, v in LANGUAGE_MAP.items()}
    
    def __init__(self):
        print("🔍 SuryaLanguages initialized")
        print(f"   Supports {len(self.LANGUAGE_MAP)} languages")
    
    def get_surya_language(self, tesseract_code):
        """
        Convert Tesseract language code to Surya language code
        """
        return self.LANGUAGE_MAP.get(tesseract_code, 'en')
    
    def get_tesseract_language(self, surya_code):
        """
        Convert Surya language code to Tesseract language code
        """
        return self.REVERSE_MAP.get(surya_code, 'eng')
    
    def is_language_supported(self, language_code):
        """
        Check if language is supported
        """
        # Check if it's a Surya code directly
        if language_code in self.REVERSE_MAP:
            return True
        
        # Check if it's a Tesseract code
        if language_code in self.LANGUAGE_MAP:
            return True
        
        return False
    
    def get_supported_languages(self):
        """
        Get list of supported languages
        """
        return [
            {
                'code': tesseract_code,
                'surya_code': surya_code,
                'name': self.get_language_name(tesseract_code)
            }
            for tesseract_code, surya_code in self.LANGUAGE_MAP.items()
        ]
    
    def get_language_name(self, tesseract_code):
        """
        Get language name from Tesseract code
        """
        language_names = {
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
            'san': 'Sanskrit',
            'asm': 'Assamese',
            'nep': 'Nepali',
            'fra': 'French',
            'deu': 'German',
            'spa': 'Spanish',
            'ita': 'Italian',
            'por': 'Portuguese',
            'rus': 'Russian',
            'jpn': 'Japanese',
            'kor': 'Korean',
            'chi_sim': 'Chinese (Simplified)',
            'chi_tra': 'Chinese (Traditional)',
            'tha': 'Thai',
            'vie': 'Vietnamese',
            'ara': 'Arabic',
            'fas': 'Persian',
            'heb': 'Hebrew'
        }
        return language_names.get(tesseract_code, tesseract_code)