from datetime import datetime, timezone

from backend.adapters.persistence.sqlalchemy.repositories import (
    SqlAlchemyIncidentRepository,
    SqlAlchemyTimelineEventRepository,
)
from backend.domain.incidents.entities import TimelineEvent
from backend.domain.incidents.enums import Severity, Status


def _incident_repo(db_session):
    return SqlAlchemyIncidentRepository(db_session)


def _event_repo(db_session):
    return SqlAlchemyTimelineEventRepository(db_session)


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


def test_create_event_returns_domain_timeline_event(db_session):
    incident = _incident_repo(db_session).create(
        _incident_data(title="Event Parent Incident")
    )
    repo = _event_repo(db_session)
    occurred_at = datetime(2026, 1, 23, 12, 0, tzinfo=timezone.utc)

    event = repo.create(
        incident.id,
        _event_data(
            occurred_at=occurred_at,
            event_type="mitigation",
            message="Restarted the primary node.",
        ),
    )

    assert isinstance(event, TimelineEvent)
    assert event.id is not None
    assert event.incident_id == incident.id
    assert event.occurred_at == occurred_at
    assert event.event_type == "mitigation"
    assert event.message == "Restarted the primary node."
    assert event.created_at is not None
    assert event.updated_at is not None


def test_get_event_returns_created_event(db_session):
    incident = _incident_repo(db_session).create(_incident_data(title="Get Event"))
    repo = _event_repo(db_session)
    created = repo.create(
        incident.id,
        _event_data(event_type="update", message="Fetching this event."),
    )

    event = repo.get(incident.id, created.id)

    assert event == created


def test_get_event_missing_returns_none(db_session):
    incident = _incident_repo(db_session).create(
        _incident_data(title="Missing Event Parent")
    )
    repo = _event_repo(db_session)

    assert repo.get(incident.id, 999) is None


def test_get_event_wrong_incident_returns_none(db_session):
    incident_repo = _incident_repo(db_session)
    first_incident = incident_repo.create(_incident_data(title="First Incident"))
    second_incident = incident_repo.create(_incident_data(title="Second Incident"))
    repo = _event_repo(db_session)
    event = repo.create(first_incident.id, _event_data())

    assert repo.get(second_incident.id, event.id) is None


def test_list_incident_events_returns_empty_list_initially(db_session):
    incident = _incident_repo(db_session).create(_incident_data(title="No Events"))
    repo = _event_repo(db_session)

    assert repo.list_incident_events(incident.id) == []


def test_list_incident_events_returns_events_for_incident(db_session):
    incident_repo = _incident_repo(db_session)
    first_incident = incident_repo.create(_incident_data(title="First Incident"))
    second_incident = incident_repo.create(_incident_data(title="Second Incident"))
    repo = _event_repo(db_session)
    first_event = repo.create(
        first_incident.id,
        _event_data(event_type="update", message="First incident event."),
    )
    repo.create(
        second_incident.id,
        _event_data(event_type="update", message="Second incident event."),
    )

    events = repo.list_incident_events(first_incident.id)

    assert [event.id for event in events] == [first_event.id]
    assert all(event.incident_id == first_incident.id for event in events)


def test_list_incident_events_returns_newest_first(db_session):
    incident = _incident_repo(db_session).create(_incident_data(title="Ordered Events"))
    repo = _event_repo(db_session)
    first = repo.create(incident.id, _event_data(message="Older event."))
    second = repo.create(incident.id, _event_data(message="Newer event."))

    events = repo.list_incident_events(incident.id)

    assert [event.id for event in events] == [second.id, first.id]


def test_update_event_persists_changes(db_session):
    incident = _incident_repo(db_session).create(_incident_data(title="Update Event"))
    repo = _event_repo(db_session)
    created = repo.create(incident.id, _event_data())
    occurred_at = datetime(2026, 1, 24, 15, 30, tzinfo=timezone.utc)

    updated = repo.update(
        incident.id,
        created.id,
        {
            "occurred_at": occurred_at,
            "event_type": "mitigation",
            "message": "Primary node restarted.",
        },
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.incident_id == incident.id
    assert updated.occurred_at == occurred_at
    assert updated.event_type == "mitigation"
    assert updated.message == "Primary node restarted."

    fetched = repo.get(incident.id, created.id)
    assert fetched == updated


def test_update_event_missing_returns_none(db_session):
    incident = _incident_repo(db_session).create(
        _incident_data(title="Missing Update Event")
    )
    repo = _event_repo(db_session)

    updated = repo.update(incident.id, 999, {"message": "Updated message."})

    assert updated is None


def test_update_event_wrong_incident_returns_none(db_session):
    incident_repo = _incident_repo(db_session)
    first_incident = incident_repo.create(_incident_data(title="First Incident"))
    second_incident = incident_repo.create(_incident_data(title="Second Incident"))
    repo = _event_repo(db_session)
    event = repo.create(first_incident.id, _event_data(message="Original message."))

    updated = repo.update(
        second_incident.id,
        event.id,
        {"message": "Wrong incident update."},
    )

    assert updated is None
    fetched = repo.get(first_incident.id, event.id)
    assert fetched == event


def test_delete_event_removes_row(db_session):
    incident = _incident_repo(db_session).create(_incident_data(title="Delete Event"))
    repo = _event_repo(db_session)
    event = repo.create(incident.id, _event_data())

    deleted = repo.delete(incident.id, event.id)

    assert deleted is True
    assert repo.get(incident.id, event.id) is None


def test_delete_event_missing_returns_false(db_session):
    incident = _incident_repo(db_session).create(
        _incident_data(title="Missing Delete Event")
    )
    repo = _event_repo(db_session)

    assert repo.delete(incident.id, 999) is False


def test_delete_event_wrong_incident_returns_false(db_session):
    incident_repo = _incident_repo(db_session)
    first_incident = incident_repo.create(_incident_data(title="First Incident"))
    second_incident = incident_repo.create(_incident_data(title="Second Incident"))
    repo = _event_repo(db_session)
    event = repo.create(first_incident.id, _event_data())

    deleted = repo.delete(second_incident.id, event.id)

    assert deleted is False
    assert repo.get(first_incident.id, event.id) == event
