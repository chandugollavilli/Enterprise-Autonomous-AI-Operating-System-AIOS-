import io
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Generator
import cv2
import fitz  # PyMuPDF
import numpy as np
from PIL import Image


@dataclass
class RenderingProfile:
    name: str
    dpi: int
    format: str = "PNG"
    color_mode: str = "RGB"


PROFILES: Dict[str, RenderingProfile] = {
    "fast": RenderingProfile(name="fast", dpi=200),
    "balanced": RenderingProfile(name="balanced", dpi=300),
    "high_quality": RenderingProfile(name="high_quality", dpi=400),
    "engineering": RenderingProfile(name="engineering", dpi=600),
}


class PDFRenderingEngine:
    """Multi-DPI PyMuPDF Page Rendering Engine."""

    @staticmethod
    def select_profile_for_document(doc_type: str, hint_dpi: int = 300) -> RenderingProfile:
        """Select rendering profile based on document classification or DPI requirement."""
        if doc_type == "engineering_drawing":
            return PROFILES["engineering"]
        elif hint_dpi >= 400:
            return PROFILES["high_quality"]
        elif hint_dpi <= 200:
            return PROFILES["fast"]
        return PROFILES["balanced"]

    @classmethod
    def render_pdf_bytes(
        cls, pdf_content: bytes, profile: RenderingProfile = PROFILES["balanced"]
    ) -> List[Tuple[int, np.ndarray, bytes]]:
        """
        Render all pages of a PDF into OpenCV BGR NumPy arrays.
        Returns List of Tuples: [(page_num, numpy_bgr_image, raw_png_bytes)]
        """
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        rendered_pages: List[Tuple[int, np.ndarray, bytes]] = []

        # Calculate PyMuPDF Zoom Matrix based on target DPI (72 DPI baseline)
        zoom = profile.dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        for page_idx in range(doc.page_count):
            page = doc.load_page(page_idx)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Convert PyMuPDF Pixmap to NumPy BGR Array
            img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 3:  # RGB -> BGR for OpenCV
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = img_np

            png_bytes = pix.tobytes("png")
            rendered_pages.append((page_idx + 1, img_bgr, png_bytes))

        doc.close()
        return rendered_pages

    @classmethod
    def render_image_bytes(cls, image_content: bytes) -> List[Tuple[int, np.ndarray, bytes]]:
        """
        Prepare single image file (PNG/JPEG/TIFF/BMP/WEBP) for preprocessing.
        Returns List containing single Tuple: [(1, numpy_bgr_image, raw_png_bytes)]
        """
        img_np = cv2.imdecode(np.frombuffer(image_content, np.uint8), cv2.IMREAD_COLOR)
        if img_np is None:
            raise ValueError("Failed to decode image bytes with OpenCV.")

        success, png_bytes = cv2.imencode(".png", img_np)
        return [(1, img_np, png_bytes.tobytes())]
