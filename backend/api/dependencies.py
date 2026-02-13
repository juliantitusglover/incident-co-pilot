from __future__ import annotations

from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.db.sessions import get_db
from backend.adapters.persistence.sqlalchemy.uow import SqlAlchemyUnitOfWork
from backend.domain.incidents.ports import UnitOfWork
from backend.services.incidents.usecases import IncidentUseCases

def get_uow(session: Session = Depends(get_db)) -> Generator[UnitOfWork, None, None]:
    with SqlAlchemyUnitOfWork(session=session, close_on_exit=False) as uow:
        yield uow

def get_incident_usecases(uow: UnitOfWork = Depends(get_uow)) -> IncidentUseCases:
    return IncidentUseCases(uow)