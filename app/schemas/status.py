from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SystemStatusBase(BaseModel):
    timestamp: datetime
    status_type: str
    status_value: str
    message: str | None = None
    source: str | None = "http"


class SystemStatusCreate(SystemStatusBase):
    pass


class SystemStatusResponse(SystemStatusBase):
    id: int
    logged_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)