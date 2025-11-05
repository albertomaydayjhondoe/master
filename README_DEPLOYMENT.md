# 🚀 Neural Forge - Production Deployment Package

## Quick Start

### 1. Clone this deployment branch:
```bash
git clone -b deployment/hetzner-production https://github.com/tu-usuario/neural-forge.git
cd neural-forge
```

### 2. Configure environment:
```bash
cp .env.production.template .env.production
nano .env.production  # Edit with your values
```

### 3. Deploy to Hetzner VPS:
```bash
# One-command deployment
make deploy-production

# Or step by step
./deploy/hetzner/setup-vps.sh
./deploy/hetzner/install-docker.sh
./deploy/hetzner/deploy-services.sh
./deploy/hetzner/ssl-setup.sh
./deploy/hetzner/monitoring-setup.sh
```

## Documentation

- 📖 **Complete Guide:** [docs/DEPLOYMENT_HETZNER_AIM_BY_AIM.md](docs/DEPLOYMENT_HETZNER_AIM_BY_AIM.md)
- ⚡ **Quick Start:** [docs/QUICK_START_EXPRESS.md](docs/QUICK_START_EXPRESS.md)
- 🔧 **Operations:** Use `./operations.sh help`

## Support

- 🆘 **Troubleshooting:** Check logs with `./operations.sh logs`
- 📊 **Monitoring:** Access Grafana at `https://your-domain.com/grafana`
- 🔍 **Health Check:** Run `./operations.sh health`

## Structure

This deployment package includes:
- 🐳 **Docker infrastructure** (9 services)
- 🏗️ **Hetzner deployment scripts** (5 automated scripts)
- 🔒 **SSL configuration** (Let's Encrypt automation)
- 📊 **Monitoring stack** (Prometheus + Grafana)
- 🔧 **Operations tools** (Management and health check scripts)

Version: Neural Forge v3.0 Production Ready
