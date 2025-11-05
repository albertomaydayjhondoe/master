# 🚀 Neural Forge - Hetzner Deployment Guide
## Guía Paso a Paso para Deployment en Producción

---

### 📋 **Tabla de Contenidos**

1. [Preparativos Iniciales](#preparativos-iniciales)
2. [Configuración del VPS](#configuración-del-vps)
3. [Deployment de Servicios](#deployment-de-servicios)
4. [Configuración SSL](#configuración-ssl)
5. [Monitoreo y Alertas](#monitoreo-y-alertas)
6. [Verificación Final](#verificación-final)
7. [Mantenimiento](#mantenimiento)

---

## 🎯 **Preparativos Iniciales**

### **Paso 1: Requisitos del Sistema**

**VPS Recomendado:** Hetzner CX33 (€5.49/mes)
- **CPU:** 2 vCPU AMD
- **RAM:** 8 GB
- **Almacenamiento:** 80 GB SSD
- **Transferencia:** 20 TB
- **Conexión:** 1 Gbit/s

```bash
# 📝 Información necesaria antes de comenzar:
DOMAIN="tu-dominio.com"           # Tu dominio
SERVER_IP="xxx.xxx.xxx.xxx"      # IP del servidor
SSH_KEY_PATH="~/.ssh/id_rsa"     # Ruta a tu clave SSH
```

### **Paso 2: Preparación Local**

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/neural-forge.git
cd neural-forge

# 2. Configura las variables de producción
cp .env.production.template .env.production

# 3. Edita las variables críticas en .env.production
nano .env.production
```

**Variables críticas a configurar:**
```bash
# Dominio y SSL
DOMAIN=tu-dominio.com
SSL_EMAIL=tu-email@dominio.com

# Base de datos segura
POSTGRES_PASSWORD=contraseña-ultra-segura-2025
POSTGRES_DB=neural_forge_prod

# Claves de seguridad
SECRET_KEY=clave-secreta-super-segura-de-64-caracteres-mínimo
JWT_SECRET=jwt-secret-igual-de-segura-y-diferente-a-la-anterior

# APIs externas
OPENAI_API_KEY=sk-real-openai-key-here
META_ACCESS_TOKEN=real-meta-token-here
GOLOGIN_API_TOKEN=real-gologin-token-here

# Monitoreo
GRAFANA_ADMIN_PASSWORD=password-grafana-super-segura
```

---

## 🏗️ **Configuración del VPS**

### **Paso 3: Creación del Servidor**

1. **Accede a Hetzner Cloud Console**
2. **Crea nuevo servidor:**
   - **Imagen:** Ubuntu 22.04 LTS
   - **Tipo:** CX33 (2 vCPU, 8GB RAM)
   - **Ubicación:** Nuremberg (recomendado para Europa)
   - **SSH Key:** Añade tu clave pública
   - **Nombre:** neural-forge-prod

### **Paso 4: Configuración Inicial del VPS**

```bash
# 1. Conecta al servidor
ssh root@tu-servidor-ip

# 2. Actualiza el sistema
apt update && apt upgrade -y

# 3. Descarga el proyecto
git clone https://github.com/tu-usuario/neural-forge.git
cd neural-forge

# 4. Ejecuta la configuración automática del VPS
chmod +x deploy/hetzner/setup-vps.sh
./deploy/hetzner/setup-vps.sh
```

**¿Qué hace el setup automático?**
- ✅ Crea usuario no-root (`neuralforge`)
- ✅ Configura SSH seguro (deshabilita root login)
- ✅ Instala y configura firewall (UFW)
- ✅ Optimiza configuraciones del sistema
- ✅ Configura swap y parámetros de memoria
- ✅ Instala dependencias básicas

### **Paso 5: Instalación de Docker**

```bash
# Cambia al usuario no-root
su - neuralforge
cd neural-forge

# Instala Docker de forma automática
chmod +x deploy/hetzner/install-docker.sh
./deploy/hetzner/install-docker.sh
```

**¿Qué incluye la instalación?**
- ✅ Docker Engine más reciente
- ✅ Docker Compose V2
- ✅ Configuración de usuario en grupo docker
- ✅ Optimizaciones de rendimiento
- ✅ Configuración de límites de recursos

---

## 🚀 **Deployment de Servicios**

### **Paso 6: Configuración de Variables**

```bash
# 1. Copia las variables de producción
cp .env.production.template .env.production

# 2. Edita con tus valores reales
nano .env.production

# 3. Ajusta permisos de seguridad
chmod 600 .env.production
```

### **Paso 7: Deployment Automático**

```bash
# Ejecuta el deployment completo
chmod +x deploy/hetzner/deploy-services.sh
./deploy/hetzner/deploy-services.sh
```

**Proceso de deployment:**

1. **🔧 Preparación del entorno**
   ```
   ✅ Verificación de requisitos
   ✅ Creación de directorios
   ✅ Configuración de permisos
   ```

2. **🐳 Construcción de imágenes**
   ```
   ✅ Build de ML Core
   ✅ Build de Production Controller
   ✅ Build de Analytics Engine
   ✅ Build de Meta Automation
   ```

3. **🚀 Lanzamiento de servicios**
   ```
   ✅ PostgreSQL Database
   ✅ Redis Cache
   ✅ ML Core API
   ✅ Production Controller
   ✅ Analytics Engine
   ✅ N8N Workflows
   ✅ Prometheus Monitoring
   ✅ Grafana Dashboard
   ```

4. **🔍 Verificación de salud**
   ```
   ✅ Health checks de todos los servicios
   ✅ Conectividad de base de datos
   ✅ Disponibilidad de APIs
   ```

---

## 🔒 **Configuración SSL**

### **Paso 8: Instalación de Certificados SSL**

```bash
# Configura SSL con Let's Encrypt
chmod +x deploy/hetzner/ssl-setup.sh
sudo ./deploy/hetzner/ssl-setup.sh
```

**Proceso SSL automático:**

1. **📋 Preparación**
   ```
   ✅ Instalación de Certbot
   ✅ Configuración de Nginx
   ✅ Verificación de dominio
   ```

2. **🔐 Generación de certificados**
   ```
   ✅ Certificado SSL para dominio principal
   ✅ Certificado para subdominios (si aplica)
   ✅ Configuración de renovación automática
   ```

3. **🌐 Configuración de proxy reverso**
   ```
   ✅ HTTPS redirection
   ✅ Security headers
   ✅ Rate limiting
   ✅ Compression gzip
   ```

**URLs disponibles después del SSL:**
- 🎮 **Principal:** `https://tu-dominio.com`
- 📊 **Analytics:** `https://tu-dominio.com/analytics`
- 📈 **Grafana:** `https://tu-dominio.com/grafana`
- 🔧 **API Docs:** `https://tu-dominio.com/api/docs`

---

## 📊 **Monitoreo y Alertas**

### **Paso 9: Configuración de Monitoreo**

```bash
# Instala el stack de monitoreo completo
chmod +x deploy/hetzner/monitoring-setup.sh
./deploy/hetzner/monitoring-setup.sh
```

**Stack de monitoreo incluye:**

1. **📈 Prometheus (Métricas)**
   - Recolección de métricas del sistema
   - Métricas de Docker y contenedores
   - Métricas de aplicación personalizadas
   - Retention: 15 días

2. **📊 Grafana (Visualización)**
   - Dashboard de sistema general
   - Dashboard de rendimiento ML
   - Dashboard de métricas de campaña
   - Alertas automáticas

3. **🚨 Configuración de alertas**
   - CPU > 80% por 5 minutos
   - RAM > 85% por 3 minutos
   - Disco > 90%
   - Servicios caídos
   - Errores en APIs

### **Dashboards disponibles:**

1. **🖥️ System Overview**
   ```
   • CPU, Memory, Disk usage
   • Network I/O
   • Load average
   • Container status
   ```

2. **🧠 ML Performance**
   ```
   • Model inference time
   • API response times
   • Processing queue status
   • Error rates
   ```

3. **📱 Campaign Metrics**
   ```
   • Video generation rate
   • Distribution success
   • Engagement metrics
   • Revenue tracking
   ```

---

## ✅ **Verificación Final**

### **Paso 10: Tests de Sistema**

```bash
# 1. Verifica el estado de todos los servicios
./operations.sh status

# 2. Ejecuta health check completo
./operations.sh health

# 3. Prueba las URLs principales
curl -I https://tu-dominio.com
curl -I https://tu-dominio.com/api/health
curl -I https://tu-dominio.com/analytics
```

### **Checklist de verificación:**

- [ ] **🌐 URLs principales responden con HTTPS**
- [ ] **🔐 Certificados SSL válidos y auto-renovables**
- [ ] **🐳 Todos los contenedores en estado "running"**
- [ ] **📊 Grafana accesible con dashboards**
- [ ] **🧠 ML Core API respondiendo correctamente**
- [ ] **📈 Métricas apareciendo en Prometheus**
- [ ] **🔄 N8N workflows activos**
- [ ] **💾 Base de datos accesible y respaldada**

### **Paso 11: Configuración de Backups**

```bash
# Configura backup automático diario
crontab -e

# Añade esta línea para backup diario a las 2 AM
0 2 * * * cd /home/neuralforge/neural-forge && ./operations.sh backup daily
```

---

## 🔧 **Mantenimiento**

### **Comandos de Operación Diaria**

```bash
# Ver estado del sistema
./operations.sh status

# Logs en tiempo real
./operations.sh logs

# Métricas rápidas
./operations.sh metrics

# Actualizar sistema
./operations.sh update

# Backup manual
./operations.sh backup manual
```

### **Operaciones de Servicios**

```bash
# Reiniciar servicio específico
./scripts/service-manager.sh restart ml-core

# Ver logs de servicio específico
./scripts/service-manager.sh logs production-controller

# Escalar servicio
./scripts/service-manager.sh scale analytics 3

# Acceder a shell de contenedor
./scripts/service-manager.sh shell postgres
```

### **Monitoreo Continuo**

1. **📊 Acceso a Grafana:**
   - URL: `https://tu-dominio.com/grafana`
   - Usuario: `admin`
   - Password: `tu-password-configurado`

2. **🔍 Alertas importantes:**
   - **CPU alto:** Considera escalar el VPS
   - **Memoria baja:** Optimiza contenedores o aumenta RAM
   - **Disco lleno:** Limpia logs y backups antiguos
   - **API errors:** Check logs de servicios específicos

### **Actualizaciones y Seguridad**

```bash
# Actualizaciones de seguridad del SO
sudo apt update && sudo apt upgrade -y

# Actualización de contenedores
./operations.sh update

# Renovación manual de SSL (si es necesario)
sudo certbot renew

# Scan de seguridad
./operations.sh security-scan
```

---

## 🎉 **¡Deployment Completado!**

### **URLs de Acceso Final:**

- 🎮 **Interfaz Principal:** `https://tu-dominio.com`
- 📊 **Panel Analytics:** `https://tu-dominio.com/analytics`
- 📈 **Monitoreo Grafana:** `https://tu-dominio.com/grafana`
- 🔧 **API Documentation:** `https://tu-dominio.com/api/docs`
- 🔄 **N8N Workflows:** `https://tu-dominio.com/n8n` (si habilitado)

### **Información de Acceso:**

- **Sistema:** Usuario `neuralforge` con acceso SSH
- **Grafana:** `admin` / tu-password-configurado
- **PostgreSQL:** Acceso interno via docker network
- **APIs:** Autenticación via JWT tokens

### **Soporte y Troubleshooting:**

```bash
# Guía rápida de comandos más útiles:
./operations.sh help              # Ver todos los comandos
./operations.sh health            # Check completo del sistema
./operations.sh logs [servicio]   # Ver logs
./operations.sh dashboard         # Abrir dashboard principal
./operations.sh monitoring        # Abrir Grafana
```

---

## 🔗 **Recursos Adicionales**

- **📖 Documentación completa:** `docs/`
- **🔧 Scripts de operación:** `scripts/`
- **📊 Configuraciones:** `config/`
- **🚨 Logs del sistema:** `logs/`
- **💾 Backups:** `backups/`

**¡Tu sistema Neural Forge está ahora corriendo en producción con monitoreo completo, seguridad SSL y backups automáticos!** 🚀