from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.system_status import SystemStatusLog
from app.schemas.status import SystemStatusResponse

router = APIRouter(prefix="/api/status", tags=["System Status"])


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

    return status


@router.get("/history", response_model=list[SystemStatusResponse])
def get_status_history(db: Session = Depends(get_db)):
    return (
        db.query(SystemStatusLog)
        .order_by(SystemStatusLog.timestamp.desc())
        .limit(50)
        .all()
    )