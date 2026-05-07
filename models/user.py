from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """Public-facing user representation. Never includes the password hash."""

    id: int
    email: EmailStr
    full_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserInDB(User):
    """Internal representation including the stored PBKDF2 password hash."""

    password: str
