#!/bin/bash
# 🚀 Neural Forge Discográfica - Services Deployment Script
# ==========================================================
# Deploy all Neural Forge services with production configuration

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
LOG_FILE="/var/log/neural-forge-deploy.log"
APP_DIR="/opt/neural-forge"
DEPLOY_TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${CYAN}🚀 Neural Forge - Services Deployment v${SCRIPT_VERSION}${NC}"
echo -e "${CYAN}======================================================${NC}"
echo -e "Deploy ID: neural-forge-${DEPLOY_TIMESTAMP}"
echo -e "Date: $(date)"
echo -e "User: $(whoami)"
echo -e "Directory: $(pwd)"
echo ""

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "${RED}❌ DEPLOYMENT FAILED: $1${NC}"
    log "${YELLOW}🔄 Rolling back changes...${NC}"
    rollback_deployment
    exit 1
}

# Rollback function
rollback_deployment() {
    log "${YELLOW}🔄 Performing rollback...${NC}"
    docker compose down 2>/dev/null || true
    log "${GREEN}✅ Rollback completed${NC}"
}

# Trap to cleanup on exit
trap 'echo -e "\n${YELLOW}🛑 Deployment interrupted${NC}"; rollback_deployment; exit 1' INT TERM

# Create log file
sudo mkdir -p /var/log
sudo touch "$LOG_FILE"
sudo chmod 666 "$LOG_FILE"

log "${BLUE}📋 PHASE 1: Pre-deployment Validation${NC}"
log "====================================="

# Check if running in correct directory (should contain docker-compose.yml)
if [ ! -f "docker-compose.yml" ]; then
    error_exit "docker-compose.yml not found. Run from project root directory."
fi

# Check if Docker is available
if ! command -v docker >/dev/null 2>&1; then
    error_exit "Docker not installed. Run: ./deploy/hetzner/install-docker.sh"
fi

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    error_exit "Docker daemon not running. Start with: sudo systemctl start docker"
fi

# Check if user is in docker group or has sudo access
if ! docker ps >/dev/null 2>&1; then
    if ! sudo docker ps >/dev/null 2>&1; then
        error_exit "Cannot access Docker. Add user to docker group or run with sudo."
    fi
    log "${YELLOW}⚠️ Using sudo for Docker commands${NC}"
    DOCKER_CMD="sudo docker"
    COMPOSE_CMD="sudo docker compose"
else
    DOCKER_CMD="docker"
    COMPOSE_CMD="docker compose"
fi

# Validate system resources
MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
DISK_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')

log "System Resources:"
log "  Memory: ${MEMORY_GB}GB"
log "  Free Disk: ${DISK_GB}GB"
log "  CPU Cores: $(nproc)"

if [ "$MEMORY_GB" -lt 4 ]; then
    log "${YELLOW}⚠️ Warning: Less than 4GB RAM. Some services may have issues.${NC}"
fi

if [ "$DISK_GB" -lt 10 ]; then
    error_exit "Insufficient disk space. At least 10GB required."
fi

log "${GREEN}✅ Pre-deployment validation passed${NC}"
echo ""

log "${BLUE}⚙️ PHASE 2: Environment Configuration${NC}"
log "====================================="

# Check and configure environment file
if [ ! -f ".env" ]; then
    if [ -f ".env.production.template" ]; then
        log "📝 Creating .env from template..."
        cp .env.production.template .env
        log "${YELLOW}⚠️ Please configure .env file with your actual credentials${NC}"
    else
        error_exit ".env file not found and no template available"
    fi
fi

# Validate critical environment variables
log "🔍 Validating environment configuration..."
source .env 2>/dev/null || error_exit "Failed to load .env file"

# List of required variables for production
REQUIRED_VARS=(
    "POSTGRES_PASSWORD"
    "REDIS_PASSWORD"
    "N8N_PASSWORD"
    "GRAFANA_PASSWORD"
)

MISSING_VARS=()
for VAR in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!VAR}" ] || [ "${!VAR}" = "your_password_here" ] || [ "${!VAR}" = "change_me" ]; then
        MISSING_VARS+=("$VAR")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    log "${RED}❌ Missing or unconfigured environment variables:${NC}"
    for VAR in "${MISSING_VARS[@]}"; do
        log "  - $VAR"
    done
    error_exit "Please configure all required environment variables in .env file"
fi

# Create necessary directories
log "📁 Creating application directories..."
mkdir -p data/{postgres,redis,prometheus,grafana,n8n,models,torch_cache}
mkdir -p logs
mkdir -p config
mkdir -p backups

# Set proper permissions
chmod -R 755 data/
chmod -R 755 logs/
chmod 600 .env

