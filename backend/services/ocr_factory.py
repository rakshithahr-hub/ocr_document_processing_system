from services.tesseract.engine import TesseractEngine


class OCRFactory:
    """
    Factory class for creating OCR engine instances.
    """

    @staticmethod
    def get_engine(engine_name="tesseract"):

        engine_name = engine_name.lower()

        engines = {
            "tesseract": TesseractEngine(),
        }

        if engine_name not in engines:
            raise ValueError(f"OCR Engine '{engine_name}' is not supported.")

        return engines[engine_name]