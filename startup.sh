#!/bin/bash
set -e

# Function to log with timestamp
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S %Z")] $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for a service to be ready
wait_for_service() {
    local service_name="$1"
    local max_attempts="${2:-30}"
    local attempt=1
    
    log "Waiting for $service_name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if command_exists "$service_name" && "$service_name" --version >/dev/null 2>&1; then
            log "$service_name is ready"
            return 0
        fi
        log "Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    log "ERROR: $service_name failed to start after $max_attempts attempts"
    return 1
}

# Display configuration
log "Starting Contabo Snapshot Manager with Cron..."
log "Configuration:"
log "  SMTP_SERVER: ${SMTP_SERVER:-not set}"
log "  TZ: ${TZ:-Asia/Manila}"
log "  CRON_SCHEDULE: ${CRON_SCHEDULE:-0 0,12 * * *}"
log "  LOG_MAX_MB: ${LOG_MAX_MB:-200}"
log "  LOG_BACKUP_COUNT: ${LOG_BACKUP_COUNT:-5}"

# Set timezone
log "Setting timezone to ${TZ:-Asia/Manila}..."
ln -snf /usr/share/zoneinfo/${TZ:-Asia/Manila} /etc/localtime
echo ${TZ:-Asia/Manila} > /etc/timezone

# Verify required commands exist
log "Verifying required commands..."
for cmd in python supervisord cron; do
    if ! command_exists "$cmd"; then
        log "ERROR: Required command '$cmd' not found"
        exit 1
    fi
done

# Verify required files exist
log "Verifying required files..."
if [ ! -f "manage.py" ]; then
    log "ERROR: manage.py file not found"
    exit 1
fi

# Create superuser if it doesn't exist
log "Creating superuser..."
python manage.py create_superuser

# Setup cron schedule
log "Setting up scheduled task..."
python manage.py run_snapshot_job --schedule

# Verify cron setup
log "Verifying cron setup..."
if crontab -l 2>/dev/null | grep -q "run_snapshot_job"; then
    log "Cron job successfully configured"
else
    log "WARNING: Cron job may not be properly configured"
fi

# Start supervisor
log "Starting supervisor..."
exec supervisord -c /etc/supervisor/conf.d/supervisor.conf 