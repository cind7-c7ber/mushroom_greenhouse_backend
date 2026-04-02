from datetime import datetime
from pydantic import BaseModel


class SystemStatusBase(BaseModel):
    timestamp: datetime
    status_type: str
    status_value: str
    message: str | None = None
    source: str = "mqtt"


class SystemStatusCreate(SystemStatusBase):
    pass


class SystemStatusResponse(SystemStatusBase):
    id: int
    logged_at: datetime

    class Config:
        from_attributes = True