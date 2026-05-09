from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime
from database import Base

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # status_change, error, warning, maintenance
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    message = Column(Text, nullable=False)
    data = Column(Text, nullable=True)  # JSON data
    timestamp = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)  # False = non traité, True = traité
