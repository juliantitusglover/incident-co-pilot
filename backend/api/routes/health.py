from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.config import Settings, get_settings
from backend.db.health import is_database_ready

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/live")
def health(settings: Annotated[Settings, Depends(get_settings)]):
    return {"status": "ok", "version": settings.API_VERSION}

@router.get("/ready")
def db_health(settings: Annotated[Settings, Depends(get_settings)]):
    return is_database_ready()
