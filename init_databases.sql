-- Script d'initialisation des bases de données PostgreSQL
-- Exécutez ce script avec: psql -U postgres -f init_databases.sql

-- Créer les bases de données
CREATE DATABASE smartfactory_users;
CREATE DATABASE smartfactory_machines;
CREATE DATABASE smartfactory_events;
CREATE DATABASE smartfactory_alerts;

-- Afficher les bases de données créées
\l

-- Message de confirmation
\echo 'Bases de données créées avec succès!'
\echo 'Utilisateur par défaut: postgres'
\echo 'Mot de passe: postgres'
\echo 'Host: localhost'
\echo 'Port: 5432'
