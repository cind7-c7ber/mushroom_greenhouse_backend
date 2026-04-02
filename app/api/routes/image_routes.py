from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.image_metadata import ImageMetadata
from app.schemas.image import ImageMetadataResponse

router = APIRouter(prefix="/api/images", tags=["Images"])


@router.get("/latest", response_model=ImageMetadataResponse)
def get_latest_image(db: Session = Depends(get_db)):
    image = (
        db.query(ImageMetadata)
        .order_by(ImageMetadata.capture_timestamp.desc())
        .first()
    )

    if not image:
        return {
            "id": 0,
            "capture_timestamp": "2000-01-01T00:00:00",
            "section": "combined",
            "image_filename": "none.jpg",
            "storage_path": None,
            "image_url": None,
            "upload_status": "none",
            "notes": "No image uploaded yet",
            "ingested_at": "2000-01-01T00:00:00",
        }

    return image


@router.get("/history", response_model=list[ImageMetadataResponse])
def get_image_history(db: Session = Depends(get_db)):
    return (
        db.query(ImageMetadata)
        .order_by(ImageMetadata.capture_timestamp.desc())
        .limit(50)
        .all()
    )