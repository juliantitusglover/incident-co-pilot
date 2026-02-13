from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from backend.domain.incidents.enums import Severity, Status


@dataclass(frozen=True)
class CreateIncidentCmd:
    title: str
    description: str
    severity: Severity
    status: Status = Status.OPEN


@dataclass(frozen=True)
class UpdateIncidentCmd:
    # only include what can change; optional means “patch”
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[Severity] = None
    status: Optional[Status] = None


@dataclass(frozen=True)
class CreateTimelineEventCmd:
    occurred_at: datetime
    event_type: str
    message: str


@dataclass(frozen=True)
class UpdateTimelineEventCmd:
    occurred_at: Optional[datetime] = None
    event_type: Optional[str] = None
    message: Optional[str] = None
