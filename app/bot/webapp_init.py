from __future__ import annotations

from urllib.parse import urlencode

from app.core.config import settings


def build_webapp_url(extra_params: dict | None = None) -> str:
    """
    Build WebApp URL with optional extra query params (e.g. deep-link).
    """
    if not settings.TELEGRAM_WEBAPP_URL:
        base = "https://moonlit-garden-frontend.vercel.app"
    else:
        base = str(settings.TELEGRAM_WEBAPP_URL)

    if not extra_params:
        return base

    return f"{base}?{urlencode(extra_params)}"
