# backend/domain/incidents/entities.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from backend.domain.incidents.enums import Severity, Status


@dataclass(slots=True)
class TimelineEvent:
    id: int
    incident_id: int
    occurred_at: datetime
    event_type: str
    message: str
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class Incident:
    id: int
    title: str
    description: str | None
    severity: Severity
    status: Status
    created_at: datetime
    updated_at: datetime
    events: list[TimelineEvent] = field(default_factory=list)