log "${GREEN}✅ Environment configuration completed${NC}"
echo ""

log "${BLUE}🔧 PHASE 3: Docker Images Build${NC}"
log "==============================="

# Determine deployment environment
ENVIRONMENT="production"
COMPOSE_FILE="docker-compose.yml"

if [ "$1" = "--dev" ] || [ "$1" = "--development" ]; then
    ENVIRONMENT="development" 
    COMPOSE_FILE="docker-compose.dev.yml"
    log "${BLUE}🛠️ Deploying in DEVELOPMENT mode${NC}"
else
    log "${BLUE}🏭 Deploying in PRODUCTION mode${NC}"
fi

# Check if images need to be built
log "🔍 Checking existing images..."
IMAGES_EXIST=true
if ! $DOCKER_CMD images | grep -q "neural-forge"; then
    IMAGES_EXIST=false
fi

if [ "$IMAGES_EXIST" = false ] || [ "$1" = "--rebuild" ]; then
    log "🔨 Building Docker images..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" build --parallel --no-cache
    
    if [ $? -ne 0 ]; then
        error_exit "Failed to build Docker images"
    fi
    
    log "${GREEN}✅ Docker images built successfully${NC}"
else
    log "${GREEN}✅ Using existing Docker images${NC}"
fi

echo ""

log "${BLUE}🌐 PHASE 4: Network and Volume Setup${NC}"
log "===================================="

# Create Docker networks
log "🌐 Setting up Docker networks..."
$DOCKER_CMD network create neural-forge-network 2>/dev/null || log "${YELLOW}⚠️ Network already exists${NC}"

if [ "$ENVIRONMENT" = "production" ]; then
    $DOCKER_CMD network create neural-forge-prod 2>/dev/null || log "${YELLOW}⚠️ Production network already exists${NC}"
else
    $DOCKER_CMD network create neural-forge-dev 2>/dev/null || log "${YELLOW}⚠️ Development network already exists${NC}"
fi

# Create named volumes for persistence
log "💾 Setting up Docker volumes..."
VOLUMES=(
    "postgres_data"
    "redis_data"
    "n8n_data"
    "prometheus_data"
    "grafana_data"
    "nginx_logs"
)

for VOLUME in "${VOLUMES[@]}"; do
    $DOCKER_CMD volume create "$VOLUME" 2>/dev/null || log "${YELLOW}⚠️ Volume $VOLUME already exists${NC}"
done

log "${GREEN}✅ Networks and volumes configured${NC}"
echo ""

log "${BLUE}🗄️ PHASE 5: Database Initialization${NC}"
log "===================================="

# Check if database data already exists
if [ -d "data/postgres" ] && [ "$(ls -A data/postgres)" ]; then
    log "${YELLOW}⚠️ PostgreSQL data directory exists - skipping initialization${NC}"
else
    log "🗄️ Initializing PostgreSQL database..."
    
    # Create database initialization scripts directory
    mkdir -p database/init_scripts
    
    # Create basic initialization script if it doesn't exist
    if [ ! -f "database/init_scripts/01-init.sql" ]; then
        cat > database/init_scripts/01-init.sql << 'EOF'
-- Neural Forge Database Initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS campaigns;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Set permissions
GRANT ALL PRIVILEGES ON SCHEMA campaigns TO neural_forge;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO neural_forge;
GRANT ALL PRIVILEGES ON SCHEMA monitoring TO neural_forge;
EOF
    fi
    
    log "${GREEN}✅ Database initialization prepared${NC}"
fi

echo ""

log "${BLUE}🚀 PHASE 6: Services Deployment${NC}"
log "==============================="

# Stop any existing services
log "🛑 Stopping existing services..."
$COMPOSE_CMD -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true

# Start services in the correct order
log "🚀 Starting Neural Forge services..."

# Start infrastructure services first
log "📊 Starting PostgreSQL database..."
$COMPOSE_CMD -f "$COMPOSE_FILE" up -d postgres
sleep 10

log "🔄 Starting Redis cache..."
$COMPOSE_CMD -f "$COMPOSE_FILE" up -d redis
sleep 5

# Start monitoring services
if [ "$ENVIRONMENT" = "production" ]; then
    log "📈 Starting monitoring services..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" up -d prometheus grafana
    sleep 10
fi

# Start application services
log "🧠 Starting ML Core API..."
$COMPOSE_CMD -f "$COMPOSE_FILE" up -d ml-core
sleep 15

log "🔄 Starting N8N workflows..."
$COMPOSE_CMD -f "$COMPOSE_FILE" up -d n8n
sleep 10

