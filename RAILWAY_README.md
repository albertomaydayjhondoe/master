# 🚀 Stakas MVP - Railway Deployment

## 🎯 Canal Target: UCgohgqLVu1QPdfa64Vkrgeg

Dashboard interactivo de análisis de viralidad para el canal **Stakas MVP** especializado en **Drill/Rap Español**.

### 📊 Features del Dashboard

- **🎵 Análisis de Viralidad**: Predicciones ML para contenido drill español
- **💰 Optimización Meta Ads**: Estrategia €500/mes ES+LATAM
- **📈 Proyecciones Crecimiento**: 0→10K subscribers en 12 meses
- **🎬 Calendario Contenido**: Planning viral automatizado
- **🏆 Análisis Competitivo**: Benchmarks sector drill español

### 🚀 Deploy a Railway

#### Método 1: GitHub Actions (Recomendado)

1. **Setup Secrets en GitHub**:
   ```
   RAILWAY_TOKEN=your_railway_token
   RAILWAY_PROJECT_ID=your_project_id
   DISCORD_WEBHOOK_URL=your_discord_webhook
   ```

2. **Push a main branch**:
   ```bash
   git add .
   git commit -m "🚀 Deploy viral dashboard"
   git push origin main
   ```

3. **Auto-deploy**: GitHub Actions se ejecuta automáticamente

#### Método 2: Manual Railway CLI

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login

# Create/link project  
railway init stakas-mvp-viral

# Set environment variables
railway variables set APP_ENV=production
railway variables set CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg
railway variables set STREAMLIT_SERVER_HEADLESS=true

# Deploy
railway up
```

### 🔧 Environment Variables

```env
# Core App
APP_ENV=production
CHANNEL_ID=UCgohgqLVu1QPdfa64Vkrgeg
CHANNEL_NAME=Stakas MVP
GENRE=drill_rap_espanol
TARGET_SUBSCRIBERS=10000
META_ADS_BUDGET=500

# Streamlit Config
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### 📱 Dashboard Sections

1. **📈 Growth Projections**: Comparativa orgánico vs Meta Ads vs ML optimizado
2. **💰 Meta Ads Strategy**: Distribución €500 España/LATAM/Lookalike  
3. **🎬 Viral Content Analysis**: Tipos de contenido con mayor potencial
4. **📅 Content Calendar**: Planning próximos 7 días optimizado
5. **🎯 Recommendations**: Acciones inmediatas y goals mensuales

### 🎵 Especialización Drill Español

- **Keywords Viral**: drill español, barrio life, trap madrid, freestyle real
- **Horarios Peak**: 19:00-22:00 weekdays, 15:00-21:30 weekends
- **Targeting**: España + LATAM 16-28 años + intereses Hip Hop/Urban
- **Collaborations**: 96% viral score (máximo impacto)

### 📊 KPIs Objetivo

- **Subscriber Growth**: >8% mensual
- **Video Views**: >15K promedio por video
- **Engagement Rate**: >6%
- **Meta Ads ROAS**: >3:1
- **Cost per Subscriber**: <€1.50

---

**🎯 Objetivo Final**: Crecimiento de 0 a 10.000 subscribers en 12 meses con €500/mes Meta Ads optimizados por ML para contenido drill/rap español auténtico.**
