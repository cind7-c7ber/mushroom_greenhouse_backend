from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AlertBase(BaseModel):
    timestamp: datetime
    section: str
    parameter: str
    value: float
    severity: str
    band: str
    message: str
    recommended_action: str | None = None
    status: str = "active"
    source: str | None = "http"


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)