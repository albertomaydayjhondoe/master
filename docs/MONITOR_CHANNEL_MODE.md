# 🔄 MODO MONITOR-CHANNEL

## Descripción

Monitorea un canal de YouTube 24/7 y **automáticamente viraliza** videos nuevos que tengan alto potencial viral detectado por ML.

---

## 🎯 **CONTROL DE CARGA INTELIGENTE**

### **Protecciones Implementadas:**

1. **Límite Diario de Campañas** (`max_campaigns_per_day`)
   - Default: **2 campañas/día**
   - Evita sobrecarga de UTM (Meta Ads, Device Farm, GoLogin)
   - Se reinicia cada 24 horas (00:00 UTC)

2. **Threshold de Virality** (`virality_threshold`)
   - Default: **0.70** (70% score ML)
   - Solo lanza campañas para videos con alto potencial
   - Evita gastar budget en contenido de bajo rendimiento

3. **Intervalo de Revisión** (`check_interval_hours`)
   - Default: **6 horas** entre checks
   - Reduce llamadas a YouTube API
   - Evita rate limits

4. **Priorización Inteligente**
   - Si hay múltiples videos nuevos, prioriza por **virality score**
   - Lanza campañas para los mejores N videos (hasta el límite diario)

5. **Delay Entre Campañas**
   - **5 minutos** de espera entre cada launch
   - Evita rate limits en Meta Ads API
   - Permite que servicios se estabilicen

---

## 📊 **FLUJO COMPLETO**

```
┌─────────────────────────────────────────────┐
│  1. VERIFICAR LÍMITES DIARIOS               │
│     - ¿Alcanzado max_campaigns_per_day?     │
│     - Si SÍ: Wait until next day            │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  2. DETECTAR VIDEOS NUEVOS                  │
│     - YouTube Data API v3                   │
│     - Últimas N horas (2x check_interval)   │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  3. ANÁLISIS ML (YOLOv8)                    │
│     - Predict virality score (0.0-1.0)      │
│     - Para cada video encontrado            │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  4. PRIORIZAR Y FILTRAR                     │
│     - Filter: score >= threshold            │
│     - Sort: highest score first             │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  5. LANZAR CAMPAÑAS (CON LÍMITE)            │
│     - Toma top N (remaining slots)          │
│     - Launch full viral campaign            │
│     - Delay 5min entre cada una             │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  6. ESPERAR PRÓXIMA REVISIÓN                │
│     - Sleep check_interval_hours            │
│     - Repeat desde paso 1                   │
└─────────────────────────────────────────────┘
```

---

## 🚀 **USO**

### **Opción 1: CLI**

```bash
python unified_system_v3.py \
  --mode monitor-channel \
  --youtube-channel "UC_ABC123XYZ" \
  --auto-launch \
  --virality-threshold 0.70 \
  --max-campaigns-per-day 2 \
  --paid-budget 50.0 \
  --check-interval 6
```

### **Opción 2: Desde Dashboard (UI)**

1. Abre: http://localhost:8501
2. Tab: **"Monitorear Canal"**
3. Pega URL del canal: `https://www.youtube.com/@artist_channel`
4. Configura:
   - **Auto-launch**: ON/OFF
   - **Virality threshold**: 0.70
   - **Max campañas/día**: 2
   - **Budget por video**: $50
5. Click: **"Iniciar Monitoreo 24/7"**

---

## ⚙️ **PARÁMETROS**

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `youtube_channel_id` | str | - | ID del canal (UC_xxx) **[REQUERIDO]** |
| `auto_launch` | bool | `True` | Si False, solo notifica (no lanza) |
| `virality_threshold` | float | `0.70` | Score ML mínimo para auto-launch |
| `max_campaigns_per_day` | int | `2` | Máximo campañas diarias (protección UTM) |
| `daily_ad_budget_per_video` | float | `50.0` | Budget Meta Ads por video ($) |
| `target_countries` | list | `["US", "MX", ...]` | Países objetivo |
| `check_interval_hours` | int | `6` | Intervalo revisión (horas) |

---

## 📈 **EJEMPLO: ESCENARIO REAL**

