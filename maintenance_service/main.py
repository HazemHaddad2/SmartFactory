from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import httpx

from database import get_db, init_db
from models import MaintenanceTicket
from schemas import (
    MaintenanceTicketCreate,
    MaintenanceTicketUpdate,
    MaintenanceTicketResponse,
    MaintenanceTicketStatusUpdate,
    MaintenanceTicketAssign,
    MaintenanceTicketStats
)

app = FastAPI(title="SmartFactory Maintenance Service")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs des autres services
MACHINE_SERVICE_URL = "http://machine-service:8002"
USER_SERVICE_URL = "http://user-service:8001"
EVENT_SERVICE_URL = "http://event-service:8003"


@app.on_event("startup")
def startup_event():
    init_db()


# Helper functions
async def get_machine_name(machine_id: int) -> Optional[str]:
    """Récupère le nom de la machine depuis le service machine"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{MACHINE_SERVICE_URL}/machines/{machine_id}")
            if response.status_code == 200:
                return response.json().get("name")
    except Exception as e:
        print(f"Warning: Could not get machine name: {e}")
    return None


async def get_user_name(user_id: int) -> Optional[str]:
    """Récupère le nom de l'utilisateur depuis le service user"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
            if response.status_code == 200:
                return response.json().get("username")
    except Exception as e:
        print(f"Warning: Could not get user name: {e}")
    return None


async def create_event(event_type: str, machine_id: int, description: str, severity: str = "info"):
    """Crée un événement dans le service event"""
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(
                f"{EVENT_SERVICE_URL}/events/",
                json={
                    "machine_id": machine_id,
                    "event_type": event_type,
                    "message": description,
                    "severity": severity
                }
            )
    except Exception as e:
        print(f"Warning: Could not create event: {e}")


async def enrich_ticket(ticket: MaintenanceTicket) -> MaintenanceTicketResponse:
    """Enrichit un ticket avec les noms de machine et utilisateurs"""
    machine_name = None
    assigned_to_name = None
    created_by_name = None
    
    try:
        machine_name = await get_machine_name(ticket.machine_id)
    except Exception:
        pass
    
    try:
        if ticket.assigned_to:
            assigned_to_name = await get_user_name(ticket.assigned_to)
    except Exception:
        pass
    
    try:
        created_by_name = await get_user_name(ticket.created_by)
    except Exception:
        pass
    
    return MaintenanceTicketResponse(
        id=ticket.id,
        machine_id=ticket.machine_id,
        title=ticket.title,
        description=ticket.description,
        status=ticket.status,
        priority=ticket.priority,
        assigned_to=ticket.assigned_to,
        created_by=ticket.created_by,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        completed_at=ticket.completed_at,
        machine_name=machine_name,
        assigned_to_name=assigned_to_name,
        created_by_name=created_by_name
    )


# Routes
@app.get("/")
def read_root():
    return {"service": "SmartFactory Maintenance Service", "status": "running"}


