from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies import get_uow
from backend.adapters.persistence.sqlalchemy.uow import SqlAlchemyUnitOfWork
from backend.domain.incidents.enums import Severity, Status
from backend.schemas.incident import IncidentCreate, IncidentRead, IncidentListItem, IncidentUpdate
from backend.schemas.timeline_event import TimelineEventCreate, TimelineEventRead, TimelineEventUpdate

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _incident_or_404(uow: SqlAlchemyUnitOfWork, incident_id: int, *, with_events: bool = False):
    incident = (
        uow.incidents.get_with_events(incident_id)
        if with_events
        else uow.incidents.get(incident_id)
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


def _event_or_404(uow: SqlAlchemyUnitOfWork, incident_id: int, event_id: int):
    _incident_or_404(uow, incident_id, with_events=False)

    event = uow.events.get(incident_id, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("", response_model=List[IncidentListItem])
def get_all_incidents(
    status: Status | None = None,
    severity: Severity | None = None,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    incidents = uow.incidents.list(status=status, severity=severity)
    return [IncidentListItem.model_validate(i, from_attributes=True) for i in incidents]


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(
    incident_id: int,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    incident = _incident_or_404(uow, incident_id, with_events=True)
    return IncidentRead.model_validate(incident, from_attributes=True)


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident: IncidentCreate,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    created = uow.incidents.create(incident.model_dump())
    return IncidentRead.model_validate(created, from_attributes=True)


@router.patch("/{incident_id}", response_model=IncidentRead)
def update_incident(
    incident_id: int,
    incident_update: IncidentUpdate,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    _incident_or_404(uow, incident_id)

    update_data = incident_update.model_dump(exclude_unset=True)
    updated = uow.incidents.update(incident_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Incident not found")

    return IncidentRead.model_validate(updated, from_attributes=True)


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: int,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    deleted = uow.incidents.delete(incident_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Incident not found")
    return None


@router.post("/{incident_id}/events", response_model=TimelineEventRead, status_code=status.HTTP_201_CREATED)
def create_timeline_event(
    incident_id: int,
    event: TimelineEventCreate,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    _incident_or_404(uow, incident_id)

    created = uow.events.create(incident_id, event.model_dump())
    return TimelineEventRead.model_validate(created, from_attributes=True)


@router.patch("/{incident_id}/events/{event_id}", response_model=TimelineEventRead)
def update_timeline_event(
    incident_id: int,
    event_id: int,
    event_update: TimelineEventUpdate,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    _event_or_404(uow, incident_id, event_id)

    update_data = event_update.model_dump(exclude_unset=True)
    updated = uow.events.update(incident_id, event_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")

    return TimelineEventRead.model_validate(updated, from_attributes=True)


@router.delete("/{incident_id}/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timeline_event(
    incident_id: int,
    event_id: int,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    deleted = uow.events.delete(incident_id, event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
    return None
