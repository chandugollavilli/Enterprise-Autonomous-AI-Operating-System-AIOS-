import secrets
import hashlib
from typing import Tuple


def generate_api_key(prefix: str = "dip_live_") -> Tuple[str, str, str]:
    """
    Generate an API key.
    Returns: (full_key, key_prefix, key_hash)
    """
    random_bytes = secrets.token_hex(24)
    full_key = f"{prefix}{random_bytes}"
    key_prefix = full_key[:12]
    key_hash = hashlib.sha256(full_key.encode("utf-8")).hexdigest()
    return full_key, key_prefix, key_hash


def hash_api_key(key: str) -> str:
    """Hash raw API key for database lookup comparison."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()
