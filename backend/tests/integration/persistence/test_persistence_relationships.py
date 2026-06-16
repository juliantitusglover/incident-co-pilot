from datetime import datetime, timezone

from backend.adapters.persistence.sqlalchemy.repositories import (
    SqlAlchemyIncidentRepository,
    SqlAlchemyTimelineEventRepository,
)
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


def _event_data(
    *,
    occurred_at=datetime(2026, 1, 23, 12, 0, tzinfo=timezone.utc),
    event_type="update",
    message="Restarting the primary node.",
):
    return {
        "occurred_at": occurred_at,
        "event_type": event_type,
        "message": message,
    }


def test_delete_incident_cascades_to_timeline_events(db_session):
    incident_repo = SqlAlchemyIncidentRepository(db_session)
    event_repo = SqlAlchemyTimelineEventRepository(db_session)
    incident = incident_repo.create(_incident_data(title="Incident With Event"))
    event = event_repo.create(incident.id, _event_data())

    assert event_repo.get(incident.id, event.id) == event

    deleted = incident_repo.delete(incident.id)

    assert deleted is True
    assert event_repo.get(incident.id, event.id) is None
