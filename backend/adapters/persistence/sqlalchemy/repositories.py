from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.db.models.incident import Incident as IncidentModel
from backend.db.models.timeline_event import TimelineEvent as TimelineEventModel
from backend.domain.incidents.entities import Incident, TimelineEvent
from backend.domain.incidents.enums import Severity, Status
from backend.adapters.persistence.sqlalchemy.mappers import to_domain_incident, to_domain_event


class SqlAlchemyIncidentRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self, *, status: Status | None = None, severity: Severity | None = None) -> list[Incident]:
        stmt = select(IncidentModel)

        if status:
            stmt = stmt.where(IncidentModel.status == status)
        if severity:
            stmt = stmt.where(IncidentModel.severity == severity)

        stmt = stmt.order_by(IncidentModel.created_at.desc())
        models = self.session.execute(stmt).scalars().all()
        return [to_domain_incident(m) for m in models]

    def get(self, incident_id: int) -> Incident | None:
        stmt = select(IncidentModel).where(IncidentModel.id == incident_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        return to_domain_incident(model) if model else None

    def get_with_events(self, incident_id: int) -> Incident | None:
        stmt = (
            select(IncidentModel)
            .where(IncidentModel.id == incident_id)
            .options(selectinload(IncidentModel.events))
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        return to_domain_incident(model, includes_events=True) if model else None

    def create(self, incident_data: dict) -> Incident:
        model = IncidentModel(**incident_data)
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return to_domain_incident(model)

    def update(self, incident_id: int, changes: dict) -> Incident | None:
        stmt = select(IncidentModel).where(IncidentModel.id == incident_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None

        for key, value in changes.items():
            setattr(model, key, value)

        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return to_domain_incident(model)

    def delete(self, incident_id: int) -> bool:
        stmt = select(IncidentModel).where(IncidentModel.id == incident_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return False

        self.session.delete(model)
        self.session.flush()
        return True


class SqlAlchemyTimelineEventRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_incident_events(self, incident_id: int) -> list[TimelineEvent]:
        stmt = select(TimelineEventModel).where(
            TimelineEventModel.incident_id == incident_id,
        ).order_by(TimelineEventModel.created_at.desc())
        models = self.session.execute(stmt).scalars().all()
        return [to_domain_event(model) for model in models]
    
    def get(self, incident_id: int, event_id: int) -> TimelineEvent | None:
        stmt = select(TimelineEventModel).where(
            TimelineEventModel.id == event_id,
            TimelineEventModel.incident_id == incident_id,
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        return to_domain_event(model) if model else None

    def create(self, incident_id: int, event_data: dict) -> TimelineEvent:
        model = TimelineEventModel(**event_data, incident_id=incident_id)
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return to_domain_event(model)

    def update(self, incident_id: int, event_id: int, changes: dict) -> TimelineEvent | None:
        stmt = select(TimelineEventModel).where(
            TimelineEventModel.id == event_id,
            TimelineEventModel.incident_id == incident_id,
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None

        for key, value in changes.items():
            setattr(model, key, value)

        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        return to_domain_event(model)

    def delete(self, incident_id: int, event_id: int) -> bool:
        stmt = select(TimelineEventModel).where(
            TimelineEventModel.id == event_id,
            TimelineEventModel.incident_id == incident_id,
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return False

        self.session.delete(model)
        self.session.flush()
        return True
