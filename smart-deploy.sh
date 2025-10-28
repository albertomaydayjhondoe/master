#!/bin/bash
# Auto-detect deployment environment and start services accordingly

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🚀 TikTok ML Automation - Smart Deployment         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect environment
if [ -n "$CODESPACE_NAME" ]; then
    ENV="codespaces"
    echo -e "${YELLOW}📍 Detected: GitHub Codespaces${NC}"
elif [ -f /.dockerenv ]; then
    ENV="docker-container"
    echo -e "${BLUE}📍 Detected: Docker Container${NC}"
elif command -v docker &> /dev/null && docker ps &> /dev/null; then
    ENV="docker-host"
    echo -e "${GREEN}📍 Detected: Docker Host${NC}"
else
    ENV="native"
    echo -e "${YELLOW}📍 Detected: Native Environment${NC}"
fi

echo ""
echo -e "${BLUE}🔧 Deployment Environment: ${ENV}${NC}"
echo ""

# Function to start services based on environment
start_services() {
    case $ENV in
        codespaces)
            echo -e "${YELLOW}🌐 Starting in Codespaces mode...${NC}"
            start_codespaces
            ;;
        docker-host)
            echo -e "${GREEN}🐳 Starting in Docker mode...${NC}"
            start_docker
            ;;
        docker-container)
            echo -e "${BLUE}📦 Running inside Docker container${NC}"
            # Already running, just show status
            show_status
            ;;
        native)
            echo -e "${YELLOW}💻 Starting in Native mode...${NC}"
            start_native
            ;;
    esac
}

# Codespaces deployment
start_codespaces() {
    echo "🔧 Codespaces Configuration:"
    echo "  • Lightweight services"
    echo "  • Keep-alive enabled"
    echo "  • Dashboard on port 8501"
    echo ""
    
    # Create keep-alive script
    cat > /tmp/keepalive.sh << 'EOFKA'
#!/bin/bash
while true; do
    curl -s http://localhost:8501 > /dev/null 2>&1
    curl -s http://localhost:8000 > /dev/null 2>&1
    echo "Keepalive ping: $(date)" >> /tmp/keepalive.log
    sleep 120
done
EOFKA
    chmod +x /tmp/keepalive.sh
    
    # Start keep-alive in background
    if ! pgrep -f "keepalive.sh" > /dev/null; then
        nohup /tmp/keepalive.sh > /dev/null 2>&1 &
        echo -e "${GREEN}✅ Keep-alive started${NC}"
    fi
    
    # Start dashboard
    if ! pgrep -f "streamlit" > /dev/null; then
        nohup streamlit run scripts/production_control_dashboard.py \
            --server.port=8501 \
            --server.address=0.0.0.0 \
            --server.enableCORS=true \
            --server.enableXsrfProtection=true \
            --browser.gatherUsageStats=false \
            > /tmp/streamlit.log 2>&1 &
        echo -e "${GREEN}✅ Dashboard started on port 8501${NC}"
    fi
    
    # Start Telegram bot (optional)
    read -p "Start Telegram bot? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if ! pgrep -f "telegram_like4like_bot" > /dev/null; then
            nohup python telegram_like4like_bot.py > /tmp/telegram.log 2>&1 &
            echo -e "${GREEN}✅ Telegram bot started${NC}"
        fi
    fi
    
    echo ""
    echo -e "${GREEN}✅ Codespaces deployment complete!${NC}"
    echo ""
    echo "🌐 Access URLs:"
    if [ -n "$CODESPACE_NAME" ]; then
        echo "  Dashboard: https://${CODESPACE_NAME}-8501.app.github.dev"
    fi
    echo "  Local: http://localhost:8501"
    echo ""
    echo "📝 Logs:"
    echo "  Dashboard: tail -f /tmp/streamlit.log"
    echo "  Telegram: tail -f /tmp/telegram.log"
    echo "  Keep-alive: tail -f /tmp/keepalive.log"
}

# Docker deployment
start_docker() {
    echo "🐳 Docker Configuration:"
    echo "  • Full service stack"
    echo "  • Auto-restart enabled"
    echo "  • Production ready"
    echo ""
    
    # Check if .env exists
    if [ ! -f .env ]; then
        echo -e "${YELLOW}⚠️  .env file not found${NC}"
        echo "Creating from .env.example..."
        cp .env.example .env
        echo -e "${RED}❌ Please edit .env with your credentials${NC}"
        exit 1
    fi
    
    # Build and start
    echo "Building services..."
    docker-compose build
    
    echo "Starting services..."
    docker-compose up -d
    
    echo ""
    echo -e "${GREEN}✅ Docker deployment complete!${NC}"
    echo ""
    echo "🎛️  Services:"
    docker-compose ps
    
    echo ""
    echo "🌐 Access URLs:"
    echo "  Dashboard: http://localhost:8501"
    echo "  ML Core API: http://localhost:8000"
    echo "  Meta Ads API: http://localhost:8002"
    echo ""
    echo "🔧 Management:"
    echo "  Status: ./docker-manage.sh status"
    echo "  Logs: ./docker-manage.sh logs"
    echo "  Health: ./docker-manage.sh health"
}

# Native deployment
start_native() {
    echo "💻 Native Configuration:"
    echo "  • Direct Python execution"
    echo "  • Development mode"
    echo ""
    
    # Check Python
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ Python not found${NC}"
        exit 1
    fi
    
    # Check dependencies
    echo "Checking dependencies..."
    python -c "from config.dependency_manager import DependencyManager; DependencyManager().check_all_dependencies()"
    
    echo ""
    echo "Starting services..."
    
    # Start dashboard
    nohup streamlit run scripts/production_control_dashboard.py > /tmp/streamlit.log 2>&1 &
    echo -e "${GREEN}✅ Dashboard started${NC}"
    
    # Start Telegram bot
    read -p "Start Telegram bot? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nohup python telegram_like4like_bot.py > /tmp/telegram.log 2>&1 &
        echo -e "${GREEN}✅ Telegram bot started${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Native deployment complete!${NC}"
    echo ""
    echo "🌐 Access: http://localhost:8501"
}

# Show status
show_status() {
    echo "📊 Service Status:"
    echo ""
    
    # Check dashboard
    if curl -sf http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        echo -e "  Dashboard: ${GREEN}✅ Running${NC}"
    else
        echo -e "  Dashboard: ${RED}❌ Not running${NC}"
    fi
    
    # Check ML Core
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "  ML Core: ${GREEN}✅ Running${NC}"
    else
        echo -e "  ML Core: ${YELLOW}⚠️  Not running${NC}"
    fi
    
    # Check processes
    echo ""
    echo "🔧 Running Processes:"
    ps aux | grep -E "(streamlit|telegram|python)" | grep -v grep | head -5
}

# Main execution
start_services

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
