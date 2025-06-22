# Security Guidelines

## Environment Variables Security

### ✅ What's Protected
- `.env` files are excluded from git via `.gitignore`
- Only `.env.example` template is committed
- No real credentials are stored in the repository

### 🔒 Best Practices

1. **Local Development**
   - Copy `.env.example` to `.env`
   - Fill in real values locally
   - Never commit `.env` files

2. **Production Deployment**
   - Use Docker secrets or Kubernetes secrets
   - Use environment variables at runtime
   - Never bake secrets into Docker images

3. **Webhook-Based Deployment**
   - Store secrets in platform's secret management (GitHub Secrets, GitLab Variables, etc.)
   - Use encrypted secrets when available
   - Never expose secrets in build logs or webhook payloads
   - Rotate deployment keys and SSH keys regularly
   - Use HTTPS for all webhook endpoints
   - Implement webhook signature verification when possible

4. **Credential Management**
   - Rotate API keys regularly
   - Use least privilege API keys
   - Monitor API usage for anomalies

5. **Container Security**
   - Run as non-root user (already configured)
   - Use specific image tags, not `latest`
   - Regularly update base images

### 🚨 What to Never Do
- ❌ Commit `.env` files to git
- ❌ Hardcode secrets in source code
- ❌ Use default passwords
- ❌ Share credentials in issues or discussions
- ❌ Store secrets in Docker images
- ❌ Expose secrets in webhook URLs or build logs
- ❌ Use unencrypted webhook endpoints

### 🔍 Monitoring
- Check logs for failed authentication attempts
- Monitor API usage patterns
- Set up alerts for unusual activity
- Regularly audit access logs
- Monitor webhook delivery and deployment success rates

### 🛠️ Emergency Response
If credentials are compromised:
1. Immediately rotate all API keys
2. Check for unauthorized API usage
3. Review logs for suspicious activity
4. Update all deployment environments
5. Consider revoking and regenerating all credentials
6. Rotate deployment keys and SSH keys
7. Review webhook access logs 