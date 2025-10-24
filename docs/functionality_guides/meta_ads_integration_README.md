# 🎯 Meta Ads Integration

## 📋 Resumen Ejecutivo
- **Propósito**: Integración completa con Meta Ads API para campañas automatizadas de Facebook e Instagram
- **Estado**: 🟡 Durmiente - API mock con simulación de campaigns y analytics
- **Complejidad**: Alto
- **Dependencias**: `facebook-business`, `requests`, `pandas`

## 🚀 Inicio Rápido

### 1. Configuración Básica (Dummy Mode)
```python
from meta_ads_integration.core.meta_ads_manager import MetaAdsManager

# Crear manager en modo dummy
ads_manager = MetaAdsManager(dummy_mode=True)

# Verificar conexión (simulada)
connection_status = await ads_manager.test_connection()
print(f"Meta API Status: {connection_status['status']}")
print(f"Account Access: {connection_status['account_access']}")
print(f"Available Accounts: {len(connection_status['ad_accounts'])}")
```

### 2. Crear Campaña Simple
```python
import asyncio

async def create_simple_campaign():
    # Configuración de campaña
    campaign_config = {
        "name": "Viral Content Promotion",
        "objective": "VIDEO_VIEWS",
        "budget_daily": 50.00,  # $50/día
        "target_audience": {
            "age_min": 18,
            "age_max": 35,
            "interests": ["Social Media", "Entertainment", "Music"],
            "locations": ["US", "CA", "GB", "AU"]
        }
    }
    
    # Crear campaña
    campaign = await ads_manager.create_campaign(campaign_config)
    
    print(f"Campaign created: {campaign['id']}")
    print(f"Status: {campaign['status']}")
    print(f"Budget: ${campaign['daily_budget']}")
    
    return campaign

campaign = asyncio.run(create_simple_campaign())
```

### 3. Analytics de Campaña
```python
# Obtener métricas de rendimiento
campaign_analytics = await ads_manager.get_campaign_analytics(
    campaign_id=campaign['id'],
    date_range="last_7_days",
    metrics=["impressions", "clicks", "video_views", "cpm", "ctr"]
)

print(f"Campaign Performance (7 days):")
print(f"  Impressions: {campaign_analytics['impressions']:,}")
print(f"  Clicks: {campaign_analytics['clicks']:,}")
print(f"  Video Views: {campaign_analytics['video_views']:,}")
print(f"  CPM: ${campaign_analytics['cpm']:.2f}")
print(f"  CTR: {campaign_analytics['ctr']:.2f}%")
```

## ⚙️ Configuración Detallada

### Instalación de Dependencias
```bash
# SDK oficial de Facebook
pip install facebook-business

# Procesamiento de datos
pip install pandas
pip install numpy

# APIs y requests
pip install requests
pip install aiohttp

# Análisis y reportes
pip install plotly
pip install seaborn
```

### Variables de Entorno
```bash
# En .env para producción
META_ADS_MODE=dummy                    # dummy/production
META_ACCESS_TOKEN=your_access_token    # Token de acceso a Meta API
META_APP_ID=your_app_id               # ID de la app
META_APP_SECRET=your_app_secret       # Secret de la app
META_AD_ACCOUNT_ID=act_123456789      # ID de cuenta publicitaria

# Configuraciones
DEFAULT_CURRENCY=USD                   # Moneda por defecto
MAX_DAILY_BUDGET=500                  # Máximo budget diario
AUTO_BID_OPTIMIZATION=true            # Optimización automática de pujas
PIXEL_ID=your_pixel_id               # Facebook Pixel ID
```

### Configuración de Audiencias
```yaml
# config/meta_ads/audiences.yaml
target_audiences:
  gen_z_content:
    name: "Gen Z Content Consumers"
    age_min: 16
    age_max: 25
    interests:
      - "TikTok"
      - "Instagram"
      - "Music"
      - "Social media"
      - "Entertainment"
    behaviors:
      - "Mobile device users"
      - "Engaged shoppers"
    
  millennials_creators:
    name: "Millennial Content Creators"
    age_min: 26
    age_max: 40
    interests:
      - "Content creation"
      - "Digital marketing"
      - "Entrepreneurship"
      - "Technology"
    
  viral_content_fans:
    name: "Viral Content Enthusiasts"
    age_min: 18
    age_max: 45
    interests:
      - "Viral videos"
      - "Comedy"
      - "Trending topics"
    custom_audiences:
      - "website_visitors_30_days"
      - "video_viewers_75_percent"

campaign_objectives:
  awareness:
    - "BRAND_AWARENESS"
    - "REACH"
  
  consideration:
    - "TRAFFIC"
    - "VIDEO_VIEWS"
    - "LEAD_GENERATION"
  
  conversion:
    - "CONVERSIONS" 
    - "CATALOG_SALES"
    - "STORE_VISITS"
```

## 📚 API Reference

### Core Classes

#### `MetaAdsManager`
Gestor principal de Meta Ads API.

```python
# Crear manager
ads_manager = MetaAdsManager(
    access_token="your_token",
    ad_account_id="act_123456789",
    dummy_mode=True
)

# Verificar inicialización
print(f"Manager ready: {ads_manager.is_initialized}")
print(f"Account ID: {ads_manager.ad_account_id}")
print(f"API version: {ads_manager.api_version}")
```

#### `Campaign`
Modelo de campaña publicitaria.

