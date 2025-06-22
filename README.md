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

#### Manual Deployment
Build the image:
```bash
docker build -t contabo-snapshot-manager .
```

Run with environment variables:
```bash
docker run -d \
  --env-file .env \
  --name contabo-snapshots \
  contabo-snapshot-manager
```

#### Webhook-Based Deployment
For automated deployments via git webhooks:

1. **Set environment variables in your deployment platform:**
   - GitHub Actions: Use repository secrets
   - GitLab CI: Use CI/CD variables
   - Docker Hub: Use build arguments (for non-sensitive data)
   - CapRover: Use app secrets

2. **Example GitHub Actions workflow:**
```yaml
name: Deploy to Server
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v0.1.4
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.KEY }}
          script: |
            cd /path/to/app
            git pull
            docker build -t contabo-snapshot-manager .
            docker stop contabo-snapshots || true
            docker rm contabo-snapshots || true
            docker run -d \
              -e CLIENT_ID="${{ secrets.CLIENT_ID }}" \
              -e API_USER="${{ secrets.API_USER }}" \
              -e API_PASSWORD="${{ secrets.API_PASSWORD }}" \
              -e CLIENT_SECRET="${{ secrets.CLIENT_SECRET }}" \
              -e ADMIN_EMAIL="${{ secrets.ADMIN_EMAIL }}" \
              -e EMAIL_FROM="${{ secrets.EMAIL_FROM }}" \
              -e SMTP_SERVER="${{ secrets.SMTP_SERVER }}" \
              -e SMTP_PORT="${{ secrets.SMTP_PORT }}" \
              -e SMTP_USERNAME="${{ secrets.SMTP_USERNAME }}" \
              -e SMTP_PASSWORD="${{ secrets.SMTP_PASSWORD }}" \
              --name contabo-snapshots \
              contabo-snapshot-manager
```

3. **Example CapRover deployment:**
```json
{
  "appName": "contabo-snapshots",
  "imageName": "your-registry/contabo-snapshot-manager",
  "envVars": [
    {
      "key": "CLIENT_ID",
      "value": "your_client_id"
    },
    {
      "key": "API_USER", 
      "value": "your_api_user"
    }
    // ... other environment variables
  ]
}
```

## Security Best Practices

1. **Never commit `.env` files** - They're already in `.gitignore`
2. **Use secrets management** in production (Docker secrets, Kubernetes secrets, etc.)
3. **Rotate credentials regularly**
4. **Use least privilege API keys**
5. **Monitor logs for suspicious activity**
6. **For webhook deployments:**
   - Store secrets in your deployment platform's secret management
   - Never expose secrets in build logs
   - Use encrypted secrets when possible
   - Rotate deployment keys regularly

## Features

- Automated snapshot creation every 2 minutes
- Automatic cleanup of old snapshots when limit is reached
- Email reporting with detailed summaries
- Asia/Manila timezone support
- Comprehensive logging with rotation
- Docker containerization

## License

GNU General Public License (GPL) v3.0