#!/bin/bash
# 🔧 Neural Forge - Development Environment Setup
# ==============================================
# Complete development environment initialization

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔧 Neural Forge - Development Setup${NC}"
echo -e "${CYAN}===================================${NC}"

# Configuration
PYTHON_VERSION="3.11"
NODE_VERSION="18"
REQUIRED_DOCKER_VERSION="20.10"

# Logging function
log_step() {
    echo -e "\n${BLUE}🔹 $1${NC}"
    echo "----------------------------------------"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check system requirements
check_requirements() {
    log_step "Checking System Requirements"
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "Linux system detected"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_success "macOS system detected"
    else
        log_warning "Unsupported OS: $OSTYPE"
    fi
    
    # Check Docker
    if command -v docker >/dev/null 2>&1; then
        DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
        log_success "Docker $DOCKER_VERSION installed"
        
        # Check Docker Compose
        if docker compose version >/dev/null 2>&1; then
            log_success "Docker Compose available"
        else
            log_error "Docker Compose not available"
            exit 1
        fi
    else
        log_error "Docker not installed"
        echo "Please install Docker from https://docker.com"
        exit 1
    fi
    
    # Check Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VER=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
        log_success "Python $PYTHON_VER installed"
    else
        log_warning "Python3 not found"
    fi
    
    # Check Node.js (optional)
    if command -v node >/dev/null 2>&1; then
        NODE_VER=$(node --version | grep -oE '[0-9]+\.[0-9]+')
        log_success "Node.js $NODE_VER installed"
    else
        log_warning "Node.js not found (optional)"
    fi
    
    # Check Git
    if command -v git >/dev/null 2>&1; then
        log_success "Git available"
    else
        log_error "Git not installed"
        exit 1
    fi
}

# Setup Python environment
setup_python() {
    log_step "Setting up Python Environment"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    echo "Upgrading pip..."
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements-dev.txt" ]; then
        echo "Installing development dependencies..."
        pip install -r requirements-dev.txt
        log_success "Development dependencies installed"
    fi
    
    if [ -f "requirements.txt" ]; then
        echo "Installing core dependencies..."
        pip install -r requirements.txt
        log_success "Core dependencies installed"
    fi
    
    # Install ML dependencies if available
    if [ -f "requirements-ml.txt" ]; then
        echo "Installing ML dependencies..."
        pip install -r requirements-ml.txt
        log_success "ML dependencies installed"
    fi
}

# Setup directories
setup_directories() {
    log_step "Setting up Directory Structure"
    
    DIRECTORIES=(
        "logs"
        "data/models"
        "data/uploads"
        "data/exports"
        "data/backups"
        "config/secrets"
        "monitoring/logs"
        "scripts/backups"
        "tests/fixtures"
    )
    
    for dir in "${DIRECTORIES[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            echo "Created: $dir"
        fi
    done
    
    log_success "Directory structure ready"
}

# Setup configuration files
setup_config() {
    log_step "Setting up Configuration Files"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        cat > .env << 'EOF'
# Neural Forge Development Configuration
# =====================================

# Application Settings
APP_NAME="Neural Forge Discográfica"
APP_VERSION="3.0.0"
ENVIRONMENT="development"
DEBUG=true
DUMMY_MODE=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Database Configuration
POSTGRES_DB=neural_forge_dev
POSTGRES_USER=neural_forge
POSTGRES_PASSWORD=dev_password_2025
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# ML Configuration
ML_MODEL_PATH=data/models
ML_ENABLE_GPU=false
ML_MAX_WORKERS=2

# N8N Configuration
N8N_HOST=localhost
N8N_PORT=5678
N8N_BASIC_AUTH_ACTIVE=false

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
GRAFANA_ADMIN_PASSWORD=neuralforge2025

# Security
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET=dev-jwt-secret-change-in-production
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","http://localhost:7860","http://localhost:8501"]

# External APIs (Development/Dummy)
OPENAI_API_KEY=sk-dummy-key-for-development
META_ACCESS_TOKEN=dummy-meta-token
GOLOGIN_API_TOKEN=dummy-gologin-token

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=detailed
EOF
        chmod 600 .env
        log_success ".env file created"
    else
        log_success ".env file already exists"
    fi
    
    # Create development Docker override
    if [ ! -f "docker-compose.override.yml" ]; then
        echo "Creating docker-compose.override.yml..."
        cat > docker-compose.override.yml << 'EOF'
version: '3.8'

# Development overrides
services:
  ml-core:
    volumes:
      - ./ml_core:/app/ml_core
      - ./data:/app/data
    environment:
      - RELOAD=true
      - DEBUG=true
    ports:
      - "8000:8000"
    
  production-controller:
    volumes:
      - ./:/app
    environment:
      - GRADIO_SERVER_NAME=0.0.0.0
      - GRADIO_SHARE=false
    ports:
      - "7860:7860"
    
  analytics-engine:
    volumes:
      - ./:/app
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
    ports:
      - "8501:8501"
    
  n8n:
    volumes:
      - ./orchestration/n8n_workflows:/home/node/.n8n/workflows
    environment:
      - N8N_BASIC_AUTH_ACTIVE=false
      - N8N_LOG_LEVEL=debug
    ports:
      - "5678:5678"
    
  postgres:
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=neural_forge_dev
    
  redis:
    ports:
      - "6379:6379"
    
  prometheus:
    ports:
      - "9090:9090"
    
  grafana:
    ports:
      - "3000:3000"
EOF
        log_success "Development override created"
    else
        log_success "Development override already exists"
    fi
}

# Setup pre-commit hooks
setup_hooks() {
    log_step "Setting up Git Hooks"
    
    if [ -d ".git" ]; then
        # Create pre-commit hook
        mkdir -p .git/hooks
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Neural Forge pre-commit hook

echo "🔍 Running pre-commit checks..."

# Run tests
if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
    echo "Running tests..."
    python -m pytest tests/unit/ -v
    if [ $? -ne 0 ]; then
        echo "❌ Tests failed. Commit aborted."
        exit 1
    fi
fi

# Check code formatting
if command -v black >/dev/null 2>&1; then
    echo "Checking code formatting..."
    black --check . || {
        echo "❌ Code formatting issues found. Run 'black .' to fix."
        exit 1
    }
fi

# Check imports
if command -v isort >/dev/null 2>&1; then
    echo "Checking import sorting..."
    isort --check-only . || {
        echo "❌ Import sorting issues found. Run 'isort .' to fix."
        exit 1
    }
fi

echo "✅ Pre-commit checks passed!"
EOF
        chmod +x .git/hooks/pre-commit
        log_success "Pre-commit hook installed"
    else
        log_warning "Not a Git repository - skipping hooks"
    fi
}

# Setup development tools
setup_dev_tools() {
    log_step "Setting up Development Tools"
    
    # Create Makefile for common tasks
    if [ ! -f "Makefile.dev" ]; then
        cat > Makefile.dev << 'EOF'
# Neural Forge Development Makefile
# =================================

.PHONY: help dev test lint format clean

help:
	@echo "🔧 Neural Forge Development Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup:"
	@echo "  dev        Start development environment"
	@echo "  test       Run all tests"
	@echo "  test-unit  Run unit tests only"
	@echo "  lint       Run code linting"
	@echo "  format     Format code"
	@echo ""
	@echo "Database:"
	@echo "  db-reset   Reset development database"
	@echo "  db-seed    Seed database with test data"
	@echo ""
	@echo "Services:"
	@echo "  start      Start all services"
	@echo "  stop       Stop all services"
	@echo "  logs       View service logs"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean      Clean temporary files"
	@echo "  update     Update dependencies"
	@echo ""

dev:
	@echo "🚀 Starting development environment..."
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "✅ Development environment ready!"
	@echo ""
	@echo "🌐 Available services:"
	@echo "  • Production Controller: http://localhost:7860"
	@echo "  • Analytics Engine: http://localhost:8501"
	@echo "  • ML Core API: http://localhost:8000/docs"
	@echo "  • N8N Workflows: http://localhost:5678"
	@echo "  • Grafana: http://localhost:3000"
	@echo "  • Prometheus: http://localhost:9090"

test:
	@echo "🧪 Running all tests..."
	python -m pytest tests/ -v --cov=./ --cov-report=html

test-unit:
	@echo "🧪 Running unit tests..."
	python -m pytest tests/unit/ -v

lint:
	@echo "🔍 Running linters..."
	flake8 .
	pylint **/*.py

format:
	@echo "✨ Formatting code..."
	black .
	isort .

db-reset:
	@echo "🗄️  Resetting database..."
	docker compose exec postgres psql -U neural_forge -c "DROP DATABASE IF EXISTS neural_forge_dev;"
	docker compose exec postgres psql -U neural_forge -c "CREATE DATABASE neural_forge_dev;"
	python -c "from database.models import create_tables; create_tables()"

db-seed:
	@echo "🌱 Seeding database..."
	python scripts/seed_database.py

start:
	docker compose up -d

stop:
	docker compose down

logs:
	docker compose logs -f

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf htmlcov/
	rm -rf .coverage

update:
	@echo "🔄 Updating dependencies..."
	pip install --upgrade -r requirements-dev.txt
	docker compose pull
EOF
        log_success "Development Makefile created"
    fi
    
    # Create VS Code settings
    if [ ! -d ".vscode" ]; then
        mkdir -p .vscode
        
        cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        "htmlcov": true
    },
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
EOF
        
        cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "ML Core API",
            "type": "python",
            "request": "launch",
            "program": "ml_core/api/main.py",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            },
            "console": "integratedTerminal"
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal"
        }
    ]
}
EOF
        log_success "VS Code configuration created"
    fi
}

# Build Docker images
build_images() {
    log_step "Building Docker Images"
    
    echo "Building development images..."
    docker compose -f docker-compose.yml -f docker-compose.dev.yml build --parallel
    
    log_success "Docker images built"
}

# Initialize database
init_database() {
    log_step "Initializing Database"
    
    # Start database service
    echo "Starting PostgreSQL..."
    docker compose up -d postgres
    
    # Wait for database to be ready
    echo "Waiting for database to be ready..."
    timeout=30
    while ! docker compose exec postgres pg_isready -U neural_forge >/dev/null 2>&1; do
        sleep 1
        timeout=$((timeout - 1))
        if [ $timeout -eq 0 ]; then
            log_error "Database failed to start"
            exit 1
        fi
    done
    
    # Create tables
    if [ -f "database/models/__init__.py" ]; then
        echo "Creating database tables..."
        python -c "
import sys
sys.path.append('.')
try:
    from database.models import create_tables
    create_tables()
    print('✅ Database tables created')
except Exception as e:
    print(f'⚠️  Could not create tables: {e}')
"
    else
        log_warning "Database models not found - skipping table creation"
    fi
    
    log_success "Database initialized"
}

# Final setup
final_setup() {
    log_step "Final Setup Steps"
    
    # Set executable permissions
    find scripts/ -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    chmod +x operations.sh 2>/dev/null || true
    
    # Create quick start script
    cat > start-dev.sh << 'EOF'
#!/bin/bash
# Neural Forge Development Quick Start

echo "🚀 Starting Neural Forge Development Environment..."
echo "=================================================="

# Activate Python environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Python environment activated"
fi

# Start services
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "🌐 Available URLs:"
echo "  • Production Controller: http://localhost:7860"
echo "  • Analytics Engine: http://localhost:8501" 
echo "  • ML Core API: http://localhost:8000/docs"
echo "  • N8N Workflows: http://localhost:5678"
echo "  • Grafana: http://localhost:3000 (admin/neuralforge2025)"
echo "  • Prometheus: http://localhost:9090"
echo ""
echo "🔧 Useful commands:"
echo "  • View logs: docker compose logs -f"
echo "  • Stop services: docker compose down"
echo "  • Run tests: python -m pytest"
echo "  • Health check: ./operations.sh health"
echo ""
EOF
    chmod +x start-dev.sh
    
    log_success "Quick start script created"
}

# Main setup process
main() {
    echo "Starting development environment setup..."
    echo "Current directory: $(pwd)"
    echo ""
    
    check_requirements
    setup_directories
    setup_config
    
    # Python setup (optional)
    if command -v python3 >/dev/null 2>&1; then
        setup_python
    else
        log_warning "Skipping Python setup - Python3 not found"
    fi
    
    setup_hooks
    setup_dev_tools
    build_images
    init_database
    final_setup
    
    echo ""
    echo -e "${GREEN}🎉 Development environment setup complete!${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "1. Review and customize .env file"
    echo "2. Run './start-dev.sh' to start development environment"
    echo "3. Open http://localhost:7860 to access the main interface"
    echo "4. Run './operations.sh health' to verify everything is working"
    echo ""
    echo -e "${YELLOW}📖 Documentation:${NC}"
    echo "• Development Guide: docs/DEVELOPMENT_GUIDE.md"
    echo "• API Documentation: http://localhost:8000/docs"
    echo "• Available commands: ./operations.sh help"
    echo ""
}

# Execute main function
main "$@"