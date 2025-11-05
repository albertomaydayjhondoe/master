#!/bin/bash
# 🚀 NEURAL FORGE TRAP ARTIST - HETZNER AUTO DEPLOYMENT
# ===================================================
# Script automático para deployment completo en Hetzner
# Presupuesto: $500 USD - Servidor CPX41
# Tiempo estimado: 15 minutos

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Banner
echo -e "${PURPLE}"
echo "🎵 NEURAL FORGE TRAP ARTIST - HETZNER DEPLOYMENT"
echo "================================================="
echo "Artista: TrapStar ML"
echo "Presupuesto servidor: \$92/mes (CPX41)"
echo "Tiempo deployment: ~15 minutos"
echo -e "${NC}"

# Variables
DOMAIN="${1:-trapforge.example.com}"
DB_PASSWORD=$(openssl rand -base64 32)
ADMIN_PASSWORD=$(openssl rand -base64 16)
HETZNER_IP=$(curl -s ifconfig.me)

echo -e "${BLUE}🔧 CONFIGURACIÓN:${NC}"
echo "Domain: $DOMAIN"
echo "Server IP: $HETZNER_IP"
echo "Admin Password: $ADMIN_PASSWORD"
echo ""

# Confirm deployment
read -p "¿Proceder con deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Deployment cancelado${NC}"
    exit 1
fi

echo -e "${YELLOW}🚀 Iniciando deployment Neural Forge...${NC}"

# 1. SYSTEM UPDATE
echo -e "${BLUE}📦 Actualizando sistema...${NC}"
apt update && apt upgrade -y

# 2. INSTALL ESSENTIALS
echo -e "${BLUE}🔧 Instalando dependencias...${NC}"
apt install -y \
    docker.io \
    docker-compose-plugin \
    nginx \
    certbot \
    python3-certbot-nginx \
    htop \
    git \
    curl \
    wget \
    unzip

# Start docker
systemctl start docker
systemctl enable docker

# 3. CREATE APP USER
echo -e "${BLUE}👤 Creando usuario trapforge...${NC}"
if ! id "trapforge" &>/dev/null; then
    useradd -m -s /bin/bash trapforge
    usermod -aG docker trapforge
    echo "trapforge:$ADMIN_PASSWORD" | chpasswd
fi

# 4. SETUP APPLICATION
echo -e "${BLUE}📥 Clonando repositorio Neural Forge...${NC}"
cd /home/trapforge

if [ -d "discografica-ml-system" ]; then
    rm -rf discografica-ml-system
fi

sudo -u trapforge git clone https://github.com/albertomaydayjhondoe/discografica-ml-system.git
cd discografica-ml-system
sudo -u trapforge git checkout deployment/hetzner-production

# 5. CONFIGURE ENVIRONMENT
echo -e "${BLUE}🔑 Configurando variables del artista trap...${NC}"
sudo -u trapforge cp .env.production.template .env.production

# Update .env.production with trap artist config
sudo -u trapforge tee .env.production > /dev/null << EOF
# 🎵 TRAP ARTIST PRODUCTION CONFIG
TRAP_ARTIST_MODE=true
DUMMY_MODE=false
ML_PRODUCTION_MODE=true

# Database
DATABASE_URL=postgresql://trapuser:${DB_PASSWORD}@db:5432/trapforge
REDIS_URL=redis://redis:6379

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
API_BASE_URL=https://${DOMAIN}

# YouTube API del artista
YOUTUBE_CLIENT_ID=524783623513-rksdl9ncl9c6un9omiqpk4rug8b2dcku.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=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
YOUTUBE_REFRESH_TOKEN=1//03tPk1spNX9mYCgYIARAAGAMSNwF-L9Irs89ebCVgaWgoFSPNyNJaFWgj9HdqcSIodYFQWPUaYClY6LMKXcx8Q1Z7YdWRPnoD3EE
YOUTUBE_CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg

# Meta Ads API del artista  
META_APP_ID=2672426126432982
META_APP_SECRET=MsMBRKtntDDCRLlOVFlhJIDlDYI
META_ACCESS_TOKEN=EAAlZBjrH0WtYBPZCl4coYC9taVE8E55hkiLHLgqDoEi41sv8gY20TvXyB3YICmvmB3khotGEBxkzfAA6PELIyIOyO6UOSxlcCoa8hj0monPIsyFhRLgYFlunFFNlvbO9ckttzcHJgjEdd4rbtWFZAkDz6furs0kAykVQgjRIZComxn1GYVAjPcV8dLx95t1xc1ZC7838G44pIMMvuZB5hiN2BrUZCYX5JAWYklN

