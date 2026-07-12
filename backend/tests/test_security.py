import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


class TestSecurity:
    def test_hash_and_verify_password(self):
        password = "test_password_123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_create_and_decode_token(self):
        data = {"sub": 1, "role": "user"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == 1
        assert decoded["role"] == "user"

    def test_expired_token(self):
        from datetime import timedelta
        data = {"sub": 1}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        decoded = decode_access_token(token)
        assert decoded is None

    def test_invalid_token(self):
        decoded = decode_access_token("invalid_token_here")
        assert decoded is None
