#!/bin/bash
# 🔧 Neural Forge - Operations Master Script
# ===========================================
# Central management script for all Neural Forge operations

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
APP_NAME="Neural Forge Discográfica"

echo -e "${CYAN}🔧 $APP_NAME - Operations Manager v${SCRIPT_VERSION}${NC}"
echo -e "${CYAN}=======================================================${NC}"

# Function to show help
show_help() {
    echo ""
    echo -e "${YELLOW}📋 Available Commands:${NC}"
    echo ""
    echo -e "${BLUE}🚀 DEPLOYMENT:${NC}"
    echo -e "  ${GREEN}deploy${NC}           Deploy full system to production"
    echo -e "  ${GREEN}deploy-dev${NC}       Deploy development environment"
    echo -e "  ${GREEN}setup-vps${NC}        Setup VPS (run on server)"
    echo -e "  ${GREEN}setup-ssl${NC}        Configure SSL certificates"
    echo ""
    echo -e "${BLUE}📊 MONITORING:${NC}"
    echo -e "  ${GREEN}health${NC}          Complete health check"
    echo -e "  ${GREEN}status${NC}          Quick system status"
    echo -e "  ${GREEN}logs${NC}            View system logs"
    echo -e "  ${GREEN}metrics${NC}         Show key metrics"
    echo ""
    echo -e "${BLUE}🔧 MANAGEMENT:${NC}"
    echo -e "  ${GREEN}start${NC}           Start all services"
    echo -e "  ${GREEN}stop${NC}            Stop all services"
    echo -e "  ${GREEN}restart${NC}         Restart all services"
    echo -e "  ${GREEN}update${NC}          Update system"
    echo ""
    echo -e "${BLUE}💾 MAINTENANCE:${NC}"
    echo -e "  ${GREEN}backup${NC}          Create full backup"
    echo -e "  ${GREEN}restore${NC}         Restore from backup"
    echo -e "  ${GREEN}cleanup${NC}         Clean unused resources"
    echo -e "  ${GREEN}optimize${NC}        Optimize system performance"
    echo ""
    echo -e "${BLUE}🔐 SECURITY:${NC}"
    echo -e "  ${GREEN}security-scan${NC}   Scan for vulnerabilities"
    echo -e "  ${GREEN}update-certs${NC}    Update SSL certificates"
    echo -e "  ${GREEN}firewall${NC}        Configure firewall"
    echo ""
    echo -e "${BLUE}📱 QUICK ACCESS:${NC}"
    echo -e "  ${GREEN}dashboard${NC}       Open main dashboard"
    echo -e "  ${GREEN}analytics${NC}       Open analytics dashboard"
    echo -e "  ${GREEN}monitoring${NC}      Open monitoring dashboard"
    echo -e "  ${GREEN}api-docs${NC}        Open API documentation"
    echo ""
    echo -e "${YELLOW}💡 Examples:${NC}"
    echo -e "  ./operations.sh deploy          # Deploy to production"
    echo -e "  ./operations.sh health          # Full health check"
    echo -e "  ./operations.sh logs api        # View API logs"
    echo -e "  ./operations.sh backup daily    # Create daily backup"
    echo ""
}

# Function to check if running on server or local
is_server() {
    [ -f "/etc/nginx/nginx.conf" ] || [ -d "/opt/neural-forge" ]
}

# Function to get service URLs
get_urls() {
    if is_server; then
        DOMAIN=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")
        echo -e "${YELLOW}🌐 Production URLs:${NC}"
        echo -e "  🎮 Main Dashboard: https://$DOMAIN"
        echo -e "  📊 Analytics: https://$DOMAIN/analytics"
        echo -e "  📈 Monitoring: https://$DOMAIN/grafana"
        echo -e "  🔧 API Docs: https://$DOMAIN/api/docs"
    else
        echo -e "${YELLOW}🛠️ Development URLs:${NC}"
        echo -e "  🎮 Production Controller: http://localhost:7860"
        echo -e "  📊 Analytics Engine: http://localhost:8501"
        echo -e "  🧠 ML Core API: http://localhost:8000/docs"
        echo -e "  🔄 N8N Workflows: http://localhost:5678"
        echo -e "  📈 Grafana: http://localhost:3000"
        echo -e "  📊 Prometheus: http://localhost:9090"
    fi
}

