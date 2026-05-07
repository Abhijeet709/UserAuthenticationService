"""Login service. Verifies credentials and issues a JWT."""
import logging
from typing import Any, Optional

from repository.database import Database
from services.JWT.jwt import JWT
from services.login.login_queries import user_by_email_query
from services.signup.signup_utils import hash_password, verify_password
from services.utils import normalize_email


logger = logging.getLogger(__name__)

# Pre-computed dummy hash used to keep login response time roughly constant
# whether or not the email exists. Helps mitigate user-enumeration via timing.
_DUMMY_HASH = hash_password("not-a-real-password")


class InvalidCredentialsError(Exception):
    """Raised when an email/password pair does not authenticate."""


class LoginService:
    def __init__(self, db: Database, jwt_service: Optional[JWT] = None) -> None:
        self.db = db
        self.jwt_service = jwt_service or JWT()

    async def login(self, email: str, password: str) -> dict[str, Any]:
        normalized_email = normalize_email(email)

        row = await self.db.fetchrow(user_by_email_query, normalized_email)

        if row is None:
            # Run verify against a dummy hash so timing matches the success path.
            verify_password(password, _DUMMY_HASH)
            logger.info("Login failed: user not found")
            raise InvalidCredentialsError("Invalid email or password.")

        if not verify_password(password, row["password"]):
            logger.info("Login failed: bad password for user_id=%s", row["id"])
            raise InvalidCredentialsError("Invalid email or password.")

        token = self.jwt_service.generate_token(user_id=row["id"])
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": row["id"],
                "email": row["email"],
                "full_name": row["full_name"],
            },
        }
