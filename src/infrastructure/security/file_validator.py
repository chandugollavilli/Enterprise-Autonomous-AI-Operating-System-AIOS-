import hashlib
import os
import re
from pathlib import Path
from typing import Dict, Tuple

# Magic Number Signatures mapping
MAGIC_SIGNATURES: Dict[str, Tuple[bytes, str]] = {
    "pdf": (b"%PDF-", "application/pdf"),
    "png": (b"\x89PNG\r\n\x1a\n", "image/png"),
    "jpeg": (b"\xff\xd8\xff", "image/jpeg"),
    "jpg": (b"\xff\xd8\xff", "image/jpeg"),
    "bmp": (b"BM", "image/bmp"),
    "tiff_le": (b"II*\x00", "image/tiff"),
    "tiff_be": (b"MM\x00*", "image/tiff"),
    "webp": (b"RIFF", "image/webp"),  # Starts with RIFF, bytes 8-11 are WEBP
}

MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB max file size


def sanitize_filename(filename: str) -> str:
    """Sanitize original filename to prevent path traversal and shell exploits."""
    clean_name = os.path.basename(filename)
    # Strip dangerous control characters and relative path tokens
    clean_name = re.sub(r"[^\w\s\.-]", "_", clean_name)
    clean_name = clean_name.strip()
    return clean_name or "uploaded_document"


def calculate_sha256(content: bytes) -> str:
    """Calculate SHA-256 checksum string for content."""
    return hashlib.sha256(content).hexdigest()


def detect_file_type_from_magic_bytes(content: bytes) -> Tuple[str, str]:
    """
    Detect genuine file extension and MIME type using header magic bytes.
    Never trusts incoming client header or file extension.
    Returns: (ext, mime_type)
    """
    if not content or len(content) == 0:
        raise ValueError("File validation failed: Empty file payload.")

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"File validation failed: File size ({len(content)} bytes) exceeds max limit ({MAX_FILE_SIZE_BYTES} bytes)."
        )

    # Check magic byte signatures
    if content.startswith(MAGIC_SIGNATURES["pdf"][0]):
        return "pdf", MAGIC_SIGNATURES["pdf"][1]

    if content.startswith(MAGIC_SIGNATURES["png"][0]):
        return "png", MAGIC_SIGNATURES["png"][1]

    if content.startswith(MAGIC_SIGNATURES["jpeg"][0]):
        return "jpeg", MAGIC_SIGNATURES["jpeg"][1]

    if content.startswith(MAGIC_SIGNATURES["bmp"][0]):
        return "bmp", MAGIC_SIGNATURES["bmp"][1]

    if content.startswith(MAGIC_SIGNATURES["tiff_le"][0]) or content.startswith(MAGIC_SIGNATURES["tiff_be"][0]):
        return "tiff", "image/tiff"

    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return "webp", "image/webp"

    raise ValueError(
        "File validation failed: Unsupported or invalid file format header. "
        "Allowed formats: PDF, PNG, JPEG, BMP, TIFF, WEBP."
    )
