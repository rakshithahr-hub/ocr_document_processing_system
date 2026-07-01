import os
from services.ocr_factory import OCRFactory
from PIL import Image


class ImageProcessor:
    """
    Process image files and perform OCR safely.
    """

    def __init__(self, engine_name="tesseract"):
        self.engine = OCRFactory.get_engine(engine_name)

    def process(self, image_path, language="eng"):
        """
        Perform OCR on an image safely.
        """

        # =========================
        # 1. Validate file existence
        # =========================
        if not image_path or not os.path.exists(image_path):
            return {
                "status": "error",
                "message": "Image file not found."
            }

        try:
            # =========================
            # 2. Validate image integrity
            # =========================
            with Image.open(image_path) as img:
                img.verify()  # checks corruption

            # reopen after verify (PIL requirement)
            Image.open(image_path)

            # =========================
            # 3. OCR processing
            # =========================
            result = self.engine.extract_text(
                image_path=image_path,
                language=language
            )

            return {
                "status": "success",
                "file_type": "image",
                "filename": os.path.basename(image_path),
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0),
                "processing_time": result.get("processing_time", 0)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"OCR failed: {str(e)}"
            }