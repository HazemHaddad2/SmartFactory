from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging
import httpx

import models, schemas
from database import SessionLocal, engine, Base
from event_client import event_client
from config import EVENT_SERVICE_URL, ALERT_SERVICE_URL, TEMPERATURE_THRESHOLD

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Machine Service")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    """Afficher la configuration au démarrage"""
    logger.info("="*60)
    logger.info("Machine Service Configuration")
    logger.info("="*60)
    logger.info(f"Event Service URL: {EVENT_SERVICE_URL}")
    logger.info(f"Alert Service URL: {ALERT_SERVICE_URL}")
    logger.info(f"Temperature Threshold: {TEMPERATURE_THRESHOLD}°C")
    logger.info("="*60)


async def create_event_and_alert(
    machine_id: int,
    machine_name: str,
    event_type: str,
    severity: str,
    message: str,
    alert_type: str,
    alert_title: str
):
    """Créer un événement et une alerte automatiquement"""
    logger.info(f"🔔 Starting alert creation for machine {machine_id} ({machine_name})")
    logger.info(f"   Event type: {event_type}, Severity: {severity}")
    logger.info(f"   Alert type: {alert_type}, Title: {alert_title}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Créer l'événement
            event_url = f"{EVENT_SERVICE_URL}/events/"
            logger.info(f"📤 Sending event to: {event_url}")
            
            event_response = await client.post(
                event_url,
                json={
                    "machine_id": machine_id,
                    "event_type": event_type,
                    "severity": severity,
                    "message": message
                }
            )
            
            logger.info(f"📥 Event response: {event_response.status_code}")
            
            if event_response.status_code == 200:
                event_data = event_response.json()
                event_id = event_data.get("id", 0)
                logger.info(f"✅ Event created: #{event_id} for machine {machine_id}")
                
                # 2. Créer l'alerte
                alert_url = f"{ALERT_SERVICE_URL}/alerts/"
                logger.info(f"📤 Sending alert to: {alert_url}")
                
                alert_payload = {
                    "event_id": event_id,
                    "machine_id": machine_id,
                    "alert_type": alert_type,
                    "severity": severity,
                    "title": alert_title,
                    "message": message
                }
                logger.info(f"   Payload: {alert_payload}")
                
                alert_response = await client.post(
                    alert_url,
                    json=alert_payload
                )
                
                logger.info(f"📥 Alert response: {alert_response.status_code}")
                logger.info(f"   Response body: {alert_response.text}")
                
                if alert_response.status_code == 200:
                    alert_data = alert_response.json()
                    logger.info(f"✅ Alert created: #{alert_data.get('id')} for machine {machine_id}")
                else:
                    logger.error(f"❌ Failed to create alert: {alert_response.status_code}")
                    logger.error(f"   Response: {alert_response.text}")
            else:
                logger.error(f"❌ Failed to create event: {event_response.status_code}")
                logger.error(f"   Response: {event_response.text}")
                
    except Exception as e:
        logger.error(f"❌ Error creating event and alert: {e}")
        import traceback
        logger.error(traceback.format_exc())

@app.get("/")
def root():
    return {"message": "Machine Service running"}

@app.post("/machines/", response_model=schemas.MachineResponse)
def create_machine(machine: schemas.MachineCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle machine"""
    try:
        new_machine = models.Machine(
            name=machine.name,
            status=machine.status
        )
        db.add(new_machine)
        db.commit()
        db.refresh(new_machine)
        
        logger.info(f"Machine created: {new_machine.id}")
        return new_machine
    except Exception as e:
        logger.error(f"Error creating machine: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/machines/", response_model=List[schemas.MachineResponse])
