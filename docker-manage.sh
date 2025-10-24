#!/bin/bash
# Docker Management Script for TikTok ML Automation System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  🐳 TikTok ML Automation - Docker Manager           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found"
        print_info "Creating .env from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file with your credentials"
        exit 1
    fi
    print_success ".env file found"
}

# Build all services
build_services() {
    print_info "Building all services..."
    docker-compose build
    print_success "All services built successfully"
}

# Start all services
start_services() {
    print_info "Starting all services..."
    docker-compose up -d
    print_success "All services started"
    echo ""
    show_status
}

# Stop all services
stop_services() {
    print_info "Stopping all services..."
    docker-compose stop
    print_success "All services stopped"
}

# Restart services
restart_services() {
    print_info "Restarting all services..."
    docker-compose restart
    print_success "All services restarted"
}

# Show service status
show_status() {
    print_info "Service Status:"
    docker-compose ps
    echo ""
    print_info "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
}

# Show logs
show_logs() {
    if [ -z "$1" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$1"
    fi
}

# Run health checks
health_check() {
    print_info "Running health checks..."
    echo ""
    
    # Dashboard
    if curl -sf http://localhost:8501/_stcore/health > /dev/null; then
        print_success "Dashboard: Healthy"
    else
        print_error "Dashboard: Unhealthy"
    fi
    
    # ML Core
    if curl -sf http://localhost:8000/health > /dev/null; then
        print_success "ML Core: Healthy"
    else
        print_error "ML Core: Unhealthy"
    fi
    
    # Meta Ads
    if curl -sf http://localhost:8002/health > /dev/null; then
        print_success "Meta Ads: Healthy"
    else
        print_error "Meta Ads: Unhealthy"
    fi
    
    # Database
    if docker-compose exec -T database pg_isready -U tiktok_user > /dev/null 2>&1; then
        print_success "Database: Healthy"
    else
        print_error "Database: Unhealthy"
    fi
    
    # Redis
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis: Healthy"
    else
        print_error "Redis: Unhealthy"
    fi
}

# Backup data
backup_data() {
    BACKUP_DIR="backups/docker-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    print_info "Creating backup in $BACKUP_DIR..."
    
    # Backup database
    print_info "Backing up database..."
    docker-compose exec -T database pg_dump -U tiktok_user tiktok_automation > "$BACKUP_DIR/database.sql"
    
    # Backup volumes
    print_info "Backing up volumes..."
    docker run --rm -v master_postgres-data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/postgres-data.tar.gz -C /data .
    docker run --rm -v master_redis-data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/redis-data.tar.gz -C /data .
    
    print_success "Backup completed: $BACKUP_DIR"
}

# Clean up
cleanup() {
    print_warning "This will remove all containers, networks, and volumes"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up..."
        docker-compose down -v
        print_success "Cleanup completed"
    fi
}

# Show help
show_help() {
    cat << EOF
Usage: $0 [COMMAND]

Commands:
    start           Start all services
    stop            Stop all services
    restart         Restart all services
    build           Build all service images
    status          Show service status
    logs [service]  Show logs (optionally for specific service)
    health          Run health checks
    backup          Backup database and volumes
    cleanup         Remove all containers, networks, and volumes
    help            Show this help message

Examples:
    $0 start                # Start all services
    $0 logs dashboard       # Show dashboard logs
    $0 health               # Check service health
    $0 backup               # Create backup

EOF
}

# Main script
print_header

case "$1" in
    start)
        check_docker
        check_env
        start_services
        ;;
    stop)
        check_docker
        stop_services
        ;;
    restart)
        check_docker
        restart_services
        ;;
    build)
        check_docker
        check_env
        build_services
        ;;
    status)
        check_docker
        show_status
        ;;
    logs)
        check_docker
        show_logs "$2"
        ;;
    health)
        check_docker
        health_check
        ;;
    backup)
        check_docker
        backup_data
        ;;
    cleanup)
        check_docker
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Invalid command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
