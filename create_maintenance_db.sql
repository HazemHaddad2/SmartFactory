-- Script de création de la base de données maintenance uniquement
-- Exécuter en tant que superuser PostgreSQL (postgres)

-- Création de la base de données pour la maintenance
DROP DATABASE IF EXISTS smartfactory_maintenance;
CREATE DATABASE smartfactory_maintenance
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

COMMENT ON DATABASE smartfactory_maintenance IS 'Base de données pour la gestion des tickets de maintenance';

\echo ''
\echo '============================================================'
\echo 'BASE DE DONNÉES MAINTENANCE CRÉÉE AVEC SUCCÈS'
\echo '============================================================'
\echo ''
\echo 'Base: smartfactory_maintenance'
\echo 'Description: Tickets de maintenance'
\echo ''
\echo 'Les tables seront créées automatiquement au démarrage du service'
\echo ''
