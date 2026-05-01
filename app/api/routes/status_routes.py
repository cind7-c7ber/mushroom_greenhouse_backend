from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.system_status import SystemStatusLog
from app.schemas.status import SystemStatusResponse

router = APIRouter(prefix="/api/status", tags=["System Status"])


def serialize_status_log(status: SystemStatusLog):
    return {
        "id": getattr(status, "id", 0),
        "timestamp": getattr(status, "timestamp", "2000-01-01T00:00:00"),
        "status_type": getattr(status, "status_type", "system"),
        "status_value": getattr(status, "status_value", "UNKNOWN"),
        "message": getattr(status, "message", None),
        "source": getattr(status, "source", "http"),
        "logged_at": getattr(
            status,
            "logged_at",
            getattr(status, "timestamp", "2000-01-01T00:00:00"),
        ),
    }


@router.get("/latest", response_model=SystemStatusResponse)
def get_latest_status(db: Session = Depends(get_db)):
    status = (
        db.query(SystemStatusLog)
        .order_by(SystemStatusLog.timestamp.desc())
        .first()
    )

    if not status:
        return {
            "id": 0,
            "timestamp": "2000-01-01T00:00:00",
            "status_type": "system",
            "status_value": "UNKNOWN",
            "message": "No status logs available yet",
            "source": "none",
            "logged_at": "2000-01-01T00:00:00",
        }

    return serialize_status_log(status)


@router.get("/history", response_model=list[SystemStatusResponse])
def get_status_history(db: Session = Depends(get_db)):
    records = (
        db.query(SystemStatusLog)
        .order_by(SystemStatusLog.timestamp.desc())
        .limit(50)
        .all()
    )
    return [serialize_status_log(r) for r in records]