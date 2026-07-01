# utils/file_sanitizer.py
import magic
import hashlib
import os
from PIL import Image
import io
import zipfile

class FileSanitizer:
    """
    File sanitization utility to validate and clean uploaded files.
    """
    
    def __init__(self):
        # Blocked file types (executables, scripts, etc.)
        self.blocked_mime_types = {
            'application/x-msdownload',
            'application/x-msdos-program',
            'application/x-executable',
            'application/x-sh',
            'application/x-bat',
            'text/javascript',
            'text/x-script.python',
            'application/x-php',
            'application/x-httpd-php',
            'application/x-javascript',
            'application/x-msi',
            'application/vnd.microsoft.portable-executable'
        }
        
        # Allowed file types for OCR
        self.allowed_mime_types = {
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'image/png',
            'image/jpeg',
            'image/jpg',
            'image/bmp',
            'image/tiff',
            'image/webp'
        }
        
        # Allowed extensions
        self.allowed_extensions = {
            'pdf', 'docx', 'doc', 'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'
        }
        
        # Maximum file size (50MB)
        self.max_file_size = 50 * 1024 * 1024
        
        # Maximum image dimensions
        self.max_dimensions = 5000 * 5000
        
        # Suspicious patterns
        self.suspicious_patterns = [
            b'<script>eval',
            b'<?php eval',
            b'base64_decode',
            b'wget http://',
            b'curl http://',
            b'exec(',
            b'system(',
            b'passthru(',
            b'shell_exec(',
            b'popen(',
            b'proc_open(',
            b'pcntl_exec('
        ]
    
    def sanitize(self, file):
        """Main sanitization method"""
        try:
            file_content = file.read()
            file.seek(0)
            
            # Check file size
            if len(file_content) > self.max_file_size:
                return False, f"File too large. Maximum size: {self.max_file_size // (1024 * 1024)}MB"
            
            # Check extension
            if not self._check_extension(file.filename):
                ext = os.path.splitext(file.filename)[1].lower()
                return False, f"File extension '{ext}' is not supported"
            
            # Check MIME type
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(file_content[:1024])
            
            if file_type in self.blocked_mime_types:
                return False, f"File type '{file_type}' is blocked for security reasons"
            
            if file_type not in self.allowed_mime_types:
                return False, f"File type '{file_type}' is not supported"
            
            # Check zip bomb
            if self._check_zip_bomb(file_content):
                return False, "Potentially unsafe file detected"
            
            # Check image dimensions
            if file_type.startswith('image/'):
                if not self._check_image_dimensions(file_content):
                    return False, "Image dimensions exceed maximum allowed size"
            
            # Check malware signatures
            if self._check_malware_signatures(file_content):
                return False, "Potential malware detected in file"
            
            # Generate file hash
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            return True, {
                'mime_type': file_type,
                'file_size': len(file_content),
                'file_hash': file_hash,
                'file_extension': self._get_extension(file.filename),
                'is_safe': True
            }
            
        except Exception as e:
            return False, f"Sanitization error: {str(e)}"
    
    def _check_extension(self, filename):
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in self.allowed_extensions
    
    def _get_extension(self, filename):
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ''
    
    def _check_zip_bomb(self, content):
        try:
            if len(content) > 20 * 1024 * 1024:
                try:
                    with zipfile.ZipFile(io.BytesIO(content)) as zf:
                        total_size = sum([info.file_size for info in zf.infolist()])
                        if total_size > len(content) * 100:
                            return True
                except:
                    pass
            return False
        except:
            return False
    
    def _check_image_dimensions(self, content):
        try:
            img = Image.open(io.BytesIO(content))
            width, height = img.size
            if width * height > self.max_dimensions:
                return False
            return True
        except:
            return True
    
    def _check_malware_signatures(self, content):
        for pattern in self.suspicious_patterns:
            if pattern in content:
                return True
        return False

# Create singleton instance
file_sanitizer = FileSanitizer()