#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
export POSTGRES_USER="${POSTGRES_USER:-postgres}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-WinSer2016}"
export POSTGRES_DB="${POSTGRES_DB:-aviasales}"
export PGCLIENTENCODING=utf8

[ -d .venv ] && . .venv/bin/activate || true
pip install -q -r requirements.txt
python run.py
