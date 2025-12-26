#!/bin/bash
set -e

# Gameplay process - handles game APIs only (no registration, no bot)
# This process is isolated from registration traffic

echo "[$(date)] Starting Gameplay API server (Gunicorn + Uvicorn)..."

# Start Gunicorn with Uvicorn workers for ASGI support
# 2 workers for 1GB RAM (can scale up if needed)
exec gunicorn bingo.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --workers 2 \
    --worker-connections 1000 \
    --timeout 30 \
    --keep-alive 5 \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

