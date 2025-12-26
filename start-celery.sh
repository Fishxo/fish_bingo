#!/bin/bash
set -e

# Celery process - handles background tasks only
# CRITICAL FIX: Separate queues to prevent gameplay starvation
# Gameplay tasks must never be blocked by registration/reward tasks

echo "[$(date)] Starting Celery workers with queue isolation..."

# Start Celery worker that listens to multiple queues
# Queue order matters: Celery checks queues in the order specified
# gameplay is checked first, ensuring gameplay tasks are processed before others
# Increased concurrency to 3 so gameplay can run while registration tasks process
exec celery -A bingo worker \
    --loglevel=info \
    --queues=gameplay,default,registration \
    --concurrency=3 \
    --max-tasks-per-child=50 \
    --max-memory-per-child=200000 \
    --time-limit=300 \
    --soft-time-limit=240 \
    --pool=prefork \
    --prefetch-multiplier=2

