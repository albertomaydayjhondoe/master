#!/bin/bash

# Docker v2.0 Management Script
# Meta Ads → Pixeles → Landing Pages → YouTube

set -e

COMPOSE_FILE="docker-compose-v2.yml"
PROJECT_NAME="marketing-funnel-v2"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║         Docker v2.0 - Marketing Funnel Manager        ║"
    echo "║     Meta Ads → Pixeles → Landing Pages → YouTube      ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_env() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        print_info "Copy .env.v2 to .env and configure your credentials"
        exit 1
    fi
    print_success ".env file found"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

build() {
    print_info "Building Docker v2.0 images..."
    docker-compose -f $COMPOSE_FILE build "$@"
    print_success "Build completed!"
}

start() {
    print_info "Starting Docker v2.0 services..."
    docker-compose -f $COMPOSE_FILE up -d "$@"
    print_success "Services started!"
    
    echo ""
    print_info "Waiting for services to be ready..."
    sleep 10
    
    health_check
}

stop() {
    print_info "Stopping Docker v2.0 services..."
    docker-compose -f $COMPOSE_FILE stop "$@"
    print_success "Services stopped!"
}

restart() {
    print_info "Restarting Docker v2.0 services..."
    docker-compose -f $COMPOSE_FILE restart "$@"
    print_success "Services restarted!"
}

down() {
    print_warning "Stopping and removing all containers..."
    read -p "Are you sure? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f $COMPOSE_FILE down "$@"
        print_success "All containers removed!"
    else
        print_info "Operation cancelled"
    fi
}

status() {
    print_info "Service Status:"
    docker-compose -f $COMPOSE_FILE ps
}

logs() {
    service=${1:-}
    if [ -z "$service" ]; then
        docker-compose -f $COMPOSE_FILE logs -f
    else
        docker-compose -f $COMPOSE_FILE logs -f "$service"
    fi
}

health_check() {
    print_info "Checking service health..."
    echo ""
    
    services=(
        "meta-ads-manager:9000"
        "pixel-tracker:9001"
        "landing-optimizer:9002"
        "youtube-uploader:9003"
        "ml-predictor-v2:9004"
        "analytics-dashboard:9005"
        "automation-orchestrator:9006"
    )
    
    for service_port in "${services[@]}"; do
        IFS=':' read -r service port <<< "$service_port"
        
        if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
            print_success "$service (port $port)"
        else
            print_error "$service (port $port) - NOT RESPONDING"
        fi
    done
    
    echo ""
}

show_urls() {
    print_header
    echo ""
    print_info "Service URLs:"
    echo ""
    echo "Meta Ads Manager:       http://localhost:9000"
    echo "Pixel Tracker:          http://localhost:9001"
    echo "Landing Pages:          http://localhost:9002"
    echo "Landing Admin:          http://localhost:9012"
    echo "YouTube Uploader:       http://localhost:9003"
    echo "ML Predictor:           http://localhost:9004"
    echo "Analytics Dashboard:    http://localhost:9005"
    echo "Automation Orchestrator: http://localhost:9006"
    echo ""
    echo "Database (PostgreSQL):  localhost:5433"
    echo "Redis:                  localhost:6380"
    echo "Nginx HTTP:             http://localhost:8080"
    echo "Nginx HTTPS:            https://localhost:8443"
    echo ""
}

api_docs() {
    print_info "API Documentation URLs:"
    echo ""
    echo "Meta Ads Manager:   http://localhost:9000/docs"
    echo "Pixel Tracker:      http://localhost:9001/docs"
    echo "Landing Optimizer:  http://localhost:9002/docs"
    echo "YouTube Uploader:   http://localhost:9003/docs"
    echo "ML Predictor:       http://localhost:9004/docs"
    echo "Analytics:          http://localhost:9005/docs"
    echo "Orchestrator:       http://localhost:9006/docs"
    echo ""
}

quick_campaign() {
    print_info "Creating quick campaign..."
    
    read -p "Artist Name: " artist_name
    read -p "Song Name: " song_name
    read -p "Landing URL: " landing_url
    read -p "Daily Budget (USD): " daily_budget
    
    curl -X POST http://localhost:9000/quick-campaign \
        -H "Content-Type: application/json" \
        -d "{
            \"artist_name\": \"$artist_name\",
            \"song_name\": \"$song_name\",
            \"landing_url\": \"$landing_url\",
            \"daily_budget\": $daily_budget,
            \"target_countries\": [\"US\", \"MX\", \"ES\"]
        }"
    
    echo ""
    print_success "Campaign created! Check Meta Ads Manager for details"
}

