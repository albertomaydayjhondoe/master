#!/bin/bash
# 🚀 Neural Forge Discográfica - Auto Deploy Script
# =================================================
# Quick deployment script for Hetzner VPS or any Docker-compatible server

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script info
SCRIPT_VERSION="3.0"
DEPLOY_DATE=$(date +"%Y-%m-%d %H:%M:%S")

echo -e "${CYAN}🎵 Neural Forge Discográfica - Auto Deploy v${SCRIPT_VERSION}${NC}"
echo -e "${CYAN}=========================================================${NC}"
echo -e "Deploy Date: ${DEPLOY_DATE}"
echo ""

# Check if running as root (not recommended)
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}⚠️ Warning: Running as root. Consider using a non-root user.${NC}"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Docker if not present
install_docker() {
    if ! command_exists docker; then
        echo -e "${BLUE}🐳 Installing Docker...${NC}"
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        echo -e "${GREEN}✅ Docker installed successfully${NC}"
    else
        echo -e "${GREEN}✅ Docker already installed${NC}"
    fi
}

# Function to install Docker Compose if not present
install_docker_compose() {
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        echo -e "${BLUE}🔧 Installing Docker Compose...${NC}"
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        echo -e "${GREEN}✅ Docker Compose installed successfully${NC}"
    else
        echo -e "${GREEN}✅ Docker Compose already available${NC}"
    fi
}

