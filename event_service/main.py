from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging

from database import SessionLocal, engine, Base
import models
import schemas
from kafka_producer import event_producer

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer les tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Service")

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
    return {"message": "Event Service is running"}

@app.post("/events/", response_model=schemas.EventResponse)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    """Créer un événement et l'envoyer à Kafka"""
    
    logger.info(f"📝 Creating new event: machine_id={event.machine_id}, type={event.event_type}, severity={event.severity}")
    
    # Sauvegarder l'événement dans la base de données
    new_event = models.Event(
        machine_id=event.machine_id,
        event_type=event.event_type,
        severity=event.severity,
        message=event.message,
        data=event.data
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    logger.info(f"✅ Event saved to database with ID: {new_event.id}")
    
    # Préparer les données pour Kafka
    event_data = {
        "id": new_event.id,
        "machine_id": new_event.machine_id,
        "event_type": new_event.event_type,
        "severity": new_event.severity,
        "message": new_event.message,
        "data": new_event.data,
        "timestamp": new_event.timestamp.isoformat()
    }
    
    # Envoyer à Kafka
    topic = "machine-events"
    success = event_producer.send_event(topic, event_data)
    
    if success:
        logger.info(f"🚀 Event {new_event.id} sent to Kafka topic '{topic}' successfully")
    else:
        logger.warning(f"⚠️ Event {new_event.id} saved to DB but failed to send to Kafka")
    
    return new_event

@app.get("/events/", response_model=List[schemas.EventResponse])
def get_events(
    skip: int = 0,
    limit: int = 100,
    machine_id: int = None,
    db: Session = Depends(get_db)
):
    """Récupérer les événements"""
    query = db.query(models.Event)
    
    if machine_id:
        query = query.filter(models.Event.machine_id == machine_id)
    
    events = query.order_by(models.Event.timestamp.desc()).offset(skip).limit(limit).all()
    return events

@app.get("/events/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Récupérer un événement spécifique"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.on_event("shutdown")
def shutdown_event():
    """Fermer le producteur Kafka à l'arrêt"""
    event_producer.close()
