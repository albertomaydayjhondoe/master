# 🚀 DEPLOY V3 EN CLOUD

Guía para desplegar el sistema V3 en producción (cloud).

---

## 📋 **Pre-requisitos**

### **Servidor Cloud:**
- **CPU:** 4 cores mínimo (8 cores recomendado)
- **RAM:** 8 GB mínimo (16 GB recomendado)
- **Disk:** 50 GB mínimo (100 GB recomendado para videos)
- **OS:** Ubuntu 22.04 LTS / Debian 11+
- **Puertos:** 80, 443, 8000, 8501, 9000-9003, 10000, 5678, 3000

### **Software:**
- Docker 24.0+
- Docker Compose 2.20+
- Git
- (Opcional) Nginx para reverse proxy

---

## 🔧 **PASO 1: Preparar Servidor**

```bash
# SSH al servidor
ssh usuario@tu-servidor.com

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

---

## 📦 **PASO 2: Clonar Repositorio**

```bash
# Clonar proyecto
git clone https://github.com/TU_USUARIO/master.git
cd master

# Checkout a main (o tu branch)
git checkout main
```

---

## 🔐 **PASO 3: Configurar Credenciales**

### **Opción A: Interactivo (Recomendado)**

```bash
./setup-credentials.sh
```

Pedirá:
- Meta Ads credentials
- YouTube API credentials
- Artista genérico (nombre, YouTube, Instagram, TikTok)
- Runway ML (opcional)
- n8n webhooks
- Telegram (opcional)
- Passwords (PostgreSQL, n8n, Grafana)

### **Opción B: Manual**

```bash
# Copiar template
cp .env.v3 .env

# Editar con tus credenciales
nano .env

# O usa vim
vim .env
```

Actualiza:
```bash
# Meta Ads
META_ACCESS_TOKEN=tu_token_aqui
META_AD_ACCOUNT_ID=act_123456789
META_PIXEL_ID=123456789012345

# YouTube
YOUTUBE_CLIENT_ID=xxx.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-xxx
YOUTUBE_CHANNEL_ID=UC_xxx

# Artista Genérico
ARTIST_NAME=Nombre del Artista
ARTIST_YOUTUBE_CHANNEL=https://www.youtube.com/@artist
ARTIST_INSTAGRAM=@artist_instagram
ARTIST_TIKTOK=@artist_tiktok

# Passwords (¡CAMBIAR EN PRODUCCIÓN!)
POSTGRES_PASSWORD=strong_random_password_here
N8N_PASSWORD=another_strong_password
GRAFANA_PASSWORD=yet_another_strong_password
```

---

## 📥 **PASO 4: Descargar Modelos YOLOv8**

```bash
./download-models.sh
```

Descarga:
- `yolov8n_screenshot.pt` (6.2 MB)
- `yolov8s_video.pt` (21.5 MB)
- `yolov8m_detection.pt` (49.7 MB)

---

## 🐳 **PASO 5: Build & Deploy**

### **Opción A: Script Automatizado (Recomendado)**

```bash
./build-and-deploy-v3.sh
```

Este script:
1. Verifica prerequisites
2. Build 3 imágenes Docker
3. Pregunta si desplegar ahora
4. Deploy con docker-compose
5. Verifica health

### **Opción B: Manual**

```bash
# Build imágenes
docker build -f docker/ml-core-v3.Dockerfile -t community-manager/ml-core:v3 .
docker build -f docker/unified-orchestrator-v3.Dockerfile -t community-manager/unified-orchestrator:v3 .
docker build -f docker/dashboard-v3.Dockerfile -t community-manager/dashboard:v3 .

# Deploy
docker-compose -f docker-compose-v3.yml up -d

# Ver logs
docker-compose -f docker-compose-v3.yml logs -f
```

---

## ✅ **PASO 6: Verificar Deployment**

```bash
# Health check
./v3-docker.sh health

# Ver servicios corriendo
docker-compose -f docker-compose-v3.yml ps

# Ver logs en tiempo real
./v3-docker.sh logs unified-orchestrator
```

**Output esperado:**
```
✅ ml-core: Healthy
✅ unified-orchestrator: Healthy
✅ meta-ads-manager: Healthy
✅ pixel-tracker: Healthy
✅ youtube-uploader: Healthy
✅ n8n: Healthy
✅ dashboard: Healthy
✅ postgres: Healthy
✅ redis: Healthy
```

---

## 🌐 **PASO 7: Configurar Nginx (Reverse Proxy)**

Para acceso HTTPS en producción:

```bash
# Instalar Nginx
sudo apt install nginx -y

# Crear config
sudo nano /etc/nginx/sites-available/community-manager
```

**Contenido:**
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    # Dashboard
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:10000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # n8n
    location /n8n/ {
        proxy_pass http://localhost:5678/;
        proxy_set_header Host $host;
    }

    # Grafana
    location /grafana/ {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
    }
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/community-manager /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### **SSL con Let's Encrypt:**

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado
sudo certbot --nginx -d tu-dominio.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## 🔒 **PASO 8: Configurar Firewall**

```bash
# UFW (Ubuntu Firewall)
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS

