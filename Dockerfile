FROM python:3.9-slim

# Install supervisor and timezone data
RUN apt-get update && apt-get install -y supervisor tzdata && \
    rm -rf /var/lib/apt/lists/*

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
COPY manage.py .
COPY snapshot_manager/ snapshot_manager/
COPY snapshots/ snapshots/
COPY templates/ templates/
COPY supervisor.conf /etc/supervisor/conf.d/supervisor.conf

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/templates/email && \
    chmod 755 /app/logs /app/templates/email

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Contabo Snapshot Manager with Django Q..."\n\
echo "SMTP_SERVER: $SMTP_SERVER"\n\
echo "Running Django migrations..."\n\
cd /app && python manage.py migrate\n\
echo "Creating superuser..."\n\
cd /app && python manage.py create_superuser\n\
echo "Setting up scheduled task..."\n\
cd /app && python manage.py run_snapshot_job --schedule\n\
echo "Running initial snapshot job..."\n\
cd /app && python manage.py run_snapshot_job\n\
echo "Starting Supervisor with Django Q cluster and web server..."\n\
exec supervisord -n -c /etc/supervisor/conf.d/supervisor.conf' > /app/startup.sh && \
    chmod +x /app/startup.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=snapshot_manager.settings

# Set up volume for logs
VOLUME ["/app/logs"]

# Expose port 8000 for the Django server
EXPOSE 443,80

# Start with the startup script
CMD ["/app/startup.sh"]
