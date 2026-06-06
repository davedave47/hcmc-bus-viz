"""Global exception handlers — structured JSON, no stack leakage; errors are logged.

HTTPException + validation errors keep FastAPI's built-in handlers; these cover the
*unhandled* paths (a missing warehouse, a query failure) so clients get a clean
status + shape instead of an opaque 500 with a traceback.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

log = logging.getLogger("busanalytics_api.errors")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(FileNotFoundError)
    async def _warehouse_missing(request: Request, exc: FileNotFoundError) -> JSONResponse:
        log.error("warehouse unavailable: %s", exc)
        return JSONResponse(
            status_code=503,
            content={"error": "warehouse_unavailable", "detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        log.exception("unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"error": "internal_error"})
