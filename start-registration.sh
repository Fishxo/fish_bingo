#!/bin/bash
set -e

# Registration process - handles registration + Telegram bot
# This process handles all registration traffic and is isolated from gameplay

# Function to handle bot process with automatic restart
# Run in subshell with error handling to prevent failures from stopping main script
(
    set +e  # Don't exit on error in bot process
    while true; do
        echo "[$(date)] Starting Telegram bot..."
        python manage.py runbot 2>&1 || {
            EXIT_CODE=$?
            echo "[$(date)] Bot process exited with error code $EXIT_CODE. Restarting in 10 seconds..."
        }
        sleep 10
    done
) > /tmp/bot.log 2>&1 &

# Capture bot PID for potential cleanup (though exec will orphan it)
BOT_PID=$!
echo "[$(date)] Bot started in background (PID: $BOT_PID)"

# Give bot a moment to initialize
sleep 2 || true

# Start Gunicorn with Uvicorn workers for ASGI support
# 2 workers for 1GB RAM (registration can be CPU-intensive)
echo "[$(date)] Starting Registration API server (Gunicorn + Uvicorn)..."
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

