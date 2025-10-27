"""
🎯 Meta Ads €400 Landing Page Generator + UTM Tracking
Sistema automático que genera landing pages desde campañas Meta Ads con UTM tracking completo
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import httpx
import asyncio
import logging
from datetime import datetime
import json
import os
from jinja2 import Template
import aiofiles
import uuid

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Meta Ads Landing Page Generator",
    description="Genera landing pages automáticas desde campañas Meta Ads con UTM tracking",
    version="1.0.0"
)

# URLs de servicios
ML_CORE_URL = os.getenv("ML_CORE_URL", "http://ml-core:8000")
RAILWAY_BASE_URL = os.getenv("RAILWAY_STATIC_URL", "https://meta-ads-centric.railway.app")
DUMMY_MODE = os.getenv("DUMMY_MODE", "true").lower() == "true"

# ============================================
# MODELOS DE DATOS
# ============================================

class MetaCampaignData(BaseModel):
    campaign_id: str
    campaign_name: str
    artist_name: str
    song_name: str
    budget_euros: float = 400.0
    genre: str = "pop"
    target_countries: List[str] = ["ES", "MX", "US"]
    youtube_channel: Optional[str] = None
    landing_page_template: str = "music_release"
    auto_approve_budget: float = 50.0  # Auto-aprobar hasta €50 de ajustes

class LandingPageRequest(BaseModel):
    campaign_data: MetaCampaignData
    utm_source: str = "meta_ads"
    utm_medium: str = "social"
    utm_campaign: str
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None

class UTMTrackingData(BaseModel):
    page_id: str
    utm_params: Dict[str, str]
    visitor_data: Dict[str, Any]
    conversion_events: List[Dict[str, Any]] = []
    revenue_attribution: float = 0.0

class MLAuthorizationRequest(BaseModel):
    campaign_id: str
    decision_type: str  # "budget_increase", "platform_expansion", "content_optimization"
    current_performance: Dict[str, Any]
    recommended_action: Dict[str, Any]
    cost_impact_euros: float
    confidence_score: float
    urgency_level: str  # "low", "medium", "high", "critical"

# ============================================
# LANDING PAGE GENERATOR
# ============================================

class LandingPageGenerator:
    """Generador automático de landing pages para campañas Meta Ads"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.pages_dir = "generated_pages"
        os.makedirs(self.pages_dir, exist_ok=True)
    
    def _load_templates(self) -> Dict[str, str]:
        """Cargar templates de landing pages"""
        
        music_template = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ artist_name }} - {{ song_name }} | Nuevo Lanzamiento</title>
    
    <!-- Meta Tags para SEO -->
    <meta name="description" content="Escucha {{ song_name }} de {{ artist_name }}. Disponible en todas las plataformas digitales.">
    <meta name="keywords" content="{{ artist_name }}, {{ song_name }}, {{ genre }}, música, streaming">
    
    <!-- Open Graph para redes sociales -->
    <meta property="og:title" content="{{ artist_name }} - {{ song_name }}">
    <meta property="og:description" content="Nuevo lanzamiento disponible en todas las plataformas">
    <meta property="og:type" content="music.song">
    <meta property="og:url" content="{{ page_url }}">
    
    <!-- UTM Tracking -->
    <script>
        // Capturar UTM parameters
        const urlParams = new URLSearchParams(window.location.search);
        const utmData = {
            utm_source: urlParams.get('utm_source'),
            utm_medium: urlParams.get('utm_medium'),
            utm_campaign: urlParams.get('utm_campaign'),
            utm_content: urlParams.get('utm_content'),
            utm_term: urlParams.get('utm_term'),
            page_id: '{{ page_id }}',
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent,
            referrer: document.referrer
        };
        
        // Enviar datos de tracking
        fetch('/api/utm/track', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(utmData)
        });
    </script>
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        
        .hero {
            padding: 80px 0;
        }
        
        .artist-name {
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .song-title {
            font-size: 2.5rem;
            margin-bottom: 30px;
            color: #FFD700;
        }
        
        .genre-tag {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 25px;
            margin-bottom: 40px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .streaming-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin: 40px 0;
        }
        
        .stream-btn {
            display: inline-block;
            padding: 15px 30px;
            background: #1DB954;
            color: white;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            transition: all 0.3s ease;
            min-width: 200px;
        }
        
        .stream-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }
        
        .stream-btn.spotify { background: #1DB954; }
        .stream-btn.apple { background: #000000; }
        .stream-btn.youtube { background: #FF0000; }
        .stream-btn.amazon { background: #FF9900; }
        
        .social-links {
            margin: 60px 0;
        }
        
        .social-btn {
            display: inline-block;
            width: 50px;
            height: 50px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
            margin: 0 10px;
            line-height: 50px;
            text-decoration: none;
            color: white;
            transition: all 0.3s ease;
        }
        
        .social-btn:hover {
            background: rgba(255,255,255,0.3);
            transform: scale(1.1);
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin: 40px 0;
            flex-wrap: wrap;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #FFD700;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .artist-name { font-size: 2rem; }
            .song-title { font-size: 1.8rem; }
            .streaming-buttons { flex-direction: column; align-items: center; }
            .stats { flex-direction: column; gap: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1 class="artist-name">{{ artist_name }}</h1>
            <h2 class="song-title">{{ song_name }}</h2>
            <span class="genre-tag">{{ genre }}</span>
            
            <div class="streaming-buttons">
                <a href="{{ youtube_url }}?utm_source=landing&utm_medium=button&utm_campaign={{ campaign_id }}" 
                   class="stream-btn youtube" onclick="trackConversion('youtube_click')">
                   ▶ YouTube
                </a>
                <a href="https://open.spotify.com/search/{{ artist_name }}%20{{ song_name }}?utm_source=landing&utm_medium=button&utm_campaign={{ campaign_id }}" 
                   class="stream-btn spotify" onclick="trackConversion('spotify_click')">
                   🎵 Spotify
                </a>
                <a href="https://music.apple.com/search?term={{ artist_name }}%20{{ song_name }}&utm_source=landing&utm_medium=button&utm_campaign={{ campaign_id }}" 
                   class="stream-btn apple" onclick="trackConversion('apple_click')">
                   🍎 Apple Music
                </a>
                <a href="https://music.amazon.com/search/{{ artist_name }}%20{{ song_name }}?utm_source=landing&utm_medium=button&utm_campaign={{ campaign_id }}" 
                   class="stream-btn amazon" onclick="trackConversion('amazon_click')">
                   📦 Amazon Music
                </a>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number" id="plays-counter">0</div>
                    <div class="stat-label">Reproducciones</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="fans-counter">0</div>
                    <div class="stat-label">Fans</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="countries-counter">{{ target_countries|length }}</div>
                    <div class="stat-label">Países</div>
                </div>
            </div>
            
            <div class="social-links">
                <a href="https://instagram.com/{{ artist_name|lower|replace(' ', '') }}?utm_source=landing&utm_medium=social&utm_campaign={{ campaign_id }}" 
                   class="social-btn" onclick="trackConversion('instagram_follow')">📷</a>
                <a href="https://tiktok.com/@{{ artist_name|lower|replace(' ', '') }}?utm_source=landing&utm_medium=social&utm_campaign={{ campaign_id }}" 
                   class="social-btn" onclick="trackConversion('tiktok_follow')">🎵</a>
                <a href="https://twitter.com/{{ artist_name|lower|replace(' ', '') }}?utm_source=landing&utm_medium=social&utm_campaign={{ campaign_id }}" 
                   class="social-btn" onclick="trackConversion('twitter_follow')">🐦</a>
            </div>
        </div>
    </div>
    
    <script>
        // Tracking de conversiones
        function trackConversion(action) {
            fetch('/api/utm/convert', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    page_id: '{{ page_id }}',
                    action: action,
                    timestamp: new Date().toISOString(),
                    utm_campaign: '{{ campaign_id }}'
                })
            });
        }
        
        // Animación de contadores
        function animateCounter(id, target, duration = 2000) {
            const element = document.getElementById(id);
            const start = 0;
            const increment = target / (duration / 16);
            let current = start;
            
            const timer = setInterval(() => {
                current += increment;
                element.textContent = Math.floor(current).toLocaleString();
                
                if (current >= target) {
                    element.textContent = target.toLocaleString();
                    clearInterval(timer);
                }
            }, 16);
        }
        
        // Inicializar contadores con datos simulados
        setTimeout(() => {
            animateCounter('plays-counter', {{ estimated_plays }});
            animateCounter('fans-counter', {{ estimated_fans }});
        }, 500);
        
        // Tracking de tiempo en página
        let startTime = Date.now();
        window.addEventListener('beforeunload', () => {
            const timeSpent = Date.now() - startTime;
            navigator.sendBeacon('/api/utm/time-spent', JSON.stringify({
                page_id: '{{ page_id }}',
                time_spent_ms: timeSpent,
                utm_campaign: '{{ campaign_id }}'
            }));
        });
    </script>
</body>
</html>
        """
        
        return {
            "music_release": music_template
        }
    
    async def generate_landing_page(self, request: LandingPageRequest) -> Dict[str, Any]:
        """Generar landing page automática desde campaña Meta Ads"""
        
        try:
            campaign = request.campaign_data
            page_id = str(uuid.uuid4())
            
            # Generar URL de la página
            page_url = f"{RAILWAY_BASE_URL}/landing/{page_id}"
            
            # Preparar datos para el template
            template_data = {
                "artist_name": campaign.artist_name,
                "song_name": campaign.song_name,
                "genre": campaign.genre,
                "campaign_id": campaign.campaign_id,
                "page_id": page_id,
                "page_url": page_url,
                "youtube_url": campaign.youtube_channel or f"https://youtube.com/results?search_query={campaign.artist_name}+{campaign.song_name}",
                "target_countries": campaign.target_countries,
                "estimated_plays": self._estimate_plays(campaign.budget_euros, campaign.genre),
                "estimated_fans": self._estimate_fans(campaign.budget_euros, campaign.genre)
            }
            
            # Generar HTML desde template
            template = Template(self.templates[campaign.landing_page_template])
            html_content = template.render(**template_data)
            
            # Guardar página generada
            page_path = f"{self.pages_dir}/{page_id}.html"
            async with aiofiles.open(page_path, 'w', encoding='utf-8') as f:
                await f.write(html_content)
            
            # Crear UTM tracking
            utm_data = UTMTrackingData(
                page_id=page_id,
                utm_params={
                    "utm_source": request.utm_source,
                    "utm_medium": request.utm_medium,
                    "utm_campaign": request.utm_campaign,
                    "utm_content": request.utm_content,
                    "utm_term": request.utm_term
                },
                visitor_data={
                    "campaign_id": campaign.campaign_id,
                    "budget_euros": campaign.budget_euros,
                    "created_at": datetime.now().isoformat()
                }
            )
            
            # Guardar datos de tracking
            await self._save_utm_data(utm_data)
            
            logger.info(f"Landing page generated: {page_url}")
            
            return {
                "page_id": page_id,
                "page_url": page_url,
                "utm_tracking": utm_data.dict(),
                "template_data": template_data,
                "file_path": page_path
            }
            
        except Exception as e:
            logger.error(f"Landing page generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _estimate_plays(self, budget: float, genre: str) -> int:
        """Estimar reproducciones basado en presupuesto y género"""
        
        genre_multipliers = {
            "pop": 1.2,
            "reggaeton": 1.5,
            "hip_hop": 1.3,
            "electronic": 1.1,
            "rock": 0.9,
            "latin": 1.4
        }
        
        base_plays = budget * 150  # €1 = ~150 plays aproximadamente
        multiplier = genre_multipliers.get(genre, 1.0)
        
        return int(base_plays * multiplier)
    
    def _estimate_fans(self, budget: float, genre: str) -> int:
        """Estimar nuevos fans basado en presupuesto"""
        
        return int(self._estimate_plays(budget, genre) * 0.05)  # 5% conversion rate
    
    async def _save_utm_data(self, utm_data: UTMTrackingData):
        """Guardar datos de UTM tracking"""
        
        tracking_path = f"utm_tracking/{utm_data.page_id}.json"
        os.makedirs(os.path.dirname(tracking_path), exist_ok=True)
        
        async with aiofiles.open(tracking_path, 'w') as f:
            await f.write(utm_data.json(indent=2))

# Instanciar generador
landing_generator = LandingPageGenerator()

# ============================================
# SISTEMA DE AUTORIZACIÓN ML
# ============================================

class MLAuthorizationSystem:
    """Sistema de autorización inteligente para decisiones ML"""
    
    def __init__(self):
        self.pending_authorizations = {}
        self.auto_approve_threshold = 50.0  # €50 auto-aprobación
        
    async def request_authorization(self, auth_request: MLAuthorizationRequest) -> Dict[str, Any]:
        """Solicitar autorización para decisión ML"""
        
        # Auto-aprobar si está bajo el threshold y alta confianza
        if (auth_request.cost_impact_euros <= self.auto_approve_threshold and 
            auth_request.confidence_score >= 0.8):
            
            logger.info(f"Auto-approved: {auth_request.decision_type} - €{auth_request.cost_impact_euros}")
            
            return {
                "authorization_id": str(uuid.uuid4()),
                "status": "auto_approved",
                "decision": "approved",
                "reason": f"Auto-approved: bajo threshold €{self.auto_approve_threshold} y alta confianza {auth_request.confidence_score:.2f}",
                "timestamp": datetime.now().isoformat(),
                "action": auth_request.recommended_action
            }
        
        # Solicitar autorización manual
        auth_id = str(uuid.uuid4())
        
        authorization_data = {
            "id": auth_id,
            "request": auth_request.dict(),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now().timestamp() + 3600),  # 1 hora para decidir
            "risk_level": self._calculate_risk_level(auth_request),
            "recommendation": self._generate_recommendation(auth_request)
        }
        
        self.pending_authorizations[auth_id] = authorization_data
        
        # Enviar notificación (dashboard/email/etc)
        await self._notify_authorization_needed(authorization_data)
        
        return {
            "authorization_id": auth_id,
            "status": "pending_approval",
            "estimated_response_time": "5-15 minutes",
            "dashboard_url": f"{RAILWAY_BASE_URL}/dashboard/authorizations/{auth_id}",
            "risk_level": authorization_data["risk_level"],
            "recommendation": authorization_data["recommendation"]
        }
    
    def _calculate_risk_level(self, request: MLAuthorizationRequest) -> str:
        """Calcular nivel de riesgo de la decisión"""
        
        if request.cost_impact_euros > 100:
            return "high"
        elif request.confidence_score < 0.6:
            return "medium"
        elif request.urgency_level == "critical":
            return "high"
        else:
            return "low"
    
    def _generate_recommendation(self, request: MLAuthorizationRequest) -> str:
        """Generar recomendación para el usuario"""
        
        recommendations = {
            "budget_increase": f"Incrementar presupuesto en €{request.cost_impact_euros:.2f} basado en performance {request.confidence_score:.2f}",
            "platform_expansion": f"Expandir a nuevas plataformas con inversión €{request.cost_impact_euros:.2f}",
            "content_optimization": f"Optimizar contenido con coste €{request.cost_impact_euros:.2f}"
        }
        
        return recommendations.get(request.decision_type, "Revisar manualmente")
    
    async def _notify_authorization_needed(self, auth_data: Dict[str, Any]):
        """Notificar que se necesita autorización"""
        
        # En producción: enviar email, push notification, etc.
        logger.info(f"Authorization needed: {auth_data['id']}")
        
        # Aquí integrarías con tu sistema de notificaciones
        # - Discord webhook
        # - Email notification  
        # - Dashboard alert
        # - Push notification

# Instanciar sistema de autorización
auth_system = MLAuthorizationSystem()

# ============================================
# ENDPOINTS API
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "meta-ads-landing-generator",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/webhook/meta-ads")
async def meta_ads_webhook(request: Request):
    """Webhook para recibir campañas Meta Ads y generar landing pages automáticas"""
    
    try:
        # Obtener datos del webhook de Meta
        webhook_data = await request.json()
        
        # Extraer datos de la campaña (adaptado para Meta Ads API)
        campaign_data = MetaCampaignData(
            campaign_id=webhook_data.get("campaign_id", str(uuid.uuid4())),
            campaign_name=webhook_data.get("campaign_name", "Nueva Campaña"),
            artist_name=webhook_data.get("artist_name", "Artista"),
            song_name=webhook_data.get("song_name", "Nueva Canción"),
            budget_euros=webhook_data.get("daily_budget", 400.0),
            genre=webhook_data.get("genre", "pop"),
            target_countries=webhook_data.get("target_countries", ["ES", "MX"]),
            youtube_channel=webhook_data.get("youtube_channel")
        )
        
        # Generar UTM campaign
        utm_campaign = f"{campaign_data.artist_name}_{campaign_data.song_name}_{campaign_data.campaign_id}".replace(" ", "_").lower()
        
        # Crear request para landing page
        landing_request = LandingPageRequest(
            campaign_data=campaign_data,
            utm_campaign=utm_campaign,
            utm_content=f"{campaign_data.genre}_music_release"
        )
        
        # Generar landing page automáticamente
        landing_result = await landing_generator.generate_landing_page(landing_request)
        
        # Trigger análisis ML (Ultralytics + análisis musical)
        ml_analysis = await _trigger_ml_analysis(campaign_data)
        
        # Solicitar autorización para optimizaciones ML si es necesario
        if ml_analysis.get("requires_authorization"):
            auth_request = MLAuthorizationRequest(
                campaign_id=campaign_data.campaign_id,
                decision_type="content_optimization",
                current_performance=ml_analysis.get("current_metrics", {}),
                recommended_action=ml_analysis.get("recommendations", {}),
                cost_impact_euros=ml_analysis.get("optimization_cost", 25.0),
                confidence_score=ml_analysis.get("confidence", 0.85),
                urgency_level="medium"
            )
            
            auth_result = await auth_system.request_authorization(auth_request)
            ml_analysis["authorization"] = auth_result
        
        return {
            "success": True,
            "campaign_id": campaign_data.campaign_id,
            "landing_page": landing_result,
            "ml_analysis": ml_analysis,
            "railway_deployment": f"{RAILWAY_BASE_URL}",
            "dashboard_url": f"{RAILWAY_BASE_URL}/dashboard/campaigns/{campaign_data.campaign_id}",
            "automation_status": "24/7 active"
        }
        
    except Exception as e:
        logger.error(f"Meta Ads webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/landing/{page_id}")
async def serve_landing_page(page_id: str):
    """Servir landing page generada"""
    
    from fastapi.responses import HTMLResponse
    
    try:
        page_path = f"generated_pages/{page_id}.html"
        
        async with aiofiles.open(page_path, 'r', encoding='utf-8') as f:
            html_content = await f.read()
        
        return HTMLResponse(content=html_content)
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Landing page not found")

@app.post("/api/utm/track")
async def track_utm_data(utm_data: Dict[str, Any]):
    """Endpoint para tracking de UTM parameters"""
    
    try:
        # Guardar datos de tracking
        tracking_file = f"utm_tracking/{utm_data.get('page_id')}_visits.json"
        os.makedirs(os.path.dirname(tracking_file), exist_ok=True)
        
        # Cargar datos existentes o crear nuevos
        try:
            async with aiofiles.open(tracking_file, 'r') as f:
                existing_data = json.loads(await f.read())
        except FileNotFoundError:
            existing_data = {"visits": []}
        
        # Añadir nueva visita
        existing_data["visits"].append({
            **utm_data,
            "server_timestamp": datetime.now().isoformat()
        })
        
        # Guardar datos actualizados
        async with aiofiles.open(tracking_file, 'w') as f:
            await f.write(json.dumps(existing_data, indent=2))
        
        return {"success": True, "tracked": True}
        
    except Exception as e:
        logger.error(f"UTM tracking error: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/utm/convert")
async def track_conversion(conversion_data: Dict[str, Any]):
    """Endpoint para tracking de conversiones"""
    
    try:
        page_id = conversion_data.get("page_id")
        conversion_file = f"utm_tracking/{page_id}_conversions.json"
        
        # Cargar conversiones existentes
        try:
            async with aiofiles.open(conversion_file, 'r') as f:
                existing_data = json.loads(await f.read())
        except FileNotFoundError:
            existing_data = {"conversions": []}
        
        # Añadir nueva conversión
        existing_data["conversions"].append({
            **conversion_data,
            "server_timestamp": datetime.now().isoformat(),
            "value": 1.0  # €1 por conversión base
        })
        
        # Guardar datos
        async with aiofiles.open(conversion_file, 'w') as f:
            await f.write(json.dumps(existing_data, indent=2))
        
        return {"success": True, "conversion_tracked": True}
        
    except Exception as e:
        logger.error(f"Conversion tracking error: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/campaign/{campaign_id}/analytics")
async def get_campaign_analytics(campaign_id: str):
    """Obtener analytics completas de campaña con UTM data"""
    
    try:
        # Buscar páginas de la campaña
        analytics = {
            "campaign_id": campaign_id,
            "total_visits": 0,
            "total_conversions": 0,
            "conversion_rate": 0.0,
            "revenue_euros": 0.0,
            "utm_sources": {},
            "platform_performance": {},
            "hourly_traffic": []
        }
        
        # Aquí implementarías la lógica de agregación de UTM data
        # Por simplicidad, retornamos datos mock
        
        if DUMMY_MODE:
            analytics.update({
                "total_visits": 1250,
                "total_conversions": 89,
                "conversion_rate": 7.12,
                "revenue_euros": 156.80,
                "utm_sources": {
                    "meta_ads": 850,
                    "instagram": 200,
                    "youtube": 150,
                    "direct": 50
                },
                "platform_performance": {
                    "spotify_clicks": 234,
                    "youtube_clicks": 189,
                    "apple_clicks": 98,
                    "instagram_follows": 67
                }
            })
        
        return analytics
        
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/authorization/approve/{auth_id}")
async def approve_authorization(auth_id: str, approval_data: Dict[str, Any]):
    """Aprobar/rechazar autorización ML"""
    
    try:
        if auth_id not in auth_system.pending_authorizations:
            raise HTTPException(status_code=404, detail="Authorization not found")
        
        auth_data = auth_system.pending_authorizations[auth_id]
        decision = approval_data.get("decision")  # "approved" or "rejected"
        
        auth_data.update({
            "status": decision,
            "decided_at": datetime.now().isoformat(),
            "decision_reason": approval_data.get("reason", ""),
            "decided_by": approval_data.get("user_id", "dashboard_user")
        })
        
        # Ejecutar acción si fue aprobada
        if decision == "approved":
            await _execute_ml_action(auth_data)
        
        return {
            "success": True,
            "authorization_id": auth_id,
            "decision": decision,
            "executed": decision == "approved"
        }
        
    except Exception as e:
        logger.error(f"Authorization approval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# FUNCIONES AUXILIARES
# ============================================

async def _trigger_ml_analysis(campaign_data: MetaCampaignData) -> Dict[str, Any]:
    """Trigger análisis ML con Ultralytics + análisis musical"""
    
    try:
        if DUMMY_MODE:
            return {
                "analysis_complete": True,
                "ultralytics_score": 0.87,
                "music_genre_confidence": 0.92,
                "virality_prediction": 0.78,
                "requires_authorization": True,
                "recommendations": {
                    "increase_budget": 75.0,
                    "target_platforms": ["tiktok", "youtube_shorts"],
                    "optimal_posting_time": "19:00-21:00"
                },
                "optimization_cost": 35.0,
                "confidence": 0.89
            }
        
        # En producción: llamar a ML Core
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ML_CORE_URL}/analyze-campaign",
                json=campaign_data.dict()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"ML analysis failed: {response.text}")
                return {"analysis_complete": False}
                
    except Exception as e:
        logger.error(f"ML analysis error: {str(e)}")
        return {"analysis_complete": False, "error": str(e)}

async def _execute_ml_action(auth_data: Dict[str, Any]):
    """Ejecutar acción ML aprobada"""
    
    logger.info(f"Executing approved ML action: {auth_data['request']['decision_type']}")
    
    # Aquí implementarías la ejecución real de las acciones ML
    # - Aumentar presupuesto en Meta Ads
    # - Expandir a nuevas plataformas
    # - Optimizar contenido
    # - Ajustar targeting

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8004,
        log_level="info"
    )