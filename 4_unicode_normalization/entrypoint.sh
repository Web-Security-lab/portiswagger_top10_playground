#!/bin/bash
set -e

echo "[*] Polylot Notes starting..."
echo "[*] Waiting for database and seeding initial data..."

python /app/scripts/wait_and_seed.py

echo "[*] Launching Gunicorn on 0.0.0.0:8004 ..."
exec gunicorn \
    --bind 0.0.0.0:8004 \
    --workers 4 \
    --timeout 30 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "app.app:create_app()"
