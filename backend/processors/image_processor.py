import os
from services.ocr_factory import OCRFactory


class ImageProcessor:
    """
    Process image files and perform OCR.
    """

    def __init__(self, engine_name="tesseract"):
        self.engine = OCRFactory.get_engine(engine_name)

    def process(self, image_path, language="eng"):
        """
        Perform OCR on an image.

        Args:
            image_path (str): Path to image.
            language (str): OCR language.

        Returns:
            dict
        """

        if not os.path.exists(image_path):
            return {
                "status": "error",
                "message": "Image file not found."
            }

        result = self.engine.extract_text(
            image_path=image_path,
            language=language
        )

        return {
            "status": "success",
            "file_type": "image",
            "filename": os.path.basename(image_path),
            "text": result["text"],
            "confidence": result["confidence"],
            "processing_time": result["processing_time"]
        }