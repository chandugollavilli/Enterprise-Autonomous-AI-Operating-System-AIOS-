import pytest
from src.infrastructure.security.file_validator import (
    sanitize_filename,
    calculate_sha256,
    detect_file_type_from_magic_bytes,
)


def test_sanitize_filename():
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("my invoice #123 (final).pdf") == "my invoice _123 _final_.pdf"
    assert sanitize_filename("  clean_name.png  ") == "clean_name.png"


def test_calculate_sha256():
    content = b"Sample Document Stream"
    sha = calculate_sha256(content)
    assert len(sha) == 64
    assert sha == calculate_sha256(content)


def test_magic_byte_detection():
    # PDF
    pdf_bytes = b"%PDF-1.7 header..."
    ext, mime = detect_file_type_from_magic_bytes(pdf_bytes)
    assert ext == "pdf"
    assert mime == "application/pdf"

    # PNG
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR..."
    ext, mime = detect_file_type_from_magic_bytes(png_bytes)
    assert ext == "png"
    assert mime == "image/png"

    # JPEG
    jpeg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF..."
    ext, mime = detect_file_type_from_magic_bytes(jpeg_bytes)
    assert ext == "jpeg"
    assert mime == "image/jpeg"

    # Invalid / Fake file
    fake_bytes = b"This is plain text pretending to be a pdf"
    with pytest.raises(ValueError, match="Unsupported or invalid file format"):
        detect_file_type_from_magic_bytes(fake_bytes)
