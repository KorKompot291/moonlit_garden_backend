from __future__ import annotations

from typing import List

from fastapi import APIRouter

from app.api.deps import CurrentUser, DBSession
from app.schemas.plant import GardenPlant
from app.services.garden_service import get_garden_state

router = APIRouter()


@router.get("/state", response_model=List[GardenPlant], summary="Get garden state")
async def get_garden(db: DBSession, current_user: CurrentUser) -> List[GardenPlant]:
    return await get_garden_state(db, current_user)
