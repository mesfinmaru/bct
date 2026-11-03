# PostgreSQL setup script for the ETL assignment.
# Run from a PowerShell with the postgres client on PATH, e.g.:
#   pwsh scripts/setup_db.ps1

$ErrorActionPreference = "Stop"

$Server   = "localhost"
$Port     = "5432"
$Database = "etl_db"
$User     = "postgres"
$Password = $env:DB_PASSWORD

if ([string]::IsNullOrWhiteSpace($Password)) {
    Write-Host "DB_PASSWORD is not set. Edit the script or export DB_PASSWORD before running." -ForegroundColor Red
    exit 1
}

$psql = Get-Command "psql" -ErrorAction Stop
$proc = Start-Process -FilePath $psql.Path -ArgumentList `
    "-h $Server -p $Port -U $User -d postgres -v ON_ERROR_STOP=1 -c `"DROP TABLE IF EXISTS bank_transactions CASCADE;"`" `
    -Wait -NoNewWindow -PassThru

if ($proc.ExitCode -ne 0) {
    Write-Host "DROP failed or database does not exist yet." -ForegroundColor Yellow
}

$proc2 = Start-Process -FilePath $psql.Path -ArgumentList `
    "-h $Server -p $Port -U $User -d postgres -v ON_ERROR_STOP=1 -c `"CREATE DATABASE etl_db WITH TEMPLATE template0 ENCODING 'UTF-8';"`" `
    -Wait -NoNewWindow -PassThru

if ($proc2.ExitCode -ne 0) {
    Write-Host "Database creation failed." -ForegroundColor Red
    exit 1
}

Write-Host "Created/confirmed database: $Database" -ForegroundColor Green

$proc3 = Start-Process -FilePath $psql.Path -ArgumentList `
    "-h $Server -p $Port -U $User -d $Database -v ON_ERROR_STOP=1 -f `"$PSScriptRoot/../database/schema.sql`"" `
    -Wait -NoNewWindow -PassThru

if ($proc3.ExitCode -ne 0) {
    Write-Host "Schema load failed." -ForegroundColor Red
    exit 1
}

Write-Host "Schema loaded (table + indexes)." -ForegroundColor Green
