class AppError(Exception):
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(message)


class ValidationError(AppError):
    pass


class NotFoundError(AppError):
    pass


class UnauthorizedError(AppError):
    pass