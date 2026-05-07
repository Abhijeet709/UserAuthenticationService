"""FastAPI application factory and ASGI entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configs.settings import get_settings
from controller.controller import router
from repository.database import Database


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    _configure_logging(settings.LOG_LEVEL)

    database = Database()
    await database.connect()
    app.state.db = database
    try:
        yield
    finally:
        await database.close()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="User Authentication Service",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/", tags=["Health"])
    async def root() -> dict:
        return {"message": "User Authentication Service is running"}

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
