#!/bin/bash
set -e

# Function to log with timestamp
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S %Z")] $1"
}

# Display configuration
log "Starting Contabo Snapshot Manager with Django-Q..."
log "Configuration:"
log "  SMTP_SERVER: ${SMTP_SERVER:-not set}"
log "  TZ: ${TZ:-Asia/Manila}"
log "  LOG_MAX_MB: ${LOG_MAX_MB:-200}"
log "  LOG_BACKUP_COUNT: ${LOG_BACKUP_COUNT:-5}"

# Run Django migrations
log "Running Django migrations..."
python manage.py migrate --noinput

# Collect static files
log "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
log "Creating superuser..."
python manage.py create_superuser

# Setup django-q scheduled task
log "Setting up scheduled task (every 6 hours)..."
python manage.py setup_schedule --hours 6

# List scheduled tasks
log "Listing scheduled tasks..."
python manage.py list_schedules

# Run initial test job
log "Running initial test job..."
python manage.py run_snapshot_job --test-mode

# Start Django-Q cluster in background
log "Starting Django-Q cluster..."
python manage.py qcluster &

# Wait a moment for qcluster to start
sleep 3

# Start Django development server
log "Starting Django server on port 8000..."
exec python manage.py runserver 0.0.0.0:8000 