# Denegar acceso directo a puertos internos
sudo ufw deny 5432/tcp     # PostgreSQL
sudo ufw deny 6379/tcp     # Redis
sudo ufw deny 8000/tcp     # ML Core (solo via Nginx)
sudo ufw deny 10000/tcp    # API (solo via Nginx)

# Activar firewall
sudo ufw enable
sudo ufw status
```

---

## 🎛️ **PASO 9: Configurar n8n Workflows**

```bash
./n8n-setup.sh
```

O manualmente:
1. Abre: https://tu-dominio.com/n8n
2. Login: `admin` / `viral_admin_2025` (cambiar password)
3. Import workflows:
   - `orchestration/n8n_workflows/main_orchestrator.json`
   - `orchestration/n8n_workflows/ml_decision_engine.json`
   - `orchestration/n8n_workflows/device_farm_trigger.json`
   - `orchestration/n8n_workflows/landing_page_generator.json`
4. Activa workflows (toggle ON)

---

## 🚀 **PASO 10: Lanzar Primera Campaña**

### **Desde Dashboard:**
```
https://tu-dominio.com
→ Tab: "Lanzar Campaña"
→ Completa datos
→ Click: "Lanzar Campaña Viral"
```

### **Desde API:**
```bash
curl -X POST https://tu-dominio.com/api/launch \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/data/videos/video.mp4",
    "artist_name": "Stakas",
    "song_name": "Nueva Vida",
    "genre": "Trap",
    "daily_ad_budget": 50.0,
    "target_countries": ["US", "MX", "ES"]
  }'
```

### **Desde CLI (en servidor):**
```bash
python unified_system_v3.py \
  --mode launch \
  --video "/data/videos/video.mp4" \
  --campaign-name "Mi Hit 2025" \
  --artist-name "Stakas" \
  --paid-budget 500.0
```

---

## 📊 **PASO 11: Monitorear con Grafana**

```
https://tu-dominio.com/grafana
Login: admin / viral_monitor_2025 (cambiar password)

Dashboards:
- Campaign Performance
- Channel Monitor
- UTM Health
- Budget Tracking
```

---

## 🔄 **Actualizar Sistema**

```bash
# Pull latest changes
git pull origin main

# Rebuild imágenes
./build-and-deploy-v3.sh

# O rebuild específico
docker-compose -f docker-compose-v3.yml build unified-orchestrator
docker-compose -f docker-compose-v3.yml up -d unified-orchestrator
```

---

## 🛠️ **Troubleshooting**

### **Servicio no inicia:**
```bash
# Ver logs
docker-compose -f docker-compose-v3.yml logs unified-orchestrator

# Reiniciar servicio
docker-compose -f docker-compose-v3.yml restart unified-orchestrator
```

### **Base de datos no conecta:**
```bash
# Verificar PostgreSQL
docker exec -it unified-postgres psql -U postgres -d community_manager

# Reset database
./v3-docker.sh psql < database/schema.sql
```

### **Memory issues:**
```bash
# Ver uso de recursos
docker stats

# Aumentar límites en docker-compose-v3.yml
services:
  unified-orchestrator:
    mem_limit: 2g
    mem_reservation: 1g
```

---

## 📈 **Optimización Producción**

### **1. Database Backups:**
```bash
# Crear cron job para backups
crontab -e

# Backup diario a las 3am
0 3 * * * docker exec unified-postgres pg_dump -U postgres community_manager > /backups/db_$(date +\%Y\%m\%d).sql
```

### **2. Log Rotation:**
```bash
# Configurar logrotate
sudo nano /etc/logrotate.d/docker-containers

/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    missingok
    delaycompress
    copytruncate
}
```

### **3. Resource Limits:**
```yaml
# docker-compose-v3.yml
services:
  unified-orchestrator:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## ✅ **Checklist Post-Deploy**

- [ ] Todas las credenciales configuradas
- [ ] Modelos YOLOv8 descargados
- [ ] Servicios corriendo (health check OK)
- [ ] Nginx configurado con SSL
- [ ] Firewall configurado
- [ ] n8n workflows activados
- [ ] Primera campaña lanzada exitosamente
- [ ] Grafana configurado
- [ ] Backups automáticos configurados
- [ ] Passwords de producción cambiados
- [ ] Logs monitoreados

---

## 📞 **Soporte**

- **Documentación:** Ver carpeta `/docs`
- **Issues:** [GitHub Issues](https://github.com/TU_USUARIO/master/issues)
- **Logs:** `./v3-docker.sh logs [service]`

---

## 🎉 **¡LISTO!**

Tu sistema V3 está desplegado en producción y listo para **romper las RRSS** 🚀🔥
