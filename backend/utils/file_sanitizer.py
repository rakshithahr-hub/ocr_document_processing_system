import magic
import hashlib
import os
from PIL import Image
import io
import zipfile


class FileSanitizer:
    """
    Secure file sanitization utility for validating uploaded files.
    Designed for OCR/image/document pipelines.
    """

    def __init__(self):

        # Blocked MIME types (executables, scripts, installers)
        self.blocked_mime_types = {
            'application/x-msdownload',
            'application/x-msdos-program',
            'application/x-executable',
            'application/x-sh',
            'application/x-bat',
            'text/javascript',
            'application/x-php',
            'application/x-httpd-php',
            'application/x-javascript',
            'application/x-msi',
            'application/vnd.microsoft.portable-executable'
        }

        # Allowed MIME types for OCR pipeline
        self.allowed_mime_types = {
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'image/png',
            'image/jpeg',
            'image/bmp',
            'image/tiff',
            'image/webp'
        }

        # Allowed extensions
        self.allowed_extensions = {
            'pdf', 'docx', 'doc',
            'png', 'jpg', 'jpeg',
            'bmp', 'tiff', 'webp'
        }

        # Limits
        self.max_file_size = 50 * 1024 * 1024      # 50MB
        self.max_image_pixels = 25_000_000         # safer than width*height only
        self.max_zip_uncompressed = 200 * 1024 * 1024  # 200MB
        self.max_zip_files = 500

        # Suspicious byte patterns (basic heuristic only)
        self.suspicious_patterns = [
            b'<script',
            b'eval(',
            b'base64_decode',
            b'wget http',
            b'curl http',
            b'exec(',
            b'system(',
            b'shell_exec(',
            b'popen(',
            b'proc_open(',
            b'pcntl_exec('
        ]

    # =========================
    # MAIN SANITIZATION METHOD
    # =========================
    def sanitize(self, file):
        try:
            file_content = file.read()
            file.seek(0)

            # 1. File size check
            if len(file_content) > self.max_file_size:
                return False, {
                    "error": "FILE_TOO_LARGE",
                    "message": f"Max allowed size is {self.max_file_size // (1024*1024)}MB"
                }

            # 2. Extension check
            if not self._check_extension(file.filename):
                return False, {
                    "error": "INVALID_EXTENSION",
                    "message": "File extension not allowed"
                }

            # 3. MIME detection (FULL BUFFER)
            mime = magic.from_buffer(file_content, mime=True)

            if mime in self.blocked_mime_types:
                return False, {
                    "error": "BLOCKED_FILE_TYPE",
                    "message": f"Blocked file type: {mime}"
                }

            if mime not in self.allowed_mime_types and not mime.startswith("image/"):
                return False, {
                    "error": "UNSUPPORTED_FILE_TYPE",
                    "message": f"Unsupported file type: {mime}"
                }

            # 4. ZIP bomb protection
            if self._check_zip_bomb(file_content):
                return False, {
                    "error": "ZIP_BOMB_DETECTED",
                    "message": "Unsafe compressed file detected"
                }

            # 5. Image validation
            if mime.startswith("image/"):
                if not self._check_image(file_content):
                    return False, {
                        "error": "INVALID_IMAGE",
                        "message": "Image failed validation checks"
                    }

            # 6. Malware signature scan
            if self._check_malware_signatures(file_content):
                return False, {
                    "error": "SUSPICIOUS_CONTENT",
                    "message": "Potential malicious patterns detected"
                }

            # 7. Generate hash
            file_hash = hashlib.sha256(file_content).hexdigest()

            return True, {
                "mime_type": mime,
                "file_size": len(file_content),
                "file_hash": file_hash,
                "extension": self._get_extension(file.filename),
                "is_safe": True
            }

        except Exception as e:
            return False, {
                "error": "SANITIZATION_ERROR",
                "message": str(e)
            }

    # =========================
    # HELPERS
    # =========================
    def _check_extension(self, filename):
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in self.allowed_extensions

    def _get_extension(self, filename):
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ""

    # =========================
    # ZIP BOMB CHECK
    # =========================
    def _check_zip_bomb(self, content):
        try:
            if len(content) < 10 * 1024 * 1024:
                return False

            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                file_list = zf.infolist()

                if len(file_list) > self.max_zip_files:
                    return True

                total_size = sum(f.file_size for f in file_list)

                if total_size > self.max_zip_uncompressed:
                    return True

            return False

        except zipfile.BadZipFile:
            return False
        except Exception:
            return True

    # =========================
    # IMAGE VALIDATION
    # =========================
    def _check_image(self, content):
        try:
            img = Image.open(io.BytesIO(content))

            # Verify integrity (detect corrupted/weaponized images)
            img.verify()

            img = Image.open(io.BytesIO(content))
            width, height = img.size

            if width <= 0 or height <= 0:
                return False

            if width > 5000 or height > 5000:
                return False

            if (width * height) > self.max_image_pixels:
                return False

            return True

        except Exception:
            return False

    # =========================
    # BASIC MALWARE SCAN (HEURISTIC)
    # =========================
    def _check_malware_signatures(self, content):
        try:
            lower = content[:2 * 1024 * 1024]  # scan first 2MB only for speed

            for pattern in self.suspicious_patterns:
                if pattern in lower:
                    return True

            return False

        except Exception:
            return True


# Singleton instance
file_sanitizer = FileSanitizer()