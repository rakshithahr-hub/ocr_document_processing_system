import time

import pytesseract
from pytesseract import Output

from config import Config
from services.tesseract.preprocess import ImagePreprocessor
from services.tesseract.languages import TesseractLanguages

# Configure Tesseract executable
pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD


class TesseractEngine:
    """
    Tesseract OCR Engine
    """

    def __init__(self):
        self.language_manager = TesseractLanguages()

    def extract_text(self, image_path, language="eng"):
        """
        Extract text from an image.
        """

        start_time = time.time()

        # Validate language
        if not self.language_manager.is_language_installed(language):
            return {
                "status": "error",
                "message": f"Tesseract language '{language}' is not installed."
            }

        # Preprocess image
        processed_image = ImagePreprocessor.preprocess(image_path)

        # OCR
        text = pytesseract.image_to_string(
            processed_image,
            lang=language
        )

        confidence = self.calculate_confidence(
            processed_image,
            language
        )

        elapsed_time = round(time.time() - start_time, 2)

        return {
            "status": "success",
            "text": text,
            "confidence": confidence,
            "processing_time": elapsed_time
        }

    def calculate_confidence(self, image, language="eng"):
        """
        Calculate average OCR confidence.
        """

        data = pytesseract.image_to_data(
            image,
            lang=language,
            output_type=Output.DICT
        )

        confidences = []

        for value in data["conf"]:

            try:

                score = float(value)

                if score >= 0:
                    confidences.append(score)

            except Exception:
                continue

        if not confidences:
            return 0.0

        return round(
            sum(confidences) / len(confidences),
            2
        )

    def get_supported_languages(self):
        """
        Return installed Tesseract languages.
        """

        return self.language_manager.get_installed_languages()

    def is_language_installed(self, language):
        """
        Check whether language exists.
        """

        return self.language_manager.is_language_installed(language)