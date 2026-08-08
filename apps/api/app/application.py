from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions.handlers import register_exception_handlers
from app.core.lifespan.application import lifespan
from app.core.logging.logger import configure_logging
from app.middleware.manager import register_middlewares


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """

    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    register_middlewares(app)
    register_exception_handlers(app)

    app.include_router(api_router)

    return app