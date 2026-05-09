"""
Configuration du Machine Service
"""
import os

# URLs des services - utiliser les noms de services Docker
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://event-service:8003")
ALERT_SERVICE_URL = os.getenv("ALERT_SERVICE_URL", "http://alert-service:8004")

# Configuration des seuils d'alerte
TEMPERATURE_THRESHOLD = float(os.getenv("TEMPERATURE_THRESHOLD", "85.0"))
