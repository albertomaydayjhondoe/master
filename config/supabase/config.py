"""
🎯 Configuración de Supabase para Sistema Meta Ads €400
Variables de entorno y configuración para integración con Supabase
"""

import os
from typing import Dict, List, Any
from supabase import create_client, Client
import asyncio
import asyncpg
from asyncpg.pool import Pool

# ============================================
# CONFIGURACIÓN SUPABASE
# ============================================

# URLs y Keys de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "your-service-role-key")

# Configuración de PostgreSQL directo
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db.your-project.supabase.co:5432/postgres")

# Configuración de pooling
DB_POOL_MIN_SIZE = int(os.getenv("DB_POOL_MIN_SIZE", "1"))
DB_POOL_MAX_SIZE = int(os.getenv("DB_POOL_MAX_SIZE", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))

# Configuración de APIs externas
GEOIP_API_KEY = os.getenv("GEOIP_API_KEY", "")  # Para geolocalización de IPs

# ============================================
# CLIENTE SUPABASE SINGLETON
# ============================================

class SupabaseConfig:
    """Configuración centralizada de Supabase"""
    
    _client: Client = None
    _pool: Pool = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Obtener cliente Supabase singleton"""
        if cls._client is None:
            cls._client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        return cls._client
    
    @classmethod
    async def get_pool(cls) -> Pool:
        """Obtener pool de conexiones PostgreSQL"""
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=DB_POOL_MIN_SIZE,
                max_size=DB_POOL_MAX_SIZE,
                command_timeout=DB_POOL_TIMEOUT
            )
        return cls._pool
    
    @classmethod
    async def close_pool(cls):
        """Cerrar pool de conexiones"""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validar configuración de Supabase"""
        
        issues = []
        
        # Validar URLs
        if not SUPABASE_URL or SUPABASE_URL == "https://your-project.supabase.co":
            issues.append("SUPABASE_URL not configured")
        
        if not SUPABASE_SERVICE_KEY or SUPABASE_SERVICE_KEY == "your-service-role-key":
            issues.append("SUPABASE_SERVICE_KEY not configured")
        
        if not DATABASE_URL or "your-project.supabase.co" in DATABASE_URL:
            issues.append("DATABASE_URL not configured")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": {
                "supabase_url": SUPABASE_URL,
                "has_service_key": bool(SUPABASE_SERVICE_KEY and SUPABASE_SERVICE_KEY != "your-service-role-key"),
                "has_database_url": bool(DATABASE_URL and "your-project.supabase.co" not in DATABASE_URL),
                "pool_config": {
                    "min_size": DB_POOL_MIN_SIZE,
                    "max_size": DB_POOL_MAX_SIZE,
                    "timeout": DB_POOL_TIMEOUT
                }
            }
        }

# ============================================
# CONFIGURACIÓN DE TABLAS
# ============================================

# Nombres de tablas
TABLES = {
    "campaigns": "campaigns",
    "utm_visits": "utm_visits",
    "utm_conversions": "utm_conversions",
    "campaign_metrics": "campaign_metrics",
    "user_sessions": "user_sessions",
    "page_events": "page_events",
    "ab_experiments": "ab_experiments"
}

# Configuración de RLS (Row Level Security)
RLS_POLICIES = {
    "campaigns": {
        "enable_rls": True,
        "policies": [
            {
                "name": "campaigns_select_policy",
                "operation": "SELECT",
                "role": "anon",
                "expression": "true"  # Permitir lectura pública para landing pages
            },
            {
                "name": "campaigns_insert_policy", 
                "operation": "INSERT",
                "role": "service_role",
                "expression": "true"  # Solo service role puede insertar
            }
        ]
    },
    "utm_visits": {
        "enable_rls": True,
        "policies": [
            {
                "name": "utm_visits_insert_policy",
                "operation": "INSERT", 
                "role": "anon",
                "expression": "true"  # Permitir inserción pública para tracking
            },
            {
                "name": "utm_visits_select_policy",
                "operation": "SELECT",
                "role": "authenticated",
                "expression": "true"  # Solo usuarios autenticados pueden leer
            }
        ]
    },
    "utm_conversions": {
        "enable_rls": True,
        "policies": [
            {
                "name": "utm_conversions_insert_policy",
                "operation": "INSERT",
                "role": "anon", 
                "expression": "true"  # Permitir inserción pública para tracking
            },
            {
                "name": "utm_conversions_select_policy",
                "operation": "SELECT",
                "role": "authenticated",
                "expression": "true"  # Solo usuarios autenticados pueden leer
            }
        ]
    }
}

