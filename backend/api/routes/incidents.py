from fastapi import APIRouter

from backend.core.config import Settings, get_settings

router = APIRouter(prefix=f"{get_settings().API_PREFIX}/incidents", tags=["incidents"])
