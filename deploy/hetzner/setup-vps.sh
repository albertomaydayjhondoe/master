#!/bin/bash
# 🚀 Neural Forge Discográfica - Hetzner VPS Setup Script
# =========================================================
# Complete VPS setup for production deployment on Hetzner Cloud

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
LOG_FILE="/var/log/neural-forge-setup.log"
NEURAL_FORGE_USER="neuralforge"
NEURAL_FORGE_HOME="/opt/neural-forge"

echo -e "${CYAN}🚀 Neural Forge Discográfica - Hetzner VPS Setup v${SCRIPT_VERSION}${NC}"
echo -e "${CYAN}=================================================================${NC}"
echo -e "Date: $(date)"
echo -e "Server: $(hostname)"
echo -e "IP: $(curl -s ifconfig.me 2>/dev/null || echo 'Unknown')"
echo ""

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "${RED}❌ ERROR: $1${NC}"
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

log "${BLUE}📋 PHASE 1: System Information and Validation${NC}"
log "=============================================="

# System information
log "OS: $(lsb_release -d | cut -f2)"
log "Kernel: $(uname -r)"
log "Architecture: $(uname -m)"
log "CPU Cores: $(nproc)"
log "RAM: $(free -h | awk '/^Mem:/{print $2}')"
log "Disk: $(df -h / | awk 'NR==2{print $2}')"
log "Free Space: $(df -h / | awk 'NR==2{print $4}')"

# Validate minimum requirements for Hetzner CX33
MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
DISK_GB=$(df -BG / | tail -1 | awk '{print $4}' | sed 's/G//')

if [ "$MEMORY_GB" -lt 8 ]; then
    log "${YELLOW}⚠️ Warning: Less than 8GB RAM detected (${MEMORY_GB}GB). Hetzner CX33 recommended.${NC}"
fi

if [ "$DISK_GB" -lt 40 ]; then
    log "${YELLOW}⚠️ Warning: Less than 40GB free space (${DISK_GB}GB). Consider storage upgrade.${NC}"
fi

log "${GREEN}✅ System validation completed${NC}"
echo ""

log "${BLUE}📦 PHASE 2: System Updates and Essential Packages${NC}"
log "================================================="

# Update system
log "🔄 Updating package lists..."
apt-get update -qq

log "⬆️ Upgrading system packages..."
DEBIAN_FRONTEND=noninteractive apt-get upgrade -y -qq

# Install essential packages
log "📦 Installing essential packages..."
apt-get install -y -qq \
    curl \
    wget \
    git \
    unzip \
    zip \
    htop \
    nano \
    vim \
    tree \
    jq \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    fail2ban \
    logrotate \
    cron \
    rsync \
    net-tools \
    dnsutils \
    certbot \
    python3-certbot-nginx

log "${GREEN}✅ System packages updated and installed${NC}"
echo ""

log "${BLUE}👤 PHASE 3: User Management and Security${NC}"
log "========================================"

# Create neural-forge user
if ! id "$NEURAL_FORGE_USER" &>/dev/null; then
    log "👤 Creating $NEURAL_FORGE_USER user..."
    useradd -m -s /bin/bash "$NEURAL_FORGE_USER"
    usermod -aG sudo "$NEURAL_FORGE_USER"
    
    # Set up SSH key authentication (if provided)
    if [ -n "$SSH_PUBLIC_KEY" ]; then
        log "🔑 Setting up SSH key authentication..."
        mkdir -p "/home/$NEURAL_FORGE_USER/.ssh"
        echo "$SSH_PUBLIC_KEY" > "/home/$NEURAL_FORGE_USER/.ssh/authorized_keys"
        chown -R "$NEURAL_FORGE_USER:$NEURAL_FORGE_USER" "/home/$NEURAL_FORGE_USER/.ssh"
        chmod 700 "/home/$NEURAL_FORGE_USER/.ssh"
        chmod 600 "/home/$NEURAL_FORGE_USER/.ssh/authorized_keys"
    fi
    
    log "${GREEN}✅ User $NEURAL_FORGE_USER created${NC}"
else
    log "${YELLOW}⚠️ User $NEURAL_FORGE_USER already exists${NC}"
fi

# Create neural-forge directory
log "📁 Creating Neural Forge directory..."
mkdir -p "$NEURAL_FORGE_HOME"
chown "$NEURAL_FORGE_USER:$NEURAL_FORGE_USER" "$NEURAL_FORGE_HOME"

log "${GREEN}✅ User setup completed${NC}"
echo ""

