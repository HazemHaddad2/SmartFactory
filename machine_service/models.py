from sqlalchemy import Column, Integer, String, DateTime, Float, Interval
from datetime import datetime, timedelta
from database import Base

class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="idle")  # idle, running, error, maintenance
    temperature = Column(Float, default=0.0)
    uptime = Column(Interval, default=timedelta(seconds=0))  # en interval
    last_maintenance = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)