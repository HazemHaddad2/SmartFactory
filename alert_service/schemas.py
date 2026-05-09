from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertCreate(BaseModel):
    event_id: Optional[int] = 0
    machine_id: int
    alert_type: str
    severity: str
    title: str
    message: str

class AlertResponse(BaseModel):
    id: int
    event_id: int
    machine_id: int
    alert_type: str
    severity: str
    title: str
    message: str
    status: str
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class AlertUpdate(BaseModel):
    status: str  # acknowledged, resolved
