import io
from typing import Dict, Any, Tuple
import fitz  # PyMuPDF
from PIL import Image


class PDFInspector:
    """PyMuPDF inspector for PDF document metrics and safety checks."""

    @staticmethod
    def inspect(content: bytes) -> Dict[str, Any]:
        """
        Inspect PDF bytes and extract metadata.
        Raises ValueError if PDF is password-protected or corrupted.
        """
        try:
            doc = fitz.open(stream=content, filetype="pdf")
        except Exception as e:
            raise ValueError(f"Corrupted or invalid PDF file: {e}")

        if doc.is_encrypted:
            doc.close()
            raise ValueError("Encrypted or password-protected PDFs are not supported. Remove password first.")

        page_count = doc.page_count
        if page_count == 0:
            doc.close()
            raise ValueError("PDF document contains 0 pages.")

        # Check first page dimensions
        first_page = doc.load_page(0)
        rect = first_page.rect
        width, height = int(rect.width), int(rect.height)

        # Detect digital vs scanned PDF by checking for selectable text across pages
        has_text = False
        for page in doc:
            if page.get_text("text").strip():
                has_text = True
                break

        pdf_version = doc.metadata.get("format", "PDF-1.4") if doc.metadata else "PDF"

        metrics = {
            "page_count": page_count,
            "width": width,
            "height": height,
            "dpi": 300,  # Standard reference DPI
            "is_encrypted": False,
            "is_scanned": not has_text,
            "pdf_version": pdf_version,
            "embedded_images_count": sum(len(page.get_images()) for page in doc),
        }

        doc.close()
        return metrics


class ImageInspector:
    """Pillow inspector for multi-format image metadata."""

    @staticmethod
    def inspect(content: bytes) -> Dict[str, Any]:
        """
        Inspect image bytes and extract resolution, color mode, DPI, and dimensions.
        """
        try:
            img = Image.open(io.BytesIO(content))
            img.verify()  # Verify image integrity
            # Re-open for metric extraction after verify()
            img = Image.open(io.BytesIO(content))
        except Exception as e:
            raise ValueError(f"Corrupted or unreadable image file: {e}")

        width, height = img.size
        if width == 0 or height == 0:
            raise ValueError("Invalid image dimensions (0x0).")

        dpi_info = img.info.get("dpi", (300, 300))
        dpi = int(dpi_info[0]) if isinstance(dpi_info, (tuple, list)) and len(dpi_info) > 0 else 300

        metrics = {
            "page_count": 1,
            "width": width,
            "height": height,
            "dpi": dpi,
            "color_mode": img.mode,
            "format": img.format,
            "is_scanned": True,
        }
        return metrics