# Main command handler
case "$1" in
    # DEPLOYMENT COMMANDS
    deploy)
        echo -e "${BLUE}🚀 Deploying Neural Forge to production...${NC}"
        if [ -f "./deploy/hetzner/deploy-services.sh" ]; then
            ./deploy/hetzner/deploy-services.sh
        else
            echo -e "${RED}❌ Deployment script not found${NC}"
            exit 1
        fi
        ;;
        
    deploy-dev)
        echo -e "${BLUE}🛠️ Deploying development environment...${NC}"
        docker compose -f docker-compose.dev.yml up -d
        echo -e "${GREEN}✅ Development environment started${NC}"
        get_urls
        ;;
        
    setup-vps)
        echo -e "${BLUE}🏗️ Setting up VPS...${NC}"
        if [ -f "./deploy/hetzner/setup-vps.sh" ]; then
            sudo ./deploy/hetzner/setup-vps.sh
        else
            echo -e "${RED}❌ VPS setup script not found${NC}"
            exit 1
        fi
        ;;
        
    setup-ssl)
        echo -e "${BLUE}🔒 Setting up SSL certificates...${NC}"
        if [ -f "./deploy/hetzner/ssl-setup.sh" ]; then
            sudo ./deploy/hetzner/ssl-setup.sh
        else
            echo -e "${RED}❌ SSL setup script not found${NC}"
            exit 1
        fi
        ;;
    
    # MONITORING COMMANDS  
    health)
        echo -e "${BLUE}🏥 Running comprehensive health check...${NC}"
        if [ -f "./scripts/health-check.sh" ]; then
            ./scripts/health-check.sh
        else
            echo -e "${YELLOW}⚠️ Health check script not found, running basic check...${NC}"
            docker compose ps
            echo ""
            echo "System Resources:"
            echo "  CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')"
            echo "  Memory: $(free -h | awk '/^Mem:/{print $3 "/" $2}')"
            echo "  Disk: $(df -h / | awk 'NR==2{print $3 "/" $2}')"
        fi
        ;;
        
    status)
        echo -e "${BLUE}📊 Quick system status...${NC}"
        docker compose ps
        echo ""
        get_urls
        ;;
        
    logs)
        SERVICE="${2:-}"
        if [ -n "$SERVICE" ]; then
            echo -e "${BLUE}📋 Viewing logs for $SERVICE...${NC}"
            docker compose logs -f "$SERVICE"
        else
            echo -e "${BLUE}📋 Viewing all system logs...${NC}"
            docker compose logs -f
        fi
        ;;
        
    metrics)
        echo -e "${BLUE}📈 Key system metrics...${NC}"
        echo "Docker containers:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
        echo ""
        echo "System resources:"
        echo "  Load: $(uptime | awk -F'load average:' '{print $2}')"
        echo "  Disk usage: $(df -h / | awk 'NR==2{print $5 " used"}')"
        echo "  Memory: $(free -h | awk '/^Mem:/{print $3 "/" $2}')"
        ;;
    
    # MANAGEMENT COMMANDS
    start)
        echo -e "${BLUE}🚀 Starting all Neural Forge services...${NC}"
        docker compose up -d
        echo -e "${GREEN}✅ All services started${NC}"
        sleep 5
        docker compose ps
        ;;
        
    stop)
        echo -e "${BLUE}🛑 Stopping all Neural Forge services...${NC}"
        docker compose down
        echo -e "${GREEN}✅ All services stopped${NC}"
        ;;
        
    restart)
        echo -e "${BLUE}🔄 Restarting all Neural Forge services...${NC}"
        docker compose restart
        echo -e "${GREEN}✅ All services restarted${NC}"
        sleep 5
        docker compose ps
        ;;
        
    update)
        echo -e "${BLUE}🔄 Updating Neural Forge system...${NC}"
        git pull origin main
        docker compose pull
        docker compose build --parallel
        docker compose up -d
        echo -e "${GREEN}✅ System updated${NC}"
        ;;
    
    # MAINTENANCE COMMANDS
    backup)
        BACKUP_TYPE="${2:-full}"
        echo -e "${BLUE}💾 Creating $BACKUP_TYPE backup...${NC}"
        
        BACKUP_DIR="backups/backup-$(date +%Y%m%d-%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Database backup
        if docker compose ps postgres | grep -q "Up"; then
            echo "Backing up PostgreSQL database..."
            docker compose exec postgres pg_dump -U neural_forge neural_forge > "$BACKUP_DIR/postgres.sql"
        fi
        
        # Configuration backup
        echo "Backing up configuration..."
        cp -r config/ "$BACKUP_DIR/"
        cp .env "$BACKUP_DIR/" 2>/dev/null || true
        
        # Data volumes backup
        echo "Backing up data volumes..."
        docker run --rm -v neural-forge_postgres_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
        docker run --rm -v neural-forge_grafana_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/grafana_data.tar.gz -C /data .
        
        echo -e "${GREEN}✅ Backup completed: $BACKUP_DIR${NC}"
        ;;
        
    restore)
        BACKUP_DIR="$2"
        if [ -z "$BACKUP_DIR" ] || [ ! -d "$BACKUP_DIR" ]; then
            echo -e "${RED}❌ Please specify a valid backup directory${NC}"
            echo "Usage: $0 restore <backup-directory>"
            exit 1
        fi
        
        echo -e "${YELLOW}⚠️ This will overwrite current data. Continue? (y/N)${NC}"
        read -r CONFIRM
        if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
            echo "Restore cancelled"
            exit 0
        fi
        
        echo -e "${BLUE}🔄 Restoring from backup: $BACKUP_DIR${NC}"
        
        # Stop services
        docker compose down
        
        # Restore database
        if [ -f "$BACKUP_DIR/postgres.sql" ]; then
            echo "Restoring PostgreSQL database..."
            docker compose up -d postgres
            sleep 10
            docker compose exec -T postgres psql -U neural_forge -d neural_forge < "$BACKUP_DIR/postgres.sql"
        fi
        
        # Restore configuration
        if [ -d "$BACKUP_DIR/config" ]; then
            echo "Restoring configuration..."
            cp -r "$BACKUP_DIR/config/" ./
        fi
        
        # Start services
        docker compose up -d
        
        echo -e "${GREEN}✅ Restore completed${NC}"
        ;;
        
    cleanup)
        echo -e "${BLUE}🧹 Cleaning up system resources...${NC}"
        
        # Docker cleanup
        docker system prune -f
        docker volume prune -f
        docker network prune -f
        
        # Log cleanup
        find logs/ -name "*.log" -mtime +30 -delete 2>/dev/null || true
        
        # Backup cleanup (keep last 10)
        if [ -d "backups" ]; then
            ls -t backups/ | tail -n +11 | xargs -I {} rm -rf backups/{}
        fi
        
        echo -e "${GREEN}✅ Cleanup completed${NC}"
        ;;
        
    optimize)
        echo -e "${BLUE}⚡ Optimizing system performance...${NC}"
        
        # Docker optimization
        docker system prune -f
        
        # Restart services to clear memory
        docker compose restart
        
        # System optimization (if running as root)
        if [ "$EUID" -eq 0 ]; then
            echo "Optimizing system parameters..."
            sysctl -p /etc/sysctl.d/neural-forge.conf 2>/dev/null || true
            echo 3 > /proc/sys/vm/drop_caches
        fi
        
        echo -e "${GREEN}✅ System optimized${NC}"
        ;;
    
    # SECURITY COMMANDS
    security-scan)
        echo -e "${BLUE}🔐 Running security scan...${NC}"
        
        # Check for updates
        echo "Checking for system updates..."
        if command -v apt >/dev/null 2>&1; then
            sudo apt update && sudo apt list --upgradable
        fi
        
        # Docker image security scan
        echo "Scanning Docker images..."
        docker images --format "table {{.Repository}}:{{.Tag}}" | grep neural-forge | while read image; do
            echo "Scanning $image (basic check)..."
            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image "$image" || echo "Trivy not available, skipping detailed scan"
        done
        
        # Check file permissions
        echo "Checking file permissions..."
        find . -name "*.sh" -not -perm 755 -exec chmod 755 {} \;
        [ -f .env ] && chmod 600 .env
        
        echo -e "${GREEN}✅ Security scan completed${NC}"
        ;;
        
    update-certs)
        echo -e "${BLUE}🔒 Updating SSL certificates...${NC}"
        if command -v certbot >/dev/null 2>&1; then
            sudo certbot renew
            sudo systemctl reload nginx
            echo -e "${GREEN}✅ Certificates updated${NC}"
        else
            echo -e "${RED}❌ Certbot not installed${NC}"
        fi
        ;;
        
    firewall)
        echo -e "${BLUE}🔥 Configuring firewall...${NC}"
        if command -v ufw >/dev/null 2>&1; then
            sudo ufw status
            echo "Firewall is configured. Use 'sudo ufw' to modify rules."
        else
            echo -e "${YELLOW}⚠️ UFW not installed${NC}"
        fi
        ;;
    
    # QUICK ACCESS COMMANDS
    dashboard)
        echo -e "${BLUE}🎮 Opening main dashboard...${NC}"
        if is_server; then
            echo "Dashboard URL: https://$(curl -s ifconfig.me)"
        else
            echo "Dashboard URL: http://localhost:7860"
            command -v xdg-open >/dev/null && xdg-open http://localhost:7860 || open http://localhost:7860 2>/dev/null || echo "Please open http://localhost:7860 in your browser"
        fi
        ;;
        
    analytics)
        echo -e "${BLUE}📊 Opening analytics dashboard...${NC}"
        if is_server; then
            echo "Analytics URL: https://$(curl -s ifconfig.me)/analytics"
        else
            echo "Analytics URL: http://localhost:8501"
            command -v xdg-open >/dev/null && xdg-open http://localhost:8501 || open http://localhost:8501 2>/dev/null || echo "Please open http://localhost:8501 in your browser"
        fi
        ;;
        
    monitoring)
        echo -e "${BLUE}📈 Opening monitoring dashboard...${NC}"
        if is_server; then
            echo "Monitoring URL: https://$(curl -s ifconfig.me)/grafana"
        else
            echo "Grafana URL: http://localhost:3000 (admin/neuralforge2025)"
            command -v xdg-open >/dev/null && xdg-open http://localhost:3000 || open http://localhost:3000 2>/dev/null || echo "Please open http://localhost:3000 in your browser"
        fi
        ;;
        
    api-docs)
        echo -e "${BLUE}🔧 Opening API documentation...${NC}"
        if is_server; then
            echo "API Docs URL: https://$(curl -s ifconfig.me)/api/docs"
        else
            echo "API Docs URL: http://localhost:8000/docs"
            command -v xdg-open >/dev/null && xdg-open http://localhost:8000/docs || open http://localhost:8000/docs 2>/dev/null || echo "Please open http://localhost:8000/docs in your browser"
        fi
        ;;
    
    # HELP AND DEFAULT
    help|--help|-h)
        show_help
        ;;
        
    *)
        if [ -z "$1" ]; then
            echo -e "${YELLOW}💡 No command specified. Showing system status...${NC}"
            echo ""
            $0 status
            echo ""
            echo -e "${BLUE}Run '$0 help' for available commands${NC}"
        else
            echo -e "${RED}❌ Unknown command: $1${NC}"
            echo -e "${BLUE}Run '$0 help' for available commands${NC}"
            exit 1
        fi
        ;;
esac

exit 0