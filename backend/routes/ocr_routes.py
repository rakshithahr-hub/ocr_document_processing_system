from flask import Blueprint
from controllers.ocr_controller import upload_file, get_languages

ocr_bp = Blueprint(
    "ocr",
    __name__,
    url_prefix="/api"
)

@ocr_bp.route("/upload", methods=["POST"])
def upload():
    return upload_file()

@ocr_bp.route("/languages", methods=["GET"])
def languages():
    return get_languages()