"""Gateway API - Point d'entrée unique pour tous les microservices"""

from fastapi import FastAPI, Depends, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Any, Dict
import logging

from config import SERVICES
from http_client import ServiceClient
from auth_middleware import verify_token, require_admin, require_auth

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SmartFactory Gateway API",
    description="Point d'entrée unique pour tous les microservices",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clients pour chaque service
user_client = ServiceClient(SERVICES["user"])
machine_client = ServiceClient(SERVICES["machine"])
event_client = ServiceClient(SERVICES["event"])
alert_client = ServiceClient(SERVICES["alert"])
maintenance_client = ServiceClient(SERVICES.get("maintenance", "http://maintenance-service:8005"))

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
def root():
    return {
        "message": "SmartFactory Gateway API",
        "version": "1.0.0",
        "services": list(SERVICES.keys())
    }

@app.get("/health")
async def health_check():
    """Vérifier la santé de tous les services"""
    health_status = {}
    
    for service_name, service_url in SERVICES.items():
        try:
            client = ServiceClient(service_url)
            await client.get("/")
            health_status[service_name] = "healthy"
            await client.close()
        except Exception as e:
            health_status[service_name] = f"unhealthy: {str(e)}"
    
    return health_status

# ============================================================================
# USER SERVICE ROUTES
# ============================================================================