quick_youtube_upload() {
    print_info "Uploading video to YouTube..."
    
    read -p "Video Path: " video_path
    read -p "Artist Name: " artist_name
    read -p "Song Name: " song_name
    read -p "Genre (default: Trap): " genre
    genre=${genre:-Trap}
    
    curl -X POST http://localhost:9003/quick-upload \
        -H "Content-Type: application/json" \
        -d "{
            \"video_path\": \"$video_path\",
            \"artist_name\": \"$artist_name\",
            \"song_name\": \"$song_name\",
            \"genre\": \"$genre\"
        }"
    
    echo ""
    print_success "Video uploaded! Check YouTube for confirmation"
}

test_pixel() {
    print_info "Testing Facebook Pixel..."
    
    curl -X POST http://localhost:9001/track/pageview \
        -H "Content-Type: application/json" \
        -d '{
            "event_source_url": "https://test-domain.com",
            "content_name": "Test Page",
            "user_ip": "127.0.0.1"
        }'
    
    echo ""
    print_success "Pixel test event sent!"
}

backup() {
    print_info "Creating backup..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backups/v2_backup_$timestamp"
    
    mkdir -p "$backup_dir"
    
    # Backup database
    print_info "Backing up database..."
    docker exec marketing-database-v2 pg_dump -U marketing_user marketing_funnel_v2 > "$backup_dir/database.sql"
    
    # Backup Redis
    print_info "Backing up Redis..."
    docker exec marketing-redis-v2 redis-cli --no-auth-warning -a "$REDIS_PASSWORD" SAVE
    docker cp marketing-redis-v2:/data/dump.rdb "$backup_dir/redis.rdb"
    
    # Backup configs
    print_info "Backing up configs..."
    cp .env "$backup_dir/.env"
    cp docker-compose-v2.yml "$backup_dir/docker-compose-v2.yml"
    
    # Compress
    print_info "Compressing backup..."
    tar -czf "backups/v2_backup_$timestamp.tar.gz" "$backup_dir"
    rm -rf "$backup_dir"
    
    print_success "Backup created: backups/v2_backup_$timestamp.tar.gz"
}

restore() {
    print_warning "This will restore from a backup. Current data will be lost!"
    read -p "Backup file path: " backup_path
    
    if [ ! -f "$backup_path" ]; then
        print_error "Backup file not found!"
        exit 1
    fi
    
    read -p "Are you sure? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Operation cancelled"
        exit 0
    fi
    
    print_info "Restoring from backup..."
    
    # Extract backup
    temp_dir=$(mktemp -d)
    tar -xzf "$backup_path" -C "$temp_dir"
    
    # Restore database
    print_info "Restoring database..."
    cat "$temp_dir"/*/database.sql | docker exec -i marketing-database-v2 psql -U marketing_user marketing_funnel_v2
    
    # Restore Redis
    print_info "Restoring Redis..."
    docker cp "$temp_dir"/*/redis.rdb marketing-redis-v2:/data/dump.rdb
    docker-compose -f $COMPOSE_FILE restart redis-v2
    
    rm -rf "$temp_dir"
    
    print_success "Restore completed!"
}

usage() {
    print_header
    echo "Usage: $0 {command} [options]"
    echo ""
    echo "Commands:"
    echo "  build          Build Docker images"
    echo "  start          Start all services"
    echo "  stop           Stop all services"
    echo "  restart        Restart all services"
    echo "  down           Stop and remove all containers"
    echo "  status         Show service status"
    echo "  logs [service] Show logs (all or specific service)"
    echo "  health         Check service health"
    echo "  urls           Show service URLs"
    echo "  docs           Show API documentation URLs"
    echo "  campaign       Create quick Meta Ads campaign"
    echo "  upload         Upload video to YouTube"
    echo "  test-pixel     Test Facebook Pixel"
    echo "  backup         Create system backup"
    echo "  restore        Restore from backup"
    echo ""
    echo "Examples:"
    echo "  $0 start                # Start all services"
    echo "  $0 logs meta-ads-manager # Show Meta Ads logs"
    echo "  $0 health               # Check all services"
    echo "  $0 campaign             # Create quick campaign"
    echo ""
}

# Main
case "${1:-}" in
    build)
        check_docker
        check_env
        build "${@:2}"
        ;;
    start)
        check_docker
        check_env
        start "${@:2}"
        ;;
    stop)
        stop "${@:2}"
        ;;
    restart)
        restart "${@:2}"
        ;;
    down)
        down "${@:2}"
        ;;
    status)
        status
        ;;
    logs)
        logs "${2:-}"
        ;;
    health)
        health_check
        ;;
    urls)
        show_urls
        ;;
    docs)
        api_docs
        ;;
    campaign)
        quick_campaign
        ;;
    upload)
        quick_youtube_upload
        ;;
    test-pixel)
        test_pixel
        ;;
    backup)
        backup
        ;;
    restore)
        restore
        ;;
    *)
        usage
        exit 1
        ;;
esac
