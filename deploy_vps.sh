#!/bin/bash
"""
VPS Deployment Script for TikTok Viral ML System
Automated deployment to Hetzner CX21 or compatible VPS
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
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

# Configuration variables
VPS_USER="metasystem"
APP_DIR="/home/${VPS_USER}/apps/metasystem-core"
VENV_DIR="${APP_DIR}/venv"
LOG_DIR="/var/log/metasystem"
BACKUP_DIR="/home/${VPS_USER}/backups"
SCRIPTS_DIR="/home/${VPS_USER}/scripts"

# Function to create system user
create_system_user() {
    log_info "Creating system user: ${VPS_USER}"
    
    if ! id "${VPS_USER}" &>/dev/null; then
        adduser --disabled-password --gecos "" ${VPS_USER}
        usermod -aG sudo ${VPS_USER}
        log_success "User ${VPS_USER} created"
    else
        log_warning "User ${VPS_USER} already exists"
    fi
    
    # Create SSH directory and copy keys
    mkdir -p /home/${VPS_USER}/.ssh
    if [ -f /root/.ssh/authorized_keys ]; then
        cp /root/.ssh/authorized_keys /home/${VPS_USER}/.ssh/
        chown -R ${VPS_USER}:${VPS_USER} /home/${VPS_USER}/.ssh
        chmod 700 /home/${VPS_USER}/.ssh
        chmod 600 /home/${VPS_USER}/.ssh/authorized_keys
        log_success "SSH keys configured for ${VPS_USER}"
    fi
}

# Function to install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."
    
    apt update && apt upgrade -y
    
    # Core build tools
    apt install -y build-essential git curl wget vim htop tree
    
    # Python 3.11
    apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
    
    # Media processing
    apt install -y ffmpeg
    
    # Database systems
    apt install -y postgresql postgresql-contrib redis-server
    
    # Web server
    apt install -y nginx
    
    # SSL certificates
    apt install -y certbot python3-certbot-nginx
    
    # Monitoring tools
    apt install -y htop iotop nethogs
    
    # System utilities
    apt install -y supervisor logrotate fail2ban
    
    log_success "System dependencies installed"
}

# Function to configure firewall
configure_firewall() {
    log_info "Configuring UFW firewall..."
    
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH, HTTP, HTTPS
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Allow specific application ports (optional, behind nginx)
    # ufw allow 7860/tcp  # Gradio
    # ufw allow 8501/tcp  # Streamlit  
    # ufw allow 8000/tcp  # ML API
    
    ufw --force enable
    log_success "Firewall configured"
}

# Function to secure SSH
secure_ssh() {
    log_info "Securing SSH configuration..."
    
    # Backup original config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
    
    # Apply security settings
    sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
    
    # Restart SSH service
    systemctl restart sshd
    log_success "SSH secured"
}

# Function to configure databases
configure_databases() {
    log_info "Configuring databases..."
    
    # Start services
    systemctl start postgresql redis-server
    systemctl enable postgresql redis-server
    
    # Create PostgreSQL user and database
    sudo -u postgres psql -c "CREATE USER ${VPS_USER} WITH PASSWORD 'metasystem_secure_2024';"
    sudo -u postgres psql -c "CREATE DATABASE metasystem_db OWNER ${VPS_USER};"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE metasystem_db TO ${VPS_USER};"
    
    log_success "Databases configured"
}

# Function to create directory structure
create_directories() {
    log_info "Creating directory structure..."
    
    # Create directories as VPS_USER
    sudo -u ${VPS_USER} mkdir -p ${APP_DIR}
    sudo -u ${VPS_USER} mkdir -p ${BACKUP_DIR}
    sudo -u ${VPS_USER} mkdir -p ${SCRIPTS_DIR}
    
    # Create log directory
    mkdir -p ${LOG_DIR}
    chown -R ${VPS_USER}:${VPS_USER} ${LOG_DIR}
    
    log_success "Directory structure created"
}

# Function to deploy application code
deploy_application() {
    log_info "Deploying application code..."
    
    # Clone repository as VPS_USER
    sudo -u ${VPS_USER} bash -c "
        cd /home/${VPS_USER}/apps
        if [ ! -d metasystem-core ]; then
            git clone https://github.com/albertomaydayjhondoe/master.git metasystem-core
        fi
        cd metasystem-core
        git checkout experimental/vps-migration
        git pull origin experimental/vps-migration
    "
    
    log_success "Application code deployed"
}

# Function to create Python virtual environment
setup_python_env() {
    log_info "Setting up Python virtual environment..."
    
    sudo -u ${VPS_USER} bash -c "
        cd ${APP_DIR}
        python3.11 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip setuptools wheel
        pip install -r requirements-vps.txt
    "
    
    log_success "Python environment configured"
}

# Function to create environment file
create_env_file() {
    log_info "Creating environment configuration..."
    
    sudo -u ${VPS_USER} bash -c "cat > ${APP_DIR}/.env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://metasystem:metasystem_secure_2024@localhost:5432/metasystem_db
REDIS_URL=redis://localhost:6379/0

# Application Configuration
SECRET_KEY=vps_production_secret_key_$(openssl rand -hex 32)
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
VPS_MODE=true
DUMMY_MODE=false

# API Keys (to be configured)
META_API_KEY=your_meta_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here

# VPS Specific
MAX_WORKERS=2
WORKER_TIMEOUT=300
GRADIO_SERVER_PORT=7860
STREAMLIT_SERVER_PORT=8501
ML_API_SERVER_PORT=8000
EOF"
    
    chmod 600 ${APP_DIR}/.env
    log_success "Environment file created"
}

# Function to create systemd services
create_systemd_services() {
    log_info "Creating systemd services..."
    
    # Gradio Trigger Manager
    cat > /etc/systemd/system/metasystem-gradio.service << EOF
[Unit]
Description=MetaSystem Gradio Trigger Manager
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=${VPS_USER}
Group=${VPS_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_DIR}/bin/python gradio_trigger_manager.py
Restart=always
RestartSec=10
StandardOutput=append:${LOG_DIR}/gradio.log
StandardError=append:${LOG_DIR}/gradio.error.log
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Streamlit Analytics
    cat > /etc/systemd/system/metasystem-streamlit.service << EOF
[Unit]
Description=MetaSystem Streamlit COCO Analytics
After=network.target

[Service]
Type=simple
User=${VPS_USER}
Group=${VPS_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_DIR}/bin/streamlit run streamlit_coco_analytics.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10
StandardOutput=append:${LOG_DIR}/streamlit.log
StandardError=append:${LOG_DIR}/streamlit.error.log
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF

    # ML API
    cat > /etc/systemd/system/metasystem-api.service << EOF
[Unit]
Description=MetaSystem ML API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=${VPS_USER}
Group=${VPS_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
Environment="PYTHONPATH=${APP_DIR}"
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_DIR}/bin/uvicorn ml_core.api.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10
StandardOutput=append:${LOG_DIR}/ml-api.log
StandardError=append:${LOG_DIR}/ml-api.error.log
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable services
    systemctl daemon-reload
    systemctl enable metasystem-gradio.service
    systemctl enable metasystem-streamlit.service
    systemctl enable metasystem-api.service
    
    log_success "Systemd services created"
}

# Function to configure Nginx
configure_nginx() {
    log_info "Configuring Nginx reverse proxy..."
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Create MetaSystem configuration
    cat > /etc/nginx/sites-available/metasystem << 'EOF'
# Upstream definitions
upstream gradio_backend {
    server 127.0.0.1:7860;
    keepalive 32;
}

upstream streamlit_backend {
    server 127.0.0.1:8501;
    keepalive 32;
}

upstream ml_api_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

# Main Gradio Interface
server {
    listen 443 ssl http2;
    server_name metasystem.example.com;  # Change to your domain

    # SSL Configuration (will be configured by certbot)
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Gradio specific configuration
    location / {
        proxy_pass http://gradio_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}

# Streamlit Analytics
server {
    listen 443 ssl http2;
    server_name analytics.metasystem.example.com;  # Change to your domain

    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;

    location / {
        proxy_pass http://streamlit_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    # Streamlit specific WebSocket handling
    location /_stcore/stream {
        proxy_pass http://streamlit_backend/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass 1;
        proxy_no_cache 1;
    }
}

# ML API
server {
    listen 443 ssl http2;
    server_name api.metasystem.example.com;  # Change to your domain

    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;

    # API rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://ml_api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        
        # CORS headers for API
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Authorization, Content-Type";
    }
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/metasystem /etc/nginx/sites-enabled/
    
    # Test configuration
    nginx -t
    
    # Start nginx
    systemctl start nginx
    systemctl enable nginx
    
    log_success "Nginx configured"
}

# Function to create maintenance scripts
create_maintenance_scripts() {
    log_info "Creating maintenance scripts..."
    
    # Daily backup script
    sudo -u ${VPS_USER} bash -c "cat > ${SCRIPTS_DIR}/backup_daily.sh << 'EOF'
#!/bin/bash
TIMESTAMP=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=${BACKUP_DIR}/\$TIMESTAMP

mkdir -p \$BACKUP_DIR

# Database backup
pg_dump -U ${VPS_USER} metasystem_db | gzip > \$BACKUP_DIR/db_backup.sql.gz

# Application files backup
tar -czf \$BACKUP_DIR/app_backup.tar.gz \\
    ${APP_DIR}/data \\
    ${APP_DIR}/config \\
    ${APP_DIR}/.env \\
    ${LOG_DIR}

# Cleanup old backups (keep 7 days)
find ${BACKUP_DIR} -type d -mtime +7 -exec rm -rf {} + 2>/dev/null

echo \"\$(date): Backup completed in \$BACKUP_DIR\"
EOF"

    # Health check script
    sudo -u ${VPS_USER} bash -c "cat > ${SCRIPTS_DIR}/health_check.sh << 'EOF'
#!/bin/bash
SERVICES=(\"metasystem-gradio\" \"metasystem-streamlit\" \"metasystem-api\")
LOG_FILE=${LOG_DIR}/health_check.log

for service in \"\${SERVICES[@]}\"; do
    if ! systemctl is-active --quiet \$service.service; then
        echo \"\$(date): \$service is DOWN, restarting...\" >> \$LOG_FILE
        systemctl restart \$service.service
        sleep 5
        
        # Check if restart was successful
        if systemctl is-active --quiet \$service.service; then
            echo \"\$(date): \$service restarted successfully\" >> \$LOG_FILE
        else
            echo \"\$(date): \$service restart FAILED\" >> \$LOG_FILE
        fi
    fi
done

# API health check
curl -f http://localhost:8000/health > /dev/null 2>&1
if [ \$? -ne 0 ]; then
    echo \"\$(date): API health check failed\" >> \$LOG_FILE
fi
EOF"

    # Make scripts executable
    chmod +x ${SCRIPTS_DIR}/*.sh
    
    # Add to crontab
    sudo -u ${VPS_USER} bash -c "(crontab -l 2>/dev/null; echo '0 3 * * * ${SCRIPTS_DIR}/backup_daily.sh >> ${LOG_DIR}/backup.log 2>&1') | crontab -"
    sudo -u ${VPS_USER} bash -c "(crontab -l 2>/dev/null; echo '*/5 * * * * ${SCRIPTS_DIR}/health_check.sh') | crontab -"
    
    log_success "Maintenance scripts created"
}

# Function to start services
start_services() {
    log_info "Starting MetaSystem services..."
    
    # Start application services
    systemctl start metasystem-gradio.service
    systemctl start metasystem-streamlit.service
    systemctl start metasystem-api.service
    
    # Wait a moment for services to start
    sleep 5
    
    # Check service status
    services=("metasystem-gradio" "metasystem-streamlit" "metasystem-api")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet $service.service; then
            log_success "$service service started successfully"
        else
            log_error "$service service failed to start"
            systemctl status $service.service
        fi
    done
}

# Function to run deployment validation
validate_deployment() {
    log_info "Validating deployment..."
    
    # Check if services are responding
    sleep 10  # Give services time to fully start
    
    # Test local endpoints
    if curl -f http://localhost:7860 > /dev/null 2>&1; then
        log_success "Gradio service responding"
    else
        log_error "Gradio service not responding"
    fi
    
    if curl -f http://localhost:8501 > /dev/null 2>&1; then
        log_success "Streamlit service responding"
    else
        log_error "Streamlit service not responding"
    fi
    
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "ML API responding"
    else
        log_error "ML API not responding"
    fi
    
    # Display service status
    echo
    log_info "Service Status Summary:"
    systemctl status metasystem-gradio.service --no-pager -l
    systemctl status metasystem-streamlit.service --no-pager -l
    systemctl status metasystem-api.service --no-pager -l
}

# Main deployment function
main() {
    log_info "Starting VPS deployment for TikTok Viral ML System"
    echo "=============================================="
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
    
    # Run deployment steps
    create_system_user
    install_system_deps
    configure_firewall
    secure_ssh
    configure_databases
    create_directories
    deploy_application
    setup_python_env
    create_env_file
    create_systemd_services
    configure_nginx
    create_maintenance_scripts
    start_services
    validate_deployment
    
    echo
    log_success "VPS deployment completed successfully!"
    echo "=============================================="
    echo
    log_info "Next steps:"
    echo "1. Configure your domain DNS to point to this VPS IP"
    echo "2. Update domain names in /etc/nginx/sites-available/metasystem"
    echo "3. Run: certbot --nginx -d yourdomain.com"
    echo "4. Update API keys in ${APP_DIR}/.env"
    echo "5. Test all endpoints are working"
    echo
    log_info "Service URLs (after DNS configuration):"
    echo "• Gradio Trigger Manager: https://metasystem.yourdomain.com"
    echo "• Streamlit Analytics: https://analytics.metasystem.yourdomain.com"
    echo "• ML API: https://api.metasystem.yourdomain.com"
    echo
    log_info "Local access (for testing):"
    echo "• Gradio: http://$(curl -s ifconfig.me):7860"
    echo "• Streamlit: http://$(curl -s ifconfig.me):8501"
    echo "• ML API: http://$(curl -s ifconfig.me):8000"
}

# Run main function
main "$@"