"""JWT issuance and verification."""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt as _jwt

from configs.settings import get_settings
from services.JWT.jwt_errors import TokenExpired, InvalidToken


class JWT:
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
        expires_minutes: Optional[int] = None,
    ) -> None:
        settings = get_settings()
        self.secret_key = secret_key if secret_key is not None else settings.JWT_SECRET_KEY
        self.algorithm = algorithm if algorithm is not None else settings.JWT_ALGORITHM
        self.expires_minutes = (
            expires_minutes if expires_minutes is not None else settings.JWT_EXPIRES_MINUTES
        )

    def generate_token(self, user_id: int) -> str:
        now = datetime.now(timezone.utc)
        payload: dict[str, Any] = {
            "sub": str(user_id),
            "user_id": user_id,
            "iat": now,
            "exp": now + timedelta(minutes=self.expires_minutes),
        }
        return _jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict[str, Any]:
        try:
            return _jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except _jwt.ExpiredSignatureError as exc:
            raise TokenExpired(exc)
        except _jwt.InvalidTokenError as exc:
            raise InvalidToken(exc)