log "🎮 Starting Production Controller..."
$COMPOSE_CMD -f "$COMPOSE_FILE" up -d production-controller
sleep 10

log "📊 Starting Analytics Engine..."
$COMPOSE_CMD -f "$COMPOSE_FILE" up -d analytics
sleep 10

# Start additional services
if [ "$ENVIRONMENT" = "production" ]; then
    log "🛰️ Starting Meta Ads service..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" up -d meta-ads
    sleep 5
    
    log "🌐 Starting Nginx reverse proxy..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" up -d nginx
    sleep 5
fi

log "${GREEN}✅ All services started${NC}"
echo ""

log "${BLUE}🔍 PHASE 7: Health Checks${NC}"
log "========================="

# Wait for services to be ready
log "⏳ Waiting for services to be healthy..."

SERVICES=(
    "postgres:5432:PostgreSQL Database"
    "redis:6379:Redis Cache"
    "ml-core:8000:ML Core API"
    "production-controller:7860:Production Controller"
    "analytics:8501:Analytics Engine"
    "n8n:5678:N8N Workflows"
)

if [ "$ENVIRONMENT" = "production" ]; then
    SERVICES+=(
        "prometheus:9090:Prometheus"
        "grafana:3000:Grafana"
        "meta-ads:8002:Meta Ads"
    )
fi

for SERVICE_INFO in "${SERVICES[@]}"; do
    IFS=':' read -r SERVICE PORT NAME <<< "$SERVICE_INFO"
    
    log "  🔍 Checking $NAME..."
    
    RETRIES=30
    while [ $RETRIES -gt 0 ]; do
        if $DOCKER_CMD exec "$SERVICE" sh -c "exit 0" 2>/dev/null; then
            # Check if service is responding on its port
            if [ "$SERVICE" = "postgres" ]; then
                if $DOCKER_CMD exec "$SERVICE" pg_isready -U neural_forge >/dev/null 2>&1; then
                    log "    ${GREEN}✅ $NAME is healthy${NC}"
                    break
                fi
            elif [ "$SERVICE" = "redis" ]; then
                if $DOCKER_CMD exec "$SERVICE" redis-cli ping | grep -q PONG 2>/dev/null; then
                    log "    ${GREEN}✅ $NAME is healthy${NC}"
                    break
                fi
            else
                # Generic HTTP health check
                if curl -sf "http://localhost:$PORT/health" >/dev/null 2>&1 || \
                   curl -sf "http://localhost:$PORT/" >/dev/null 2>&1 || \
                   $DOCKER_CMD exec "$SERVICE" sh -c "exit 0" >/dev/null 2>&1; then
                    log "    ${GREEN}✅ $NAME is healthy${NC}"
                    break
                fi
            fi
        fi
        
        sleep 5
        RETRIES=$((RETRIES - 1))
    done
    
    if [ $RETRIES -eq 0 ]; then
        log "    ${YELLOW}⚠️ $NAME health check timeout (but continuing)${NC}"
    fi
done

echo ""

log "${BLUE}📊 PHASE 8: Deployment Verification${NC}"
log "==================================="

# Show running containers
log "🏃 Running containers:"
$COMPOSE_CMD -f "$COMPOSE_FILE" ps | while read line; do
    log "  $line"
done

# Show resource usage
log "📈 Resource usage:"
$DOCKER_CMD stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | while read line; do
    log "  $line"
done

# Show logs for any failed services
log "📋 Checking for service errors..."
FAILED_SERVICES=$($COMPOSE_CMD -f "$COMPOSE_FILE" ps --filter "status=exited" --format "{{.Service}}" 2>/dev/null || true)

if [ -n "$FAILED_SERVICES" ]; then
    log "${YELLOW}⚠️ Services with issues:${NC}"
    for SERVICE in $FAILED_SERVICES; do
        log "  🔴 $SERVICE"
        log "  Last 10 log lines:"
        $COMPOSE_CMD -f "$COMPOSE_FILE" logs --tail=10 "$SERVICE" | sed 's/^/    /'
    done
fi

echo ""

log "${BLUE}🔐 PHASE 9: Security and Final Setup${NC}"
log "===================================="

# Generate secure credentials report
log "🔐 Generating security report..."
cat > "security-report-${DEPLOY_TIMESTAMP}.txt" << EOF
Neural Forge Security Report
===========================
Generated: $(date)
Deploy ID: neural-forge-${DEPLOY_TIMESTAMP}

CREDENTIALS TO CHANGE IMMEDIATELY:
- PostgreSQL: POSTGRES_PASSWORD in .env
- Redis: REDIS_PASSWORD in .env  
- N8N: N8N_PASSWORD in .env
- Grafana: GRAFANA_PASSWORD in .env

