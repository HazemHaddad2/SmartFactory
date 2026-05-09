from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, nullable=True, index=True, default=0)
    machine_id = Column(Integer, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # error, warning, critical, failure, temperature
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="active")  # active, acknowledged, resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
