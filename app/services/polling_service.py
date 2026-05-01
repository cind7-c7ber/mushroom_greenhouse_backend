import logging
import threading
import time

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.sync_health import record_sync_failure, record_sync_success
from app.services.telemetry_fetcher import fetch_telemetry, ingest_telemetry_payload

logger = logging.getLogger(__name__)

_polling_started = False


def polling_loop(interval_seconds: int = 30):
    while True:
        db = SessionLocal()
        try:
            payload = fetch_telemetry()
            ingest_telemetry_payload(db, payload)
            record_sync_success(settings.TELEMETRY_SOURCE_URL)
            logger.info("Polling sync succeeded")
        except Exception as e:
            db.rollback()
            record_sync_failure(settings.TELEMETRY_SOURCE_URL, str(e))
            logger.exception("Polling sync failed")
        finally:
            db.close()

        time.sleep(interval_seconds)


def start_polling(interval_seconds: int = 30):
    global _polling_started

    if _polling_started:
        return

    logger.info("Starting telemetry polling service | interval=%s seconds", interval_seconds)

    thread = threading.Thread(target=polling_loop, args=(interval_seconds,), daemon=True)
    thread.start()
    _polling_started = True