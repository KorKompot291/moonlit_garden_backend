from __future__ import annotations

from fastapi import APIRouter

from . import artifacts, auth, garden, habits, lunar

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(habits.router, prefix="/habits", tags=["habits"])
api_router.include_router(artifacts.router, prefix="/artifacts", tags=["artifacts"])
api_router.include_router(lunar.router, prefix="/lunar", tags=["lunar"])
api_router.include_router(garden.router, prefix="/garden", tags=["garden"])