# Function to setup environment
setup_environment() {
    echo -e "${BLUE}🌍 Setting up environment...${NC}"
    
    # Create necessary directories
    mkdir -p data/{models,torch_cache} config logs backups
    
    # Copy environment template if .env doesn't exist
    if [ ! -f .env.production ]; then
        if [ -f .env.production.template ]; then
            cp .env.production.template .env.production
            echo -e "${YELLOW}📝 Created .env.production from template${NC}"
            echo -e "${RED}⚠️ IMPORTANT: Edit .env.production with your actual credentials!${NC}"
        else
            echo -e "${RED}❌ .env.production.template not found${NC}"
            exit 1
        fi
    fi
    
    # Set permissions
    chmod 600 .env.production
    chmod +x docker/scripts/*.sh
    
    echo -e "${GREEN}✅ Environment setup completed${NC}"
}

# Function to check system requirements
check_requirements() {
    echo -e "${BLUE}🔍 Checking system requirements...${NC}"
    
    # Check available memory (should be at least 4GB for production)
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$MEMORY_GB" -lt 4 ]; then
        echo -e "${YELLOW}⚠️ Warning: Less than 4GB RAM detected (${MEMORY_GB}GB). Consider upgrading.${NC}"
    else
        echo -e "${GREEN}✅ RAM: ${MEMORY_GB}GB${NC}"
    fi
    
    # Check available disk space (should be at least 20GB)
    DISK_GB=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$DISK_GB" -lt 20 ]; then
        echo -e "${RED}❌ Warning: Less than 20GB free disk space (${DISK_GB}GB)${NC}"
    else
        echo -e "${GREEN}✅ Disk Space: ${DISK_GB}GB free${NC}"
    fi
    
    # Check if ports are available
    REQUIRED_PORTS=(80 443 7860 8501 8000 5678 3000 9090 5432 6379)
    for PORT in "${REQUIRED_PORTS[@]}"; do
        if netstat -tuln | grep -q ":${PORT} "; then
            echo -e "${YELLOW}⚠️ Port ${PORT} is already in use${NC}"
        fi
    done
    
    echo -e "${GREEN}✅ System requirements check completed${NC}"
}

# Function to configure firewall
configure_firewall() {
    echo -e "${BLUE}🔥 Configuring firewall...${NC}"
    
    if command_exists ufw; then
        # Enable UFW
        sudo ufw --force enable
        
        # Allow SSH
        sudo ufw allow ssh
        
        # Allow HTTP and HTTPS
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        
        # Allow application ports (only from localhost for security)
        sudo ufw allow from 127.0.0.1 to any port 7860
        sudo ufw allow from 127.0.0.1 to any port 8501
        sudo ufw allow from 127.0.0.1 to any port 8000
        sudo ufw allow from 127.0.0.1 to any port 5678
        sudo ufw allow from 127.0.0.1 to any port 3000
        sudo ufw allow from 127.0.0.1 to any port 9090
        
        echo -e "${GREEN}✅ Firewall configured${NC}"
    else
        echo -e "${YELLOW}⚠️ UFW not available, skipping firewall configuration${NC}"
    fi
}

# Function to start services
start_services() {
    local ENVIRONMENT=$1
    echo -e "${BLUE}🚀 Starting Neural Forge services (${ENVIRONMENT})...${NC}"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker compose -f docker-compose.prod.yml up -d
    else
        docker compose -f docker-compose.dev.yml up -d
    fi
    
    echo -e "${GREEN}✅ Services started${NC}"
}

# Function to wait for services to be ready
wait_for_services() {
    echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
    
    SERVICES=(
        "http://localhost:7860/health:Production Controller"
        "http://localhost:8501/health:Analytics Engine"
        "http://localhost:8000/health:ML Core API"
        "http://localhost:5678/healthz:N8N"
    )
    
    for SERVICE_INFO in "${SERVICES[@]}"; do
        IFS=':' read -r URL NAME <<< "$SERVICE_INFO"
        
        echo -n "  Waiting for ${NAME}..."
        
        RETRIES=30
        while [ $RETRIES -gt 0 ]; do
            if curl -s -f "$URL" >/dev/null 2>&1; then
                echo -e " ${GREEN}✅${NC}"
                break
            fi
            sleep 5
            RETRIES=$((RETRIES - 1))
            echo -n "."
        done
        
        if [ $RETRIES -eq 0 ]; then
            echo -e " ${YELLOW}⚠️ (timeout)${NC}"
        fi
    done
    
    echo -e "${GREEN}✅ Service health check completed${NC}"
}

# Function to show access information
show_access_info() {
    local ENVIRONMENT=$1
    echo ""
    echo -e "${CYAN}🎉 Neural Forge Discográfica is ready!${NC}"
    echo -e "${CYAN}====================================${NC}"
    echo ""
    
    if [ "$ENVIRONMENT" = "production" ]; then
        echo -e "${GREEN}🚀 Production Environment${NC}"
        echo -e "${YELLOW}📊 Access your system:${NC}"
        echo -e "  🌐 Main Dashboard: https://$(hostname -I | awk '{print $1}')"
        echo -e "  📈 Monitoring: https://$(hostname -I | awk '{print $1}')/grafana"
        echo -e "  🔒 Admin Panel: https://$(hostname -I | awk '{print $1}')/admin"
    else
        echo -e "${BLUE}🛠️ Development Environment${NC}"  
        echo -e "${YELLOW}📊 Access your dashboards:${NC}"
        echo -e "  🎮 Production Controller: http://localhost:7860"
        echo -e "  📈 Analytics Engine: http://localhost:8501"
        echo -e "  🧠 ML Core API: http://localhost:8000/docs"
        echo -e "  🔄 N8N Workflows: http://localhost:5678"
        echo -e "  📊 Grafana Monitoring: http://localhost:3000"
        echo -e "  📈 Prometheus Metrics: http://localhost:9090"
    fi
    
    echo ""
    echo -e "${YELLOW}🔧 Management Commands:${NC}"
    echo -e "  📋 View logs: make logs (or docker compose logs -f)"
    echo -e "  🔍 Check health: make health"
    echo -e "  🛑 Stop system: make stop"
    echo -e "  📊 View stats: make stats"
    echo ""
    echo -e "${YELLOW}💡 Next Steps:${NC}"
    echo -e "  1. Configure your API keys in the Production Controller"
    echo -e "  2. Upload your first music track"
    echo -e "  3. Launch your first viral campaign"
    echo -e "  4. Monitor results in the Analytics Engine"
    echo ""
    echo -e "${PURPLE}🎵 Ready to dominate social media! 🔥${NC}"
}

# Main deployment function
main() {
    echo -e "${BLUE}🚀 Starting deployment process...${NC}"
    echo ""
    
    # Parse command line arguments
    ENVIRONMENT="development"
    SKIP_DEPS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --production|-p)
                ENVIRONMENT="production"
                shift
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --production, -p    Deploy in production mode"
                echo "  --skip-deps        Skip dependency installation"
                echo "  --help, -h         Show this help message"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Unknown option: $1${NC}"
                exit 1
                ;;
        esac
    done
    
    echo -e "${YELLOW}📋 Deployment Configuration:${NC}"
    echo -e "  Environment: ${ENVIRONMENT}"
    echo -e "  Skip Dependencies: ${SKIP_DEPS}"
    echo ""
    
    # Step 1: Check system requirements
    check_requirements
    echo ""
    
    # Step 2: Install dependencies
    if [ "$SKIP_DEPS" = false ]; then
        install_docker
        install_docker_compose
        echo ""
    fi
    
    # Step 3: Setup environment
    setup_environment
    echo ""
    
    # Step 4: Configure firewall (production only)
    if [ "$ENVIRONMENT" = "production" ]; then
        configure_firewall
        echo ""
    fi
    
    # Step 5: Build images
    echo -e "${BLUE}🔨 Building Docker images...${NC}"
    if [ "$ENVIRONMENT" = "production" ]; then
        docker compose -f docker-compose.prod.yml build --parallel
    else
        docker compose -f docker-compose.dev.yml build --parallel
    fi
    echo -e "${GREEN}✅ Images built successfully${NC}"
    echo ""
    
    # Step 6: Start services
    start_services "$ENVIRONMENT"
    echo ""
    
    # Step 7: Wait for services
    wait_for_services
    echo ""
    
    # Step 8: Show access information
    show_access_info "$ENVIRONMENT"
}

# Trap to cleanup on exit
trap 'echo -e "\n${YELLOW}🛑 Deployment interrupted${NC}"; exit 1' INT TERM

# Run main function
main "$@"