import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


class OutputGenerator:

    def __init__(self, output_folder="outputs"):
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

    def _generate_filename(self, extension):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(
            self.output_folder,
            f"ocr_result_{timestamp}.{extension}"
        )

    # -----------------------------
    # TXT
    # -----------------------------
    def save_txt(self, text):
        try:
            filepath = self._generate_filename("txt")

            with open(filepath, "w", encoding="utf-8") as file:
                file.write(text or "")

            return filepath

        except Exception as e:
            return {"error": str(e)}

    # -----------------------------
    # JSON
    # -----------------------------
    def save_json(self, text, confidence, processing_time, file_type, pages):
        try:
            filepath = self._generate_filename("json")

            data = {
                "status": "success",
                "file_type": file_type,
                "pages": pages,
                "confidence": confidence,
                "processing_time": processing_time,
                "text": text or ""
            }

            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            return filepath

        except Exception as e:
            return {"error": str(e)}

    # -----------------------------
    # PDF (SAFE VERSION)
    # -----------------------------
    def save_pdf(self, text):
        try:
            filepath = self._generate_filename("pdf")

            styles = getSampleStyleSheet()
            document = SimpleDocTemplate(filepath, pagesize=A4)

            story = []

            if not text:
                story.append(Paragraph("No text extracted", styles["BodyText"]))
            else:
                for line in text.split("\n"):
                    line = line.strip()

                    if not line:
                        continue

                    # prevent PDF crash on long text
                    if len(line) > 1000:
                        line = line[:1000] + "..."

                    story.append(Paragraph(line, styles["BodyText"]))

            document.build(story)

            return filepath

        except Exception as e:
            return {"error": str(e)}

    # -----------------------------
    # MAIN
    # -----------------------------
    def generate_outputs(self, text, confidence, processing_time, file_type, pages):
        txt_path = self.save_txt(text)
        json_path = self.save_json(text, confidence, processing_time, file_type, pages)
        pdf_path = self.save_pdf(text)

        return {
            "txt": txt_path,
            "json": json_path,
            "pdf": pdf_path
        }