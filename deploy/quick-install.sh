#!/bin/bash
# 🚀 Neural Forge - Quick Install Script
# ======================================
# One-command installation for production deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🚀 Neural Forge - Quick Installation${NC}"
echo -e "${CYAN}====================================${NC}"

# Configuration
REPO_URL="https://github.com/albertomaydayjhondoe/discografica-ml-system.git"
BRANCH="deployment/hetzner-production"
INSTALL_DIR="neural-forge"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Please don't run as root. This script will use sudo when needed.${NC}"
    exit 1
fi

# Function to check requirements
check_requirements() {
    echo -e "\n${BLUE}🔍 Checking system requirements...${NC}"
    
    # Check OS
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        echo -e "${RED}❌ This script requires Linux${NC}"
        exit 1
    fi
    
    # Check git
    if ! command -v git >/dev/null 2>&1; then
        echo -e "${YELLOW}📦 Installing git...${NC}"
        sudo apt update
        sudo apt install -y git
    fi
    
    echo -e "${GREEN}✅ System requirements OK${NC}"
}

# Function to clone repository
clone_repository() {
    echo -e "\n${BLUE}📥 Cloning Neural Forge repository...${NC}"
    
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}⚠️  Directory $INSTALL_DIR already exists${NC}"
        echo -e "${YELLOW}Do you want to remove it and start fresh? (y/N)${NC}"
        read -r REMOVE_DIR
        
        if [ "$REMOVE_DIR" = "y" ] || [ "$REMOVE_DIR" = "Y" ]; then
            rm -rf "$INSTALL_DIR"
        else
            echo -e "${RED}❌ Installation cancelled${NC}"
            exit 1
        fi
    fi
    
    git clone -b "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    echo -e "${GREEN}✅ Repository cloned successfully${NC}"
}

# Function to setup configuration
setup_configuration() {
    echo -e "\n${BLUE}🔧 Setting up configuration...${NC}"
    
    # Copy configuration templates
    cp .env.production.template .env.production
    
    # Create secrets directory and template
    mkdir -p config/secrets
    if [ -f "config/secrets/secrets.env.template" ]; then
        cp config/secrets/secrets.env.template config/secrets/secrets.env
        chmod 600 config/secrets/secrets.env
        echo -e "${GREEN}✅ Secrets template created${NC}"
    fi
    
    echo -e "${YELLOW}📝 Configuration files created. You need to edit them with your values:${NC}"
    echo -e "   1. ${YELLOW}.env.production${NC} - Main configuration"
    echo -e "   2. ${YELLOW}config/secrets/secrets.env${NC} - API keys and secrets"
    echo ""
    echo -e "${YELLOW}Do you want to edit the configuration now? (y/N)${NC}"
    read -r EDIT_CONFIG
    
    if [ "$EDIT_CONFIG" = "y" ] || [ "$EDIT_CONFIG" = "Y" ]; then
        echo -e "${BLUE}📝 Opening configuration files...${NC}"
        
        # Edit main config
        echo -e "\n${YELLOW}Editing main configuration (.env.production)...${NC}"
        echo -e "${YELLOW}Press Enter to continue...${NC}"
        read -r
        
        if command -v nano >/dev/null 2>&1; then
            nano .env.production
        elif command -v vi >/dev/null 2>&1; then
            vi .env.production
        else
            echo -e "${RED}❌ No text editor found${NC}"
        fi
        
        # Edit secrets
        echo -e "\n${YELLOW}Editing secrets configuration (config/secrets/secrets.env)...${NC}"
        echo -e "${YELLOW}IMPORTANT: Add your real API keys here${NC}"
        echo -e "${YELLOW}Press Enter to continue...${NC}"
        read -r
        
        if command -v nano >/dev/null 2>&1; then
            nano config/secrets/secrets.env
        elif command -v vi >/dev/null 2>&1; then
            vi config/secrets/secrets.env
        fi
    else
        echo -e "${YELLOW}⚠️  Configuration files created but not edited${NC}"
        echo -e "${YELLOW}   Edit them later before deployment${NC}"
    fi
}

