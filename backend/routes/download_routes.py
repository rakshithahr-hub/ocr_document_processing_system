from flask import Blueprint
from controllers.download_controller import DownloadController

download_bp = Blueprint(
    "download",
    __name__,
    url_prefix="/api/download"
)

@download_bp.route("/files", methods=["GET"])
def list_files():
    return DownloadController.list_output_files()

@download_bp.route("/<filename>", methods=["GET"])
def download_file(filename):
    return DownloadController.download_file(filename)

@download_bp.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    return DownloadController.delete_file(filename)

@download_bp.route("/txt/<filename>", methods=["GET"])
def download_txt(filename):
    return DownloadController.download_txt(filename)

@download_bp.route("/pdf/<filename>", methods=["GET"])
def download_pdf(filename):
    return DownloadController.download_pdf(filename)

@download_bp.route("/json/<filename>", methods=["GET"])
def download_json(filename):
    return DownloadController.download_json(filename)