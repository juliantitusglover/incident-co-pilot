from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.domain.incidents.entities import TimelineEvent
from backend.schemas.timeline_event import (
    TimelineEventCreate,
    TimelineEventRead,
    TimelineEventUpdate,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def test_timeline_event_create_strips_whitespace():
    now = _now()

    model = TimelineEventCreate(
        occurred_at=now,
        event_type="  note  ",
        message="  Investigation started  ",
    )

    assert model.event_type == "note"
    assert model.message == "Investigation started"


def test_timeline_event_create_rejects_extra_fields():
    now = _now()

    with pytest.raises(ValidationError):
        TimelineEventCreate(
            occurred_at=now,
            event_type="note",
            message="Investigation started",
            unexpected="x",
        )


def test_timeline_event_create_rejects_short_message():
    now = _now()

    with pytest.raises(ValidationError):
        TimelineEventCreate(
            occurred_at=now,
            event_type="note",
            message="no",
        )


def test_timeline_event_update_allows_partial_fields():
    model = TimelineEventUpdate(message="Updated message")
    assert model.message == "Updated message"
    assert model.event_type is None
    assert model.occurred_at is None


def test_timeline_event_update_rejects_extra_fields():
    with pytest.raises(ValidationError):
        TimelineEventUpdate(message="Updated message", unexpected="x")


def test_timeline_event_read_can_be_built_from_domain_entity():
    now = _now()
    event = TimelineEvent(
        id=10,
        incident_id=1,
        occurred_at=now,
        event_type="note",
        message="Investigation started",
        created_at=now,
        updated_at=now,
    )

    model = TimelineEventRead.model_validate(event)

    assert model.id == 10
    assert model.incident_id == 1
    assert model.event_type == "note"
    assert model.message == "Investigation started"


def test_timeline_event_create_rejects_event_type_longer_than_50():
    now = _now()

    with pytest.raises(ValidationError):
        TimelineEventCreate(
            occurred_at=now,
            event_type="x" * 51,
            message="Investigation started",
        )


def test_timeline_event_create_rejects_message_longer_than_5000():
    now = _now()

    with pytest.raises(ValidationError):
        TimelineEventCreate(
            occurred_at=now,
            event_type="note",
            message="x" * 5001,
        )
