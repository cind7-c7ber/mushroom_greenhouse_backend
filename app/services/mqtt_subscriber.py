import json
from datetime import datetime
from urllib.parse import urlparse

import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.sensor_readings import SensorReading
from app.models.system_status import SystemStatusLog
from app.models.image_metadata import ImageMetadata


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


def save_sensor_reading(db: Session, timestamp: datetime, section: str, payload: dict):
    reading = SensorReading(
        timestamp=timestamp,
        section=section,
        temperature_c=float(payload["temperature"]),
        humidity_pct=float(payload["humidity"]),
        co2_ppm=float(payload["co2"]),
        light_lux=float(payload["light"]),
        moisture_pct=float(payload["moisture"]),
        source="mqtt",
    )
    db.add(reading)


def save_status_log(db: Session, timestamp: datetime, status_value: str):
    status = SystemStatusLog(
        timestamp=timestamp,
        status_type="system",
        status_value=status_value,
        message="Received from MQTT JSON payload",
        source="mqtt",
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

    image = ImageMetadata(
        capture_timestamp=timestamp,
        section="combined",
        image_filename=filename,
        image_url=image_url,
        stream_url=stream_url,
        storage_path=None,
        upload_status="external_url",
        notes="Received from MQTT payload",
    )
    db.add(image)


def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")
    for topic in settings.MQTT_TOPICS:
        client.subscribe(topic)
        print(f"[MQTT] Subscribed to {topic}")


def on_message(client, userdata, msg):
    topic = msg.topic
    raw_payload = msg.payload.decode()
    print(f"[MQTT] Received {topic} -> {raw_payload}")

    db = SessionLocal()

    try:
        data = json.loads(raw_payload)

        timestamp = parse_datetime(data["timestamp"])
        status = data.get("status", "UNKNOWN")
        controlled = data.get("controlled", {})
        control = data.get("control", {})
        image_url = data.get("image")
        stream_url = data.get("stream")

        save_status_log(db, timestamp, status)

        if controlled:
            save_sensor_reading(db, timestamp, "controlled", controlled)

        if control:
            save_sensor_reading(db, timestamp, "control", control)

        save_image_metadata(db, timestamp, image_url, stream_url)

        db.commit()
        print(f"[DB] Saved MQTT payload for timestamp {data['timestamp']}")

    except Exception as e:
        db.rollback()
        print(f"[MQTT ERROR] {e}")

    finally:
        db.close()


def start_mqtt_subscriber():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, settings.MQTT_KEEPALIVE)
    client.loop_start()

    return client