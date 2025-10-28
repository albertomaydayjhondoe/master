#!/bin/bash

# TikTok ML System v4 - Production Startup Script
# Automated setup and deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logo
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    TikTok ML System v4                       ║"
echo "║              Production Deployment Script                    ║"
echo "║                                                              ║"
echo "║  🧠 n8n + 🤖 Ultralytics + 📊 Meta Ads + 📈 Supabase      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Windows (Git Bash/WSL)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    log_info "Detected Windows environment"
    PLATFORM="windows"
else
    log_info "Detected Unix-like environment"
    PLATFORM="unix"
fi

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        log_warning "curl is not installed. Some features may not work properly."
    fi
    
    log_success "All dependencies found"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."
    
    # Create .env from example if it doesn't exist
    if [ ! -f ".env" ]; then
        log_info "Creating .env from .env.example..."
        cp .env.example .env
        log_warning "Please edit .env file with your actual credentials before continuing"
        
        # Open .env file for editing
        if [[ "$PLATFORM" == "windows" ]]; then
            notepad .env || nano .env || vi .env
        else
            ${EDITOR:-nano} .env
        fi
        
        echo ""
        read -p "Have you configured the .env file with your credentials? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "Please configure the .env file and run this script again"
            exit 1
        fi
    else
        log_success ".env file already exists"
    fi
    
    # Create necessary directories
    log_info "Creating directories..."
    mkdir -p data/models logs uploads
    
    log_success "Environment setup complete"
}

# Validate configuration
validate_config() {
    log_info "Validating configuration..."
    
    # Check if required variables are set
    source .env
    
    required_vars=(
        "API_SECRET_KEY"
        "SUPABASE_URL"
        "SUPABASE_ANON_KEY"
        "SUPABASE_SERVICE_KEY"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        exit 1
    fi
    
    log_success "Configuration validation passed"
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."
    
    docker build -f Dockerfile.v4 -t tiktok-ml-v4:latest .
    
    if [ $? -eq 0 ]; then
        log_success "Docker image built successfully"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

# Deploy with Docker Compose
deploy_compose() {
    log_info "Deploying with Docker Compose..."
    
    # Stop any existing services
    docker-compose -f docker-compose.v4.yml down
    
    # Start services
    docker-compose -f docker-compose.v4.yml up -d
    
    if [ $? -eq 0 ]; then
        log_success "Services deployed successfully"
    else
        log_error "Failed to deploy services"
        exit 1
    fi
}

# Wait for services to be healthy
wait_for_services() {
    log_info "Waiting for services to be healthy..."
    
    # Wait for main API
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            log_success "API is healthy"
            break
        fi
        
        log_info "Attempt $attempt/$max_attempts: Waiting for API to be ready..."
        sleep 10
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "API failed to become healthy"
        exit 1
    fi
}

# Test API endpoints
test_api() {
    log_info "Testing API endpoints..."
    
    # Test health endpoint
    health_response=$(curl -s http://localhost:8000/health)
    if [[ $health_response == *"healthy"* ]]; then
        log_success "Health endpoint working"
    else
        log_error "Health endpoint failed"
    fi
    
    # Test API documentation
    if curl -f http://localhost:8000/docs &> /dev/null; then
        log_success "API documentation available at http://localhost:8000/docs"
    else
        log_warning "API documentation not accessible"
    fi
}

# Display deployment info
show_deployment_info() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                   DEPLOYMENT SUCCESSFUL!                     ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}🌐 Service URLs:${NC}"
    echo "  • Main API:        http://localhost:8000"
    echo "  • API Docs:        http://localhost:8000/docs"
    echo "  • Health Check:    http://localhost:8000/health"
    echo "  • n8n Workflows:   http://localhost:5678"
    echo ""
    echo -e "${BLUE}📊 Management Commands:${NC}"
    echo "  • View logs:       docker-compose -f docker-compose.v4.yml logs -f"
    echo "  • Stop services:   docker-compose -f docker-compose.v4.yml down"
    echo "  • Restart:         docker-compose -f docker-compose.v4.yml restart"
    echo "  • Check status:    docker-compose -f docker-compose.v4.yml ps"
    echo ""
    echo -e "${BLUE}🔧 Configuration:${NC}"
    echo "  • Edit config:     nano .env"
    echo "  • Reload:          docker-compose -f docker-compose.v4.yml up -d"
    echo ""
    echo -e "${YELLOW}📋 Next Steps:${NC}"
    echo "  1. Configure n8n workflows at http://localhost:5678"
    echo "  2. Test API endpoints at http://localhost:8000/docs"
    echo "  3. Monitor logs for any issues"
    echo "  4. Configure SSL/TLS for production use"
    echo ""
}

# Main execution
main() {
    log_info "Starting TikTok ML System v4 deployment..."
    
    check_dependencies
    setup_environment
    validate_config
    build_image
    deploy_compose
    wait_for_services
    test_api
    show_deployment_info
    
    log_success "Deployment completed successfully! 🚀"
}

# Handle script arguments
case "${1:-}" in
    "start"|"deploy")
        main
        ;;
    "stop")
        log_info "Stopping services..."
        docker-compose -f docker-compose.v4.yml down
        log_success "Services stopped"
        ;;
    "restart")
        log_info "Restarting services..."
        docker-compose -f docker-compose.v4.yml down
        docker-compose -f docker-compose.v4.yml up -d
        log_success "Services restarted"
        ;;
    "logs")
        docker-compose -f docker-compose.v4.yml logs -f
        ;;
    "status")
        docker-compose -f docker-compose.v4.yml ps
        ;;
    "build")
        build_image
        ;;
    "help"|"--help"|"-h")
        echo "TikTok ML System v4 - Deployment Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  start, deploy    Full deployment (default)"
        echo "  stop            Stop all services"
        echo "  restart         Restart all services"
        echo "  logs            Show live logs"
        echo "  status          Show services status"
        echo "  build           Build Docker image only"
        echo "  help            Show this help"
        echo ""
        ;;
    *)
        log_info "No command specified, running full deployment..."
        main
        ;;
esac