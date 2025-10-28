"""
Advanced Campaign System - Campaign Tagging
Etiquetado avanzado de campañas con género, subgénero y colaboradores
"""

import uuid
import json
import hashlib
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class GenrePrimary(Enum):
    TRAP = "trap"
    REGGAETON = "reggaeton"
    RAP = "rap"
    CORRIDO = "corrido"
    LATIN_POP = "latin_pop"
    URBAN_POP = "urban_pop"

class AudienceType(Enum):
    PROPIA = "audience_propia"           # Audiencia del artista principal
    COLABORADOR = "audience_colaborador"  # Audiencia de colaboradores
    MIXTA = "audience_mixta"             # Audiencia combinada
    NUEVA = "audience_nueva"             # Nueva audiencia objetivo
    CROSSOVER = "audience_crossover"     # Cruce entre géneros

@dataclass
class CollaboratorProfile:
    """Perfil de colaborador con métricas de audiencia"""
    name: str
    follower_count: int
    avg_engagement: float
    primary_demographics: Dict[str, float]  # {'18-24': 0.4, '25-34': 0.35, ...}
    regional_strength: Dict[str, float]     # {'MX': 0.8, 'CO': 0.6, ...}
    genre_affinity: Dict[str, float]        # {'trap': 0.9, 'reggaeton': 0.7, ...}

@dataclass
class MusicalElements:
    """Elementos musicales identificados"""
    bpm: int
    key: str
    energy_level: float  # 0.0 - 1.0
    danceability: float  # 0.0 - 1.0
    valence: float       # 0.0 - 1.0 (positivity)
    darkness_score: float # 0.0 - 1.0 (darkness/aggression)
    vocal_style: List[str]  # ['melodic', 'aggressive', 'autotune_heavy']
    instrumental_elements: List[str]  # ['808s', 'piano', 'guitar', 'strings']

@dataclass
class CampaignTags:
    """Tags completos de campaña"""
    campaign_id: str
    primary_genre: GenrePrimary
    subgenre: str
    collaborators: List[CollaboratorProfile]
    audience_composition: Dict[AudienceType, float]
    musical_elements: MusicalElements
    target_demographics: Dict[str, float]
    regional_focus: List[str]
    campaign_objectives: List[str]
    content_style: str
    ml_features: Dict[str, any]
    created_at: datetime