### **Setup:**
- Canal: `UC_ArtistChannel`
- Auto-launch: `ON`
- Threshold: `0.70`
- Max campañas/día: `2`
- Budget: `$50/video`
- Intervalo: `6h`

### **Timeline:**

**08:00** - Primer check
- Video 1: "Nuevo Single" - Score: **0.85** ✅
- Video 2: "Behind Scenes" - Score: **0.55** ❌
- Video 3: "Live Performance" - Score: **0.78** ✅

**Acción:**
- ✅ Launch campaña Video 1 (0.85)
- ⏳ Wait 5min
- ✅ Launch campaña Video 3 (0.78)
- ✅ Límite alcanzado (2/2)
- ⏸️ Video 2 ignorado (bajo score)

**14:00** - Segundo check
- No videos nuevos
- Wait hasta 20:00

**20:00** - Tercer check
- Video 4: "Official Remix" - Score: **0.92** ✅

**Acción:**
- ⚠️ Límite diario alcanzado (2/2)
- 📧 Notificación: Video 4 detectado pero limit reached
- ⏸️ Se lanzará mañana en primer check

**00:00** - Reinicio contador diario
- Campañas lanzadas hoy: `0/2`
- Video 4 pendiente de lanzar

**02:00** - Cuarto check
- ✅ Launch campaña Video 4 (0.92)
- ✅ Nuevo contador: 1/2

---

## 🛡️ **PROTECCIONES UTM**

### **Meta Ads API**
- Delay 5min entre campañas
- Rate limit: 200 req/hora (sobra con 2 campañas)
- Budget diario total: max_campaigns * budget_per_video
- Ejemplo: 2 × $50 = **$100/día max**

### **Device Farm (TikTok/IG)**
- 10 cuentas TikTok × 2 campañas = **20 posts/día**
- 5 cuentas Instagram × 2 campañas = **10 posts/día**
- Rate limit TikTok: ~50 posts/día/cuenta ✅
- Rate limit IG: ~25 posts/día/cuenta ✅

### **GoLogin (Browsers)**
- 30 perfiles disponibles
- 2 campañas × 5 cuentas IG = **10 sesiones simultáneas**
- Uso: 33% capacidad ✅

### **YouTube API**
- Quota: 10,000 units/día
- 1 check = ~100 units (search)
- 4 checks/día × 100 = **400 units** (4% quota) ✅

---

## 🎛️ **AJUSTES RECOMENDADOS**

### **Canal Pequeño** (<10K subs)
```bash
--max-campaigns-per-day 1      # Más conservador
--virality-threshold 0.75      # Solo mejor contenido
--paid-budget 30.0             # Budget reducido
--check-interval 12            # Menos checks
```

### **Canal Mediano** (10K-100K subs)
```bash
--max-campaigns-per-day 2      # Default (recomendado)
--virality-threshold 0.70      # Threshold estándar
--paid-budget 50.0             # Budget moderado
--check-interval 6             # Check regular
```

### **Canal Grande** (>100K subs)
```bash
--max-campaigns-per-day 3      # Más agresivo
--virality-threshold 0.65      # Threshold flexible
--paid-budget 100.0            # Budget alto
--check-interval 4             # Checks frecuentes
```

---

## 📊 **ANALYTICS & MONITORING**

### **Métricas Trackeadas:**

1. **Videos analizados** (total)
2. **Videos con potencial viral** (score >= threshold)
3. **Campañas lanzadas** (total)
4. **Campañas lanzadas hoy** (counter diario)
5. **Virality score promedio** (de videos analizados)
6. **Budget gastado** (total diario)
7. **Rate limit status** (YouTube API, Meta Ads)

### **Logs Importantes:**

