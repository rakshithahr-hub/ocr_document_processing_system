import os


class Config:

    SECRET_KEY = "ocr_secret_key"

    MAX_CONTENT_LENGTH = 100 * 1024 * 1024      # 100 MB

    UPLOAD_FOLDER = "uploads"

    OUTPUT_FOLDER = "outputs"

    TEMP_FOLDER = "temp"

    ALLOWED_EXTENSIONS = {
        "pdf",
        "png",
        "jpg",
        "jpeg",
        "bmp",
        "tiff",
        "webp",
        "docx"
    }

    TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    POPPLER_PATH = r"C:\Program Files\poppler\Library\bin"