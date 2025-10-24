# 🚀 GUÍA DE LANZAMIENTO - Paso a Paso

## Para Community Manager: Lanza tu Primera Campaña Viral

---

## ✅ Pre-requisitos

Asegúrate de tener:

```bash
# 1. Clonar repositorio
git clone https://github.com/albertomaydayjhondoe/master.git
cd master

# 2. Verificar Python
python --version  # Python 3.12.1

# 3. Health check del sistema
./v3-manage.sh health
```

**Output esperado:**
```
✅ unified_system_v3.py
✅ community_manager_dashboard.py
✅ Python imports working
✅ Dummy mode working
```

---

## 📋 Escenario: Lanzamiento de "Nueva Vida" por Stakas

### Información del Video:
- **Artista:** Stakas
- **Canción:** Nueva Vida
- **Género:** Trap
- **Budget:** $50/día
- **Target:** US, MX, ES, AR, CL, CO

---

## 🎬 MÉTODO 1: CLI (Rápido)

### Paso 1: Launch Campaign

```bash
cd /workspaces/master

./v3-manage.sh launch-campaign \
  --artist "Stakas" \
  --song "Nueva Vida" \
  --video "/data/videos/nueva_vida_official.mp4" \
  --budget 50 \
  --countries "US,MX,ES,AR,CL,CO"
```

### Paso 2: Ver Output en Tiempo Real

```
🚀 LAUNCHING VIRAL CAMPAIGN: Stakas - Nueva Vida

📋 FASE 1: Preparando assets...
✅ Assets preparados

📱 FASE 2: Publicando en TODAS las plataformas...
✅ YouTube: https://youtube.com/watch?v=dummy_yt_1761325935
✅ TikTok: 10 cuentas
✅ Instagram: 5 cuentas
✅ Twitter: tweet_1761325935
✅ Facebook: fb_post_1761325935

💰 FASE 3: Lanzando Meta Ads campaign...
✅ Meta Ads: Campaign ID campaign_1761325935

🤖 FASE 4: Activando engagement automation...
✅ Engagement: 6 acciones programadas

📊 FASE 5: Configurando tracking...
✅ Tracking: Pixel instalado, eventos configurados

🎉 CAMPAIGN LAUNCHED SUCCESSFULLY!
📊 Summary:
   - Platforms: 5
   - Total accounts: 18
   - Meta Ads budget: $50.0/day
   - Estimated reach: 140,000 (Regional)
```

### Paso 3: Esperar 2 Horas

```bash
# Simular espera (en producción serían 2 horas reales)
sleep 2
```

### Paso 4: Ver Analytics

```bash
./v3-manage.sh analytics
```

**Output:**
```json
{
  "campaign_id": "viral_1761325935.954628",
  "elapsed_time": "2 hours",
  "platforms": {
    "youtube": {
      "views": 5400,
      "likes": 320,
      "comments": 45,
      "shares": 28
    },
    "tiktok": {
      "total_views": 127000,
      "avg_views_per_account": 12700,
      "total_likes": 8900,
      "total_comments": 450,
      "viral_probability": 0.72
    },
    "instagram": {
      "total_views": 34000,
      "avg_views_per_account": 6800,
      "total_likes": 3200,
      "total_comments": 180
    },
    "twitter": {
      "views": 8900,
      "retweets": 145,
      "likes": 560,
      "replies": 34
    }
  },
  "meta_ads": {
    "impressions": 45000,
    "clicks": 1350,
    "ctr": 3.0,
    "spend": 25.00,
    "landing_page_views": 980,
    "cost_per_view": 0.026
  },
  "totals": {
    "total_views": 220300,
    "total_engagement": 15334,
    "estimated_reach": 180000,
    "viral_score": 8.5
  },
  "recommendations": [
    "Aumentar presupuesto Meta Ads (+20%): ROAS actual 3.2x",
    "Boost engagement en TikTok cuenta #3 (85k views)",
    "Crear lookalike audience con mejores performers"
  ]
}
```

### Paso 5: Optimizar Campaign

```bash
./v3-manage.sh optimize
```

**Output:**
```
🎯 Optimizando campaña...

🔧 Increase Budget
   Platform: meta_ads
   Reason: High CTR (3.0%)
   Current: $50 → New: $60

🔧 Boost Engagement
   Platform: tiktok
   Target accounts: #1, #3, #5
   Additional likes: 500
   Reason: High viral probability (0.72)

Estimated Impact: +35% reach

✅ Optimization completed!
```

---

## 🎨 MÉTODO 2: Dashboard UI (Visual)

### Paso 1: Lanzar Dashboard

```bash
./v3-manage.sh dashboard
```

**Output:**
```
🎨 Starting Community Manager Dashboard...

Dashboard URL: http://localhost:8502
Press CTRL+C to stop

You can now view your Streamlit app in your browser.
Local URL: http://localhost:8502
Network URL: http://172.16.5.4:8502
```

