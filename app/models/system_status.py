from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class SystemStatusLog(Base):
    __tablename__ = "system_status_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)

    status_type = Column(String, nullable=False)
    status_value = Column(String, nullable=False)
    message = Column(Text, nullable=True)

    source = Column(String, nullable=False, default="http")
    logged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)