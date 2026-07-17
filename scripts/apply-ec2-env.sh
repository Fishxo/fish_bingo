#!/usr/bin/env bash
# Apply production env keys from .env.example onto an existing backend/.env (EC2).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/backend/.env"
EXAMPLE="$ROOT/backend/.env.example"
VALUE="http://16.16.200.57"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Creating $ENV_FILE from .env.example (edit secrets before restarting services)."
  cp "$EXAMPLE" "$ENV_FILE"
  exit 0
fi

if grep -q '^TELEGRAM_WEB_APP_URL=' "$ENV_FILE"; then
  sed -i "s|^TELEGRAM_WEB_APP_URL=.*|TELEGRAM_WEB_APP_URL=${VALUE}|" "$ENV_FILE"
else
  echo "TELEGRAM_WEB_APP_URL=${VALUE}" >> "$ENV_FILE"
fi

# Remove mistaken legacy key if present (Django reads TELEGRAM_WEB_APP_URL)
sed -i '/^TELEGRAM_WEB_URL=/d' "$ENV_FILE" || true

echo "Updated TELEGRAM_WEB_APP_URL=${VALUE} in $ENV_FILE"
echo "Restart: sudo systemctl restart bingo-gunicorn bingo-telegram-bot celery"
