@echo off
echo ========================================
echo    Checking Service Logs
echo ========================================

echo.
echo 1. Alert Service Logs (last 20 lines):
echo ----------------------------------------
docker-compose logs --tail=20 alert-service

echo.
echo 2. Event Service Logs (last 20 lines):
echo ----------------------------------------
docker-compose logs --tail=20 event-service

echo.
echo 3. Kafka Logs (last 10 lines):
echo ----------------------------------------
docker-compose logs --tail=10 kafka

echo.
echo ========================================
echo To follow logs in real-time, use:
echo docker-compose logs -f alert-service
echo docker-compose logs -f event-service
echo ========================================
pause