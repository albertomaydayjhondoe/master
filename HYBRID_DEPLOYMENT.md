# 🔄 Hybrid Deployment Guide - Docker + GitHub Codespaces

## 24/7 Meta Ads Automation - Dual Environment Support

Este sistema está diseñado para ejecutarse **indistintamente** en Docker local o GitHub Codespaces, permitiendo máxima flexibilidad para operaciones 24/7.

---

## 🎯 Escenarios de Deployment

### Scenario 1: Docker 24/7 (Recomendado para Producción)
- **Mejor para:** Servidor dedicado, VPS, Cloud VM
- **Ventajas:** Control total, sin límites de tiempo, costos predecibles
- **Uptime:** 24/7/365
- **Costo:** Según hosting elegido

### Scenario 2: GitHub Codespaces 24/7
- **Mejor para:** Testing, desarrollo, operaciones temporales
- **Ventajas:** Setup instantáneo, sin infraestructura
- **Uptime:** 24/7 con configuración especial
- **Costo:** 60 horas gratis/mes, $0.18/hora después

### Scenario 3: Hybrid (Mejor de ambos mundos)
- **Docker para producción estable**
- **Codespaces para testing y emergency backup**
- **Failover automático entre ambos**

---

## 🐳 Option A: Docker 24/7 Production

### 1. Deploy en VPS/Cloud

#### DigitalOcean (Recomendado - Simple y económico)
```bash
# Crear Droplet Ubuntu 22.04
# 2 vCPU, 4GB RAM - $24/mes
ssh root@your-droplet-ip

# Clonar repo
git clone https://github.com/albertomaydayjhondoe/master.git
cd master

# Configurar
cp .env.example .env
nano .env  # Configurar credenciales

# Iniciar
./docker-manage.sh start

# Verificar que corre 24/7
./docker-manage.sh status
```

#### AWS ECS (Escalable)
```bash
# Usar docker-compose.yml con AWS ECS CLI
ecs-cli compose up --create-log-groups

# O usar AWS Fargate para serverless
```

#### Google Cloud Run (Serverless)
```bash
# Deploy automático desde docker-compose
gcloud run deploy --source .
```

### 2. Monitoreo 24/7
```bash
# Configurar auto-restart
docker-compose up -d --restart=always

# Configurar health checks
# (ya incluidos en docker-compose.yml)

# Logs persistentes
docker-compose logs -f > /var/log/tiktok-automation.log &
```

### 3. Backup Automático
```bash
# Crontab para backup diario
crontab -e

# Añadir:
0 2 * * * cd /root/master && ./docker-manage.sh backup
0 4 * * * cd /root/master && git add backups/ && git commit -m "Backup $(date)" && git push
```

---

## 💻 Option B: GitHub Codespaces 24/7

### 1. Configuración para Mantener Activo

GitHub Codespaces se detiene automáticamente tras 30 minutos de inactividad. Para mantenerlo 24/7:

#### A. Keep-Alive Script
```bash
# Crear keep-alive.sh
cat > keep-alive.sh << 'EOF'
#!/bin/bash
while true; do
    echo "Keeping codespace alive: $(date)" >> /tmp/keepalive.log
    curl -s http://localhost:8501 > /dev/null
    curl -s http://localhost:8000/health > /dev/null
    sleep 120  # Cada 2 minutos
done
EOF

chmod +x keep-alive.sh

# Ejecutar en background
nohup ./keep-alive.sh &
```

#### B. Configuración de Timeout
```json
// .devcontainer/devcontainer.json
{
    "settings": {
        "codespaces.idleTimeout": "4h"  // Máximo 4 horas
    },
    "postStartCommand": "./keep-alive.sh &"
}
```

### 2. Iniciar Servicios en Codespaces

```bash
# Método 1: Sin Docker (más ligero)
# Dashboard
nohup streamlit run scripts/production_control_dashboard.py &

# ML Core (si tienes API)
nohup python -m ml_core.api.main &

# Telegram Bot
nohup python telegram_like4like_bot.py &

# Método 2: Con Docker (más robusto)
docker-compose up -d
```

