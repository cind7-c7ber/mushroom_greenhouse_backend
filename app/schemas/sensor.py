from datetime import datetime
from pydantic import BaseModel


class SensorReadingBase(BaseModel):
    timestamp: datetime
    section: str
    temperature_c: float
    humidity_pct: float
    co2_ppm: float
    light_lux: float
    moisture_pct: float
    source: str = "mqtt"


class SensorReadingCreate(SensorReadingBase):
    pass


class SensorReadingResponse(SensorReadingBase):
    id: int
    ingested_at: datetime

    class Config:
        from_attributes = True