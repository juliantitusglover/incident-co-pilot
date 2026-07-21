from pydantic import BaseModel, Field


class HealthLiveResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    version: str = Field(..., examples=["0.6.0"])


class HealthReadyResponse(BaseModel):
    status: str = Field(..., examples=["healthy"])
    connectivity: bool
    tables_found: list[str] = Field(..., examples=[["incidents", "timeline_events"]])
    error: str | None = Field(None, examples=["Internal database connection error"])


class HealthReadyErrorResponse(BaseModel):
    detail: HealthReadyResponse
