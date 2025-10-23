"""
Advanced Campaign System - Follower Exclusion Module
Exclusión de seguidores actuales para evitar mostrar anuncios a usuarios ya convertidos
"""

import json
import random
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

@dataclass
class FollowerData:
    """Datos de un seguidor para exclusión"""
    user_id: str
    follow_date: datetime
    engagement_level: float  # 0-1
    account_type: str  # personal, business, creator
    location: Optional[str] = None
    demographics: Dict[str, str] = field(default_factory=dict)

@dataclass 
class AudienceSegment:
    """Segmento de audiencia filtrado"""
    segment_id: str
    original_size: int
    filtered_size: int
    exclusion_count: int
    exclusion_percentage: float
    segment_type: str
    targeting_criteria: Dict[str, any]

class FollowerExclusionManager:
    """Manager para exclusión de seguidores actuales de campañas"""
    
    def __init__(self):
        self.followers_cache = {}
        self.exclusion_history = []
        
        # Configuración de exclusión
        self.exclusion_settings = {
            'exclude_recent_followers': True,  # Excluir seguidores recientes
            'recent_threshold_days': 30,       # Días para considerar "reciente"
            'exclude_high_engagement': True,   # Excluir seguidores muy activos
            'engagement_threshold': 0.7,       # Threshold para "alta engagement"
            'preserve_segment_size': True,     # Mantener tamaño mínimo de audiencia
            'minimum_audience_size': 1000      # Tamaño mínimo de audiencia
        }
    
    def collect_followers(self, account_id: str) -> List[FollowerData]:
        """
        Simula recolección de lista de seguidores actuales
        En producción: integrar con Meta Graph API o base de datos real
        """
        print(f"📥 RECOLECTANDO SEGUIDORES ACTUALES - Cuenta: {account_id}")
        print("-" * 50)
        
        # Simular seguidores existentes
        follower_count = random.randint(1500, 8000)  # Entre 1.5K y 8K seguidores
        followers = []
        
        # Generar seguidores simulados
        for i in range(follower_count):
            user_id = f"user_{account_id}_{i:05d}"
            
            # Simular diferentes tipos de seguidores
            account_types = ['personal', 'business', 'creator']
            weights = [0.7, 0.2, 0.1]  # 70% personal, 20% business, 10% creator
            
            follow_days_ago = random.randint(1, 365)
            follow_date = datetime.now() - timedelta(days=follow_days_ago)
            
            # Engagement más alto para seguidores más recientes
            if follow_days_ago <= 30:
                engagement_level = random.uniform(0.4, 0.9)
            elif follow_days_ago <= 90:
                engagement_level = random.uniform(0.2, 0.6)
            else:
                engagement_level = random.uniform(0.1, 0.4)
            
            follower = FollowerData(
                user_id=user_id,
                follow_date=follow_date,
                engagement_level=engagement_level,
                account_type=random.choices(account_types, weights=weights)[0],
                location=random.choice(['ES', 'MX', 'CO', 'AR', 'CL', 'PE', 'EC', 'US']),
                demographics={
                    'age_range': random.choice(['18-24', '25-34', '35-44', '45-54']),
                    'gender': random.choice(['male', 'female', 'unknown']),
                    'interests': random.sample(['music', 'trap', 'reggaeton', 'lifestyle', 'fashion'], 2)
                }
            )
            followers.append(follower)
        
        # Cache para reutilización
        self.followers_cache[account_id] = followers
        
        print(f"✅ Seguidores recolectados: {len(followers):,}")
        print(f"   📊 Por tipo: Personal={sum(1 for f in followers if f.account_type=='personal'):,}, Business={sum(1 for f in followers if f.account_type=='business'):,}")
        print(f"   🔥 Alta engagement (>0.7): {sum(1 for f in followers if f.engagement_level > 0.7):,}")
        print(f"   📅 Recientes (<30 días): {sum(1 for f in followers if (datetime.now() - f.follow_date).days < 30):,}")
        print()
        
        return followers
    
    def create_exclusion_list(self, followers: List[FollowerData], 
                            exclusion_criteria: Dict = None) -> Set[str]:
        """
        Crea lista de exclusión basada en criterios específicos
        """
        if exclusion_criteria is None:
            exclusion_criteria = self.exclusion_settings
        
        exclusion_set = set()
        
        print("🚫 CREANDO LISTA DE EXCLUSIÓN")
        print("-" * 30)
        
        # 1. Excluir seguidores recientes si está activado
        if exclusion_criteria.get('exclude_recent_followers', True):
            threshold_days = exclusion_criteria.get('recent_threshold_days', 30)
            recent_followers = [
                f for f in followers 
                if (datetime.now() - f.follow_date).days <= threshold_days
            ]
            exclusion_set.update(f.user_id for f in recent_followers)
            print(f"   📅 Recientes (<{threshold_days} días): {len(recent_followers):,} excluidos")
        
        # 2. Excluir seguidores con alta engagement si está activado
        if exclusion_criteria.get('exclude_high_engagement', True):
            engagement_threshold = exclusion_criteria.get('engagement_threshold', 0.7)
            high_engagement_followers = [
                f for f in followers 
                if f.engagement_level > engagement_threshold
            ]
            exclusion_set.update(f.user_id for f in high_engagement_followers)
            print(f"   🔥 Alta engagement (>{engagement_threshold}): {len(high_engagement_followers):,} excluidos")
        
        # 3. Excluir todos los seguidores (opción más agresiva)
        if exclusion_criteria.get('exclude_all_followers', False):
            exclusion_set.update(f.user_id for f in followers)
            print(f"   🚫 Todos los seguidores: {len(followers):,} excluidos")
        
        print(f"✅ Total únicos en lista de exclusión: {len(exclusion_set):,}")
        print()
        
        return exclusion_set
    
    def filter_audience(self, audience_segment: Dict, 
                       exclusion_list: Set[str],
                       account_id: str) -> AudienceSegment:
        """
        Filtra audiencia eliminando seguidores de la lista de exclusión
        """
        print(f"🎯 FILTRANDO AUDIENCIA - {audience_segment.get('name', 'Unnamed')}")
        print("-" * 40)
        
        # Simular audiencia original
        original_size = audience_segment.get('estimated_size', random.randint(50000, 500000))
        
        # Simular overlap con seguidores (típicamente 5-20%)
        overlap_percentage = random.uniform(0.05, 0.20)
        overlap_count = int(original_size * overlap_percentage)
        
        # Calcular audiencia filtrada
        filtered_size = original_size - overlap_count
        exclusion_percentage = (overlap_count / original_size) * 100
        
        # Validar tamaño mínimo de audiencia
        minimum_size = self.exclusion_settings.get('minimum_audience_size', 1000)
        if filtered_size < minimum_size:
            print(f"⚠️ Audiencia filtrada muy pequeña ({filtered_size:,})")
            print(f"   Ajustando a tamaño mínimo: {minimum_size:,}")
            filtered_size = minimum_size
            overlap_count = original_size - filtered_size
            exclusion_percentage = (overlap_count / original_size) * 100
        
        segment_id = hashlib.md5(f"{account_id}_{audience_segment.get('name', 'default')}_{datetime.now()}".encode()).hexdigest()[:12]
        
        filtered_segment = AudienceSegment(
            segment_id=segment_id,
            original_size=original_size,
            filtered_size=filtered_size,
            exclusion_count=overlap_count,
            exclusion_percentage=exclusion_percentage,
            segment_type=audience_segment.get('type', 'lookalike'),
            targeting_criteria=audience_segment.get('targeting', {})
        )
        
        print(f"   📊 Tamaño original: {original_size:,}")
        print(f"   🚫 Seguidores excluidos: {overlap_count:,} ({exclusion_percentage:.1f}%)")
        print(f"   ✅ Audiencia filtrada: {filtered_size:,}")
        print(f"   🆔 Segment ID: {segment_id}")
        print()
        
        return filtered_segment
    
    def apply_exclusion_to_campaign(self, campaign_data: Dict, 
                                  account_id: str) -> Dict:
        """
        Aplica exclusión de seguidores a toda la campaña
        """
        print("🚀 APLICANDO EXCLUSIÓN A CAMPAÑA COMPLETA")
        print("=" * 45)
        
        # 1. Recolectar seguidores
        followers = self.collect_followers(account_id)
        
        # 2. Crear lista de exclusión
        exclusion_list = self.create_exclusion_list(followers)
        
        # 3. Filtrar todas las audiencias de la campaña
        filtered_audiences = []
        total_exclusions = 0
        
        # Simular audiencias de campaña
        audience_templates = [
            {'name': 'Lookalike Trap Fans', 'type': 'lookalike', 'estimated_size': 150000},
            {'name': 'Interest Reggaeton', 'type': 'interest', 'estimated_size': 280000},
            {'name': 'Behavioral Music Lovers', 'type': 'behavioral', 'estimated_size': 320000},
            {'name': 'Custom Audience Upload', 'type': 'custom', 'estimated_size': 45000},
            {'name': 'Engagement Music Videos', 'type': 'engagement', 'estimated_size': 95000}
        ]
        
        for audience_template in audience_templates:
            filtered_segment = self.filter_audience(
                audience_template, 
                exclusion_list,
                account_id
            )
            filtered_audiences.append(filtered_segment)
            total_exclusions += filtered_segment.exclusion_count
        
        # 4. Compilar resultados de exclusión
        exclusion_results = {
            'account_id': account_id,
            'total_followers': len(followers),
            'exclusion_list_size': len(exclusion_list),
            'audiences_processed': len(filtered_audiences),
            'total_users_excluded': total_exclusions,
            'filtered_segments': filtered_audiences,
            'exclusion_settings': self.exclusion_settings,
            'processing_timestamp': datetime.now().isoformat()
        }
        
        # 5. Actualizar datos de campaña
        updated_campaign = campaign_data.copy()
        updated_campaign['follower_exclusion'] = exclusion_results
        updated_campaign['audiences'] = [
            {
                'segment_id': seg.segment_id,
                'name': f"Filtered_{seg.segment_type}_{seg.segment_id[:6]}",
                'size': seg.filtered_size,
                'exclusion_applied': True,
                'original_size': seg.original_size,
                'exclusion_percentage': seg.exclusion_percentage
            }
            for seg in filtered_audiences
        ]
        
        print("📊 RESUMEN DE EXCLUSIÓN:")
        print(f"   👥 Total seguidores: {len(followers):,}")
        print(f"   🚫 Lista exclusión: {len(exclusion_list):,}")
        print(f"   🎯 Audiencias procesadas: {len(filtered_audiences)}")
        print(f"   📉 Total usuarios excluidos: {total_exclusions:,}")
        print(f"   💾 Audiencia promedio filtrada: {sum(seg.filtered_size for seg in filtered_audiences) // len(filtered_audiences):,}")
        
        avg_exclusion = sum(seg.exclusion_percentage for seg in filtered_audiences) / len(filtered_audiences)
        print(f"   📊 Exclusión promedio: {avg_exclusion:.1f}%")
        print()
        
        return updated_campaign

# Importar datetime que faltaba
from datetime import timedelta

# Test del módulo
if __name__ == "__main__":
    print("🧪 TEST FOLLOWER EXCLUSION MODULE")
    print("=" * 40)
    
    # Crear instancia del manager
    exclusion_manager = FollowerExclusionManager()
    
    # Datos simulados de campaña
    campaign_data = {
        'campaign_id': 'camp_test_001',
        'genre': 'trap',
        'budget_total': 400,
        'target_regions': ['ES', 'MX', 'CO']
    }
    
    # Aplicar exclusión completa
    updated_campaign = exclusion_manager.apply_exclusion_to_campaign(
        campaign_data, 
        account_id='acc_trap_artist_001'
    )
    
    print("✅ TEST COMPLETADO")
    print(f"   Audiencias con exclusión: {len(updated_campaign['audiences'])}")
    print(f"   Promedio exclusión: {updated_campaign['follower_exclusion']['exclusion_list_size']:,} usuarios")