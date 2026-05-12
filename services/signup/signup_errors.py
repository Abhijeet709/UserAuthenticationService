from services.errors import AppError
class UserAlreadyExistsError(AppError):
    def __init__(self, exc: Exception):
        super().__init__(message="User already exists", code="409", details=str(exc))
