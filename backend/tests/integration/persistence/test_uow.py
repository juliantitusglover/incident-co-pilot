import pytest

from backend.adapters.persistence.sqlalchemy.repositories import (
    SqlAlchemyIncidentRepository,
    SqlAlchemyTimelineEventRepository,
)
from backend.adapters.persistence.sqlalchemy.uow import SqlAlchemyUnitOfWork
from backend.domain.incidents.enums import Severity, Status


def _incident_data(
    *,
    title="Test Incident",
    description="Something went wrong",
    severity=Severity.SEV2,
    status=Status.OPEN,
):
    return {
        "title": title,
        "description": description,
        "severity": severity,
        "status": status,
    }


def test_uow_exposes_sqlalchemy_repositories_and_commits_on_success(db_session):
    with SqlAlchemyUnitOfWork(session=db_session, close_on_exit=False) as uow:
        assert isinstance(uow.incidents, SqlAlchemyIncidentRepository)
        assert isinstance(uow.events, SqlAlchemyTimelineEventRepository)
        incident = uow.incidents.create(
            _incident_data(title="Committed UoW Incident")
        )

    fetched = SqlAlchemyIncidentRepository(db_session).get(incident.id)

    assert fetched == incident


def test_uow_rolls_back_flushed_incident_on_exception(db_session):
    incident_id = None

    with pytest.raises(RuntimeError):
        with SqlAlchemyUnitOfWork(session=db_session, close_on_exit=False) as uow:
            incident = uow.incidents.create(
                _incident_data(title="Rolled Back UoW Incident")
            )
            incident_id = incident.id
            raise RuntimeError("force rollback")

    assert incident_id is not None
    assert SqlAlchemyIncidentRepository(db_session).get(incident_id) is None