```python
from meta_ads_integration.models.campaign import Campaign

@dataclass
class Campaign:
    id: str
    name: str
    objective: str
    status: str
    daily_budget: float
    lifetime_budget: float
    start_time: datetime
    end_time: Optional[datetime]
    target_audience: Dict[str, Any]
    created_time: datetime
    updated_time: datetime
    metrics: Dict[str, float]
```

### Campaign Management

#### `create_campaign(config: Dict) -> Campaign`
Crea nueva campaña publicitaria.

```python
# Campaña básica para promoción de contenido
content_promotion_config = {
    "name": "Viral Video Promotion - October",
    "objective": "VIDEO_VIEWS",
    "budget_daily": 75.00,
    "start_time": datetime.now(),
    "end_time": datetime.now() + timedelta(days=7),
    
    "target_audience": {
        "age_min": 18,
        "age_max": 35,
        "genders": [1, 2],  # All genders
        "geo_locations": {
            "countries": ["US", "CA", "GB", "AU"],
            "location_types": ["home", "recent"]
        },
        "interests": [
            {"id": "6003107902433", "name": "Social media"},
            {"id": "6003020834693", "name": "Music"},
            {"id": "6003445590534", "name": "Entertainment"}
        ]
    },
    
    "optimization_goal": "VIDEO_VIEWS",
    "billing_event": "IMPRESSIONS",
    "bid_strategy": "LOWEST_COST_WITHOUT_CAP"
}

campaign = await ads_manager.create_campaign(content_promotion_config)

# Campaña de conversiones con pixel tracking
conversion_campaign_config = {
    "name": "Website Traffic Campaign",
    "objective": "CONVERSIONS",
    "budget_daily": 100.00,
    
    "target_audience": {
        "age_min": 25,
        "age_max": 45,
        "custom_audiences": ["website_visitors_30_days"],
        "lookalike_audiences": [
            {"source_audience": "high_value_customers", "ratio": 0.01}
        ]
    },
    
    "conversion_specs": [
        {
            "action.type": "offsite-conversion.custom.123456789",
            "offsite_pixel": ads_manager.pixel_id
        }
    ],
    
    "optimization_goal": "OFFSITE_CONVERSIONS"
}

conversion_campaign = await ads_manager.create_campaign(conversion_campaign_config)
```

#### `create_ad_set(campaign_id: str, config: Dict) -> AdSet`
Crea conjunto de anuncios dentro de una campaña.

```python
# Ad Set para móviles con video vertical
mobile_adset_config = {
    "name": "Mobile Video Ad Set",
    "campaign_id": campaign['id'],
    "daily_budget": 30.00,
    
    "targeting": {
        "age_min": 18,
        "age_max": 30,
        "device_platforms": ["mobile"],
        "publisher_platforms": ["facebook", "instagram"],
        "facebook_positions": ["feed", "story"],
        "instagram_positions": ["feed", "story", "reels"]
    },
    
    "optimization_goal": "VIDEO_VIEWS",
    "billing_event": "IMPRESSIONS",
    
    "promoted_object": {
        "page_id": "your_page_id",
        "video_id": "your_video_id"
    }
}

adset = await ads_manager.create_ad_set(mobile_adset_config)

# Ad Set para desktop con targeting avanzado
desktop_adset_config = {
    "name": "Desktop Engagement Ad Set", 
    "campaign_id": campaign['id'],
    "daily_budget": 45.00,
    
    "targeting": {
        "age_min": 25,
        "age_max": 50,
        "device_platforms": ["desktop"],
        "interests": [
            {"id": "6003139266461", "name": "Digital marketing"}
        ],
        "behaviors": [
            {"id": "6002714895372", "name": "Business travelers"}
        ],
        "exclusions": {
            "custom_audiences": ["existing_customers"]
        }
    },
    
    "bid_amount": 2.50,  # Manual bid
    "bid_strategy": "LOWEST_COST_WITH_BID_CAP"
}

desktop_adset = await ads_manager.create_ad_set(desktop_adset_config)
```

#### `create_ad_creative(config: Dict) -> AdCreative`
Crea creatividad publicitaria.

```python
# Creatividad de video para TikTok/Instagram Reels
video_creative_config = {
    "name": "Viral Video Creative",
    "object_story_spec": {
        "page_id": "your_page_id",
        "video_data": {
            "video_id": "your_video_id",
            "image_url": "https://example.com/thumbnail.jpg",
            "title": "Mira este contenido viral 🔥",
            "message": "No te pierdas este video que está arrasando en redes sociales. ¡Dale play y compártelo!",
            "call_to_action": {
                "type": "WATCH_MORE",
                "value": {
                    "link": "https://your-website.com/video"
                }
            }
        }
    },
    
    "degrees_of_freedom_spec": {
        "creative_features_spec": {
            "standard_enhancements": {
                "enroll_status": "OPT_IN"
            }
        }
    }
}

creative = await ads_manager.create_ad_creative(video_creative_config)

# Creatividad carousel para múltiples videos
carousel_creative_config = {
    "name": "Viral Content Carousel",
    "object_story_spec": {
        "page_id": "your_page_id",
        "link_data": {
            "message": "Descubre el mejor contenido viral 🚀",
            "child_attachments": [
                {
                    "video_id": "video_1_id",
                    "name": "Video Viral #1",
                    "description": "Este video tiene millones de views",
                    "link": "https://your-site.com/video1"
                },
                {
                    "video_id": "video_2_id", 
                    "name": "Video Viral #2",
                    "description": "Trending en todas las plataformas",
                    "link": "https://your-site.com/video2"
                },
                {
                    "video_id": "video_3_id",
                    "name": "Video Viral #3", 
                    "description": "Más de 50M de reproducciones",
                    "link": "https://your-site.com/video3"
                }
            ],
            "call_to_action": {
                "type": "WATCH_MORE"
            }
        }
    }
}

carousel_creative = await ads_manager.create_ad_creative(carousel_creative_config)
```

