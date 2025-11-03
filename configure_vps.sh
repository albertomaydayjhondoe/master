#!/bin/bash
"""
Production Environment Configuration Generator
Creates production-ready environment files for VPS deployment
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Default values
VPS_IP=""
DOMAIN=""
DATABASE_PASSWORD=""
SECRET_KEY=""

# Function to generate secure password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Function to generate secret key
generate_secret_key() {
    openssl rand -hex 32
}

# Function to prompt for input
prompt_input() {
    local prompt="$1"
    local var_name="$2"
    local default="$3"
    local is_password="$4"
    
    if [ "$is_password" = "true" ]; then
        echo -n "$prompt: "
        read -s input
        echo
    else
        echo -n "$prompt"
        if [ -n "$default" ]; then
            echo -n " (default: $default)"
        fi
        echo -n ": "
        read input
    fi
    
    if [ -z "$input" ] && [ -n "$default" ]; then
        input="$default"
    fi
    
    eval "$var_name='$input'"
}

# Function to validate IP address
validate_ip() {
    local ip=$1
    local stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

# Function to validate domain
validate_domain() {
    local domain=$1
    if [[ $domain =~ ^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to collect configuration
collect_config() {
    log_info "MetaSystem VPS Configuration Generator"
    echo "========================================"
    echo
    
    # VPS IP Address
    while true; do
        prompt_input "Enter VPS IP address" VPS_IP
        if validate_ip "$VPS_IP"; then
            break
        else
            log_error "Invalid IP address format"
        fi
    done
    
    # Domain (optional)
    while true; do
        prompt_input "Enter domain name (optional, press Enter to skip)" DOMAIN
        if [ -z "$DOMAIN" ] || validate_domain "$DOMAIN"; then
            break
        else
            log_error "Invalid domain format"
        fi
    done
    
    # Database password
    default_db_pass=$(generate_password)
    prompt_input "Enter database password" DATABASE_PASSWORD "$default_db_pass" true
    
    # Secret key
    default_secret=$(generate_secret_key)
    SECRET_KEY="$default_secret"
    
    # API Keys (optional)
    echo
    log_info "API Keys Configuration (optional - can be configured later)"
    prompt_input "Meta API Key (optional)" META_API_KEY
    prompt_input "YouTube API Key (optional)" YOUTUBE_API_KEY
    prompt_input "Spotify Client ID (optional)" SPOTIFY_CLIENT_ID
    prompt_input "Spotify Client Secret (optional)" SPOTIFY_CLIENT_SECRET "false" true
    prompt_input "Telegram Bot Token (optional)" TELEGRAM_BOT_TOKEN
    prompt_input "OpenAI API Key (optional)" OPENAI_API_KEY "false" true
}

# Function to create environment file
create_env_file() {
    local env_file=".env.production"
    
    log_info "Creating production environment file: $env_file"
    
    cat > "$env_file" << EOF
# Production Environment Configuration
# Generated on $(date)

# Database Configuration
DATABASE_URL=postgresql://metasystem:${DATABASE_PASSWORD}@localhost:5432/metasystem_db
REDIS_URL=redis://localhost:6379/0

# Application Configuration
SECRET_KEY=${SECRET_KEY}
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
VPS_MODE=true
DUMMY_MODE=false

# Server Configuration
VPS_IP=${VPS_IP}
MAX_WORKERS=2
WORKER_TIMEOUT=300
GRADIO_SERVER_PORT=7860
STREAMLIT_SERVER_PORT=8501
ML_API_SERVER_PORT=8000

# Domain Configuration
EOF

    if [ -n "$DOMAIN" ]; then
        cat >> "$env_file" << EOF
DOMAIN=${DOMAIN}
GRADIO_URL=https://${DOMAIN}
STREAMLIT_URL=https://analytics.${DOMAIN}
ML_API_URL=https://api.${DOMAIN}
EOF
    else
        cat >> "$env_file" << EOF
DOMAIN=${VPS_IP}
GRADIO_URL=http://${VPS_IP}:7860
STREAMLIT_URL=http://${VPS_IP}:8501
ML_API_URL=http://${VPS_IP}:8000
EOF
    fi

    cat >> "$env_file" << EOF

# API Keys (configure as needed)
META_API_KEY=${META_API_KEY:-your_meta_api_key_here}
YOUTUBE_API_KEY=${YOUTUBE_API_KEY:-your_youtube_api_key_here}
SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID:-your_spotify_client_id_here}
SPOTIFY_CLIENT_SECRET=${SPOTIFY_CLIENT_SECRET:-your_spotify_client_secret_here}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-your_telegram_bot_token_here}
OPENAI_API_KEY=${OPENAI_API_KEY:-your_openai_api_key_here}

# Security Configuration
SESSION_LIFETIME=3600
MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_DURATION=300

# Monitoring Configuration
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=300

# File Upload Configuration
MAX_UPLOAD_SIZE=100MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,mp4,mov,avi

# Cache Configuration
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Logging Configuration
LOG_ROTATION_SIZE=10MB
LOG_RETENTION_DAYS=30
EOF

    chmod 600 "$env_file"
    log_success "Environment file created: $env_file"
}

# Function to create deployment script
create_deployment_script() {
    local deploy_script="deploy_to_vps.sh"
    
    log_info "Creating deployment script: $deploy_script"
    
    cat > "$deploy_script" << EOF
#!/bin/bash
# Auto-generated deployment script for ${DOMAIN:-$VPS_IP}

set -e

VPS_IP="${VPS_IP}"
VPS_USER="root"  # Change this if using different user
APP_NAME="metasystem"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "\${YELLOW}ℹ️  \$1\${NC}"
}

log_success() {
    echo -e "\${GREEN}✅ \$1\${NC}"
}

# Upload files to VPS
log_info "Uploading files to VPS..."
scp -r . \${VPS_USER}@\${VPS_IP}:/tmp/metasystem-upload/

# Run deployment on VPS
log_info "Running deployment on VPS..."
ssh \${VPS_USER}@\${VPS_IP} "
    cd /tmp/metasystem-upload
    chmod +x deploy_vps.sh
    ./deploy_vps.sh
"

log_success "Deployment completed!"
EOF

    if [ -n "$DOMAIN" ]; then
        cat >> "$deploy_script" << EOF

log_info "Configure DNS and SSL:"
echo "1. Point ${DOMAIN} to ${VPS_IP}"
echo "2. Point analytics.${DOMAIN} to ${VPS_IP}"
echo "3. Point api.${DOMAIN} to ${VPS_IP}"
echo "4. Run SSL setup: ssh root@${VPS_IP} 'certbot --nginx -d ${DOMAIN} -d analytics.${DOMAIN} -d api.${DOMAIN}'"
EOF
    fi

    chmod +x "$deploy_script"
    log_success "Deployment script created: $deploy_script"
}

# Function to create SSL setup script
create_ssl_script() {
    if [ -n "$DOMAIN" ]; then
        local ssl_script="setup_ssl.sh"
        
        log_info "Creating SSL setup script: $ssl_script"
        
        cat > "$ssl_script" << EOF
#!/bin/bash
# SSL setup script for ${DOMAIN}

set -e

# Install certbot if not present
if ! command -v certbot &> /dev/null; then
    apt update
    apt install -y certbot python3-certbot-nginx
fi

# Update nginx configuration with correct domain
sed -i 's/metasystem\.example\.com/${DOMAIN}/g' /etc/nginx/sites-available/metasystem
sed -i 's/analytics\.metasystem\.example\.com/analytics.${DOMAIN}/g' /etc/nginx/sites-available/metasystem
sed -i 's/api\.metasystem\.example\.com/api.${DOMAIN}/g' /etc/nginx/sites-available/metasystem

# Test nginx configuration
nginx -t

# Reload nginx
systemctl reload nginx

# Obtain SSL certificates
certbot --nginx -d ${DOMAIN} -d analytics.${DOMAIN} -d api.${DOMAIN} --non-interactive --agree-tos -m admin@${DOMAIN}

# Enable auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer

echo "SSL certificates installed successfully!"
echo "Your sites are now available at:"
echo "• Gradio: https://${DOMAIN}"
echo "• Analytics: https://analytics.${DOMAIN}"
echo "• API: https://api.${DOMAIN}"
EOF

        chmod +x "$ssl_script"
        log_success "SSL setup script created: $ssl_script"
    fi
}

# Function to create database init script
create_db_init_script() {
    local db_script="init_database.sh"
    
    log_info "Creating database initialization script: $db_script"
    
    cat > "$db_script" << EOF
#!/bin/bash
# Database initialization script

set -e

DB_NAME="metasystem_db"
DB_USER="metasystem"
DB_PASS="${DATABASE_PASSWORD}"

# Create user and database
sudo -u postgres psql << EOSQL
-- Create user
CREATE USER \${DB_USER} WITH PASSWORD '\${DB_PASS}';

-- Create database
CREATE DATABASE \${DB_NAME} OWNER \${DB_USER};

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE \${DB_NAME} TO \${DB_USER};

-- Connect to the database and set up extensions
\c \${DB_NAME}

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

EOSQL

echo "Database initialized successfully!"
EOF

    chmod +x "$db_script"
    log_success "Database script created: $db_script"
}

# Function to create monitoring setup
create_monitoring_setup() {
    local monitor_script="setup_monitoring.sh"
    
    log_info "Creating monitoring setup script: $monitor_script"
    
    cat > "$monitor_script" << EOF
#!/bin/bash
# Monitoring setup script

set -e

# Install monitoring tools
apt update
apt install -y htop iotop nethogs prometheus-node-exporter

# Create log rotation configuration
cat > /etc/logrotate.d/metasystem << 'LOGROTATE_EOF'
/var/log/metasystem/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 metasystem metasystem
    postrotate
        systemctl reload metasystem-*
    endscript
}
LOGROTATE_EOF

# Create system monitoring script
cat > /usr/local/bin/system_monitor.sh << 'MONITOR_EOF'
#!/bin/bash
LOG_FILE="/var/log/metasystem/system_monitor.log"

# System metrics
CPU_USAGE=\$(top -bn1 | grep "Cpu(s)" | awk '{print \$2}' | awk -F'%' '{print \$1}')
MEMORY_USAGE=\$(free | grep Mem | awk '{printf("%.2f", \$3/\$2 * 100.0)}')
DISK_USAGE=\$(df -h / | awk 'NR==2{printf("%s", \$5)}' | sed 's/%//')

# Log metrics
echo "\$(date): CPU: \${CPU_USAGE}%, Memory: \${MEMORY_USAGE}%, Disk: \${DISK_USAGE}%" >> \$LOG_FILE

# Check if any metric is too high
if (( \$(echo "\$CPU_USAGE > 80" | bc -l) )); then
    echo "\$(date): HIGH CPU USAGE: \${CPU_USAGE}%" >> \$LOG_FILE
fi

if (( \$(echo "\$MEMORY_USAGE > 80" | bc -l) )); then
    echo "\$(date): HIGH MEMORY USAGE: \${MEMORY_USAGE}%" >> \$LOG_FILE
fi

if (( \$DISK_USAGE > 80 )); then
    echo "\$(date): HIGH DISK USAGE: \${DISK_USAGE}%" >> \$LOG_FILE
fi
MONITOR_EOF

chmod +x /usr/local/bin/system_monitor.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/system_monitor.sh") | crontab -

echo "Monitoring setup completed!"
EOF

    chmod +x "$monitor_script"
    log_success "Monitoring script created: $monitor_script"
}

# Function to create summary
create_summary() {
    local summary_file="DEPLOYMENT_SUMMARY.md"
    
    log_info "Creating deployment summary: $summary_file"
    
    cat > "$summary_file" << EOF
# MetaSystem VPS Deployment Summary

## Configuration Details

- **VPS IP**: ${VPS_IP}
- **Domain**: ${DOMAIN:-"Not configured (using IP)"}
- **Generated**: $(date)

## Files Created

1. \`.env.production\` - Production environment configuration
2. \`deploy_to_vps.sh\` - Automated deployment script
3. \`init_database.sh\` - Database initialization
4. \`setup_monitoring.sh\` - System monitoring setup
EOF

    if [ -n "$DOMAIN" ]; then
        cat >> "$summary_file" << EOF
5. \`setup_ssl.sh\` - SSL certificate configuration
EOF
    fi

    cat >> "$summary_file" << EOF

## Deployment Steps

1. **Prepare VPS**:
   \`\`\`bash
   # Ensure VPS is accessible via SSH
   ssh root@${VPS_IP}
   \`\`\`

2. **Deploy Application**:
   \`\`\`bash
   ./deploy_to_vps.sh
   \`\`\`

3. **Initialize Database**:
   \`\`\`bash
   ssh root@${VPS_IP} '/tmp/metasystem-upload/init_database.sh'
   \`\`\`

4. **Setup Monitoring**:
   \`\`\`bash
   ssh root@${VPS_IP} '/tmp/metasystem-upload/setup_monitoring.sh'
   \`\`\`
EOF

    if [ -n "$DOMAIN" ]; then
        cat >> "$summary_file" << EOF

5. **Configure SSL** (after DNS setup):
   \`\`\`bash
   ssh root@${VPS_IP} '/tmp/metasystem-upload/setup_ssl.sh'
   \`\`\`
EOF
    fi

    cat >> "$summary_file" << EOF

## Access URLs

EOF

    if [ -n "$DOMAIN" ]; then
        cat >> "$summary_file" << EOF
- **Gradio Trigger Manager**: https://${DOMAIN}
- **Streamlit Analytics**: https://analytics.${DOMAIN}
- **ML API**: https://api.${DOMAIN}
EOF
    else
        cat >> "$summary_file" << EOF
- **Gradio Trigger Manager**: http://${VPS_IP}:7860
- **Streamlit Analytics**: http://${VPS_IP}:8501
- **ML API**: http://${VPS_IP}:8000
EOF
    fi

    cat >> "$summary_file" << EOF

## Post-Deployment Tasks

1. **Configure API Keys**: Update API keys in \`.env.production\`
2. **Test Services**: Verify all endpoints are responding
3. **Setup Monitoring**: Configure alerts and monitoring
4. **Backup Configuration**: Setup automated backups
5. **Security Hardening**: Review firewall and security settings

## Troubleshooting

- **Check Service Status**: \`systemctl status metasystem-*\`
- **View Logs**: \`journalctl -u metasystem-gradio -f\`
- **System Resources**: \`htop\` and \`df -h\`
- **Network Connectivity**: \`netstat -tlnp\`

## Support

For issues or questions, check the logs in \`/var/log/metasystem/\` and service status with systemctl.
EOF

    log_success "Deployment summary created: $summary_file"
}

# Main function
main() {
    log_info "MetaSystem VPS Configuration Generator"
    echo "========================================"
    echo
    
    collect_config
    
    echo
    log_info "Generating configuration files..."
    
    create_env_file
    create_deployment_script
    create_ssl_script
    create_db_init_script
    create_monitoring_setup
    create_summary
    
    echo
    log_success "Configuration generation completed!"
    echo "========================================"
    echo
    log_info "Files created:"
    echo "• .env.production - Production environment"
    echo "• deploy_to_vps.sh - Deployment script"
    echo "• init_database.sh - Database setup"
    echo "• setup_monitoring.sh - Monitoring setup"
    if [ -n "$DOMAIN" ]; then
        echo "• setup_ssl.sh - SSL configuration"
    fi
    echo "• DEPLOYMENT_SUMMARY.md - Complete guide"
    echo
    log_info "Next steps:"
    echo "1. Review .env.production and update API keys if needed"
    echo "2. Run: ./deploy_to_vps.sh"
    echo "3. Follow the deployment summary guide"
    echo
    log_warning "Important: Keep .env.production secure and never commit it to git!"
}

# Run main function
main "$@"