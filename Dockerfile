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

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/templates/email && \
    chmod 755 /app/logs /app/templates/email

# Create a non-root user and switch to it
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# Set up volume for logs
VOLUME ["/app/logs"]

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create log directory and set it as a volume
RUN mkdir -p logs
VOLUME ["/app/logs"]

# Create cron job with environment variables
RUN echo "0 */12 * * * cd /app && python main_job.py >> /app/logs/cron.log 2>&1" > /etc/cron.d/snapshot-cron
RUN chmod 0644 /etc/cron.d/snapshot-cron

# Create empty log file
RUN touch /app/logs/contabo_snapshot_manager.log

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
# Create log file if it doesn'\''t exist\n\
touch /app/logs/contabo_snapshot_manager.log\n\
\n\
# Set Python to run unbuffered\n\
export PYTHONUNBUFFERED=1\n\
\n\
# Start tailing the log file in the background\n\
tail -f /app/logs/contabo_snapshot_manager.log &\n\
\n\
# Keep container running\n\
while true; do\n\
    sleep 1\n\
done' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 