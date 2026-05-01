from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.sensor_readings import SensorReading
from app.schemas.sensor import SensorReadingResponse

router = APIRouter(prefix="/api/sensors", tags=["Sensors"])


def serialize_sensor_reading(reading: SensorReading):
    return {
        "id": getattr(reading, "id", 0),
        "timestamp": getattr(reading, "timestamp", "2000-01-01T00:00:00"),
        "section": getattr(reading, "section", "unknown"),
        "temperature_c": getattr(reading, "temperature_c", 0.0),
        "humidity_pct": getattr(reading, "humidity_pct", 0.0),
        "co2_ppm": getattr(reading, "co2_ppm", 0.0),
        "light_lux": getattr(reading, "light_lux", 0.0),
        "moisture_pct": getattr(reading, "moisture_pct", 0.0),
        "source": getattr(reading, "source", "http"),
        "ingested_at": getattr(
            reading,
            "ingested_at",
            getattr(reading, "timestamp", "2000-01-01T00:00:00"),
        ),
    }


@router.get("/latest/{section}", response_model=SensorReadingResponse)
def get_latest_sensor_reading(section: str, db: Session = Depends(get_db)):
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.section == section)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    if not reading:
        return {
            "id": 0,
            "timestamp": "2000-01-01T00:00:00",
            "section": section,
            "temperature_c": 0.0,
            "humidity_pct": 0.0,
            "co2_ppm": 0.0,
            "light_lux": 0.0,
            "moisture_pct": 0.0,
            "source": "none",
            "ingested_at": "2000-01-01T00:00:00",
        }

    return serialize_sensor_reading(reading)


@router.get("/history/{section}", response_model=list[SensorReadingResponse])
def get_sensor_history(
    section: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.section == section)
        .order_by(SensorReading.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [serialize_sensor_reading(r) for r in readings]


@router.get("/compare", response_model=list[SensorReadingResponse])
def compare_sensor_readings(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    readings = (
        db.query(SensorReading)
        .order_by(SensorReading.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [serialize_sensor_reading(r) for r in readings]