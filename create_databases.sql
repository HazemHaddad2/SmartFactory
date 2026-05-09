-- Script de création des bases de données PostgreSQL pour SmartFactory
-- Exécuter en tant que superuser PostgreSQL (postgres)

-- ============================================================
-- CRÉATION DES BASES DE DONNÉES
-- ============================================================

-- 1. Base de données pour les utilisateurs
DROP DATABASE IF EXISTS smartfactory_users;
CREATE DATABASE smartfactory_users
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

COMMENT ON DATABASE smartfactory_users IS 'Base de données pour la gestion des utilisateurs et authentification';

-- 2. Base de données pour les machines
DROP DATABASE IF EXISTS smartfactory_machines;
CREATE DATABASE smartfactory_machines
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

COMMENT ON DATABASE smartfactory_machines IS 'Base de données pour la gestion des machines';

-- 3. Base de données pour les événements
DROP DATABASE IF EXISTS smartfactory_events;
CREATE DATABASE smartfactory_events
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

COMMENT ON DATABASE smartfactory_events IS 'Base de données pour l''historique des événements';

-- 4. Base de données pour les alertes
DROP DATABASE IF EXISTS smartfactory_alerts;
CREATE DATABASE smartfactory_alerts
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

COMMENT ON DATABASE smartfactory_alerts IS 'Base de données pour la gestion des alertes';

-- 5. Base de données pour la maintenance (NOUVEAU)
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

-- ============================================================
-- AFFICHAGE DES BASES CRÉÉES
-- ============================================================

\echo ''
\echo '============================================================'
\echo 'BASES DE DONNÉES CRÉÉES AVEC SUCCÈS'
\echo '============================================================'
\echo ''
\echo '1. smartfactory_users       - Utilisateurs et authentification'
\echo '2. smartfactory_machines    - Gestion des machines'
\echo '3. smartfactory_events      - Historique des événements'
\echo '4. smartfactory_alerts      - Gestion des alertes'
\echo '5. smartfactory_maintenance - Tickets de maintenance (NOUVEAU)'
\echo ''
\echo '============================================================'
\echo ''

-- Liste des bases de données SmartFactory
SELECT datname, pg_size_pretty(pg_database_size(datname)) AS size
FROM pg_database
WHERE datname LIKE 'smartfactory_%'
ORDER BY datname;
