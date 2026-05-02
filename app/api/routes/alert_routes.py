from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies.security_dependencies import get_current_user
from app.core.database import get_db
from app.models.alert_record import Alert
from app.models.user import User
from app.schemas.alert_schema import AlertResponse

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


def serialize_alert(alert: Alert):
    return {
        "id": alert.id,
        "timestamp": alert.timestamp,
        "section": alert.section,
        "parameter": alert.parameter,
        "value": alert.value,
        "severity": alert.severity,
        "band": alert.band,
        "message": alert.message,
        "recommended_action": alert.recommended_action,
        "status": alert.status,
        "source": alert.source,
        "created_at": alert.created_at,
    }


@router.get("/latest", response_model=list[AlertResponse])
def get_latest_alerts(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alerts = (
        db.query(Alert)
        .order_by(Alert.timestamp.desc(), Alert.id.desc())
        .limit(limit)
        .all()
    )
    return [serialize_alert(a) for a in alerts]


@router.get("/history", response_model=list[AlertResponse])
def get_alert_history(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alerts = (
        db.query(Alert)
        .order_by(Alert.timestamp.desc(), Alert.id.desc())
        .limit(limit)
        .all()
    )
    return [serialize_alert(a) for a in alerts]


@router.get("/active", response_model=list[AlertResponse])
def get_active_alerts(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alerts = (
        db.query(Alert)
        .filter(Alert.status == "active")
        .order_by(Alert.timestamp.desc(), Alert.id.desc())
        .limit(limit)
        .all()
    )
    return [serialize_alert(a) for a in alerts]


@router.get("/summary")
def get_alert_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    active_total = db.query(func.count(Alert.id)).filter(Alert.status == "active").scalar() or 0
    critical_total = (
        db.query(func.count(Alert.id))
        .filter(Alert.status == "active", Alert.severity == "critical")
        .scalar()
        or 0
    )
    watch_total = (
        db.query(func.count(Alert.id))
        .filter(Alert.status == "active", Alert.severity == "watch")
        .scalar()
        or 0
    )

    latest_timestamp = (
        db.query(Alert.timestamp)
        .order_by(Alert.timestamp.desc(), Alert.id.desc())
        .limit(1)
        .scalar()
    )

    return {
        "active_total": active_total,
        "critical_total": critical_total,
        "watch_total": watch_total,
        "latest_timestamp": latest_timestamp,
    }