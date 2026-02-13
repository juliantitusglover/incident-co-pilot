import pytest
from dataclasses import replace
from datetime import datetime, timezone

from backend.domain.incidents.entities import Incident, TimelineEvent
from backend.domain.incidents.enums import Severity, Status
from backend.services.errors import NotFoundError, ValidationError
from backend.services.incidents.commands import (
    CreateIncidentCmd,
    UpdateIncidentCmd,
    CreateTimelineEventCmd,
    UpdateTimelineEventCmd,
)
from backend.services.incidents.usecases import IncidentUseCases


def _now() -> datetime:
    return datetime.now(timezone.utc)


class FakeIncidentRepo:
    def __init__(self, incidents: list[Incident] | None = None):
        self._incidents: dict[int, Incident] = {i.id: i for i in (incidents or [])}
        self.exists_calls = 0
        self._next_id = (max(self._incidents.keys()) + 1) if self._incidents else 1

    def list(self, *, status: Status | None = None, severity: Severity | None = None) -> list[Incident]:
        items = list(self._incidents.values())
        if status is not None:
            items = [i for i in items if i.status == status]
        if severity is not None:
            items = [i for i in items if i.severity == severity]
        return sorted(items, key=lambda x: x.created_at, reverse=True)

    def get(self, incident_id: int) -> Incident | None:
        return self._incidents.get(incident_id)

    def get_with_events(self, incident_id: int) -> Incident | None:
        return self._incidents.get(incident_id)

    def create(self, incident_data: dict) -> Incident:
        now = _now()
        incident = Incident(
            id=self._next_id,
            title=incident_data["title"],
            description=incident_data["description"],
            severity=incident_data["severity"],
            status=incident_data["status"],
            created_at=now,
            updated_at=now,
            events=[],
        )
        self._incidents[incident.id] = incident
        self._next_id += 1
        return incident

    def update(self, incident_id: int, changes: dict) -> Incident | None:
        inc = self._incidents.get(incident_id)
        if not inc:
            return None

        # mutate in place (dataclass slots=True allows attribute set)
        for k, v in changes.items():
            setattr(inc, k, v)
        inc.updated_at = _now()
        return inc

    def delete(self, incident_id: int) -> bool:
        return self._incidents.pop(incident_id, None) is not None

    def exists(self, incident_id: int) -> bool:
        self.exists_calls += 1
        return incident_id in self._incidents


class FakeEventRepo:
    def __init__(self, events: list[TimelineEvent] | None = None):
        self._events: dict[tuple[int, int], TimelineEvent] = {}
        for e in (events or []):
            self._events[(e.incident_id, e.id)] = e
        self._next_id = (max((e.id for e in (events or [])), default=0) + 1)

    def list_incident_events(self, incident_id: int) -> list[TimelineEvent]:
        items = [e for (iid, _), e in self._events.items() if iid == incident_id]
        return sorted(items, key=lambda x: x.created_at, reverse=True)

    def get(self, incident_id: int, event_id: int) -> TimelineEvent | None:
        return self._events.get((incident_id, event_id))

    def create(self, incident_id: int, event_data: dict) -> TimelineEvent:
        now = _now()
        e = TimelineEvent(
            id=self._next_id,
            incident_id=incident_id,
            occurred_at=event_data["occurred_at"],
            event_type=event_data["event_type"],
            message=event_data["message"],
            created_at=now,
            updated_at=now,
        )
        self._events[(incident_id, e.id)] = e
        self._next_id += 1
        return e

    def update(self, incident_id: int, event_id: int, changes: dict) -> TimelineEvent | None:
        e = self._events.get((incident_id, event_id))
        if not e:
            return None
        for k, v in changes.items():
            setattr(e, k, v)
        e.updated_at = _now()
        return e

    def delete(self, incident_id: int, event_id: int) -> bool:
        return self._events.pop((incident_id, event_id), None) is not None


class FakeUoW:
    """
    Mimics your SqlAlchemyUnitOfWork behaviour:
    commit on success, rollback on exception, context-managed.
    """
    def __init__(self, incidents: FakeIncidentRepo, events: FakeEventRepo):
        self.incidents = incidents
        self.events = events
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc:
            self.rollback()
        else:
            self.commit()
        return False  # don't suppress exceptions

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


def make_incident(
    *,
    incident_id: int = 1,
    status: Status = Status.OPEN,
    severity: Severity = Severity.SEV2,
) -> Incident:
    now = _now()
    return Incident(
        id=incident_id,
        title="Incident",
        description="Desc",
        severity=severity,
        status=status,
        created_at=now,
        updated_at=now,
        events=[],
    )


def make_event(*, incident_id: int, event_id: int = 1) -> TimelineEvent:
    now = _now()
    return TimelineEvent(
        id=event_id,
        incident_id=incident_id,
        occurred_at=now,
        event_type="note",
        message="hello",
        created_at=now,
        updated_at=now,
    )


def test_create_incident_trims_and_persists():
    incidents = FakeIncidentRepo()
    events = FakeEventRepo()
    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        created = uc.create_incident(
            CreateIncidentCmd(title="  A  ", description="  B  ", severity=Severity.SEV1)
        )
        assert created.title == "A"
        assert created.description == "B"
    assert uow.committed is True
    assert uow.rolled_back is False


def test_update_incident_rejects_invalid_status_transition():
    inc = make_incident(status=Status.OPEN)
    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo()

    with pytest.raises(ValidationError) as e:
        with FakeUoW(incidents, events) as uow:
            uc = IncidentUseCases(uow)
            uc.update_incident(inc.id, UpdateIncidentCmd(status=Status.RESOLVED))
        assert "invalid status transition" in str(e.value)
    assert uow.rolled_back is True


def test_get_event_happy_path_does_not_call_exists():
    inc = make_incident(incident_id=1)
    ev = make_event(incident_id=1, event_id=10)

    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo([ev])

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        got = uc.get_event(1, 10)
        assert got.id == 10
        assert incidents.exists_calls == 0


def test_get_event_missing_event_checks_exists_then_chooses_error():
    inc = make_incident(incident_id=1)
    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        with pytest.raises(NotFoundError) as e:
            uc.get_event(1, 999)
        assert str(e.value) == "Event not found"
        assert incidents.exists_calls == 1


def test_get_event_missing_incident_returns_incident_not_found():
    incidents = FakeIncidentRepo([])
    events = FakeEventRepo([])

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        with pytest.raises(NotFoundError) as e:
            uc.get_event(123, 1)
        assert str(e.value) == "Incident not found"
        assert incidents.exists_calls == 1
