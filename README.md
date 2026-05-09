# 🏭 SmartFactory Monitor

Un système de monitoring intelligent pour usines connectées avec gestion automatique des alertes et maintenance prédictive.

## 📋 Description

SmartFactory Monitor est une solution complète de monitoring industriel qui permet de :
- Surveiller l'état des machines en temps réel
- Générer automatiquement des alertes en cas de problème
- Gérer les tickets de maintenance
- Analyser les performances et tendances

## 🏗️ Architecture

Le système utilise une architecture microservices avec :

### Services Backend
- **User Service** (Port 8001) - Gestion des utilisateurs et authentification
- **Machine Service** (Port 8002) - Monitoring des machines
- **Event Service** (Port 8003) - Gestion des événements système
- **Alert Service** (Port 8004) - Génération automatique d'alertes
- **Maintenance Service** (Port 8005) - Gestion des tickets de maintenance
- **Gateway** (Port 8000) - Point d'entrée unique de l'API

### Infrastructure
- **Kafka** - Messaging asynchrone entre services
- **PostgreSQL** - Base de données relationnelle
- **Docker** - Containerisation des services

### Frontend
- **Flutter Web** (Port 8080) - Interface utilisateur moderne

## 🚀 Démarrage rapide

### Prérequis
- Docker Desktop
- Docker Compose
- PostgreSQL (pour développement local)

### Installation

1. **Cloner le repository**
```bash
git clone <votre-repo-url>
cd SmartFactory-monitor
```

2. **Démarrer avec Docker**
```bash
docker-compose up -d
```

3. **Vérifier les services**
```bash
docker-compose ps
```

### URLs des services
- 🌐 **Frontend**: http://localhost:8080
- 🔗 **API Gateway**: http://localhost:8000
- 👥 **Users**: http://localhost:8001
- 🏭 **Machines**: http://localhost:8002
- 📊 **Events**: http://localhost:8003
- 🚨 **Alerts**: http://localhost:8004
- 🔧 **Maintenance**: http://localhost:8005

## 🔧 Configuration

### Variables d'environnement
Les services utilisent les variables suivantes :
- `KAFKA_BOOTSTRAP_SERVERS` - Serveurs Kafka
- `DATABASE_URL` - URL de la base de données
- `TEMPERATURE_THRESHOLD` - Seuil de température critique

### Base de données
Exécutez les scripts SQL d'initialisation :
```bash
# Créer les bases de données
psql -f create_databases.sql
psql -f init_databases.sql
```

## 📊 Fonctionnalités

### ✅ Monitoring en temps réel
- Surveillance continue des machines
- Métriques de performance
- Alertes automatiques

### ✅ Gestion des alertes
- Génération automatique basée sur des règles
- Classification par sévérité
- Workflow de résolution

### ✅ Maintenance prédictive
- Tickets de maintenance automatiques
- Planification des interventions
- Historique des réparations

### ✅ Sécurité
- Authentification JWT
- Contrôle d'accès basé sur les rôles (RBAC)
- Audit des actions

## 🧪 Tests

### Tests automatisés
```bash
# Tester le flux complet
python test_simple_flow.py

# Vérifier la connexion Kafka
python check_kafka_connection.py

# Démonstration complète
python demo_final.py
```

### Tests manuels
```bash
# Vérifier les logs
docker-compose logs -f alert-service
docker-compose logs -f event-service
```

## 📁 Structure du projet

```
SmartFactory-monitor/
├── alert_service/          # Service de gestion des alertes
├── event_service/          # Service de gestion des événements
├── gateway/               # API Gateway
├── machine_service/       # Service de monitoring des machines
├── maintenance_service/   # Service de maintenance
├── user_service/         # Service de gestion des utilisateurs
├── docker-compose.yml    # Configuration Docker
├── create_databases.sql  # Scripts de création BDD
└── README.md            # Documentation
```

## 🔄 Workflow des alertes

1. **Détection** - Les machines envoient des événements
2. **Traitement** - Le service d'événements traite et envoie à Kafka
3. **Analyse** - Le service d'alertes analyse les événements
4. **Génération** - Création automatique d'alertes si nécessaire
5. **Notification** - Envoi aux utilisateurs concernés

## 🛠️ Développement

### Démarrage en mode développement
```bash
# Démarrer les services individuellement
./start_services_local.bat
```

### Ajout de nouvelles fonctionnalités
1. Créer une nouvelle branche
2. Développer la fonctionnalité
3. Tester avec les scripts fournis
4. Créer une pull request

## 📈 Monitoring et observabilité

- Logs structurés avec emojis pour faciliter le debug
- Métriques de performance des services
- Monitoring de la santé des conteneurs

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Équipe

- **Développement Backend** - Architecture microservices
- **Développement Frontend** - Interface Flutter
- **DevOps** - Containerisation et déploiement

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation des APIs
- Vérifier les logs des services

---

⭐ **N'hésitez pas à donner une étoile si ce projet vous aide !**