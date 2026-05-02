from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging_config import setup_logging

from app.models.sensor_readings import SensorReading
from app.models.image_metadata import ImageMetadata
from app.models.system_status import SystemStatusLog
from app.models.alert_record import Alert
from app.models.user import User

from app.api.routes.sensor_routes import router as sensor_router
from app.api.routes.image_routes import router as image_router
from app.api.routes.status_routes import router as status_router
from app.api.routes.sync_routes import router as sync_router
from app.api.routes.alert_routes import router as alert_router
from app.api.routes.auth_routes import router as auth_router

from app.services.polling_service import start_polling

setup_logging()

docs_url = "/docs" if settings.ENABLE_DOCS else None
redoc_url = "/redoc" if settings.ENABLE_DOCS else None
openapi_url = "/openapi.json" if settings.ENABLE_DOCS else None

app = FastAPI(
    title="Mushroom Greenhouse Backend",
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)

allowed_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    if settings.POLLING_ENABLED:
        start_polling(settings.POLLING_INTERVAL_SECONDS)


@app.get("/")
def root():
    return {"message": "Mushroom Greenhouse Backend is running"}


app.include_router(sensor_router)
app.include_router(image_router)
app.include_router(status_router)
app.include_router(sync_router)
app.include_router(alert_router)
app.include_router(auth_router)