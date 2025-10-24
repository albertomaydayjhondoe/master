# 📊 Analytics Dashboard

## 📋 Resumen Ejecutivo
- **Propósito**: Dashboard centralizado para métricas, análisis y KPIs del sistema social media
- **Estado**: 🟡 Durmiente - Mock data y visualizaciones de prueba
- **Complejidad**: Intermedio
- **Dependencias**: `streamlit`, `plotly`, `pandas`, `numpy`

## 🚀 Inicio Rápido

### 1. Lanzar Dashboard (Dummy Mode)
```bash
# Desde la raíz del proyecto
cd analytics_dashboard/
streamlit run main.py --server.port 8501

# El dashboard estará en http://localhost:8501
```

### 2. Explorar Métricas Dummy
```python
# Generar datos de prueba
from analytics_dashboard.data.mock_generator import generate_sample_data

# Generar 30 días de datos dummy
sample_data = generate_sample_data(days=30)
print(f"Generated {len(sample_data)} data points")

# Explorar métricas
metrics_summary = sample_data.describe()
print(metrics_summary)
```

### 3. API de Métricas
```python
import asyncio
from analytics_dashboard.api.metrics_api import MetricsAPI

async def test_metrics_api():
    metrics_api = MetricsAPI(dummy_mode=True)
    
    # Obtener métricas generales
    overview = await metrics_api.get_overview_metrics()
    print(f"Total accounts: {overview['total_accounts']}")
    print(f"Active sessions: {overview['active_sessions']}")
    print(f"Success rate: {overview['success_rate']:.2f}%")
    
    # Métricas por plataforma
    platform_metrics = await metrics_api.get_platform_metrics("tiktok")
    print(f"TikTok engagement: {platform_metrics['avg_engagement']:.2f}")

asyncio.run(test_metrics_api())
```

## ⚙️ Configuración Detallada

### Instalación de Dependencias
```bash
# Dependencias principales
pip install streamlit
pip install plotly
pip install pandas
pip install numpy
pip install altair

# Para gráficos avanzados
pip install seaborn
pip install matplotlib

# Para data processing
pip install scipy
pip install scikit-learn
```

### Variables de Entorno
```bash
# En .env
ANALYTICS_MODE=dummy                  # dummy/production
DASHBOARD_PORT=8501                   # Puerto del dashboard
DATA_REFRESH_INTERVAL=300             # Refresh cada 5 minutos
ENABLE_REAL_TIME=false               # Real-time updates
MAX_DATA_POINTS=10000                # Límite de datos en memoria
CHART_THEME=dark                     # dark/light theme
```

### Configuración Dashboard
```yaml
# config/analytics/dashboard_config.yaml
dashboard:
  title: "Social Media Analytics"
  refresh_interval: 300  # seconds
  
  pages:
    - name: "Overview"
      path: "/overview"
      enabled: true
    - name: "Account Performance"  
      path: "/accounts"
      enabled: true
    - name: "Device Farm Status"
      path: "/devices"
      enabled: true
    - name: "ML Insights"
      path: "/ml-insights"
      enabled: false  # Activar cuando ML esté listo

  metrics:
    retention_days: 30
    aggregation_levels: ["hourly", "daily", "weekly"]
```

## 📚 API Reference

### Core Classes

#### `AnalyticsDashboard`
Dashboard principal con múltiples páginas.

```python
# Crear dashboard
from analytics_dashboard.core.dashboard import AnalyticsDashboard

dashboard = AnalyticsDashboard(
    title="Social Media Analytics",
    theme="dark",
    dummy_mode=True
)

# Añadir páginas
dashboard.add_page("overview", OverviewPage())
dashboard.add_page("accounts", AccountsPage())
dashboard.add_page("devices", DevicesPage())

# Lanzar
dashboard.run(port=8501)
```

#### `MetricsCollector`
Recolector de métricas del sistema.

```python
# Collector de métricas
from analytics_dashboard.collectors.metrics_collector import MetricsCollector

collector = MetricsCollector(dummy_mode=True)

# Recopilar métricas actuales
current_metrics = await collector.collect_current_metrics()
print(f"Metrics collected: {len(current_metrics)}")
```

