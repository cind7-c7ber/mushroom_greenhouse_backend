from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SensorReadingBase(BaseModel):
    timestamp: datetime
    section: str
    temperature_c: float
    humidity_pct: float
    co2_ppm: float
    light_lux: float
    moisture_pct: float
    source: str | None = "http"


class SensorReadingCreate(SensorReadingBase):
    pass


class SensorReadingResponse(SensorReadingBase):
    id: int
    ingested_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)