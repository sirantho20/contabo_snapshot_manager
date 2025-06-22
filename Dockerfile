FROM python:3.9-slim

# Install cron and sudo
RUN apt-get update && apt-get install -y cron sudo tzdata

# Set timezone to Asia/Manila
ENV TZ=Asia/Manila
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY lib.py .
COPY main_job.py .
COPY templates/ templates/

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/templates/email && \
    chmod 755 /app/logs /app/templates/email

# Create cron job with environment variables (as root)
# RUN echo "0 */12 * * * cd /app && python main_job.py >> /app/logs/cron.log 2>&1" > /etc/cron.d/snapshot-cron && \
RUN echo "*/2 * * * * cd /app && python main_job.py 2>&1" > /etc/cron.d/snapshot-cron && \
    chmod 0644 /etc/cron.d/snapshot-cron

# Create a non-root user and configure sudo
RUN useradd -m appuser && \
    echo "appuser ALL=(ALL) NOPASSWD: /usr/sbin/service cron start" >> /etc/sudoers && \
    echo "appuser ALL=(ALL) NOPASSWD: /usr/sbin/cron" >> /etc/sudoers && \
    chown -R appuser:appuser /app && \
    mkdir -p /var/run && \
    chown appuser:appuser /var/run
USER appuser

# Set up volume for logs
VOLUME ["/app/logs"]

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Create entrypoint script that ensures environment is loaded
RUN echo '#!/bin/sh\n\
# Ensure logs directory exists and has proper permissions\n\
mkdir -p /app/logs\n\
chmod 755 /app/logs\n\
\n\
# Create log file if it doesnt exist\n\
touch /app/logs/contabo_snapshot_manager.log\n\
\n\
# Set Python to run unbuffered\n\
export PYTHONUNBUFFERED=1\n\
export TZ=Asia/Manila\n\
\n\
# Start cron with stdout logging and tail the log file\n\
exec tail -f /app/logs/contabo_snapshot_manager.log & sudo cron -f' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# run main_job.py once to ensure the script is working

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
RUN python main_job.py
