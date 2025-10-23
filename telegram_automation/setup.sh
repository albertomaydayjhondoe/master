#!/bin/bash

# Like4Like Telegram Bot Setup Script
# Sets up the environment and dependencies for the Like4Like automation system

set -e

echo "🚀 Setting up Like4Like Telegram Bot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Python 3.9+ is installed
check_python() {
    print_status "Checking Python version..."
    
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

# Check if PostgreSQL is installed
check_postgresql() {
    print_status "Checking PostgreSQL..."
    
    if command -v psql &> /dev/null; then
        PG_VERSION=$(psql --version | cut -d' ' -f3)
        print_success "PostgreSQL $PG_VERSION found"
    else
        print_warning "PostgreSQL not found. Please install PostgreSQL 13+"
        print_status "Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
        print_status "CentOS/RHEL: sudo yum install postgresql-server postgresql-contrib"
        print_status "macOS: brew install postgresql"
    fi
}

# Check if Chrome is installed (for Selenium)
check_chrome() {
    print_status "Checking Google Chrome..."
    
    if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null; then
        print_success "Chrome/Chromium found"
    else
        print_warning "Chrome not found. Installing Chrome..."
        
        # Install Chrome on Linux
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
            echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
            sudo apt-get update
            sudo apt-get install -y google-chrome-stable
            print_success "Chrome installed successfully"
        else
            print_warning "Please install Google Chrome manually"
        fi
    fi
}

# Create virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    print_success "Virtual environment activated and pip upgraded"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p data/exports
    mkdir -p data/screenshots
    mkdir -p config/secrets
    
    print_success "Directories created"
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    # Check if PostgreSQL service is running
    if systemctl is-active --quiet postgresql || service postgresql status &> /dev/null; then
        print_success "PostgreSQL service is running"
        
        # Create database and user (if they don't exist)
        sudo -u postgres psql -c "CREATE DATABASE like4like_bot;" 2>/dev/null || print_status "Database already exists"
        sudo -u postgres psql -c "CREATE USER like4like_user WITH PASSWORD 'like4like_pass';" 2>/dev/null || print_status "User already exists"
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE like4like_bot TO like4like_user;" 2>/dev/null
        
        # Run database schema
        if [ -f "database/schema.sql" ]; then
            PGPASSWORD=like4like_pass psql -h localhost -U like4like_user -d like4like_bot -f database/schema.sql
            print_success "Database schema applied"
        else
            print_warning "Database schema file not found"
        fi
    else
        print_warning "PostgreSQL service not running. Please start it manually:"
        print_status "sudo systemctl start postgresql"
    fi
}

# Create configuration template
create_config() {
    print_status "Creating configuration template..."
    
    if [ ! -f "config/secrets/.env" ]; then
        cat > config/secrets/.env << EOF
# Telegram API Configuration
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_BOT_TOKEN=your_bot_token_here  # Optional
TELEGRAM_PHONE=+1234567890

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=like4like_bot
DB_USER=like4like_user
DB_PASSWORD=like4like_pass

# GoLogin Configuration
GOLOGIN_API_TOKEN=your_gologin_token_here
GOLOGIN_MAX_PROFILES=3
GOLOGIN_ROTATION_HOURS=2

# YouTube Executor Configuration
YOUTUBE_MIN_WATCH_TIME=30
YOUTUBE_MAX_WATCH_TIME=300
YOUTUBE_MAX_ACTIONS_PER_DAY=50
YOUTUBE_ENABLE_COMMENTS=true

# Security Configuration
SECURITY_HUMAN_DELAYS=true
SECURITY_AUTO_ROTATE=true
SECURITY_BAN_DETECTION=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/like4like_bot.log
EOF
        print_success "Configuration template created at config/secrets/.env"
        print_warning "Please edit config/secrets/.env with your actual credentials"
    else
        print_status "Configuration file already exists"
    fi
}

# Create systemd service file
create_service() {
    print_status "Creating systemd service file..."
    
    CURRENT_DIR=$(pwd)
    SERVICE_FILE="/etc/systemd/system/like4like-bot.service"
    
    sudo tee $SERVICE_FILE > /dev/null << EOF
[Unit]
Description=Like4Like Telegram Bot
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=like4like-bot

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    print_success "Systemd service created"
    print_status "To start the service: sudo systemctl start like4like-bot"
    print_status "To enable auto-start: sudo systemctl enable like4like-bot"
}

# Main setup function
main() {
    print_status "Starting Like4Like Telegram Bot setup..."
    
    # Check system requirements
    check_python
    check_postgresql
    check_chrome
    
    # Setup Python environment
    setup_venv
    install_dependencies
    
    # Setup project structure
    create_directories
    create_config
    
    # Setup database
    setup_database
    
    # Create service file
    if [ "$EUID" -eq 0 ] || [ -w "/etc/systemd/system" ]; then
        create_service
    else
        print_warning "Cannot create systemd service (no sudo access)"
        print_status "You can run the bot manually with: python main.py"
    fi
    
    print_success "Setup completed successfully!"
    echo
    print_status "Next steps:"
    echo "1. Edit config/secrets/.env with your credentials"
    echo "2. Make sure PostgreSQL is running"
    echo "3. Run the bot: python main.py"
    echo "   Or use systemd: sudo systemctl start like4like-bot"
    echo
    print_warning "Don't forget to get your Telegram API credentials from https://my.telegram.org"
}

# Run main function
main "$@"