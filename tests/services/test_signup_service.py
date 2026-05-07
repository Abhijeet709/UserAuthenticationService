from types import SimpleNamespace

import asyncpg
import pytest

from services.signup.signup import SignupService, UserAlreadyExistsError
from services.signup.signup_queries import insert_user_query


class FakeDB:
    """Minimal stand-in for repository.database.Database.

    Each entry in ``responses`` is either a row dict (or ``None``) to be
    returned, or an Exception instance to be raised on the matching call."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls: list[tuple[str, tuple]] = []

    async def fetchrow(self, query, *args):
        self.calls.append((query, args))
        response = self._responses[len(self.calls) - 1]
        if isinstance(response, Exception):
            raise response
        return response


@pytest.mark.asyncio
async def test_signup_success_hashes_password_and_returns_inserted_user():
    db = FakeDB(
        responses=[
            {"id": 1, "email": "user@example.com", "full_name": "Alice"},
        ]
    )
    service = SignupService(db=db)
    payload = SimpleNamespace(
        email="  USER@Example.com ",
        password="Password123",
        full_name=" Alice ",
    )

    result = await service.signup(payload)

    assert result["id"] == 1
    assert len(db.calls) == 1
    assert db.calls[0][0] == insert_user_query
    args = db.calls[0][1]
    assert args[0] == "user@example.com"
    assert args[1] == "Alice"
    assert args[2] != "Password123"
    assert "$" in args[2]


@pytest.mark.asyncio
async def test_signup_raises_when_user_already_exists():
    db = FakeDB(responses=[asyncpg.UniqueViolationError("duplicate key")])
    service = SignupService(db=db)
    payload = SimpleNamespace(
        email="exists@example.com",
        password="Password123",
        full_name="Existing User",
    )

    with pytest.raises(UserAlreadyExistsError, match="already exists"):
        await service.signup(payload)

    assert len(db.calls) == 1
