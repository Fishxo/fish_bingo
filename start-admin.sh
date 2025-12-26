#!/bin/bash
set -e

# Admin process - handles admin dashboard only
# This process is isolated from gameplay and registration traffic

echo "[$(date)] Starting Admin API server (Gunicorn + Uvicorn)..."

# Start Gunicorn with Uvicorn workers for ASGI support
# 1 worker for admin (less traffic, more stability)
exec gunicorn bingo.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --workers 1 \
    --worker-connections 1000 \
    --timeout 60 \
    --keep-alive 5 \
    --bind 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

