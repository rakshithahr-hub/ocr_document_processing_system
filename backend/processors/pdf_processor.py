import os
from pdf2image import convert_from_path
from config import Config


def pdf_to_images(pdf_path):
    """
    Convert PDF pages to images.

    Args:
        pdf_path (str): Path to uploaded PDF.

    Returns:
        list: List of generated image paths.
    """

    os.makedirs("temp/pdf_pages", exist_ok=True)

    images = convert_from_path(
        pdf_path,
        poppler_path=Config.POPPLER_PATH
    )

    image_paths = []

    for index, image in enumerate(images):

        image_path = f"temp/pdf_pages/page_{index + 1}.png"

        image.save(image_path, "PNG")

        image_paths.append(image_path)

    return image_paths