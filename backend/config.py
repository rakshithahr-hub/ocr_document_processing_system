import os
import subprocess

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "ocr_secret_key")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

    # Use absolute paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
    TEMP_FOLDER = os.path.join(BASE_DIR, "temp")

    ALLOWED_EXTENSIONS = {
        "pdf", "png", "jpg", "jpeg", "bmp", "tiff", "webp", "docx"
    }

    # Tesseract path
    if os.name == "nt":
        TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    else:
        TESSERACT_CMD = "/usr/bin/tesseract"

    # ✅ DYNAMIC POPPLER PATH DETECTION
    @staticmethod
    def get_poppler_path():
        """Detect poppler path dynamically"""
        if os.name == "nt":
            # Windows
            possible_paths = [
                r"C:\Program Files\poppler\Library\bin",
                r"C:\poppler\bin",
                r"C:\Program Files\poppler\bin"
            ]
            for path in possible_paths:
                if os.path.exists(os.path.join(path, "pdfinfo.exe")):
                    return path
            return None
        else:
            # Linux (Render)
            try:
                # Check if poppler is installed
                result = subprocess.run(
                    ['which', 'pdfinfo'], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    return os.path.dirname(result.stdout.strip())
            except:
                pass
            
            # Check common locations
            possible_paths = [
                '/usr/bin',
                '/usr/local/bin',
                None  # Let system PATH handle it
            ]
            
            for path in possible_paths:
                if path:
                    if os.path.exists(os.path.join(path, 'pdfinfo')):
                        return path
                else:
                    # Try without path (system PATH)
                    try:
                        import subprocess
                        result = subprocess.run(
                            ['pdfinfo', '-v'], 
                            capture_output=True, 
                            text=True
                        )
                        if result.returncode == 0:
                            return None  # Use system PATH
                    except:
                        pass
            
            return None

# ✅ Set POPPLER_PATH dynamically
POPPLER_PATH = Config.get_poppler_path()

# Print for debugging
print(f"🔍 Poppler path detected: {POPPLER_PATH}")