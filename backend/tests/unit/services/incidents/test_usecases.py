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

    def list(
        self, *, status: Status | None = None, severity: Severity | None = None
    ) -> list[Incident]:
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
        for e in events or []:
            self._events[(e.incident_id, e.id)] = e
        self._next_id = max((e.id for e in (events or [])), default=0) + 1

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

    def update(
        self, incident_id: int, event_id: int, changes: dict
    ) -> TimelineEvent | None:
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
    title: str = "Incident",
    description: str = "Desc",
    status: Status = Status.OPEN,
    severity: Severity = Severity.SEV2,
    events: list[TimelineEvent] | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> Incident:
    now = _now()
    created = created_at or now
    updated = updated_at or created

    return Incident(
        id=incident_id,
        title=title,
        description=description,
        severity=severity,
        status=status,
        created_at=created,
        updated_at=updated,
        events=[] if events is None else list(events),
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
            CreateIncidentCmd(
                title="  A  ", description="  B  ", severity=Severity.SEV1
            )
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


def test_list_incidents_returns_all_when_no_filters():
    older_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
    newer_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

    older = make_incident(
        incident_id=1, title="Older", created_at=older_time, updated_at=older_time
    )
    newer = make_incident(
        incident_id=2, title="Newer", created_at=newer_time, updated_at=newer_time
    )
    incidents = FakeIncidentRepo([older, newer])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        got = uc.list_incidents()

    assert [i.id for i in got] == [2, 1]


def test_list_incidents_passes_status_filter():
    open_incident = make_incident(incident_id=1, status=Status.OPEN)
    investigating_incident = make_incident(incident_id=2, status=Status.INVESTIGATING)
    incidents = FakeIncidentRepo([open_incident, investigating_incident])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        got = uc.list_incidents(status=Status.OPEN)

    assert [i.id for i in got] == [1]


def test_list_incidents_passes_severity_filter():
    sev1_incident = make_incident(incident_id=1, severity=Severity.SEV1)
    sev3_incident = make_incident(incident_id=2, severity=Severity.SEV3)
    incidents = FakeIncidentRepo([sev1_incident, sev3_incident])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        got = uc.list_incidents(severity=Severity.SEV3)

    assert [i.id for i in got] == [2]


def test_get_incident_without_events_uses_plain_get():
    inc = make_incident(incident_id=1)
    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        got = uc.get_incident(1, with_events=False)

    assert got.id == 1
    assert got.events == []


def test_get_incident_with_events_uses_get_with_events():
    ev = make_event(incident_id=1, event_id=10)
    inc = make_incident(incident_id=1, events=[ev])
    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo([ev])

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        got = uc.get_incident(1, with_events=True)

    assert got.id == 1
    assert len(got.events) == 1
    assert got.events[0].id == 10


def test_get_incident_missing_raises_not_found():
    incidents = FakeIncidentRepo([])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        with pytest.raises(NotFoundError) as e:
            uc.get_incident(123)

    assert str(e.value) == "Incident not found"


def test_create_incident_rejects_empty_title_after_trimming():
    incidents = FakeIncidentRepo()
    events = FakeEventRepo()

    with pytest.raises(ValidationError) as e:
        with FakeUoW(incidents, events) as uow:
            uc = IncidentUseCases(uow)
            uc.create_incident(
                CreateIncidentCmd(
                    title="   ",
                    description="Valid description",
                    severity=Severity.SEV1,
                )
            )

    assert str(e.value) == "title cannot be empty"
    assert uow.committed is False
    assert uow.rolled_back is True


def test_create_incident_rejects_empty_description_after_trimming():
    incidents = FakeIncidentRepo()
    events = FakeEventRepo()

    with pytest.raises(ValidationError) as e:
        with FakeUoW(incidents, events) as uow:
            uc = IncidentUseCases(uow)
            uc.create_incident(
                CreateIncidentCmd(
                    title="Valid title",
                    description="   ",
                    severity=Severity.SEV1,
                )
            )

    assert str(e.value) == "description cannot be empty"
    assert uow.committed is False
    assert uow.rolled_back is True


def test_create_incident_rolls_back_on_validation_error():
    incidents = FakeIncidentRepo()
    events = FakeEventRepo()

    with pytest.raises(ValidationError):
        with FakeUoW(incidents, events) as uow:
            uc = IncidentUseCases(uow)
            uc.create_incident(
                CreateIncidentCmd(
                    title="   ",
                    description="   ",
                    severity=Severity.SEV1,
                )
            )

    assert uow.committed is False
    assert uow.rolled_back is True


def test_update_incident_trims_title_and_description():
    inc = make_incident(incident_id=1, title="Old", description="Old desc")
    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        updated = uc.update_incident(
            1,
            UpdateIncidentCmd(
                title="  New title  ",
                description="  New description  ",
            ),
        )

    assert updated.title == "New title"
    assert updated.description == "New description"
    assert uow.committed is True
    assert uow.rolled_back is False


def test_update_incident_allows_valid_open_to_investigating_transition():
    inc = make_incident(incident_id=1, status=Status.OPEN)
    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        updated = uc.update_incident(1, UpdateIncidentCmd(status=Status.INVESTIGATING))

    assert updated.status is Status.INVESTIGATING
    assert uow.committed is True
    assert uow.rolled_back is False


def test_update_incident_allows_valid_investigating_to_mitigated_transition():
    inc = make_incident(incident_id=1, status=Status.INVESTIGATING)
    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        updated = uc.update_incident(1, UpdateIncidentCmd(status=Status.MITIGATED))

    assert updated.status is Status.MITIGATED
    assert uow.committed is True
    assert uow.rolled_back is False


def test_update_incident_missing_incident_raises_not_found():
    incidents = FakeIncidentRepo([])
    events = FakeEventRepo()

    with pytest.raises(NotFoundError) as e:
        with FakeUoW(incidents, events) as uow:
            uc = IncidentUseCases(uow)
            uc.update_incident(123, UpdateIncidentCmd(title="Updated"))

    assert str(e.value) == "Incident not found"
    assert uow.committed is False
    assert uow.rolled_back is True


def test_update_incident_rejects_empty_title_after_trimming():
    inc = make_incident(incident_id=1)
    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo()

    with pytest.raises(ValidationError) as e:
        with FakeUoW(incidents, events) as uow:
            uc = IncidentUseCases(uow)
            uc.update_incident(1, UpdateIncidentCmd(title="   "))

    assert str(e.value) == "title cannot be empty"
    assert uow.committed is False
    assert uow.rolled_back is True


def test_update_incident_rejects_empty_description_after_trimming():
    inc = make_incident(incident_id=1)
    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo()

    with pytest.raises(ValidationError) as e:
        with FakeUoW(incidents, events) as uow:
            uc = IncidentUseCases(uow)
            uc.update_incident(1, UpdateIncidentCmd(description="   "))

    assert str(e.value) == "description cannot be empty"
    assert uow.committed is False
    assert uow.rolled_back is True


def test_delete_incident_happy_path():
    inc = make_incident(incident_id=1)
    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        uc.delete_incident(1)

    assert 1 not in incidents._incidents
    assert uow.committed is True
    assert uow.rolled_back is False


def test_delete_incident_missing_raises_not_found():
    incidents = FakeIncidentRepo([])
    events = FakeEventRepo()

    with pytest.raises(NotFoundError) as e:
        with FakeUoW(incidents, events) as uow:
            uc = IncidentUseCases(uow)
            uc.delete_incident(123)

    assert str(e.value) == "Incident not found"
    assert uow.committed is False
    assert uow.rolled_back is True


def test_list_incidents_commits_on_success():
    incidents = FakeIncidentRepo([make_incident(incident_id=1)])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        got = uc.list_incidents()

    assert len(got) == 1
    assert uow.committed is True
    assert uow.rolled_back is False


def test_get_incident_commits_on_success():
    inc = make_incident(incident_id=1)
    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        got = uc.get_incident(1)

    assert got.id == 1
    assert uow.committed is True
    assert uow.rolled_back is False


def test_update_incident_commits_on_success():
    inc = make_incident(incident_id=1, title="Old")
    incidents = FakeIncidentRepo([inc])
    events = FakeEventRepo()

    with FakeUoW(incidents, events) as uow:
        uc = IncidentUseCases(uow)
        updated = uc.update_incident(1, UpdateIncidentCmd(title="Updated"))

    assert updated.title == "Updated"
    assert uow.committed is True
    assert uow.rolled_back is False


def test_delete_incident_rolls_back_on_not_found():
    incidents = FakeIncidentRepo([])
    events = FakeEventRepo()

    with pytest.raises(NotFoundError):
        with FakeUoW(incidents, events) as uow:
            uc = IncidentUseCases(uow)
            uc.delete_incident(999)

    assert uow.committed is False
    assert uow.rolled_back is True
