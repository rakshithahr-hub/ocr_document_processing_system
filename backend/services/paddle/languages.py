# services/paddle/languages.py

class PaddleLanguages:
    """
    Language support for PaddleOCR
    PaddleOCR supports 80+ languages with specific language codes
    """
    
    LANGUAGE_MAP = {
        # Indian Languages
        'en': 'English',
        'kn': 'Kannada',
        'hi': 'Hindi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ml': 'Malayalam',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'mr': 'Marathi',
        'or': 'Odia',
        'pa': 'Punjabi',
        'ur': 'Urdu',
        'sa': 'Sanskrit',
        'as': 'Assamese',
        'ne': 'Nepali',
        
        # European Languages
        'fr': 'French',
        'de': 'German',
        'es': 'Spanish',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'da': 'Danish',
        'no': 'Norwegian',
        'fi': 'Finnish',
        'el': 'Greek',
        'cs': 'Czech',
        'hu': 'Hungarian',
        'ro': 'Romanian',
        'bg': 'Bulgarian',
        'sr': 'Serbian',
        'hr': 'Croatian',
        'pl': 'Polish',
        'uk': 'Ukrainian',
        
        # Asian Languages
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'id': 'Indonesian',
        'ms': 'Malay',
        'km': 'Khmer',
        'lo': 'Lao',
        'my': 'Burmese',
        'tl': 'Tagalog',
        
        # Middle Eastern Languages
        'ar': 'Arabic',
        'fa': 'Persian',
        'he': 'Hebrew',
        
        # African Languages
        'sw': 'Swahili',
        'af': 'Afrikaans',
        'am': 'Amharic',
        'ha': 'Hausa',
        'ig': 'Igbo',
        'yo': 'Yoruba',
        'zu': 'Zulu'
    }
    
    # Map for converting 3-letter codes (like Tesseract) to 2-letter codes (Paddle)
    THREE_TO_TWO_MAP = {
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
        'pol': 'pl',
        'ukr': 'uk',
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
    
    @classmethod
    def get_supported_languages(cls):
        """Return list of supported languages for frontend"""
        return [{'code': code, 'name': name} for code, name in cls.LANGUAGE_MAP.items()]
    
    @classmethod
    def is_supported(cls, lang_code):
        """Check if language is supported"""
        return lang_code in cls.LANGUAGE_MAP
    
    @classmethod
    def convert_code(cls, lang_code):
        """Convert 3-letter code to 2-letter code for PaddleOCR"""
        # If it's already 2-letter and supported, return it
        if lang_code in cls.LANGUAGE_MAP:
            return lang_code
        
        # Try to convert from 3-letter to 2-letter
        if lang_code in cls.THREE_TO_TWO_MAP:
            return cls.THREE_TO_TWO_MAP[lang_code]
        
        # Default to English
        return 'en'
    
    @classmethod
    def get_language_name(cls, lang_code):
        """Get language name from code"""
        lang_code = cls.convert_code(lang_code)
        return cls.LANGUAGE_MAP.get(lang_code, 'Unknown')
    
    @classmethod
    def get_supported_indic_languages(cls):
        """Get supported Indian languages"""
        indic_codes = ['hi', 'kn', 'ta', 'te', 'ml', 'bn', 'gu', 'mr', 'or', 'pa', 'ur', 'sa', 'as', 'ne']
        return [{'code': code, 'name': cls.LANGUAGE_MAP[code]} for code in indic_codes if code in cls.LANGUAGE_MAP]
    
    @classmethod
    def get_paddle_lang_codes(cls, languages):
        """
        Convert language codes to PaddleOCR format
        PaddleOCR uses specific language codes for different languages
        """
        lang_codes = []
        for lang in languages:
            converted = cls.convert_code(lang)
            if converted not in lang_codes:
                lang_codes.append(converted)
        return lang_codes