### 3. Limitaciones de Codespaces

⚠️ **Importantes:**
- **Timeout:** Máximo 4 horas de inactividad (Free tier)
- **Storage:** 15GB por workspace
- **CPU:** Compartido, no garantizado
- **Network:** IP cambia cada reinicio
- **Costo:** $0.18/hora después de 60h gratis

💡 **Solución:** Usar script de keep-alive + Codespaces Pro ($10/mes = 90h)

---

## 🔄 Option C: Hybrid Setup (RECOMENDADO)

### Arquitectura Híbrida

```
┌─────────────────────────────────────────────────────────┐
│                   PRODUCTION (Docker)                   │
│              VPS/Cloud con Docker 24/7                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Dashboard   │  │   ML Core    │  │  Meta Ads    │  │
│  │   (8501)     │  │   (8000)     │  │   (8002)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ║
                    Failover/Backup
                            ║
┌─────────────────────────────────────────────────────────┐
│            DEVELOPMENT/BACKUP (Codespaces)              │
│                GitHub Codespaces                        │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │  Dashboard   │  │ Telegram Bot │                    │
│  │   (Testing)  │  │  (Backup)    │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

### Configuración Híbrida

```bash
# 1. Producción en Docker (siempre corriendo)
# En VPS
export DEPLOYMENT_ENV=production
export DUMMY_MODE=false
./docker-manage.sh start

# 2. Backup en Codespaces (para emergencias)
# En GitHub Codespaces
export DEPLOYMENT_ENV=backup
export DUMMY_MODE=true
./keep-alive.sh &
streamlit run scripts/production_control_dashboard.py &

# 3. Failover automático (usar mismo .env y datos compartidos)
```

---

## 📊 Comparación de Costos 24/7

### Docker en VPS (DigitalOcean)
```
Droplet 4GB RAM: $24/mes
Backup 25GB: $5/mes
Total: $29/mes
Uptime: 99.99%
```

### Docker en AWS
```
t3.medium: ~$30/mes
EBS 20GB: $2/mes
Total: ~$32/mes
Uptime: 99.99%
```

### GitHub Codespaces
```
Free: 60h/mes ($0)
Después: $0.18/hora x 720h = $129.60/mes
Codespaces Pro: $10/mes base + overage
Total: $10-140/mes (variable)
Uptime: 95% (con keep-alive)
```

### Hybrid (Recomendado)
```
VPS: $29/mes (producción)
Codespaces Free: $0 (backup/testing)
Total: $29/mes
Uptime: 99.99% + backup
```

---

## 🚀 Setup Rápido para 24/7

### Para Docker (Producción)

```bash
# 1. En tu VPS
git clone https://github.com/albertomaydayjhondoe/master.git
cd master

# 2. Configurar
cp .env.example .env
nano .env  # Poner credenciales reales

# 3. Iniciar con auto-restart
docker-compose up -d --restart=always

# 4. Verificar
./docker-manage.sh health

# 5. Configurar monitoreo
./docker-manage.sh status
```

### Para Codespaces (Development/Backup)

```bash
# 1. Ya estás en Codespaces (este ambiente)

# 2. Keep-alive automático
cat > /tmp/keepalive.sh << 'EOF'
#!/bin/bash
while true; do
    curl -s http://localhost:8501 > /dev/null 2>&1
    sleep 120
done
EOF
chmod +x /tmp/keepalive.sh
nohup /tmp/keepalive.sh &

# 3. Iniciar servicios
streamlit run scripts/production_control_dashboard.py &
python telegram_like4like_bot.py &

