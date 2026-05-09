import httpx
import logging
import json

logger = logging.getLogger(__name__)

class EventServiceClient:
    def __init__(self, event_service_url="http://localhost:8003"):
        self.event_service_url = event_service_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def send_event(self, machine_id: int, event_type: str, severity: str, message: str, data: dict = None):
        """Envoyer un événement à l'Event Service"""
        try:
            event_payload = {
                "machine_id": machine_id,
                "event_type": event_type,
                "severity": severity,
                "message": message,
                "data": json.dumps(data) if data else None
            }
            
            response = await self.client.post(
                f"{self.event_service_url}/events/",
                json=event_payload
            )
            
            if response.status_code == 200:
                logger.info(f"Event sent successfully: {event_payload}")
                return True
            else:
                logger.error(f"Failed to send event: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending event to Event Service: {e}")
            return False
    
    async def close(self):
        await self.client.aclose()

# Instance globale
event_client = EventServiceClient()
