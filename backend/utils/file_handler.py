import os
from werkzeug.utils import secure_filename

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


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_folder(extension):
    extension = extension.lower()

    if extension == "pdf":
        return "uploads/pdf"

    elif extension == "docx":
        return "uploads/docx"

    return "uploads/images"


def save_uploaded_file(file):
    filename = secure_filename(file.filename)

    extension = filename.rsplit(".", 1)[1].lower()

    upload_folder = get_upload_folder(extension)

    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, filename)

    file.save(filepath)

    return filepath, filename, extension