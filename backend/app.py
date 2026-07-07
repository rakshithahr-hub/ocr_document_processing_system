from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import subprocess
import os
import shutil
import subprocess


from routes.health_routes import health_bp
from routes.ocr_routes import ocr_bp
from routes.download_routes import download_bp
from config import Config, POPPLER_PATH

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Store poppler path in app config
    app.config['POPPLER_PATH'] = POPPLER_PATH

    # Ensure directories exist
    for folder in [Config.UPLOAD_FOLDER, Config.OUTPUT_FOLDER, Config.TEMP_FOLDER]:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Directory ready: {folder}")

    # Check poppler
    if POPPLER_PATH:
        print(f"✅ Poppler found at: {POPPLER_PATH}")
    else:
        print("ℹ️ Poppler will use system PATH")

    # Enable CORS with comprehensive configuration
    CORS(
    app,
    origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://ocr-document-processing-system-1.onrender.com"
    ]
)
    
    # Optional: Add after_request handler for additional CORS headers
    

    # Register Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(ocr_bp)
    app.register_blueprint(download_bp)
    

    @app.route("/")
    def home():
        return jsonify({
            "message": "OCR Text Extraction API",
            "version": "1.0.0",
            "status": "Running",
            "environment": os.environ.get("ENV", "development"),
            "directories": {
                "uploads": os.path.exists(Config.UPLOAD_FOLDER),
                "outputs": os.path.exists(Config.OUTPUT_FOLDER),
                "temp": os.path.exists(Config.TEMP_FOLDER)
            },
            "poppler": {
                "path": POPPLER_PATH,
                "available": POPPLER_PATH is not None or os.system("pdfinfo -v > /dev/null 2>&1") == 0
            }
        })
    

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("ENV") != "production"  # Disable debug in production
    )