### Dashboard Pages

#### Overview Page
```python
# Página de resumen general
class OverviewPage:
    def render(self, data):
        st.title("📊 System Overview")
        
        # KPIs principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Active Accounts", 
                data['active_accounts'],
                delta=data['accounts_delta']
            )
        
        with col2:
            st.metric(
                "Success Rate", 
                f"{data['success_rate']:.1f}%",
                delta=f"{data['success_rate_delta']:.1f}%"
            )
        
        with col3:
            st.metric(
                "Daily Actions", 
                data['daily_actions'],
                delta=data['actions_delta']
            )
        
        with col4:
            st.metric(
                "ML Predictions", 
                data['ml_predictions'],
                delta=data['ml_delta']
            )
        
        # Gráfico de actividad temporal
        st.subheader("Activity Over Time")
        activity_chart = create_activity_chart(data['timeline'])
        st.plotly_chart(activity_chart, use_container_width=True)
```

#### Account Performance Page
```python
# Análisis detallado de cuentas
class AccountsPage:
    def render(self, accounts_data):
        st.title("👤 Account Performance")
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            platform_filter = st.selectbox(
                "Platform", 
                ["All", "TikTok", "Instagram", "YouTube"]
            )
        
        with col2:
            status_filter = st.selectbox(
                "Status",
                ["All", "Active", "Paused", "Banned"]
            )
        
        # Tabla de cuentas
        filtered_data = filter_accounts(
            accounts_data, 
            platform_filter, 
            status_filter
        )
        
        st.dataframe(
            filtered_data,
            columns=[
                "Account", "Platform", "Status", "Engagement", 
                "Followers", "Posts", "Last Activity"
            ]
        )
        
        # Gráficos de performance
        col1, col2 = st.columns(2)
        
        with col1:
            engagement_chart = create_engagement_chart(filtered_data)
            st.plotly_chart(engagement_chart)
        
        with col2:
            growth_chart = create_growth_chart(filtered_data)
            st.plotly_chart(growth_chart)
```

### Data Visualization

#### `create_activity_chart(data) -> plotly.Figure`
Gráfico de actividad temporal.

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_activity_chart(timeline_data):
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=["Actions per Hour", "Success Rate"],
        vertical_spacing=0.1
    )
    
    # Actions per hour
    fig.add_trace(
        go.Scatter(
            x=timeline_data['timestamp'],
            y=timeline_data['actions_count'],
            mode='lines+markers',
            name='Actions',
            line=dict(color='#00ff00', width=2)
        ),
        row=1, col=1
    )
    
    # Success rate
    fig.add_trace(
        go.Scatter(
            x=timeline_data['timestamp'],
            y=timeline_data['success_rate'],
            mode='lines+markers',
            name='Success Rate %',
            line=dict(color='#ff6b6b', width=2),
            yaxis='y2'
        ),
        row=2, col=1
    )
    
    # Styling
    fig.update_layout(
        title="System Activity Timeline",
        xaxis_title="Time",
        template="plotly_dark",
        height=600
    )
    
    return fig
```

#### `create_performance_heatmap(data) -> plotly.Figure`
Heatmap de performance por hora/día.

```python
def create_performance_heatmap(performance_data):
    # Preparar datos para heatmap
    pivot_data = performance_data.pivot_table(
        values='success_rate',
        index='hour',
        columns='day_of_week',
        aggfunc='mean'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        y=list(range(24)),
        colorscale='RdYlGn',
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Performance Heatmap (Success Rate by Hour/Day)",
        xaxis_title="Day of Week",
        yaxis_title="Hour of Day",
        template="plotly_dark"
    )
    
    return fig
