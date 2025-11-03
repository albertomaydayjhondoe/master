# 🚀 MIGRACIÓN SISTEMA META ADS A VPS DEDICADO

## 🎯 PROPÓSITO GENERAL

### Rol del Sistema
El **TikTok Viral ML System** es un ecosistema completo de automatización para campañas artísticas que integra:
- **Generación de contenido viral** mediante IA
- **Automatización de Meta Ads** para promoción pagada  
- **Distribución en redes sociales** (TikTok, Instagram, Facebook)
- **Analytics avanzados** con modelos COCO/YOLO
- **Gestión de triggers** para orquestación automática

### Objetivo de Migración
Migrar de Railway (fragmentado, costoso, limitado) a **VPS unificado Hetzner CX21** (10€/mes) para:
- ✅ **4x más capacidad** (4GB RAM vs 1GB)
- ✅ **50% menos coste** (10€ vs 20€)
- ✅ **99.9% uptime** sin hibernaciones
- ✅ **Todos los módulos concurrentes** sin límites

---

## 🏗️ ARQUITECTURA VPS OBJETIVO

### 📊 Servicios Simultáneos
```
Puerto 7860: 🎯 Gradio Trigger Manager     - Control humano
Puerto 8501: 📊 Streamlit COCO Analytics   - Dashboards ML  
Puerto 8000: 🤖 ML API FastAPI             - Inferencia IA
Puerto 8080: 🎭 Orchestrator Central       - Coordinación
Puerto 3000: 💬 Bot Telegram               - Intercambio social
Puerto 9000: 📢 Módulo Meta Ads            - Campañas pagadas
Puerto 9001: 📱 Módulo Fanpages            - Contenido orgánico
Puerto 5432: 🗄️ PostgreSQL                 - Base datos
Puerto 6379: ⚡ Redis                       - Cola tareas
```

### 🛡️ Supervisión y Persistencia
- **Systemd**: Servicios auto-reinicio
- **Nginx**: Reverse proxy + SSL
- **Logs centralizados**: `/var/log/metasystem/`
- **Backups diarios**: Automáticos S3/local
- **Monitoreo**: Health checks cada 5min

---

## 📋 PLAN DE MIGRACIÓN DETALLADO

### 🌟 FASE 1: APROVISIONAMIENTO VPS

#### 1.1 Contratación Hetzner CX21
```bash
# Especificaciones objetivo
CPU: 2 vCPU dedicadas
RAM: 4GB dedicada  
SSD: 40GB NVMe
Tráfico: 20TB/mes
Coste: 10€/mes
OS: Ubuntu 24.04 LTS
```

#### 1.2 Configuración Inicial
```bash
# Conexión inicial
ssh root@IP_VPS

# Actualización sistema
apt update && apt upgrade -y
apt install -y build-essential git curl wget vim htop

# Configuración básica
hostnamectl set-hostname metasystem-prod
timedatectl set-timezone Europe/Madrid
```

#### 1.3 Usuario y Seguridad
```bash
# Crear usuario operacional
adduser metasystem
usermod -aG sudo metasystem

# Configurar SSH keys
mkdir -p /home/metasystem/.ssh
cp /root/.ssh/authorized_keys /home/metasystem/.ssh/
chown -R metasystem:metasystem /home/metasystem/.ssh

# Firewall UFW
ufw allow 22/tcp
ufw allow 80/tcp  
ufw allow 443/tcp
ufw enable

# Deshabilitar root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd
```

### 🐍 FASE 2: INSTALACIÓN DEPENDENCIAS

#### 2.1 Python y Stack ML
```bash
# Python 3.11 + herramientas
apt install -y python3.11 python3.11-venv python3-pip
python3.11 -m pip install --upgrade pip setuptools wheel

# FFmpeg para procesamiento video
apt install -y ffmpeg

# Node.js para frontend
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
```

#### 2.2 Bases de Datos
```bash
# PostgreSQL
apt install -y postgresql postgresql-contrib
systemctl start postgresql
systemctl enable postgresql

# Redis para colas
apt install -y redis-server
systemctl start redis
systemctl enable redis

# Nginx reverse proxy
apt install -y nginx
systemctl start nginx
systemctl enable nginx
```

### 📦 FASE 3: TRANSFERENCIA CÓDIGO

#### 3.1 Clonar Repositorios
```bash
su - metasystem
mkdir -p /home/metasystem/apps
cd /home/metasystem/apps

# Clonar desde GitHub (adaptar URLs)
git clone https://github.com/albertomaydayjhondoe/master.git metasystem-core
cd metasystem-core
git checkout experimental/vps-migration
```

#### 3.2 Entornos Virtuales
```bash
# Crear entorno para cada módulo
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias específicas VPS
pip install -r requirements-vps.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install ultralytics librosa openai-whisper gradio streamlit
deactivate
```

#### 3.3 Variables de Entorno VPS
```bash
nano /home/metasystem/apps/.env
```