# Trap Artist Config
TRAP_ARTIST_NAME="TrapStar ML"
TRAP_ARTIST_REAL_NAME="Neural Beats Producer"
TRAP_ARTIST_GENRE="trap"
TRAP_ARTIST_STYLE="dark_trap"
TRAP_ARTIST_LANGUAGE="spanish"
TRAP_ARTIST_TARGET_AUDIENCE="18-35_hispanic_urban"

# Campaign Config
TRAP_CAMPAIGN_BUDGET_DAILY=500
TRAP_CAMPAIGN_BUDGET_TOTAL=5000
TRAP_CAMPAIGN_DURATION_DAYS=14
TRAP_CAMPAIGN_TARGET_COUNTRIES="ES,MX,AR,CO,PE,CL"

# Satellite Config
TRAP_SATELLITE_1_NAME="DarkBeats_Official"
TRAP_SATELLITE_2_NAME="UrbanTrap_Studios"
TRAP_SATELLITE_3_NAME="NeonTrap_Collective"
TRAP_SATELLITE_4_NAME="TrapML_Records"
TRAP_SATELLITE_5_NAME="Neural_TrapHouse"

# Revenue Sharing
TRAP_ARTIST_PERCENTAGE=70
TRAP_PLATFORM_PERCENTAGE=30
TRAP_PAYMENT_METHOD="crypto_wallet"

# Security
JWT_SECRET=$(openssl rand -base64 64)
ENCRYPTION_KEY=$(openssl rand -base64 32)

# Monitoring
GRAFANA_ADMIN_PASSWORD=${ADMIN_PASSWORD}
PROMETHEUS_RETENTION=30d
EOF

# 6. CREATE DOCKER COMPOSE FOR PRODUCTION
echo -e "${BLUE}🐳 Configurando Docker Compose...${NC}"
sudo -u trapforge tee docker-compose.prod.yml > /dev/null << 'EOF'
version: '3.8'
services:
  # Neural Forge API
  neural-forge-api:
    build:
      context: .
      dockerfile: docker/Dockerfile.ml-api.no-gpu
    container_name: neural-forge-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://trapuser:${DB_PASSWORD}@db:5432/trapforge
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    depends_on:
      - db
      - redis
    networks:
      - trapforge-network

  # PostgreSQL Database
  db:
    image: postgres:15
    container_name: trapforge-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: trapforge
      POSTGRES_USER: trapuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - trapforge-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: trapforge-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - trapforge-network

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    container_name: trapforge-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/dashboards/grafana:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    networks:
      - trapforge-network

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: trapforge-prometheus
    restart: unless-stopped
    volumes:
      - prometheus_data:/prometheus
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    networks:
      - trapforge-network

volumes:
  postgres_data:
  redis_data:
  grafana_data:
  prometheus_data:

networks:
  trapforge-network:
    driver: bridge
EOF

# 7. CREATE INITIAL DATABASE SCHEMA
echo -e "${BLUE}🗄️ Creando schema de base de datos...${NC}"
sudo -u trapforge mkdir -p database
sudo -u trapforge tee database/init.sql > /dev/null << 'EOF'
-- Neural Forge Trap Artist Database Schema

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(255) UNIQUE NOT NULL,
    artist_name VARCHAR(255) NOT NULL,
    song_title VARCHAR(255) NOT NULL,
    budget DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    target_countries TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Satellites table
