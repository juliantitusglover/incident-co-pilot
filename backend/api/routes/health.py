from typing import Annotated

from fastapi import APIRouter, Depends

from backend.core.config import Settings, get_settings

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health(settings: Annotated[Settings, Depends(get_settings)]):
    return {"status": "ok", "version": settings.API_VERSION}
