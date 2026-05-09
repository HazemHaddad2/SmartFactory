from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging
import threading
import time

from database import SessionLocal, engine, Base
import models
import schemas
from kafka_consumer import AlertConsumer

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer les tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Alert Service")

# Instance globale du consumer
alert_consumer = None

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

@app.get("/")
def root():
    return {"message": "Alert Service is running"}

@app.post("/alerts/", response_model=schemas.AlertResponse)
def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    """Créer une alerte manuellement"""
    new_alert = models.Alert(
        event_id=alert.event_id,
        machine_id=alert.machine_id,
        alert_type=alert.alert_type,
        severity=alert.severity,
        title=alert.title,
        message=alert.message
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert

@app.get("/alerts/", response_model=List[schemas.AlertResponse])
def get_alerts(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    machine_id: int = None,
    db: Session = Depends(get_db)
):
    """Récupérer les alertes"""
    query = db.query(models.Alert)
    
    if status:
        query = query.filter(models.Alert.status == status)
    
    if machine_id:
        query = query.filter(models.Alert.machine_id == machine_id)
    
    alerts = query.order_by(models.Alert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts

@app.get("/alerts/{alert_id}", response_model=schemas.AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Récupérer une alerte spécifique"""
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@app.patch("/alerts/{alert_id}", response_model=schemas.AlertResponse)
def update_alert_status(
    alert_id: int,
    alert_update: schemas.AlertUpdate,
    db: Session = Depends(get_db)
):
    """Mettre à jour le statut d'une alerte"""
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = alert_update.status
    
    if alert_update.status == "acknowledged":
        alert.acknowledged_at = datetime.utcnow()
    elif alert_update.status == "resolved":
        alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    return alert

@app.get("/alerts/stats/summary")
def get_alert_stats(db: Session = Depends(get_db)):
    """Obtenir des statistiques sur les alertes"""
    total = db.query(models.Alert).count()
    active = db.query(models.Alert).filter(models.Alert.status == "active").count()
    acknowledged = db.query(models.Alert).filter(models.Alert.status == "acknowledged").count()
    resolved = db.query(models.Alert).filter(models.Alert.status == "resolved").count()
    
    critical = db.query(models.Alert).filter(
        models.Alert.severity == "critical",
        models.Alert.status == "active"
    ).count()
    
    return {
        "total": total,
        "active": active,
        "acknowledged": acknowledged,
        "resolved": resolved,
        "critical_active": critical
    }

@app.post("/alerts/{alert_id}/acknowledge", response_model=schemas.AlertResponse)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """Acquitter une alerte"""
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.status == "resolved":
        raise HTTPException(status_code=400, detail="Cannot acknowledge a resolved alert")
    
    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    logger.info(f"✅ Alert {alert_id} acknowledged")
    return alert

@app.post("/alerts/{alert_id}/resolve", response_model=schemas.AlertResponse)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Résoudre une alerte"""
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    logger.info(f"✅ Alert {alert_id} resolved")
    return alert

@app.post("/alerts/bulk/acknowledge")
def bulk_acknowledge_alerts(machine_id: int = None, db: Session = Depends(get_db)):
    """Acquitter toutes les alertes actives d'une machine ou toutes les alertes actives"""
    query = db.query(models.Alert).filter(models.Alert.status == "active")
    
    if machine_id:
        query = query.filter(models.Alert.machine_id == machine_id)
    
    alerts = query.all()
    count = 0
    
    for alert in alerts:
        alert.status = "acknowledged"
        alert.acknowledged_at = datetime.utcnow()
        count += 1
    
    db.commit()
    
    logger.info(f"✅ Bulk acknowledged {count} alerts" + (f" for machine {machine_id}" if machine_id else ""))
    
    return {"acknowledged_count": count, "machine_id": machine_id}

@app.post("/alerts/bulk/resolve")
def bulk_resolve_alerts(machine_id: int = None, db: Session = Depends(get_db)):
    """Résoudre toutes les alertes d'une machine ou toutes les alertes"""
    query = db.query(models.Alert).filter(models.Alert.status.in_(["active", "acknowledged"]))
    
    if machine_id:
        query = query.filter(models.Alert.machine_id == machine_id)
    
    alerts = query.all()
    count = 0
    
    for alert in alerts:
        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        count += 1
    
    db.commit()
    
    logger.info(f"✅ Bulk resolved {count} alerts" + (f" for machine {machine_id}" if machine_id else ""))
    
    return {"resolved_count": count, "machine_id": machine_id}

@app.get("/alerts/by-machine/{machine_id}", response_model=List[schemas.AlertResponse])
def get_alerts_by_machine(machine_id: int, status: str = None, db: Session = Depends(get_db)):
    """Récupérer toutes les alertes d'une machine spécifique"""
    query = db.query(models.Alert).filter(models.Alert.machine_id == machine_id)
    
    if status:
        query = query.filter(models.Alert.status == status)
    
    alerts = query.order_by(models.Alert.created_at.desc()).all()
    return alerts

@app.get("/alerts/stats/by-machine")
def get_alert_stats_by_machine(db: Session = Depends(get_db)):
    """Obtenir des statistiques d'alertes par machine"""
    from sqlalchemy import func
    
    stats = db.query(
        models.Alert.machine_id,
        func.count(models.Alert.id).label('total'),
        func.sum(func.case([(models.Alert.status == 'active', 1)], else_=0)).label('active'),
        func.sum(func.case([(models.Alert.status == 'acknowledged', 1)], else_=0)).label('acknowledged'),
        func.sum(func.case([(models.Alert.status == 'resolved', 1)], else_=0)).label('resolved'),
        func.sum(func.case([(models.Alert.severity == 'critical', 1)], else_=0)).label('critical')
    ).group_by(models.Alert.machine_id).all()
    
    result = []
    for stat in stats:
        result.append({
            "machine_id": stat.machine_id,
            "total": stat.total,
            "active": stat.active or 0,
            "acknowledged": stat.acknowledged or 0,
            "resolved": stat.resolved or 0,
            "critical": stat.critical or 0
        })
    
    return result

def start_kafka_consumer():
    """Démarre le consumer Kafka en arrière-plan"""
    global alert_consumer
    
    def consumer_thread():
        # Attendre que Kafka soit prêt
        time.sleep(10)
        logger.info("Starting Kafka consumer thread...")
        
        alert_consumer = AlertConsumer()
        alert_consumer.start_consuming()
    
    # Démarrer le consumer dans un thread séparé
    thread = threading.Thread(target=consumer_thread, daemon=True)
    thread.start()
    logger.info("Kafka consumer thread started")

def start_auto_resolver():
    """Démarre le système de résolution automatique des alertes"""
    def auto_resolver_thread():
        while True:
            try:
                time.sleep(60)  # Vérifier toutes les minutes
                
                db = SessionLocal()
                try:
                    # Résoudre automatiquement les alertes anciennes (plus de 30 minutes)
                    from datetime import timedelta
                    cutoff_time = datetime.utcnow() - timedelta(minutes=30)
                    
                    old_alerts = db.query(models.Alert).filter(
                        models.Alert.status == "acknowledged",
                        models.Alert.acknowledged_at < cutoff_time
                    ).all()
                    
                    resolved_count = 0
                    for alert in old_alerts:
                        alert.status = "resolved"
                        alert.resolved_at = datetime.utcnow()
                        resolved_count += 1
                    
                    if resolved_count > 0:
                        db.commit()
                        logger.info(f"🔄 Auto-resolved {resolved_count} old acknowledged alerts")
                    
                except Exception as e:
                    logger.error(f"Error in auto-resolver: {e}")
                    db.rollback()
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"Error in auto-resolver thread: {e}")
                time.sleep(60)
    
    # Démarrer le résolveur automatique dans un thread séparé
    thread = threading.Thread(target=auto_resolver_thread, daemon=True)
    thread.start()
    logger.info("Auto-resolver thread started")

@app.on_event("startup")
def startup_event():
    """Démarrer le consumer Kafka et le résolveur automatique au démarrage de l'application"""
    start_kafka_consumer()
    start_auto_resolver()

@app.on_event("shutdown")
def shutdown_event():
    """Fermer le consumer Kafka à l'arrêt"""
    global alert_consumer
    if alert_consumer:
        alert_consumer.close()
