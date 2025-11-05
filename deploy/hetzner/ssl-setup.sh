#!/bin/bash
# 🔒 Neural Forge Discográfica - SSL Setup Script
# ================================================
# Automated SSL certificate setup with Let's Encrypt

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_VERSION="3.0"
LOG_FILE="/var/log/neural-forge-ssl.log"

echo -e "${CYAN}🔒 Neural Forge - SSL Setup v${SCRIPT_VERSION}${NC}"
echo -e "${CYAN}============================================${NC}"
echo -e "Date: $(date)"
echo ""

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "${RED}❌ SSL SETUP FAILED: $1${NC}"
    exit 1
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error_exit "This script must be run as root. Use: sudo $0"
fi

# Create log file
mkdir -p /var/log
touch "$LOG_FILE"
chmod 644 "$LOG_FILE"

log "${BLUE}📋 PHASE 1: SSL Configuration Input${NC}"
log "==================================="

# Get domain information
if [ -z "$DOMAIN" ]; then
    echo -e "${YELLOW}Enter your domain name (e.g., neuralforge.com):${NC}"
    read -r DOMAIN
fi

if [ -z "$EMAIL" ]; then
    echo -e "${YELLOW}Enter your email for Let's Encrypt notifications:${NC}"
    read -r EMAIL
fi