# 4. Verificar
ps aux | grep -E "(streamlit|telegram)"
```

---

## 🔐 Configuración de Producción

### .env para Ambiente Aleatorio

```bash
# === DEPLOYMENT CONFIGURATION ===
DEPLOYMENT_ENV=${DEPLOYMENT_ENV:-development}  # production | development | backup
DUMMY_MODE=${DUMMY_MODE:-true}  # false para producción

# === META ADS (24/7 Production) ===
META_APP_ID=your_app_id
META_APP_SECRET=your_secret
META_ACCESS_TOKEN=your_long_lived_token  # Renovar cada 60 días
META_AD_ACCOUNT_ID=act_123456789
META_PAGE_ID=your_page_id
META_PIXEL_ID=your_pixel_id

# === SHARED DATABASE (para ambos ambientes) ===
# Usar base de datos externa (no local)
DATABASE_URL=postgresql://user:pass@external-db.com:5432/tiktok_automation

# === REDIS COMPARTIDO ===
REDIS_URL=redis://user:pass@external-redis.com:6379

# === MONITORING ===
HEALTHCHECK_URL=https://hc-ping.com/your-check-id  # Healthchecks.io
SLACK_WEBHOOK=https://hooks.slack.com/your-webhook  # Alertas
```

---

## 📈 Monitoreo 24/7

### Healthchecks.io (Gratis)

```bash
# Registrarse en https://healthchecks.io
# Crear check "TikTok Automation"

# Ping cada 5 minutos
while true; do
    curl -fsS --retry 3 https://hc-ping.com/YOUR-UUID-HERE > /dev/null
    sleep 300
done
```

### UptimeRobot (Gratis - 50 monitores)

```bash
# Configurar en https://uptimerobot.com
# Monitor HTTP(s) para:
# - http://your-vps:8501 (Dashboard)
# - http://your-vps:8000/health (ML API)
# - http://your-vps:8002/health (Meta Ads)
```

---

## 🔄 Failover Automático

```bash
# Script de failover
cat > failover-check.sh << 'EOF'
#!/bin/bash

PRIMARY="http://your-vps-ip:8501"
BACKUP="https://your-codespace-url:8501"

# Check primary
if ! curl -sf $PRIMARY/health > /dev/null; then
    echo "Primary down! Activating backup..."
    
    # Activar servicios en Codespaces
    curl -X POST $BACKUP/activate
    
    # Notificar
    curl -X POST $SLACK_WEBHOOK -d '{"text":"Failover activated!"}'
fi
EOF

# Ejecutar cada minuto
* * * * * /root/master/failover-check.sh
```

---

## ✅ Recomendación Final

### Para Meta Ads 24/7:

1. **Producción Principal:** Docker en VPS ($29/mes)
   - DigitalOcean Droplet 4GB
   - Auto-restart habilitado
   - Backups diarios automáticos

2. **Backup/Testing:** GitHub Codespaces (Free tier)
   - Desarrollo y testing
   - Emergency failover
   - Sin costo adicional

3. **Datos Compartidos:**
   - Base de datos externa (PostgreSQL)
   - Redis externo (Upstash.com - gratis)
   - S3 para backups

### Comandos para Ambos Ambientes:

```bash
# Detectar ambiente automáticamente
if [ -n "$CODESPACE_NAME" ]; then
    export DEPLOYMENT_ENV=codespaces
    # Configuración ligera
else
    export DEPLOYMENT_ENV=docker
    # Configuración full
fi

# Iniciar apropiadamente
./docker-manage.sh start
```

---

## 🆘 Troubleshooting

### Codespaces se detiene
```bash
# Aumentar keep-alive frequency
# Usar Codespaces Pro ($10/mes)
# O migrar a Docker VPS
```

### Docker en VPS sin memoria
```bash
# Añadir swap
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

### Meta Ads token expira
```bash
# Renovar token cada 60 días
# Usar token long-lived
# Configurar auto-refresh en código
```

---

**TL;DR:** Usa Docker en VPS para producción 24/7 ($29/mes) y Codespaces como backup/desarrollo (gratis). Ambos comparten datos externos.
