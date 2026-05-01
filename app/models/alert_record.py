from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)

    section = Column(String, nullable=False, index=True)   # controlled / control
    parameter = Column(String, nullable=False, index=True) # temperature / humidity / etc.
    value = Column(Float, nullable=False)

    severity = Column(String, nullable=False, index=True)  # watch / critical
    band = Column(String, nullable=False)                  # watch_low / critical_high / etc.

    message = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=True)

    status = Column(String, nullable=False, default="active")  # active / resolved
    source = Column(String, nullable=False, default="http")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)