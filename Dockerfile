FROM python:3.9-slim

# Install timezone data only
RUN apt-get update && apt-get install -y tzdata && \
    rm -rf /var/lib/apt/lists/*

# Set default timezone
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

# Create staticfiles directory
RUN mkdir -p staticfiles

# Create data directory for persistent database
RUN mkdir -p data

# Set proper permissions for data directory
RUN chmod 755 data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=snapshot_manager.settings

# Expose port for Django server
EXPOSE 8000

# Copy and set startup script
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# Start with the startup script
CMD ["/app/startup.sh"]
