from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.config import Settings, get_settings
from backend.db.health import is_database_ready
from backend.schemas.health import (
    HealthLiveResponse,
    HealthReadyErrorResponse,
    HealthReadyResponse,
)

router = APIRouter(prefix="/health", tags=["health"])

@router.get(
    "/live",
    response_model=HealthLiveResponse,
    summary="Check API liveness",
    description="Returns API liveness status and version; does not require database readiness.",
)
def liveness(settings: Annotated[Settings, Depends(get_settings)]):
    return {"status": "ok", "version": settings.API_VERSION}

@router.get(
    "/ready",
    response_model=HealthReadyResponse,
    response_model_exclude_none=True,
    summary="Check API readiness",
    description=(
        "Verifies database connectivity and required tables; returns 503 when "
        "dependencies are not ready."
    ),
    responses={
        200: {"description": "Database is healthy and schema is correct"},
        503: {
            "model": HealthReadyErrorResponse,
            "description": "Database is unreachable or schema is missing",
        },
    }
)
def readiness(health_results: Annotated[dict, Depends(is_database_ready)]):
    if health_results["status"] != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=health_results
        )
    
    return health_results