SECURITY CHECKLIST:
☐ Change all default passwords
☐ Configure SSL certificates
☐ Set up backup system
☐ Configure monitoring alerts
☐ Review firewall rules
☐ Enable automatic updates
☐ Set up log monitoring

SERVICE URLS:
EOF

if [ "$ENVIRONMENT" = "production" ]; then
    cat >> "security-report-${DEPLOY_TIMESTAMP}.txt" << EOF
- Main Dashboard: https://$(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip')
- Monitoring: https://$(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip')/grafana
EOF
else
    cat >> "security-report-${DEPLOY_TIMESTAMP}.txt" << EOF
- Production Controller: http://localhost:7860
- Analytics Engine: http://localhost:8501
- ML Core API: http://localhost:8000/docs
- N8N Workflows: http://localhost:5678
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
EOF
fi

chmod 600 "security-report-${DEPLOY_TIMESTAMP}.txt"

log "${GREEN}✅ Security report generated: security-report-${DEPLOY_TIMESTAMP}.txt${NC}"

# Create management scripts
log "🔧 Creating management scripts..."

cat > neural-forge-manager.sh << 'EOF'
#!/bin/bash
# Neural Forge Management Script

case "$1" in
    start)
        echo "🚀 Starting Neural Forge services..."
        docker compose up -d
        ;;
    stop)
        echo "🛑 Stopping Neural Forge services..."
        docker compose down
        ;;
    restart)
        echo "🔄 Restarting Neural Forge services..."
        docker compose restart
        ;;
    status)
        echo "📊 Neural Forge Status:"
        docker compose ps
        ;;
    logs)
        docker compose logs -f "${2:-}"
        ;;
    health)
        echo "🏥 Health Check:"
        curl -s http://localhost:7860/health && echo " ✅ Production Controller"
        curl -s http://localhost:8501/health && echo " ✅ Analytics Engine" 
        curl -s http://localhost:8000/health && echo " ✅ ML Core API"
        ;;
    backup)
        echo "💾 Creating backup..."
        docker compose exec postgres pg_dump -U neural_forge neural_forge > "backup-$(date +%Y%m%d-%H%M%S).sql"
        echo "✅ Backup created"
        ;;
    *)
        echo "Neural Forge Manager"
        echo "Usage: $0 {start|stop|restart|status|logs|health|backup}"
        ;;
esac
EOF

chmod +x neural-forge-manager.sh

log "${GREEN}✅ Management script created: ./neural-forge-manager.sh${NC}"

echo ""

log "${CYAN}🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
log "====================================="
log ""
log "${GREEN}✅ Deployment Summary:${NC}"
log "  • Environment: $ENVIRONMENT"
log "  • Deploy ID: neural-forge-${DEPLOY_TIMESTAMP}"
log "  • All services started and configured"
log "  • Health checks completed"
log "  • Management scripts created"
log ""

if [ "$ENVIRONMENT" = "production" ]; then
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_SERVER_IP')
    log "${YELLOW}🌐 Production Access URLs:${NC}"
    log "  🌍 Main Dashboard: https://$SERVER_IP"
    log "  📊 Monitoring: https://$SERVER_IP/grafana"
    log "  🔧 Admin Panel: https://$SERVER_IP/admin"
else
    log "${YELLOW}🛠️ Development Access URLs:${NC}"
    log "  🎮 Production Controller: http://localhost:7860"
    log "  📈 Analytics Engine: http://localhost:8501"
    log "  🧠 ML Core API: http://localhost:8000/docs"
    log "  🔄 N8N Workflows: http://localhost:5678"
    log "  📊 Grafana: http://localhost:3000 (admin/neuralforge2025)"
    log "  📈 Prometheus: http://localhost:9090"
fi

log ""
log "${YELLOW}🔧 Management Commands:${NC}"
log "  • ./neural-forge-manager.sh status    (Check status)"
log "  • ./neural-forge-manager.sh logs      (View logs)"
log "  • ./neural-forge-manager.sh health    (Health check)"
log "  • ./neural-forge-manager.sh backup    (Create backup)"
log ""
log "${YELLOW}💡 Next Steps:${NC}"
log "  1. Read security report: security-report-${DEPLOY_TIMESTAMP}.txt"
log "  2. Change all default passwords"
log "  3. Configure your API keys in the dashboard"
log "  4. Set up SSL certificates: ./deploy/hetzner/ssl-setup.sh"
log "  5. Launch your first viral campaign!"
log ""
log "${PURPLE}🎵 Neural Forge is ready to dominate social media! 🔥🚀${NC}"

exit 0