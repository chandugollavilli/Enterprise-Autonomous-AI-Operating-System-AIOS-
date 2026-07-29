import uuid
import pytest
from src.infrastructure.security.password import hash_password, verify_password
from src.infrastructure.security.jwt import create_access_token, create_refresh_token, decode_token
from src.infrastructure.security.api_key import generate_api_key, hash_api_key


def test_password_hashing():
    raw_pass = "SecureP@ssword123!"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_flow():
    user_id = uuid.uuid4()
    access_token = create_access_token(subject=user_id, claims={"role": "admin"})
    
    payload = decode_token(access_token)
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert payload["role"] == "admin"

    refresh_token = create_refresh_token(subject=user_id)
    refresh_payload = decode_token(refresh_token)
    assert refresh_payload["sub"] == str(user_id)
    assert refresh_payload["type"] == "refresh"


def test_api_key_generation():
    full_key, prefix, key_hash = generate_api_key(prefix="dip_test_")
    assert full_key.startswith("dip_test_")
    assert prefix == full_key[:12]
    assert hash_api_key(full_key) == key_hash