```

### Real-time Updates

#### `StreamingDataUpdater`
Actualizador de datos en tiempo real.

```python
class StreamingDataUpdater:
    def __init__(self, refresh_interval=30):
        self.refresh_interval = refresh_interval
        self.last_update = datetime.now()
    
    async def start_streaming(self, dashboard):
        """Inicia actualizaciones en tiempo real"""
        while True:
            try:
                # Obtener nuevos datos
                new_data = await self.fetch_latest_data()
                
                # Actualizar dashboard
                dashboard.update_data(new_data)
                
                # Marcar última actualización
                self.last_update = datetime.now()
                
                await asyncio.sleep(self.refresh_interval)
                
            except Exception as e:
                st.error(f"Update failed: {e}")
                await asyncio.sleep(self.refresh_interval)
    
    async def fetch_latest_data(self):
        # En modo dummy, generar datos aleatorios
        if self.dummy_mode:
            return self.generate_mock_update()
        
        # En producción, consultar APIs reales
        return await self.fetch_production_data()
```

## 🔧 Troubleshooting

### Problemas de Instalación

#### 1. **Streamlit no se instala**
```bash
# Actualizar pip
pip install --upgrade pip

# Instalar streamlit
pip install streamlit

# Verificar instalación
streamlit hello
```

#### 2. **Plotly charts no se muestran**
```bash
# Instalar dependencias adicionales
pip install plotly-express
pip install kaleido  # Para export de imágenes

# En el código
import plotly.express as px
import plotly.graph_objects as go
```

#### 3. **Puerto 8501 en uso**
```bash
# Encontrar proceso usando el puerto
lsof -i :8501

# Matar proceso
kill -9 <PID>

# O usar puerto diferente
streamlit run main.py --server.port 8502
```

### Problemas de Datos

#### 4. **Datos no se cargan**
```python
# Debug data loading
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar conexión a fuentes de datos
async def test_data_sources():
    try:
        # Test monitoring system
        from social_extensions.telegram.monitoring import get_recent_activities
        activities = await get_recent_activities(limit=10)
        print(f"✅ Monitoring: {len(activities)} activities")
        
    except Exception as e:
        print(f"❌ Monitoring error: {e}")
    
    try:
        # Test device farm
        from device_farm.controllers.factory import create_device_manager
        dm = create_device_manager()
        devices = await dm.get_available_devices()
        print(f"✅ Device Farm: {len(devices)} devices")
        
    except Exception as e:
        print(f"❌ Device Farm error: {e}")

asyncio.run(test_data_sources())
```

#### 5. **Performance lenta**
```python
# Optimizar carga de datos
import pandas as pd

# Usar cache para datos costosos
@st.cache_data(ttl=300)  # Cache 5 minutos
def load_heavy_data():
    # Cargar y procesar datos pesados
    return processed_data

# Limitar datos históricos
def limit_data_points(df, max_points=1000):
    if len(df) > max_points:
        # Tomar muestra representativa
        step = len(df) // max_points
        return df.iloc[::step]
    return df
```

## 🔗 Integraciones

### Con Sistema de Monitoring
```python
# Integrar métricas de monitoring
from social_extensions.telegram.monitoring import ActivityMetric

async def fetch_monitoring_metrics():
    # Obtener actividades recientes
    activities = await monitor.get_recent_activities(hours=24)
    
    # Agregar métricas
    metrics = {
        "total_activities": len(activities),
        "success_rate": sum(1 for a in activities if a.success) / len(activities) * 100,
        "avg_duration": statistics.mean(a.duration_ms for a in activities),
        "error_rate": sum(1 for a in activities if not a.success) / len(activities) * 100
    }
    
    # Métricas por tipo de actividad
    by_type = {}
    for activity in activities:
        if activity.type not in by_type:
            by_type[activity.type] = {"count": 0, "success": 0}
        by_type[activity.type]["count"] += 1
        if activity.success:
            by_type[activity.type]["success"] += 1
    
    metrics["by_type"] = by_type
    return metrics
```

### Con Device Farm
```python
# Dashboard de estado de dispositivos
async def fetch_device_metrics():
    from device_farm.controllers.factory import create_device_manager
    
    device_manager = create_device_manager()
    devices = await device_manager.get_available_devices()
    
    device_metrics = {
        "total_devices": len(devices),
        "online_devices": len([d for d in devices if d['status'] == 'connected']),
        "busy_devices": len([d for d in devices if d['status'] == 'busy']),
        "offline_devices": len([d for d in devices if d['status'] == 'disconnected']),
    }
    
    # Health score promedio
    health_scores = [d.get('health_score', 0) for d in devices]
    device_metrics["avg_health"] = statistics.mean(health_scores) if health_scores else 0
    
    return device_metrics

