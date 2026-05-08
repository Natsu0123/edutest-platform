@echo off
set PG_DUMP="C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"
set BACKUP_DIR=D:\edutest_backups
set DB_NAME=edutest
set DB_USER=postgres

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set TS=%%i

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

%PG_DUMP% -U %DB_USER% -F c -d %DB_NAME% -f "%BACKUP_DIR%\edutest_%TS%.backup"

pause