import logging

from sqlalchemy.orm import Session

from app.models.alert_record import Alert
from app.services.threshold import classify_value

logger = logging.getLogger(__name__)

RECOMMENDATIONS = {
    "temperature": "Check ventilation and fan performance.",
    "humidity": "Inspect humidification conditions and greenhouse moisture balance.",
    "co2": "Check airflow and ventilation conditions.",
    "light": "Inspect light exposure and lighting conditions.",
    "moisture": "Inspect substrate moisture and irrigation conditions.",
}


def build_alert_message(section: str, parameter: str, value: float, severity: str, unit: str) -> str:
    pretty_section = section.capitalize()
    pretty_param = parameter.upper() if parameter == "co2" else parameter.capitalize()

    if severity == "watch":
        return f"{pretty_param} in the {pretty_section} section is outside the optimal range ({value} {unit})."
    return f"{pretty_param} in the {pretty_section} section is at a critical level ({value} {unit})."


def alert_exists(db: Session, section: str, parameter: str, severity: str, band: str) -> bool:
    existing = (
        db.query(Alert)
        .filter(
            Alert.section == section,
            Alert.parameter == parameter,
            Alert.severity == severity,
            Alert.band == band,
            Alert.status == "active",
        )
        .first()
    )
    return existing is not None


def resolve_active_alerts(db: Session, section: str, parameter: str) -> int:
    active_alerts = (
        db.query(Alert)
        .filter(
            Alert.section == section,
            Alert.parameter == parameter,
            Alert.status == "active",
        )
        .all()
    )

    for alert in active_alerts:
        alert.status = "resolved"

    if active_alerts:
        logger.info(
            "Resolved %s active alert(s) | section=%s | parameter=%s",
            len(active_alerts),
            section,
            parameter,
        )

    return len(active_alerts)


def evaluate_section_alerts(db: Session, timestamp, section: str, payload: dict) -> list[Alert]:
    created_alerts = []

    for parameter in ["temperature", "humidity", "co2", "light", "moisture"]:
        value = float(payload[parameter])
        result = classify_value(parameter, value)

        if result["severity"] == "normal":
            resolve_active_alerts(db, section, parameter)
            continue

        if result["severity"] == "unknown":
            continue

        if alert_exists(
            db=db,
            section=section,
            parameter=parameter,
            severity=result["severity"],
            band=result["band"],
        ):
            continue

        alert = Alert(
            timestamp=timestamp,
            section=section,
            parameter=parameter,
            value=value,
            severity=result["severity"],
            band=result["band"],
            message=build_alert_message(
                section=section,
                parameter=parameter,
                value=value,
                severity=result["severity"],
                unit=result["unit"],
            ),
            recommended_action=RECOMMENDATIONS.get(parameter),
            status="active",
            source="http",
        )
        db.add(alert)
        created_alerts.append(alert)

        logger.info(
            "Alert created | section=%s | parameter=%s | severity=%s | band=%s | value=%s",
            section,
            parameter,
            result["severity"],
            result["band"],
            value,
        )

    return created_alerts


def evaluate_payload_alerts(db: Session, timestamp, controlled: dict, control: dict) -> list[Alert]:
    created = []
    created.extend(evaluate_section_alerts(db, timestamp, "controlled", controlled))
    created.extend(evaluate_section_alerts(db, timestamp, "control", control))
    return created