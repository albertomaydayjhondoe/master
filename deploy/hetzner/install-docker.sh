#!/bin/bash
# 🐳 Neural Forge Discográfica - Docker Installation Script
# ==========================================================
# Install Docker and Docker Compose optimized for Hetzner VPS

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_VERSION="3.0"
LOG_FILE="/var/log/neural-forge-docker.log"
DOCKER_COMPOSE_VERSION="v2.23.0"

echo -e "${CYAN}🐳 Neural Forge - Docker Installation v${SCRIPT_VERSION}${NC}"
echo -e "${CYAN}===================================================${NC}"
echo -e "Date: $(date)"
echo -e "User: $(whoami)"
echo ""

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "${RED}❌ ERROR: $1${NC}"
    exit 1
}

# Create log file (if doesn't exist)
sudo mkdir -p /var/log
sudo touch "$LOG_FILE"
sudo chmod 666 "$LOG_FILE"

log "${BLUE}📋 PHASE 1: Pre-installation Checks${NC}"
log "===================================="

# Check if running as neuralforge user (recommended)
if [ "$(whoami)" != "neuralforge" ]; then
    log "${YELLOW}⚠️ Warning: Not running as 'neuralforge' user. Run: sudo su - neuralforge${NC}"
fi

# Check system requirements
MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
DISK_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')

log "System Info:"
log "  Memory: ${MEMORY_GB}GB"
log "  Free Disk: ${DISK_GB}GB"
log "  Architecture: $(uname -m)"

if [ "$MEMORY_GB" -lt 4 ]; then
    log "${YELLOW}⚠️ Warning: Less than 4GB RAM. Docker may have performance issues.${NC}"
fi

if [ "$DISK_GB" -lt 20 ]; then
    error_exit "Insufficient disk space. At least 20GB required."
fi

# Check if Docker is already installed
if command -v docker >/dev/null 2>&1; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    log "${YELLOW}⚠️ Docker already installed (version: $DOCKER_VERSION)${NC}"
    log "Continuing with configuration verification..."
else
    log "${GREEN}✅ Docker not found - proceeding with installation${NC}"
fi

echo ""

log "${BLUE}📦 PHASE 2: Docker Installation${NC}"
log "==============================="

if ! command -v docker >/dev/null 2>&1; then
    log "🐳 Installing Docker..."
    
    # Update package index
    sudo apt-get update -qq
    
    # Install prerequisites
    sudo apt-get install -y -qq \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    log "🔑 Adding Docker GPG key..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    log "📁 Adding Docker repository..."
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update package index with Docker repository
    sudo apt-get update -qq
    
    # Install Docker Engine
    log "⬇️ Installing Docker Engine..."
    sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin
    
    log "${GREEN}✅ Docker Engine installed successfully${NC}"
else
    log "${GREEN}✅ Docker Engine already available${NC}"
fi

# Add current user to docker group
log "👤 Adding user to docker group..."
if groups | grep -q docker; then
    log "${GREEN}✅ User already in docker group${NC}"
else
    sudo usermod -aG docker $(whoami)
    log "${YELLOW}⚠️ Added to docker group. Please logout and login again, or run: newgrp docker${NC}"
fi

echo ""

log "${BLUE}🔧 PHASE 3: Docker Compose Installation${NC}"
log "======================================="

# Check if Docker Compose is available (Docker Desktop or standalone)
if docker compose version >/dev/null 2>&1; then
    COMPOSE_VERSION=$(docker compose version --short)
    log "${GREEN}✅ Docker Compose already available (version: $COMPOSE_VERSION)${NC}"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
    log "${GREEN}✅ Docker Compose (standalone) available (version: $COMPOSE_VERSION)${NC}"
else
    log "⬇️ Installing Docker Compose..."
    
    # Install Docker Compose standalone
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Create symlink for 'docker compose' command
    sudo ln -sf /usr/local/bin/docker-compose /usr/local/bin/docker-compose
    
    log "${GREEN}✅ Docker Compose installed successfully${NC}"
fi

echo ""

log "${BLUE}⚙️ PHASE 4: Docker Configuration${NC}"
log "=================================="

# Configure Docker daemon for production
log "⚙️ Configuring Docker daemon..."
sudo mkdir -p /etc/docker

cat | sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "dns": ["8.8.8.8", "8.8.4.4"],
  "default-runtime": "runc",
  "runtimes": {
    "runc": {
      "path": "runc"
    }
  },
  "exec-opts": ["native.cgroupdriver=systemd"],
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": false
}
EOF

# Configure Docker service
log "🔄 Configuring Docker service..."
sudo systemctl enable docker
sudo systemctl enable containerd

# Start Docker service
log "🚀 Starting Docker service..."
sudo systemctl start docker
sudo systemctl start containerd

# Wait for Docker to be ready
log "⏳ Waiting for Docker to be ready..."
sleep 5

# Verify Docker installation
if docker info >/dev/null 2>&1; then
    log "${GREEN}✅ Docker daemon is running${NC}"
else
    error_exit "Docker daemon failed to start"
fi

echo ""

log "${BLUE}🧹 PHASE 5: Docker Optimization${NC}"
log "==============================="

# Create Docker data directory with proper permissions
log "📁 Setting up Docker data directory..."
sudo mkdir -p /var/lib/docker
sudo chmod 700 /var/lib/docker

# Configure log rotation for Docker containers
log "📝 Configuring Docker log rotation..."
cat | sudo tee /etc/logrotate.d/docker > /dev/null << 'EOF'
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=50M
    missingok
    delaycompress
    copytruncate
}
EOF

