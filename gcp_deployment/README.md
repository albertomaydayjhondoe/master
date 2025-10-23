# Meta Ads Google Cloud Platform Deployment

Este directorio contiene toda la configuración e infraestructura necesaria para desplegar el sistema Meta Ads en Google Cloud Platform.

## 🏗️ Arquitectura

El sistema utiliza los siguientes servicios de GCP:

- **Cloud Run**: API principal con auto-escalado
- **Cloud SQL**: Base de datos PostgreSQL privada
- **Cloud Storage**: Almacenamiento de modelos ML y datos
- **Pub/Sub**: Cola de mensajes para eventos
- **Secret Manager**: Gestión segura de credenciales
- **Cloud Scheduler**: Tareas programadas de ML
- **Cloud Monitoring**: Métricas, alertas y dashboards
- **Cloud Build**: CI/CD automatizado

## 📁 Estructura de Archivos

```
gcp_deployment/
├── main.tf                 # Configuración principal de Terraform
├── Dockerfile             # Imagen Docker para Cloud Run
├── cloudbuild.yaml        # Pipeline de CI/CD
├── .env.template          # Template de variables de entorno
├── setup_gcp.sh          # Script de configuración inicial
├── deploy.sh             # Script de deployment
├── setup_monitoring.sh   # Script de monitoreo
└── README.md             # Esta documentación
```

## 🚀 Deployment Rápido

### 1. Prerequisitos

Instala las herramientas requeridas:

```bash
# Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 2. Configuración del Proyecto

```bash
# Crear proyecto en GCP (opcional)
gcloud projects create tu-proyecto-meta-ads
gcloud config set project tu-proyecto-meta-ads

# Habilitar facturación (requerido)
# Ve a: https://console.cloud.google.com/billing
```

### 3. Deployment Automático

```bash
# Clonar repositorio
git clone <tu-repo>
cd master/gcp_deployment

# Configurar infraestructura
./setup_gcp.sh tu-proyecto-meta-ads us-central1

# Desplegar aplicación
./deploy.sh

# Configurar monitoreo
./setup_monitoring.sh tu-proyecto-meta-ads us-central1 tu-email@ejemplo.com
```

## 🔧 Configuración Manual

### 1. Variables de Entorno

Copia y edita el archivo de configuración:

```bash
cp .env.template .env
nano .env
```

Variables críticas que debes configurar:

```bash
# Meta API
META_APP_ID=tu-app-id
META_APP_SECRET=tu-app-secret
META_ACCESS_TOKEN=tu-access-token
META_AD_ACCOUNT_ID=act_tu-account-id

# GCP
GCP_PROJECT_ID=tu-proyecto
GCP_REGION=us-central1
```

### 2. Secretos en Secret Manager

Crea un archivo JSON con tus credenciales de Meta:

```bash
cat > meta-secrets.json << EOF
{
  "app_id": "tu-app-id",
  "app_secret": "tu-app-secret", 
  "access_token": "tu-long-lived-token",
  "ad_account_id": "act_tu-account-id",
  "business_id": "tu-business-id",
  "pixel_id": "tu-pixel-id"
}
EOF

# Subir a Secret Manager
gcloud secrets versions add meta-api-secrets --data-file=meta-secrets.json
rm meta-secrets.json
```

### 3. Deploy Paso a Paso

```bash
# 1. Inicializar Terraform
terraform init

# 2. Crear plan de infraestructura
terraform plan -var="project_id=tu-proyecto"

# 3. Aplicar infraestructura
terraform apply -var="project_id=tu-proyecto"

# 4. Construir y desplegar aplicación
./deploy.sh tu-proyecto

