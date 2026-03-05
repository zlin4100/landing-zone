#!/usr/bin/env bash
# ============================================================
# Initialize database: run all DDL scripts, seed data, and stored procedures
# Usage: bash db/init.sh [-h host] [-u user] [-p password]
# ============================================================
set -euo pipefail

HOST="${1:-localhost}"
USER="${2:-root}"
PASS="${3:-}"

MYSQL_CMD="mysql -h $HOST -u $USER"
[ -n "$PASS" ] && MYSQL_CMD="$MYSQL_CMD -p$PASS"

echo "=== Creating database ==="
$MYSQL_CMD < db/ddl/00_create_database.sql

echo "=== Creating tables (Layer 0 -> Layer 1 -> Layer 2) ==="
for f in db/ddl/0{1,2,3,4,5,6,7,8,9}_*.sql; do
    echo "  Running $f ..."
    $MYSQL_CMD < "$f"
done

echo "=== Loading seed data ==="
$MYSQL_CMD < db/seed/indicator_catalog_seed.sql

echo "=== Creating stored procedures ==="
$MYSQL_CMD < db/procedures/proc_build_monthly_snapshot.sql

echo "=== Done! Database robo_advisor initialized. ==="
