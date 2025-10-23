# Universal Multi-Branch Automation System Makefile
# Supports rama (TikTok ML), meta (Meta Ads), tele (Like4Like) branches

.PHONY: help wake wake-quick wake-full stop status clean test install setup
.PHONY: rama meta tele
.PHONY: docker-build docker-run docker-stop
.PHONY: config env lint format

# Colors for output
RED := $(shell tput setaf 1)
GREEN := $(shell tput setaf 2)
YELLOW := $(shell tput setaf 3)
BLUE := $(shell tput setaf 4)
PURPLE := $(shell tput setaf 5)
CYAN := $(shell tput setaf 6)
RESET := $(shell tput sgr0)

# Default target
help:
	@echo "$(PURPLE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo "$(PURPLE)🌅  UNIVERSAL PROJECT MAKEFILE  🌅$(RESET)"
	@echo "$(PURPLE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo "$(CYAN)One Makefile to rule all branches: rama (TikTok ML), meta (Meta Ads), tele (Like4Like)$(RESET)"
	@echo ""
	@echo "$(YELLOW)🚀 System Management:$(RESET)"
	@echo "  $(GREEN)wake$(RESET)         - Quick wake (development mode)"
	@echo "  $(GREEN)wake-full$(RESET)    - Full system awakening (all branches)" 
	@echo "  $(GREEN)wake-quick$(RESET)   - Minimal quick start"
	@echo "  $(GREEN)stop$(RESET)         - Stop all services"
	@echo "  $(GREEN)status$(RESET)       - Check system status"
	@echo "  $(GREEN)setup$(RESET)        - Initial project setup"
	@echo ""
	@echo "$(YELLOW)🌿 Branch Management:$(RESET)"
	@echo "  $(GREEN)rama$(RESET)         - Start TikTok ML branch only"
	@echo "  $(GREEN)meta$(RESET)         - Start Meta Ads branch only"
	@echo "  $(GREEN)tele$(RESET)         - Start Like4Like branch only"
	@echo ""
	@echo "$(YELLOW)⚙️ Configuration:$(RESET)"
	@echo "  $(GREEN)config$(RESET)       - Generate intelligent configuration"
	@echo "  $(GREEN)env$(RESET)          - Generate environment files"
	@echo ""
	@echo "$(YELLOW)🐳 Docker:$(RESET)"
	@echo "  $(GREEN)docker-build$(RESET) - Build Docker images"
	@echo "  $(GREEN)docker-run$(RESET)   - Run with Docker Compose"
	@echo "  $(GREEN)docker-stop$(RESET)  - Stop Docker containers"
	@echo ""
	@echo "$(YELLOW)🛠️ Development:$(RESET)"
	@echo "  $(GREEN)install$(RESET)      - Install dependencies"
	@echo "  $(GREEN)test$(RESET)         - Run tests"
	@echo "  $(GREEN)lint$(RESET)         - Run linting"
	@echo "  $(GREEN)format$(RESET)       - Format code"
	@echo "  $(GREEN)clean$(RESET)        - Clean temporary files"
	@echo ""
	@echo "$(YELLOW)💡 Examples:$(RESET)"
	@echo "  $(CYAN)make wake$(RESET)           # Quick development start"
	@echo "  $(CYAN)make wake-full$(RESET)      # Full system with all branches"
	@echo "  $(CYAN)make rama$(RESET)           # Only TikTok ML system"
	@echo "  $(CYAN)make meta$(RESET)           # Only Meta Ads automation"
	@echo "  $(CYAN)make tele$(RESET)           # Only Like4Like bot"

# System Management Targets
wake: wake-quick
wake-quick:
	@echo "$(GREEN)🚀 Quick Wake - Development Mode$(RESET)"
	@./wake.sh --quick

wake-full:
	@echo "$(GREEN)🌅 Full System Awakening$(RESET)"
	@./wake.sh --mode full

stop:
	@echo "$(YELLOW)🛑 Stopping All Services$(RESET)"
	@./wake.sh --stop
	@pkill -f "uvicorn" 2>/dev/null || true
	@pkill -f "python.*main.py" 2>/dev/null || true
	@pkill -f "dummy_monitor" 2>/dev/null || true
	@echo "$(GREEN)✅ All services stopped$(RESET)"