```env
# Base de datos
DATABASE_URL=postgresql://metasystem:PASSWORD@localhost:5432/metasystem_db
REDIS_URL=redis://localhost:6379/0

# APIs Externas  
META_API_KEY=tu_meta_api_key
YOUTUBE_API_KEY=tu_youtube_api_key
SPOTIFY_CLIENT_ID=tu_spotify_client_id
SPOTIFY_CLIENT_SECRET=tu_spotify_client_secret
TELEGRAM_BOT_TOKEN=tu_telegram_bot_token
OPENAI_API_KEY=tu_openai_api_key

# Configuración VPS
SECRET_KEY=clave_secreta_fuerte_vps
ENVIRONMENT=production
LOG_LEVEL=INFO
HOST=0.0.0.0
VPS_MODE=true
DUMMY_MODE=false
```

### ⚙️ FASE 4: SERVICIOS SYSTEMD

#### 4.1 Gradio Trigger Manager
```bash
sudo nano /etc/systemd/system/gradio-trigger.service
```

```ini
[Unit]
Description=Gradio Trigger Manager - VPS Production
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=metasystem
WorkingDirectory=/home/metasystem/apps/metasystem-core
Environment="PATH=/home/metasystem/apps/metasystem-core/venv/bin"
EnvironmentFile=/home/metasystem/apps/.env
ExecStart=/home/metasystem/apps/metasystem-core/venv/bin/python gradio_trigger_manager.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/metasystem/gradio.log
StandardError=append:/var/log/metasystem/gradio.error.log

[Install]
WantedBy=multi-user.target
```

#### 4.2 Streamlit COCO Analytics
```bash
sudo nano /etc/systemd/system/streamlit-analytics.service
```

```ini
[Unit]
Description=Streamlit COCO Analytics - VPS Production
After=network.target

[Service]
Type=simple
User=metasystem
WorkingDirectory=/home/metasystem/apps/metasystem-core
Environment="PATH=/home/metasystem/apps/metasystem-core/venv/bin"
EnvironmentFile=/home/metasystem/apps/.env
ExecStart=/home/metasystem/apps/metasystem-core/venv/bin/streamlit run streamlit_coco_analytics.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10
StandardOutput=append:/var/log/metasystem/streamlit.log
StandardError=append:/var/log/metasystem/streamlit.error.log

[Install]
WantedBy=multi-user.target
```

#### 4.3 ML API FastAPI
```bash
sudo nano /etc/systemd/system/ml-api.service
```

```ini
[Unit]
Description=ML API FastAPI - VPS Production
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=metasystem
WorkingDirectory=/home/metasystem/apps/metasystem-core
Environment="PATH=/home/metasystem/apps/metasystem-core/venv/bin"
EnvironmentFile=/home/metasystem/apps/.env
ExecStart=/home/metasystem/apps/metasystem-core/venv/bin/uvicorn ml_core.api.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10
StandardOutput=append:/var/log/metasystem/ml-api.log
StandardError=append:/var/log/metasystem/ml-api.error.log

[Install]
WantedBy=multi-user.target
```

#### 4.4 Habilitar Servicios
```bash
# Crear logs directory
sudo mkdir -p /var/log/metasystem
sudo chown -R metasystem:metasystem /var/log/metasystem

# Habilitar servicios
sudo systemctl daemon-reload
sudo systemctl enable gradio-trigger.service
sudo systemctl enable streamlit-analytics.service  
sudo systemctl enable ml-api.service

# Iniciar servicios
sudo systemctl start gradio-trigger.service
sudo systemctl start streamlit-analytics.service
sudo systemctl start ml-api.service

# Verificar estado
sudo systemctl status gradio-trigger.service
sudo systemctl status streamlit-analytics.service
sudo systemctl status ml-api.service
```

### 🌐 FASE 5: NGINX REVERSE PROXY

#### 5.1 Configuración SSL
```bash
# Instalar Certbot
apt install -y certbot python3-certbot-nginx

# Obtener certificados (adaptar dominio)
certbot --nginx -d metasystem.tudominio.com -d api.metasystem.tudominio.com
```

#### 5.2 Virtual Hosts
```bash
sudo nano /etc/nginx/sites-available/metasystem-vps
```

```nginx
upstream gradio_backend {
    server 127.0.0.1:7860;
}

upstream streamlit_backend {
    server 127.0.0.1:8501;
}

upstream ml_api_backend {
    server 127.0.0.1:8000;
}

# Gradio Trigger Manager
server {
    listen 443 ssl http2;
    server_name metasystem.tudominio.com;

    ssl_certificate /etc/letsencrypt/live/metasystem.tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/metasystem.tudominio.com/privkey.pem;

    location / {
        proxy_pass http://gradio_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Streamlit Analytics
server {
    listen 443 ssl http2;
    server_name analytics.metasystem.tudominio.com;

    ssl_certificate /etc/letsencrypt/live/metasystem.tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/metasystem.tudominio.com/privkey.pem;

    location / {
        proxy_pass http://streamlit_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /_stcore/stream {
        proxy_pass http://streamlit_backend/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# ML API
server {
    listen 443 ssl http2;
    server_name api.metasystem.tudominio.com;

    ssl_certificate /etc/letsencrypt/live/metasystem.tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/metasystem.tudominio.com/privkey.pem;

    location / {
        proxy_pass http://ml_api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar configuración
sudo ln -s /etc/nginx/sites-available/metasystem-vps /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 🔄 FASE 6: AUTOMATIZACIÓN Y MONITOREO

#### 6.1 Backup Diario
```bash
mkdir -p /home/metasystem/scripts
nano /home/metasystem/scripts/backup_daily.sh
```

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/home/metasystem/backups/$TIMESTAMP

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump -U metasystem metasystem_db | gzip > $BACKUP_DIR/db_backup.sql.gz

# Backup archivos importantes
tar -czf $BACKUP_DIR/files_backup.tar.gz \
    /home/metasystem/apps/metasystem-core/data \
    /home/metasystem/apps/metasystem-core/config \
    /var/log/metasystem

# Limpiar backups antiguos (>7 días)
find /home/metasystem/backups -type d -mtime +7 -exec rm -rf {} +

echo "$(date): Backup completado en $BACKUP_DIR"
```

