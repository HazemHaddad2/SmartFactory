#!/usr/bin/env python3
"""
Script de test simple pour vérifier les APIs
"""

import requests
import time
import json

# URLs des services
EVENT_SERVICE_URL = "http://localhost:8003"
ALERT_SERVICE_URL = "http://localhost:8004"

def test_services_health():
    """Tester que les services répondent"""
    print("🏥 Testing services health...")
    
    try:
        # Test event service
        response = requests.get(f"{EVENT_SERVICE_URL}/")
        if response.status_code == 200:
            print("✅ Event Service is running")
        else:
            print(f"❌ Event Service error: {response.status_code}")
            
        # Test alert service
        response = requests.get(f"{ALERT_SERVICE_URL}/")
        if response.status_code == 200:
            print("✅ Alert Service is running")
        else:
            print(f"❌ Alert Service error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Service health check failed: {e}")

def create_test_events():
    """Créer des événements de test"""
    print("\n📝 Creating test events...")
    
    events = [
        {
            "machine_id": 1,
            "event_type": "temperature_critical",
            "severity": "critical",
            "message": "Temperature exceeded critical threshold: 85°C",
            "data": json.dumps({"temperature": 85.0, "threshold": 75.0})
        },
        {
            "machine_id": 2,
            "event_type": "error",
            "severity": "high",
            "message": "Machine malfunction detected",
            "data": json.dumps({"error_code": "E001", "component": "motor"})
        },
        {
            "machine_id": 3,
            "event_type": "status_update",
            "severity": "low",
            "message": "Machine status updated to active",
            "data": json.dumps({"previous_status": "idle", "new_status": "active"})
        }
    ]
    
    created_events = []
    
    for i, event_data in enumerate(events, 1):
        print(f"\n{i}️⃣ Creating {event_data['event_type']} event (severity: {event_data['severity']})")
        
        try:
            response = requests.post(f"{EVENT_SERVICE_URL}/events/", json=event_data)
            if response.status_code == 200:
                event = response.json()
                print(f"   ✅ Event created with ID: {event['id']}")
                created_events.append(event)
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return created_events

def check_alerts():
    """Vérifier les alertes"""
    print("\n🚨 Checking alerts...")
    
    try:
        response = requests.get(f"{ALERT_SERVICE_URL}/alerts/")
        if response.status_code == 200:
            alerts = response.json()
            print(f"   📊 Total alerts found: {len(alerts)}")
            
            if alerts:
                print("   📋 Recent alerts:")
                for alert in alerts[-5:]:  # 5 dernières alertes
                    print(f"      - ID: {alert['id']}, Event: {alert['event_id']}, "
                          f"Machine: {alert['machine_id']}, Type: {alert['alert_type']}, "
                          f"Severity: {alert['severity']}, Status: {alert['status']}")
            else:
                print("   ℹ️ No alerts found")
                
            return alerts
        else:
            print(f"   ❌ Failed to get alerts: {response.status_code}")
            return []
    except Exception as e:
        print(f"   ❌ Error getting alerts: {e}")
        return []

def get_alert_stats():
    """Obtenir les statistiques d'alertes"""
    print("\n📈 Getting alert statistics...")
    
    try:
        response = requests.get(f"{ALERT_SERVICE_URL}/alerts/stats/summary")
        if response.status_code == 200:
            stats = response.json()
            print(f"   📊 Statistics:")
            print(f"      - Total: {stats['total']}")
            print(f"      - Active: {stats['active']}")
            print(f"      - Acknowledged: {stats['acknowledged']}")
            print(f"      - Resolved: {stats['resolved']}")
            print(f"      - Critical Active: {stats['critical_active']}")
            return stats
        else:
            print(f"   ❌ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting stats: {e}")

def main():
    print("🧪 Simple Flow Test")
    print("=" * 50)
    
    # 1. Vérifier que les services fonctionnent
    test_services_health()
    
    # 2. Créer des événements
    events = create_test_events()
    
    # 3. Attendre un peu pour le traitement
    print(f"\n⏳ Waiting 10 seconds for Kafka processing...")
    time.sleep(10)
    
    # 4. Vérifier les alertes
    alerts = check_alerts()
    
    # 5. Statistiques
    stats = get_alert_stats()
    
    # 6. Résumé
    print(f"\n📋 Test Summary:")
    print(f"   - Events created: {len(events)}")
    print(f"   - Alerts found: {len(alerts) if alerts else 0}")
    
    if len(events) > 0 and len(alerts) > 0:
        print("   ✅ Flow working: Events are creating alerts!")
    elif len(events) > 0 and len(alerts) == 0:
        print("   ⚠️ Events created but no alerts found. Check Kafka consumer logs.")
    else:
        print("   ❌ No events created. Check event service.")

if __name__ == "__main__":
    main()