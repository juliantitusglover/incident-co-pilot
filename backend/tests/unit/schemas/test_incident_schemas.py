from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.domain.incidents.entities import Incident
from backend.domain.incidents.enums import Severity, Status
from backend.schemas.incident import IncidentCreate, IncidentRead, IncidentUpdate


def _now() -> datetime:
    return datetime.now(timezone.utc)


def test_incident_create_defaults_status_to_open():
    model = IncidentCreate(
        title="Database outage",
        description="Primary unavailable",
        severity="sev1",
    )

    assert model.status is Status.OPEN


def test_incident_create_parses_enum_values():
    model = IncidentCreate(
        title="Database outage",
        description="Primary unavailable",
        severity="sev1",
        status="investigating",
    )

    assert model.severity is Severity.SEV1
    assert model.status is Status.INVESTIGATING


def test_incident_create_strips_whitespace():
    model = IncidentCreate(
        title="  Database outage  ",
        description="  Primary unavailable  ",
        severity="sev2",
    )

    assert model.title == "Database outage"
    assert model.description == "Primary unavailable"


def test_incident_create_rejects_extra_fields():
    with pytest.raises(ValidationError):
        IncidentCreate(
            title="Database outage",
            description="Primary unavailable",
            severity="sev1",
            unexpected="x",
        )


def test_incident_create_rejects_empty_title_after_stripping():
    with pytest.raises(ValidationError):
        IncidentCreate(
            title="   ",
            description="Primary unavailable",
            severity="sev1",
        )


def test_incident_update_allows_partial_fields():
    model = IncidentUpdate(status="resolved")
    assert model.status is Status.RESOLVED
    assert model.title is None
    assert model.description is None
    assert model.severity is None


def test_incident_update_parses_enum_values():
    model = IncidentUpdate(severity="sev4", status="mitigated")

    assert model.severity is Severity.SEV4
    assert model.status is Status.MITIGATED


def test_incident_update_rejects_extra_fields():
    with pytest.raises(ValidationError):
        IncidentUpdate(status="open", unexpected="x")


def test_incident_read_can_be_built_from_domain_entity():
    now = _now()
    incident = Incident(
        id=1,
        title="Database outage",
        description="Primary unavailable",
        severity=Severity.SEV1,
        status=Status.OPEN,
        created_at=now,
        updated_at=now,
        events=[],
    )

    model = IncidentRead.model_validate(incident)

    assert model.id == 1
    assert model.title == "Database outage"
    assert model.severity is Severity.SEV1
    assert model.status is Status.OPEN
    assert model.events == []


def test_incident_create_rejects_title_longer_than_255():
    with pytest.raises(ValidationError):
        IncidentCreate(
            title="x" * 256,
            description="Primary unavailable",
            severity="sev1",
        )


def test_incident_create_rejects_description_longer_than_2000():
    with pytest.raises(ValidationError):
        IncidentCreate(
            title="Database outage",
            description="x" * 2001,
            severity="sev1",
        )