```log
INFO - 🔄 STARTING CHANNEL MONITOR: UC_ABC123
INFO -    - Auto-launch: True
INFO -    - Virality threshold: 0.70
INFO -    - Max campaigns/day: 2
INFO -    - Check interval: 6h

INFO - 📹 Buscando videos nuevos en el canal...
INFO -    Encontrados: 3 videos nuevos

INFO - 🧠 Analizando potencial viral con ML...
INFO -    Analizando: Nuevo Single 2025
INFO -       Score: 0.85 ✅
INFO -    Analizando: Behind The Scenes
INFO -       Score: 0.55 ❌
INFO -    Analizando: Live Performance
INFO -       Score: 0.78 ✅

INFO -    Videos con potencial viral: 2/3

INFO - 🚀 Lanzando 2 campañas (quedan 2 slots)

INFO - CAMPAÑA 1/2: Nuevo Single 2025
INFO - Virality Score: 0.85
INFO - ✅ Campaña lanzada: viral_1729785600

INFO - ⏳ Esperando 5 minutos antes de siguiente campaña...

INFO - CAMPAÑA 2/2: Live Performance
INFO - Virality Score: 0.78
INFO - ✅ Campaña lanzada: viral_1729785900

INFO - RESUMEN DEL CICLO:
INFO -    Videos analizados: 3
INFO -    Con potencial viral: 2
INFO -    Campañas lanzadas: 2
INFO -    Campañas hoy: 2/2
INFO -    Próxima revisión: 6 horas
```

---

## ⚠️ **LIMITACIONES Y CONSIDERACIONES**

### **1. YouTube Quota**
- Cuota diaria: 10,000 units
- Si se agota: espera hasta 00:00 PT (Pacific Time)
- Solución: Reduce `check_interval` o usa OAuth refresh

### **2. Meta Ads Budget**
- Budget real gastado: puede exceder `daily_ad_budget_per_video`
- Meta optimiza spend automáticamente
- Monitorear: Grafana dashboard

### **3. Shadowban Risk**
- 2 campañas/día es seguro
- >3 campañas/día: aumenta risk
- ML detecta shadowban en cada check

### **4. Content Rights**
- Sistema no verifica copyright
- Asegúrate de tener derechos del contenido
- Responsabilidad del usuario

---

## 🔧 **TROUBLESHOOTING**

### **"Daily campaign limit reached"**
- Causa: `campaigns_today >= max_campaigns_per_day`
- Solución: Espera hasta 00:00 UTC o aumenta límite

### **"No videos above threshold"**
- Causa: Todos los videos tienen score < threshold
- Solución: Reduce threshold o mejora contenido

### **"YouTube API quota exceeded"**
- Causa: >10,000 units/día usados
- Solución: Espera reset (00:00 PT) o habilita OAuth

### **"Meta Ads rate limit"**
- Causa: Demasiadas requests muy rápido
- Solución: Aumenta delay entre campañas (5min → 10min)

---

## 🚀 **PRÓXIMOS PASOS**

1. **Inicia monitoreo:**
   ```bash
   python unified_system_v3.py \
     --mode monitor-channel \
     --youtube-channel "TU_CANAL_ID" \
     --auto-launch \
     --max-campaigns-per-day 2
   ```

2. **Monitorea logs en tiempo real:**
   ```bash
   tail -f logs/unified_system_v3.log
   ```

3. **Verifica analytics en Grafana:**
   - http://localhost:3000
   - Dashboard: "Channel Monitor"
   - Métricas: campañas/día, budget gastado, videos analizados

4. **Ajusta parámetros según resultados:**
   - Si muchos videos ignorados: reduce threshold
   - Si sobrecarga UTM: reduce max_campaigns_per_day
   - Si poco contenido nuevo: aumenta check_interval

---

## ✅ **RESUMEN: ¿POR QUÉ NO SOBRECARGA?**

| Recurso | Capacidad | Uso con 2 campañas/día | % Uso |
|---------|-----------|------------------------|-------|
| **Meta Ads API** | 200 req/h | ~10 req/h | **5%** |
| **Device Farm TikTok** | 500 posts/día | 20 posts/día | **4%** |
| **Device Farm IG** | 125 posts/día | 10 posts/día | **8%** |
| **GoLogin Browsers** | 30 perfiles | 10 sesiones | **33%** |
| **YouTube API** | 10,000 units/día | 400 units/día | **4%** |
| **Budget Meta Ads** | ∞ (tu límite) | $100/día | **Variable** |

**Conclusión:** Sistema opera al **5-10% de capacidad** con 2 campañas/día = **SEGURO** ✅

Puedes aumentar hasta **3-4 campañas/día** sin problemas. Más de 5/día requiere:
- Más cuentas Device Farm
- Más perfiles GoLogin
- YouTube API OAuth (sin quota)
