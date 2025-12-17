from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.APP_DEBUG,
    )

    # CORS
    cors_origins = [str(o) for o in settings.BACKEND_CORS_ORIGINS]
    if settings.TELEGRAM_WEBAPP_URL:
        cors_origins.append(str(settings.TELEGRAM_WEBAPP_URL))

    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router, prefix="/api")

    @app.get("/health", tags=["system"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
