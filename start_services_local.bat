@echo off
echo ========================================
echo    Démarrage des services en local
echo ========================================

echo.
echo PRÉREQUIS:
echo - PostgreSQL doit être installé et démarré
echo - Kafka doit être installé et démarré
echo - Python avec les dépendances installées

echo.
echo 1. Démarrage du service utilisateurs (port 8001)...
start "User Service" cmd /k "cd user_service && python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

timeout /t 2 /nobreak

echo 2. Démarrage du service machines (port 8002)...
start "Machine Service" cmd /k "cd machine_service && python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload"

timeout /t 2 /nobreak

echo 3. Démarrage du service événements (port 8003)...
start "Event Service" cmd /k "cd event_service && python -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload"

timeout /t 2 /nobreak

echo 4. Démarrage du service alertes (port 8004)...
start "Alert Service" cmd /k "cd alert_service && python -m uvicorn main:app --host 0.0.0.0 --port 8004 --reload"

timeout /t 2 /nobreak

echo 5. Démarrage du service maintenance (port 8005)...
start "Maintenance Service" cmd /k "cd maintenance_service && python -m uvicorn main:app --host 0.0.0.0 --port 8005 --reload"

timeout /t 2 /nobreak

echo 6. Démarrage de la gateway (port 8000)...
start "Gateway" cmd /k "cd gateway && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo ========================================
echo Services démarrés en local !
echo Vérifiez que tous les services sont accessibles:
echo - http://localhost:8001 (Users)
echo - http://localhost:8002 (Machines)  
echo - http://localhost:8003 (Events)
echo - http://localhost:8004 (Alerts)
echo - http://localhost:8005 (Maintenance)
echo - http://localhost:8000 (Gateway)
echo ========================================
pause