from flask import Flask, jsonify
from flask_cors import CORS
import os

# Import Route Blueprints
from routes.health_routes import health_bp
from routes.ocr_routes import ocr_bp
from routes.download_routes import download_bp

# Import Configuration
from config import Config

# ✅ Ensure directories exist on startup
def ensure_directories():
    """Create necessary directories if they don't exist"""
    folders = [
        Config.UPLOAD_FOLDER,
        Config.OUTPUT_FOLDER,
        Config.TEMP_FOLDER
    ]
    for folder in folders:
        try:
            os.makedirs(folder, exist_ok=True)
            print(f"✅ Directory ready: {folder}")
        except Exception as e:
            print(f"❌ Failed to create directory {folder}: {e}")

def create_app():
    app = Flask(__name__)

    # Load Configuration
    app.config.from_object(Config)

    # ✅ Ensure directories exist
    ensure_directories()

    # Enable CORS - ✅ Allow both frontend and local development
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://ocr-document-processing-system-1.onrender.com",
                "http://localhost:3000",
                "http://localhost:5000"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

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
            "directories": {
                "uploads": os.path.exists(Config.UPLOAD_FOLDER),
                "outputs": os.path.exists(Config.OUTPUT_FOLDER),
                "temp": os.path.exists(Config.TEMP_FOLDER)
            }
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )