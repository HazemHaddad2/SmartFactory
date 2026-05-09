from kafka import KafkaProducer
import json
import logging
import os
import time

logger = logging.getLogger(__name__)

class EventProducer:
    def __init__(self, bootstrap_servers=None):
        if bootstrap_servers is None:
            # Use environment variable or default to Docker service name
            bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
        
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self._create_producer()
        
    def _create_producer(self):
        """Créer une nouvelle instance du producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(0, 10, 1),
                retries=3,
                retry_backoff_ms=1000
            )
            logger.info(f"Kafka producer initialized successfully with {self.bootstrap_servers}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.producer = None
            return False
    
    def send_event(self, topic: str, event_data: dict):
        """Envoie un événement à Kafka avec retry automatique"""
        max_retries = 3
        
        for attempt in range(max_retries):
            if self.producer is None:
                logger.warning(f"Producer not available, attempting to recreate... (attempt {attempt + 1})")
                if not self._create_producer():
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        logger.error("Failed to create producer after all retries")
                        return False
            
            try:
                logger.info(f"📤 Sending event to Kafka topic '{topic}': {event_data}")
                future = self.producer.send(topic, event_data)
                # Attendre la confirmation
                record_metadata = future.get(timeout=10)
                logger.info(f"✅ Event sent successfully to {topic}: partition={record_metadata.partition}, offset={record_metadata.offset}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to send event to Kafka (attempt {attempt + 1}): {e}")
                self.producer = None  # Force recreation on next attempt
                
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    logger.error("Failed to send event after all retries")
                    return False
        
        return False
    
    def close(self):
        if self.producer:
            try:
                self.producer.close()
                logger.info("Kafka producer closed")
            except Exception as e:
                logger.error(f"Error closing producer: {e}")

# Instance globale
event_producer = EventProducer()
