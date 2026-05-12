# app/core/exception_handlers.py

from fastapi import Request
from fastapi.responses import JSONResponse
from services.errors import AppError


async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )