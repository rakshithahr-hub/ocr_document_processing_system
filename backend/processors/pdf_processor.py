import os
import gc
from pdf2image import convert_from_path, pdfinfo_from_path
from config import Config


def pdf_to_images(pdf_path):
    """
    Convert PDF to images one page at a time.
    Much lower memory usage.
    """

    temp_dir = os.path.join(Config.TEMP_FOLDER, "pdf_pages")
    os.makedirs(temp_dir, exist_ok=True)

    info = pdfinfo_from_path(
        pdf_path,
        poppler_path=Config.POPPLER_PATH if os.name == "nt" else None,
    )

    total_pages = info["Pages"]

    image_paths = []

    for page in range(1, total_pages + 1):
        try:
            images = convert_from_path(
                pdf_path,
                dpi=150,              # reduced from 200
                first_page=page,
                last_page=page,
                fmt="png",
                poppler_path=Config.POPPLER_PATH if os.name == "nt" else None,
            )

            if not images:
                continue

            image = images[0].convert("RGB")

            image_path = os.path.join(
                temp_dir,
                f"page_{page}.png"
            )

            image.save(image_path, "PNG")

            image_paths.append(image_path)

            image.close()
            del image
            del images
            gc.collect()

        except Exception as e:
            print(f"Page {page} failed: {e}")

    return image_paths