# Visualización en dashboard
def render_device_status(device_metrics):
    st.subheader("📱 Device Farm Status")
    
    # Status cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Devices", device_metrics["total_devices"])
    with col2:
        st.metric("Online", device_metrics["online_devices"])
    with col3:
        st.metric("Busy", device_metrics["busy_devices"])  
    with col4:
        st.metric("Offline", device_metrics["offline_devices"])
    
    # Health gauge
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = device_metrics["avg_health"] * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Average Health %"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    st.plotly_chart(fig)
```

### Con ML Integration
```python
# Dashboard de insights ML
async def fetch_ml_metrics():
    from ml_integration.ultralytics_bridge import create_ml_bridge
    
    ml_bridge = create_ml_bridge()
    
    # Métricas dummy para mostrar estructura
    if ml_bridge.dummy_mode:
        return {
            "predictions_today": random.randint(50, 200),
            "avg_confidence": random.uniform(0.7, 0.95),
            "viral_predictions": random.randint(5, 25),
            "top_trending_objects": [
                {"object": "person", "frequency": 45},
                {"object": "phone", "frequency": 32},
                {"object": "car", "frequency": 28}
            ]
        }
    
    # En producción, obtener métricas reales
    return await ml_bridge.get_system_metrics()

# Visualización ML insights
def render_ml_insights(ml_metrics):
    st.subheader("🧠 ML Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Predictions Today", ml_metrics["predictions_today"])
    with col2:
        st.metric("Avg Confidence", f"{ml_metrics['avg_confidence']:.2f}")
    with col3:
        st.metric("Viral Predictions", ml_metrics["viral_predictions"])
    
    # Top trending objects
    st.subheader("📈 Trending Visual Elements")
    trending_df = pd.DataFrame(ml_metrics["top_trending_objects"])
    
    fig = px.bar(
        trending_df, 
        x='object', 
        y='frequency',
        title="Most Detected Objects"
    )
    st.plotly_chart(fig)
```

## 📈 Métricas Predefinidas

### Core KPIs
```python
# KPIs principales del sistema
CORE_KPIS = {
    "system_health": {
        "name": "System Health Score",
        "description": "Overall system health (0-100)",
        "target": "> 90",
        "calculation": "weighted_avg(device_health, account_health, service_health)"
    },
    
    "account_performance": {
        "name": "Account Success Rate", 
        "description": "% of successful account actions",
        "target": "> 85%",
        "calculation": "successful_actions / total_actions * 100"
    },
    
    "engagement_growth": {
        "name": "Daily Engagement Growth",
        "description": "Average engagement increase per day",
        "target": "> 5%",
        "calculation": "(today_engagement - yesterday_engagement) / yesterday_engagement * 100"
    },
    
    "ml_accuracy": {
        "name": "ML Prediction Accuracy",
        "description": "Accuracy of viral predictions",
        "target": "> 70%",
        "calculation": "correct_predictions / total_predictions * 100"
    }
}
```

### Custom Metrics Builder
```python
class MetricBuilder:
    def __init__(self):
        self.metrics = {}
    
    def add_metric(self, name, query_func, aggregation="sum"):
        """Añade métrica personalizada"""
        self.metrics[name] = {
            "query": query_func,
            "aggregation": aggregation,
            "last_calculated": None,
            "value": None
        }
    
    async def calculate_metric(self, name, time_range="24h"):
        """Calcula valor de métrica"""
        if name not in self.metrics:
            raise ValueError(f"Metric {name} not found")
        
        metric = self.metrics[name]
        raw_data = await metric["query"](time_range)
        
        # Aplicar agregación
        if metric["aggregation"] == "sum":
            value = sum(raw_data)
        elif metric["aggregation"] == "avg":
            value = statistics.mean(raw_data)
        elif metric["aggregation"] == "max":
            value = max(raw_data)
        elif metric["aggregation"] == "count":
            value = len(raw_data)
        
        # Actualizar métrica
        metric["value"] = value
        metric["last_calculated"] = datetime.now()
        
        return value

