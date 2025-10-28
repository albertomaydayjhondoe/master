"""
🎯 Meta Ads €400 Landing Page Generator + UTM Tracking + Supabase Integration
Sistema automático que genera landing pages desde campañas Meta Ads con métricas en Supabase
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
import uuid
from supabase import create_client, Client
import asyncpg
from asyncpg.pool import Pool

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Meta Ads Landing Page Generator + Supabase",
    description="Genera landing pages automáticas desde campañas Meta Ads con métricas en Supabase",
    version="2.0.0"
)

# URLs y configuraciones
ML_CORE_URL = os.getenv("ML_CORE_URL", "http://ml-core:8000")
RAILWAY_BASE_URL = os.getenv("RAILWAY_STATIC_URL", "https://meta-ads-centric.railway.app")
DUMMY_MODE = os.getenv("DUMMY_MODE", "true").lower() == "true"

# Configuración Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "your-supabase-url.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "your-supabase-anon-key")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "your-supabase-service-key")

# Cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Pool de conexiones PostgreSQL para operaciones directas
db_pool: Optional[Pool] = None

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
    auto_approve_budget: float = 50.0

class LandingPageRequest(BaseModel):
    campaign_data: MetaCampaignData
    utm_source: str = "meta_ads"
    utm_medium: str = "social"
    utm_campaign: str
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None

class UTMVisit(BaseModel):
    page_id: str
    campaign_id: str
    utm_source: str
    utm_medium: str
    utm_campaign: str
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None
    visitor_ip: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    country: Optional[str] = None
    device_type: Optional[str] = None
    timestamp: datetime = datetime.now()

class UTMConversion(BaseModel):
    page_id: str
    campaign_id: str
    action_type: str  # 'youtube_click', 'spotify_click', 'instagram_follow', etc.
    platform: str
    conversion_value: float = 1.0
    utm_source: str
    timestamp: datetime = datetime.now()

class CampaignMetrics(BaseModel):
    campaign_id: str
    total_visits: int = 0
    unique_visits: int = 0
    total_conversions: int = 0
    conversion_rate: float = 0.0
    revenue_euros: float = 0.0
    cost_per_conversion: float = 0.0
    roi_percentage: float = 0.0
    updated_at: datetime = datetime.now()

# ============================================
# CONFIGURACIÓN BASE DE DATOS SUPABASE
# ============================================

async def init_database():
    """Inicializar tablas en Supabase si no existen"""
    
    create_tables_sql = [
        """
        -- Tabla de campañas
        CREATE TABLE IF NOT EXISTS campaigns (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            campaign_id VARCHAR UNIQUE NOT NULL,
            campaign_name VARCHAR NOT NULL,
            artist_name VARCHAR NOT NULL,
            song_name VARCHAR NOT NULL,
            budget_euros DECIMAL(10,2) DEFAULT 400.00,
            genre VARCHAR DEFAULT 'pop',
            target_countries TEXT[] DEFAULT '{"ES","MX","US"}',
            youtube_channel VARCHAR,
            landing_page_template VARCHAR DEFAULT 'music_release',
            auto_approve_budget DECIMAL(10,2) DEFAULT 50.00,
            page_id VARCHAR,
            page_url VARCHAR,
            status VARCHAR DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        """
        -- Tabla de visitas UTM
        CREATE TABLE IF NOT EXISTS utm_visits (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            page_id VARCHAR NOT NULL,
            campaign_id VARCHAR NOT NULL,
            utm_source VARCHAR,
            utm_medium VARCHAR,
            utm_campaign VARCHAR,
            utm_content VARCHAR,
            utm_term VARCHAR,
            visitor_ip INET,
            user_agent TEXT,
            referrer TEXT,
            country VARCHAR(2),
            device_type VARCHAR,
            session_id VARCHAR,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
        );
        """,
        
        """
        -- Tabla de conversiones UTM
        CREATE TABLE IF NOT EXISTS utm_conversions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            page_id VARCHAR NOT NULL,
            campaign_id VARCHAR NOT NULL,
            action_type VARCHAR NOT NULL,
            platform VARCHAR NOT NULL,
            conversion_value DECIMAL(10,2) DEFAULT 1.00,
            utm_source VARCHAR,
            utm_medium VARCHAR,
            utm_campaign VARCHAR,
            revenue_attributed DECIMAL(10,2) DEFAULT 0.00,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
        );
        """,
        
        """
        -- Tabla de métricas agregadas por campaña
        CREATE TABLE IF NOT EXISTS campaign_metrics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            campaign_id VARCHAR UNIQUE NOT NULL,
            total_visits INTEGER DEFAULT 0,
            unique_visits INTEGER DEFAULT 0,
            total_conversions INTEGER DEFAULT 0,
            conversion_rate DECIMAL(5,2) DEFAULT 0.00,
            revenue_euros DECIMAL(10,2) DEFAULT 0.00,
            cost_per_conversion DECIMAL(10,2) DEFAULT 0.00,
            roi_percentage DECIMAL(5,2) DEFAULT 0.00,
            avg_session_duration INTEGER DEFAULT 0,
            bounce_rate DECIMAL(5,2) DEFAULT 0.00,
            top_utm_source VARCHAR,
            top_platform VARCHAR,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
        );
        """,
        
        """
        -- Índices para performance
        CREATE INDEX IF NOT EXISTS idx_utm_visits_campaign_id ON utm_visits(campaign_id);
        CREATE INDEX IF NOT EXISTS idx_utm_visits_timestamp ON utm_visits(timestamp);
        CREATE INDEX IF NOT EXISTS idx_utm_conversions_campaign_id ON utm_conversions(campaign_id);
        CREATE INDEX IF NOT EXISTS idx_utm_conversions_timestamp ON utm_conversions(timestamp);
        CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
        """,
        
        """
        -- Función para actualizar métricas automáticamente
        CREATE OR REPLACE FUNCTION update_campaign_metrics(campaign_id_param VARCHAR)
        RETURNS VOID AS $$
        BEGIN
            INSERT INTO campaign_metrics (
                campaign_id, total_visits, unique_visits, total_conversions, 
                conversion_rate, revenue_euros, updated_at
            )
            SELECT 
                campaign_id_param,
                COUNT(*) as total_visits,
                COUNT(DISTINCT visitor_ip) as unique_visits,
                (SELECT COUNT(*) FROM utm_conversions WHERE campaign_id = campaign_id_param) as total_conversions,
                CASE 
                    WHEN COUNT(*) > 0 THEN 
                        ((SELECT COUNT(*) FROM utm_conversions WHERE campaign_id = campaign_id_param) * 100.0 / COUNT(*))
                    ELSE 0 
                END as conversion_rate,
                (SELECT COALESCE(SUM(conversion_value), 0) FROM utm_conversions WHERE campaign_id = campaign_id_param) as revenue_euros,
                NOW()
            FROM utm_visits 
            WHERE campaign_id = campaign_id_param
            ON CONFLICT (campaign_id) 
            DO UPDATE SET
                total_visits = EXCLUDED.total_visits,
                unique_visits = EXCLUDED.unique_visits,
                total_conversions = EXCLUDED.total_conversions,
                conversion_rate = EXCLUDED.conversion_rate,
                revenue_euros = EXCLUDED.revenue_euros,
                updated_at = NOW();
        END;
        $$ LANGUAGE plpgsql;
        """,
        
        """
        -- Triggers para actualización automática de métricas
        CREATE OR REPLACE FUNCTION trigger_update_metrics()
        RETURNS TRIGGER AS $$
        BEGIN
            PERFORM update_campaign_metrics(NEW.campaign_id);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        DROP TRIGGER IF EXISTS update_metrics_on_visit ON utm_visits;
        CREATE TRIGGER update_metrics_on_visit
            AFTER INSERT ON utm_visits
            FOR EACH ROW
            EXECUTE FUNCTION trigger_update_metrics();
            
        DROP TRIGGER IF EXISTS update_metrics_on_conversion ON utm_conversions;
        CREATE TRIGGER update_metrics_on_conversion
            AFTER INSERT ON utm_conversions
            FOR EACH ROW
            EXECUTE FUNCTION trigger_update_metrics();
        """
    ]
    
    try:
        # Ejecutar cada statement SQL
        for sql in create_tables_sql:
            if sql.strip():  # Solo ejecutar si no está vacío
                result = supabase.rpc('exec_sql', {'sql': sql})
                logger.info(f"Database setup completed: {len(create_tables_sql)} statements executed")
                
    except Exception as e:
        logger.warning(f"Database setup via RPC failed: {e}")
        # Fallback: intentar con pool directo si está disponible
        try:
            if db_pool:
                async with db_pool.acquire() as conn:
                    for sql in create_tables_sql:
                        if sql.strip():
                            await conn.execute(sql)
                logger.info("Database setup completed via direct connection")
        except Exception as e2:
            logger.error(f"Database setup failed completely: {e2}")

