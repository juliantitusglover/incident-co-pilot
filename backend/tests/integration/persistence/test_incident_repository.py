from datetime import datetime, timezone

from backend.adapters.persistence.sqlalchemy.repositories import (
    SqlAlchemyIncidentRepository,
)
from backend.db.models.timeline_event import TimelineEvent as TimelineEventModel
from backend.domain.incidents.entities import Incident
from backend.domain.incidents.enums import Severity, Status


def _repo(db_session):
    return SqlAlchemyIncidentRepository(db_session)


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


def test_create_incident_returns_domain_incident(db_session):
    repo = _repo(db_session)

    incident = repo.create(
        _incident_data(
            title="Nullable Description Incident",
            description=None,
            severity=Severity.SEV1,
            status=Status.INVESTIGATING,
        )
    )

    assert isinstance(incident, Incident)
    assert incident.id is not None
    assert incident.title == "Nullable Description Incident"
    assert incident.description is None
    assert incident.severity == Severity.SEV1
    assert incident.status == Status.INVESTIGATING
    assert incident.created_at is not None
    assert incident.updated_at is not None


def test_get_incident_returns_created_incident(db_session):
    repo = _repo(db_session)
    created = repo.create(
        _incident_data(
            title="Get Me",
            description="Fetch this incident",
            severity=Severity.SEV3,
            status=Status.OPEN,
        )
    )

    incident = repo.get(created.id)

    assert incident == created


def test_get_incident_missing_returns_none(db_session):
    repo = _repo(db_session)

    assert repo.get(999) is None


def test_list_incidents_returns_empty_list_initially(db_session):
    repo = _repo(db_session)

    assert repo.list() == []


def test_list_incidents_returns_newest_first(db_session):
    repo = _repo(db_session)
    first = repo.create(_incident_data(title="Older Incident"))
    second = repo.create(_incident_data(title="Newer Incident"))

    incidents = repo.list()

    assert [incident.id for incident in incidents] == [second.id, first.id]


def test_list_incidents_filters_by_status(db_session):
    repo = _repo(db_session)
    open_incident = repo.create(
        _incident_data(title="Open Incident", status=Status.OPEN)
    )
    repo.create(
        _incident_data(title="Investigating Incident", status=Status.INVESTIGATING)
    )

    incidents = repo.list(status=Status.OPEN)

    assert [incident.id for incident in incidents] == [open_incident.id]
    assert all(incident.status == Status.OPEN for incident in incidents)


def test_list_incidents_filters_by_severity(db_session):
    repo = _repo(db_session)
    repo.create(_incident_data(title="SEV1 Incident", severity=Severity.SEV1))
    sev3_incident = repo.create(
        _incident_data(title="SEV3 Incident", severity=Severity.SEV3)
    )

    incidents = repo.list(severity=Severity.SEV3)

    assert [incident.id for incident in incidents] == [sev3_incident.id]
    assert all(incident.severity == Severity.SEV3 for incident in incidents)


def test_list_incidents_filters_by_status_and_severity(db_session):
    repo = _repo(db_session)
    matching = repo.create(
        _incident_data(
            title="Matching Incident",
            status=Status.OPEN,
            severity=Severity.SEV1,
        )
    )
    repo.create(
        _incident_data(
            title="Wrong Severity",
            status=Status.OPEN,
            severity=Severity.SEV3,
        )
    )
    repo.create(
        _incident_data(
            title="Wrong Status",
            status=Status.INVESTIGATING,
            severity=Severity.SEV1,
        )
    )

    incidents = repo.list(status=Status.OPEN, severity=Severity.SEV1)

    assert [incident.id for incident in incidents] == [matching.id]
    assert incidents[0].status == Status.OPEN
    assert incidents[0].severity == Severity.SEV1


def test_update_incident_persists_changes(db_session):
    repo = _repo(db_session)
    created = repo.create(_incident_data(title="Original Title"))

    updated = repo.update(
        created.id,
        {
            "title": "Updated Title",
            "description": "Updated description",
            "status": Status.INVESTIGATING,
            "severity": Severity.SEV1,
        },
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.title == "Updated Title"
    assert updated.description == "Updated description"
    assert updated.status == Status.INVESTIGATING
    assert updated.severity == Severity.SEV1

    fetched = repo.get(created.id)
    assert fetched == updated


def test_update_incident_missing_returns_none(db_session):
    repo = _repo(db_session)

    updated = repo.update(999, {"title": "Updated Title"})

    assert updated is None


def test_delete_incident_removes_row(db_session):
    repo = _repo(db_session)
    created = repo.create(_incident_data(title="Delete Me"))

    deleted = repo.delete(created.id)

    assert deleted is True
    assert repo.get(created.id) is None


def test_delete_incident_missing_returns_false(db_session):
    repo = _repo(db_session)

    assert repo.delete(999) is False


def test_exists_returns_true_for_existing_incident(db_session):
    repo = _repo(db_session)
    created = repo.create(_incident_data(title="Existing Incident"))

    assert repo.exists(created.id) is True


def test_exists_returns_false_for_missing_incident(db_session):
    repo = _repo(db_session)

    assert repo.exists(999) is False


def test_get_with_events_returns_incident_with_events(db_session):
    repo = _repo(db_session)
    created = repo.create(_incident_data(title="Incident With Event"))
    event = TimelineEventModel(
        incident_id=created.id,
        occurred_at=datetime(2026, 1, 23, 12, 0, tzinfo=timezone.utc),
        event_type="update",
        message="Restarting the primary node.",
    )
    db_session.add(event)
    db_session.flush()

    incident = repo.get_with_events(created.id)

    assert incident is not None
    assert incident.id == created.id
    assert len(incident.events) == 1
    assert incident.events[0].id == event.id
    assert incident.events[0].incident_id == created.id
    assert incident.events[0].event_type == "update"
    assert incident.events[0].message == "Restarting the primary node."


def test_get_with_events_missing_returns_none(db_session):
    repo = _repo(db_session)

    assert repo.get_with_events(999) is None
