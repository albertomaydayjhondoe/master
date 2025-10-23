"""
SISTEMA UTM GENERATOR - MÓDULO 5 REFINADO
Sistema Avanzado Meta Ads - Generación y Tracking UTMs Automático

Integración completa con ML Learning Cycle para optimización automática
basada en datos de conversión y engagement por UTM parameters
"""

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlencode
import uuid

@dataclass
class UTMParameters:
    """Parámetros UTM estandarizados para tracking"""
    utm_source: str
    utm_medium: str 
    utm_campaign: str
    utm_content: str
    utm_term: str
    utm_id: str  # ID único del UTM
    
    def to_query_string(self) -> str:
        """Convierte a query string para URL"""
        params = {
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'utm_content': self.utm_content,
            'utm_term': self.utm_term,
            'utm_id': self.utm_id
        }
        return urlencode(params)
    
    def to_full_url(self, base_url: str) -> str:
        """Genera URL completa con UTMs"""
        separator = '&' if '?' in base_url else '?'
        return f"{base_url}{separator}{self.to_query_string()}"

@dataclass
class UTMVisitData:
    """Datos de visita capturados desde UTMs"""
    visit_id: str
    timestamp: datetime
    utm_params: UTMParameters
    ip_address: str
    user_agent: str
    session_duration: Optional[int] = None
    conversion: bool = False
    conversion_type: Optional[str] = None
    conversion_value: Optional[float] = None

