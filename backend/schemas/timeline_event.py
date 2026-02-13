from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class TimelineEventBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )

    occurred_at: datetime = Field(
        ...,
        description="The ISO-8601 timestamp when the event actually took place.",
        examples=["2026-01-23T12:00:00Z"]
    )
    event_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="The category of the event (e.g., 'note', 'status_change', 'system_log').",
        examples=["note"]
    )
    message: str = Field(
        ...,
        min_length=3,
        max_length=5000,
        description="A detailed description of the event or update.",
        examples=["Investigation started: identified a memory leak in the auth service."]
    )

class TimelineEventCreate(TimelineEventBase):
    """Schema for adding a new event to an incident's timeline."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

class TimelineEventRead(TimelineEventBase):
    """Full detail of a timeline event as stored in the database."""
    id: int = Field(..., description="Unique identifier for this specific event.")
    incident_id: int = Field(..., description="The ID of the incident this event belongs to.")
    created_at: datetime = Field(..., description="System timestamp when this record was created.")
    updated_at: datetime = Field(..., description="System timestamp when this record was last updated.")

class TimelineEventUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    occurred_at: Optional[datetime] = Field(
        None,
        description="The ISO-8601 timestamp when the event actually took place.",
        examples=["2026-01-23T12:00:00Z"]
    )
    event_type: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="The category of the event (e.g., 'note', 'status_change', 'system_log').",
        examples=["note"]
    )
    message: Optional[str] = Field(
        None,
        min_length=3,
        max_length=5000,
        description="A detailed description of the event or update.",
        examples=["Investigation started: identified a memory leak in the auth service."]
    )