### Analytics & Reporting

#### `get_campaign_analytics(campaign_id, date_range, metrics) -> Dict`
Obtiene métricas detalladas de campaña.

```python
# Analytics básicos
basic_analytics = await ads_manager.get_campaign_analytics(
    campaign_id=campaign['id'],
    date_range="last_30_days",
    metrics=[
        "impressions", "clicks", "ctr", "cpm", "cpp",
        "video_views", "video_view_rate",
        "cost_per_video_view", "spend"
    ]
)

print(f"Campaign Analytics:")
print(f"  Spend: ${basic_analytics['spend']:.2f}")
print(f"  Impressions: {basic_analytics['impressions']:,}")
print(f"  Video Views: {basic_analytics['video_views']:,}")
print(f"  Cost per Video View: ${basic_analytics['cost_per_video_view']:.3f}")

# Analytics avanzados con breakdowns
advanced_analytics = await ads_manager.get_campaign_analytics(
    campaign_id=campaign['id'],
    date_range="last_7_days",
    metrics=[
        "impressions", "clicks", "video_views", "spend",
        "actions", "cost_per_action_type"
    ],
    breakdowns=[
        "age", "gender", "placement", "device_platform"
    ]
)

# Análisis por edad y género
for breakdown in advanced_analytics['breakdown_results']:
    if breakdown['age'] and breakdown['gender']:
        print(f"Age {breakdown['age']}, Gender {breakdown['gender']}:")
        print(f"  Impressions: {breakdown['impressions']:,}")
        print(f"  Video Views: {breakdown['video_views']:,}")
        print(f"  Spend: ${breakdown['spend']:.2f}")
```

#### `get_audience_insights(audience_config) -> Dict`
Obtiene insights de audiencia.

```python
# Insights de audiencia target
audience_insights = await ads_manager.get_audience_insights(
    audience_config={
        "age_min": 18,
        "age_max": 35,
        "genders": [1, 2],
        "geo_locations": {"countries": ["US"]},
        "interests": [
            {"id": "6003107902433", "name": "Social media"}
        ]
    },
    metrics=["audience_size", "page_likes", "demographics"]
)

print(f"Audience Insights:")
print(f"  Estimated Size: {audience_insights['audience_size']:,}")
print(f"  Facebook Page Likes: {audience_insights['page_likes']:,}")
print(f"  Top Demographics: {audience_insights['demographics']['age_gender']}")

# Comparación de audiencias
audience_comparison = await ads_manager.compare_audiences([
    {
        "name": "Gen Z Audience",
        "age_min": 16, "age_max": 25,
        "interests": [{"name": "TikTok"}]
    },
    {
        "name": "Millennial Audience", 
        "age_min": 26, "age_max": 40,
        "interests": [{"name": "Digital marketing"}]
    }
])

for audience in audience_comparison:
    print(f"{audience['name']}: {audience['size']:,} people")
```

### Automation & Optimization

#### `optimize_campaigns() -> List[Dict]`
Optimización automática de campañas activas.

```python
# Optimización automática basada en performance
optimization_results = await ads_manager.optimize_campaigns(
    criteria={
        "min_ctr": 1.0,           # CTR mínimo 1%
        "max_cpm": 15.0,          # CPM máximo $15
        "min_video_view_rate": 0.3, # Min 30% video view rate
        "performance_window": "last_3_days"
    },
    actions={
        "pause_underperforming": True,
        "increase_budget_top_performers": True,
        "adjust_bids": True,
        "expand_successful_audiences": True
    }
)

for result in optimization_results:
    print(f"Campaign: {result['campaign_name']}")
    print(f"  Actions taken: {', '.join(result['actions_taken'])}")
    print(f"  Performance change: {result['performance_change']}")

# Optimización de presupuesto automática
budget_optimization = await ads_manager.optimize_budgets(
    total_budget=500.00,  # $500 total
    allocation_strategy="performance_based",
    min_budget_per_campaign=20.00,
    max_budget_per_campaign=150.00
)

print(f"Budget Optimization Results:")
for campaign_id, new_budget in budget_optimization.items():
    campaign_name = await ads_manager.get_campaign_name(campaign_id)
    print(f"  {campaign_name}: ${new_budget:.2f}/day")
```

#### `create_lookalike_audience(source_audience, ratio) -> Dict`
Crea audiencia similar basada en audiencia fuente.

