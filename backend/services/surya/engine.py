# services/surya/engine.py

import time
from PIL import Image

# Try importing Surya components
try:
    from surya.detection import DetectionPredictor
    from surya.recognition import RecognitionPredictor
    from surya.settings import settings
    SURYA_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Surya import error: {e}")
    SURYA_AVAILABLE = False


class SuryaEngine:
    """
    Surya OCR Engine
    """

    def __init__(self):
        self.detection_predictor = None
        self.recognition_predictor = None
        
        if SURYA_AVAILABLE:
            try:
                self.detection_predictor = DetectionPredictor()
                self.recognition_predictor = RecognitionPredictor()
                print("✅ Surya OCR initialized successfully")
            except Exception as e:
                print(f"⚠️ Error initializing Surya predictors: {e}")
        else:
            print("⚠️ Surya OCR not available")

    def extract_text(self, image_path, language="en"):
        """
        Extract text from an image using Surya OCR.
        """
        start_time = time.time()

        if not SURYA_AVAILABLE:
            return {
                "status": "error",
                "message": "Surya OCR is not installed. Please run: pip install surya-ocr"
            }

        if self.detection_predictor is None or self.recognition_predictor is None:
            return {
                "status": "error",
                "message": "Surya predictors not initialized properly"
            }

        try:
            # Load image
            image = Image.open(image_path)
            
            # Detect text regions
            detections = self.detection_predictor([image])
            
            if not detections:
                return {
                    "status": "success",
                    "text": "",
                    "confidence": 0.0,
                    "processing_time": round(time.time() - start_time, 2)
                }

            # Extract text from detected regions
            text_lines = []
            
            for detection in detections:
                if hasattr(detection, 'bboxes') and detection.bboxes:
                    for bbox in detection.bboxes:
                        # Crop the detected region
                        cropped = self._crop_region(image, bbox)
                        if cropped:
                            try:
                                # Recognize text
                                recognition = self.recognition_predictor(
                                    [cropped],
                                    languages=[language]
                                )
                                
                                if recognition and len(recognition) > 0:
                                    result = recognition[0]
                                    if hasattr(result, 'text_lines'):
                                        for line in result.text_lines:
                                            if hasattr(line, 'text') and line.text:
                                                text_lines.append(line.text)
                            except Exception as e:
                                print(f"⚠️ Recognition error: {e}")
                                continue

            text = "\n".join(text_lines)

            elapsed_time = round(time.time() - start_time, 2)

            return {
                "status": "success",
                "text": text,
                "confidence": 0.0,  # Surya confidence calculation may vary
                "processing_time": elapsed_time
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Surya OCR failed: {str(e)}"
            }

    def _crop_region(self, image, bbox):
        """
        Crop image based on bounding box.
        """
        try:
            if hasattr(bbox, 'polygon'):
                polygon = bbox.polygon
                x_coords = [p[0] for p in polygon]
                y_coords = [p[1] for p in polygon]
                x0 = max(0, int(min(x_coords)))
                y0 = max(0, int(min(y_coords)))
                x1 = min(image.size[0], int(max(x_coords)))
                y1 = min(image.size[1], int(max(y_coords)))
                
                if x1 > x0 and y1 > y0:
                    return image.crop((x0, y0, x1, y1))
            elif hasattr(bbox, 'bbox'):
                x0, y0, x1, y1 = bbox.bbox
                x0 = max(0, int(x0))
                y0 = max(0, int(y0))
                x1 = min(image.size[0], int(x1))
                y1 = min(image.size[1], int(y1))
                
                if x1 > x0 and y1 > y0:
                    return image.crop((x0, y0, x1, y1))
        except Exception as e:
            print(f"⚠️ Crop error: {e}")
        
        return None

    def get_supported_languages(self):
        """Return list of supported languages."""
        return [
            'en', 'af', 'am', 'ar', 'as', 'az', 'be', 'bg', 'bn', 'bo',
            'br', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'es', 'et',
            'eu', 'fa', 'fi', 'fr', 'ga', 'gd', 'gl', 'gu', 'he', 'hi',
            'hr', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'ka', 'kk', 'km',
            'kn', 'ko', 'ku', 'ky', 'la', 'lb', 'lo', 'lt', 'lv', 'mk',
            'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'ne', 'nl', 'no', 'oc',
            'or', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'rw', 'sa', 'sd',
            'si', 'sk', 'sl', 'so', 'sq', 'sr', 'sv', 'sw', 'ta', 'te',
            'th', 'tl', 'tr', 'ug', 'uk', 'ur', 'uz', 'vi', 'xh', 'zh', 'zu'
        ]

    def is_language_installed(self, language):
        """Check if language is supported."""
        return language in self.get_supported_languages()