class CampaignTagging:
    """Sistema de etiquetado avanzado para campañas"""
    
    def __init__(self):
        # Taxonomía de subgéneros por género principal
        self.genre_taxonomy = {
            GenrePrimary.TRAP: [
                'trap_oscuro', 'trap_melodico', 'trap_comercial', 
                'trap_emo', 'trap_hardcore', 'trap_experimental'
            ],
            GenrePrimary.REGGAETON: [
                'reggaeton_clasico', 'reggaeton_pop', 'reggaeton_urbano',
                'reggaeton_romantico', 'reggaeton_hardcore', 'perreo'
            ],
            GenrePrimary.RAP: [
                'rap_consciente', 'rap_comercial', 'rap_underground',
                'rap_old_school', 'rap_trap', 'rap_experimental'
            ],
            GenrePrimary.CORRIDO: [
                'corrido_tumbado', 'corrido_tradicional', 'corrido_progresivo',
                'corrido_trap', 'corrido_banda', 'corrido_alterado'
            ]
        }
        
        # Estilos de contenido visual
        self.content_styles = [
            'urbano_oscuro', 'tropical_vibrante', 'minimalista_moderno',
            'street_culture', 'luxury_lifestyle', 'underground_raw',
            'pop_comercial', 'artistico_conceptual'
        ]
        
        # Base de datos simulada de colaboradores conocidos
        self.collaborator_database = {
            'bad_bunny': CollaboratorProfile(
                'Bad Bunny', 45000000, 8.5,
                {'18-24': 0.35, '25-34': 0.40, '35-44': 0.20, '45+': 0.05},
                {'MX': 0.9, 'CO': 0.8, 'AR': 0.7, 'ES': 0.85, 'PR': 1.0},
                {'reggaeton': 1.0, 'trap': 0.8, 'latin_pop': 0.7}
            ),
            'anuel_aa': CollaboratorProfile(
                'Anuel AA', 25000000, 7.8,
                {'18-24': 0.40, '25-34': 0.35, '35-44': 0.20, '45+': 0.05},
                {'MX': 0.8, 'CO': 0.7, 'AR': 0.6, 'ES': 0.7, 'PR': 0.9},
                {'trap': 1.0, 'reggaeton': 0.9, 'rap': 0.6}
            ),
            'natanael_cano': CollaboratorProfile(
                'Natanael Cano', 8000000, 9.2,
                {'18-24': 0.50, '25-34': 0.30, '35-44': 0.15, '45+': 0.05},
                {'MX': 1.0, 'CO': 0.4, 'AR': 0.3, 'ES': 0.5, 'US': 0.7},
                {'corrido': 1.0, 'trap': 0.8, 'corrido_tumbado': 1.0}
            )
        }
    
    def create_advanced_tags(self, campaign_data: Dict) -> CampaignTags:
        """
        Crea etiquetas avanzadas completas para campaña
        """
        print("🏷️ CREANDO ETIQUETAS AVANZADAS DE CAMPAÑA")
        print("-" * 50)
        
        # Generar ID único de campaña
        campaign_id = self.generate_campaign_id(campaign_data)
        
        # Procesar género y subgénero
        primary_genre = GenrePrimary(campaign_data['genre'])
        subgenre = self.classify_subgenre(campaign_data)
        
        print(f"🎵 Género: {primary_genre.value} → {subgenre}")
        
        # Procesar colaboradores
        collaborators = self.extract_collaborators(campaign_data)
        print(f"🤝 Colaboradores: {[c.name for c in collaborators]}")
        
        # Analizar composición de audiencia
        audience_composition = self.analyze_audience_composition(campaign_data, collaborators)
        print(f"👥 Audiencia: {[(k.value, f'{v*100:.0f}%') for k, v in audience_composition.items()]}")
        
        # Extraer elementos musicales
        musical_elements = self.extract_musical_elements(campaign_data)
        print(f"🎹 BPM: {musical_elements.bpm} | Energy: {musical_elements.energy_level:.2f}")
        
        # Definir demographics objetivo
        target_demographics = self.define_demographics(campaign_data, collaborators)
        
        # Clasificar estilo de contenido
        content_style = self.classify_content_style(campaign_data, musical_elements)
        print(f"🎬 Estilo: {content_style}")
        
        # Generar features para ML
        ml_features = self.generate_ml_features({
            'primary_genre': primary_genre,
            'subgenre': subgenre,
            'collaborators': collaborators,
            'audience_composition': audience_composition,
            'musical_elements': musical_elements,
            'regional_focus': campaign_data.get('target_regions', []),
            'content_style': content_style
        })
        
        tags = CampaignTags(
            campaign_id=campaign_id,
            primary_genre=primary_genre,
            subgenre=subgenre,
            collaborators=collaborators,
            audience_composition=audience_composition,
            musical_elements=musical_elements,
            target_demographics=target_demographics,
            regional_focus=campaign_data.get('target_regions', []),
            campaign_objectives=campaign_data.get('objectives', ['views', 'engagement']),
            content_style=content_style,
            ml_features=ml_features,
            created_at=datetime.now()
        )
        
        print(f"✅ Tags creadas: ID {campaign_id}")
        print()
        
        return tags
    
    def generate_campaign_id(self, campaign_data: Dict) -> str:
        """Genera ID único de campaña"""
        # Crear hash basado en elementos únicos
        unique_string = f"{campaign_data.get('campaign_name', '')}"
        unique_string += f"{campaign_data.get('artist_main', '')}"
        unique_string += f"{datetime.now().strftime('%Y%m%d')}"
        
        hash_object = hashlib.md5(unique_string.encode())
        return f"camp_{hash_object.hexdigest()[:8]}"
    
    def classify_subgenre(self, campaign_data: Dict) -> str:
        """
        Clasifica subgénero automáticamente basado en características musicales
        """
        genre = GenrePrimary(campaign_data['genre'])
        audio_features = campaign_data.get('audio_features', {})
        
        if genre == GenrePrimary.TRAP:
            bpm = audio_features.get('bpm', 140)
            darkness_score = audio_features.get('darkness', 0.5)
            energy = audio_features.get('energy', 0.7)
            
            if bpm > 160 and darkness_score > 0.7 and energy > 0.8:
                return 'trap_hardcore'
            elif darkness_score > 0.7:
                return 'trap_oscuro'
            elif darkness_score < 0.3 and energy < 0.6:
                return 'trap_melodico'
            elif energy > 0.9:
                return 'trap_comercial'
            else:
                return 'trap_comercial'
        
        elif genre == GenrePrimary.REGGAETON:
            valence = audio_features.get('valence', 0.6)
            danceability = audio_features.get('danceability', 0.8)
            
            if danceability > 0.9 and valence > 0.7:
                return 'perreo'
            elif valence > 0.8:
                return 'reggaeton_pop'
            elif valence < 0.4:
                return 'reggaeton_hardcore'
            else:
                return 'reggaeton_clasico'
        
        elif genre == GenrePrimary.RAP:
            energy = audio_features.get('energy', 0.7)
            bpm = audio_features.get('bpm', 120)
            
            if bpm > 150:
                return 'rap_trap'
            elif energy < 0.5:
                return 'rap_consciente'
            elif energy > 0.9:
                return 'rap_comercial'
            else:
                return 'rap_underground'
        
        elif genre == GenrePrimary.CORRIDO:
            bpm = audio_features.get('bpm', 120)
            modernity_score = audio_features.get('modernity', 0.5)
            
            if bpm > 140 and modernity_score > 0.7:
                return 'corrido_tumbado'
            elif modernity_score > 0.6:
                return 'corrido_progresivo'
            else:
                return 'corrido_tradicional'
        
        # Fallback al primer subgénero disponible
        return self.genre_taxonomy.get(genre, ['generic'])[0]
    
    def extract_collaborators(self, campaign_data: Dict) -> List[CollaboratorProfile]:
        """
        Extrae y procesa información de colaboradores
        """
        collaborator_names = campaign_data.get('collaborators', [])
        collaborators = []
        
        for name in collaborator_names:
            # Buscar en base de datos
            name_key = name.lower().replace(' ', '_')
            if name_key in self.collaborator_database:
                collaborators.append(self.collaborator_database[name_key])
            else:
                # Crear perfil estimado para colaborador desconocido
                estimated_profile = self.estimate_collaborator_profile(name, campaign_data)
                collaborators.append(estimated_profile)
        
        return collaborators
    
    def estimate_collaborator_profile(self, name: str, campaign_data: Dict) -> CollaboratorProfile:
        """
        Estima perfil de colaborador desconocido
        """
        genre = campaign_data['genre']
        
        # Estimaciones basadas en género
        if genre == 'trap':
            base_followers = 2000000
            base_engagement = 7.5
        elif genre == 'reggaeton':
            base_followers = 3500000
            base_engagement = 8.2
        elif genre == 'corrido':
            base_followers = 1200000
            base_engagement = 9.0
        else:
            base_followers = 1500000
            base_engagement = 7.0
        
        return CollaboratorProfile(
            name=name,
            follower_count=base_followers,
            avg_engagement=base_engagement,
            primary_demographics={'18-24': 0.40, '25-34': 0.35, '35-44': 0.20, '45+': 0.05},
            regional_strength={'MX': 0.6, 'CO': 0.5, 'AR': 0.4, 'ES': 0.5},
            genre_affinity={genre: 0.8, 'latin_pop': 0.4}
        )
    
    def analyze_audience_composition(self, campaign_data: Dict, 
                                   collaborators: List[CollaboratorProfile]) -> Dict[AudienceType, float]:
        """
        Analiza composición de audiencia basada en artista principal y colaboradores
        """
        composition = {}
        
        # Audiencia propia del artista principal
        artist_strength = campaign_data.get('artist_follower_count', 1000000) / 10000000
        composition[AudienceType.PROPIA] = min(0.6, 0.3 + artist_strength * 0.3)
        
        # Audiencia de colaboradores
        if collaborators:
            total_collab_strength = sum([c.follower_count for c in collaborators]) / 50000000
            composition[AudienceType.COLABORADOR] = min(0.4, total_collab_strength * 0.4)
        else:
            composition[AudienceType.COLABORADOR] = 0.0
        
        # Audiencia mixta (overlap entre artista y colaboradores)
        if collaborators:
            composition[AudienceType.MIXTA] = 0.2
        else:
            composition[AudienceType.MIXTA] = 0.0
        
        # Nueva audiencia objetivo
        used_percentage = sum(composition.values())
        composition[AudienceType.NUEVA] = max(0.1, 1.0 - used_percentage)
        
        # Normalizar para que sume 1.0
        total = sum(composition.values())
        if total > 1.0:
            for audience_type in composition:
                composition[audience_type] = composition[audience_type] / total
        
        return composition
    
    def extract_musical_elements(self, campaign_data: Dict) -> MusicalElements:
        """
        Extrae elementos musicales del audio
        """
        audio_features = campaign_data.get('audio_features', {})
        
        # Valores por defecto basados en género
        genre = campaign_data['genre']
        if genre == 'trap':
            defaults = {'bpm': 145, 'energy': 0.8, 'darkness': 0.7, 'danceability': 0.6}
        elif genre == 'reggaeton':
            defaults = {'bpm': 95, 'energy': 0.9, 'darkness': 0.3, 'danceability': 0.9}
        elif genre == 'corrido':
            defaults = {'bpm': 120, 'energy': 0.6, 'darkness': 0.4, 'danceability': 0.7}
        else:
            defaults = {'bpm': 130, 'energy': 0.7, 'darkness': 0.5, 'danceability': 0.7}
        
        return MusicalElements(
            bpm=audio_features.get('bpm', defaults['bpm']),
            key=audio_features.get('key', 'C'),
            energy_level=audio_features.get('energy', defaults['energy']),
            danceability=audio_features.get('danceability', defaults['danceability']),
            valence=audio_features.get('valence', 0.6),
            darkness_score=audio_features.get('darkness', defaults['darkness']),
            vocal_style=audio_features.get('vocal_style', ['melodic']),
            instrumental_elements=audio_features.get('instruments', ['808s', 'synth'])
        )
    
    def define_demographics(self, campaign_data: Dict, 
                          collaborators: List[CollaboratorProfile]) -> Dict[str, float]:
        """
        Define demographics objetivo basado en artista y colaboradores
        """
        # Demographics base por género
        genre = campaign_data['genre']
        if genre == 'trap':
            base_demographics = {'18-24': 0.45, '25-34': 0.35, '35-44': 0.15, '45+': 0.05}
        elif genre == 'reggaeton':
            base_demographics = {'18-24': 0.40, '25-34': 0.40, '35-44': 0.15, '45+': 0.05}
        elif genre == 'corrido':
            base_demographics = {'18-24': 0.35, '25-34': 0.30, '35-44': 0.25, '45+': 0.10}
        else:
            base_demographics = {'18-24': 0.40, '25-34': 0.35, '35-44': 0.20, '45+': 0.05}
        
        # Ajustar con colaboradores si existen
        if collaborators:
            weighted_demographics = base_demographics.copy()
            for collab in collaborators:
                weight = collab.follower_count / 10000000  # Peso basado en seguidores
                for age_group in weighted_demographics:
                    collab_demo = collab.primary_demographics.get(age_group, 0)
                    weighted_demographics[age_group] = (
                        weighted_demographics[age_group] * (1 - weight * 0.3) + 
                        collab_demo * weight * 0.3
                    )
            return weighted_demographics
        
        return base_demographics
    
    def classify_content_style(self, campaign_data: Dict, musical_elements: MusicalElements) -> str:
        """
        Clasifica estilo de contenido visual basado en género y elementos musicales
        """
        genre = campaign_data['genre']
        
        if genre == 'trap':
            if musical_elements.darkness_score > 0.7:
                return 'urbano_oscuro'
            elif musical_elements.energy_level > 0.8:
                return 'street_culture'
            else:
                return 'underground_raw'
        
        elif genre == 'reggaeton':
            if musical_elements.valence > 0.7:
                return 'tropical_vibrante'
            elif musical_elements.energy_level > 0.9:
                return 'pop_comercial'
            else:
                return 'luxury_lifestyle'
        
        elif genre == 'corrido':
            if musical_elements.bpm > 140:
                return 'street_culture'
            else:
                return 'artistico_conceptual'
        
        return 'minimalista_moderno'
    
    def generate_ml_features(self, tag_data: Dict) -> Dict[str, any]:
        """
        Genera features vectorizados para ML basado en etiquetas
        """
        features = {}
        
        # Vector de género (one-hot encoding)
        genre_vector = [0] * len(GenrePrimary)
        genre_index = list(GenrePrimary).index(tag_data['primary_genre'])
        genre_vector[genre_index] = 1
        features['genre_vector'] = genre_vector
        
        # Vector de subgénero
        all_subgenres = [sg for sublist in self.genre_taxonomy.values() for sg in sublist]
        subgenre_vector = [0] * len(all_subgenres)
        if tag_data['subgenre'] in all_subgenres:
            subgenre_index = all_subgenres.index(tag_data['subgenre'])
            subgenre_vector[subgenre_index] = 1
        features['subgenre_vector'] = subgenre_vector
        
        # Influencia de colaboradores
        total_followers = sum([c.follower_count for c in tag_data['collaborators']])
        avg_engagement = sum([c.avg_engagement for c in tag_data['collaborators']]) / max(len(tag_data['collaborators']), 1)
        features['collaborator_influence'] = min(total_followers / 50000000, 1.0)
        features['collaborator_engagement'] = avg_engagement / 10.0
        
        # Score de diversidad de audiencia
        import math
        audience_entropy = -sum([p * math.log2(p) if p > 0 else 0 
                               for p in tag_data['audience_composition'].values()])
        features['audience_diversity_score'] = audience_entropy
        
        # Vector de pesos regionales
        all_regions = ['ES', 'MX', 'CO', 'AR', 'CL', 'PE', 'EC']
        regional_weights = [1.0 if region in tag_data['regional_focus'] else 0.0 
                          for region in all_regions]
        features['regional_weight_vector'] = regional_weights
        
        # Features musicales normalizadas
        musical = tag_data['musical_elements']
        features['musical_features'] = [
            musical.bpm / 200.0,  # Normalizar BPM
            musical.energy_level,
            musical.danceability,
            musical.valence,
            musical.darkness_score
        ]
        
        # Vector de estilo de contenido
        content_style_vector = [0] * len(self.content_styles)
        if tag_data['content_style'] in self.content_styles:
            style_index = self.content_styles.index(tag_data['content_style'])
            content_style_vector[style_index] = 1
        features['content_style_vector'] = content_style_vector
        
        return features