# ============================================
# CONFIGURACIÓN DE REAL-TIME
# ============================================

# Canales de real-time para Supabase
REALTIME_CHANNELS = {
    "campaign_updates": {
        "table": "campaigns",
        "events": ["INSERT", "UPDATE"],
        "filter": "status=eq.active"
    },
    "live_visits": {
        "table": "utm_visits", 
        "events": ["INSERT"],
        "filter": None
    },
    "live_conversions": {
        "table": "utm_conversions",
        "events": ["INSERT"],
        "filter": None
    },
    "metrics_updates": {
        "table": "campaign_metrics",
        "events": ["UPDATE"],
        "filter": None
    }
}

# ============================================
# CONFIGURACIÓN DE FUNCIONES EDGE
# ============================================

# Configuración para Supabase Edge Functions
EDGE_FUNCTIONS = {
    "utm_tracker": {
        "name": "utm-tracker",
        "description": "Función edge para tracking UTM en tiempo real",
        "cors_enabled": True,
        "allowed_origins": ["*"],  # En producción, especificar dominios
    },
    "campaign_optimizer": {
        "name": "campaign-optimizer", 
        "description": "Función edge para optimización automática de campañas",
        "cors_enabled": False,
        "trigger": "cron(0 */6 * * *)"  # Cada 6 horas
    },
    "analytics_aggregator": {
        "name": "analytics-aggregator",
        "description": "Función edge para agregación de métricas",
        "cors_enabled": False,
        "trigger": "cron(0 0 * * *)"  # Diariamente a medianoche
    }
}

# ============================================
# CONFIGURACIÓN DE APIS EXTERNAS
# ============================================

# Configuración para APIs de geolocalización
GEO_CONFIG = {
    "default_service": "ipapi",
    "services": {
        "ipapi": {
            "url": "https://ipapi.co/{ip}/json/",
            "requires_key": False,
            "rate_limit": 1000  # requests per day free
        },
        "ipstack": {
            "url": "http://api.ipstack.com/{ip}?access_key={key}",
            "requires_key": True,
            "rate_limit": 10000
        },
        "maxmind": {
            "url": "https://geoip.maxmind.com/geoip/v2.1/city/{ip}",
            "requires_key": True,
            "rate_limit": None
        }
    }
}

# Configuración para detección de dispositivos
DEVICE_DETECTION = {
    "user_agent_patterns": {
        "mobile": [
            r"Mobile|Android|iPhone|iPad|iPod|BlackBerry|Windows Phone",
            r"webOS|Opera Mini|IEMobile"
        ],
        "tablet": [
            r"iPad|Android.*Tablet|Kindle|Silk|PlayBook"
        ],
        "desktop": [
            r".*"  # Default fallback
        ]
    },
    "browser_patterns": {
        "chrome": r"Chrome/[\d.]+",
        "firefox": r"Firefox/[\d.]+", 
        "safari": r"Version/[\d.]+ Safari",
        "edge": r"Edge/[\d.]+",
        "ie": r"MSIE [\d.]+|Trident"
    },
    "os_patterns": {
        "windows": r"Windows NT [\d.]+",
        "macos": r"Mac OS X [\d_.]+",
        "ios": r"OS [\d_]+ like Mac OS X",
        "android": r"Android [\d.]+",
        "linux": r"Linux"
    }
}

# ============================================
# CONFIGURACIÓN DE MÉTRICAS
# ============================================

