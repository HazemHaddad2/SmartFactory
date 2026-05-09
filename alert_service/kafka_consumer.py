from kafka import KafkaConsumer
import json
import logging
import os
import time
from datetime import datetime
from database import SessionLocal
import models

logger = logging.getLogger(__name__)

class AlertConsumer:
    def __init__(self, bootstrap_servers=None, topic='machine-events'):
        if bootstrap_servers is None:
            # Use environment variable or default to Docker service name
            bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
        
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.consumer = None
        self.running = False
        
    def _create_consumer(self):
        """Créer une nouvelle instance du consumer"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',  # Changé de 'latest' à 'earliest' pour traiter tous les messages
                enable_auto_commit=True,
                group_id='alert-service-group',
                api_version=(0, 10, 1),
                consumer_timeout_ms=30000,  # Augmenté le timeout à 30 secondes
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            logger.info(f"Kafka consumer created for topic: {self.topic} with {self.bootstrap_servers}")
            return True
        except Exception as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            return False
    
    def process_event(self, event_data: dict):
        """Traiter un événement et créer une alerte si nécessaire"""
        db = SessionLocal()
        try:
            severity = event_data.get('severity', 'low')
            event_type = event_data.get('event_type', 'unknown')
            machine_id = event_data.get('machine_id')
            
            logger.info(f"Processing event: ID={event_data.get('id')}, Type={event_type}, Severity={severity}")
            
            # Créer une alerte pour les événements critiques, d'erreur, ou de haute sévérité
            should_create_alert = (
                severity in ['high', 'critical'] or 
                event_type in ['error', 'failure', 'malfunction', 'temperature_critical', 'pressure_high'] or
                'critical' in event_type.lower() or
                'error' in event_type.lower()
            )
            
            if should_create_alert:
                # Vérifier si une alerte existe déjà pour cet événement
                existing_alert = db.query(models.Alert).filter(
                    models.Alert.event_id == event_data['id']
                ).first()
                
                if not existing_alert:
                    alert = models.Alert(
                        event_id=event_data['id'],
                        machine_id=event_data['machine_id'],
                        alert_type=event_type,
                        severity=severity,
                        title=f"Alert: {event_type.upper()} on Machine {event_data['machine_id']}",
                        message=event_data['message'],
                        status='active'
                    )
                    db.add(alert)
                    db.commit()
                    logger.info(f"✅ NEW ALERT CREATED for event {event_data['id']} - Machine {event_data['machine_id']} - Type: {event_type} - Severity: {severity}")
                else:
                    logger.info(f"Alert already exists for event {event_data['id']}")
            else:
                # Pour les événements normaux, vérifier s'il faut résoudre des alertes existantes
                if event_type in ['status_normal', 'temperature_normal', 'pressure_normal', 'maintenance_complete']:
                    # Résoudre automatiquement les alertes actives de cette machine
                    active_alerts = db.query(models.Alert).filter(
                        models.Alert.machine_id == machine_id,
                        models.Alert.status.in_(['active', 'acknowledged'])
                    ).all()
                    
                    resolved_count = 0
                    for alert in active_alerts:
                        alert.status = 'resolved'
                        alert.resolved_at = datetime.utcnow()
                        resolved_count += 1
                    
                    if resolved_count > 0:
                        db.commit()
                        logger.info(f"🔄 AUTO-RESOLVED {resolved_count} alerts for machine {machine_id} due to normal status event")
                
                logger.info(f"Event {event_data['id']} processed but no alert created (severity: {severity}, type: {event_type}) - Not meeting alert criteria")
        
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            db.rollback()
        finally:
            db.close()
    
    def start_consuming(self):
        """Démarrer la consommation des messages avec reconnexion automatique"""
        self.running = True
        
        while self.running:
            try:
                if not self._create_consumer():
                    logger.warning("Failed to create consumer, retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                
                logger.info(f"🚀 Starting to consume messages from topic: {self.topic}")
                
                for message in self.consumer:
                    if not self.running:
                        break
                        
                    try:
                        logger.info(f"📨 Received message: {message.value}")
                        self.process_event(message.value)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        
            except KeyboardInterrupt:
                logger.info("Consumer stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                logger.info("Reconnecting in 5 seconds...")
                time.sleep(5)
            finally:
                if self.consumer:
                    try:
                        self.consumer.close()
                    except:
                        pass
                    self.consumer = None
        
        logger.info("Alert consumer stopped")
    
    def close(self):
        """Arrêter le consumer proprement"""
        self.running = False
        if self.consumer:
            try:
                self.consumer.close()
            except:
                pass
            logger.info("Kafka consumer closed")
