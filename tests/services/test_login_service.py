import pytest

from services.JWT.jwt import JWT
from services.login.login import InvalidCredentialsError, LoginService
from services.signup.signup_utils import hash_password

from tests.fakes import FakeDB


@pytest.mark.asyncio
async def test_login_success_returns_token_and_user():
    db = FakeDB(
        responses=[
            {
                "id": 5,
                "email": "user@example.com",
                "full_name": "User Name",
                "password": hash_password("Password123"),
            }
        ]
    )
    service = LoginService(db=db)

    result = await service.login(email=" USER@example.com ", password="Password123")

    assert result["token_type"] == "bearer"
    assert result["user"]["id"] == 5
    assert result["user"]["email"] == "user@example.com"
    assert db.calls[0][1] == ("user@example.com",)

    decoded = JWT(secret_key="test-secret", algorithm="HS256").verify_token(
        result["access_token"]
    )
    assert decoded["user_id"] == 5
    assert decoded["sub"] == "5"


@pytest.mark.asyncio
async def test_login_raises_for_wrong_password():
    db = FakeDB(
        responses=[
            {
                "id": 5,
                "email": "user@example.com",
                "full_name": "User Name",
                "password": hash_password("Password123"),
            }
        ]
    )
    service = LoginService(db=db)

    with pytest.raises(InvalidCredentialsError, match="Invalid email or password"):
        await service.login(email="user@example.com", password="WrongPassword1")


@pytest.mark.asyncio
async def test_login_raises_when_user_not_found():
    db = FakeDB(responses=[None])
    service = LoginService(db=db)

    with pytest.raises(InvalidCredentialsError, match="Invalid email or password"):
        await service.login(email="missing@example.com", password="Password123")


@pytest.mark.asyncio
async def test_login_uses_injected_jwt_service():
    """Regression: the service must honour the injected JWT instance."""
    db = FakeDB(
        responses=[
            {
                "id": 7,
                "email": "user@example.com",
                "full_name": "User Name",
                "password": hash_password("Password123"),
            }
        ]
    )
    custom_jwt = JWT(secret_key="other-secret", algorithm="HS256")
    service = LoginService(db=db, jwt_service=custom_jwt)

    result = await service.login(email="user@example.com", password="Password123")

    decoded = JWT(secret_key="other-secret", algorithm="HS256").verify_token(
        result["access_token"]
    )
    assert decoded["user_id"] == 7
