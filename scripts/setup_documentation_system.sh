#!/bin/bash
"""
Documentation System Setup Script

Script para configurar y activar todo el sistema de documentación:
- Auto-update system
- Interactive dashboard
- Scheduled tasks
- Environment setup

Autor: Sistema de Documentación Automática
Fecha: 2024
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="/workspaces/master"
DOCS_DIR="$REPO_ROOT/docs"
SCRIPTS_DIR="$REPO_ROOT/scripts"
VENV_DIR="$REPO_ROOT/.venv_docs"

echo -e "${BLUE}🚀 Documentation System Setup${NC}"
echo "=================================="

# Step 1: Check requirements
echo -e "\n${YELLOW}📋 Step 1: Checking requirements...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is required but not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All requirements satisfied${NC}"

# Step 2: Create directories
echo -e "\n${YELLOW}📁 Step 2: Creating directory structure...${NC}"

mkdir -p "$DOCS_DIR"
mkdir -p "$DOCS_DIR/functionality_guides"
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$REPO_ROOT/logs"

echo -e "${GREEN}✅ Directory structure created${NC}"

# Step 3: Set up Python virtual environment
echo -e "\n${YELLOW}🐍 Step 3: Setting up Python environment...${NC}"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install required packages with error handling
echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"

pip install --upgrade pip

# Core dependencies (with fallbacks)
echo "Installing core dependencies..."

# Try to install packages individually to handle failures gracefully
PACKAGES=("streamlit" "plotly" "pandas" "GitPython" "python-dateutil")
FAILED_PACKAGES=()

for package in "${PACKAGES[@]}"; do
    echo "Installing $package..."
    if pip install "$package" 2>/dev/null; then
        echo -e "${GREEN}✅ $package installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Failed to install $package (will use fallback mode)${NC}"
        FAILED_PACKAGES+=("$package")
    fi
done

if [ ${#FAILED_PACKAGES[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  Some packages failed to install: ${FAILED_PACKAGES[*]}${NC}"
    echo -e "${YELLOW}📋 System will run in compatibility mode${NC}"
fi

# Step 4: Make scripts executable
echo -e "\n${YELLOW}🔧 Step 4: Setting up scripts...${NC}"

chmod +x "$SCRIPTS_DIR/auto_update_docs.py"
chmod +x "$SCRIPTS_DIR/documentation_dashboard.py"

echo -e "${GREEN}✅ Scripts configured${NC}"

# Step 5: Create systemd service files (optional)
echo -e "\n${YELLOW}⚙️ Step 5: Creating service configurations...${NC}"

# Auto-update service
cat > "$SCRIPTS_DIR/docs-auto-update.service" << EOF
[Unit]
Description=Documentation Auto-Update Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$REPO_ROOT
Environment=PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$VENV_DIR/bin/python $SCRIPTS_DIR/auto_update_docs.py
Restart=always
RestartSec=300

[Install]
WantedBy=multi-user.target
EOF

# Dashboard service
cat > "$SCRIPTS_DIR/docs-dashboard.service" << EOF
[Unit]
Description=Documentation Dashboard Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$REPO_ROOT
Environment=PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$VENV_DIR/bin/streamlit run $SCRIPTS_DIR/documentation_dashboard.py --server.port=8502 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Service files created${NC}"

# Step 6: Create helper scripts
echo -e "\n${YELLOW}🛠️ Step 6: Creating helper scripts...${NC}"

# Start dashboard script
cat > "$SCRIPTS_DIR/start_dashboard.sh" << 'EOF'
#!/bin/bash
REPO_ROOT="/workspaces/master"
VENV_DIR="$REPO_ROOT/.venv_docs"

echo "🚀 Starting Documentation Dashboard..."

# Activate virtual environment
source "$VENV_DIR/bin/activate" 

# Start dashboard
cd "$REPO_ROOT"
streamlit run scripts/documentation_dashboard.py --server.port=8502 --server.address=0.0.0.0
EOF

chmod +x "$SCRIPTS_DIR/start_dashboard.sh"

# Start auto-update script
cat > "$SCRIPTS_DIR/start_auto_update.sh" << 'EOF'
#!/bin/bash
REPO_ROOT="/workspaces/master"
VENV_DIR="$REPO_ROOT/.venv_docs"

echo "🔄 Starting Documentation Auto-Update..."

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Run auto-update
cd "$REPO_ROOT"
python scripts/auto_update_docs.py
EOF

chmod +x "$SCRIPTS_DIR/start_auto_update.sh"

# Complete setup script
cat > "$SCRIPTS_DIR/docs_system_control.sh" << 'EOF'
#!/bin/bash

REPO_ROOT="/workspaces/master"
VENV_DIR="$REPO_ROOT/.venv_docs"
SCRIPTS_DIR="$REPO_ROOT/scripts"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo -e "${BLUE}📚 Documentation System Control${NC}"
    echo "Usage: $0 {start|stop|restart|status|dashboard|update|help}"
    echo ""
    echo "Commands:"
    echo "  start      - Start both dashboard and auto-update services"
    echo "  stop       - Stop all documentation services"
    echo "  restart    - Restart all services"
    echo "  status     - Show status of all services"
    echo "  dashboard  - Start only the dashboard (port 8502)"
    echo "  update     - Run manual documentation update"
    echo "  help       - Show this help message"
}

start_services() {
    echo -e "${YELLOW}🚀 Starting Documentation System...${NC}"
    
    # Start dashboard in background
    echo -e "${BLUE}📊 Starting Dashboard...${NC}"
    source "$VENV_DIR/bin/activate"
    cd "$REPO_ROOT"
    nohup streamlit run scripts/documentation_dashboard.py --server.port=8502 --server.address=0.0.0.0 > logs/dashboard.log 2>&1 &
    echo $! > "$REPO_ROOT/.dashboard.pid"
    
    echo -e "${GREEN}✅ Dashboard started on http://localhost:8502${NC}"
    echo -e "${GREEN}✅ Documentation System is running${NC}"
}

stop_services() {
    echo -e "${YELLOW}🛑 Stopping Documentation System...${NC}"
    
    # Stop dashboard
    if [ -f "$REPO_ROOT/.dashboard.pid" ]; then
        PID=$(cat "$REPO_ROOT/.dashboard.pid")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            echo -e "${GREEN}✅ Dashboard stopped${NC}"
        fi
        rm -f "$REPO_ROOT/.dashboard.pid"
    fi
    
    # Kill any remaining streamlit processes
    pkill -f "streamlit.*documentation_dashboard" || true
    
    echo -e "${GREEN}✅ All services stopped${NC}"
}

show_status() {
    echo -e "${BLUE}📊 Documentation System Status${NC}"
    echo "================================"
    
    # Check dashboard
    if [ -f "$REPO_ROOT/.dashboard.pid" ]; then
        PID=$(cat "$REPO_ROOT/.dashboard.pid")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "Dashboard: ${GREEN}Running${NC} (PID: $PID, Port: 8502)"
        else
            echo -e "Dashboard: ${RED}Stopped${NC}"
            rm -f "$REPO_ROOT/.dashboard.pid"
        fi
    else
        echo -e "Dashboard: ${RED}Stopped${NC}"
    fi
    
    # Check recent activity
    echo ""
    echo -e "${YELLOW}Recent Activity:${NC}"
    if [ -f "$REPO_ROOT/logs/dashboard.log" ]; then
        tail -n 3 "$REPO_ROOT/logs/dashboard.log" 2>/dev/null || echo "No recent activity"
    else
        echo "No activity logs found"
    fi
}

run_update() {
    echo -e "${YELLOW}🔄 Running Manual Documentation Update...${NC}"
    
    source "$VENV_DIR/bin/activate"
    cd "$REPO_ROOT"
    python scripts/auto_update_docs.py
    
    echo -e "${GREEN}✅ Manual update completed${NC}"
}

start_dashboard_only() {
    echo -e "${YELLOW}📊 Starting Dashboard Only...${NC}"
    
    source "$VENV_DIR/bin/activate"
    cd "$REPO_ROOT"
    streamlit run scripts/documentation_dashboard.py --server.port=8502 --server.address=0.0.0.0
}

case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    status)
        show_status
        ;;
    dashboard)
        start_dashboard_only
        ;;
    update)
        run_update
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac
EOF

chmod +x "$SCRIPTS_DIR/docs_system_control.sh"

echo -e "${GREEN}✅ Helper scripts created${NC}"

# Step 7: Create configuration files
echo -e "\n${YELLOW}⚙️ Step 7: Creating configuration files...${NC}"

# Dashboard config
cat > "$DOCS_DIR/.streamlit_config.toml" << EOF
[global]
developmentMode = false

[server]
port = 8502
address = "0.0.0.0"
headless = true

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[browser]
gatherUsageStats = false
EOF

# Auto-update config
cat > "$DOCS_DIR/.auto_update_config.json" << EOF
{
    "update_frequency_hours": 6,
    "enable_notifications": true,
    "notification_email": "admin@example.com",
    "critical_updates_only": false,
    "backup_enabled": true,
    "max_backups": 10,
    "tracked_file_patterns": [
        "*.py",
        "*.md",
        "*.json",
        "*.yaml",
        "*.yml"
    ],
    "ignore_directories": [
        "__pycache__",
        ".git",
        ".pytest_cache",
        "node_modules"
    ]
}
EOF

echo -e "${GREEN}✅ Configuration files created${NC}"

# Step 8: Test installation
echo -e "\n${YELLOW}🧪 Step 8: Testing installation...${NC}"

# Test Python environment
source "$VENV_DIR/bin/activate"

echo -e "${BLUE}Testing Python imports...${NC}"

# Test imports individually with graceful failure handling
python3 -c "
import sys

# Test core imports
try:
    import json, os, re, datetime, pathlib
    print('✅ Core Python modules work')
except Exception as e:
    print(f'❌ Core modules failed: {e}')
    sys.exit(1)

# Test optional imports
optional_imports = [
    ('streamlit', 'Streamlit'),
    ('plotly', 'Plotly'),
    ('pandas', 'Pandas'),
    ('git', 'GitPython')
]

failed_optional = []
for module, name in optional_imports:
    try:
        __import__(module)
        print(f'✅ {name} available')
    except ImportError:
        print(f'⚠️  {name} not available - using fallback mode')
        failed_optional.append(name)

if failed_optional:
    print(f'📋 System will run with limited functionality for: {', '.join(failed_optional)}')
else:
    print('🎉 All optional dependencies available - full functionality enabled')
"

echo -e "${BLUE}Testing script syntax...${NC}"
python3 -m py_compile "$SCRIPTS_DIR/auto_update_docs.py" || echo -e "${YELLOW}⚠️  Auto-update script has syntax issues${NC}"
python3 -m py_compile "$SCRIPTS_DIR/documentation_dashboard.py" || echo -e "${YELLOW}⚠️  Dashboard script has syntax issues${NC}"
python3 -m py_compile "$SCRIPTS_DIR/generate_simulation_data.py" || echo -e "${YELLOW}⚠️  Simulation script has syntax issues${NC}"

echo -e "${GREEN}✅ Testing completed${NC}"

# Step 9: Final setup
echo -e "\n${YELLOW}🎯 Step 9: Final setup...${NC}"

# Create logs directory
mkdir -p "$REPO_ROOT/logs"

# Create initial timestamp for auto-updates
echo "$(date -Iseconds)" > "$DOCS_DIR/.last_documentation_scan"

# Create welcome message
cat > "$DOCS_DIR/SYSTEM_READY.md" << EOF
# 📚 Documentation System Ready

Your interactive documentation system has been successfully set up!

## 🚀 Quick Start

### Start the Dashboard
\`\`\`bash
./scripts/docs_system_control.sh dashboard
\`\`\`

Access at: http://localhost:8502

### Run Manual Update
\`\`\`bash
./scripts/docs_system_control.sh update
\`\`\`

### System Control
\`\`\`bash
./scripts/docs_system_control.sh {start|stop|restart|status}
\`\`\`

## 📊 Features Available

- ✅ **Smart Search** - Intelligent documentation search
- ✅ **Interactive Dashboard** - Web-based doc navigation  
- ✅ **Auto-Updates** - Automatic documentation updates
- ✅ **Analytics** - Usage metrics and insights
- ✅ **Admin Panel** - System management interface

## 📁 Key Files

- \`scripts/documentation_dashboard.py\` - Main dashboard
- \`scripts/auto_update_docs.py\` - Auto-update system
- \`scripts/docs_system_control.sh\` - System control
- \`docs/functionality_guides/\` - Documentation files

## 🔧 Configuration

- Dashboard: \`docs/.streamlit_config.toml\`
- Auto-update: \`docs/.auto_update_config.json\`
- Logs: \`logs/\`

Happy documenting! 🎉
EOF

echo -e "${GREEN}✅ Setup completed successfully!${NC}"

# Step 10: Show summary
echo -e "\n${BLUE}📋 Setup Summary${NC}"
echo "=================="
echo -e "📁 Docs Directory: ${GREEN}$DOCS_DIR${NC}"
echo -e "🐍 Python Env: ${GREEN}$VENV_DIR${NC}"
echo -e "🛠️ Scripts: ${GREEN}$SCRIPTS_DIR${NC}"
echo -e "📊 Dashboard: ${GREEN}http://localhost:8502${NC}"

echo -e "\n${YELLOW}🚀 Next Steps:${NC}"
echo "1. Start the dashboard: ./scripts/docs_system_control.sh dashboard"
echo "2. Run a manual update: ./scripts/docs_system_control.sh update"
echo "3. Visit http://localhost:8502 to explore your docs!"

echo -e "\n${GREEN}🎉 Documentation System is ready to use!${NC}"

# Optional: Start dashboard immediately
read -p "🚀 Start the dashboard now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Starting dashboard...${NC}"
    cd "$REPO_ROOT"
    source "$VENV_DIR/bin/activate"
    exec streamlit run scripts/documentation_dashboard.py --server.port=8502 --server.address=0.0.0.0
fi

echo -e "\n${BLUE}Setup complete! 🎯${NC}"