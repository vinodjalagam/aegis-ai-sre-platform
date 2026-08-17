from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions.handlers import register_exception_handlers
from app.core.lifespan.application import lifespan
from app.core.logging.logger import configure_logging
from app.middleware.manager import register_middlewares
from fastapi.middleware.cors import CORSMiddleware

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
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_middlewares(app)
    register_exception_handlers(app)

    app.include_router(api_router)

    return app