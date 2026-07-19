from fastapi import APIRouter, Depends, Query, Response, status

from backend.api.dependencies import get_incident_usecases, require_api_key
from backend.domain.incidents.enums import Severity, Status
from backend.schemas.error import ErrorResponse
from backend.schemas.incident import (
    IncidentCreate,
    IncidentListItem,
    IncidentListResponse,
    IncidentReportResponse,
    IncidentRead,
    IncidentUpdate,
)
from backend.schemas.timeline_event import (
    TimelineEventCreate,
    TimelineEventListResponse,
    TimelineEventRead,
    TimelineEventUpdate,
)
from backend.services.errors import NotFoundError, ValidationError
from backend.services.incidents.commands import CreateIncidentCmd, CreateTimelineEventCmd, UpdateIncidentCmd, UpdateTimelineEventCmd
from backend.services.incidents.report_markdown import render_incident_report_markdown
from backend.services.incidents.usecases import IncidentUseCases

router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
    dependencies=[Depends(require_api_key)],
)

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
API_KEY_AUTH_RESPONSE = {
    "model": ErrorResponse,
    "description": "Invalid or missing API key",
    "content": {
        "application/json": {
            "example": {"detail": "Invalid or missing API key"},
        }
    },
}
INCIDENT_LIST_RESPONSE_EXAMPLE = {
    "items": [
        {
            "id": 1,
            "title": "Database Outage",
            "status": "investigating",
            "severity": "sev1",
            "created_at": "2026-06-28T13:45:35.344353+01:00",
            "updated_at": "2026-06-28T13:45:35.344353+01:00",
        }
    ],
    "limit": 50,
    "offset": 0,
    "total": 1,
}
TIMELINE_EVENT_LIST_RESPONSE_EXAMPLE = {
    "items": [
        {
            "id": 2,
            "incident_id": 1,
            "occurred_at": "2026-07-11T12:00:00Z",
            "event_type": "update",
            "message": "Investigating database latency.",
            "created_at": "2026-07-11T12:05:00Z",
            "updated_at": "2026-07-11T12:05:00Z",
        }
    ],
    "limit": 50,
    "offset": 0,
    "total": 1,
}
INCIDENT_REPORT_RESPONSE_EXAMPLE = {
    "incident": {
        "id": 1,
        "title": "Database Outage",
        "description": "Production database is unavailable.",
        "status": "investigating",
        "severity": "sev1",
        "created_at": "2026-01-23T12:00:00Z",
        "updated_at": "2026-01-23T12:05:00Z",
    },
    "timeline_events": [
        {
            "id": 2,
            "incident_id": 1,
            "occurred_at": "2026-01-23T12:01:00Z",
            "event_type": "update",
            "message": "Restarting the primary node.",
            "created_at": "2026-01-23T12:02:00Z",
            "updated_at": "2026-01-23T12:02:00Z",
        }
    ],
    "timeline_order": "created_at_desc_id_desc",
    "timeline_event_count": 1,
}
INCIDENT_REPORT_MARKDOWN_EXAMPLE = """# Incident Report: Database Outage

## Incident

- ID: 1
- Severity: sev1
- Status: investigating
- Created at: 2026-01-23T12:00:00Z
- Updated at: 2026-01-23T12:05:00Z
- Description: Production database is unavailable.

## Timeline

Timeline order: created_at_desc_id_desc
Timeline event count: 1

### Event 2

- Event type: update
- Occurred at: 2026-01-23T12:01:00Z
- Created at: 2026-01-23T12:02:00Z
- Updated at: 2026-01-23T12:02:00Z

Restarting the primary node.
"""