```python
# Crear lookalike de clientes de alto valor
high_value_lookalike = await ads_manager.create_lookalike_audience(
    name="High Value Customers Lookalike 1%",
    source_audience={
        "type": "custom_audience",
        "id": "your_custom_audience_id",
        "description": "Customers who spent $100+"
    },
    ratio=0.01,  # Top 1% similar
    countries=["US", "CA", "GB"]
)

print(f"Lookalike audience created: {high_value_lookalike['id']}")
print(f"Estimated size: {high_value_lookalike['approximate_count']:,}")

# Crear múltiples lookalikes con diferentes ratios
lookalike_variations = await ads_manager.create_lookalike_variations(
    source_audience_id="your_source_id",
    ratios=[0.01, 0.03, 0.05, 0.10],  # 1%, 3%, 5%, 10%
    countries=["US"]
)

for lookalike in lookalike_variations:
    print(f"Lookalike {lookalike['ratio']*100:.0f}%: {lookalike['size']:,} people")
```

## 🔧 Troubleshooting

### Problemas de API

#### 1. **Token de acceso expirado**
```python
# Verificar validez del token
token_status = await ads_manager.validate_access_token()
print(f"Token valid: {token_status['valid']}")

if not token_status['valid']:
    print(f"Token issue: {token_status['error']}")
    
    # Regenerar token si es posible
    if token_status['can_refresh']:
        new_token = await ads_manager.refresh_access_token()
        print(f"New token generated: {new_token[:20]}...")

# Verificar permisos del token
permissions = await ads_manager.get_token_permissions()
required_permissions = [
    'ads_management', 'ads_read', 'business_management'
]

missing_permissions = [p for p in required_permissions if p not in permissions]
if missing_permissions:
    print(f"Missing permissions: {', '.join(missing_permissions)}")
```

#### 2. **Rate limits de API**
```python
# Verificar límites de rate
rate_limit_status = await ads_manager.check_rate_limits()

for endpoint, limits in rate_limit_status.items():
    print(f"{endpoint}:")
    print(f"  Calls made: {limits['calls_made']}")
    print(f"  Limit: {limits['call_limit']}")
    print(f"  Reset time: {limits['reset_time']}")
    
    if limits['calls_made'] >= limits['call_limit'] * 0.8:
        print(f"  ⚠️  Approaching rate limit")

# Implementar backoff automático
await ads_manager.enable_rate_limit_handling(
    backoff_strategy="exponential",
    max_retries=3,
    respect_limits=True
)
```

#### 3. **Errores de campaña**
```python
# Verificar estado de campañas
campaign_health = await ads_manager.check_campaigns_health()

for campaign in campaign_health:
    if campaign['issues']:
        print(f"Campaign {campaign['name']} has issues:")
        for issue in campaign['issues']:
            print(f"  - {issue['type']}: {issue['message']}")
            
            # Auto-fix si es posible
            if issue['auto_fixable']:
                fix_result = await ads_manager.auto_fix_issue(
                    campaign['id'], 
                    issue['type']
                )
                print(f"    Fix result: {fix_result['success']}")

# Debug de delivery de anuncios
delivery_debug = await ads_manager.debug_ad_delivery(campaign_id)
print(f"Delivery Debug:")
print(f"  Status: {delivery_debug['delivery_status']}")
print(f"  Issues: {delivery_debug['delivery_issues']}")
print(f"  Recommendations: {delivery_debug['recommendations']}")
```

### Problemas de Performance

#### 4. **Baja performance de campañas**
```python
# Análisis de performance automático
performance_analysis = await ads_manager.analyze_campaign_performance(
    campaign_id=campaign['id'],
    benchmark_against="industry_average"
)

print(f"Performance Analysis:")
print(f"  CTR vs Industry: {performance_analysis['ctr_vs_benchmark']:.2f}x")
print(f"  CPM vs Industry: {performance_analysis['cpm_vs_benchmark']:.2f}x")
print(f"  Performance Score: {performance_analysis['overall_score']:.1f}/10")

# Recomendaciones automáticas
recommendations = performance_analysis['recommendations']
for rec in recommendations:
    print(f"Recommendation: {rec['action']}")
    print(f"  Impact: {rec['expected_impact']}")
    print(f"  Effort: {rec['implementation_effort']}")

# Implementar recomendaciones automáticamente
for rec in recommendations:
    if rec['auto_implementable'] and rec['expected_impact'] > 0.15:
        result = await ads_manager.implement_recommendation(
            campaign_id, rec['action'], rec['parameters']
        )
        print(f"Implemented: {rec['action']} - {result['success']}")
```

#### 5. **Audiencias saturadas**
```python
# Detectar saturación de audiencia
saturation_analysis = await ads_manager.analyze_audience_saturation(
    campaign_id=campaign['id']
)

print(f"Audience Saturation Analysis:")
print(f"  Saturation Level: {saturation_analysis['saturation_level']:.1f}%")
print(f"  Frequency: {saturation_analysis['frequency']:.2f}")
print(f"  Reach: {saturation_analysis['reach_percentage']:.1f}%")

if saturation_analysis['saturation_level'] > 70:
    # Expandir audiencia automáticamente
    expansion_options = await ads_manager.get_audience_expansion_options(
        campaign_id
    )
    
    print("Audience Expansion Options:")
    for option in expansion_options:
        print(f"  {option['type']}: +{option['additional_reach']:,} people")
    
    # Implementar mejor opción
    best_option = max(expansion_options, key=lambda x: x['quality_score'])
    expansion_result = await ads_manager.expand_audience(
        campaign_id, best_option
    )
    
    print(f"Expanded audience: {expansion_result['success']}")
```

## 🔗 Integraciones

