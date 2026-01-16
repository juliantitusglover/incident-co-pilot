from enum import Enum
from typing import TYPE_CHECKING, List
from sqlalchemy import BigInteger, CheckConstraint, Index, String, TIMESTAMP, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.db.models.timeline_event import TimelineEvent

class Severity(str, Enum):
    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"
    SEV4 = "sev4"

class Status(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"

class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[Severity] = mapped_column(SQLEnum(Severity), nullable=False)
    status: Mapped[Status] = mapped_column(SQLEnum(Status), nullable=False, default=Status.OPEN)
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    events: Mapped[List["TimelineEvent"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="title_not_empty"),
        Index("ix_incidents_created_at", created_at.desc()),
        Index("ix_incidents_status_created_at", status, created_at),
    )