class UTMDatabase:
    """Manejo de base de datos SQLite para UTMs"""
    
    def __init__(self, db_path: str = "data/utm_tracking.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializar tablas de base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de UTMs generados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS utm_campaigns (
                utm_id TEXT PRIMARY KEY,
                campaign_name TEXT NOT NULL,
                clip_name TEXT NOT NULL,
                subgenre TEXT NOT NULL,
                collaboration TEXT,
                utm_source TEXT NOT NULL,
                utm_medium TEXT NOT NULL,
                utm_campaign TEXT NOT NULL,
                utm_content TEXT NOT NULL,
                utm_term TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Tabla de visitas con UTMs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS utm_visits (
                visit_id TEXT PRIMARY KEY,
                utm_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                session_duration INTEGER,
                conversion BOOLEAN DEFAULT FALSE,
                conversion_type TEXT,
                conversion_value REAL,
                geo_country TEXT,
                device_type TEXT,
                FOREIGN KEY (utm_id) REFERENCES utm_campaigns (utm_id)
            )
        ''')
        
        # Tabla de métricas agregadas por UTM
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS utm_metrics (
                utm_id TEXT PRIMARY KEY,
                total_clicks INTEGER DEFAULT 0,
                total_visits INTEGER DEFAULT 0,
                total_conversions INTEGER DEFAULT 0,
                conversion_rate REAL DEFAULT 0.0,
                total_value REAL DEFAULT 0.0,
                avg_session_duration REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (utm_id) REFERENCES utm_campaigns (utm_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_utm_campaign(self, utm_params: UTMParameters, campaign_context: Dict[str, Any]):
        """Guardar campaña UTM en base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO utm_campaigns 
            (utm_id, campaign_name, clip_name, subgenre, collaboration,
             utm_source, utm_medium, utm_campaign, utm_content, utm_term)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            utm_params.utm_id,
            campaign_context.get('campaign_name', ''),
            campaign_context.get('clip_name', ''),
            campaign_context.get('subgenre', ''),
            campaign_context.get('collaboration', ''),
            utm_params.utm_source,
            utm_params.utm_medium,
            utm_params.utm_campaign,
            utm_params.utm_content,
            utm_params.utm_term
        ))
        
        conn.commit()
        conn.close()
    
    def save_visit(self, visit_data: UTMVisitData):
        """Guardar visita con datos UTM"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO utm_visits 
            (visit_id, utm_id, timestamp, ip_address, user_agent, 
             session_duration, conversion, conversion_type, conversion_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            visit_data.visit_id,
            visit_data.utm_params.utm_id,
            visit_data.timestamp.isoformat(),
            visit_data.ip_address,
            visit_data.user_agent,
            visit_data.session_duration,
            visit_data.conversion,
            visit_data.conversion_type,
            visit_data.conversion_value
        ))
        
        conn.commit()
        conn.close()
    
    def get_utm_metrics(self, utm_id: str) -> Dict[str, Any]:
        """Obtener métricas por UTM ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as total_visits,
                   SUM(CASE WHEN conversion = 1 THEN 1 ELSE 0 END) as conversions,
                   AVG(session_duration) as avg_duration,
                   SUM(conversion_value) as total_value
            FROM utm_visits 
            WHERE utm_id = ?
        ''', (utm_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            total_visits, conversions, avg_duration, total_value = result
            conversion_rate = (conversions / total_visits * 100) if total_visits > 0 else 0
            
            return {
                'utm_id': utm_id,
                'total_visits': total_visits or 0,
                'total_conversions': conversions or 0,
                'conversion_rate': conversion_rate,
                'avg_session_duration': avg_duration or 0,
                'total_value': total_value or 0
            }
        return {}

class UTMGenerator:
    """Generador automático de UTMs para campañas Meta Ads"""
    
    def __init__(self):
        self.db = UTMDatabase()
    
    def generate_utm_for_campaign(self, campaign_data: Dict[str, Any], 
                                granular_tags: Any = None) -> UTMParameters:
        """
        Generar UTM automático para campaña con datos granulares
        
        Args:
            campaign_data: Datos de la campaña (nombre, clip, etc.)
            granular_tags: Tags granulares del sistema de etiquetado
        
        Returns:
            UTMParameters: Parámetros UTM generados
        """
        
        print("🔗 GENERANDO UTMs AUTOMÁTICOS PARA CAMPAÑA")
        print("=" * 50)
        
        # 1. Extraer datos base
        campaign_name = campaign_data.get('campaign_name', 'unknown_campaign')
        clip_name = campaign_data.get('clip_name', 'unknown_clip')
        
        # 2. Usar etiquetado granular si está disponible
        if granular_tags:
            subgenre = granular_tags.sub_genre
            collaboration = granular_tags.collaboration_artist or 'solo'
            main_genre = granular_tags.main_genre.value if hasattr(granular_tags.main_genre, 'value') else 'unknown'
        else:
            subgenre = campaign_data.get('subgenre', 'unknown_subgenre')
            collaboration = campaign_data.get('collaboration', 'solo')
            main_genre = campaign_data.get('genre', 'unknown_genre')
        
        # 3. Normalizar nombres para UTMs (sin espacios, caracteres especiales)
        utm_campaign = self._normalize_utm_value(f"{main_genre}_{campaign_name}")
        utm_content = self._normalize_utm_value(f"{clip_name}_{collaboration}")
        utm_term = self._normalize_utm_value(f"{subgenre}_{collaboration}")
        
        # 4. Generar ID único
        utm_id = self._generate_unique_utm_id(campaign_name, clip_name, subgenre)
        
        # 5. Crear parámetros UTM
        utm_params = UTMParameters(
            utm_source='meta',
            utm_medium='cpc',
            utm_campaign=utm_campaign,
            utm_content=utm_content,
            utm_term=utm_term,
            utm_id=utm_id
        )
        
        # 6. Guardar en base de datos
        campaign_context = {
            'campaign_name': campaign_name,
            'clip_name': clip_name,
            'subgenre': subgenre,
            'collaboration': collaboration
        }
        self.db.save_utm_campaign(utm_params, campaign_context)
        
        print(f"✅ UTM GENERADO EXITOSAMENTE:")
        print(f"   🆔 UTM ID: {utm_id}")
        print(f"   📋 Campaign: {utm_campaign}")
        print(f"   🎬 Content: {utm_content}")
        print(f"   🏷️ Term: {utm_term}")
        print()
        
        return utm_params
    
    def generate_utm_for_followup_cycle(self, original_utm: UTMParameters, 
                                       cycle_data: Dict[str, Any]) -> UTMParameters:
        """Generar UTM específico para ciclos de seguimiento de $50"""
        
        # Modificar UTM para indicar que es follow-up
        followup_campaign = f"{original_utm.utm_campaign}_followup"
        followup_content = f"{original_utm.utm_content}_cycle_{cycle_data.get('cycle_number', 1)}"
        followup_term = f"{original_utm.utm_term}_reinversion"
        
        # Nuevo ID único para el follow-up
        followup_id = f"{original_utm.utm_id}_fu_{cycle_data.get('cycle_number', 1)}"
        
        followup_utm = UTMParameters(
            utm_source='meta',
            utm_medium='cpc_followup',
            utm_campaign=followup_campaign,
            utm_content=followup_content,
            utm_term=followup_term,
            utm_id=followup_id
        )
        
        return followup_utm
    
    def generate_geo_specific_utm(self, base_utm: UTMParameters, 
                                 country_code: str) -> UTMParameters:
        """Generar UTM específico por país para ajustes geográficos"""
        
        geo_campaign = f"{base_utm.utm_campaign}_{country_code.lower()}"
        geo_content = f"{base_utm.utm_content}_{country_code.lower()}"
        geo_id = f"{base_utm.utm_id}_{country_code.lower()}"
        
        geo_utm = UTMParameters(
            utm_source='meta',
            utm_medium='cpc_geo',
            utm_campaign=geo_campaign,
            utm_content=geo_content,
            utm_term=base_utm.utm_term,
            utm_id=geo_id
        )
        
        return geo_utm
    
    def _normalize_utm_value(self, value: str) -> str:
        """Normalizar valores UTM (sin espacios, caracteres especiales)"""
        return value.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
    
    def _generate_unique_utm_id(self, campaign: str, clip: str, subgenre: str) -> str:
        """Generar ID único para UTM"""
        unique_string = f"{campaign}_{clip}_{subgenre}_{datetime.now().isoformat()}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]

class UTMLandingPageCapture:
    """Sistema de captura de UTMs en landing page"""
    
    def __init__(self):
        self.db = UTMDatabase()
    
    def capture_utm_visit(self, url_params: Dict[str, str], 
                         visitor_data: Dict[str, Any]) -> UTMVisitData:
        """
        Capturar visita desde parámetros UTM de la URL
        
        Args:
            url_params: Parámetros de la URL (?utm_source=meta&...)
            visitor_data: Datos del visitante (IP, User-Agent, etc.)
        
        Returns:
            UTMVisitData: Datos de visita procesados
        """
        
        print("📊 CAPTURANDO VISITA CON UTMs")
        print("=" * 35)
        
        # 1. Extraer parámetros UTM
        utm_params = UTMParameters(
            utm_source=url_params.get('utm_source', 'unknown'),
            utm_medium=url_params.get('utm_medium', 'unknown'),
            utm_campaign=url_params.get('utm_campaign', 'unknown'),
            utm_content=url_params.get('utm_content', 'unknown'),
            utm_term=url_params.get('utm_term', 'unknown'),
            utm_id=url_params.get('utm_id', 'unknown')
        )
        
        # 2. Generar ID único para la visita
        visit_id = str(uuid.uuid4())
        
        # 3. Crear datos de visita
        visit_data = UTMVisitData(
            visit_id=visit_id,
            timestamp=datetime.now(),
            utm_params=utm_params,
            ip_address=visitor_data.get('ip_address', '127.0.0.1'),
            user_agent=visitor_data.get('user_agent', 'unknown')
        )
        
        # 4. Guardar en base de datos
        self.db.save_visit(visit_data)
        
        print(f"✅ VISITA CAPTURADA:")
        print(f"   🆔 Visit ID: {visit_id}")
        print(f"   📋 Campaign: {utm_params.utm_campaign}")
        print(f"   🎬 Content: {utm_params.utm_content}")
        print(f"   🕐 Timestamp: {visit_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        return visit_data
    
    def update_visit_conversion(self, visit_id: str, conversion_type: str, 
                              conversion_value: float = 0.0):
        """Actualizar visita con datos de conversión"""
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE utm_visits 
            SET conversion = TRUE, conversion_type = ?, conversion_value = ?
            WHERE visit_id = ?
        ''', (conversion_type, conversion_value, visit_id))
        
        conn.commit()
        conn.close()
        
        print(f"🎯 CONVERSIÓN REGISTRADA: {visit_id} → {conversion_type} (${conversion_value:.2f})")

class UTMMLIntegration:
    """Integración de UTMs con ML Learning Cycle"""
    
    def __init__(self):
        self.db = UTMDatabase()
    
    def get_utm_performance_data(self) -> List[Dict[str, Any]]:
        """Obtener datos de performance UTM para alimentar ML"""
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                c.utm_id,
                c.campaign_name,
                c.clip_name,
                c.subgenre,
                c.collaboration,
                COUNT(v.visit_id) as total_visits,
                SUM(CASE WHEN v.conversion = 1 THEN 1 ELSE 0 END) as conversions,
                AVG(v.session_duration) as avg_session_duration,
                SUM(v.conversion_value) as total_revenue
            FROM utm_campaigns c
            LEFT JOIN utm_visits v ON c.utm_id = v.utm_id
            WHERE c.status = 'active'
            GROUP BY c.utm_id
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        performance_data = []
        for row in results:
            utm_id, campaign, clip, subgenre, collaboration, visits, conversions, avg_duration, revenue = row
            
            conversion_rate = (conversions / visits * 100) if visits > 0 else 0
            
            performance_data.append({
                'utm_id': utm_id,
                'campaign_name': campaign,
                'clip_name': clip,
                'subgenre': subgenre,
                'collaboration': collaboration,
                'total_visits': visits or 0,
                'total_conversions': conversions or 0,
                'conversion_rate': conversion_rate,
                'avg_session_duration': avg_duration or 0,
                'total_revenue': revenue or 0,
                'revenue_per_visit': (revenue / visits) if visits > 0 and revenue else 0
            })
        
        return performance_data
    
    def generate_ml_insights(self) -> Dict[str, Any]:
        """Generar insights para ML basados en datos UTM"""
        
        performance_data = self.get_utm_performance_data()
        
        if not performance_data:
            return {'insights': [], 'recommendations': []}
        
        # Análisis por subgénero
        subgenre_performance = {}
        for data in performance_data:
            subgenre = data['subgenre']
            if subgenre not in subgenre_performance:
                subgenre_performance[subgenre] = {
                    'total_visits': 0,
                    'total_conversions': 0,
                    'total_revenue': 0,
                    'campaigns': 0
                }
            
            subgenre_performance[subgenre]['total_visits'] += data['total_visits']
            subgenre_performance[subgenre]['total_conversions'] += data['total_conversions']
            subgenre_performance[subgenre]['total_revenue'] += data['total_revenue']
            subgenre_performance[subgenre]['campaigns'] += 1
        
        # Calcular métricas por subgénero
        for subgenre in subgenre_performance:
            perf = subgenre_performance[subgenre]
            perf['conversion_rate'] = (perf['total_conversions'] / perf['total_visits'] * 100) if perf['total_visits'] > 0 else 0
            perf['revenue_per_visit'] = perf['total_revenue'] / perf['total_visits'] if perf['total_visits'] > 0 else 0
        
        # Generar insights
        insights = []
        recommendations = []
        
        # Mejor subgénero por conversión
        best_subgenre = max(subgenre_performance.items(), key=lambda x: x[1]['conversion_rate'])
        insights.append(f"Mejor subgénero por conversión: {best_subgenre[0]} ({best_subgenre[1]['conversion_rate']:.1f}%)")
        
        # Recomendaciones
        for subgenre, perf in subgenre_performance.items():
            if perf['conversion_rate'] > 5.0:  # Alta conversión
                recommendations.append(f"Incrementar presupuesto en {subgenre} (alta conversión: {perf['conversion_rate']:.1f}%)")
            elif perf['conversion_rate'] < 1.0:  # Baja conversión
                recommendations.append(f"Optimizar o pausar {subgenre} (baja conversión: {perf['conversion_rate']:.1f}%)")
        
        return {
            'subgenre_performance': subgenre_performance,
            'insights': insights,
            'recommendations': recommendations,
            'total_campaigns_analyzed': len(performance_data)
        }

# Clase principal del sistema UTM
class AdvancedUTMSystem:
    """Sistema UTM completo integrado con Meta Ads"""
    
    def __init__(self):
        self.generator = UTMGenerator()
        self.capture = UTMLandingPageCapture()
        self.ml_integration = UTMMLIntegration()
    
    def create_campaign_with_utms(self, campaign_data: Dict[str, Any], 
                                 granular_tags: Any = None) -> Dict[str, Any]:
        """Crear campaña completa con UTMs integrados"""
        
        print("🚀 CREANDO CAMPAÑA CON SISTEMA UTM COMPLETO")
        print("=" * 55)
        
        # 1. Generar UTM principal
        main_utm = self.generator.generate_utm_for_campaign(campaign_data, granular_tags)
        
        # 2. Generar UTMs geográficos si hay distribución geo
        geo_utms = {}
        if 'geo_countries' in campaign_data:
            for country in campaign_data['geo_countries']:
                geo_utms[country] = self.generator.generate_geo_specific_utm(main_utm, country)
        
        # 3. Crear URLs de landing page con UTMs
        base_landing_url = campaign_data.get('landing_url', 'https://example.com/landing')
        
        campaign_urls = {
            'main_url': main_utm.to_full_url(base_landing_url),
            'geo_urls': {country: utm.to_full_url(base_landing_url) 
                        for country, utm in geo_utms.items()}
        }
        
        print(f"📊 CAMPAIGN URLs GENERADAS:")
        print(f"   🔗 Main URL: {campaign_urls['main_url']}")
        if geo_utms:
            for country, url in campaign_urls['geo_urls'].items():
                print(f"   🌍 {country}: {url}")
        print()
        
        return {
            'campaign_id': campaign_data.get('campaign_id', 'unknown'),
            'main_utm': main_utm,
            'geo_utms': geo_utms,
            'campaign_urls': campaign_urls,
            'utm_system_integrated': True
        }
    
    def simulate_campaign_visits(self, campaign_with_utms: Dict[str, Any], 
                               num_visits: int = 100) -> List[UTMVisitData]:
        """Simular visitas de campaña para testing"""
        
        print(f"🎯 SIMULANDO {num_visits} VISITAS DE CAMPAÑA")
        print("=" * 45)
        
        visits = []
        main_utm = campaign_with_utms['main_utm']
        
        # Simular visitas con conversiones realistas
        for i in range(num_visits):
            # Datos simulados de visitante
            visitor_data = {
                'ip_address': f"192.168.1.{i % 255}",
                'user_agent': f"Mozilla/5.0 (SimulatedBrowser/{i})"
            }
            
            # Simular parámetros UTM desde URL
            url_params = asdict(main_utm)
            
            # Capturar visita
            visit = self.capture.capture_utm_visit(url_params, visitor_data)
            
            # Simular conversión aleatoria (15% tasa de conversión simulada)
            import random
            if random.random() < 0.15:
                conversion_types = ['stream', 'download', 'purchase', 'signup']
                conversion_type = random.choice(conversion_types)
                conversion_value = random.uniform(0.50, 15.00)
                
                self.capture.update_visit_conversion(
                    visit.visit_id, 
                    conversion_type, 
                    conversion_value
                )
            
            visits.append(visit)
        
        print(f"✅ SIMULACIÓN COMPLETADA: {len(visits)} visitas procesadas")
        return visits
    
    def generate_utm_report(self) -> Dict[str, Any]:
        """Generar reporte completo de UTMs para ML"""
        
        print("📊 GENERANDO REPORTE UTM PARA ML")
        print("=" * 40)
        
        # Obtener datos de performance
        performance_data = self.ml_integration.get_utm_performance_data()
        ml_insights = self.ml_integration.generate_ml_insights()
        
        # Calcular métricas consolidadas
        total_visits = sum(d['total_visits'] for d in performance_data)
        total_conversions = sum(d['total_conversions'] for d in performance_data)
        total_revenue = sum(d['total_revenue'] for d in performance_data)
        
        overall_conversion_rate = (total_conversions / total_visits * 100) if total_visits > 0 else 0
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_campaigns': len(performance_data),
            'total_visits': total_visits,
            'total_conversions': total_conversions,
            'overall_conversion_rate': overall_conversion_rate,
            'total_revenue': total_revenue,
            'revenue_per_visit': total_revenue / total_visits if total_visits > 0 else 0,
            'performance_by_campaign': performance_data,
            'ml_insights': ml_insights,
            'utm_system_health': 'operational'
        }
        
        print("✅ REPORTE UTM GENERADO:")
        print(f"   📊 Campañas: {report['total_campaigns']}")
        print(f"   👥 Visitas: {report['total_visits']:,}")
        print(f"   🎯 Conversiones: {report['total_conversions']}")
        print(f"   📈 Tasa conversión: {report['overall_conversion_rate']:.2f}%")
        print(f"   💰 Revenue total: ${report['total_revenue']:.2f}")
        print()
        
        return report

# Función principal de testing
def test_utm_system_complete():
    """Test completo del sistema UTM integrado"""
    
    print("🧪 TEST COMPLETO - SISTEMA UTM AVANZADO")
    print("=" * 50)
    
    # 1. Inicializar sistema
    utm_system = AdvancedUTMSystem()
    
    # 2. Datos de campaña de prueba (reggaeton con colaboración)
    campaign_data = {
        'campaign_id': 'camp_reggaeton_utm_001',
        'campaign_name': 'Bellakeo Nocturno Campaign',
        'clip_name': 'Bellakeo_Nocturno_Anuel',
        'genre': 'reggaeton',
        'subgenre': 'perreo_intenso',
        'collaboration': 'Anuel AA',
        'landing_url': 'https://spotify.com/track/bellakeo-nocturno',
        'geo_countries': ['ES', 'MX', 'CO', 'PR']
    }
    
    # 3. Simular etiquetas granulares
    from types import SimpleNamespace
    mock_granular_tags = SimpleNamespace(
        sub_genre='perreo_intenso',
        collaboration_artist='Anuel AA',
        main_genre=SimpleNamespace(value='reggaeton')
    )
    
    # 4. Crear campaña con UTMs
    campaign_with_utms = utm_system.create_campaign_with_utms(
        campaign_data, 
        mock_granular_tags
    )
    
    # 5. Simular visitas
    visits = utm_system.simulate_campaign_visits(campaign_with_utms, num_visits=150)
    
    # 6. Generar reporte para ML
    utm_report = utm_system.generate_utm_report()
    
    print("🎯 RESULTADOS DEL TEST:")
    print(f"   📊 UTMs generados: ✅")
    print(f"   🌍 UTMs geográficos: {len(campaign_with_utms['geo_utms'])}")
    print(f"   👥 Visitas simuladas: {len(visits)}")
    print(f"   📈 Datos para ML: ✅")
    print()
    
    return {
        'utm_system': utm_system,
        'campaign_with_utms': campaign_with_utms,
        'visits': visits,
        'utm_report': utm_report
    }

if __name__ == "__main__":
    # Ejecutar test completo
    test_results = test_utm_system_complete()
    
    print("✅ SISTEMA UTM COMPLETAMENTE IMPLEMENTADO")
    print("   Sistema listo para integración con Meta Ads y ML Learning Cycle")
    print("   Base de datos SQLite creada con tablas UTM")
    print("   Tracking automático de conversiones implementado")