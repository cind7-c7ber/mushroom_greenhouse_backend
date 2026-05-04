from datetime import datetime

sync_health_state = {
    "source_url": None,
    "last_successful_sync": None,
    "last_failed_sync": None,
    "last_error": None,
    "status": "unknown",
}

def record_sync_success(source_url: str):
    sync_health_state["source_url"] = source_url
    sync_health_state["last_successful_sync"] = datetime.utcnow().isoformat()
    sync_health_state["last_error"] = None
    sync_health_state["status"] = "healthy"

def record_sync_failure(source_url: str, error_message: str):
    sync_health_state["source_url"] = source_url
    sync_health_state["last_failed_sync"] = datetime.utcnow().isoformat()
    sync_health_state["last_error"] = error_message
    sync_health_state["status"] = "unreachable"

def get_sync_health():
    return sync_health_state