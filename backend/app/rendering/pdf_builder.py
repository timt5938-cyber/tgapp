from io import BytesIO
from typing import List
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pathlib import Path

class PDFBuilder:
    @staticmethod
    def build_pdf_from_images(images: List[Image.Image]) -> bytes:
        """
        Converts a list of PIL Images into a print-ready multi-page A4 PDF document.
        Returns the PDF as raw bytes.
        """
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        a4_w, a4_h = A4

        for img in images:
            # Convert RGBA to RGB for PDF embedding
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "RGBA":
                rgb_img.paste(img, mask=img.split()[3])
            else:
                rgb_img.paste(img)

            img_buffer = BytesIO()
            rgb_img.save(img_buffer, format="JPEG", quality=92)
            img_buffer.seek(0)

            # Draw image fitted to A4 page
            from reportlab.lib.utils import ImageReader
            reader = ImageReader(img_buffer)
            c.drawImage(reader, 0, 0, width=a4_w, height=a4_h)
            c.showPage()

        c.save()
        return pdf_buffer.getvalue()

    @staticmethod
    def save_pdf_to_file(images: List[Image.Image], output_path: Path) -> Path:
        pdf_bytes = PDFBuilder.build_pdf_from_images(images)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        return output_path

pdf_builder = PDFBuilder()
