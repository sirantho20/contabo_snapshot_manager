FROM python:3.9-slim

# Install cron
RUN apt-get update && apt-get install -y cron

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY lib.py .
COPY main_job.py .
COPY templates/ templates/
COPY .env .

# Create log directory and set it as a volume
RUN mkdir -p logs
VOLUME ["/app/logs"]

# Create cron job with environment variables
RUN echo "0 */12 * * * cd /app && python main_job.py >> /app/logs/cron.log 2>&1" > /etc/cron.d/snapshot-cron
RUN chmod 0644 /etc/cron.d/snapshot-cron

# Run main_job.py once to ensure the script is working
RUN python main_job.py

# Create entrypoint script that ensures environment is loaded
RUN echo '#!/bin/sh\n\
# Start cron service\n\
service cron start\n\
\n\
# Ensure logs directory exists and has proper permissions\n\
mkdir -p /app/logs\n\
chmod 755 /app/logs\n\
\n\
# Set Python to run unbuffered\n\
export PYTHONUNBUFFERED=1\n\
\n\
# Start tailing the log file\n\
tail -f /app/logs/contabo_snapshot_manager.log' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 