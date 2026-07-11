from __future__ import annotations

from secrets import compare_digest
from typing import Annotated, Generator

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from backend.db.sessions import get_db
from backend.adapters.persistence.sqlalchemy.uow import SqlAlchemyUnitOfWork
from backend.core.config import Settings, get_settings
from backend.domain.incidents.ports import UnitOfWork
from backend.services.incidents.usecases import IncidentUseCases

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_uow(session: Session = Depends(get_db)) -> Generator[UnitOfWork, None, None]:
    with SqlAlchemyUnitOfWork(session=session, close_on_exit=False) as uow:
        yield uow

def get_incident_usecases(uow: UnitOfWork = Depends(get_uow)) -> IncidentUseCases:
    return IncidentUseCases(uow)

def require_api_key(
    api_key: Annotated[str | None, Security(api_key_header)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    if not settings.API_AUTH_ENABLED:
        return None

    if not settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API authentication is enabled but API_KEY is not configured",
        )

    if not api_key or not compare_digest(api_key, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    return None