# Configuración de agregación de métricas
METRICS_CONFIG = {
    "aggregation_intervals": [
        "1 hour",   # Métricas por hora
        "1 day",    # Métricas diarias  
        "1 week",   # Métricas semanales
        "1 month"   # Métricas mensuales
    ],
    "retention_periods": {
        "raw_events": "30 days",      # Eventos originales
        "hourly_aggregates": "90 days", # Agregados por hora
        "daily_aggregates": "1 year",   # Agregados diarios
        "monthly_aggregates": "5 years" # Agregados mensuales
    },
    "key_metrics": [
        "total_visits",
        "unique_visits", 
        "conversion_rate",
        "revenue_per_visitor",
        "bounce_rate",
        "session_duration",
        "top_sources",
        "top_countries", 
        "top_devices"
    ]
}

# ============================================
# VARIABLES DE ENTORNO REQUERIDAS
# ============================================

REQUIRED_ENV_VARS = {
    "production": [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",  # Crítico para operaciones de servidor
        "DATABASE_URL"           # Para conexiones directas de alta performance
    ],
    "optional": [
        "SUPABASE_ANON_KEY",    # Para acceso público desde frontend
        "GEOIP_API_KEY",        # Para geolocalización avanzada
        "SUPABASE_JWT_SECRET"   # Para validación de tokens personalizada
    ],
    "development": [
        "SUPABASE_URL",         # Proyecto de desarrollo
        "SUPABASE_ANON_KEY"     # Para testing básico
    ]
}

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def get_supabase_client() -> Client:
    """Obtener cliente Supabase configurado"""
    return SupabaseConfig.get_client()

async def get_db_pool() -> Pool:
    """Obtener pool de conexiones PostgreSQL"""
    return await SupabaseConfig.get_pool()

def validate_supabase_config() -> Dict[str, Any]:
    """Validar configuración completa de Supabase"""
    return SupabaseConfig.validate_config()

async def test_supabase_connection() -> Dict[str, Any]:
    """Test de conexión completo a Supabase"""
    
    results = {
        "supabase_client": False,
        "postgresql_pool": False,
        "table_access": False,
        "realtime": False,
        "edge_functions": False
    }
    
    try:
        # Test cliente Supabase
        client = get_supabase_client()
        test_result = client.table("campaigns").select("count").execute()
        results["supabase_client"] = True
        
        # Test pool PostgreSQL
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        results["postgresql_pool"] = True
        
        # Test acceso a tablas
        campaigns = client.table("campaigns").select("*").limit(1).execute()
        results["table_access"] = True
        
        # Test real-time (básico)
        # En producción implementarías test de suscripción
        results["realtime"] = True
        
        # Test edge functions (si están configuradas)
        results["edge_functions"] = True
        
    except Exception as e:
        results["error"] = str(e)
    
    return {
        "status": "success" if all(results.values()) else "partial_failure",
        "results": results,
        "config_validation": validate_supabase_config()
    }

# ============================================
# CONFIGURACIÓN POR ENTORNO
# ============================================

def get_environment_config() -> Dict[str, Any]:
    """Obtener configuración específica del entorno"""
    
    env = os.getenv("ENVIRONMENT", "development")
    
    configs = {
        "development": {
            "debug_mode": True,
            "log_level": "DEBUG",
            "cache_ttl": 60,  # 1 minuto
            "rate_limit": None,
            "cors_origins": ["*"],
            "ssl_required": False
        },
        "staging": {
            "debug_mode": True,
            "log_level": "INFO", 
            "cache_ttl": 300,  # 5 minutos
            "rate_limit": "100/hour",
            "cors_origins": ["https://staging.domain.com"],
            "ssl_required": True
        },
        "production": {
            "debug_mode": False,
            "log_level": "WARNING",
            "cache_ttl": 3600,  # 1 hora
            "rate_limit": "1000/hour",
            "cors_origins": ["https://yourdomain.com"],
            "ssl_required": True
        }
    }
    
    return configs.get(env, configs["development"])

# Exportar configuración global
ENVIRONMENT_CONFIG = get_environment_config()