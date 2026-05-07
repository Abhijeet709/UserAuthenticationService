from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=100)

    @field_validator("password")
    @classmethod
    def _password_complexity(cls, value: str) -> str:
        if not any(ch.isalpha() for ch in value):
            raise ValueError("Password must contain at least one letter.")
        if not any(ch.isdigit() for ch in value):
            raise ValueError("Password must contain at least one digit.")
        return value

    @field_validator("full_name")
    @classmethod
    def _full_name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Full name must not be blank.")
        return value
