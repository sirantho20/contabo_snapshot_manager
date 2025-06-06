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

# Create log directory
RUN mkdir -p logs

# Create cron job
RUN echo "0 */12 * * * cd /app && python main_job.py >> /app/logs/cron.log 2>&1" > /etc/cron.d/snapshot-cron
RUN chmod 0644 /etc/cron.d/snapshot-cron

# Create entrypoint script
RUN echo '#!/bin/sh\nservice cron start\ntail -f /app/logs/cron.log' > /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 