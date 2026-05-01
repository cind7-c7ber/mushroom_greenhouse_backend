from datetime import datetime
from urllib.parse import urlparse

import requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.sensor_readings import SensorReading
from app.models.system_status import SystemStatusLog
from app.models.image_metadata import ImageMetadata
from app.services.alert_engine import evaluate_payload_alerts


REQUIRED_SENSOR_FIELDS = {"temperature", "humidity", "co2", "light", "moisture"}

VALID_SENSOR_RANGES = {
    "temperature": (-10.0, 60.0),
    "humidity": (0.0, 100.0),
    "co2": (0.0, 10000.0),
    "light": (0.0, 200000.0),
    "moisture": (0.0, 100.0),
}


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
            numeric_value = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{section_name}.{field} must be numeric")

        min_value, max_value = VALID_SENSOR_RANGES[field]
        if not (min_value <= numeric_value <= max_value):
            raise ValueError(
                f"{section_name}.{field} out of valid range: {numeric_value} "
                f"(expected {min_value} to {max_value})"
            )


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

    latest_record = (
        db.query(ImageMetadata)
        .order_by(ImageMetadata.capture_timestamp.desc(), ImageMetadata.id.desc())
        .first()
    )

    if latest_record:
        same_image = latest_record.image_url == image_url
        same_stream = latest_record.stream_url == stream_url
        same_filename = latest_record.image_filename == filename

        if same_image and same_stream and same_filename:
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

    created_alerts = evaluate_payload_alerts(db, timestamp, controlled, control)

    db.commit()

    return {
        "message": "Telemetry ingested successfully",
        "timestamp": data["timestamp"],
        "status": status,
        "alerts_created": len(created_alerts),
    }


def fetch_telemetry():
    response = requests.get(
        settings.TELEMETRY_SOURCE_URL,
        timeout=10,
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    return response.json()