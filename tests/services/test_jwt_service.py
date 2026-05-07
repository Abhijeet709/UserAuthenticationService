from datetime import datetime, timedelta, timezone

import jwt as _jwt
import pytest

from services.JWT.jwt import JWT, InvalidToken, TokenExpired


def test_generate_and_verify_round_trip():
    service = JWT(secret_key="s", algorithm="HS256", expires_minutes=60)
    token = service.generate_token(user_id=42)
    payload = service.verify_token(token)
    assert payload["user_id"] == 42
    assert payload["sub"] == "42"
    assert "iat" in payload and "exp" in payload


def test_verify_token_raises_invalid_for_bad_signature():
    issuer = JWT(secret_key="one", algorithm="HS256")
    verifier = JWT(secret_key="two", algorithm="HS256")
    token = issuer.generate_token(user_id=1)
    with pytest.raises(InvalidToken):
        verifier.verify_token(token)


def test_verify_token_raises_expired():
    service = JWT(secret_key="s", algorithm="HS256")
    expired_payload = {
        "sub": "1",
        "user_id": 1,
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    token = _jwt.encode(expired_payload, "s", algorithm="HS256")
    with pytest.raises(TokenExpired):
        service.verify_token(token)
