@echo off
echo ========================================
echo    SmartFactory Monitor - Start & Test
echo ========================================

echo.
echo 1. Starting Docker services...
docker-compose up -d

echo.
echo 2. Waiting for services to start (30 seconds)...
timeout /t 30 /nobreak

echo.
echo 3. Checking Kafka connection...
python check_kafka_connection.py

echo.
echo 4. Testing Event -> Alert flow...
python test_event_alert_flow.py

echo.
echo 5. Services status:
docker-compose ps

echo.
echo ========================================
echo Test completed! Check the logs above.
echo ========================================
pause