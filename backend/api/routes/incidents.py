from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.db.models.timeline_event import TimelineEvent
from backend.schemas.incident import IncidentCreate, IncidentRead, IncidentListItem, IncidentUpdate
from backend.db.models.incident import Incident, Severity, Status
from backend.db.sessions import get_db
from backend.schemas.timeline_event import TimelineEventCreate, TimelineEventRead, TimelineEventUpdate

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("", response_model=List[IncidentListItem])
def get_all_incidents(
    status: Status | None = None,
    severity: Severity | None = None,
    session: Session = Depends(get_db),
):
    query = select(Incident)

    if status:
        query = query.where(Incident.status == status)
    
    if severity:
        query = query.where(Incident.severity == severity)

    query = query.order_by(Incident.created_at.desc())

    incidents = session.execute(query).scalars().all()

    return incidents


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(
    incident_id: int,
    session: Session = Depends(get_db),
):
    query = select(Incident).where(Incident.id == incident_id).options(selectinload(Incident.events))

    incident = session.execute(query).scalar_one_or_none()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        )

    return incident

def get_incident_or_404(
    incident_id: int,
    session: Session = Depends(get_db),
):
    query = select(Incident).where(Incident.id == incident_id)

    incident = session.execute(query).scalar_one_or_none()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        )

    return incident

def get_timeline_event(
    incident_id: int,
    event_id: int,
    session: Session = Depends(get_db),
):
    get_incident_or_404(incident_id, session)
    
    query = select(TimelineEvent).where(
        TimelineEvent.id == event_id,
        TimelineEvent.incident_id == incident_id
    )

    event = session.execute(query).scalar_one_or_none()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    
    return event

@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(
    incident: IncidentCreate,
    session: Session = Depends(get_db),
):
    new_incident = Incident(**incident.model_dump())
    session.add(new_incident)
    session.commit()
    session.refresh(new_incident)
    return new_incident

@router.post("/{incident_id}/events", response_model=TimelineEventRead, status_code=status.HTTP_201_CREATED)
def create_timeline_event(
    incident_id: int,
    event: TimelineEventCreate,
    session: Session = Depends(get_db),
):
    db_incident = get_incident_or_404(incident_id, session)

    new_event = TimelineEvent(
        **event.model_dump(), 
        incident_id=db_incident.id
    )

    session.add(new_event)
    session.commit()
    session.refresh(new_event)
    
    return new_event

@router.patch("/{incident_id}", response_model=IncidentRead)
def update_incident(
    incident_id: int,
    incident_update: IncidentUpdate,
    session: Session = Depends(get_db),
):
    db_incident = get_incident_or_404(incident_id, session)

    update_data = incident_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_incident, key, value)

    session.add(db_incident)
    session.commit()
    session.refresh(db_incident)
    return db_incident

@router.patch("/{incident_id}/events/{event_id}", response_model=TimelineEventRead)
def update_timeline_event(
    incident_id: int,
    event_id: int,
    event_update: TimelineEventUpdate,
    session: Session = Depends(get_db),
):
    db_event = get_timeline_event(incident_id, event_id, session)

    update_data = event_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_event, key, value)

    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event

@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(
    incident_id: int,
    session: Session = Depends(get_db),
):
    db_incident = get_incident_or_404(incident_id, session)
    
    session.delete(db_incident)
    session.commit()
    
    return None

@router.delete("/{incident_id}/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timeline_event(
    incident_id: int,
    event_id: int,
    session: Session = Depends(get_db),
):
    db_event = get_timeline_event(incident_id, event_id, session)

    session.delete(db_event)
    session.commit()
    
    return None
