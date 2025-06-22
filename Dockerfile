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

# Create necessary directories
RUN mkdir -p /app/logs /app/templates/email

# Create cron job
RUN echo "*/2 * * * * cd /app && python main_job.py 2>&1" > /etc/cron.d/snapshot-cron && \
    chmod 0644 /etc/cron.d/snapshot-cron

# Create a non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Set up volume for logs
VOLUME ["/app/logs"]

# Start cron in foreground
CMD ["cron", "-f"]
