from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import TIMESTAMP, BigInteger, CheckConstraint, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base

if TYPE_CHECKING:
    from backend.db.models.incident import Incident

class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False
    )
    occurred_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(5000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    incident: Mapped["Incident"] = relationship(back_populates="events")

    __table_args__ = (
        CheckConstraint("length(trim(event_type)) > 0", name="event_type_not_empty"),
        CheckConstraint("length(trim(message)) > 0", name="message_not_empty"),
        Index("ix_timeline_incident_occurred", incident_id, occurred_at),
    )