# Ejemplo de uso
if __name__ == "__main__":
    # Datos de campaña de ejemplo
    campaign_example = {
        'campaign_name': 'Trap Oscuro 2025',
        'genre': 'trap',
        'artist_main': 'ArtistaPrincipal',
        'artist_follower_count': 5000000,
        'collaborators': ['anuel_aa'],
        'target_regions': ['ES', 'MX', 'CO'],
        'objectives': ['views', 'engagement', 'conversions'],
        'audio_features': {
            'bpm': 150,
            'energy': 0.85,
            'darkness': 0.8,
            'danceability': 0.6,
            'valence': 0.3,
            'vocal_style': ['aggressive', 'autotune_heavy'],
            'instruments': ['808s', 'dark_synth', 'guitar']
        }
    }
    
    # Crear tags avanzadas
    tagging = CampaignTagging()
    tags = tagging.create_advanced_tags(campaign_example)
    
    print("🏷️ TAGS GENERADAS:")
    print("-" * 30)
    print(f"ID: {tags.campaign_id}")
    print(f"Género: {tags.primary_genre.value} → {tags.subgenre}")
    print(f"Colaboradores: {[c.name for c in tags.collaborators]}")
    print(f"Estilo: {tags.content_style}")
    print(f"BPM: {tags.musical_elements.bpm}")
    print(f"Features ML: {len(tags.ml_features)} vectors generados")
    print("\n✅ Sistema de Etiquetado Avanzado completado!")