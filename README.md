# Contabo Snapshot Manager

A Python application for managing snapshots of Contabo compute instances with automated email reporting.

## Setup

### 1. Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
# Contabo API Credentials
CLIENT_ID=your_actual_client_id
API_USER=your_actual_api_user
API_PASSWORD=your_actual_api_password
CLIENT_SECRET=your_actual_client_secret

# Email Configuration
ADMIN_EMAIL=your_actual_admin_email
EMAIL_FROM=your_actual_from_email
SMTP_SERVER=your_smtp_server
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password

# Logging Configuration
LOG_MAX_MB=200
LOG_BACKUP_COUNT=5
```

### 2. Docker Deployment

#### Build the Image
```bash
docker build -t contabo-snapshot-manager .
```

#### Run with Environment Variables
```bash
docker run -d \
  -e CLIENT_ID=your_client_id \
  -e API_USER=your_api_user \
  -e API_PASSWORD=your_api_password \
  -e CLIENT_SECRET=your_client_secret \
  -e ADMIN_EMAIL=your_email \
  -e EMAIL_FROM=your_from_email \
  -e SMTP_SERVER=your_smtp_server \
  -e SMTP_PORT=587 \
  -e SMTP_USERNAME=your_smtp_username \
  -e SMTP_PASSWORD=your_smtp_password \
  --name contabo-snapshots \
  contabo-snapshot-manager
```

#### Run with .env File
```bash
docker run -d \
  --env-file .env \
  --name contabo-snapshots \
  contabo-snapshot-manager
```

## Features

- Automated snapshot creation every 12 hours
- Automatic cleanup of old snapshots when limit is reached
- Email reporting with detailed summaries
- Asia/Manila timezone support
- Comprehensive logging with rotation
- Docker containerization
- Immediate execution on container start

## Security Best Practices

1. **Never commit `.env` files** - They're already in `.gitignore`
2. **Use environment variables** at runtime with Docker `-e` flags
3. **Rotate credentials regularly**
4. **Use least privilege API keys**
5. **Monitor logs for suspicious activity**

## Container Behavior

- **Startup**: Runs the main script once immediately when container starts
- **Scheduling**: Runs every 12 hours at 00:00 and 12:00 (Asia/Manila time)
- **Logging**: All output goes to Docker logs (stdout)
- **Timezone**: All timestamps are in Asia/Manila timezone

## Monitoring

```bash
# Check container status
docker ps -a | grep contabo-snapshots

# View logs
docker logs -f contabo-snapshots

# Check container environment variables
docker exec contabo-snapshots env | grep -E "(CLIENT_ID|API_USER|SMTP_SERVER)"
```

## License

GNU General Public License (GPL) v3.0