### Paso 2: Abrir en Browser

Abre tu navegador en: **http://localhost:8502**

### Paso 3: Configurar en Sidebar

En el sidebar izquierdo:

1. **📹 Video**
   - Path: `/data/videos/nueva_vida_official.mp4`

2. **🎤 Artista**
   - Nombre: `Stakas`
   - Canción: `Nueva Vida`
   - Género: `Trap`

3. **💰 Meta Ads**
   - Budget: `$50` (slider)

4. **🌎 Targeting**
   - Países: `US, MX, ES, AR, CL, CO`

### Paso 4: Click BIG RED BUTTON

En la tab **🚀 Launch**:

1. Verifica el preview en el panel derecho
2. Click botón: **🚀 LANZAR CAMPAÑA**

### Paso 5: Ver Progress en Tiempo Real

El dashboard mostrará:

```
📋 Preparando assets...         [████████----------] 20%
📱 Publicando en plataformas... [████████████------] 40%
💰 Creando Meta Ads campaign... [████████████████--] 60%
🤖 Activando engagement...      [██████████████████] 80%
📊 Configurando tracking...     [████████████████████] 100%

✅ ¡Campaña lanzada exitosamente! 🎉
```

### Paso 6: Ver Resultados

Después del lanzamiento verás:

**Summary Metrics:**
```
Plataformas: 5
Cuentas Activas: 18
Meta Ads: $50/día
Alcance Est.: 140,000 (Regional)
```

**URLs Publicadas:**
- 🎥 YouTube: [link]
- 📱 TikTok (10 cuentas): [expandir]
- 📸 Instagram (5 cuentas): [expandir]
- 🐦 Twitter: [link]

### Paso 7: Tab Analytics

Cambia a la tab **📊 Analytics**:

1. Click botón: **🔄 Actualizar Analytics**

Verás métricas en cards:

```
┌────────────┬────────────┬────────────┬────────────┐
│ Total      │   Total    │ Estimated  │   Viral    │
│  Views     │ Engagement │   Reach    │   Score    │
│           │            │            │            │
│ 220,300    │  15,334   │  180,000   │  8.5/10    │
└────────────┴────────────┴────────────┴────────────┘
```

**Platform Breakdown:**

- **📱 TikTok**
  - Total Views: 127,000
  - Likes: 8,900
  - Viral Probability: 72%

- **📸 Instagram**
  - Total Views: 34,000
  - Likes: 3,200

- **🎥 YouTube**
  - Views: 5,400
  - Likes: 320

**Meta Ads Performance:**

```
Impressions: 45,000
Clicks: 1,350
CTR: 3.0%
Spend: $25.00
Landing Views: 980
Cost/View: $0.026
```

### Paso 8: Tab Optimize

Cambia a la tab **🎯 Optimize**:

1. Click botón: **🎯 Optimizar Campaña**

El sistema mostrará:

```
✅ 2 optimizaciones aplicadas

Impacto Estimado: +35% reach

Cambios Aplicados:
🔧 Increase Budget - meta_ads
   High CTR (3.0%)
   $50 → $60

🔧 Boost Engagement - tiktok
   High viral probability (0.72)
   +500 likes en cuentas #1, #3, #5
```

---

## 📊 Interpretar Resultados

### Métricas Clave:

1. **Viral Score: 8.5/10** ⭐
   - Excelente! Arriba de 7.0 es viral
   - Indica alto potencial de alcance orgánico

2. **CTR: 3.0%** 📈
   - Industria promedio: 0.9%
   - 3.0% es EXCELENTE para Meta Ads

3. **ROAS: 3.2x** 💰
   - Por cada $1 gastado → $3.20 retorno
   - Rentable! (target es 2.0x)

4. **Viral Probability (TikTok): 0.72** 🚀
   - 72% chance de volverse viral
   - Arriba de 0.6 es muy alto

### Qué Significa Cada Número:

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| Total Views | 220,300 | Alcance orgánico en 2h |
| TikTok Views | 127,000 | 57% del tráfico (principal plataforma) |
| Meta Ads Clicks | 1,350 | Tráfico pagado de calidad |
| Engagement | 15,334 | Likes + comments + shares |
| Reach | 180,000 | Personas únicas alcanzadas |

---

## 🎯 Decisiones Basadas en Data

### Escenario 1: CTR > 2.5% (Como nuestro 3.0%)

**Acción:** Aumentar budget Meta Ads

```bash
# El sistema ya lo sugiere automáticamente
./v3-manage.sh optimize

# O manualmente:
# Aumentar de $50 → $70/día
```

**Razón:** Alto CTR indica que el creative funciona bien. Más budget = más conversions al mismo costo.

