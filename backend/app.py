from flask import Flask, jsonify
from flask_cors import CORS
import os

# Import Route Blueprints
from routes.health_routes import health_bp
from routes.ocr_routes import ocr_bp
from routes.download_routes import download_bp

# Import Configuration
from config import Config


def create_app():
    app = Flask(__name__)

    # Load Configuration
    app.config.from_object(Config)

    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register Blueprints
    # health_bp already has /api/health prefix in its definition
    app.register_blueprint(health_bp)  # Remove url_prefix
    # ocr_bp already has /api prefix in its definition
    app.register_blueprint(ocr_bp)     # Remove url_prefix
    # download_bp already has /api/download prefix in its definition
    app.register_blueprint(download_bp) # Remove url_prefix

    @app.route("/")
    def home():
        return jsonify({
            "message": "OCR Text Extraction API",
            "version": "1.0.0",
            "status": "Running"
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )