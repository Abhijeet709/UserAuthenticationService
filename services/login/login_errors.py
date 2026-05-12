from services.errors import AppError
class InvalidCredentialsError(AppError):
    def __init__(self, exc: Exception):
        super().__init__(message="Invalid credentials", code="403", details=str(exc))
    """Raised when an email/password pair does not authenticate."""