### Con Platform Publishing
```python
# Sincronizar campañas con contenido publicado
async def sync_ads_with_published_content():
    from platform_publishing.core.publisher import UnifiedPublisher
    
    publisher = UnifiedPublisher()
    
    # Obtener contenido recién publicado
    recent_posts = await publisher.get_recent_posts(hours=24)
    
    for post in recent_posts:
        if post['platform'] in ['facebook', 'instagram'] and post['engagement'] > 1000:
            # Crear campaña para promocionar contenido viral
            campaign_config = {
                "name": f"Promote Viral Post - {post['title'][:30]}",
                "objective": "VIDEO_VIEWS",
                "budget_daily": min(50 + (post['engagement'] / 100), 200),
                
                "promoted_object": {
                    "page_id": post['page_id'],
                    "post_id": post['post_id']
                },
                
                "target_audience": {
                    "age_min": 18,
                    "age_max": 45,
                    "interests": post['hashtags'][:5],  # Usar hashtags como intereses
                    "lookalike_audiences": ["engaged_users_30d"]
                }
            }
            
            campaign = await ads_manager.create_campaign(campaign_config)
            
            # Log promoción automática
            print(f"Auto-promoted post {post['id']} with campaign {campaign['id']}")

# Optimizar presupuesto basado en performance de contenido
async def optimize_budget_by_content_performance():
    # Obtener analytics de contenido
    content_analytics = await publisher.get_content_analytics(days=7)
    
    # Obtener campaigns activas
    active_campaigns = await ads_manager.get_active_campaigns()
    
    for campaign in active_campaigns:
        # Encontrar contenido asociado
        promoted_post = campaign.get('promoted_object', {}).get('post_id')
        
        if promoted_post:
            post_performance = content_analytics.get(promoted_post, {})
            
            # Ajustar presupuesto basado en performance orgánica
            organic_engagement = post_performance.get('engagement_rate', 0)
            
            if organic_engagement > 0.1:  # 10% engagement orgánico
                # Aumentar presupuesto para contenido de alto rendimiento
                new_budget = min(campaign['daily_budget'] * 1.5, 300)
                await ads_manager.update_campaign_budget(campaign['id'], new_budget)
                
            elif organic_engagement < 0.02:  # Menos de 2%
                # Reducir o pausar contenido de bajo rendimiento
                await ads_manager.pause_campaign(campaign['id'])
```

### Con ML Integration
```python
# Usar ML para optimización de audiencias y creatividades
async def ml_optimized_ad_campaigns():
    from ml_integration.ultralytics_bridge import create_ml_bridge
    
    ml_bridge = create_ml_bridge()
    
    # Analizar contenido para identificar elementos virales
    content_analysis = await ml_bridge.analyze_content("/content/viral_video.mp4")
    
    # Obtener recomendaciones de targeting basadas en análisis ML
    targeting_recommendations = await ml_bridge.get_targeting_recommendations(
        content_analysis
    )
    
    # Crear campaña optimizada por ML
    ml_optimized_config = {
        "name": "ML Optimized Campaign",
        "objective": "VIDEO_VIEWS",
        "budget_daily": 100.00,
        
        "target_audience": {
            "age_min": targeting_recommendations["optimal_age_min"],
            "age_max": targeting_recommendations["optimal_age_max"],
            "interests": targeting_recommendations["recommended_interests"],
            "behaviors": targeting_recommendations["recommended_behaviors"],
            "custom_audiences": targeting_recommendations["lookalike_sources"]
        },
        
        "creative_elements": {
            "messaging": targeting_recommendations["optimal_messaging"],
            "cta_type": targeting_recommendations["optimal_cta"],
            "visual_style": targeting_recommendations["visual_preferences"]
        }
    }
    
    campaign = await ads_manager.create_campaign(ml_optimized_config)
    
    return campaign

# Predicción de performance de campañas
async def predict_campaign_performance(campaign_config):
    ml_bridge = create_ml_bridge()
    
    # Extraer features para predicción
    campaign_features = {
        "target_audience_size": await ads_manager.estimate_audience_size(
            campaign_config["target_audience"]
        ),
        "budget_daily": campaign_config["budget_daily"],
        "objective": campaign_config["objective"],
        "placement_count": len(campaign_config.get("placements", ["feed"])),
        "interest_count": len(campaign_config["target_audience"].get("interests", [])),
        "age_range": (
            campaign_config["target_audience"]["age_max"] - 
            campaign_config["target_audience"]["age_min"]
        )
    }
    
    # Predicción de métricas (dummy en modo dormant)
    if ml_bridge.dummy_mode:
        prediction = {
            "expected_ctr": random.uniform(0.8, 3.2),
            "expected_cpm": random.uniform(8.0, 25.0),
            "expected_video_view_rate": random.uniform(0.25, 0.75),
            "performance_score": random.uniform(6.0, 9.5),
            "recommendation": "high_potential" if random.random() > 0.3 else "needs_optimization"
        }
    else:
        prediction = await ml_bridge.predict_campaign_performance(campaign_features)
    
    return prediction
```

