import io
from typing import Dict, Tuple
import cv2
import numpy as np
from PIL import Image


class ThumbnailGenerator:
    """Multi-resolution preview thumbnail generator (128px, 256px, 512px)."""

    THUMBNAIL_SIZES: Dict[str, Tuple[int, int]] = {
        "small": (128, 128),
        "medium": (256, 256),
        "large": (512, 512),
    }

    @classmethod
    def generate_thumbnails(cls, image: np.ndarray) -> Dict[str, bytes]:
        """
        Generate PNG bytes for 128px, 256px, 512px preview thumbnails preserving aspect ratio.
        Returns dict: {"small": bytes, "medium": bytes, "large": bytes}
        """
        thumbnails: Dict[str, bytes] = {}

        # Convert OpenCV BGR to PIL RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_img)
        else:
            pil_img = Image.fromarray(image)

        for name, size in cls.THUMBNAIL_SIZES.items():
            thumb = pil_img.copy()
            thumb.thumbnail(size, Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            thumb.save(buffer, format="PNG", optimize=True)
            thumbnails[name] = buffer.getvalue()

        return thumbnails
