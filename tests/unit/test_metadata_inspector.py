import io
import pytest
import fitz
from PIL import Image
from src.infrastructure.image_processing.metadata_inspector import PDFInspector, ImageInspector


def test_pdf_inspector():
    # Generate minimal valid PDF in memory
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), "Test Document Content")
    pdf_bytes = doc.tobytes()
    doc.close()

    metrics = PDFInspector.inspect(pdf_bytes)
    assert metrics["page_count"] == 1
    assert metrics["width"] == 595
    assert metrics["height"] == 842
    assert metrics["is_encrypted"] is False
    assert metrics["is_scanned"] is False


def test_image_inspector():
    # Generate minimal valid PNG in memory
    img = Image.new("RGB", (100, 200), color="blue")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    png_bytes = img_byte_arr.getvalue()

    metrics = ImageInspector.inspect(png_bytes)
    assert metrics["page_count"] == 1
    assert metrics["width"] == 100
    assert metrics["height"] == 200
    assert metrics["color_mode"] == "RGB"
