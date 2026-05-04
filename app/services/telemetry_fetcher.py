from datetime import datetime
from urllib.parse import urlparse
import logging

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.sensor_readings import SensorReading
from app.models.system_status import SystemStatusLog
from app.models.image_metadata import ImageMetadata
from app.services.alert_engine import evaluate_payload_alerts

logger = logging.getLogger(__name__)

REQUIRED_SENSOR_FIELDS = {"temperature", "humidity", "co2", "light", "moisture"}

def parse_datetime(timestamp_str: str) -> datetime:
    formats = [
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unsupported timestamp format: {timestamp_str}")

def validate_sensor_block(section_name: str, payload: dict):
    if not isinstance(payload, dict):
        raise ValueError(f"{section_name} must be an object")

    missing = REQUIRED_SENSOR_FIELDS - payload.keys()
    if missing:
        raise ValueError(f"{section_name} missing fields: {', '.join(sorted(missing))}")

    for field in REQUIRED_SENSOR_FIELDS:
        value = payload[field]
        if value is None:
            raise ValueError(f"{section_name}.{field} is null")
        try:
            float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{section_name}.{field} must be numeric")

def validate_payload(data: dict):
    if not isinstance(data, dict):
        raise ValueError("Telemetry payload must be a JSON object")

    for field in ["timestamp", "status", "controlled", "control"]:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    validate_sensor_block("controlled", data["controlled"])
    validate_sensor_block("control", data["control"])

    if "latest_image" in data and data["latest_image"] is not None and not isinstance(data["latest_image"], str):
        raise ValueError("latest_image must be a string if provided")

    if "stream" in data and data["stream"] is not None and not isinstance(data["stream"], str):
        raise ValueError("stream must be a string if provided")

def save_sensor_reading(db: Session, timestamp: datetime, section: str, payload: dict):
    reading = SensorReading(
        timestamp=timestamp,
        section=section,
        temperature_c=float(payload["temperature"]),
        humidity_pct=float(payload["humidity"]),
        co2_ppm=float(payload["co2"]),
        light_lux=float(payload["light"]),
        moisture_pct=float(payload["moisture"]),
        source="http",
    )
    db.add(reading)

def save_status_log(db: Session, timestamp: datetime, status_value: str):
    status = SystemStatusLog(
        timestamp=timestamp,
        status_type="system",
        status_value=status_value,
        message="Received from HTTP telemetry endpoint",
        source="http",
    )
    db.add(status)

def save_image_metadata(
    db: Session,
    timestamp: datetime,
    image_url: str | None,
    stream_url: str | None,
):
    if not image_url and not stream_url:
        return

    filename = "unknown.jpg"
    if image_url:
        parsed = urlparse(image_url)
        filename = parsed.path.split("/")[-1] if parsed.path else "unknown.jpg"

    existing = (
        db.query(ImageMetadata)
        .filter(
            ImageMetadata.capture_timestamp == timestamp,
            ImageMetadata.image_url == image_url,
            ImageMetadata.stream_url == stream_url,
        )
        .first()
    )
    if existing:
        return

    image = ImageMetadata(
        capture_timestamp=timestamp,
        section="combined",
        image_filename=filename,
        image_url=image_url,
        stream_url=stream_url,
        storage_path=None,
        upload_status="external_url",
        notes="Received from HTTP telemetry payload",
    )
    db.add(image)

def ingest_telemetry_payload(db: Session, data: dict):
    validate_payload(data)

    timestamp = parse_datetime(data["timestamp"])
    status = data.get("status", "UNKNOWN")
    controlled = data["controlled"]
    control = data["control"]
    image_url = data.get("latest_image")
    stream_url = data.get("stream")

    save_status_log(db, timestamp, status)
    save_sensor_reading(db, timestamp, "controlled", controlled)
    save_sensor_reading(db, timestamp, "control", control)
    save_image_metadata(db, timestamp, image_url, stream_url)
    
    # Evaluate alerts based on the newly saved data
    evaluate_payload_alerts(db, timestamp, controlled, control)

    db.commit()

    return {
        "message": "Telemetry ingested successfully",
        "timestamp": data["timestamp"],
        "status": status,
    }

def get_ssl_verify_value():
    if settings.TELEMETRY_CA_BUNDLE and settings.TELEMETRY_CA_BUNDLE.strip():
        return settings.TELEMETRY_CA_BUNDLE.strip(), "custom_ca_bundle"

    if settings.TELEMETRY_VERIFY_SSL:
        return True, "default_verified"

    return False, "insecure_fallback"

def fetch_telemetry():
    verify_value, verify_mode = get_ssl_verify_value()

    logger.info(
        "Fetching telemetry from %s using SSL mode: %s",
        settings.TELEMETRY_SOURCE_URL,
        verify_mode,
    )

    try:
        response = requests.get(
            settings.TELEMETRY_SOURCE_URL,
            timeout=10,
            verify=verify_value,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.SSLError as exc:
        logger.error("Telemetry fetch failed due to SSL verification issue: %s", exc)
        raise ValueError(f"Telemetry SSL verification failed: {exc}") from exc

    except requests.exceptions.Timeout as exc:
        logger.error("Telemetry fetch timed out: %s", exc)
        raise ValueError("Telemetry fetch timed out") from exc

    except requests.exceptions.RequestException as exc:
        logger.error("Telemetry fetch request failed: %s", exc)
        raise ValueError(f"Telemetry fetch failed: {exc}") from exc