CREATE TABLE IF NOT EXISTS satellites (
    id SERIAL PRIMARY KEY,
    satellite_name VARCHAR(255) NOT NULL,
    satellite_theme VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    last_upload TIMESTAMP,
    total_uploads INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Revenue tracking
CREATE TABLE IF NOT EXISTS revenue (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(255) REFERENCES campaigns(campaign_id),
    revenue_source VARCHAR(100),
    amount DECIMAL(10,2),
    artist_share DECIMAL(10,2),
    platform_share DECIMAL(10,2),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics events
CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100),
    campaign_id VARCHAR(255),
    data JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default satellites
INSERT INTO satellites (satellite_name, satellite_theme) VALUES
('DarkBeats_Official', 'Dark Trap Beats'),
('UrbanTrap_Studios', 'Urban Street Trap'),
('NeonTrap_Collective', 'Neon Futuristic Trap'),
('TrapML_Records', 'AI Generated Trap'),
('Neural_TrapHouse', 'Experimental Trap House')
ON CONFLICT DO NOTHING;
EOF

# 8. LAUNCH DOCKER SERVICES
echo -e "${BLUE}🚀 Lanzando servicios Docker...${NC}"
cd /home/trapforge/discografica-ml-system
export DB_PASSWORD=$DB_PASSWORD
export ADMIN_PASSWORD=$ADMIN_PASSWORD
sudo -u trapforge docker compose -f docker-compose.prod.yml up -d

# Wait for services to start
echo -e "${YELLOW}⏳ Esperando servicios (30s)...${NC}"
sleep 30

# 9. CONFIGURE NGINX
echo -e "${BLUE}🌐 Configurando Nginx...${NC}"
tee /etc/nginx/sites-available/trapforge > /dev/null << EOF
server {
    listen 80;
    server_name ${DOMAIN};
    client_max_body_size 100M;

    # Neural Forge API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Grafana Dashboard
    location /dashboard/ {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Campaign Launcher
    location / {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/trapforge /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 10. SETUP SSL (if domain is real)
if [[ $DOMAIN != *"example.com" ]]; then
    echo -e "${BLUE}🔒 Configurando SSL con Let's Encrypt...${NC}"
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
fi

# 11. CREATE MANAGEMENT SCRIPTS
echo -e "${BLUE}📋 Creando scripts de administración...${NC}"
tee /home/trapforge/manage_trapforge.sh > /dev/null << 'EOF'
#!/bin/bash
# Neural Forge Trap Artist Management Script

case $1 in
    "status")
        cd /home/trapforge/discografica-ml-system
        docker compose -f docker-compose.prod.yml ps
        ;;
    "logs")
        cd /home/trapforge/discografica-ml-system
        docker compose -f docker-compose.prod.yml logs -f
        ;;
    "restart")
        cd /home/trapforge/discografica-ml-system
        docker compose -f docker-compose.prod.yml restart
        ;;
    "campaign")
        cd /home/trapforge/discografica-ml-system
        docker compose -f docker-compose.prod.yml exec neural-forge-api python launch_trap_campaign.py
        ;;
    "backup")
        echo "Creating backup..."
        docker exec trapforge-db pg_dump -U trapuser trapforge > /home/trapforge/backup_$(date +%Y%m%d_%H%M%S).sql
        ;;
    *)
        echo "Usage: $0 {status|logs|restart|campaign|backup}"
        ;;
esac
EOF

chmod +x /home/trapforge/manage_trapforge.sh
chown trapforge:trapforge /home/trapforge/manage_trapforge.sh

# 12. FINAL SYSTEM CHECK
echo -e "${BLUE}🔍 Verificando sistema...${NC}"
sleep 10

# Check services
SERVICES_OK=true
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Neural Forge API no responde${NC}"
    SERVICES_OK=false
fi

if ! curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${RED}❌ Grafana no responde${NC}"
    SERVICES_OK=false
fi

# 13. SUCCESS MESSAGE
echo ""
echo -e "${GREEN}✅ NEURAL FORGE TRAP ARTIST DEPLOYMENT COMPLETADO!${NC}"
echo -e "${PURPLE}=================================================${NC}"
echo ""
echo -e "${YELLOW}🎵 INFORMACIÓN DEL SISTEMA:${NC}"
echo "Servidor: $HETZNER_IP"
echo "Dominio: $DOMAIN"
echo "Admin password: $ADMIN_PASSWORD"
echo ""
echo -e "${YELLOW}🔗 ACCESOS:${NC}"
echo "API: https://$DOMAIN/api/"
echo "Dashboard: https://$DOMAIN/dashboard/"
echo "Prometheus: https://$DOMAIN:9090/"
echo ""
echo -e "${YELLOW}📋 COMANDOS ÚTILES:${NC}"
echo "Status: /home/trapforge/manage_trapforge.sh status"
echo "Logs: /home/trapforge/manage_trapforge.sh logs"
echo "Nueva campaña: /home/trapforge/manage_trapforge.sh campaign"
echo "Backup: /home/trapforge/manage_trapforge.sh backup"
echo ""
echo -e "${YELLOW}💰 COSTOS ESTIMADOS:${NC}"
echo "Servidor CPX41: \$92/mes"
echo "Dominio: \$12/año"
echo "Total: ~\$102/mes"
echo ""

if [ "$SERVICES_OK" = true ]; then
    echo -e "${GREEN}🔥 ¡TrapStar ML listo para dominar el mercado hispano!${NC}"
    echo -e "${GREEN}🚀 Sistema operacional al 100%${NC}"
else
    echo -e "${RED}⚠️ Algunos servicios necesitan revisión${NC}"
    echo "Revisa logs: docker compose -f docker-compose.prod.yml logs"
fi

echo ""
echo -e "${PURPLE}🎵 Neural Forge - Convirtiendo beats en viral desde Hetzner 🎵${NC}"