@app.post("/api/tickets", response_model=MaintenanceTicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(ticket: MaintenanceTicketCreate, db: Session = Depends(get_db)):
    """Créer un nouveau ticket de maintenance"""
    try:
        db_ticket = MaintenanceTicket(**ticket.dict())
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        
        # Créer un événement (ne pas bloquer si ça échoue)
        try:
            await create_event(
                "maintenance_ticket_created",
                ticket.machine_id,
                f"Ticket créé: {ticket.title}",
                "warning" if ticket.priority in ["high", "urgent"] else "info"
            )
        except Exception as e:
            print(f"Warning: Could not create event: {e}")
        
        return await enrich_ticket(db_ticket)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/tickets", response_model=List[MaintenanceTicketResponse])
async def get_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    machine_id: Optional[int] = None,
    assigned_to: Optional[int] = None,
    created_by: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Récupérer la liste des tickets avec filtres optionnels"""
    query = db.query(MaintenanceTicket)
    
    if status:
        query = query.filter(MaintenanceTicket.status == status)
    if priority:
        query = query.filter(MaintenanceTicket.priority == priority)
    if machine_id:
        query = query.filter(MaintenanceTicket.machine_id == machine_id)
    if assigned_to:
        query = query.filter(MaintenanceTicket.assigned_to == assigned_to)
    if created_by:
        query = query.filter(MaintenanceTicket.created_by == created_by)
    
    tickets = query.order_by(MaintenanceTicket.created_at.desc()).offset(skip).limit(limit).all()
    
    # Enrichir tous les tickets
    enriched_tickets = []
    for ticket in tickets:
        enriched_tickets.append(await enrich_ticket(ticket))
    
    return enriched_tickets


@app.get("/api/tickets/{ticket_id}", response_model=MaintenanceTicketResponse)
async def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Récupérer un ticket spécifique"""
    ticket = db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return await enrich_ticket(ticket)


@app.put("/api/tickets/{ticket_id}", response_model=MaintenanceTicketResponse)
async def update_ticket(ticket_id: int, ticket_update: MaintenanceTicketUpdate, db: Session = Depends(get_db)):
    """Mettre à jour un ticket"""
    ticket = db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    update_data = ticket_update.dict(exclude_unset=True)
    
    # Si le statut passe à completed, enregistrer la date
    if "status" in update_data and update_data["status"] == "completed":
        update_data["completed_at"] = datetime.now()
    
    for key, value in update_data.items():
        setattr(ticket, key, value)
    
    db.commit()
    db.refresh(ticket)
    
    # Créer un événement
    await create_event(
        "maintenance_ticket_updated",
        ticket.machine_id,
        f"Ticket mis à jour: {ticket.title}",
        "info"
    )
    
    return await enrich_ticket(ticket)


@app.patch("/api/tickets/{ticket_id}/status", response_model=MaintenanceTicketResponse)
async def update_ticket_status(ticket_id: int, status_update: MaintenanceTicketStatusUpdate, db: Session = Depends(get_db)):
    """Mettre à jour uniquement le statut d'un ticket"""
    ticket = db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    old_status = ticket.status
    ticket.status = status_update.status
    
    # Si le statut passe à completed, enregistrer la date
    if status_update.status == "completed":
        ticket.completed_at = datetime.now()
    
    db.commit()
    db.refresh(ticket)
    
    # Créer un événement
    await create_event(
        "maintenance_ticket_status_changed",
        ticket.machine_id,
        f"Ticket {ticket.title}: {old_status} → {status_update.status}",
        "info"
    )
    
    return await enrich_ticket(ticket)


@app.patch("/api/tickets/{ticket_id}/assign", response_model=MaintenanceTicketResponse)
async def assign_ticket(ticket_id: int, assign_data: MaintenanceTicketAssign, db: Session = Depends(get_db)):
    """Assigner un ticket à un technicien"""
    ticket = db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.assigned_to = assign_data.assigned_to
    
    # Si le ticket était en attente, le passer en cours
    if ticket.status == "pending":
        ticket.status = "in_progress"
    
    db.commit()
    db.refresh(ticket)
    
    # Créer un événement
    user_name = await get_user_name(assign_data.assigned_to)
    await create_event(
        "maintenance_ticket_assigned",
        ticket.machine_id,
        f"Ticket {ticket.title} assigné à {user_name or 'technicien'}",
        "info"
    )
    
    return await enrich_ticket(ticket)


@app.delete("/api/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Supprimer un ticket"""
    ticket = db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    machine_id = ticket.machine_id
    title = ticket.title
    
    db.delete(ticket)
    db.commit()
    
    # Créer un événement
    await create_event(
        "maintenance_ticket_deleted",
        machine_id,
        f"Ticket supprimé: {title}",
        "info"
    )
    
    return None


@app.get("/api/tickets/machine/{machine_id}", response_model=List[MaintenanceTicketResponse])
async def get_tickets_by_machine(machine_id: int, db: Session = Depends(get_db)):
    """Récupérer tous les tickets d'une machine"""
    tickets = db.query(MaintenanceTicket).filter(
        MaintenanceTicket.machine_id == machine_id
    ).order_by(MaintenanceTicket.created_at.desc()).all()
    
    enriched_tickets = []
    for ticket in tickets:
        enriched_tickets.append(await enrich_ticket(ticket))
    
    return enriched_tickets


@app.get("/api/tickets/user/{user_id}", response_model=List[MaintenanceTicketResponse])
async def get_tickets_by_user(user_id: int, db: Session = Depends(get_db)):
    """Récupérer tous les tickets assignés à un utilisateur"""
    tickets = db.query(MaintenanceTicket).filter(
        MaintenanceTicket.assigned_to == user_id
    ).order_by(MaintenanceTicket.created_at.desc()).all()
    
    enriched_tickets = []
    for ticket in tickets:
        enriched_tickets.append(await enrich_ticket(ticket))
    
    return enriched_tickets


@app.get("/api/tickets/stats", response_model=MaintenanceTicketStats)
def get_tickets_stats(db: Session = Depends(get_db)):
    """Récupérer les statistiques des tickets"""
    total = db.query(MaintenanceTicket).count()
    pending = db.query(MaintenanceTicket).filter(MaintenanceTicket.status == "pending").count()
    in_progress = db.query(MaintenanceTicket).filter(MaintenanceTicket.status == "in_progress").count()
    completed = db.query(MaintenanceTicket).filter(MaintenanceTicket.status == "completed").count()
    cancelled = db.query(MaintenanceTicket).filter(MaintenanceTicket.status == "cancelled").count()
    
    # Stats par priorité
    priority_stats = db.query(
        MaintenanceTicket.priority,
        func.count(MaintenanceTicket.id)
    ).group_by(MaintenanceTicket.priority).all()
    
    by_priority = {priority: count for priority, count in priority_stats}
    
    return MaintenanceTicketStats(
        total=total,
        pending=pending,
        in_progress=in_progress,
        completed=completed,
        cancelled=cancelled,
        by_priority=by_priority
    )


@app.get("/health")
def health_check():
    return {"status": "healthy"}
