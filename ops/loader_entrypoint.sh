#!/usr/bin/env bash
set -euo pipefail
cd /app/database_creation   # ensure ../data resolves to /app/data

# Expect: DB_HOST, DB_PORT from env (compose), plus values z .env:
# POSTGRES_DB_BRNO, POSTGRES_USER_BRNO, POSTGRES_PASSWORD_BRNO

echo ">>> Waiting a bit even after healthcheck..."
sleep 2

# Spusti 3 loadery. Tvoje skripty si vezmú hodnoty z .env (dotenv),
# ale potrebujú správny host/port (inside Docker sieť: brno-db:5432).
# Najjednoduchšie: exportneme ich pre skripty a v skriptoch ich načítaj cez dotenv/os.getenv.
export POSTGRES_HOST_BRNO="${DB_HOST:-brno-db}"
export POSTGRES_PORT_BRNO="${DB_PORT:-5432}"

echo ">>> Running alerts loader..."
python /app/database_creation/load_alerts_from_csv_to_db.py || exit 1

echo ">>> Running jams loader..."
python /app/database_creation/load_jams_from_csv_to_db.py || exit 1

echo ">>> Running nehody loader..."
python /app/database_creation/load_nehody_from_csv_to_db.py || exit 1

echo ">>> All loaders finished."
