# services/paddle/engine.py

import time
import numpy as np
from PIL import Image

class PaddleEngine:
    """
    PaddleOCR Engine
    """

    def __init__(self):
        self.available = False
        self.ocr = None
        self._initialize()

    def _initialize(self):
        """Initialize PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang='en',
                show_log=False
            )
            self.available = True
            print("✅ PaddleOCR initialized successfully")
        except ImportError as e:
            print(f"⚠️ PaddleOCR not available: {e}")
        except Exception as e:
            print(f"⚠️ Error initializing PaddleOCR: {e}")

    def extract_text(self, image_path, language="en"):
        """
        Extract text from an image using PaddleOCR.
        """
        start_time = time.time()

        if not self.available:
            return {
                "status": "error",
                "message": "PaddleOCR is not installed. Please run: pip install paddlepaddle paddleocr"
            }

        try:
            # Run OCR
            result = self.ocr.ocr(image_path, cls=True)
            
            # Extract text from result
            text_lines = []
            confidences = []
            
            if result and len(result) > 0:
                for line in result[0]:  # result[0] contains the text boxes
                    if line and len(line) >= 2:
                        # line[1] contains (text, confidence)
                        text = line[1][0] if len(line[1]) > 0 else ""
                        confidence = line[1][1] if len(line[1]) > 1 else 0.0
                        
                        if text.strip():
                            text_lines.append(text.strip())
                            confidences.append(confidence)
            
            # Join all text
            text = "\n".join(text_lines)
            
            # Calculate average confidence
            avg_confidence = self._calculate_confidence(confidences)

            elapsed_time = round(time.time() - start_time, 2)

            return {
                "status": "success",
                "text": text,
                "confidence": avg_confidence,
                "processing_time": elapsed_time
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"PaddleOCR failed: {str(e)}"
            }

    def _calculate_confidence(self, confidences):
        """Calculate average confidence from PaddleOCR results."""
        if not confidences:
            return 0.0
        
        valid_confidences = []
        for score in confidences:
            try:
                score = float(score)
                if 0 <= score <= 1:
                    valid_confidences.append(score * 100)  # Convert to percentage
                elif 0 <= score <= 100:
                    valid_confidences.append(score)
            except Exception:
                continue
        
        if not valid_confidences:
            return 0.0
        
        return round(sum(valid_confidences) / len(valid_confidences), 2)

    def get_supported_languages(self):
        """Return list of supported languages."""
        return [
            'en', 'ch', 'korean', 'japan', 'chinese_cht', 'ta', 'te', 
            'ka', 'th', 'el', 'latin', 'arabic', 'cyrillic', 'devanagari'
        ]

    def is_language_installed(self, language):
        """Check if language is supported."""
        return language in self.get_supported_languages()