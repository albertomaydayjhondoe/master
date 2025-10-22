#!/bin/bash

# Universal Project Awakener - Simple Script
# One command to wake the entire project ecosystem

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}🌅  UNIVERSAL PROJECT AWAKENER  🌅${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}One command to wake all branches: rama (TikTok ML), meta (Meta Ads), tele (Like4Like)${NC}"
    echo ""
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
MODE="full"
BRANCHES="rama meta tele"
STOP_ONLY=false
QUICK_START=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --branches)
            BRANCHES="$2"
            shift 2
            ;;
        --stop)
            STOP_ONLY=true
            shift
            ;;
        --quick)
            QUICK_START=true
            shift
            ;;
        --help|-h)
            echo "Universal Project Awakener"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --mode [basic|full|services]    Awakening mode (default: full)"
            echo "  --branches 'rama meta tele'     Branches to activate (default: all)"
            echo "  --quick                         Quick start without full setup"
            echo "  --stop                          Stop all services"
            echo "  --help                          Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                              # Full awakening of all branches"
            echo "  $0 --mode basic                 # Basic setup only"
            echo "  $0 --branches 'rama tele'       # Only TikTok ML and Like4Like"
            echo "  $0 --quick                      # Quick start for development"
            echo "  $0 --stop                       # Stop all services"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Print header
print_header

# Check if Python 3.9+ is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
            print_success "Python $PYTHON_VERSION found"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.9+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.9+"
        exit 1
    fi
}

# Quick dependency check
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        print_warning "No virtual environment found. Creating one..."
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    # Check if awakener dependencies are installed
    if ! python -c "import asyncio, json, yaml, pathlib" 2>/dev/null; then
        print_status "Installing basic dependencies..."
        pip install pyyaml asyncio-mqtt
    fi
    
    print_success "Dependencies ready"
}

# Stop all services
stop_services() {
    print_status "Stopping all project services..."
    
    # Stop any running Python processes related to the project
    pkill -f "ml_core.api.main" 2>/dev/null || true
    pkill -f "device_farm" 2>/dev/null || true
    pkill -f "meta_automation" 2>/dev/null || true
    pkill -f "telegram_automation" 2>/dev/null || true
    pkill -f "dummy_monitor.py" 2>/dev/null || true
    
    # Stop docker containers if running
    if command -v docker &> /dev/null; then
        docker ps -q --filter "name=master" | xargs -r docker stop 2>/dev/null || true
    fi
    
    print_success "All services stopped"
}

# Quick start mode
quick_start() {
    print_status "🚀 Quick Start Mode - Development Setup"
    
    # Set dummy mode
    export DUMMY_MODE=true
    
    # Start core services only
    print_status "Starting core ML API..."
    
    # Check if requirements are installed
    if [ -f "requirements-dummy.txt" ]; then
        pip install -r requirements-dummy.txt 2>/dev/null || print_warning "Could not install dummy requirements"
    fi
    
    # Start ML API in background
    nohup uvicorn ml_core.api.main:app --host 0.0.0.0 --port 8000 --reload > logs/ml_api.log 2>&1 &
    ML_API_PID=$!
    
    # Wait a moment for startup
    sleep 3
    
    # Check if service is running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "✅ ML API is running on http://localhost:8000"
        print_success "✅ API Documentation: http://localhost:8000/docs"
    else
        print_warning "ML API may not have started properly. Check logs/ml_api.log"
    fi
    
    echo ""
    print_success "🎉 Quick start complete!"
    print_status "🔗 Available endpoints:"
    echo "  • Health: http://localhost:8000/health"
    echo "  • API Docs: http://localhost:8000/docs"
    echo "  • Screenshot Analysis: http://localhost:8000/api/v1/analyze_screenshot"
    echo ""
    print_status "📝 To stop: $0 --stop"
    
    # Save PID for cleanup
    echo $ML_API_PID > .ml_api.pid
}

# Main awakening function
full_awakening() {
    print_status "🌅 Starting Full System Awakening..."
    print_status "📋 Mode: $MODE"
    print_status "🌿 Branches: $BRANCHES"
    
    # Create logs directory
    mkdir -p logs
    
    # Run the Python awakener
    if [ -f "awakener.py" ]; then
        print_status "🔧 Running Universal Awakener..."
        $PYTHON_CMD awakener.py --mode "$MODE" --branches $BRANCHES
    else
        print_error "awakener.py not found!"
        exit 1
    fi
}

# Create project structure if needed
ensure_project_structure() {
    print_status "📁 Ensuring project structure..."
    
    # Create essential directories
    mkdir -p logs
    mkdir -p data/{mock_databases,models,exports,screenshots}
    mkdir -p config/secrets
    
    # Create basic config files if they don't exist
    if [ ! -f "config/app_settings.py" ]; then
        cat > config/app_settings.py << 'EOF'
"""Runtime settings for toggling dummy vs production implementations."""
import os

def is_dummy_mode() -> bool:
    v = os.getenv("DUMMY_MODE", "true").lower()
    return v in ("1", "true", "yes", "on")

def get_env(name: str, default: str = None) -> str:
    return os.getenv(name, default)
EOF
        print_success "Created config/app_settings.py"
    fi
    
    # Create basic requirements if needed
    if [ ! -f "requirements-dummy.txt" ]; then
        cat > requirements-dummy.txt << 'EOF'
# Minimal dependencies for dummy mode
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
pillow==10.1.0
httpx==0.25.0
pyyaml==6.0.1
asyncio-mqtt==0.13.0

# Testing / dev
pytest==7.4.3
pytest-asyncio==0.21.1
EOF
        print_success "Created requirements-dummy.txt"
    fi
}

# Main execution
main() {
    # Handle stop command
    if [ "$STOP_ONLY" = true ]; then
        stop_services
        exit 0
    fi
    
    # Check system requirements
    check_python
    ensure_project_structure
    check_dependencies
    
    # Execute based on mode
    if [ "$QUICK_START" = true ]; then
        quick_start
    else
        full_awakening
    fi
}

# Trap for cleanup on exit
cleanup() {
    if [ -f ".ml_api.pid" ]; then
        ML_API_PID=$(cat .ml_api.pid)
        kill $ML_API_PID 2>/dev/null || true
        rm -f .ml_api.pid
    fi
}
trap cleanup EXIT

# Run main function
main "$@"