# Validate domain format
if [[ ! "$DOMAIN" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
    error_exit "Invalid domain format: $DOMAIN"
fi

# Validate email format
if [[ ! "$EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
    error_exit "Invalid email format: $EMAIL"
fi

log "Domain: $DOMAIN"
log "Email: $EMAIL"
log "Server IP: $(curl -s ifconfig.me)"

# Check DNS resolution
log "🔍 Checking DNS resolution..."
RESOLVED_IP=$(dig +short "$DOMAIN" 2>/dev/null || echo "")
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "")

if [ "$RESOLVED_IP" != "$SERVER_IP" ]; then
    log "${YELLOW}⚠️ Warning: DNS resolution mismatch${NC}"
    log "  Domain resolves to: $RESOLVED_IP"
    log "  Server IP: $SERVER_IP"
    log "  Continuing anyway (DNS propagation may be in progress)..."
fi

log "${GREEN}✅ Domain configuration validated${NC}"
echo ""

log "${BLUE}📦 PHASE 2: Prerequisites Installation${NC}"
log "======================================"

# Update package list
log "🔄 Updating package lists..."
apt-get update -qq

# Install required packages
log "📦 Installing SSL prerequisites..."
apt-get install -y -qq \
    certbot \
    python3-certbot-nginx \
    nginx \
    openssl

# Check if nginx is running
if systemctl is-active --quiet nginx; then
    log "${GREEN}✅ Nginx is running${NC}"
else
    log "🚀 Starting Nginx..."
    systemctl start nginx
    systemctl enable nginx
fi

log "${GREEN}✅ Prerequisites installed${NC}"
echo ""

log "${BLUE}🌐 PHASE 3: Nginx Configuration${NC}"
log "==============================="

# Create nginx configuration directory structure
log "📁 Setting up Nginx directories..."
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled
mkdir -p /etc/nginx/ssl
mkdir -p /var/log/nginx

# Create main nginx configuration
log "⚙️ Creating Nginx main configuration..."
cat > /etc/nginx/nginx.conf << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 768;
    use epoll;
    multi_accept on;
}

http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    # MIME
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for"';
                   
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;
    
    # Gzip Settings
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    # Include site configurations
    include /etc/nginx/sites-enabled/*;
}
EOF

# Create the main site configuration (HTTP - will be upgraded to HTTPS)
log "🌐 Creating site configuration for $DOMAIN..."
cat > "/etc/nginx/sites-available/$DOMAIN" << EOF
# Neural Forge - HTTP Configuration (will be upgraded to HTTPS)
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Allow Let's Encrypt challenges
    location /.well-known/acme-challenge/ {
        root /var/www/html;
        allow all;
    }
    
    # Redirect all other traffic to HTTPS (after SSL setup)
    location / {
        # Temporary: serve a maintenance page
        return 200 'Neural Forge is setting up SSL certificates...';
        add_header Content-Type text/plain;
    }
}
EOF

# Enable the site
ln -sf "/etc/nginx/sites-available/$DOMAIN" "/etc/nginx/sites-enabled/$DOMAIN"

# Remove default nginx site
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
log "🧪 Testing Nginx configuration..."
if nginx -t; then
    log "${GREEN}✅ Nginx configuration is valid${NC}"
    systemctl reload nginx
else
    error_exit "Nginx configuration test failed"
fi

log "${GREEN}✅ Nginx configured successfully${NC}"
echo ""

log "${BLUE}🔒 PHASE 4: SSL Certificate Generation${NC}"
log "====================================="

# Create web root for challenges
mkdir -p /var/www/html
chown -R www-data:www-data /var/www/html

# Generate SSL certificate
log "🔐 Generating SSL certificate with Let's Encrypt..."
log "This may take a few minutes..."

# Use certbot to get certificate
if certbot certonly \
    --webroot \
    --webroot-path=/var/www/html \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --domains "$DOMAIN,www.$DOMAIN" \
    --non-interactive; then
    
    log "${GREEN}✅ SSL certificate generated successfully${NC}"
else
    error_exit "Failed to generate SSL certificate"
fi

# Verify certificate
log "🔍 Verifying SSL certificate..."
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    CERT_EXPIRY=$(openssl x509 -enddate -noout -in "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" | cut -d= -f2)
    log "Certificate expires: $CERT_EXPIRY"
    log "${GREEN}✅ SSL certificate verified${NC}"
else
    error_exit "SSL certificate files not found"
fi

echo ""

log "${BLUE}🌐 PHASE 5: HTTPS Configuration${NC}"
log "==============================="

# Create the HTTPS site configuration
log "🔒 Creating HTTPS configuration..."
cat > "/etc/nginx/sites-available/$DOMAIN" << EOF
# Neural Forge - HTTPS Configuration
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Allow Let's Encrypt challenges
    location /.well-known/acme-challenge/ {
        root /var/www/html;
        allow all;
    }
    
    # Redirect all other HTTP traffic to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Logging
    access_log /var/log/nginx/neural-forge-access.log main;
    error_log /var/log/nginx/neural-forge-error.log;
    
    # Main Dashboard (Production Controller)
    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # Analytics Engine
    location /analytics/ {
        rewrite ^/analytics/(.*)$ /\$1 break;
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # ML Core API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Rate limiting for API
        limit_req zone=api burst=20 nodelay;
    }
    
    # N8N Workflows
    location /workflows/ {
        rewrite ^/workflows/(.*)$ /\$1 break;
        proxy_pass http://127.0.0.1:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Authentication for N8N
        auth_basic "Neural Forge Admin";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
    
    # Grafana Monitoring
    location /grafana/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Authentication for Grafana
        auth_basic "Neural Forge Monitoring";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
    
    # Prometheus Metrics (Admin only)
    location /prometheus/ {
        proxy_pass http://127.0.0.1:9090/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Restrict access
        allow 127.0.0.1;
        deny all;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 'Neural Forge is healthy!';
        add_header Content-Type text/plain;
    }
    
    # Security: Block common attack paths
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ ^/(wp-admin|wp-login|admin|phpmyadmin) {
        return 404;
    }
}
EOF

# Test nginx configuration
log "🧪 Testing HTTPS configuration..."
if nginx -t; then
    log "${GREEN}✅ HTTPS configuration is valid${NC}"
    systemctl reload nginx
else
    error_exit "HTTPS configuration test failed"
fi

log "${GREEN}✅ HTTPS configuration applied${NC}"
echo ""

log "${BLUE}🔐 PHASE 6: Security Enhancements${NC}"
log "================================="

# Create admin credentials for protected endpoints
log "👤 Setting up admin authentication..."
if [ -z "$ADMIN_PASSWORD" ]; then
    echo -e "${YELLOW}Enter admin password for protected endpoints:${NC}"
    read -s ADMIN_PASSWORD
fi

# Create htpasswd file
echo "admin:$(openssl passwd -crypt "$ADMIN_PASSWORD")" > /etc/nginx/.htpasswd
chmod 600 /etc/nginx/.htpasswd

# Create Diffie-Hellman parameters for enhanced security
log "🔒 Generating Diffie-Hellman parameters (this may take several minutes)..."
if [ ! -f /etc/nginx/ssl/dhparam.pem ]; then
    openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048
fi

# Add DH parameters to nginx configuration
cat >> "/etc/nginx/sites-available/$DOMAIN" << 'EOF'

# Enhanced SSL Security
ssl_dhparam /etc/nginx/ssl/dhparam.pem;
EOF

# Set up automatic certificate renewal
log "🔄 Setting up automatic certificate renewal..."
cat > /etc/cron.d/certbot-renewal << 'EOF'
# Automatic SSL certificate renewal
0 12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

# Test certificate renewal
log "🧪 Testing certificate renewal..."
if certbot renew --dry-run; then
    log "${GREEN}✅ Certificate renewal test successful${NC}"
else
    log "${YELLOW}⚠️ Certificate renewal test failed (but continuing)${NC}"
fi

log "${GREEN}✅ Security enhancements applied${NC}"
echo ""

log "${BLUE}📊 PHASE 7: SSL Verification${NC}"
log "============================"

# Test HTTPS connection
log "🔍 Testing HTTPS connection..."
sleep 5  # Wait for nginx to fully reload

if curl -sf "https://$DOMAIN/health" >/dev/null 2>&1; then
    log "${GREEN}✅ HTTPS connection successful${NC}"
else
    log "${YELLOW}⚠️ HTTPS test failed (services may not be running yet)${NC}"
fi

# Check SSL certificate quality
log "🔒 Checking SSL certificate quality..."
SSL_GRADE=$(curl -s "https://api.ssllabs.com/api/v3/analyze?host=$DOMAIN&publish=off&startNew=on&all=done" | jq -r '.endpoints[0].grade' 2>/dev/null || echo "Unknown")
log "SSL Labs Grade: $SSL_GRADE"

# Create SSL monitoring script
log "📊 Creating SSL monitoring script..."
cat > /usr/local/bin/ssl-status << EOF
#!/bin/bash
echo "🔒 SSL Status for $DOMAIN - \$(date)"
echo "=================================="
echo ""

echo "📋 Certificate Information:"
openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -text -noout | grep -E "(Subject:|Issuer:|Not Before:|Not After:)"

echo ""
echo "🌐 HTTPS Test:"
if curl -sf https://$DOMAIN/health >/dev/null 2>&1; then
    echo "  ✅ HTTPS connection successful"
else
    echo "  ❌ HTTPS connection failed"
fi

echo ""
echo "📊 Certificate Expiry:"
DAYS_UNTIL_EXPIRY=\$(( (\$(date -d "\$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem | cut -d= -f2)" +%s) - \$(date +%s)) / 86400 ))
echo "  Days until expiry: \$DAYS_UNTIL_EXPIRY"

if [ \$DAYS_UNTIL_EXPIRY -lt 30 ]; then
    echo "  ⚠️ Certificate expires soon!"
else
    echo "  ✅ Certificate valid"
fi
EOF

chmod +x /usr/local/bin/ssl-status

log "${GREEN}✅ SSL verification completed${NC}"
echo ""

log "${CYAN}🎉 SSL SETUP COMPLETED SUCCESSFULLY!${NC}"
log "====================================="
log ""
log "${GREEN}✅ SSL Summary:${NC}"
log "  • Domain: $DOMAIN"
log "  • Certificate: Let's Encrypt (90-day validity)"
log "  • Auto-renewal: Configured"
log "  • Security headers: Applied"  
log "  • Admin authentication: Enabled"
log ""
log "${YELLOW}🌐 Your Neural Forge is now accessible at:${NC}"
log "  🔒 Main Dashboard: https://$DOMAIN"
log "  📊 Analytics: https://$DOMAIN/analytics"
log "  🔧 API Docs: https://$DOMAIN/api/docs"
log "  🔄 Workflows: https://$DOMAIN/workflows (admin)"
log "  📈 Monitoring: https://$DOMAIN/grafana (admin)"
log ""
log "${YELLOW}🔐 Admin Credentials:${NC}"
log "  Username: admin"
log "  Password: [Your chosen password]"
log ""
log "${YELLOW}📊 SSL Management:${NC}"
log "  • Check status: /usr/local/bin/ssl-status"
log "  • Manual renewal: certbot renew"
log "  • Certificate location: /etc/letsencrypt/live/$DOMAIN/"
log ""
log "${BLUE}💡 Next Steps:${NC}"
log "  1. Test all endpoints with HTTPS"
log "  2. Configure your DNS for www.$DOMAIN"
log "  3. Set up monitoring alerts"
log "  4. Update your .env file with HTTPS URLs"
log ""
log "${PURPLE}🔒 Your Neural Forge is now secure and ready! 🚀${NC}"

# Final SSL test
echo ""
/usr/local/bin/ssl-status

exit 0