@router.get(
    "",
    response_model=IncidentListResponse,
    summary="List incidents",
    description=(
        "List paginated incident summaries, optionally filtered by status and "
        "severity. Results are ordered newest first by created_at DESC, id DESC. "
        "The response envelope contains items, limit, offset, and total."
    ),
    responses={
        200: {
            "description": "Paginated incident list response",
            "content": {
                "application/json": {
                    "example": INCIDENT_LIST_RESPONSE_EXAMPLE,
                }
            },
        },
        401: API_KEY_AUTH_RESPONSE,
    },
)
def get_all_incidents(
    status_filter: Status | None = Query(
        default=None,
        description="Filter incidents by status.",
        examples=["open"],
    ),
    severity_filter: Severity | None = Query(
        default=None,
        description="Filter incidents by severity.",
        examples=["sev1"],
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of incidents to return.",
        examples=[25],
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of matching incidents to skip.",
        examples=[0],
    ),
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    incidents, total = use_case.list_incidents(
        status=status_filter,
        severity=severity_filter,
        limit=limit,
        offset=offset,
    )
    items = [
        IncidentListItem.model_validate(incident, from_attributes=True)
        for incident in incidents
    ]
    return IncidentListResponse(
        items=items,
        limit=limit,
        offset=offset,
        total=total,
    )

@router.get(
    "/{incident_id}/report",
    response_model=IncidentReportResponse,
    summary="Get incident report",
    description=(
        "Get a deterministic, non-AI structured incident report with incident "
        "fields and timeline events. The report does not include a generated "
        "summary. Timeline events are ordered by created_at DESC, then id DESC, "
        "and the response includes timeline_order and timeline_event_count."
    ),
    responses={
        200: {
            "description": "Deterministic structured incident report.",
            "content": {
                "application/json": {
                    "example": INCIDENT_REPORT_RESPONSE_EXAMPLE,
                }
            },
        },
        401: API_KEY_AUTH_RESPONSE,
        404: INCIDENT_NOT_FOUND_RESPONSE,
    },
)
def get_incident_report(
    incident_id: int,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    incident = use_case.get_incident_report(incident_id)
    return IncidentReportResponse(
        incident=incident,
        timeline_events=incident.events,
        timeline_event_count=len(incident.events),
    )

@router.get(
    "/{incident_id}/report/markdown",
    response_class=Response,
    summary="Get incident report as Markdown",
    description=(
        "Get a deterministic, non-AI Markdown incident report with incident "
        "fields and timeline events. The export does not include a generated "
        "summary. It preserves report timeline ordering and includes "
        "timeline_order and timeline_event_count."
    ),
    responses={
        200: {
            "description": "Markdown incident report",
            "content": {
                "text/markdown": {
                    "schema": {"type": "string"},
                    "example": INCIDENT_REPORT_MARKDOWN_EXAMPLE,
                }
            },
        },
        401: API_KEY_AUTH_RESPONSE,
        404: INCIDENT_NOT_FOUND_RESPONSE,
    },
)
def get_incident_report_markdown(
    incident_id: int,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    incident = use_case.get_incident_report(incident_id)
    markdown = render_incident_report_markdown(incident)
    return Response(content=markdown, media_type="text/markdown")

@router.get(
    "/{incident_id}",
    response_model=IncidentRead,
    summary="Get incident",
    description="Get an incident by ID, including timeline events.",
    responses={
        401: API_KEY_AUTH_RESPONSE,
        404: INCIDENT_NOT_FOUND_RESPONSE,
    },
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
    responses={401: API_KEY_AUTH_RESPONSE},
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
        401: API_KEY_AUTH_RESPONSE,
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
    responses={
        401: API_KEY_AUTH_RESPONSE,
        404: INCIDENT_NOT_FOUND_RESPONSE,
    },
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
    responses={
        401: API_KEY_AUTH_RESPONSE,
        404: INCIDENT_NOT_FOUND_RESPONSE,
    },
)
def create_timeline_event(
    incident_id: int,
    event: TimelineEventCreate,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    cmd = CreateTimelineEventCmd(**event.model_dump())
    created_event = use_case.create_event(incident_id, cmd)
    return TimelineEventRead.model_validate(created_event, from_attributes=True)

@router.get(
    "/{incident_id}/events",
    response_model=TimelineEventListResponse,
    summary="List timeline events",
    description=(
        "List timeline events for an incident in a paginated envelope. Results "
        "are ordered newest first by created_at DESC, id DESC."
    ),
    responses={
        200: {
            "description": "Paginated timeline event list response",
            "content": {
                "application/json": {
                    "example": TIMELINE_EVENT_LIST_RESPONSE_EXAMPLE,
                }
            },
        },
        401: API_KEY_AUTH_RESPONSE,
        404: INCIDENT_NOT_FOUND_RESPONSE,
    },
)
def list_timeline_events(
    incident_id: int,
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of timeline events to return.",
        examples=[25],
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of matching timeline events to skip.",
        examples=[0],
    ),
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    events, total = use_case.list_events(incident_id, limit=limit, offset=offset)
    items = [
        TimelineEventRead.model_validate(event, from_attributes=True)
        for event in events
    ]
    return TimelineEventListResponse(
        items=items,
        limit=limit,
        offset=offset,
        total=total,
    )

@router.get(
    "/{incident_id}/events/{event_id}",
    response_model=TimelineEventRead,
    summary="Get timeline event",
    description="Get one timeline event scoped to an incident.",
    responses={
        401: API_KEY_AUTH_RESPONSE,
        404: EVENT_NOT_FOUND_RESPONSE,
    },
)
def get_timeline_event(
    incident_id: int,
    event_id: int,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    event = use_case.get_event(incident_id, event_id)
    return TimelineEventRead.model_validate(event, from_attributes=True)

@router.patch(
    "/{incident_id}/events/{event_id}",
    response_model=TimelineEventRead,
    summary="Update timeline event",
    description="Partially update a timeline event for an incident.",
    responses={
        401: API_KEY_AUTH_RESPONSE,
        404: EVENT_NOT_FOUND_RESPONSE,
    },
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
    responses={
        401: API_KEY_AUTH_RESPONSE,
        404: EVENT_NOT_FOUND_RESPONSE,
    },
)
def delete_timeline_event(
    incident_id: int,
    event_id: int,
    use_case: IncidentUseCases = Depends(get_incident_usecases),
):
    use_case.delete_event(incident_id, event_id)
    return None
