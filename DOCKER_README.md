# 🐳 Docker Quick Start

## One-Command Deployment

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 2. Start everything
./docker-manage.sh start
```

## Services

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| Dashboard | 8501 | http://localhost:8501 | Production Control Interface |
| ML Core | 8000 | http://localhost:8000 | Machine Learning API |
| Meta Ads | 8002 | http://localhost:8002 | Campaign Management |
| PostgreSQL | 5432 | localhost:5432 | Database |
| Redis | 6379 | localhost:6379 | Cache & Queue |

## Quick Commands

```bash
# Start services
./docker-manage.sh start

# Stop services
./docker-manage.sh stop

# View logs
./docker-manage.sh logs

# Health check
./docker-manage.sh health

# Backup data
./docker-manage.sh backup

# Full documentation
cat DOCKER_DEPLOYMENT.md
```

## Requirements

- Docker 20.10+
- Docker Compose 1.29+
- 4GB RAM minimum
- 10GB disk space

## Production Checklist

- [ ] Change all passwords in .env
- [ ] Set `DUMMY_MODE=false`
- [ ] Configure SSL certificates
- [ ] Set up automated backups
- [ ] Configure firewall rules
- [ ] Enable monitoring

## Support

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for complete documentation.
