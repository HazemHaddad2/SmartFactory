#!/usr/bin/env python3
"""
Test avec vérification des logs en temps réel
"""

import requests
import json
import time

def create_critical_event():
    event_data = {
        "machine_id": 999,
        "event_type": "temperature_critical",
        "severity": "critical",
        "message": "TEST: Température critique 99°C",
        "data": json.dumps({"temperature": 99.0, "test": True})
    }
    
    print("🔥 Création d'un événement critique de test...")
    response = requests.post("http://localhost:8003/events/", json=event_data)
    
    if response.status_code == 200:
        event = response.json()
        print(f"✅ Événement créé avec ID: {event['id']}")
        print(f"   Machine: {event['machine_id']}")
        print(f"   Type: {event['event_type']}")
        print(f"   Sévérité: {event['severity']}")
        
        print("\n⏳ Attente 10 secondes pour le traitement Kafka...")
        time.sleep(10)
        
        # Vérifier les alertes
        print("\n🔍 Vérification des alertes...")
        response = requests.get("http://localhost:8004/alerts/")
        if response.status_code == 200:
            alerts = response.json()
            
            # Chercher une alerte pour cet événement
            matching_alerts = [a for a in alerts if a['event_id'] == event['id']]
            
            if matching_alerts:
                alert = matching_alerts[0]
                print(f"✅ ALERTE TROUVÉE!")
                print(f"   ID Alerte: {alert['id']}")
                print(f"   ID Événement: {alert['event_id']}")
                print(f"   Machine: {alert['machine_id']}")
                print(f"   Type: {alert['alert_type']}")
                print(f"   Sévérité: {alert['severity']}")
                print(f"   Statut: {alert['status']}")
                print(f"   Message: {alert['message']}")
            else:
                print(f"❌ Aucune alerte trouvée pour l'événement {event['id']}")
                print(f"   Total alertes dans le système: {len(alerts)}")
        
        return event
    else:
        print(f"❌ Échec création événement: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    print("🧪 Test de création d'alerte avec logs")
    print("=" * 50)
    
    print("\nAPRÈS CE TEST, VÉRIFIEZ LES LOGS AVEC:")
    print("docker-compose logs --tail=20 alert-service")
    print("docker-compose logs --tail=20 event-service")
    
    create_critical_event()