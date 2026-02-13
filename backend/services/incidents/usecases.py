from __future__ import annotations

from backend.services.errors import NotFoundError, ValidationError
from backend.services.incidents.commands import (
    CreateIncidentCmd,
    UpdateIncidentCmd,
    CreateTimelineEventCmd,
    UpdateTimelineEventCmd,
)
from backend.domain.incidents.entities import Incident, TimelineEvent
from backend.domain.incidents.enums import Severity, Status
from backend.domain.incidents.ports import UnitOfWork


_ALLOWED_STATUS_TRANSITIONS: dict[Status, set[Status]] = {
    Status.OPEN: {Status.OPEN, Status.INVESTIGATING},
    Status.INVESTIGATING: {Status.INVESTIGATING, Status.MITIGATED, Status.RESOLVED},
    Status.MITIGATED: {Status.MITIGATED, Status.RESOLVED},
    Status.RESOLVED: {Status.RESOLVED},
}


class IncidentUseCases:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def list_incidents(self, *, status: Status | None = None, severity: Severity | None = None) -> list[Incident]:
        return self.uow.incidents.list(status=status, severity=severity)

    def get_incident(self, incident_id: int, *, with_events: bool = False) -> Incident:
        incident = (
            self.uow.incidents.get_with_events(incident_id)
            if with_events
            else self.uow.incidents.get(incident_id)
        )
        if not incident:
            raise NotFoundError("Incident not found")
        return incident

    def create_incident(self, cmd: CreateIncidentCmd) -> Incident:
        title = cmd.title.strip()
        description = cmd.description.strip()
        
        if not title:
            raise ValidationError("title cannot be empty")
        
        if not description:
            raise ValidationError("description cannot be empty")

        data = {
            "title": title,
            "description": description,
            "severity": cmd.severity,
            "status": cmd.status,
        }
        return self.uow.incidents.create(data)

    def update_incident(self, incident_id: int, cmd: UpdateIncidentCmd) -> Incident:
        existing = self.uow.incidents.get(incident_id)
        if not existing:
            raise NotFoundError("Incident not found")

        if cmd.title is not None and not cmd.title.strip():
            raise ValidationError("title cannot be empty")
        
        if cmd.description is not None and not cmd.description.strip():
            raise ValidationError("description cannot be empty")

        if cmd.status is not None:
            allowed = _ALLOWED_STATUS_TRANSITIONS.get(existing.status, {existing.status})
            if cmd.status not in allowed:
                raise ValidationError(f"invalid status transition: {existing.status} -> {cmd.status}")

        changes = {}
        if cmd.title is not None:
            changes["title"] = cmd.title.strip()
        if cmd.description is not None:
            changes["description"] = cmd.description.strip()
        if cmd.severity is not None:
            changes["severity"] = cmd.severity
        if cmd.status is not None:
            changes["status"] = cmd.status

        updated = self.uow.incidents.update(incident_id, changes)
        if not updated:
            raise NotFoundError("Incident not found")
        return updated

    def delete_incident(self, incident_id: int) -> None:
        deleted = self.uow.incidents.delete(incident_id)
        if not deleted:
            raise NotFoundError("Incident not found")

    def get_event(self, incident_id: int, event_id: int) -> TimelineEvent:
        event = self.uow.events.get(incident_id, event_id)
        if event:
            return event

        if not self.uow.incidents.exists(incident_id):
            raise NotFoundError("Incident not found")
        raise NotFoundError("Event not found")
    
    def create_event(self, incident_id: int, cmd: CreateTimelineEventCmd) -> TimelineEvent:
        if not self.uow.incidents.exists(incident_id):
            raise NotFoundError("Incident not found")

        if not cmd.event_type.strip():
            raise ValidationError("event_type cannot be empty")
        if not cmd.message.strip():
            raise ValidationError("message cannot be empty")

        data = {
            "occurred_at": cmd.occurred_at,
            "event_type": cmd.event_type.strip(),
            "message": cmd.message.strip(),
        }
        return self.uow.events.create(incident_id, data)

    def update_event(self, incident_id: int, event_id: int, cmd: UpdateTimelineEventCmd) -> TimelineEvent:
        changes = {}
        if cmd.occurred_at is not None:
            changes["occurred_at"] = cmd.occurred_at
        if cmd.event_type is not None:
            if not cmd.event_type.strip():
                raise ValidationError("event_type cannot be empty")
            changes["event_type"] = cmd.event_type.strip()
        if cmd.message is not None:
            if not cmd.message.strip():
                raise ValidationError("message cannot be empty")
            changes["message"] = cmd.message.strip()

        updated = self.uow.events.update(incident_id, event_id, changes)
        if updated:
            return updated
        
        if not self.uow.incidents.exists(incident_id):
            raise NotFoundError("Incident not found")
        raise NotFoundError("Event not found")

    def delete_event(self, incident_id: int, event_id: int) -> None:
        deleted = self.uow.events.delete(incident_id, event_id)
        if deleted:
            return

        if not self.uow.incidents.exists(incident_id):
            raise NotFoundError("Incident not found")
        raise NotFoundError("Event not found")
