FROM python:3.9-slim

# Install supervisor, timezone data, and cron
RUN apt-get update && apt-get install -y supervisor tzdata cron && \
    rm -rf /var/lib/apt/lists/*

# Set default timezone (can be overridden by TZ environment variable)
ENV TZ=Asia/Manila

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY lib.py .
COPY manage.py .
COPY snapshot_manager/ snapshot_manager/
COPY snapshots/ snapshots/
COPY templates/ templates/
COPY supervisor.conf /etc/supervisor/conf.d/supervisor.conf

# Copy startup script
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/templates/email && \
    chmod 755 /app/logs /app/templates/email

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=snapshot_manager.settings

# Set up volume for logs
VOLUME ["/app/logs"]

# Expose ports for the Django server
EXPOSE 80

# Start with the startup script
CMD ["/app/startup.sh"]