@app.post("/auth/register")
async def register(username: str, password: str, role: str = "user"):
    """Créer un nouvel utilisateur"""
    try:
        result = await user_client.post(
            "/users/",
            json={"username": username, "password": password, "role": role}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
async def login(username: str, password: str):
    """Se connecter"""
    try:
        result = await user_client.post(
            "/login",
            json={"username": username, "password": password}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/users")
async def get_users(skip: int = 0, limit: int = 100):
    """Récupérer tous les utilisateurs"""
    try:
        result = await user_client.get("/users/", params={"skip": skip, "limit": limit})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MACHINE SERVICE ROUTES
# ============================================================================

@app.post("/machines")
async def create_machine(
    name: str,
    status: str = "idle",
    user: dict = Depends(verify_token)
):
    """Créer une nouvelle machine (Admin uniquement)"""
    require_admin(user)
    
    try:
        result = await machine_client.post(
            "/machines/",
            json={"name": name, "status": status}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/machines")
async def get_machines(
    skip: int = 0,
    limit: int = 100
):
    """Récupérer toutes les machines"""
    try:
        result = await machine_client.get("/machines/", params={"skip": skip, "limit": limit})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/machines/{machine_id}")
async def get_machine(machine_id: int):
    """Récupérer une machine spécifique"""
    try:
        result = await machine_client.get(f"/machines/{machine_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="Machine not found")

@app.patch("/machines/{machine_id}")
async def update_machine(
    machine_id: int,
    status: Optional[str] = None,
    temperature: Optional[float] = None,
    uptime: Optional[int] = None,
    user: dict = Depends(verify_token)
):
    """Mettre à jour une machine (Admin uniquement)"""
    require_admin(user)
    
    try:
        update_data = {}
        if status is not None:
            update_data["status"] = status
        if temperature is not None:
            update_data["temperature"] = temperature
        if uptime is not None:
            update_data["uptime"] = uptime
        
        result = await machine_client.patch(
            f"/machines/{machine_id}",
            json=update_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/machines/{machine_id}")
async def delete_machine(
    machine_id: int,
    user: dict = Depends(verify_token)
):
    """Supprimer une machine (Admin uniquement)"""
    require_admin(user)
    
    try:
        result = await machine_client.delete(f"/machines/{machine_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="Machine not found")

# ============================================================================
# EVENT SERVICE ROUTES
# ============================================================================

@app.get("/events")
async def get_events(
    skip: int = 0,
    limit: int = 100,
    machine_id: Optional[int] = None
):
    """Récupérer les événements"""
    try:
        params = {"skip": skip, "limit": limit}
        if machine_id is not None:
            params["machine_id"] = machine_id
        
        result = await event_client.get("/events/", params=params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{event_id}")
async def get_event(event_id: int):
    """Récupérer un événement spécifique"""
    try:
        result = await event_client.get(f"/events/{event_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="Event not found")

# ============================================================================
# ALERT SERVICE ROUTES
# ============================================================================

@app.get("/alerts")
async def get_alerts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    machine_id: Optional[int] = None
):
    """Récupérer les alertes"""
    try:
        params = {"skip": skip, "limit": limit}
        if status is not None:
            params["status"] = status
        if machine_id is not None:
            params["machine_id"] = machine_id
        
        result = await alert_client.get("/alerts/", params=params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts/{alert_id}")
async def get_alert(alert_id: int):
    """Récupérer une alerte spécifique"""
    try:
        result = await alert_client.get(f"/alerts/{alert_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="Alert not found")

@app.patch("/alerts/{alert_id}")
async def update_alert_status(
    alert_id: int,
    status: str,
    user: dict = Depends(verify_token)
):
    """Mettre à jour le statut d'une alerte (Admin ou Technicien)"""
    require_auth(user)
    
    try:
        result = await alert_client.patch(
            f"/alerts/{alert_id}",
            json={"status": status}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/alerts/stats/summary")
async def get_alert_stats():
    """Obtenir les statistiques des alertes"""
    try:
        result = await alert_client.get("/alerts/stats/summary")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DASHBOARD ROUTES (Agrégation de données)
# ============================================================================

@app.get("/dashboard/overview")
async def get_dashboard_overview():
    """Obtenir un aperçu du dashboard"""
    try:
        # Récupérer les données de tous les services
        machines = await machine_client.get("/machines/", params={"limit": 100})
        events = await event_client.get("/events/", params={"limit": 10})
        alert_stats = await alert_client.get("/alerts/stats/summary")
        
        return {
            "machines_count": len(machines) if isinstance(machines, list) else 0,
            "recent_events": events if isinstance(events, list) else [],
            "alert_stats": alert_stats,
            "timestamp": None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/machine/{machine_id}")
async def get_machine_dashboard(machine_id: int):
    """Obtenir le dashboard d'une machine spécifique"""
    try:
        machine = await machine_client.get(f"/machines/{machine_id}")
        events = await event_client.get("/events/", params={"machine_id": machine_id, "limit": 20})
        alerts = await alert_client.get("/alerts/", params={"machine_id": machine_id, "limit": 20})
        
        return {
            "machine": machine,
            "recent_events": events if isinstance(events, list) else [],
            "recent_alerts": alerts if isinstance(alerts, list) else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MAINTENANCE SERVICE ROUTES
# ============================================================================

@app.post("/maintenance/tickets")
async def create_maintenance_ticket(
    machine_id: int,
    title: str,
    description: str,
    priority: str,
    assigned_to: Optional[int] = None,
    created_by: Optional[int] = None,
    user: dict = Depends(verify_token)
):
    """Créer un ticket de maintenance"""
    require_auth(user)
    
    try:
        ticket_data = {
            "machine_id": machine_id,
            "title": title,
            "description": description,
            "priority": priority
        }
        if assigned_to is not None:
            ticket_data["assigned_to"] = assigned_to
        if created_by is not None:
            ticket_data["created_by"] = created_by
        
        result = await maintenance_client.post("/api/tickets", json=ticket_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/maintenance/tickets")
async def get_maintenance_tickets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    machine_id: Optional[int] = None,
    assigned_to: Optional[int] = None,
    created_by: Optional[int] = None
):
    """Récupérer les tickets de maintenance"""
    try:
        params = {"skip": skip, "limit": limit}
        if status is not None:
            params["status"] = status
        if priority is not None:
            params["priority"] = priority
        if machine_id is not None:
            params["machine_id"] = machine_id
        if assigned_to is not None:
            params["assigned_to"] = assigned_to
        if created_by is not None:
            params["created_by"] = created_by
        
        result = await maintenance_client.get("/api/tickets", params=params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/maintenance/tickets/{ticket_id}")
async def get_maintenance_ticket(ticket_id: int):
    """Récupérer un ticket spécifique"""
    try:
        result = await maintenance_client.get(f"/api/tickets/{ticket_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="Ticket not found")

@app.put("/maintenance/tickets/{ticket_id}")
async def update_maintenance_ticket(
    ticket_id: int,
    updates: Dict[str, Any],
    user: dict = Depends(verify_token)
):
    """Mettre à jour un ticket de maintenance"""
    require_auth(user)
    
    try:
        result = await maintenance_client.put(f"/api/tickets/{ticket_id}", json=updates)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/maintenance/tickets/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    status: str,
    user: dict = Depends(verify_token)
):
    """Mettre à jour le statut d'un ticket"""
    require_auth(user)
    
    try:
        result = await maintenance_client.patch(
            f"/api/tickets/{ticket_id}/status",
            json={"status": status}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/maintenance/tickets/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: int,
    assigned_to: int,
    user: dict = Depends(verify_token)
):
    """Assigner un ticket à un technicien"""
    require_auth(user)
    
    try:
        result = await maintenance_client.patch(
            f"/api/tickets/{ticket_id}/assign",
            json={"assigned_to": assigned_to}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/maintenance/tickets/{ticket_id}")
async def delete_maintenance_ticket(
    ticket_id: int,
    user: dict = Depends(verify_token)
):
    """Supprimer un ticket de maintenance"""
    require_admin(user)
    
    try:
        result = await maintenance_client.delete(f"/api/tickets/{ticket_id}")
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail="Ticket not found")

@app.get("/maintenance/tickets/stats")
async def get_maintenance_stats():
    """Obtenir les statistiques des tickets de maintenance"""
    try:
        result = await maintenance_client.get("/api/tickets/stats")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SHUTDOWN
# ============================================================================

@app.on_event("shutdown")
async def shutdown_event():
    """Fermer tous les clients à l'arrêt"""
    await user_client.close()
    await machine_client.close()
    await event_client.close()
    await alert_client.close()
    await maintenance_client.close()
    logger.info("Gateway API shutdown")
