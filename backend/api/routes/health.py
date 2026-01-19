from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.config import Settings, get_settings
from backend.db.health import is_database_ready

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/live")
def liveness(settings: Annotated[Settings, Depends(get_settings)]):
    return {"status": "ok", "version": settings.API_VERSION}

@router.get(
    "/ready",
    responses={
        200: {"description": "Database is healthy and schema is correct"},
        503: {"description": "Database is unreachable or schema is missing"},
    }
)
def readiness(health_results: Annotated[dict, Depends(is_database_ready)]):
    if health_results["status"] != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=health_results
        )
    
    return health_results