def get_machines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer toutes les machines"""
    machines = db.query(models.Machine).offset(skip).limit(limit).all()
    return machines

@app.get("/machines/{machine_id}", response_model=schemas.MachineResponse)
def get_machine(machine_id: int, db: Session = Depends(get_db)):
    """Récupérer une machine spécifique"""
    machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@app.patch("/machines/{machine_id}", response_model=schemas.MachineResponse)
async def update_machine(
    machine_id: int,
    machine_update: schemas.MachineUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour une machine"""
    try:
        machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        
        old_status = machine.status
        old_temperature = machine.temperature
        
        # Mettre à jour les champs fournis
        if machine_update.status is not None:
            machine.status = machine_update.status
        if machine_update.temperature is not None:
            machine.temperature = machine_update.temperature
        if machine_update.uptime is not None:
            # Convertir l'uptime (en secondes) en timedelta
            from datetime import timedelta
            machine.uptime = timedelta(seconds=machine_update.uptime)
        
        machine.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(machine)
        
        # Vérifier si on doit créer une alerte pour changement de statut vers "fail"
        if machine_update.status is not None and machine_update.status == "fail" and old_status != "fail":
            logger.info(f"🚨 Status changed to 'fail' for machine {machine_id} (was: {old_status})")
            logger.info(f"   Triggering alert creation...")
            await create_event_and_alert(
                machine_id=machine.id,
                machine_name=machine.name,
                event_type="machine_failure",
                severity="critical",
                message=f"La machine {machine.name} est tombée en panne (statut: fail)",
                alert_type="failure",
                alert_title=f"Panne Machine: {machine.name}"
            )
            logger.info(f"✅ Alert creation completed for machine {machine_id}")
        
        # Vérifier si on doit créer une alerte pour dépassement de température
        if machine_update.temperature is not None and machine_update.temperature > TEMPERATURE_THRESHOLD:
            # Ne créer l'alerte que si la température vient de dépasser le seuil
            # ou si c'est la première fois qu'on définit une température au-dessus du seuil
            should_create_alert = (
                old_temperature is None or 
                (old_temperature is not None and old_temperature <= TEMPERATURE_THRESHOLD)
            )
            
            if should_create_alert:
                if old_temperature is not None:
                    logger.info(f"🌡️ Temperature threshold exceeded for machine {machine_id}")
                    logger.info(f"   Old: {old_temperature}°C, New: {machine.temperature}°C, Threshold: {TEMPERATURE_THRESHOLD}°C")
                else:
                    logger.info(f"🌡️ Temperature set above threshold for machine {machine_id}")
                    logger.info(f"   New: {machine.temperature}°C, Threshold: {TEMPERATURE_THRESHOLD}°C")
                
                logger.info(f"   Triggering alert creation...")
                await create_event_and_alert(
                    machine_id=machine.id,
                    machine_name=machine.name,
                    event_type="temperature_alert",
                    severity="critical",
                    message=f"Température critique détectée sur {machine.name}: {machine.temperature}°C (seuil: {TEMPERATURE_THRESHOLD}°C)",
                    alert_type="temperature",
                    alert_title=f"Surchauffe: {machine.name}"
                )
                logger.info(f"✅ Temperature alert creation completed for machine {machine_id}")
        
        logger.info(f"Machine {machine_id} updated")
        return machine
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating machine: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/machines/{machine_id}")
def delete_machine(machine_id: int, db: Session = Depends(get_db)):
    """Supprimer une machine"""
    try:
        machine = db.query(models.Machine).filter(models.Machine.id == machine_id).first()
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        
        db.delete(machine)
        db.commit()
        
        logger.info(f"Machine {machine_id} deleted")
        return {"message": "Machine deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting machine: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/machines/config/temperature-threshold")
def get_temperature_threshold():
    """Récupérer le seuil de température configuré"""
    return {
        "temperature_threshold": TEMPERATURE_THRESHOLD,
        "unit": "°C",
        "description": "Seuil au-delà duquel une alerte est créée automatiquement"
    }


@app.get("/machines/stats/summary")
def get_machine_stats(db: Session = Depends(get_db)):
    """Obtenir des statistiques sur les machines"""
    total = db.query(models.Machine).count()
    active = db.query(models.Machine).filter(models.Machine.status == "active").count()
    failed = db.query(models.Machine).filter(models.Machine.status == "fail").count()
    maintenance = db.query(models.Machine).filter(models.Machine.status == "maintenance").count()
    
    # Machines avec température élevée
    high_temp = db.query(models.Machine).filter(
        models.Machine.temperature > TEMPERATURE_THRESHOLD
    ).count()
    
    return {
        "total": total,
        "active": active,
        "failed": failed,
        "maintenance": maintenance,
        "high_temperature": high_temp,
        "temperature_threshold": TEMPERATURE_THRESHOLD
    }

@app.on_event("shutdown")
def shutdown_event():
    """Fermer le client HTTP à l'arrêt"""
    logger.info("Shutting down Machine Service")