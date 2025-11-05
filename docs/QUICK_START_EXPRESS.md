# ⚡ Neural Forge - Quick Start Express
## Deployment en 15 Minutos

---

## 🚀 **OPCIÓN A: Deployment Automático Completo**

### **1 Comando = Sistema Completo**

```bash
# Descarga y ejecuta el installer automático
curl -fsSL https://raw.githubusercontent.com/tu-usuario/neural-forge/main/deploy/quick-install.sh | bash
```

**¿Qué hace este comando?**
- ✅ Configura VPS completo
- ✅ Instala Docker y dependencias
- ✅ Despliega todos los servicios
- ✅ Configura SSL automático
- ✅ Activa monitoreo completo

---

## 🛠️ **OPCIÓN B: Deployment Manual Rápido**

### **Paso 1: Preparación (2 minutos)**

```bash
# En tu servidor Hetzner
ssh root@tu-servidor-ip

# Descarga Neural Forge
git clone https://github.com/tu-usuario/neural-forge.git
cd neural-forge

# Configuración exprés
cp .env.production.template .env.production
```

### **Paso 2: Configuración Crítica (3 minutos)**

```bash
# Edita solo las variables ESENCIALES
nano .env.production
```

**Variables MÍNIMAS a cambiar:**
```bash
DOMAIN=tu-dominio.com
SSL_EMAIL=tu@email.com
POSTGRES_PASSWORD=CambiaEstaPassword123!
SECRET_KEY=CambiaEstaClaveSecreta456!
```

### **Paso 3: Deployment Express (10 minutos)**

```bash
# Un solo comando lo hace todo
make deploy-production
```

**O ejecuta manualmente:**
```bash
./deploy/hetzner/setup-vps.sh && \
./deploy/hetzner/install-docker.sh && \
./deploy/hetzner/deploy-services.sh && \
./deploy/hetzner/ssl-setup.sh && \
./deploy/hetzner/monitoring-setup.sh
```

---

## ⚡ **OPCIÓN C: Desarrollo Local Inmediato**

### **Solo 3 comandos:**

```bash
# 1. Clona y prepara
git clone https://github.com/tu-usuario/neural-forge.git
cd neural-forge

# 2. Setup automático de desarrollo
./scripts/dev-setup.sh

# 3. Inicia entorno completo
./start-dev.sh
```

**¡Listo! URLs disponibles:**
- 🎮 **Principal:** http://localhost:7860
- 📊 **Analytics:** http://localhost:8501
- 🧠 **ML API:** http://localhost:8000/docs
- 📈 **Grafana:** http://localhost:3000

---

## 🔧 **Quick Commands**

### **Verificación Rápida:**
```bash
./operations.sh status    # Estado general
./operations.sh health    # Check completo
./operations.sh logs      # Ver logs
```

### **URLs Post-Deployment:**
- **🌐 Producción:** `https://tu-dominio.com`
- **📊 Analytics:** `https://tu-dominio.com/analytics`  
- **📈 Monitoreo:** `https://tu-dominio.com/grafana`

### **Credenciales por Defecto:**
- **Grafana:** `admin` / `neuralforge2025`
- **SSH:** Usuario `neuralforge`

---

## 🆘 **Troubleshooting Express**

### **Problema: Servicios no inician**
```bash
# Verificar Docker
docker --version
sudo systemctl status docker

# Reiniciar servicios
./operations.sh restart
```

### **Problema: SSL no funciona**
```bash
# Verificar dominio apunta al servidor
nslookup tu-dominio.com

# Re-generar certificados
sudo ./deploy/hetzner/ssl-setup.sh
```

### **Problema: No hay conexión a DB**
```bash
# Verificar PostgreSQL
docker logs neural-forge-postgres

# Reiniciar DB
./scripts/service-manager.sh restart postgres
```

---

## 📊 **Verificación Final (1 minuto)**

```bash
# Test completo automático
curl -I https://tu-dominio.com                    # Principal
curl -I https://tu-dominio.com/api/health         # API
curl -I https://tu-dominio.com/analytics          # Analytics
curl -I https://tu-dominio.com/grafana            # Monitoreo
```

**✅ Si todos responden con `200 OK` = ¡ÉXITO TOTAL!**

---

## 🎯 **Comandos de Emergencia**

```bash
# Parar todo
./operations.sh stop

# Reiniciar todo
./operations.sh restart

# Logs de error
./operations.sh logs | grep -i error

# Backup de emergencia
./operations.sh backup emergency
```

---

## 🎉 **¡15 Minutos = Sistema Completo!**

**Tu Neural Forge está corriendo con:**
- ✅ **9 servicios containerizados**
- ✅ **SSL automático y seguro**
- ✅ **Monitoreo en tiempo real**
- ✅ **Backups configurados**
- ✅ **APIs documentadas**
- ✅ **Dashboards analíticos**

### **Siguiente Paso:**
Accede a `https://tu-dominio.com` y ¡comienza a generar videos virales! 🚀🎵