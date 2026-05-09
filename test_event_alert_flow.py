#!/usr/bin/env python3
"""
Script de test pour vérifier le flux événement -> alerte
"""

import requests
import time
import json

# URLs des services
EVENT_SERVICE_URL = "http://localhost:8003"
ALERT_SERVICE_URL = "http://localhost:8004"

def create_test_event(machine_id, event_type, severity, message):
    """Créer un événement de test"""
    event_data = {
        "machine_id": machine_id,
        "event_type": event_type,
        "severity": severity,
        "message": message,
        "data": json.dumps({"test": True, "source": "test_script"})  # Convertir en string JSON
    }
    
    print(f"🔄 Creating event: {event_type} (severity: {severity}) for machine {machine_id}")
    
    try:
        response = requests.post(f"{EVENT_SERVICE_URL}/events/", json=event_data)
        if response.status_code == 200:
            event = response.json()
            print(f"✅ Event created with ID: {event['id']}")
            return event
        else:
            print(f"❌ Failed to create event: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating event: {e}")
        return None

def check_alerts():
    """Vérifier les alertes créées"""
    try:
        response = requests.get(f"{ALERT_SERVICE_URL}/alerts/")
        if response.status_code == 200:
            alerts = response.json()
            print(f"\n📊 Total alerts: {len(alerts)}")
            
            for alert in alerts[-5:]:  # Afficher les 5 dernières alertes
                print(f"  - Alert ID: {alert['id']}, Event ID: {alert['event_id']}, "
                      f"Machine: {alert['machine_id']}, Type: {alert['alert_type']}, "
                      f"Severity: {alert['severity']}, Status: {alert['status']}")
            return alerts
        else:
            print(f"❌ Failed to get alerts: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting alerts: {e}")
        return []

def main():
    print("🚀 Testing Event -> Alert Flow")
    print("=" * 50)
    
    # Test 1: Événement critique (doit créer une alerte)
    print("\n1️⃣ Test: Critical event (should create alert)")
    event1 = create_test_event(
        machine_id=1,
        event_type="temperature_critical",
        severity="critical",
        message="Temperature exceeded critical threshold: 85°C"
    )
    
    # Test 2: Événement d'erreur (doit créer une alerte)
    print("\n2️⃣ Test: Error event (should create alert)")
    event2 = create_test_event(
        machine_id=2,
        event_type="error",
        severity="high",
        message="Machine malfunction detected"
    )
    
    # Test 3: Événement normal (ne doit pas créer d'alerte)
    print("\n3️⃣ Test: Normal event (should NOT create alert)")
    event3 = create_test_event(
        machine_id=3,
        event_type="status_update",
        severity="low",
        message="Machine status updated"
    )
    
    # Attendre que les événements soient traités
    print("\n⏳ Waiting 5 seconds for events to be processed...")
    time.sleep(5)
    
    # Vérifier les alertes
    print("\n📋 Checking alerts:")
    alerts = check_alerts()
    
    # Statistiques
    print("\n📈 Getting alert statistics:")
    try:
        response = requests.get(f"{ALERT_SERVICE_URL}/alerts/stats/summary")
        if response.status_code == 200:
            stats = response.json()
            print(f"  - Total: {stats['total']}")
            print(f"  - Active: {stats['active']}")
            print(f"  - Critical Active: {stats['critical_active']}")
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")

if __name__ == "__main__":
    main()