log "${BLUE}🔥 PHASE 4: Firewall Configuration${NC}"
log "=================================="

# Configure UFW firewall
log "🔥 Configuring UFW firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (important: do this first!)
ufw allow ssh
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow specific application ports (restrict to localhost for security)
ufw allow from 127.0.0.1 to any port 7860  # Production Controller
ufw allow from 127.0.0.1 to any port 8501  # Analytics Engine
ufw allow from 127.0.0.1 to any port 8000  # ML Core API
ufw allow from 127.0.0.1 to any port 5678  # N8N
ufw allow from 127.0.0.1 to any port 3000  # Grafana
ufw allow from 127.0.0.1 to any port 9090  # Prometheus
ufw allow from 127.0.0.1 to any port 5432  # PostgreSQL
ufw allow from 127.0.0.1 to any port 6379  # Redis

# Enable firewall
ufw --force enable

log "${GREEN}✅ Firewall configured and enabled${NC}"
echo ""

log "${BLUE}🛡️ PHASE 5: Security Hardening${NC}"
log "==============================="

# Configure fail2ban
log "🛡️ Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
ignoreip = 127.0.0.1/8 ::1

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Secure SSH configuration
log "🔒 Hardening SSH configuration..."
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

cat > /etc/ssh/sshd_config.neural-forge << 'EOF'
# Neural Forge SSH Configuration
Port 22
Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key

# Authentication
LoginGraceTime 60
PermitRootLogin no
StrictModes yes
MaxAuthTries 3
MaxSessions 4
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM yes

# Security options
X11Forwarding no
PrintMotd no
PrintLastLog yes
TCPKeepAlive yes
Compression delayed
ClientAliveInterval 300
ClientAliveCountMax 2
AllowUsers neuralforge
EOF

# Apply SSH configuration (be careful!)
if [ -n "$SSH_PUBLIC_KEY" ]; then
    log "🔄 Applying secure SSH configuration..."
    cp /etc/ssh/sshd_config.neural-forge /etc/ssh/sshd_config
    systemctl reload sshd
    log "${GREEN}✅ SSH hardened (password auth disabled)${NC}"
else
    log "${YELLOW}⚠️ SSH hardening skipped (no SSH key provided)${NC}"
fi

# Configure automatic security updates
log "🔄 Configuring automatic security updates..."
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

apt-get install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

log "${GREEN}✅ Security hardening completed${NC}"
echo ""

log "${BLUE}⚙️ PHASE 6: System Optimization${NC}"
log "==============================="

# Optimize system limits
log "⚙️ Optimizing system limits..."
cat >> /etc/security/limits.conf << 'EOF'

# Neural Forge optimizations
* soft nofile 65536
* hard nofile 65536
* soft nproc 65536
* hard nproc 65536
root soft nofile 65536
root hard nofile 65536
EOF

# Optimize kernel parameters
log "⚙️ Optimizing kernel parameters..."
cat > /etc/sysctl.d/neural-forge.conf << 'EOF'
# Neural Forge kernel optimizations
net.core.somaxconn = 65536
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65536
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 60
net.ipv4.tcp_keepalive_probes = 10
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
fs.file-max = 2097152
EOF

sysctl -p /etc/sysctl.d/neural-forge.conf

# Configure log rotation
log "📝 Configuring log rotation..."
cat > /etc/logrotate.d/neural-forge << 'EOF'
/opt/neural-forge/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    su neuralforge neuralforge
}

