import math
from typing import Dict, Any
import cv2
import numpy as np


class ImageQualityAnalyzer:
    """Image Quality Metrics Assessor (Blur, Sharpness, Contrast, Brightness, Noise)."""

    @staticmethod
    def analyze(image: np.ndarray) -> Dict[str, Any]:
        """
        Compute image quality metrics.
        Returns dictionary of metrics.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        h, w = gray.shape[:2]

        # 1. Blur Score (Variance of Laplacian)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        is_blurry = laplacian_var < 100.0  # Threshold under 100 is blurry

        # 2. Mean Brightness (0 - 255)
        brightness = float(np.mean(gray))

        # 3. RMS Contrast (Standard deviation of pixel intensities)
        contrast = float(np.std(gray))

        # 4. Noise Estimation (Difference from Gaussian blur)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise_estimate = float(np.std(gray.astype(np.float32) - blurred.astype(np.float32)))

        return {
            "blur_score": round(laplacian_var, 2),
            "is_blurry": is_blurry,
            "brightness": round(brightness, 2),
            "contrast": round(contrast, 2),
            "noise_estimate": round(noise_estimate, 2),
            "width": w,
            "height": h,
            "aspect_ratio": round(w / float(h), 2),
        }


class ImageClassifier:
    """Heuristic / Rule-based Document Type Classifier."""

    @staticmethod
    def classify(image: np.ndarray, text_content: str = "") -> str:
        """Classify document image based on aspect ratio, dimensions, and visual density."""
        h, w = image.shape[:2]
        aspect_ratio = w / float(h)

        if text_content:
            text_lower = text_content.lower()
            if "invoice" in text_lower or "total" in text_lower:
                return "invoice"
            if "agreement" in text_lower or "contract" in text_lower:
                return "contract"

        if w > 3000 or h > 3000 or (aspect_ratio > 1.8 or aspect_ratio < 0.4):
            return "engineering_drawing"

        if aspect_ratio > 1.2:
            return "landscape_document"

        return "document"
