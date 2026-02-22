#!/bin/bash
#
# EC2 disk cleanup + DB pruning
# Run via cron every 20 minutes
#

set -Eeuo pipefail

# -------- CONFIG --------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOG_DIR="${CLEANUP_LOG_DIR:-$PROJECT_ROOT/logs}"

LOG_MAX_AGE_DAYS="${CLEANUP_LOG_MAX_DAYS:-7}"
KEEP_DB_RECORDS="${KEEP_DB_RECORDS:-20}"

DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-bingo.settings}"

# -------- LOGGING --------
echo "========== Cleanup started at $(date) =========="

# -------- 1) CLEAN APP LOGS --------
if [ -d "$LOG_DIR" ]; then
  find "$LOG_DIR" -type f -name "*.log*" -mtime +"$LOG_MAX_AGE_DAYS" -delete || true
fi

[ -d "$BACKEND_DIR/logs" ] && \
  find "$BACKEND_DIR/logs" -type f -name "*.log*" -mtime +"$LOG_MAX_AGE_DAYS" -delete || true

[ -d "/var/log/celery" ] && \
  find /var/log/celery -type f -name "*.log*" -mtime +"$LOG_MAX_AGE_DAYS" -delete || true

# -------- 2) SYSTEMD JOURNAL (VERY IMPORTANT) --------
journalctl --vacuum-size=100M || true
journalctl --vacuum-time=7d || true

# -------- 3) DJANGO DB PRUNE --------
if [ -f "$BACKEND_DIR/manage.py" ]; then
  cd "$BACKEND_DIR"

  if [ -d "$PROJECT_ROOT/venv/bin" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
  elif [ -d "$BACKEND_DIR/venv/bin" ]; then
    source "$BACKEND_DIR/venv/bin/activate"
  fi

  export DJANGO_SETTINGS_MODULE
  python manage.py prune_old_data --keep "$KEEP_DB_RECORDS"
fi

echo "========== Cleanup finished at $(date) =========="
exit 0
