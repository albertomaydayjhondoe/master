# 🐳 Docker Deployment Guide

## TikTok ML Automation System - Containerized Deployment

### 📋 Overview

This system is containerized using Docker Compose with the following services:
- **ML Core** - Machine Learning API (YOLOv8, PyTorch)
- **Dashboard** - Red Button Production Control Interface
- **Telegram Bot** - Automation and ML predictions
- **Meta Ads** - Campaign management and optimization
- **PostgreSQL** - Production database
- **Redis** - Caching and queue management
- **Nginx** - Reverse proxy and load balancer

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install Docker and Docker Compose
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your actual credentials
nano .env
```

**Important variables to configure:**
- `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_PHONE`
- `META_APP_ID`, `META_APP_SECRET`, `META_ACCESS_TOKEN`
- `DB_PASSWORD`, `REDIS_PASSWORD`
- `JWT_SECRET`, `ENCRYPTION_KEY`

### 3. Build and Start

```bash
# Build all services
docker-compose build

# Start in foreground (for testing)
docker-compose up

# Start in background (for production)
docker-compose up -d
```

### 4. Access Services

- **Dashboard:** http://localhost:8501
- **ML Core API:** http://localhost:8000
- **Meta Ads API:** http://localhost:8002
- **Database:** localhost:5432
- **Redis:** localhost:6379

---

## 📦 Service Architecture

### ML Core Service
- **Port:** 8000
- **Purpose:** Machine Learning API with YOLOv8
- **Dependencies:** PyTorch, Ultralytics, OpenCV
- **Health Check:** `curl http://localhost:8000/health`

### Dashboard Service
- **Port:** 8501
- **Purpose:** Production control interface
- **Features:** Red button, module activation, monitoring
- **Health Check:** `curl http://localhost:8501/_stcore/health`

### Telegram Bot Service
- **Purpose:** Automation and ML-powered interactions
- **Dependencies:** Telethon, ML Core API
- **Session:** Stored in `./sessions` volume

### Meta Ads Service
- **Port:** 8002
- **Purpose:** Campaign management and optimization
- **Dependencies:** Facebook Business SDK
- **Health Check:** `curl http://localhost:8002/health`

---

## 🔧 Management Commands

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d dashboard

# Scale service
docker-compose up -d --scale telegram-bot=3
```

### Stopping Services

```bash
# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop dashboard

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f dashboard

# Last 100 lines
docker-compose logs --tail=100 ml-core
```

### Executing Commands

```bash
# Access container shell
docker-compose exec dashboard bash

# Run Python command
docker-compose exec ml-core python -m pytest

# Check dependency status
docker-compose exec dashboard python -c "from config.dependency_manager import DependencyManager; DependencyManager().check_all_dependencies()"
```

---

## 🔍 Monitoring and Debugging

### Check Service Status

```bash
# List running containers
docker-compose ps

# Check resource usage
docker stats

# Inspect service
docker-compose inspect dashboard
```

### Health Checks

```bash
# All health checks
./docker/scripts/health_check.sh

# Individual services
curl http://localhost:8000/health  # ML Core
curl http://localhost:8501/_stcore/health  # Dashboard
curl http://localhost:8002/health  # Meta Ads
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec database psql -U tiktok_user -d tiktok_automation

# Backup database
docker-compose exec database pg_dump -U tiktok_user tiktok_automation > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T database psql -U tiktok_user tiktok_automation
```

### Redis Access

```bash
# Connect to Redis
docker-compose exec redis redis-cli -a ${REDIS_PASSWORD}

# Monitor commands
docker-compose exec redis redis-cli -a ${REDIS_PASSWORD} MONITOR

# Get stats
docker-compose exec redis redis-cli -a ${REDIS_PASSWORD} INFO
```

---

## 🔐 Production Deployment

### 1. Enable Production Mode

```bash
# Edit .env
DUMMY_MODE=false
```

### 2. Configure SSL (HTTPS)

```bash
# Generate SSL certificates
./docker/scripts/generate_ssl.sh

# Or use Let's Encrypt
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d
```

### 3. Security Hardening

```bash
# Change all default passwords
# Update JWT_SECRET and ENCRYPTION_KEY
# Configure firewall rules
# Enable rate limiting in nginx.conf
```

### 4. Backup Strategy

```bash
# Automated backups
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/docker/scripts/backup.sh
```

---

## 📊 Performance Optimization

### Resource Limits

Edit `docker-compose.yml` to add resource constraints:

```yaml
services:
  ml-core:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Caching

```bash
# Clear Docker build cache
docker builder prune

# Clear unused images
docker image prune -a

# Clear volumes (careful!)
docker volume prune
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs service-name

# Rebuild service
docker-compose build --no-cache service-name

# Remove and recreate
docker-compose rm service-name
docker-compose up -d service-name
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8501

# Kill process
kill -9 <PID>

# Or change port in .env
DASHBOARD_PORT=8502
```

### Volume Permission Issues

```bash
# Fix permissions
sudo chown -R $(whoami):$(whoami) ./data ./logs ./sessions

# Or run container as current user
docker-compose exec -u $(id -u):$(id -g) service-name bash
```

---

## 🔄 Updates and Maintenance

### Update Services

```bash
# Pull latest code
git pull origin main

# Rebuild services
docker-compose build

# Restart with new images
docker-compose up -d
```

### Rolling Updates

```bash
# Update one service at a time
docker-compose up -d --no-deps --build dashboard
docker-compose up -d --no-deps --build ml-core
```

### Database Migrations

```bash
# Run migrations
docker-compose exec ml-core alembic upgrade head

# Create new migration
docker-compose exec ml-core alembic revision --autogenerate -m "description"
```

---

## 📚 Additional Resources

- **Docker Compose Reference:** https://docs.docker.com/compose/
- **Streamlit in Docker:** https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker
- **Nginx Configuration:** https://nginx.org/en/docs/

---

## 🆘 Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Verify configuration: `cat .env`
3. Test connectivity: `./docker/scripts/test_connectivity.sh`
4. Review this documentation
5. Open an issue on GitHub

---

**Last updated:** $(date)
**Docker Compose version:** 3.8
**Minimum requirements:** Docker 20.10+, Docker Compose 1.29+
