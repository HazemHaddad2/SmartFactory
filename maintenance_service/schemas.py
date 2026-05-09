from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MaintenanceTicketBase(BaseModel):
    machine_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    assigned_to: Optional[int] = None


class MaintenanceTicketCreate(MaintenanceTicketBase):
    created_by: int


class MaintenanceTicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|cancelled)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    assigned_to: Optional[int] = None


class MaintenanceTicketStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|in_progress|completed|cancelled)$")


class MaintenanceTicketAssign(BaseModel):
    assigned_to: int


class MaintenanceTicketResponse(MaintenanceTicketBase):
    id: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    machine_name: Optional[str] = None
    assigned_to_name: Optional[str] = None
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True


class MaintenanceTicketStats(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    cancelled: int
    by_priority: dict
