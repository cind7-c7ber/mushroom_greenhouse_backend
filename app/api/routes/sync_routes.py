from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.telemetry_fetcher import fetch_telemetry, ingest_telemetry_payload

router = APIRouter(prefix="/api/sync", tags=["Sync"])


@router.post("/telemetry")
def sync_telemetry(db: Session = Depends(get_db)):
    try:
        payload = fetch_telemetry()
        result = ingest_telemetry_payload(db, payload)
        return {
            "success": True,
            "payload": result,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/test-payload")

def sync_test_payload(db: Session = Depends(get_db)):
    sample_payload = {
        "timestamp": "2026-04-30 19:45:00.000",
        "status": "ONLINE",
        "controlled": {
            "temperature": 45.0,
            "humidity": 66.0,
            "co2": 400.0,
            "light": 99.0,
            "moisture": 89.5,
        },
        "control": {
            "temperature": 33.6,
            "humidity": 66.9,
            "co2": 400.0,
            "light": 198.5,
            "moisture": 81.5,
        },
        "latest_image": None,
        "stream": "https://greenhouse-pi.taildaad3b.ts.net/stream",
    }

    try:
        result = ingest_telemetry_payload(db, sample_payload)
        return {
            "success": True,
            "payload": result,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))