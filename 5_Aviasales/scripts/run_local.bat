@echo off
REM Local launch (PostgreSQL must be running)
cd /d "%~dp0\.."

if not defined POSTGRES_HOST set POSTGRES_HOST=localhost
if not defined POSTGRES_PORT set POSTGRES_PORT=5432
if not defined POSTGRES_USER set POSTGRES_USER=postgres
if not defined POSTGRES_PASSWORD set POSTGRES_PASSWORD=WinSer2016
if not defined POSTGRES_DB set POSTGRES_DB=aviasales
set PGCLIENTENCODING=utf8

if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
pip install -q -r requirements.txt 2>nul
python run.py
