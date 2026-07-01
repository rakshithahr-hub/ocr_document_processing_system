import os
from pdf2image import convert_from_path
from config import Config


def pdf_to_images(pdf_path):
    """
    Convert PDF to safe image paths (Render-ready)
    """

    temp_dir = os.path.join(Config.TEMP_FOLDER, "pdf_pages")
    os.makedirs(temp_dir, exist_ok=True)

    images = convert_from_path(
        pdf_path,
        poppler_path=Config.POPPLER_PATH if os.name == "nt" else None,
        dpi=200
    )

    image_paths = []

    for index, image in enumerate(images):
        try:
            if image is None:
                print(f"Skipping empty page {index}")
                continue

            # IMPORTANT: normalize image
            image = image.convert("RGB")

            image_path = os.path.join(
                temp_dir,
                f"page_{index + 1}.png"
            )

            image.save(image_path, "PNG")
            image_paths.append(image_path)

        except Exception as e:
            print(f"Page {index} failed: {e}")
            continue

    return image_paths