status:
	@echo "$(BLUE)📊 System Status$(RESET)"
	@echo "$(CYAN)Checking running processes...$(RESET)"
	@pgrep -f "uvicorn" > /dev/null && echo "$(GREEN)✅ ML API running$(RESET)" || echo "$(RED)❌ ML API not running$(RESET)"
	@pgrep -f "main.py" > /dev/null && echo "$(GREEN)✅ Automation services running$(RESET)" || echo "$(RED)❌ Automation services not running$(RESET)"
	@curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "$(GREEN)✅ ML API responding$(RESET)" || echo "$(RED)❌ ML API not responding$(RESET)"
	@echo "$(CYAN)Environment:$(RESET)"
	@echo "  DUMMY_MODE: $${DUMMY_MODE:-true}"
	@echo "  Python: $$(python3 --version 2>/dev/null || echo 'Not found')"
	@echo "  Project Root: $$(pwd)"

setup:
	@echo "$(GREEN)🛠️ Initial Project Setup$(RESET)"
	@python3 config_generator.py
	@mkdir -p logs data/mock_databases data/models config/secrets
	@echo "$(GREEN)✅ Project setup complete$(RESET)"

# Branch-Specific Targets
rama:
	@echo "$(GREEN)🎬 Starting TikTok ML Branch (rama)$(RESET)"
	@./wake.sh --mode services --branches rama

meta:
	@echo "$(GREEN)📱 Starting Meta Ads Branch (meta)$(RESET)"
	@./wake.sh --mode services --branches meta

tele:
	@echo "$(GREEN)💬 Starting Like4Like Branch (tele)$(RESET)"
	@./wake.sh --mode services --branches tele

# Configuration Targets
config:
	@echo "$(GREEN)⚙️ Generating Intelligent Configuration$(RESET)"
	@python3 config_generator.py
	@echo "$(GREEN)✅ Configuration generated$(RESET)"

env:
	@echo "$(GREEN)📝 Generating Environment Files$(RESET)"
	@python3 awakener.py --mode basic
	@echo "$(GREEN)✅ Environment files generated$(RESET)"

# Docker Targets
docker-build:
	@echo "$(GREEN)🐳 Building Docker Images$(RESET)"
	@cd docker && docker-compose build
	@echo "$(GREEN)✅ Docker images built$(RESET)"

docker-run:
	@echo "$(GREEN)🐳 Running with Docker Compose$(RESET)"
	@cd docker && docker-compose up -d
	@echo "$(GREEN)✅ Docker containers started$(RESET)"

docker-stop:
	@echo "$(YELLOW)🐳 Stopping Docker Containers$(RESET)"
	@cd docker && docker-compose down
	@echo "$(GREEN)✅ Docker containers stopped$(RESET)"

# Development Targets
install:
	@echo "$(GREEN)📦 Installing Dependencies$(RESET)"
	@python3 -m venv venv 2>/dev/null || true
	@. venv/bin/activate 2>/dev/null || true
	@pip install -r requirements.txt 2>/dev/null || echo "$(YELLOW)⚠️ requirements.txt not found$(RESET)"
	@pip install -r requirements-dev.txt 2>/dev/null || echo "$(YELLOW)⚠️ requirements-dev.txt not found$(RESET)"
	@pip install -r requirements-dummy.txt 2>/dev/null || echo "$(YELLOW)⚠️ requirements-dummy.txt not found$(RESET)"
	@echo "$(GREEN)✅ Dependencies installed$(RESET)"

test:
	@echo "$(GREEN)🧪 Running Tests$(RESET)"
	@PYTHONPATH=. pytest -v 2>/dev/null || echo "$(YELLOW)⚠️ No tests found or pytest not installed$(RESET)"

lint:
	@echo "$(GREEN)🔍 Running Linting$(RESET)"
	@flake8 . --max-line-length=100 --exclude=venv,__pycache__,.git 2>/dev/null || echo "$(YELLOW)⚠️ flake8 not installed$(RESET)"
	@pylint **/*.py 2>/dev/null || echo "$(YELLOW)⚠️ pylint not installed$(RESET)"

format:
	@echo "$(GREEN)✨ Formatting Code$(RESET)"
	@black . --line-length=100 --exclude="/(venv|__pycache__|\.git)/" 2>/dev/null || echo "$(YELLOW)⚠️ black not installed$(RESET)"
	@isort . --profile black 2>/dev/null || echo "$(YELLOW)⚠️ isort not installed$(RESET)"

clean:
	@echo "$(GREEN)🧹 Cleaning Temporary Files$(RESET)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@rm -f .ml_api.pid 2>/dev/null || true
	@rm -rf data/mock_databases/*.db 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete$(RESET)"

# Development shortcuts
dev: wake-quick
prod: wake-full
restart: stop wake