```bash
chmod +x /home/metasystem/scripts/backup_daily.sh

# Programar backup diario 3AM
crontab -e
0 3 * * * /home/metasystem/scripts/backup_daily.sh >> /var/log/metasystem/backup.log 2>&1
```

#### 6.2 Health Check Automático
```bash
nano /home/metasystem/scripts/health_check.sh
```

```bash
#!/bin/bash
SERVICES=("gradio-trigger" "streamlit-analytics" "ml-api")

for service in "${SERVICES[@]}"; do
    if ! systemctl is-active --quiet $service.service; then
        echo "$(date): $service is DOWN, restarting..." >> /var/log/metasystem/health_check.log
        systemctl restart $service.service
        
        # Alerta Telegram (opcional)
        curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$ADMIN_CHAT_ID" \
            -d "text=⚠️ VPS Alert: $service service restarted"
    fi
done

# Health check API
curl -f https://api.metasystem.tudominio.com/health > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "$(date): API health check failed" >> /var/log/metasystem/health_check.log
fi
```

```bash
chmod +x /home/metasystem/scripts/health_check.sh

# Health check cada 5 minutos
crontab -e  
*/5 * * * * /home/metasystem/scripts/health_check.sh
```

### 📊 FASE 7: VALIDACIÓN Y TESTING

#### 7.1 Checklist de Verificación
```bash
# Verificar servicios activos
systemctl status gradio-trigger streamlit-analytics ml-api

# Test endpoints
curl -I https://metasystem.tudominio.com
curl -I https://analytics.metasystem.tudominio.com  
curl -I https://api.metasystem.tudominio.com

# Health check API
curl https://api.metasystem.tudominio.com/health

# Verificar logs
tail -f /var/log/metasystem/gradio.log
tail -f /var/log/metasystem/streamlit.log
tail -f /var/log/metasystem/ml-api.log
```

#### 7.2 Load Testing
```bash
# Instalar Apache Bench
apt install -y apache2-utils

# Test carga API
ab -n 1000 -c 10 https://api.metasystem.tudominio.com/health

# Verificar performance < 200ms
```

---

## 🎯 BENEFICIOS POST-MIGRACIÓN

### 💰 Económicos
- **Ahorro anual**: 120€ (50% reducción)
- **Coste fijo**: 10€/mes sin sorpresas
- **ROI inmediato**: Recuperación en primer mes

### 🚀 Operativos  
- **4x más RAM**: De 1GB a 4GB dedicados
- **CPU dedicada**: Sin throttling ni burst limits
- **Uptime 99.9%**: Sin hibernaciones Railway
- **Procesamiento 3x más rápido**: Videos de 15min a 5min
- **Todos los módulos simultáneos**: Sin límites de servicios

### 🔧 Técnicos
- **Control total**: Acceso root completo
- **Escalabilidad**: Upgrade vertical en 1 clic
- **Logs persistentes**: Debugging facilitado  
- **Backups automáticos**: Recuperación garantizada
- **Monitoreo personalizado**: Alertas en tiempo real

---

## 📋 CHECKLIST DE MIGRACIÓN

### ✅ Pre-Migración
- [ ] Contratar VPS Hetzner CX21
- [ ] Configurar DNS apuntando al VPS
- [ ] Exportar datos de Railway
- [ ] Preparar certificados SSL

### ✅ Durante Migración  
- [ ] Configurar servicios systemd
- [ ] Importar base de datos
- [ ] Configurar Nginx reverse proxy
- [ ] Verificar todos los endpoints

### ✅ Post-Migración
- [ ] Health checks funcionando
- [ ] Backups configurados  
- [ ] Monitoreo activo
- [ ] Performance validada
- [ ] Railway desconectado

---

## 🚀 NEXT STEPS

1. **Inmediato**: Contratar VPS Hetzner CX21
2. **Fin de semana**: Ejecutar migración completa 
3. **Seguimiento**: Monitorizar 7 días
4. **Optimización**: Ajustar configuraciones según carga real

**🎯 Resultado esperado**: Sistema unificado, estable, escalable y económico funcionando al 100% en VPS dedicado.