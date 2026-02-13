from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from backend.domain.incidents.enums import Status, Severity

from backend.schemas.timeline_event import TimelineEventRead

class IncidentBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )

    title: str = Field(
        ...,
        min_length=1, 
        max_length=255, 
        description="A concise, high-level summary of the incident.",
        examples=["Database connection timeouts in US-EAST-1"]
    )
    description: str = Field(
        ...,
        min_length=1, 
        max_length=2000,
        description="Detailed context regarding the incident, including symptoms and initial impact.",
        examples=["All API requests are failing with 504 Gateway Timeout. Affecting approximately 15% of users."]
    )
    status: Status = Field(
        default=Status.OPEN,
        description="The current lifecycle state of the incident.",
        examples=[Status.OPEN]
    )
    severity: Severity = Field(
        default=Severity.SEV1,
        description="The impact classification based on business criticality.",
        examples=[Severity.SEV1]
    )

class IncidentCreate(IncidentBase):
    """Schema for creating a new incident."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

class IncidentListItem(BaseModel):
    """Simplified schema for dashboard lists (excludes timeline events for performance)."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique internal database identifier.")
    title: str = Field(
        ...,
        min_length=1, 
        max_length=255, 
        description="A concise, high-level summary of the incident.",
        examples=["Database connection timeouts in US-EAST-1"]
    )
    status: Status = Field(
        ...,
        description="The current lifecycle state of the incident.",
        examples=[Status.OPEN]
    )
    severity: Severity = Field(
        ...,
        description="The impact classification based on business criticality.",
        examples=[Severity.SEV1]
    )
    created_at: datetime = Field(..., description="ISO-8601 timestamp of record creation.")
    updated_at: datetime = Field(..., description="ISO-8601 timestamp of the last modification.")

class IncidentRead(IncidentBase):
    """Full detail view of an incident, including system-generated fields and timeline."""
    id: int = Field(..., description="Unique internal database identifier.")
    created_at: datetime = Field(..., description="ISO-8601 timestamp of record creation.")
    updated_at: datetime = Field(..., description="ISO-8601 timestamp of the last modification.")
    events: list[TimelineEventRead] = Field(
        default_factory=list, 
        description="Chronological list of all events associated with this incident."
    )

class IncidentUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    title: Optional[str] = Field(
        None,
        min_length=1, 
        max_length=255, 
        description="A concise, high-level summary of the incident.",
        examples=["Database connection timeouts in US-EAST-1"]
    )
    description: Optional[str] = Field(
        None,
        min_length=1, 
        max_length=2000,
        description="Detailed context regarding the incident, including symptoms and initial impact.",
        examples=["All API requests are failing with 504 Gateway Timeout. Affecting approximately 15% of users."]
    )
    status: Optional[Status] = Field(
        None,
        description="The current lifecycle state of the incident.",
        examples=[Status.OPEN]
    )
    severity: Optional[Severity] = Field(
        None,
        description="The impact classification based on business criticality.",
        examples=[Severity.SEV1]
    )