# Set up Docker cleanup cron job
log "🗑️ Setting up Docker cleanup job..."
cat | sudo tee /etc/cron.d/docker-cleanup > /dev/null << 'EOF'
# Docker cleanup - remove unused images and containers
0 2 * * * root docker system prune -f --filter until=24h
0 3 * * 0 root docker system prune -af --filter until=168h
EOF

# Configure Docker Compose for the application
log "🔧 Preparing Docker Compose environment..."
if [ ! -f .env ]; then
    if [ -f .env.production.template ]; then
        cp .env.production.template .env
        log "${YELLOW}📝 Created .env from template - please configure it${NC}"
    fi
fi

echo ""

log "${BLUE}🔍 PHASE 6: Installation Verification${NC}"
log "====================================="

# Test Docker installation
log "🧪 Testing Docker installation..."

# Check Docker version
DOCKER_VERSION=$(docker --version)
log "Docker Version: $DOCKER_VERSION"

# Check Docker Compose version
if docker compose version >/dev/null 2>&1; then
    COMPOSE_VERSION=$(docker compose version)
    log "Docker Compose Version: $COMPOSE_VERSION"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_VERSION=$(docker-compose --version)
    log "Docker Compose Version: $COMPOSE_VERSION"
fi

# Test Docker with hello-world
log "🌍 Testing Docker with hello-world..."
if docker run --rm hello-world >/dev/null 2>&1; then
    log "${GREEN}✅ Docker test successful${NC}"
else
    error_exit "Docker test failed"
fi

# Check Docker system info
log "📊 Docker system information:"
docker system df | while read line; do
    log "  $line"
done

echo ""

log "${BLUE}🚀 PHASE 7: Neural Forge Preparation${NC}"
log "==================================="

# Pull required base images
log "📦 Pre-pulling required Docker images..."
IMAGES=(
    "python:3.11-slim"
    "postgres:15-alpine"
    "redis:7-alpine"
    "nginx:alpine"
    "n8nio/n8n:latest"
    "prom/prometheus:latest"
    "grafana/grafana:latest"
)

for IMAGE in "${IMAGES[@]}"; do
    log "⬇️ Pulling $IMAGE..."
    docker pull "$IMAGE" >/dev/null 2>&1 || log "${YELLOW}⚠️ Failed to pull $IMAGE${NC}"
done

# Create Docker networks
log "🌐 Creating Docker networks..."
docker network create neural-forge-network 2>/dev/null || log "${YELLOW}⚠️ Network might already exist${NC}"

# Set up volume directories
log "📁 Setting up volume directories..."
mkdir -p data/{postgres,redis,prometheus,grafana,n8n}
chmod -R 755 data/

echo ""

log "${BLUE}📋 PHASE 8: Post-Installation Setup${NC}"
log "==================================="

# Create Docker management aliases
log "🔧 Creating Docker management aliases..."
cat >> ~/.bashrc << 'EOF'

# Neural Forge Docker aliases
alias nf-ps='docker compose ps'
alias nf-logs='docker compose logs -f'
alias nf-up='docker compose up -d'
alias nf-down='docker compose down'
alias nf-restart='docker compose restart'
alias nf-build='docker compose build --parallel'
alias nf-clean='docker system prune -f'
alias nf-status='docker stats --no-stream'
EOF

# Create quick status script
log "📊 Creating Docker status script..."
cat > ~/docker-status.sh << 'EOF'
#!/bin/bash
echo "🐳 Docker Status - $(date)"
echo "========================"
echo ""
echo "📊 System Resources:"
docker system df
echo ""
echo "🏃 Running Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "🌐 Networks:"
docker network ls
echo ""
echo "💾 Volumes:"
docker volume ls
EOF

chmod +x ~/docker-status.sh

# Create cleanup script
log "🧹 Creating cleanup script..."
cat > ~/docker-cleanup.sh << 'EOF'
#!/bin/bash
echo "🧹 Docker Cleanup - $(date)"
echo "========================="
echo ""
echo "Before cleanup:"
docker system df
echo ""
echo "Running cleanup..."
docker system prune -f
docker volume prune -f
docker network prune -f
echo ""
echo "After cleanup:"
docker system df
echo ""
echo "✅ Cleanup completed!"
EOF

chmod +x ~/docker-cleanup.sh

echo ""

log "${CYAN}🎉 DOCKER INSTALLATION COMPLETED!${NC}"
log "=================================="
log ""
log "${GREEN}✅ Installation Summary:${NC}"
log "  • Docker Engine installed and configured"
log "  • Docker Compose available"
log "  • Production optimizations applied"
log "  • Base images pre-pulled"
log "  • Management scripts created"
log ""
log "${YELLOW}📋 Available Commands:${NC}"
log "  • docker --version                 (Check Docker version)"
log "  • docker compose version           (Check Compose version)"
log "  • ./docker-status.sh               (System status)"
log "  • ./docker-cleanup.sh              (Cleanup unused resources)"
log "  • nf-up / nf-down                  (Start/stop services)"
log "  • nf-logs                          (View logs)"
log ""
log "${BLUE}📊 Current Docker Status:${NC}"
docker system df | while read line; do
    log "  $line"
done
log ""
log "${YELLOW}💡 Next Steps:${NC}"
log "  1. Configure .env file with your settings"
log "  2. Run: ./deploy/hetzner/deploy-services.sh"
log "  3. Access dashboards after deployment"
log ""
log "${PURPLE}🐳 Docker ready for Neural Forge deployment! 🚀${NC}"

exit 0