# Ejemplo de uso
builder = MetricBuilder()

# Añadir métrica personalizada
async def get_tiktok_likes(time_range):
    # Query para obtener likes de TikTok en el rango de tiempo
    return [100, 150, 200, 300]  # Dummy data

builder.add_metric("tiktok_daily_likes", get_tiktok_likes, "sum")

# Calcular
total_likes = await builder.calculate_metric("tiktok_daily_likes", "24h")
print(f"Total TikTok likes today: {total_likes}")
```

## 💡 Buenas Prácticas

### 1. Performance Optimization
```python
# Cache datos costosos
import functools
from datetime import timedelta

@functools.lru_cache(maxsize=128)
def expensive_calculation(data_hash):
    # Cálculos costosos
    return processed_data

# Pagination para datasets grandes
def paginate_data(df, page_size=1000):
    for start in range(0, len(df), page_size):
        yield df.iloc[start:start + page_size]

# Usar sampling para visualizaciones
def smart_sampling(df, max_points=5000):
    if len(df) <= max_points:
        return df
    
    # Sampling estratificado manteniendo tendencias
    step = len(df) // max_points
    return df.iloc[::step]
```

### 2. Data Quality
```python
# Validación de datos
def validate_metrics_data(data):
    checks = {
        "no_null_values": data.isnull().sum().sum() == 0,
        "positive_values": (data.select_dtypes(include=[np.number]) >= 0).all().all(),
        "reasonable_ranges": all(
            data[col].between(0, 100).all() 
            for col in ['success_rate', 'engagement_rate'] 
            if col in data.columns
        )
    }
    
    failed_checks = [check for check, passed in checks.items() if not passed]
    
    if failed_checks:
        st.warning(f"Data quality issues: {failed_checks}")
    
    return len(failed_checks) == 0

# Detección de anomalías
def detect_anomalies(series, threshold=3):
    """Detecta valores anómalos usando Z-score"""
    z_scores = np.abs((series - series.mean()) / series.std())
    return series[z_scores > threshold]
```

### 3. User Experience
```python
# Loading states
def show_loading_state():
    with st.spinner("Loading data..."):
        data = load_data()
    return data

# Error handling elegante
def safe_render_chart(chart_func, data):
    try:
        return chart_func(data)
    except Exception as e:
        st.error(f"Chart rendering failed: {e}")
        st.info("Please refresh or contact support")
        return None

# Responsive layouts
def adaptive_columns(items, max_cols=4):
    """Adapta número de columnas al contenido"""
    n_items = len(items)
    n_cols = min(n_items, max_cols)
    
    cols = st.columns(n_cols)
    for i, item in enumerate(items):
        with cols[i % n_cols]:
            render_item(item)
```

## 🚀 Activación del Sistema

### Checklist para Salir de Modo Dormant

- [ ] 📦 Instalar dependencias de producción (`streamlit`, `plotly`, etc.)
- [ ] 🔌 Conectar fuentes de datos reales (monitoring, device farm, ML)
- [ ] ⚙️ Configurar variables de entorno de producción
- [ ] 📊 Validar métricas con datos reales
- [ ] 🎨 Personalizar theme y branding
- [ ] 🔒 Implementar autenticación si es necesaria
- [ ] 📈 Configurar alertas y notifications
- [ ] 🧪 Test de performance con datos de producción

### Comando de Activación
```python
# Activar dashboard en modo producción
analytics_dashboard = AnalyticsDashboard(
    dummy_mode=False,
    real_time_updates=True
)

# Health check
health = await analytics_dashboard.system_health_check()
print(f"Analytics Dashboard Ready: {health['ready']}")
```

---

## 📞 Soporte

- **Dashboard Issues**: Problemas de visualización y performance
- **Data Integration**: Conexión con fuentes de datos
- **Custom Metrics**: Creación de métricas personalizadas
- **Performance**: Optimización de queries y visualizaciones