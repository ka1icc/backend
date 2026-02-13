@echo off
cd /d "%~dp0\.."
docker compose up -d --build
echo API: http://127.0.0.1:5000
echo Stop: docker compose down