async def init_db_pool():
    """Inicializar pool de conexiones PostgreSQL directo"""
    global db_pool
    
    try:
        # Extraer configuración de URL de Supabase
        db_url = SUPABASE_URL.replace('https://', '').replace('http://', '')
        
        # En producción, usar DATABASE_URL completa
        database_url = os.getenv("DATABASE_URL") or f"postgresql://postgres:password@db.{db_url}:5432/postgres"
        
        if not DUMMY_MODE:
            db_pool = await asyncpg.create_pool(database_url, min_size=1, max_size=10)
            logger.info("PostgreSQL pool initialized")
        else:
            logger.info("DUMMY_MODE: Skip PostgreSQL pool")
            
    except Exception as e:
        logger.warning(f"PostgreSQL pool initialization failed: {e}")

# ============================================
# SUPABASE OPERATIONS
# ============================================

class SupabaseLandingOperations:
    """Operaciones de landing page con Supabase"""
    
    @staticmethod
    async def save_campaign(campaign_data: MetaCampaignData, page_id: str, page_url: str) -> Dict[str, Any]:
        """Guardar campaña en Supabase"""
        
        try:
            campaign_record = {
                "campaign_id": campaign_data.campaign_id,
                "campaign_name": campaign_data.campaign_name,
                "artist_name": campaign_data.artist_name,
                "song_name": campaign_data.song_name,
                "budget_euros": campaign_data.budget_euros,
                "genre": campaign_data.genre,
                "target_countries": campaign_data.target_countries,
                "youtube_channel": campaign_data.youtube_channel,
                "landing_page_template": campaign_data.landing_page_template,
                "auto_approve_budget": campaign_data.auto_approve_budget,
                "page_id": page_id,
                "page_url": page_url,
                "status": "active"
            }
            
            result = supabase.table("campaigns").insert(campaign_record).execute()
            
            if result.data:
                logger.info(f"Campaign saved to Supabase: {campaign_data.campaign_id}")
                return {"success": True, "campaign": result.data[0]}
            else:
                raise Exception("No data returned from insert")
                
        except Exception as e:
            logger.error(f"Failed to save campaign to Supabase: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def track_visit(visit_data: UTMVisit) -> Dict[str, Any]:
        """Registrar visita UTM en Supabase"""
        
        try:
            visit_record = {
                "page_id": visit_data.page_id,
                "campaign_id": visit_data.campaign_id,
                "utm_source": visit_data.utm_source,
                "utm_medium": visit_data.utm_medium,
                "utm_campaign": visit_data.utm_campaign,
                "utm_content": visit_data.utm_content,
                "utm_term": visit_data.utm_term,
                "visitor_ip": visit_data.visitor_ip,
                "user_agent": visit_data.user_agent,
                "referrer": visit_data.referrer,
                "country": visit_data.country,
                "device_type": visit_data.device_type,
                "timestamp": visit_data.timestamp.isoformat()
            }
            
            result = supabase.table("utm_visits").insert(visit_record).execute()
            
            if result.data:
                logger.info(f"Visit tracked: {visit_data.page_id}")
                return {"success": True, "visit_id": result.data[0]["id"]}
            else:
                raise Exception("No data returned from visit insert")
                
        except Exception as e:
            logger.error(f"Failed to track visit: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def track_conversion(conversion_data: UTMConversion) -> Dict[str, Any]:
        """Registrar conversión UTM en Supabase"""
        
        try:
            conversion_record = {
                "page_id": conversion_data.page_id,
                "campaign_id": conversion_data.campaign_id,
                "action_type": conversion_data.action_type,
                "platform": conversion_data.platform,
                "conversion_value": conversion_data.conversion_value,
                "utm_source": conversion_data.utm_source,
                "timestamp": conversion_data.timestamp.isoformat()
            }
            
            result = supabase.table("utm_conversions").insert(conversion_record).execute()
            
            if result.data:
                logger.info(f"Conversion tracked: {conversion_data.action_type} on {conversion_data.platform}")
                return {"success": True, "conversion_id": result.data[0]["id"]}
            else:
                raise Exception("No data returned from conversion insert")
                
        except Exception as e:
            logger.error(f"Failed to track conversion: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_campaign_analytics(campaign_id: str) -> Dict[str, Any]:
        """Obtener analytics completas de campaña desde Supabase"""
        
        try:
            # Obtener métricas principales
            metrics_result = supabase.table("campaign_metrics").select("*").eq("campaign_id", campaign_id).execute()
            
            if not metrics_result.data:
                # Si no hay métricas, calcular manualmente
                await SupabaseLandingOperations._update_campaign_metrics(campaign_id)
                metrics_result = supabase.table("campaign_metrics").select("*").eq("campaign_id", campaign_id).execute()
            
            # Obtener distribución por UTM source
            utm_sources = supabase.table("utm_visits").select("utm_source").eq("campaign_id", campaign_id).execute()
            
            # Obtener conversiones por plataforma
            platform_conversions = supabase.table("utm_conversions").select("platform, action_type").eq("campaign_id", campaign_id).execute()
            
            # Obtener tráfico por horas
            hourly_traffic = supabase.rpc("get_hourly_traffic", {"campaign_id_param": campaign_id}).execute()
            
            # Compilar analytics
            base_metrics = metrics_result.data[0] if metrics_result.data else {}
            
            # Procesar distribución UTM
            utm_distribution = {}
            if utm_sources.data:
                for visit in utm_sources.data:
                    source = visit["utm_source"] or "direct"
                    utm_distribution[source] = utm_distribution.get(source, 0) + 1
            
            # Procesar conversiones por plataforma
            platform_performance = {}
            if platform_conversions.data:
                for conversion in platform_conversions.data:
                    platform = conversion["platform"]
                    platform_performance[platform] = platform_performance.get(platform, 0) + 1
            
            analytics = {
                "campaign_id": campaign_id,
                "total_visits": base_metrics.get("total_visits", 0),
                "unique_visits": base_metrics.get("unique_visits", 0),
                "total_conversions": base_metrics.get("total_conversions", 0),
                "conversion_rate": float(base_metrics.get("conversion_rate", 0)),
                "revenue_euros": float(base_metrics.get("revenue_euros", 0)),
                "roi_percentage": float(base_metrics.get("roi_percentage", 0)),
                "utm_distribution": utm_distribution,
                "platform_performance": platform_performance,
                "hourly_traffic": hourly_traffic.data if hourly_traffic.data else [],
                "last_updated": base_metrics.get("updated_at"),
                "status": "success"
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get campaign analytics: {e}")
            return {
                "campaign_id": campaign_id,
                "status": "error",
                "error": str(e),
                "total_visits": 0,
                "total_conversions": 0
            }
    
    @staticmethod
    async def _update_campaign_metrics(campaign_id: str):
        """Forzar actualización de métricas de campaña"""
        
        try:
            # Usar función SQL para actualizar métricas
            result = supabase.rpc("update_campaign_metrics", {"campaign_id_param": campaign_id}).execute()
            logger.info(f"Metrics updated for campaign: {campaign_id}")
            
        except Exception as e:
            logger.error(f"Failed to update campaign metrics: {e}")

# ============================================
# LANDING PAGE GENERATOR CON SUPABASE
# ============================================

class SupabaseLandingPageGenerator:
    """Generador de landing pages integrado con Supabase"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.operations = SupabaseLandingOperations()
    
    def _load_templates(self) -> Dict[str, str]:
        """Cargar templates HTML - integrado con Supabase tracking"""
        
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
    
    <!-- Supabase UTM Tracking -->
    <script>
        // Capturar UTM parameters y enviar a Supabase
        const urlParams = new URLSearchParams(window.location.search);
        
        const trackingData = {
            page_id: '{{ page_id }}',
            campaign_id: '{{ campaign_id }}',
            utm_source: urlParams.get('utm_source') || 'direct',
            utm_medium: urlParams.get('utm_medium') || 'none',
            utm_campaign: urlParams.get('utm_campaign') || '{{ campaign_id }}',
            utm_content: urlParams.get('utm_content'),
            utm_term: urlParams.get('utm_term'),
            user_agent: navigator.userAgent,
            referrer: document.referrer,
            timestamp: new Date().toISOString()
        };
        
        // Enviar tracking a Supabase via API
        fetch('/api/supabase/track-visit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(trackingData)
        }).then(response => {
            console.log('Visit tracked in Supabase');
        }).catch(error => {
            console.error('Tracking error:', error);
        });
        
        // Detectar país y device type
        const detectDeviceAndLocation = async () => {
            try {
                // Detectar device type
                const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
                const isTablet = /iPad|Android.*Tablet/i.test(navigator.userAgent);
                let deviceType = 'desktop';
                if (isMobile && !isTablet) deviceType = 'mobile';
                if (isTablet) deviceType = 'tablet';
                
                // Obtener IP y país (opcional - usando servicio público)
                const locationResponse = await fetch('https://ipapi.co/json/');
                const locationData = await locationResponse.json();
                
                // Actualizar tracking con información adicional
                const enhancedTracking = {
                    ...trackingData,
                    device_type: deviceType,
                    country: locationData.country_code,
                    visitor_ip: locationData.ip
                };
                
                fetch('/api/supabase/update-visit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(enhancedTracking)
                });
                
            } catch (error) {
                console.log('Enhanced tracking failed:', error);
            }
        };
        
        // Ejecutar detección después de cargar la página
        window.addEventListener('load', detectDeviceAndLocation);
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
        
        /* Supabase Analytics Badge */
        .analytics-badge {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 0.8rem;
            z-index: 1000;
        }
        
        @media (max-width: 768px) {
            .artist-name { font-size: 2rem; }
            .song-title { font-size: 1.8rem; }
            .streaming-buttons { flex-direction: column; align-items: center; }
            .stats { flex-direction: column; gap: 20px; }
            .analytics-badge { display: none; }
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
                   class="stream-btn youtube" onclick="trackSupabaseConversion('youtube_click')">
                   ▶ YouTube
                </a>
                <a href="https://open.spotify.com/search/{{ artist_name }}%20{{ song_name }}?utm_source=landing&utm_medium=button&utm_campaign={{ campaign_id }}" 
                   class="stream-btn spotify" onclick="trackSupabaseConversion('spotify_click')">
                   🎵 Spotify
                </a>
                <a href="https://music.apple.com/search?term={{ artist_name }}%20{{ song_name }}&utm_source=landing&utm_medium=button&utm_campaign={{ campaign_id }}" 
                   class="stream-btn apple" onclick="trackSupabaseConversion('apple_click')">
                   🍎 Apple Music
                </a>
                <a href="https://music.amazon.com/search/{{ artist_name }}%20{{ song_name }}?utm_source=landing&utm_medium=button&utm_campaign={{ campaign_id }}" 
                   class="stream-btn amazon" onclick="trackSupabaseConversion('amazon_click')">
                   📦 Amazon Music
                </a>
            </div>
            
            <div class="stats" id="real-time-stats">
                <div class="stat-item">
                    <div class="stat-number" id="plays-counter">{{ estimated_plays }}</div>
                    <div class="stat-label">Reproducciones</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="fans-counter">{{ estimated_fans }}</div>
                    <div class="stat-label">Fans</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="visitors-counter">0</div>
                    <div class="stat-label">Visitantes Hoy</div>
                </div>
            </div>
            
            <div class="social-links">
                <a href="https://instagram.com/{{ artist_name|lower|replace(' ', '') }}?utm_source=landing&utm_medium=social&utm_campaign={{ campaign_id }}" 
                   class="social-btn" onclick="trackSupabaseConversion('instagram_follow')">📷</a>
                <a href="https://tiktok.com/@{{ artist_name|lower|replace(' ', '') }}?utm_source=landing&utm_medium=social&utm_campaign={{ campaign_id }}" 
                   class="social-btn" onclick="trackSupabaseConversion('tiktok_follow')">🎵</a>
                <a href="https://twitter.com/{{ artist_name|lower|replace(' ', '') }}?utm_source=landing&utm_medium=social&utm_campaign={{ campaign_id }}" 
                   class="social-btn" onclick="trackSupabaseConversion('twitter_follow')">🐦</a>
            </div>
        </div>
    </div>
    
    <!-- Analytics Badge -->
    <div class="analytics-badge">
        📊 Powered by Supabase Analytics
    </div>
    
    <script>
        // Tracking de conversiones en Supabase
        function trackSupabaseConversion(action) {
            const conversionData = {
                page_id: '{{ page_id }}',
                campaign_id: '{{ campaign_id }}',
                action_type: action,
                platform: action.split('_')[0], // 'youtube', 'spotify', etc.
                conversion_value: 1.0,
                utm_source: new URLSearchParams(window.location.search).get('utm_source') || 'direct',
                timestamp: new Date().toISOString()
            };
            
            fetch('/api/supabase/track-conversion', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(conversionData)
            }).then(response => {
                console.log('Conversion tracked in Supabase:', action);
            }).catch(error => {
                console.error('Conversion tracking error:', error);
            });
        }
        
        // Cargar estadísticas en tiempo real desde Supabase
        const loadRealTimeStats = async () => {
            try {
                const response = await fetch(`/api/campaign/{{ campaign_id }}/analytics`);
                const analytics = await response.json();
                
                // Actualizar contadores con datos reales
                if (analytics.status === 'success') {
                    const visitorsElement = document.getElementById('visitors-counter');
                    if (visitorsElement) {
                        visitorsElement.textContent = analytics.total_visits.toLocaleString();
                    }
                }
                
            } catch (error) {
                console.log('Real-time stats failed:', error);
            }
        };
        
        // Cargar stats cada 30 segundos
        setInterval(loadRealTimeStats, 30000);
        loadRealTimeStats(); // Cargar inmediatamente
        
        // Tracking de tiempo en página para Supabase
        let startTime = Date.now();
        window.addEventListener('beforeunload', () => {
            const timeSpent = Date.now() - startTime;
            
            navigator.sendBeacon('/api/supabase/track-time', JSON.stringify({
                page_id: '{{ page_id }}',
                campaign_id: '{{ campaign_id }}',
                time_spent_ms: timeSpent,
                timestamp: new Date().toISOString()
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
        """Generar landing page automática desde campaña Meta Ads con Supabase"""
        
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
            
            # Guardar campaña en Supabase
            campaign_result = await self.operations.save_campaign(campaign, page_id, page_url)
            
            if not campaign_result["success"]:
                raise Exception(f"Failed to save campaign to Supabase: {campaign_result['error']}")
            
            logger.info(f"Landing page generated with Supabase integration: {page_url}")
            
            return {
                "page_id": page_id,
                "page_url": page_url,
                "campaign_saved": campaign_result["success"],
                "supabase_ready": True,
                "template_data": template_data,
                "html_content": html_content,
                "tracking_endpoints": [
                    "/api/supabase/track-visit",
                    "/api/supabase/track-conversion",
                    "/api/campaign/{campaign_id}/analytics"
                ]
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

# Instanciar generador con Supabase
supabase_landing_generator = SupabaseLandingPageGenerator()

# ============================================
# ENDPOINTS API CON SUPABASE
# ============================================

@app.on_event("startup")
async def startup_event():
    """Inicializar servicios al arrancar"""
    await init_db_pool()
    await init_database()

@app.get("/health")
async def health_check():
    """Health check con estado de Supabase"""
    
    try:
        # Test Supabase connection
        supabase_test = supabase.table("campaigns").select("count").execute()
        supabase_status = "connected"
    except Exception as e:
        supabase_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "service": "meta-ads-supabase-landing-generator",
        "version": "2.0.0",
        "supabase_status": supabase_status,
        "dummy_mode": DUMMY_MODE,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/webhook/meta-ads")
async def meta_ads_webhook_supabase(request: Request):
    """Webhook Meta Ads que genera landing pages con métricas en Supabase"""
    
    try:
        # Obtener datos del webhook de Meta
        webhook_data = await request.json()
        
        # Extraer datos de la campaña
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
        
        # Generar landing page con Supabase
        landing_result = await supabase_landing_generator.generate_landing_page(landing_request)
        
        # Trigger análisis ML
        ml_analysis = await _trigger_ml_analysis(campaign_data)
        
        return {
            "success": True,
            "campaign_id": campaign_data.campaign_id,
            "landing_page": landing_result,
            "ml_analysis": ml_analysis,
            "supabase_integration": "active",
            "analytics_url": f"{RAILWAY_BASE_URL}/api/campaign/{campaign_data.campaign_id}/analytics",
            "dashboard_url": f"{RAILWAY_BASE_URL}/dashboard/campaigns/{campaign_data.campaign_id}",
            "automation_status": "24/7 active with Supabase tracking"
        }
        
    except Exception as e:
        logger.error(f"Meta Ads webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/landing/{page_id}")
async def serve_supabase_landing_page(page_id: str):
    """Servir landing page con tracking Supabase"""
    
    from fastapi.responses import HTMLResponse
    
    try:
        # Obtener campaign data desde Supabase
        campaign_result = supabase.table("campaigns").select("*").eq("page_id", page_id).execute()
        
        if not campaign_result.data:
            raise HTTPException(status_code=404, detail="Landing page not found")
        
        campaign = campaign_result.data[0]
        
        # Generar HTML dinámico con datos de Supabase
        template = Template(supabase_landing_generator.templates["music_release"])
        
        template_data = {
            "artist_name": campaign["artist_name"],
            "song_name": campaign["song_name"],
            "genre": campaign["genre"],
            "campaign_id": campaign["campaign_id"],
            "page_id": page_id,
            "page_url": campaign["page_url"],
            "youtube_url": campaign.get("youtube_channel", f"https://youtube.com/results?search_query={campaign['artist_name']}+{campaign['song_name']}"),
            "target_countries": campaign["target_countries"],
            "estimated_plays": supabase_landing_generator._estimate_plays(float(campaign["budget_euros"]), campaign["genre"]),
            "estimated_fans": supabase_landing_generator._estimate_fans(float(campaign["budget_euros"]), campaign["genre"])
        }
        
        html_content = template.render(**template_data)
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Serve landing page error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/supabase/track-visit")
async def track_visit_supabase(visit_data: Dict[str, Any]):
    """Endpoint para tracking de visitas UTM en Supabase"""
    
    try:
        utm_visit = UTMVisit(
            page_id=visit_data["page_id"],
            campaign_id=visit_data["campaign_id"],
            utm_source=visit_data.get("utm_source", "direct"),
            utm_medium=visit_data.get("utm_medium", "none"),
            utm_campaign=visit_data.get("utm_campaign"),
            utm_content=visit_data.get("utm_content"),
            utm_term=visit_data.get("utm_term"),
            visitor_ip=visit_data.get("visitor_ip"),
            user_agent=visit_data.get("user_agent"),
            referrer=visit_data.get("referrer"),
            country=visit_data.get("country"),
            device_type=visit_data.get("device_type")
        )
        
        result = await SupabaseLandingOperations.track_visit(utm_visit)
        
        return {
            "success": result["success"],
            "message": "Visit tracked in Supabase",
            "visit_id": result.get("visit_id")
        }
        
    except Exception as e:
        logger.error(f"Supabase visit tracking error: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/api/supabase/track-conversion")
async def track_conversion_supabase(conversion_data: Dict[str, Any]):
    """Endpoint para tracking de conversiones UTM en Supabase"""
    
    try:
        utm_conversion = UTMConversion(
            page_id=conversion_data["page_id"],
            campaign_id=conversion_data["campaign_id"],
            action_type=conversion_data["action_type"],
            platform=conversion_data["platform"],
            conversion_value=conversion_data.get("conversion_value", 1.0),
            utm_source=conversion_data.get("utm_source", "direct")
        )
        
        result = await SupabaseLandingOperations.track_conversion(utm_conversion)
        
        return {
            "success": result["success"],
            "message": "Conversion tracked in Supabase",
            "conversion_id": result.get("conversion_id")
        }
        
    except Exception as e:
        logger.error(f"Supabase conversion tracking error: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/campaign/{campaign_id}/analytics")
async def get_supabase_campaign_analytics(campaign_id: str):
    """Obtener analytics completas de campaña desde Supabase"""
    
    try:
        analytics = await SupabaseLandingOperations.get_campaign_analytics(campaign_id)
        
        return analytics
        
    except Exception as e:
        logger.error(f"Supabase analytics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/supabase/campaigns")
async def list_campaigns():
    """Listar todas las campañas en Supabase"""
    
    try:
        campaigns_result = supabase.table("campaigns").select("*").order("created_at", desc=True).limit(50).execute()
        
        return {
            "success": True,
            "campaigns": campaigns_result.data,
            "total": len(campaigns_result.data)
        }
        
    except Exception as e:
        logger.error(f"List campaigns error: {str(e)}")
        return {"success": False, "error": str(e)}

@app.get("/api/supabase/dashboard/{campaign_id}")
async def supabase_dashboard_data(campaign_id: str):
    """Datos completos del dashboard para una campaña específica"""
    
    try:
        # Obtener campaign data
        campaign_result = supabase.table("campaigns").select("*").eq("campaign_id", campaign_id).execute()
        
        if not campaign_result.data:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign = campaign_result.data[0]
        
        # Obtener analytics
        analytics = await SupabaseLandingOperations.get_campaign_analytics(campaign_id)
        
        # Obtener últimas visitas
        recent_visits = supabase.table("utm_visits").select("*").eq("campaign_id", campaign_id).order("timestamp", desc=True).limit(10).execute()
        
        # Obtener últimas conversiones
        recent_conversions = supabase.table("utm_conversions").select("*").eq("campaign_id", campaign_id).order("timestamp", desc=True).limit(10).execute()
        
        return {
            "campaign": campaign,
            "analytics": analytics,
            "recent_visits": recent_visits.data,
            "recent_conversions": recent_conversions.data,
            "supabase_integration": "active",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Dashboard data error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# FUNCIONES AUXILIARES
# ============================================

async def _trigger_ml_analysis(campaign_data: MetaCampaignData) -> Dict[str, Any]:
    """Trigger análisis ML con integración Supabase"""
    
    try:
        if DUMMY_MODE:
            return {
                "analysis_complete": True,
                "supabase_integration": "active",
                "ultralytics_score": 0.87,
                "music_genre_confidence": 0.92,
                "virality_prediction": 0.78,
                "requires_authorization": False,
                "recommendations": {
                    "increase_budget": 0,  # Sin incremento necesario
                    "target_platforms": ["tiktok", "youtube_shorts"],
                    "optimal_posting_time": "19:00-21:00"
                },
                "optimization_cost": 0,
                "confidence": 0.89
            }
        
        # En producción: llamar a ML Core con datos de Supabase
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ML_CORE_URL}/analyze-campaign-supabase",
                json={
                    **campaign_data.dict(),
                    "supabase_campaign_id": campaign_data.campaign_id
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"ML analysis failed: {response.text}")
                return {"analysis_complete": False}
                
    except Exception as e:
        logger.error(f"ML analysis error: {str(e)}")
        return {"analysis_complete": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8004,
        log_level="info"
    )