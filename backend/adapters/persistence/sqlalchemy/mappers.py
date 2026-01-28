from __future__ import annotations

from backend.db.models.incident import Incident as IncidentModel
from backend.db.models.timeline_event import TimelineEvent as TimelineEventModel
from backend.domain.incidents.entities import Incident, TimelineEvent

def to_domain_event(model: TimelineEventModel) -> TimelineEvent:
    return TimelineEvent(
        id=model.id,
        incident_id=model.incident_id,
        occurred_at=model.occurred_at,
        event_type=model.event_type,
        message=model.message,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )

def to_domain_incident(model: IncidentModel, *, includes_events: bool = False) -> Incident:
    incident = Incident(
        id=model.id,
        title=model.title,
        description=model.description,
        severity=model.severity,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
        events=[],
    )

    if includes_events:
        incident.events = [to_domain_event(e) for e in (model.events or [])]
    
    return incident