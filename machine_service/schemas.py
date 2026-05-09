from pydantic import BaseModel, field_validator
from datetime import datetime, timedelta
from typing import Optional, Union

class MachineCreate(BaseModel):
    name: str
    status: str = "idle"

class MachineUpdate(BaseModel):
    status: Optional[str] = None
    temperature: Optional[float] = None
    uptime: Optional[int] = None

class MachineResponse(BaseModel):
    id: int
    name: str
    status: str
    temperature: Optional[float] = None
    uptime: Optional[int] = None
    last_maintenance: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('uptime', mode='before')
    @classmethod
    def convert_uptime(cls, v):
        if isinstance(v, timedelta):
            return int(v.total_seconds())
        return v

    @field_validator('temperature', mode='before')
    @classmethod
    def convert_temperature(cls, v):
        if v is None:
            return None
        return float(v)

    class Config:
        from_attributes = True