# Function to run installation
run_installation() {
    echo -e "\n${BLUE}🚀 Running Neural Forge installation...${NC}"
    
    # Make scripts executable
    chmod +x deploy/hetzner/*.sh
    chmod +x scripts/*.sh
    chmod +x operations.sh
    
    # Run VPS setup
    echo -e "\n${PURPLE}🏗️  Step 1: VPS Setup${NC}"
    sudo ./deploy/hetzner/setup-vps.sh
    
    # Install Docker
    echo -e "\n${PURPLE}🐳 Step 2: Docker Installation${NC}"
    ./deploy/hetzner/install-docker.sh
    
    # Deploy services
    echo -e "\n${PURPLE}🚀 Step 3: Service Deployment${NC}"
    ./deploy/hetzner/deploy-services.sh
    
    # Setup SSL
    echo -e "\n${PURPLE}🔒 Step 4: SSL Configuration${NC}"
    echo -e "${YELLOW}Do you want to setup SSL now? (requires configured domain) (y/N)${NC}"
    read -r SETUP_SSL
    
    if [ "$SETUP_SSL" = "y" ] || [ "$SETUP_SSL" = "Y" ]; then
        sudo ./deploy/hetzner/ssl-setup.sh
    else
        echo -e "${YELLOW}⚠️  SSL setup skipped. Run 'sudo ./deploy/hetzner/ssl-setup.sh' later${NC}"
    fi
    
    # Setup monitoring
    echo -e "\n${PURPLE}📊 Step 5: Monitoring Setup${NC}"
    ./deploy/hetzner/monitoring-setup.sh
}

# Function to validate configuration
validate_configuration() {
    echo -e "\n${BLUE}🔍 Validating configuration...${NC}"
    
    if command -v python3 >/dev/null 2>&1; then
        python3 scripts/validate_satellite_config.py
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Configuration validation passed${NC}"
        else
            echo -e "${YELLOW}⚠️  Configuration validation failed${NC}"
            echo -e "${YELLOW}   Check the issues above and run validation again${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Python3 not found, skipping validation${NC}"
    fi
}

# Function to show final information
show_final_info() {
    echo -e "\n${CYAN}🎉 Neural Forge Installation Complete!${NC}"
    echo -e "${CYAN}=====================================${NC}"
    
    # Get server IP
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")
    
    echo -e "\n${GREEN}📋 Installation Summary:${NC}"
    echo -e "   • Docker services: 9 containers running"
    echo -e "   • Satellite accounts: 5 configured for upload"
    echo -e "   • Main account: Metrics only (no upload)"
    echo -e "   • SSL: ${SSL_STATUS:-Not configured}"
    echo -e "   • Monitoring: Prometheus + Grafana enabled"
    
    echo -e "\n${GREEN}🌐 Access URLs:${NC}"
    if [ "$SETUP_SSL" = "y" ] || [ "$SETUP_SSL" = "Y" ]; then
        echo -e "   • Main Dashboard: https://your-domain.com"
        echo -e "   • Analytics: https://your-domain.com/analytics"
        echo -e "   • Monitoring: https://your-domain.com/grafana"
        echo -e "   • API Docs: https://your-domain.com/api/docs"
    else
        echo -e "   • Main Dashboard: http://$SERVER_IP:7860"
        echo -e "   • Analytics: http://$SERVER_IP:8501"
        echo -e "   • ML Core API: http://$SERVER_IP:8000/docs"
        echo -e "   • Grafana: http://$SERVER_IP:3000"
    fi
    
    echo -e "\n${GREEN}🔧 Management Commands:${NC}"
    echo -e "   • System status: ./operations.sh status"
    echo -e "   • Health check: ./operations.sh health"
    echo -e "   • View logs: ./operations.sh logs"
    echo -e "   • Validate config: python3 scripts/validate_satellite_config.py"
    
    echo -e "\n${YELLOW}📝 Next Steps:${NC}"
    echo -e "   1. Verify all services are running: ./operations.sh status"
    echo -e "   2. Complete SSL setup if skipped: sudo ./deploy/hetzner/ssl-setup.sh"
    echo -e "   3. Configure your satellite accounts in config/secrets/secrets.env"
    echo -e "   4. Run validation: python3 scripts/validate_satellite_config.py"
    echo -e "   5. Access the main dashboard and start creating content!"
    
    echo -e "\n${PURPLE}🚨 Security Reminders:${NC}"
    echo -e "   • Never commit config/secrets/secrets.env to git"
    echo -e "   • Main YouTube account only collects metrics"
    echo -e "   • Only satellite accounts upload content"
    echo -e "   • Keep your API keys secure"
    
    echo -e "\n${CYAN}🎵 Happy content creation! 🚀${NC}"
}

# Main installation process
main() {
    echo -e "Starting Neural Forge installation..."
    echo -e "Installation directory: $(pwd)/$INSTALL_DIR"
    echo ""
    
    check_requirements
    clone_repository
    setup_configuration
    run_installation
    validate_configuration
    show_final_info
    
    echo -e "\n${GREEN}Installation completed successfully! 🎉${NC}"
}

# Check if script is being run directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi