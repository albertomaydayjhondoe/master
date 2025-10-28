# Railway Deployment Configuration

## Environment Variables Required

### Core Application
```
ENVIRONMENT=production
DUMMY_MODE=false
CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg
PORT=8080
TZ=Europe/Madrid
PYTHONPATH=/app
```

### Meta Ads Integration (€500/month budget)
```
META_ADS_BUDGET=500
META_ACCESS_TOKEN=your_meta_token
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_secret
META_PIXEL_ID=your_pixel_id
```

### Database (Auto-provisioned by Railway)
```
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}
```

### Optional Monitoring
```
DISCORD_WEBHOOK_URL=your_discord_webhook
SENTRY_DSN=your_sentry_dsn
```

## Railway Services Setup

### 1. Main Application
- **Type**: Docker Image Deployment
- **Source**: Docker Hub (`stakasml/stakas-ml:latest`)
- **Plan**: Starter ($5/month)
- **Port**: 8080
- **Health Check**: `/health`

### 2. Redis Cache
- **Type**: Redis Add-on
- **Plan**: Redis ($5/month)
- **Version**: 7.x
- **Auto-connects**: Via `REDIS_URL`

### 3. PostgreSQL Database  
- **Type**: PostgreSQL Add-on
- **Plan**: PostgreSQL ($5/month)
- **Version**: 15.x
- **Auto-connects**: Via `DATABASE_URL`

## Deployment Process

### Method 1: GitHub Actions (Recommended)
1. Configure GitHub Secrets:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`
   - `RAILWAY_TOKEN`

2. Push to main branch:
   ```bash
   git push origin main
   ```

3. Monitor deployment in GitHub Actions

### Method 2: Manual Docker Hub
1. Build and push image:
   ```bash
   python railway_docker_manager.py
   # Select option 7: Full Pipeline
   ```

2. Create Railway project from Docker Hub image

### Method 3: Railway CLI (if available)
1. Login to Railway:
   ```bash
   railway login
   ```

2. Deploy from Dockerfile:
   ```bash
   railway up
   ```

## Post-Deployment Verification

### Health Checks
```bash
curl https://your-app.railway.app/health
curl https://your-app.railway.app/metrics
```

### Channel Analytics
```bash
curl https://your-app.railway.app/channel/UCgohgqLVu1QPdfa64Vkrgeg/stats
```

### ML Endpoints
```bash
# Screenshot analysis
curl -X POST https://your-app.railway.app/analyze_screenshot \
  -H "Content-Type: application/json" \
  -d '{"image_url": "test_screenshot.jpg"}'

# Engagement prediction
curl -X POST https://your-app.railway.app/predict_engagement \
  -H "Content-Type: application/json" \
  -d '{"video_metadata": {"title": "New Drill Track"}}'
```

## Scaling Configuration

### Auto-scaling Triggers
- CPU > 80% for 5 minutes
- Memory > 85% 
- Response time > 2 seconds
- Queue depth > 10 requests

### Resource Limits
- **CPU**: 1 vCPU (burstable to 2)
- **Memory**: 1GB RAM (burstable to 2GB)
- **Storage**: 2GB (models + logs)

## Monitoring Setup

### Metrics Dashboard
Railway provides built-in metrics for:
- CPU/Memory usage
- Request rate and latency
- Error rates
- Custom application metrics

### Alerting
Configure alerts for:
- Service downtime
- High error rates (>5%)
- Resource exhaustion
- Database connection issues

### Logs
Access logs via:
- Railway dashboard
- Railway CLI: `railway logs --follow`
- External log aggregation (optional)

## Troubleshooting

### Common Issues

**Build Failures:**
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Ensure Python 3.11 compatibility

**Runtime Errors:**
- Check environment variables
- Verify database connectivity
- Monitor memory usage
- Check port configuration

**Performance Issues:**
- Scale up resources
- Optimize Docker image size
- Enable Redis caching
- Review ML model efficiency

### Debug Commands
```bash
# Check container status
railway status

# View recent logs  
railway logs --tail 100

# Access container shell
railway shell

# Check environment variables
railway env
```

## Security Considerations

### Container Security
- Non-root user execution (stakas:1001)
- Minimal base image (Python 3.11-slim)
- No secrets in image layers
- Regular vulnerability scanning

### Network Security
- HTTPS termination by Railway
- Private database connections
- Environment-based secrets
- CORS configuration for API

### Data Protection
- Encrypted data at rest
- TLS 1.3 for data in transit
- Database backups (automated)
- GDPR-compliant data handling

## Cost Optimization

### Current Estimated Costs
- **Main App**: $5/month (Starter plan)
- **PostgreSQL**: $5/month
- **Redis**: $5/month
- **Total**: ~$15/month + usage

### Usage-based Charges
- **Bandwidth**: $0.10/GB after 100GB
- **Compute**: $0.000463/CPU-hour after included
- **Storage**: $0.25/GB/month after 1GB

### Optimization Tips
- Use Redis for caching to reduce compute
- Optimize Docker image size
- Implement efficient ML model loading
- Monitor and adjust resource limits