### Escenario 2: Viral Probability > 0.7 (Como nuestro 0.72)

**Acción:** Boost engagement en posts top performers

```bash
# El sistema ya lo hace automáticamente
./v3-manage.sh optimize

# Resultado:
# +500 likes en cuentas TikTok #1, #3, #5
```

**Razón:** TikTok algorithm premia engagement temprano. Más likes = más distribución orgánica.

### Escenario 3: YouTube Views < 10k

**Acción:** Create ads campaign para YouTube video

```
1. Use YouTube URL de la campaña
2. Create Meta Ads campaign específico para YouTube traffic
3. Target: "Interested in music videos"
4. Budget: $20/día adicional
```

### Escenario 4: Instagram < 50k views

**Acción:** Cross-post a más cuentas GoLogin

```
1. Añadir 5 cuentas más GoLogin
2. Re-post con diferentes captions
3. Usar hashtags trending del momento
```

---

## 🔄 Workflow Continuo

### Día 1 (Lanzamiento):

```
09:00 - Lanzar campaña
11:00 - Primer check (2h)
14:00 - Optimizar si necesario
17:00 - Review EOD
20:00 - Boost nocturno si viral
```

### Día 2-3 (Momentum):

```
- Monitor cada 4 horas
- Optimize 2x por día
- Responder comments top posts
- Adjust Meta Ads budget based on performance
```

### Día 4-7 (Scale):

```
- Identify top performers
- Create lookalike audiences
- Scale budget 2x en ads ganadores
- Retarget engaged users
```

---

## 🚨 Troubleshooting

### Problema 1: "Port 8502 already in use"

**Solución:**
```bash
# Usar otro puerto
./v3-manage.sh dashboard --port 8503

# O matar proceso en 8502
lsof -ti:8502 | xargs kill -9
```

### Problema 2: "No active campaign"

**Causa:** No has lanzado campaña aún

**Solución:**
```bash
# Lanzar campaña primero
./v3-manage.sh launch-campaign --artist "A" --song "S" --video "/path"

# Luego puedes ver analytics
./v3-manage.sh analytics
```

### Problema 3: "Video file not found"

**Causa:** Path incorrecto del video

**Solución:**
```bash
# Verificar que existe
ls -la /data/videos/nueva_vida_official.mp4

# Usar path absoluto
./v3-manage.sh launch-campaign \
  --video "/workspaces/master/data/videos/song.mp4"
```

### Problema 4: Imports failing

**Causa:** Dependencias faltantes

**Solución:**
```bash
# Health check
./v3-manage.sh health

# Si faltan packages
pip install streamlit asyncio fastapi httpx
```

---

## 📈 Métricas de Éxito

### Para considerar campaña EXITOSA:

✅ **Total Views > 100k** en primeras 24h  
✅ **Viral Score > 7.0**  
✅ **CTR Meta Ads > 2.0%**  
✅ **ROAS > 2.0x**  
✅ **Engagement Rate > 5%**  

### Para considerar campaña VIRAL:

🚀 **Total Views > 500k** en 48h  
🚀 **Viral Score > 8.5**  
🚀 **CTR Meta Ads > 3.5%**  
🚀 **ROAS > 4.0x**  
🚀 **Trending en al menos 1 plataforma**  

---

## 🎉 Checklist Post-Lanzamiento

Después de lanzar campaña:

- [ ] Screenshot de URLs publicadas
- [ ] Export analytics JSON
- [ ] Notificar al artista con resultados
- [ ] Crear report para label/cliente
- [ ] Schedule optimization checks
- [ ] Monitor shadowban signals
- [ ] Backup campaign data
- [ ] Update calendario editorial

---

## 📞 Next Steps

### Si todo funciona bien:

1. **Scale Budget**
   ```bash
   # Aumentar de $50 → $100/día
   # Editar en dashboard o CLI
   ```

2. **Add More Accounts**
   ```
   - Device Farm: 10 → 20 devices
   - GoLogin: 5 → 10 profiles
   ```

3. **Launch Similar Songs**
   ```bash
   # Usar mismo workflow para resto del album
   for song in song2 song3 song4; do
     ./v3-manage.sh launch-campaign --song "$song" ...
   done
   ```

### Si algo falla:

1. **Check Logs**
   ```bash
   # Ver errores
   tail -f /tmp/unified_system_v3.log
   ```

2. **Health Check**
   ```bash
   ./v3-manage.sh health
   ```

3. **Ask for Support**
   - GitHub Issues
   - Documentation: `UNIFIED_V3_GUIDE.md`
   - Slack: #community-manager-v3

---

**¡Éxito con tu lanzamiento viral! 🚀🎵**

---

**Documento creado:** 24 Oct 2025  
**Sistema:** Unified v3.0  
**Status:** ✅ Testeado y funcional
