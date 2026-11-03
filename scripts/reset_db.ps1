# One-command reset: drops the table, reloads the schema and prints the row threshold.
# Requires: postgres client on PATH + DB_PASSWORD set.
$pwd = Split-Path -Parent $MyInvocation.MyCommand.Path
$db = "etl_db"

Write-Host "==> Dropping table from $db" -ForegroundColor Yellow
$proc = Start-Process -FilePath "psql" -ArgumentList "-h localhost -p 5432 -U postgres -d $db -v ON_ERROR_STOP=1 -c `"DROP TABLE IF EXISTS bank_transactions CASCADE;`"" -Wait -NoNewWindow -PassThru
if ($proc.ExitCode -ne 0) { Write-Host "DROP failed" -ForegroundColor Red; exit 1 }

Write-Host "==> Reloading schema from database/schema.sql" -ForegroundColor Yellow
$proc2 = Start-Process -FilePath "psql" -ArgumentList "-h localhost -p 5432 -U postgres -d $db -v ON_ERROR_STOP=1 -f `"$pwd/../database/schema.sql`"" -Wait -NoNewWindow -PassThru
if ($proc2.ExitCode -ne 0) { Write-Host "Schema load failed" -ForegroundColor Red; exit 1 }

Write-Host "==> Running ETL" -ForegroundColor Yellow
& python src/pipeline.py

Write-Host "==> Final row count" -ForegroundColor Green
python - <<'PY'
import psycopg2
conn = psycopg2.connect(host="localhost", port=5432, dbname="etl_db", user="postgres", password="mes@123", connect_timeout=5)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM bank_transactions;")
print("rows:", f"{cur.fetchone()[0]:,}")
cur.execute("SELECT source_dataset, COUNT(*) FROM bank_transactions GROUP BY source_dataset;")
for r in cur.fetchall(): print(r)
cur.execute("SELECT count(*) FROM pg_indexes WHERE tablename='bank_transactions';")
print("indexes:", cur.fetchone()[0])
conn.close()
PY
