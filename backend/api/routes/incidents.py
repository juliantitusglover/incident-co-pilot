from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies import get_incident_usecases
from backend.domain.incidents.enums import Severity, Status
from backend.schemas.error import ErrorResponse
from backend.schemas.incident import IncidentCreate, IncidentRead, IncidentListItem, IncidentUpdate
from backend.schemas.timeline_event import TimelineEventCreate, TimelineEventRead, TimelineEventUpdate
from backend.services.errors import NotFoundError, ValidationError
from backend.services.incidents.commands import CreateIncidentCmd, CreateTimelineEventCmd, UpdateIncidentCmd, UpdateTimelineEventCmd
from backend.services.incidents.usecases import IncidentUseCases

router = APIRouter(prefix="/incidents", tags=["incidents"])

INCIDENT_NOT_FOUND_RESPONSE = {
    "model": ErrorResponse,
    "description": "Incident not found",
}
EVENT_NOT_FOUND_RESPONSE = {
    "model": ErrorResponse,
    "description": "Incident or event not found",
}
SERVICE_VALIDATION_RESPONSE = {
    "model": ErrorResponse,
    "description": "Service validation error",
}

@router.get(
    "",
    response_model=List[IncidentListItem],
    summary="List incidents",
    description="List incidents, optionally filtered by status and severity.",
)
def get_all_incidents(
    status_filter: Status | None = None,
    severity_filter: Severity | None = None,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    incidents = use_case.list_incidents(status=status_filter, severity=severity_filter)
    return [IncidentListItem.model_validate(incident, from_attributes=True) for incident in incidents]

@router.get(
    "/{incident_id}",
    response_model=IncidentRead,
    summary="Get incident",
    description="Get an incident by ID, including timeline events.",
    responses={404: INCIDENT_NOT_FOUND_RESPONSE},
)
def get_incident(
    incident_id: int,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    incident = use_case.get_incident(incident_id, with_events=True)
    return IncidentRead.model_validate(incident, from_attributes=True)

@router.post(
    "",
    response_model=IncidentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create incident",
    description="Create a new incident record.",
)
def create_incident(
    incident: IncidentCreate,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    cmd = CreateIncidentCmd(**incident.model_dump())
    created_incident = use_case.create_incident(cmd)
    return IncidentRead.model_validate(created_incident, from_attributes=True)

@router.patch(
    "/{incident_id}",
    response_model=IncidentRead,
    summary="Update incident",
    description="Partially update an incident.",
    responses={
        400: SERVICE_VALIDATION_RESPONSE,
        404: INCIDENT_NOT_FOUND_RESPONSE,
    },
)
def update_incident(
    incident_id: int,
    incident_update: IncidentUpdate,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    cmd = UpdateIncidentCmd(**incident_update.model_dump(exclude_unset=True))
    updated = use_case.update_incident(incident_id, cmd)
    return IncidentRead.model_validate(updated, from_attributes=True)

@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete incident",
    description="Delete an incident and its timeline events.",
    responses={404: INCIDENT_NOT_FOUND_RESPONSE},
)
def delete_incident(
    incident_id: int,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    use_case.delete_incident(incident_id)
    return None
    

@router.post(
    "/{incident_id}/events",
    response_model=TimelineEventRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create timeline event",
    description="Add a timeline event to an incident.",
    responses={404: INCIDENT_NOT_FOUND_RESPONSE},
)
def create_timeline_event(
    incident_id: int,
    event: TimelineEventCreate,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    cmd = CreateTimelineEventCmd(**event.model_dump())
    created_event = use_case.create_event(incident_id, cmd)
    return TimelineEventRead.model_validate(created_event, from_attributes=True)

@router.patch(
    "/{incident_id}/events/{event_id}",
    response_model=TimelineEventRead,
    summary="Update timeline event",
    description="Partially update a timeline event for an incident.",
    responses={404: EVENT_NOT_FOUND_RESPONSE},
)
def update_timeline_event(
    incident_id: int,
    event_id: int,
    event_update: TimelineEventUpdate,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    cmd = UpdateTimelineEventCmd(**event_update.model_dump(exclude_unset=True))
    updated = use_case.update_event(incident_id, event_id, cmd)
    return TimelineEventRead.model_validate(updated, from_attributes=True)

@router.delete(
    "/{incident_id}/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete timeline event",
    description="Delete a timeline event from an incident.",
    responses={404: EVENT_NOT_FOUND_RESPONSE},
)
def delete_timeline_event(
    incident_id: int,
    event_id: int,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    use_case.delete_event(incident_id, event_id)
    return None
