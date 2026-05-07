"""HTTP layer: routes, dependency injection, and exception mapping."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from models.login_request import LoginRequest
from models.sign_up_request import SignupRequest
from repository.database import Database
from services.JWT.jwt import JWT, InvalidToken, TokenExpired
from services.login.login import InvalidCredentialsError, LoginService
from services.signup.signup import SignupService, UserAlreadyExistsError


router = APIRouter(prefix="/auth", tags=["Authentication"])

_bearer_scheme = HTTPBearer(auto_error=False)


def get_db(request: Request) -> Database:
    db: Database | None = getattr(request.app.state, "db", None)
    if db is None:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not initialised.",
        )
    return db


def get_jwt_service() -> JWT:
    return JWT()


def get_signup_service(
    db: Annotated[Database, Depends(get_db)],
) -> SignupService:
    return SignupService(db=db)


def get_login_service(
    db: Annotated[Database, Depends(get_db)],
    jwt_service: Annotated[JWT, Depends(get_jwt_service)],
) -> LoginService:
    return LoginService(db=db, jwt_service=jwt_service)


def get_current_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ],
    jwt_service: Annotated[JWT, Depends(get_jwt_service)],
) -> int:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt_service.verify_token(credentials.credentials)
    except TokenExpired as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Token expired.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except InvalidToken as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("user_id")
    if not isinstance(user_id, int):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing a user_id claim.",
        )
    return user_id


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    payload: SignupRequest,
    service: Annotated[SignupService, Depends(get_signup_service)],
) -> dict:
    try:
        user = await service.signup(payload)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "message": "Signup successful.",
    }


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    payload: LoginRequest,
    service: Annotated[LoginService, Depends(get_login_service)],
) -> dict:
    try:
        return await service.login(email=payload.email, password=payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.get("/me")
async def me(
    user_id: Annotated[int, Depends(get_current_user_id)],
) -> dict:
    return {"user_id": user_id}
