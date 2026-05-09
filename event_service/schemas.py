from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class EventCreate(BaseModel):
    machine_id: int
    event_type: str  # status_change, error, warning, maintenance
    severity: str  # low, medium, high, critical
    message: str
    data: Optional[str] = None

class EventResponse(BaseModel):
    id: int
    machine_id: int
    event_type: str
    severity: str
    message: str
    data: Optional[Any] = None  # Accepter n'importe quel type
    timestamp: datetime
    processed: bool
    
    class Config:
        from_attributes = True
