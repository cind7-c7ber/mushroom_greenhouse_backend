from datetime import datetime
from pydantic import BaseModel


class ImageMetadataBase(BaseModel):
    capture_timestamp: datetime
    section: str = "combined"
    image_filename: str
    storage_path: str | None = None
    image_url: str | None = None
    stream_url: str | None = None
    upload_status: str = "pending"
    notes: str | None = None


class ImageMetadataCreate(ImageMetadataBase):
    pass


class ImageMetadataResponse(ImageMetadataBase):
    id: int
    ingested_at: datetime

    class Config:
        from_attributes = True