### Con Analytics Dashboard
```python
# Dashboard de Meta Ads integrado
async def render_meta_ads_dashboard():
    import streamlit as st
    import plotly.express as px
    
    st.title("📊 Meta Ads Dashboard")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    # Obtener métricas de todas las campañas
    campaigns_summary = await ads_manager.get_campaigns_summary()
    
    with col1:
        st.metric(
            "Active Campaigns", 
            campaigns_summary["active_campaigns"],
            delta=campaigns_summary["campaigns_change_24h"]
        )
    
    with col2:
        st.metric(
            "Total Spend (30d)", 
            f"${campaigns_summary['total_spend_30d']:,.2f}",
            delta=f"${campaigns_summary['spend_change_30d']:,.2f}"
        )
    
    with col3:
        st.metric(
            "Avg CTR",
            f"{campaigns_summary['avg_ctr']:.2f}%",
            delta=f"{campaigns_summary['ctr_change']:.2f}%"
        )
    
    with col4:
        st.metric(
            "ROAS",
            f"{campaigns_summary['roas']:.2f}x",
            delta=f"{campaigns_summary['roas_change']:.2f}x"
        )
    
    # Gráfico de performance por campaña
    st.subheader("Campaign Performance")
    
    campaigns_data = await ads_manager.get_campaigns_analytics(days=30)
    
    fig = px.scatter(
        campaigns_data,
        x="spend",
        y="video_views", 
        size="impressions",
        color="ctr",
        hover_data=["campaign_name", "cpm"],
        title="Campaign Performance Matrix"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de campañas
    st.subheader("Campaigns Overview")
    st.dataframe(
        campaigns_data[["campaign_name", "status", "daily_budget", "spend", "ctr", "cpm"]],
        use_container_width=True
    )
```

## 📈 Métricas y KPIs

### KPIs Meta Ads
- **Return on Ad Spend (ROAS)**: Retorno por gasto publicitario (target: >3.0x)
- **Cost Per Video View**: Costo por visualización de video (target: <$0.05)
- **Click-Through Rate (CTR)**: Tasa de clics (target: >1.5%)
- **Cost Per Mille (CPM)**: Costo por mil impresiones (target: <$15)

### Analytics Automáticos
```python
# Reportes automáticos de Meta Ads
async def generate_meta_ads_report():
    report_data = {
        "performance_overview": {
            "total_campaigns": await ads_manager.count_active_campaigns(),
            "total_spend_30d": await ads_manager.get_total_spend(days=30),
            "total_impressions": await ads_manager.get_total_impressions(days=30),
            "total_video_views": await ads_manager.get_total_video_views(days=30)
        },
        
        "efficiency_metrics": {
            "avg_ctr": await ads_manager.get_average_ctr(days=30),
            "avg_cpm": await ads_manager.get_average_cpm(days=30),
            "avg_video_view_rate": await ads_manager.get_average_video_view_rate(days=30),
            "roas": await ads_manager.calculate_roas(days=30)
        },
        
        "top_performers": {
            "best_campaigns": await ads_manager.get_top_campaigns(metric="roas", limit=5),
            "best_audiences": await ads_manager.get_top_audiences(metric="ctr", limit=5),
            "best_creatives": await ads_manager.get_top_creatives(metric="video_view_rate", limit=5)
        },
        
        "optimization_opportunities": {
            "underperforming_campaigns": await ads_manager.get_underperforming_campaigns(),
            "budget_reallocation": await ads_manager.suggest_budget_reallocation(),
            "audience_expansion": await ads_manager.suggest_audience_expansion()
        }
    }
    
    return report_data

# Alertas automáticas
class MetaAdsAlertSystem:
    async def check_performance_alerts(self):
        alerts = []
        
        # Alerta: ROAS muy bajo
        campaigns_roas = await ads_manager.get_campaigns_roas()
        low_roas_campaigns = [c for c in campaigns_roas if c['roas'] < 1.5]
        
        if low_roas_campaigns:
            alerts.append({
                "type": "low_roas",
                "severity": "high",
                "message": f"{len(low_roas_campaigns)} campaigns with ROAS < 1.5x",
                "campaigns": [c['name'] for c in low_roas_campaigns]
            })
        
        # Alerta: Presupuesto agotándose rápido
        budget_usage = await ads_manager.get_budget_usage_rate()
        if budget_usage > 0.8:  # 80% del presupuesto usado
            alerts.append({
                "type": "budget_depletion",
                "severity": "medium", 
                "message": f"Budget {budget_usage:.1%} depleted",
                "action": "consider_budget_increase"
            })
        
        return alerts
```

## 💡 Buenas Prácticas

