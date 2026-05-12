from services.errors import AppError
class TokenExpired(AppError):
    def __init__(self, exc: Exception):
        super().__init__(message="Token has expired", code="401", details=str(exc))

class InvalidToken(AppError):
    def __init__(self, exc: Exception):
        super().__init__(message="Invalid token", code="402", details=str(exc))