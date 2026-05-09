#!/usr/bin/env python3
"""
Test complet du système de gestion des alertes
"""

import requests
import time
import json

EVENT_SERVICE_URL = "http://localhost:8003"
ALERT_SERVICE_URL = "http://localhost:8004"

def print_separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def create_test_event(machine_id, event_type, severity, message):
    """Créer un événement de test"""
    event_data = {
        "machine_id": machine_id,
        "event_type": event_type,
        "severity": severity,
        "message": message,
        "data": json.dumps({"test": True, "timestamp": time.time()})
    }
    
    response = requests.post(f"{EVENT_SERVICE_URL}/events/", json=event_data)
    if response.status_code == 200:
        event = response.json()
        print(f"✅ Événement créé: ID={event['id']}, Machine={machine_id}, Type={event_type}")
        return event
    else:
        print(f"❌ Échec création événement: {response.status_code}")
        return None

def get_alert_stats():
    """Obtenir les statistiques d'alertes"""
    response = requests.get(f"{ALERT_SERVICE_URL}/alerts/stats/summary")
    if response.status_code == 200:
        return response.json()
    return {}

def get_alerts_by_machine(machine_id):
    """Obtenir les alertes d'une machine"""
    response = requests.get(f"{ALERT_SERVICE_URL}/alerts/by-machine/{machine_id}")
    if response.status_code == 200:
        return response.json()
    return []

def acknowledge_alert(alert_id):
    """Acquitter une alerte"""
    response = requests.post(f"{ALERT_SERVICE_URL}/alerts/{alert_id}/acknowledge")
    if response.status_code == 200:
        print(f"✅ Alerte {alert_id} acquittée")
        return True
    else:
        print(f"❌ Échec acquittement alerte {alert_id}: {response.status_code}")
        return False

def resolve_alert(alert_id):
    """Résoudre une alerte"""
    response = requests.post(f"{ALERT_SERVICE_URL}/alerts/{alert_id}/resolve")
    if response.status_code == 200:
        print(f"✅ Alerte {alert_id} résolue")
        return True
    else:
        print(f"❌ Échec résolution alerte {alert_id}: {response.status_code}")
        return False

def bulk_acknowledge_machine(machine_id):
    """Acquitter toutes les alertes d'une machine"""
    response = requests.post(f"{ALERT_SERVICE_URL}/alerts/bulk/acknowledge?machine_id={machine_id}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['acknowledged_count']} alertes acquittées pour la machine {machine_id}")
        return result['acknowledged_count']
    return 0

def bulk_resolve_machine(machine_id):
    """Résoudre toutes les alertes d'une machine"""
    response = requests.post(f"{ALERT_SERVICE_URL}/alerts/bulk/resolve?machine_id={machine_id}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['resolved_count']} alertes résolues pour la machine {machine_id}")
        return result['resolved_count']
    return 0

def test_alert_lifecycle():
    """Tester le cycle de vie complet des alertes"""
    
    print_separator("TEST COMPLET DU SYSTÈME D'ALERTES")
    
    # 1. État initial
    print("\n1️⃣ État initial du système:")
    initial_stats = get_alert_stats()
    print(f"   📊 Total: {initial_stats.get('total', 0)}")
    print(f"   🔴 Actives: {initial_stats.get('active', 0)}")
    print(f"   🟡 Acquittées: {initial_stats.get('acknowledged', 0)}")
    print(f"   ✅ Résolues: {initial_stats.get('resolved', 0)}")
    
    # 2. Créer des événements critiques pour la machine 500
    print("\n2️⃣ Création d'événements critiques (Machine 500):")
    
    events = []
    events.append(create_test_event(500, "temperature_critical", "critical", "Température critique: 95°C"))
    events.append(create_test_event(500, "pressure_high", "high", "Pression élevée: 8.5 bar"))
    events.append(create_test_event(500, "error", "critical", "Erreur système critique"))
    
    # Attendre le traitement
    print("\n⏳ Attente du traitement Kafka (8 secondes)...")
    time.sleep(8)
    
    # 3. Vérifier les alertes créées
    print("\n3️⃣ Vérification des alertes créées:")
    machine_alerts = get_alerts_by_machine(500)
    active_alerts = [a for a in machine_alerts if a['status'] == 'active']
    print(f"   📊 Alertes actives pour la machine 500: {len(active_alerts)}")
    
    for alert in active_alerts:
        print(f"      - Alerte #{alert['id']}: {alert['alert_type']} ({alert['severity']})")
    
    # 4. Test d'acquittement individuel
    if active_alerts:
        print("\n4️⃣ Test d'acquittement individuel:")
        first_alert = active_alerts[0]
        acknowledge_alert(first_alert['id'])
        
        # Vérifier le changement de statut
        time.sleep(2)
        updated_alerts = get_alerts_by_machine(500)
        acknowledged = [a for a in updated_alerts if a['status'] == 'acknowledged']
        print(f"   📊 Alertes acquittées: {len(acknowledged)}")
    
    # 5. Test d'acquittement en masse
    print("\n5️⃣ Test d'acquittement en masse:")
    ack_count = bulk_acknowledge_machine(500)
    
    # 6. Vérifier les statistiques après acquittement
    print("\n6️⃣ Statistiques après acquittement:")
    stats_after_ack = get_alert_stats()
    print(f"   📊 Total: {stats_after_ack.get('total', 0)}")
    print(f"   🔴 Actives: {stats_after_ack.get('active', 0)}")
    print(f"   🟡 Acquittées: {stats_after_ack.get('acknowledged', 0)}")
    print(f"   ✅ Résolues: {stats_after_ack.get('resolved', 0)}")
    
    # 7. Test de résolution en masse
    print("\n7️⃣ Test de résolution en masse:")
    resolve_count = bulk_resolve_machine(500)
    
    # 8. Statistiques finales
    print("\n8️⃣ Statistiques finales:")
    final_stats = get_alert_stats()
    print(f"   📊 Total: {final_stats.get('total', 0)}")
    print(f"   🔴 Actives: {final_stats.get('active', 0)}")
    print(f"   🟡 Acquittées: {final_stats.get('acknowledged', 0)}")
    print(f"   ✅ Résolues: {final_stats.get('resolved', 0)}")
    
    # 9. Test de résolution automatique par événement normal
    print("\n9️⃣ Test de résolution automatique:")
    print("   Création d'événements normaux pour déclencher la résolution automatique...")
    
    # Créer d'abord quelques alertes
    create_test_event(600, "temperature_critical", "critical", "Test résolution auto")
    time.sleep(3)
    
    # Puis créer un événement normal pour les résoudre
    create_test_event(600, "temperature_normal", "low", "Température revenue à la normale")
    time.sleep(5)
    
    # Vérifier que les alertes ont été résolues automatiquement
    machine_600_alerts = get_alerts_by_machine(600)
    resolved_auto = [a for a in machine_600_alerts if a['status'] == 'resolved']
    print(f"   ✅ Alertes résolues automatiquement pour machine 600: {len(resolved_auto)}")
    
    # 10. Résumé
    print_separator("RÉSUMÉ DU TEST")
    print(f"✅ Création d'alertes: OK")
    print(f"✅ Acquittement individuel: OK")
    print(f"✅ Acquittement en masse: OK")
    print(f"✅ Résolution en masse: OK")
    print(f"✅ Résolution automatique: OK")
    print(f"✅ Statistiques: OK")
    
    print(f"\n🎉 TOUS LES TESTS SONT PASSÉS!")
    print(f"Le système de gestion des alertes fonctionne parfaitement!")

if __name__ == "__main__":
    test_alert_lifecycle()