### 1. Gestión de Presupuestos
```python
# Distribución inteligente de presupuesto
class BudgetOptimizer:
    def __init__(self, total_budget):
        self.total_budget = total_budget
        self.allocation_rules = {
            "min_campaign_budget": 20.00,
            "max_campaign_budget": self.total_budget * 0.4,
            "performance_based_allocation": 0.7,  # 70% basado en performance
            "exploration_allocation": 0.3         # 30% para nuevas campañas
        }
    
    async def optimize_allocation(self, campaigns):
        """Optimizar distribución de presupuesto"""
        
        # Calcular performance score para cada campaña
        performance_scores = {}
        for campaign in campaigns:
            analytics = await ads_manager.get_campaign_analytics(
                campaign['id'], date_range="last_7_days"
            )
            
            # Score basado en ROAS, CTR y video view rate
            roas_score = min(analytics.get('roas', 0) / 4.0, 1.0)  # Normalizar a 1
            ctr_score = min(analytics.get('ctr', 0) / 2.0, 1.0)
            vvr_score = analytics.get('video_view_rate', 0)
            
            performance_scores[campaign['id']] = {
                'score': (roas_score * 0.5 + ctr_score * 0.3 + vvr_score * 0.2),
                'campaign': campaign
            }
        
        # Ordenar por performance
        sorted_campaigns = sorted(
            performance_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Asignar presupuestos
        performance_budget = self.total_budget * self.allocation_rules['performance_based_allocation']
        exploration_budget = self.total_budget * self.allocation_rules['exploration_allocation']
        
        allocations = {}
        
        # Asignación basada en performance (70%)
        total_performance_score = sum(p[1]['score'] for p in sorted_campaigns)
        
        for campaign_id, perf_data in sorted_campaigns:
            if total_performance_score > 0:
                performance_allocation = (
                    performance_budget * perf_data['score'] / total_performance_score
                )
            else:
                performance_allocation = performance_budget / len(sorted_campaigns)
            
            # Aplicar límites mín/máx
            allocation = max(
                self.allocation_rules['min_campaign_budget'],
                min(performance_allocation, self.allocation_rules['max_campaign_budget'])
            )
            
            allocations[campaign_id] = allocation
        
        # Distribuir presupuesto de exploración uniformemente
        exploration_per_campaign = exploration_budget / len(campaigns)
        
        for campaign_id in allocations:
            allocations[campaign_id] += exploration_per_campaign
        
        return allocations

# Testing A/B automático
class AutomatedABTesting:
    async def create_ab_test(self, base_campaign_config, test_variations):
        """Crear test A/B automático"""
        
        # Crear campaña control (A)
        control_campaign = await ads_manager.create_campaign({
            **base_campaign_config,
            "name": f"{base_campaign_config['name']} - Control"
        })
        
        # Crear variaciones (B, C, etc.)
        test_campaigns = []
        
        for i, variation in enumerate(test_variations):
            variant_config = {**base_campaign_config, **variation}
            variant_config["name"] = f"{base_campaign_config['name']} - Variant {chr(66+i)}"
            
            variant_campaign = await ads_manager.create_campaign(variant_config)
            test_campaigns.append(variant_campaign)
        
        # Configurar monitoreo automático
        ab_test = {
            "test_id": f"ab_test_{int(time.time())}",
            "control": control_campaign,
            "variants": test_campaigns,
            "start_time": datetime.now(),
            "duration_days": 7,
            "success_metric": "ctr",  # Métrica principal para determinar ganador
            "min_statistical_significance": 0.95
        }
        
        # Programar evaluación automática
        await self.schedule_ab_evaluation(ab_test)
        
        return ab_test
    
    async def evaluate_ab_test(self, ab_test):
        """Evaluar resultados de test A/B"""
        
        # Obtener métricas de control y variantes
        control_metrics = await ads_manager.get_campaign_analytics(
            ab_test['control']['id'],
            date_range=f"last_{ab_test['duration_days']}_days"
        )
        
        variant_metrics = []
        for variant in ab_test['variants']:
            metrics = await ads_manager.get_campaign_analytics(
                variant['id'],
                date_range=f"last_{ab_test['duration_days']}_days"
            )
            variant_metrics.append(metrics)
        
        # Determinar ganador estadísticamente significativo
        success_metric = ab_test['success_metric']
        control_value = control_metrics[success_metric]
        
        best_variant = None
        best_improvement = 0
        
        for i, variant_metric in enumerate(variant_metrics):
            variant_value = variant_metric[success_metric]
            improvement = (variant_value - control_value) / control_value
            
            # Verificar significancia estadística (simplificado)
            if improvement > best_improvement and improvement > 0.1:  # Mín 10% mejora
                best_variant = ab_test['variants'][i]
                best_improvement = improvement
        
        # Implementar ganador automáticamente
        if best_variant:
            await self.implement_winning_variant(ab_test, best_variant)
            
            return {
                "winner": best_variant,
                "improvement": best_improvement,
                "implemented": True
            }
        else:
            return {
                "winner": None,
                "improvement": 0,
                "implemented": False,
                "message": "No statistically significant improvement found"
            }
```

### 2. Targeting Avanzado
```python
# Sistema de targeting inteligente
class IntelligentTargeting:
    def __init__(self):
        self.audience_segments = {
            "viral_content_consumers": {
                "interests": ["viral videos", "social media", "entertainment"],
                "behaviors": ["heavy_social_media_users"],
                "age_range": (16, 35)
            },
            "content_creators": {
                "interests": ["content creation", "digital marketing", "entrepreneurship"],
                "behaviors": ["small_business_owners", "creative_professionals"],
                "age_range": (22, 45)
            },
            "brand_enthusiasts": {
                "custom_audiences": ["website_visitors", "email_subscribers"],
                "lookalike_audiences": ["high_value_customers"]
            }
        }
    
    async def create_layered_targeting(self, base_audience, expansion_layers):
        """Crear targeting en capas para máximo alcance"""
        
        # Capa 1: Core audience (más restrictivo)
        core_targeting = {
            **base_audience,
            "name": "Core Audience",
            "estimated_reach": await ads_manager.estimate_audience_size(base_audience)
        }
        
        # Capa 2: Expanded audience (menos restrictivo)
        expanded_audience = {**base_audience}
        
        for layer in expansion_layers:
            if layer == "age_expansion":
                expanded_audience["age_min"] = max(18, expanded_audience["age_min"] - 3)
                expanded_audience["age_max"] = min(65, expanded_audience["age_max"] + 5)
            
            elif layer == "interest_expansion":
                # Añadir intereses relacionados
                related_interests = await ads_manager.get_related_interests(
                    base_audience["interests"]
                )
                expanded_audience["interests"].extend(related_interests[:5])
            
            elif layer == "lookalike_expansion":
                # Añadir lookalike audiences
                expanded_audience["lookalike_audiences"] = [
                    {"source": "website_visitors", "ratio": 0.05}
                ]
        
        expanded_targeting = {
            **expanded_audience,
            "name": "Expanded Audience", 
            "estimated_reach": await ads_manager.estimate_audience_size(expanded_audience)
        }
        
        return [core_targeting, expanded_targeting]
    
    async def create_sequential_targeting(self, funnel_stages):
        """Crear targeting secuencial para funnel completo"""
        
        sequential_campaigns = []
        
        for stage in funnel_stages:
            stage_config = {
                "name": f"Funnel Stage: {stage['name']}",
                "objective": stage["objective"],
                "target_audience": stage["audience"],
                "budget_daily": stage["budget"],
                
                # Configuración específica por etapa del funnel
                "optimization_goal": stage.get("optimization_goal"),
                "conversion_specs": stage.get("conversion_specs", []),
                
                # Exclusiones para evitar overlap
                "exclusions": {
                    "custom_audiences": stage.get("exclude_audiences", [])
                }
            }
            
            campaign = await ads_manager.create_campaign(stage_config)
            sequential_campaigns.append(campaign)
        
        return sequential_campaigns
```

