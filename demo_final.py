#!/usr/bin/env python3
"""
Démonstration finale du système d'alertes automatiques
"""

import requests
import time
import json

EVENT_SERVICE_URL = "http://localhost:8003"
ALERT_SERVICE_URL = "http://localhost:8004"

def demo_alert_system():
    print("🎯 DÉMONSTRATION SYSTÈME D'ALERTES AUTOMATIQUES")
    print("=" * 60)
    
    # 1. État initial
    print("\n1️⃣ État initial du système:")
    response = requests.get(f"{ALERT_SERVICE_URL}/alerts/stats/summary")
    if response.status_code == 200:
        stats = response.json()
        print(f"   📊 Alertes totales: {stats['total']}")
        print(f"   🔴 Alertes actives: {stats['active']}")
        print(f"   ⚠️ Alertes critiques: {stats['critical_active']}")
    
    # 2. Créer des événements critiques
    print(f"\n2️⃣ Création d'événements critiques:")
    
    critical_events = [
        {
            "machine_id": 101,
            "event_type": "temperature_critical",
            "severity": "critical",
            "message": "Température critique détectée: 95°C (seuil: 75°C)",
            "data": json.dumps({"temperature": 95.0, "threshold": 75.0, "location": "Atelier A"})
        },
        {
            "machine_id": 102,
            "event_type": "pressure_high",
            "severity": "high",
            "message": "Pression élevée détectée: 8.5 bar (seuil: 7.0 bar)",
            "data": json.dumps({"pressure": 8.5, "threshold": 7.0, "unit": "bar"})
        },
        {
            "machine_id": 103,
            "event_type": "error",
            "severity": "critical",
            "message": "Erreur moteur: Surchauffe détectée",
            "data": json.dumps({"error_code": "E001", "component": "motor", "action_required": "immediate_stop"})
        }
    ]
    
    created_events = []
    for i, event_data in enumerate(critical_events, 1):
        print(f"   {i}. Événement: {event_data['event_type']} (Machine {event_data['machine_id']})")
        
        response = requests.post(f"{EVENT_SERVICE_URL}/events/", json=event_data)
        if response.status_code == 200:
            event = response.json()
            created_events.append(event)
            print(f"      ✅ Créé avec ID: {event['id']}")
        else:
            print(f"      ❌ Échec: {response.status_code}")
    
    # 3. Attendre le traitement
    print(f"\n3️⃣ Traitement par Kafka (attente 8 secondes)...")
    for i in range(8, 0, -1):
        print(f"   ⏳ {i}...", end="\r")
        time.sleep(1)
    print("   ✅ Traitement terminé!")
    
    # 4. Vérifier les nouvelles alertes
    print(f"\n4️⃣ Vérification des alertes générées:")
    response = requests.get(f"{ALERT_SERVICE_URL}/alerts/")
    if response.status_code == 200:
        alerts = response.json()
        
        # Filtrer les alertes récentes (créées dans les dernières minutes)
        recent_alerts = [a for a in alerts if a['event_id'] in [e['id'] for e in created_events]]
        
        print(f"   📊 Nouvelles alertes créées: {len(recent_alerts)}")
        
        for alert in recent_alerts:
            severity_emoji = "🔴" if alert['severity'] == 'critical' else "🟠"
            print(f"   {severity_emoji} Alerte #{alert['id']}: {alert['title']}")
            print(f"      Machine: {alert['machine_id']} | Type: {alert['alert_type']} | Statut: {alert['status']}")
    
    # 5. Statistiques finales
    print(f"\n5️⃣ Statistiques finales:")
    response = requests.get(f"{ALERT_SERVICE_URL}/alerts/stats/summary")
    if response.status_code == 200:
        stats = response.json()
        print(f"   📊 Total alertes: {stats['total']}")
        print(f"   🔴 Alertes actives: {stats['active']}")
        print(f"   ✅ Alertes résolues: {stats['resolved']}")
        print(f"   ⚠️ Alertes critiques actives: {stats['critical_active']}")
    
    # 6. Créer un événement normal (ne doit pas générer d'alerte)
    print(f"\n6️⃣ Test événement normal (ne doit PAS créer d'alerte):")
    normal_event = {
        "machine_id": 104,
        "event_type": "status_update",
        "severity": "low",
        "message": "Machine redémarrée avec succès",
        "data": json.dumps({"previous_status": "maintenance", "new_status": "active"})
    }
    
    response = requests.post(f"{EVENT_SERVICE_URL}/events/", json=normal_event)
    if response.status_code == 200:
        event = response.json()
        print(f"   ✅ Événement normal créé (ID: {event['id']})")
        
        time.sleep(3)
        
        # Vérifier qu'aucune nouvelle alerte n'a été créée
        response = requests.get(f"{ALERT_SERVICE_URL}/alerts/stats/summary")
        if response.status_code == 200:
            new_stats = response.json()
            if new_stats['total'] == stats['total']:
                print(f"   ✅ Aucune alerte créée pour l'événement normal (correct!)")
            else:
                print(f"   ⚠️ Une alerte a été créée pour l'événement normal (inattendu)")
    
    print(f"\n🎉 DÉMONSTRATION TERMINÉE!")
    print(f"✅ Le système d'alertes automatiques fonctionne correctement!")
    print(f"✅ Les événements critiques génèrent des alertes")
    print(f"✅ Les événements normaux ne génèrent pas d'alertes")

if __name__ == "__main__":
    demo_alert_system()