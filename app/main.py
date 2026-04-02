from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine

from app.models.sensor_readings import SensorReading
from app.models.image_metadata import ImageMetadata
from app.models.system_status import SystemStatusLog

from app.api.routes.sensor_routes import router as sensor_router
from app.api.routes.image_routes import router as image_router
from app.api.routes.status_routes import router as status_router

from app.services.mqtt_subscriber import start_mqtt_subscriber

app = FastAPI(title="Mushroom Greenhouse Backend")

mqtt_client = None


@app.on_event("startup")
def on_startup():
    global mqtt_client
    Base.metadata.create_all(bind=engine)

    if settings.ENABLE_MQTT:
        mqtt_client = start_mqtt_subscriber()


@app.get("/")
def root():
    return {"message": "Mushroom Greenhouse Backend is running"}


app.include_router(sensor_router)
app.include_router(image_router)
app.include_router(status_router)