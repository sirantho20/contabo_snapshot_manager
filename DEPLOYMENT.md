# Deployment Guide

## Webhook-Based Deployment

This guide covers deploying the Contabo Snapshot Manager using git webhooks with various platforms.

## Platform-Specific Guides

### GitHub Actions

1. **Set up repository secrets:**
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `CLIENT_ID`
     - `API_USER`
     - `API_PASSWORD`
     - `CLIENT_SECRET`
     - `ADMIN_EMAIL`
     - `EMAIL_FROM`
     - `SMTP_SERVER`
     - `SMTP_PORT`
     - `SMTP_USERNAME`
     - `SMTP_PASSWORD`
     - `HOST` (your server IP)
     - `USERNAME` (SSH username)
     - `KEY` (SSH private key)

2. **Create `.github/workflows/deploy.yml`:**
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
            cd /path/to/your/app
            git pull origin main
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
              --restart unless-stopped \
              contabo-snapshot-manager
```

### GitLab CI/CD

1. **Set up CI/CD variables:**
   - Go to your project → Settings → CI/CD → Variables
   - Add the same secrets as above (mark sensitive ones as "Protected")

2. **Create `.gitlab-ci.yml`:**
```yaml
stages:
  - deploy

deploy:
  stage: deploy
  only:
    - main
  script:
    - ssh $DEPLOY_USER@$DEPLOY_HOST << 'EOF'
        cd /path/to/your/app
        git pull origin main
        docker build -t contabo-snapshot-manager .
        docker stop contabo-snapshots || true
        docker rm contabo-snapshots || true
        docker run -d \
          -e CLIENT_ID="$CLIENT_ID" \
          -e API_USER="$API_USER" \
          -e API_PASSWORD="$API_PASSWORD" \
          -e CLIENT_SECRET="$CLIENT_SECRET" \
          -e ADMIN_EMAIL="$ADMIN_EMAIL" \
          -e EMAIL_FROM="$EMAIL_FROM" \
          -e SMTP_SERVER="$SMTP_SERVER" \
          -e SMTP_PORT="$SMTP_PORT" \
          -e SMTP_USERNAME="$SMTP_USERNAME" \
          -e SMTP_PASSWORD="$SMTP_PASSWORD" \
          --name contabo-snapshots \
          --restart unless-stopped \
          contabo-snapshot-manager
      EOF
```

### CapRover

1. **Set up app secrets:**
   - In CapRover dashboard, go to your app → App Configs → Environment Variables
   - Add all environment variables

2. **Create `captain-definition`:**
```json
{
  "schemaVersion": 2,
  "dockerfilePath": "./Dockerfile"
}
```

3. **Deploy via webhook:**
   - Push to your repository
   - CapRover will automatically build and deploy
   - Environment variables are set in the app config

### Docker Hub + Webhook

1. **Set up automated builds:**
   - Connect your repository to Docker Hub
   - Enable automated builds

2. **Create webhook script on your server:**
```bash
#!/bin/bash
# /path/to/webhook.sh
cd /path/to/your/app
docker pull your-username/contabo-snapshot-manager:latest
docker stop contabo-snapshots || true
docker rm contabo-snapshots || true
docker run -d \
  -e CLIENT_ID="$CLIENT_ID" \
  -e API_USER="$API_USER" \
  -e API_PASSWORD="$API_PASSWORD" \
  -e CLIENT_SECRET="$CLIENT_SECRET" \
  -e ADMIN_EMAIL="$ADMIN_EMAIL" \
  -e EMAIL_FROM="$EMAIL_FROM" \
  -e SMTP_SERVER="$SMTP_SERVER" \
  -e SMTP_PORT="$SMTP_PORT" \
  -e SMTP_USERNAME="$SMTP_USERNAME" \
  -e SMTP_PASSWORD="$SMTP_PASSWORD" \
  --name contabo-snapshots \
  --restart unless-stopped \
  your-username/contabo-snapshot-manager:latest
```

## Security Checklist for Webhook Deployments

- [ ] Secrets are stored in platform's secret management
- [ ] SSH keys are properly secured
- [ ] Webhook endpoints are protected
- [ ] Build logs don't expose secrets
- [ ] Deployment keys are rotated regularly
- [ ] Server access is restricted
- [ ] SSL/TLS is enabled for webhooks
- [ ] Monitoring is set up for deployments

## Troubleshooting

### Common Issues

1. **Permission denied on SSH:**
   - Check SSH key permissions (should be 600)
   - Verify public key is in `~/.ssh/authorized_keys`

2. **Docker build fails:**
   - Ensure Docker is installed on target server
   - Check if all files are present in repository

3. **Environment variables not working:**
   - Verify secrets are properly set in platform
   - Check variable names match exactly
   - Ensure secrets are not marked as "Protected" if needed

4. **Container fails to start:**
   - Check container logs: `docker logs contabo-snapshots`
   - Verify all required environment variables are set
   - Check if ports are available

### Monitoring Deployments

```bash
# Check container status
docker ps -a | grep contabo-snapshots

# View logs
docker logs -f contabo-snapshots

# Check cron logs
docker exec contabo-snapshots tail -f /app/logs/contabo_snapshot_manager.log
``` 