/var/log/neural-forge-setup.log {
    weekly
    rotate 8
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF

log "${GREEN}✅ System optimization completed${NC}"
echo ""

log "${BLUE}📊 PHASE 7: Monitoring Setup${NC}"
log "============================"

# Install monitoring tools
log "📊 Installing monitoring tools..."
apt-get install -y -qq \
    htop \
    iotop \
    nethogs \
    ncdu \
    glances \
    sysstat

# Enable sysstat
systemctl enable sysstat
systemctl start sysstat

# Create monitoring script
log "📈 Creating system monitoring script..."
cat > /usr/local/bin/neural-forge-status << 'EOF'
#!/bin/bash
# Neural Forge System Status

echo "🎵 Neural Forge System Status - $(date)"
echo "======================================="
echo ""

echo "💻 System Resources:"
echo "  CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')"
echo "  Memory: $(free -h | awk '/^Mem:/{printf "Used: %s / Total: %s (%.1f%%)\n", $3, $2, $3/$2*100}')"
echo "  Disk: $(df -h / | awk 'NR==2{printf "Used: %s / Total: %s (%s)\n", $3, $2, $5}')"

echo ""
echo "🌐 Network:"
echo "  External IP: $(curl -s ifconfig.me)"
echo "  Connections: $(netstat -tun | wc -l) active"

echo ""
echo "🐳 Docker Status:"
if command -v docker >/dev/null 2>&1; then
    echo "  Docker: $(systemctl is-active docker)"
    if docker ps >/dev/null 2>&1; then
        echo "  Containers: $(docker ps -q | wc -l) running"
    fi
else
    echo "  Docker: Not installed"
fi

echo ""
echo "🔥 Firewall Status:"
echo "  UFW: $(ufw status | head -1)"

echo ""
echo "📋 Last 5 log entries:"
tail -5 /var/log/neural-forge-setup.log | sed 's/^/  /'
EOF

chmod +x /usr/local/bin/neural-forge-status

log "${GREEN}✅ Monitoring setup completed${NC}"
echo ""

log "${BLUE}🎁 PHASE 8: Final Configuration${NC}"
log "==============================="

# Create welcome message
log "🎨 Creating welcome message..."
cat > /etc/motd << 'EOF'

🎵 ═══════════════════════════════════════════════════
   Neural Forge Discográfica - Production Server
   ═══════════════════════════════════════════════════
   
   🚀 Status: Production Ready
   📊 Monitoring: /usr/local/bin/neural-forge-status
   📁 App Directory: /opt/neural-forge
   👤 App User: neuralforge
   
   💡 Quick Commands:
   • sudo su - neuralforge    (Switch to app user)
   • cd /opt/neural-forge      (Go to app directory)
   • make health               (Check system health)
   • make logs                 (View application logs)
   
   🎵 Ready to dominate social media! 🔥
   ═══════════════════════════════════════════════════

EOF

# Set up cron jobs
log "⏰ Setting up maintenance cron jobs..."
cat > /etc/cron.d/neural-forge << 'EOF'
# Neural Forge maintenance tasks

# System status check every 6 hours
0 */6 * * * root /usr/local/bin/neural-forge-status >> /var/log/neural-forge-status.log 2>&1

# Cleanup logs older than 30 days
0 2 * * * root find /opt/neural-forge/logs -name "*.log" -mtime +30 -delete

# Update package lists daily
0 3 * * * root apt-get update -qq

# Restart services weekly (Sunday 4 AM)
0 4 * * 0 neuralforge cd /opt/neural-forge && make restart
EOF

# Create initial directories for the application
log "📁 Creating application directories..."
sudo -u "$NEURAL_FORGE_USER" mkdir -p "$NEURAL_FORGE_HOME"/{data,config,logs,backups}
sudo -u "$NEURAL_FORGE_USER" mkdir -p "$NEURAL_FORGE_HOME"/data/{models,torch_cache}

# Set proper permissions
chown -R "$NEURAL_FORGE_USER:$NEURAL_FORGE_USER" "$NEURAL_FORGE_HOME"
chmod -R 755 "$NEURAL_FORGE_HOME"
chmod -R 700 "$NEURAL_FORGE_HOME"/config

log "${GREEN}✅ Final configuration completed${NC}"
echo ""

log "${CYAN}🎉 HETZNER VPS SETUP COMPLETED!${NC}"
log "==============================="
log ""
log "${GREEN}✅ Setup Summary:${NC}"
log "  • System updated and hardened"
log "  • User '$NEURAL_FORGE_USER' created with sudo access"
log "  • Firewall configured (UFW enabled)"
log "  • Security hardening applied (fail2ban, SSH)"
log "  • System optimizations applied"
log "  • Monitoring tools installed"
log "  • Application directories created"
log ""
log "${YELLOW}📋 Next Steps:${NC}"
log "  1. Switch to app user: sudo su - $NEURAL_FORGE_USER"
log "  2. Clone the repository: git clone <your-repo>"
log "  3. Run Docker installation: ./deploy/hetzner/install-docker.sh"
log "  4. Deploy services: ./deploy/hetzner/deploy-services.sh"
log ""
log "${BLUE}📊 System Status:${NC}"
log "  • Check status: /usr/local/bin/neural-forge-status"
log "  • View logs: tail -f /var/log/neural-forge-setup.log"
log "  • App directory: $NEURAL_FORGE_HOME"
log ""
log "${PURPLE}🎵 Server ready for Neural Forge Discográfica deployment! 🚀${NC}"

# Final system status
echo ""
/usr/local/bin/neural-forge-status

exit 0