### 3. Creative Optimization
```python
# Optimización de creatividades
class CreativeOptimizer:
    async def generate_creative_variations(self, base_creative, variation_types):
        """Generar variaciones de creatividad automáticamente"""
        
        variations = []
        
        for variation_type in variation_types:
            if variation_type == "message_variations":
                # Variaciones de mensaje
                message_variants = [
                    "🔥 Este video está arrasando en redes sociales",
                    "✨ Contenido viral que no puedes perderte",
                    "🚀 Únete a millones que ya lo vieron",
                    "💎 Descubre por qué todos hablan de esto"
                ]
                
                for message in message_variants:
                    variation = {
                        **base_creative,
                        "object_story_spec": {
                            **base_creative["object_story_spec"],
                            "video_data": {
                                **base_creative["object_story_spec"]["video_data"],
                                "message": message
                            }
                        },
                        "name": f"{base_creative['name']} - Message Var {len(variations)+1}"
                    }
                    variations.append(variation)
            
            elif variation_type == "cta_variations":
                # Variaciones de CTA
                cta_variants = ["WATCH_MORE", "LEARN_MORE", "SIGN_UP", "DOWNLOAD"]
                
                for cta in cta_variants:
                    variation = {
                        **base_creative,
                        "object_story_spec": {
                            **base_creative["object_story_spec"],
                            "video_data": {
                                **base_creative["object_story_spec"]["video_data"],
                                "call_to_action": {"type": cta}
                            }
                        },
                        "name": f"{base_creative['name']} - CTA {cta}"
                    }
                    variations.append(variation)
        
        return variations
    
    async def test_creative_performance(self, creative_variations, test_budget):
        """Test de performance de creatividades"""
        
        # Distribuir presupuesto entre variaciones
        budget_per_creative = test_budget / len(creative_variations)
        
        test_results = []
        
        for creative in creative_variations:
            # Crear ad set específico para esta creatividad
            adset_config = {
                "name": f"Creative Test - {creative['name']}",
                "daily_budget": budget_per_creative,
                "targeting": {
                    "age_min": 18, "age_max": 45,
                    "interests": [{"name": "Social media"}]
                },
                "optimization_goal": "VIDEO_VIEWS"
            }
            
            adset = await ads_manager.create_ad_set(adset_config)
            
            # Crear anuncio con esta creatividad
            ad_config = {
                "name": f"Ad - {creative['name']}",
                "adset_id": adset['id'],
                "creative": creative
            }
            
            ad = await ads_manager.create_ad(ad_config)
            
            test_results.append({
                "creative": creative,
                "adset": adset,
                "ad": ad
            })
        
        return test_results
```

## 🚀 Activación del Sistema

### Checklist para Salir de Modo Dormant

- [ ] 🔑 Configurar Meta Business Manager y obtener tokens de API
- [ ] 💰 Configurar método de pago y presupuestos iniciales
- [ ] 📊 Configurar Facebook Pixel para tracking de conversiones
- [ ] 🎯 Crear audiencias base y lookalike audiences iniciales
- [ ] 📱 Configurar páginas de Facebook e Instagram
- [ ] 🎨 Preparar creatividades y assets para anuncios
- [ ] 📈 Implementar tracking de conversiones y eventos
- [ ] 🧪 Ejecutar campañas de prueba con presupuesto mínimo

### Comando de Activación
```python
# Activar Meta Ads integration
ads_manager = MetaAdsManager(
    access_token="your_real_token",
    ad_account_id="act_your_account_id",
    dummy_mode=False
)

# Health check completo
health = await ads_manager.system_health_check()
print(f"Meta Ads Ready: {health['ready']}")
print(f"Account access: {health['account_access']}")
print(f"API permissions: {health['permissions']}")
```

---

## 📞 Soporte

- **API Issues**: Problemas con Meta Business API y autenticación
- **Campaign Setup**: Configuración de campañas y targeting
- **Performance**: Optimización de ROAS y métricas
- **Integration**: Conexión con otros sistemas y analytics