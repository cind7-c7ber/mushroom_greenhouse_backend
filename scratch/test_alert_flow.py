import logging
from app.core.database import SessionLocal
from app.services.telemetry_fetcher import ingest_telemetry_payload
from app.models.alert_record import Alert

# Configure logging to see alert engine output
logging.basicConfig(level=logging.INFO)

db = SessionLocal()

def ingest_payload(temp, hum, name):
    payload = {
        "timestamp": "2026-05-04 15:55:00.000",
        "status": "ONLINE",
        "controlled": {
            "temperature": temp,
            "humidity": hum,
            "co2": 450.0,
            "light": 150.0,
            "moisture": 65.0,
        },
        "control": {
            "temperature": temp,
            "humidity": hum,
            "co2": 440.0,
            "light": 145.0,
            "moisture": 64.0,
        },
        "latest_image": None,
        "stream": None
    }
    print(f"\n--- Ingesting {name} payload (Temp: {temp}, Hum: {hum}) ---")
    ingest_telemetry_payload(db, payload)
    active = db.query(Alert).filter(Alert.status == 'active').all()
    print(f"Active alerts: {len(active)}")
    for a in active:
        print(f"  - {a.parameter} ({a.section}): {a.severity} | {a.band}")

try:
    # 1. Ingest Critical
    ingest_payload(45.0, 30.0, "CRITICAL")
    
    # 2. Ingest same Critical (should not create new alerts)
    ingest_payload(45.0, 30.0, "SAME CRITICAL")
    
    # 3. Ingest Watch (should resolve critical and create watch)
    ingest_payload(28.0, 75.0, "WATCH")
    
    # 4. Ingest Normal (should resolve all)
    ingest_payload(24.5, 85.0, "NORMAL")

finally:
    db.close()
