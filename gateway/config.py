"""Configuration du Gateway API"""

import os

# URLs des microservices - lues depuis les variables d'environnement
SERVICES = {
    "user": os.getenv("USER_SERVICE_URL", "http://user-service:8001"),
    "machine": os.getenv("MACHINE_SERVICE_URL", "http://machine-service:8002"),
    "event": os.getenv("EVENT_SERVICE_URL", "http://event-service:8003"),
    "alert": os.getenv("ALERT_SERVICE_URL", "http://alert-service:8004"),
    "maintenance": os.getenv("MAINTENANCE_SERVICE_URL", "http://maintenance-service:8005"),
}

# Timeouts
REQUEST_TIMEOUT = 30.0

# Logging
LOG_LEVEL = "INFO"
