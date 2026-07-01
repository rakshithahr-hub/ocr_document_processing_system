import os


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY", "ocr_secret_key")

    MAX_CONTENT_LENGTH = 100 * 1024 * 1024      # 100 MB

    # ✅ Use absolute paths for Render compatibility
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
    TEMP_FOLDER = os.path.join(BASE_DIR, "temp")

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

    if os.name == "nt":
        # Windows
        TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        POPPLER_PATH = r"C:\Program Files\poppler\Library\bin"
    else:
        # Linux (Render)
        TESSERACT_CMD = "/usr/bin/tesseract"
        POPPLER_PATH = None

# ✅ Create directories when config is imported
for folder in [Config.UPLOAD_FOLDER, Config.OUTPUT_FOLDER, Config.TEMP_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Created directory: {folder}")