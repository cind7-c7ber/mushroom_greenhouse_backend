from fastapi import FastAPI

from app.core.database import Base, engine

from app.models.sensor_readings import SensorReading
from app.models.image_metadata import ImageMetadata
from app.models.system_status import SystemStatusLog

from app.api.routes.sensor_routes import router as sensor_router
from app.api.routes.image_routes import router as image_router
from app.api.routes.status_routes import router as status_router
from app.api.routes.sync_routes import router as sync_router
from app.models.alert_record import Alert
from app.api.routes.alert_routes import router as alert_router

app = FastAPI(title="Mushroom Greenhouse Backend")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Mushroom Greenhouse Backend is running"}


app.include_router(sensor_router)
app.include_router(image_router)
app.include_router(status_router)
app.include_router(sync_router)
app.include_router(alert_router)