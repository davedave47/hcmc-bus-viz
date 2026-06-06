"""FastAPI application factory — wiring only."""
from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.deps import close_warehouse
from .api.errors import register_error_handlers
from .api.routers import charts, health
from .config import settings
from .core.logging import request_logging_middleware, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Warehouse is opened lazily on first use; ensure it's closed on shutdown.
    yield
    close_warehouse()


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="HCMC Bus Analytics API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(request_logging_middleware)
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(charts.router)
    return app


app = create_app()