# 5. Configurar monitoreo
./setup_monitoring.sh tu-proyecto
```

## 📊 Monitoreo y Alertas

El sistema incluye monitoreo completo:

### Métricas Automáticas
- CPU y memoria de Cloud Run
- Latencia de requests
- Rate de errores  
- Conexiones de base de datos
- Uptime del servicio

### Alertas Configuradas
- CPU > 80%
- Memoria > 85%
- Error rate > 5%
- Fallos de conexión DB
- Servicio no disponible

### Dashboards
- Dashboard principal del sistema
- Métricas de ML en tiempo real
- Performance de campañas
- Logs estructurados

Accede al monitoreo en:
- [Cloud Console](https://console.cloud.google.com/monitoring)
- [Dashboards](https://console.cloud.google.com/monitoring/dashboards)
- [Alerting](https://console.cloud.google.com/monitoring/alerting)

## 🔐 Seguridad

### Red Privada
- VPC dedicada con subred privada
- Cloud SQL sin IP pública
- Comunicación interna segura

### Autenticación
- Service Account con permisos mínimos
- IAM roles específicos por servicio
- Secret Manager para credenciales

### SSL/TLS
- HTTPS obligatorio en Cloud Run
- Certificados gestionados automáticamente
- Conexiones DB encriptadas

## 💰 Costos Estimados

Costos mensuales aproximados (tráfico medio):

| Servicio | Estimado/mes |
|----------|--------------|
| Cloud Run | $10-30 |
| Cloud SQL | $15-25 |
| Cloud Storage | $5-10 |
| Monitoring | $5-15 |
| **Total** | **$35-80** |

### Optimización de Costos

```bash
# Configurar auto-shutdown para desarrollo
gcloud run services update meta-ads-api \
  --min-instances=0 \
  --region=us-central1

# Usar instancia más pequeña para testing
# Ver main.tf y cambiar: tier = "db-f1-micro"
```

## 🧪 Testing

### Tests Locales

```bash
# Tests unitarios
python -m pytest tests/unit/

# Tests de integración
python -m pytest tests/integration/

# Tests con Docker
docker build -f gcp_deployment/Dockerfile .
docker run -e DUMMY_MODE=true <image-id> python -m pytest
```

### Tests en GCP

```bash
# Health check
curl https://tu-servicio.run.app/health

# API docs
curl https://tu-servicio.run.app/docs

# Test de campaña (modo dummy)
curl -X POST https://tu-servicio.run.app/campaigns/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Campaign", "budget": 100}'
```

## 🔄 CI/CD

### Cloud Build Automático

El sistema incluye pipeline automático:

1. **Trigger**: Push a rama `main`
2. **Build**: Docker image
3. **Test**: Suite completa
4. **Deploy**: Cloud Run
5. **Verify**: Health checks

### Configurar Trigger

```bash
# Conectar repositorio
gcloud source repos create meta-ads-repo
git remote add google https://source.developers.google.com/p/tu-proyecto/r/meta-ads-repo

# Crear trigger
gcloud builds triggers create github \
  --repo-name=tu-repo \
  --repo-owner=tu-usuario \
  --branch-pattern="^main$" \
  --build-config=gcp_deployment/cloudbuild.yaml
```

## 🚨 Troubleshooting

### Problemas Comunes

**Error: "API not enabled"**
```bash
gcloud services enable run.googleapis.com
```

**Error: "Insufficient permissions"**
```bash
gcloud projects add-iam-policy-binding tu-proyecto \
  --member="user:tu-email@gmail.com" \
  --role="roles/editor"
```

**Error: "Cloud SQL connection failed"**
```bash
# Verificar conexión privada
gcloud sql instances describe meta-ads-db-prod
```

**Error: "Container not starting"**
```bash
# Ver logs
gcloud logs tail meta-ads-api --region=us-central1

# Debug container
docker run -it --entrypoint=/bin/bash <image-id>
```

### Logs y Debugging

```bash
# Logs de Cloud Run
gcloud logs tail meta-ads-api --region=us-central1

# Logs estructurados
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=meta-ads-api" --limit=50

# Métricas en tiempo real
gcloud monitoring metrics list --filter="metric.type:run.googleapis.com"
```

## 📚 Referencias

- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Meta Business API](https://developers.facebook.com/docs/marketing-apis)
- [Cloud Monitoring](https://cloud.google.com/monitoring/docs)

## 🆘 Soporte

Para problemas específicos:

1. **Check Status**: [GCP Status](https://status.cloud.google.com/)
2. **Logs**: Cloud Logging en Console
3. **Metrics**: Cloud Monitoring dashboards
4. **Issues**: GitHub Issues del proyecto

---

**¡Meta Ads está listo para ejecutarse en Google Cloud Platform! 🚀**