FROM python:3.9-slim

# Install cron and timezone data
RUN apt-get update && apt-get install -y cron tzdata && \
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
COPY main_job.py .
COPY templates/ templates/

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/templates/email && \
    chmod 755 /app/logs /app/templates/email

# Create cron job
RUN echo "*/2 * * * * cd /app && python main_job.py 2>&1" > /etc/cron.d/snapshot-cron && \
    chmod 0644 /etc/cron.d/snapshot-cron

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Contabo Snapshot Manager..."\n\
echo "Running initial snapshot job..."\n\
cd /app && python main_job.py\n\
echo "Starting cron scheduler..."\n\
exec cron -f' > /app/startup.sh && \
    chmod +x /app/startup.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set up volume for logs
VOLUME ["/app/logs"]

# Start with the startup script
CMD ["/app/startup.sh"]
