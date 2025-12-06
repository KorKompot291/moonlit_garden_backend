from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.core.config import settings

logger = logging.getLogger("moonlit_garden")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.APP_DEBUG,
    )

    origins: list[str] = []
    if settings.TELEGRAM_WEBAPP_URL:
        origins.append(str(settings.TELEGRAM_WEBAPP_URL))
    origins.extend(
        [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "The moon's magic flickers. Please try again later."},
        )

    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, Any]:
        return {"status": "ok", "env": settings.APP_ENV}

    app.include_router(api_router, prefix="/api")

    return app


app = create_app()
