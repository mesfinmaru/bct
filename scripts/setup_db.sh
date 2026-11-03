#!/usr/bin/env bash
# PostgreSQL setup script for the ETL assignment.
# Usage: bash scripts/setup_db.sh
# Requires the postgres client (psql) on PATH and write access on the server.

set -euo pipefail

SERVER="localhost"
PORT="5432"
DB_NAME="etl_db"
DB_USER="postgres"
DB_PASSWORD="${DB_PASSWORD:-}"

if [[ -z "$DB_PASSWORD" ]]; then
  echo "DB_PASSWORD is not set. Export it before running." >&2
  exit 1
fi

drop_db() {
  PGPASSWORD="$DB_PASSWORD" psql -h "$SERVER" -p "$PORT" -U "$DB_USER" -d postgres \
    -v ON_ERROR_STOP=1 -c "DROP TABLE IF EXISTS bank_transactions CASCADE;" \
    >/dev/null 2>&1 || true
}

create_db() {
  PGPASSWORD="$DB_PASSWORD" psql -h "$SERVER" -p "$PORT" -U "$DB_USER" -d postgres \
    -v ON_ERROR_STOP=1 -c "CREATE DATABASE $DB_NAME WITH TEMPLATE template0 ENCODING 'UTF-8';"
}

drop_db
create_db

psql -h "$SERVER" -p "$PORT" -U "$DB_USER" -d "$DB_NAME" \
  -v ON_ERROR_STOP=1 -f "$(dirname "$0")/../database/schema.sql"
