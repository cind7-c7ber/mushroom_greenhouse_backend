import requests

payload = {
    "timestamp": "2026-04-30 20:00:00.000",
    "status": "ONLINE",
    "controlled": {
        "temperature": 24.5, # Normal
        "humidity": 85.0,    # Normal
        "co2": 450.0,        # Normal
        "light": 150.0,      # Normal
        "moisture": 65.0,     # Normal
    },
    "control": {
        "temperature": 24.0, # Normal
        "humidity": 84.0,    # Normal
        "co2": 440.0,        # Normal
        "light": 145.0,      # Normal
        "moisture": 64.0,     # Normal
    },
    "latest_image": None,
    "stream": None
}

# The endpoint sync_test_payload uses a fixed sample_payload. 
# I need to call the actual sync endpoint or ingest directly.
# Let's call /api/sync/telemetry if I can mock the response, or just create a temporary route for testing.
# Better: I'll use a small python script that imports the app logic and calls it directly.

from app.core.database import SessionLocal
from app.services.telemetry_fetcher import ingest_telemetry_payload

db = SessionLocal()
try:
    ingest_telemetry_payload(db, payload)
    print("Normal payload ingested")
finally:
    db.close()
