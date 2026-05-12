"""Signup service. Creates a new user, relying on the DB UNIQUE constraint
on `users.email` to atomically reject duplicates (no read-then-insert race)."""
from __future__ import annotations

import logging
from typing import Any

import asyncpg

from models.sign_up_request import SignupRequest
from repository.database import Database
from services.signup.signup_queries import insert_user_query
from services.signup.signup_utils import hash_password
from services.utils import normalize_email


logger = logging.getLogger(__name__)


class SignupService:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def signup(self, payload: SignupRequest) -> dict[str, Any]:
        email = normalize_email(payload.email)
        full_name = payload.full_name.strip()
        hashed_password = hash_password(payload.password)

        try:
            row = await self.db.fetchrow(
                insert_user_query,
                email,
                full_name,
                hashed_password,
            )
        except asyncpg.UniqueViolationError as exc:
            logger.info("Signup conflict for email=%s", email)
            raise UserAlreadyExistsError(
                "User with this email already exists."
            ) from exc

        if row is None:
            raise RuntimeError("Unable to create user.")

        return row
