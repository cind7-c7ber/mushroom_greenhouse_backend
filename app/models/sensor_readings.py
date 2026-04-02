from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    section = Column(String, nullable=False, index=True)  # controlled or control

    temperature_c = Column(Float, nullable=False)
    humidity_pct = Column(Float, nullable=False)
    co2_ppm = Column(Float, nullable=False)
    light_lux = Column(Float, nullable=False)
    moisture_pct = Column(Float, nullable=False)

    source = Column(String, nullable=False, default="mqtt")
    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)