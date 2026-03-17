from datetime import datetime, timezone

from backend.domain.incidents.entities import Incident, TimelineEvent
from backend.domain.incidents.enums import Severity, Status


def _now() -> datetime:
    return datetime.now(timezone.utc)


def test_timeline_event_constructs_with_expected_fields():
    now = _now()

    event = TimelineEvent(
        id=10,
        incident_id=1,
        occurred_at=now,
        event_type="update",
        message="Restarting node",
        created_at=now,
        updated_at=now,
    )

    assert event.id == 10
    assert event.incident_id == 1
    assert event.occurred_at == now
    assert event.event_type == "update"
    assert event.message == "Restarting node"
    assert event.created_at == now
    assert event.updated_at == now


def test_incident_constructs_with_expected_fields():
    now = _now()

    incident = Incident(
        id=1,
        title="Database outage",
        description="Primary unavailable",
        severity=Severity.SEV1,
        status=Status.INVESTIGATING,
        created_at=now,
        updated_at=now,
    )

    assert incident.id == 1
    assert incident.title == "Database outage"
    assert incident.description == "Primary unavailable"
    assert incident.severity == Severity.SEV1
    assert incident.status == Status.INVESTIGATING
    assert incident.created_at == now
    assert incident.updated_at == now
    assert incident.events == []


def test_incident_allows_none_description():
    now = _now()

    incident = Incident(
        id=1,
        title="Database outage",
        description=None,
        severity=Severity.SEV2,
        status=Status.OPEN,
        created_at=now,
        updated_at=now,
    )

    assert incident.description is None


def test_incident_defaults_events_to_empty_list():
    now = _now()

    incident = Incident(
        id=1,
        title="Database outage",
        description="desc",
        severity=Severity.SEV2,
        status=Status.OPEN,
        created_at=now,
        updated_at=now,
    )

    assert incident.events == []


def test_incident_events_default_list_is_not_shared_between_instances():
    now = _now()

    a = Incident(
        id=1,
        title="A",
        description="desc",
        severity=Severity.SEV2,
        status=Status.OPEN,
        created_at=now,
        updated_at=now,
    )
    b = Incident(
        id=2,
        title="B",
        description="desc",
        severity=Severity.SEV3,
        status=Status.OPEN,
        created_at=now,
        updated_at=now,
    )

    a.events.append(
        TimelineEvent(
            id=100,
            incident_id=1,
            occurred_at=now,
            event_type="note",
            message="Only on A",
            created_at=now,
            updated_at=now,
        )
    )

    assert len(a.events) == 1
    assert b.events == []

def test_incident_uses_slots():
    assert hasattr(Incident, "__slots__")


def test_timeline_event_uses_slots():
    assert hasattr(TimelineEvent, "__slots__")
