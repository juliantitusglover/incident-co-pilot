from __future__ import annotations

from typing import Callable, Optional

from sqlalchemy.orm import Session

from backend.domain.incidents.ports import UnitOfWork
from backend.adapters.persistence.sqlalchemy.repositories import (
    SqlAlchemyIncidentRepository,
    SqlAlchemyTimelineEventRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(
        self,
        *,
        session: Session | None = None,
        session_factory: Callable[[], Session] | None = None,
        close_on_exit: bool = True,
    ):
        if (session is None) == (session_factory is None):
            raise ValueError("Provide exactly one of session= or session_factory=")

        self._external_session = session is not None
        self._session = session
        self._session_factory = session_factory
        self._close_on_exit = close_on_exit

        self.incidents = None
        self.events = None

    @property
    def session(self) -> Session:
        assert self._session is not None, "UoW session not initialised"
        return self._session

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        if self._session is None:
            assert self._session_factory is not None
            self._session = self._session_factory()
        self.incidents = SqlAlchemyIncidentRepository(self.session)
        self.events = SqlAlchemyTimelineEventRepository(self.session)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc:
                self.rollback()
            else:
                self.commit()
        finally:
            if (not self._external_session) or self._close_on_exit:
                self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
