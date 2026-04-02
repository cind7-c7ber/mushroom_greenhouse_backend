from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class ImageMetadata(Base):
    __tablename__ = "image_metadata"

    id = Column(Integer, primary_key=True, index=True)
    capture_timestamp = Column(DateTime, nullable=False, index=True)
    section = Column(String, nullable=False, default="combined")

    image_filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=True)
    image_url = Column(Text, nullable=True)
    stream_url = Column(Text, nullable=True)

    upload_status = Column(String, nullable=False, default="pending")
    notes = Column(Text, nullable=True)

    ingested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)