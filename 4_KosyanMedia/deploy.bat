@echo off
echo Building and starting containers...
docker compose up --build -d
echo.
echo When ready, open http://localhost:8000
echo To stop: docker compose down
