"""
Advanced Campaign System - Granular Tagging System
Etiquetador granular por subgénero y colaboraciones para ML avanzado
"""

import json
import random
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib

class MainGenre(Enum):
    """Géneros principales soportados"""
    TRAP = "trap"
    REGGAETON = "reggaeton"  
    RAP = "rap"
    CORRIDO = "corrido"

@dataclass
class SubGenreDefinition:
    """Definición de subgénero musical"""
    sub_genre_id: str
    display_name: str
    main_genre: MainGenre
    characteristics: List[str]
    typical_bpm_range: Tuple[int, int]
    mood_indicators: List[str]
    target_demographics: Dict[str, str]
    market_performance_modifier: float  # Multiplicador de rendimiento esperado

@dataclass
class CollaboratorProfile:
    """Perfil de colaborador musical"""
    artist_id: str
    artist_name: str
    primary_genres: List[MainGenre]
    follower_count_range: str  # "100K-500K", "1M-5M", etc.
    engagement_rate: float
    regional_strength: List[str]  # Países donde es más fuerte
    collaboration_boost_factor: float
    audience_overlap_estimates: Dict[str, float]  # % overlap con otros artistas

@dataclass
class GranularTags:
    """Etiquetas granulares completas"""
    tag_id: str
    main_genre: MainGenre
    sub_genre: str
    collaboration_artist: Optional[str]
    collaboration_type: str  # "featuring", "producer", "songwriter", "remix"
    musical_elements: Dict[str, any]
    audience_segments: Dict[str, float]
    market_predictions: Dict[str, float]
    confidence_scores: Dict[str, float]
    timestamp: datetime

class GranularTaggingSystem:
    """Sistema de etiquetado granular avanzado"""
    
    def __init__(self):
        self.sub_genre_definitions = self._initialize_sub_genres()
        self.collaborator_profiles = self._initialize_collaborators()
        self.tagging_history = []
        
        # Configuración del sistema
        self.system_config = {
            'enable_sub_genre_learning': True,
            'enable_collaboration_analysis': True,
            'confidence_threshold': 0.7,
            'market_prediction_enabled': True,
            'audience_segmentation_depth': 5
        }
    
    def _initialize_sub_genres(self) -> Dict[str, SubGenreDefinition]:
        """Inicializa definiciones de subgéneros"""
        sub_genres = {}
        
        # Subgéneros de TRAP
        trap_subgenres = [
            {
                'id': 'trap_oscuro', 'name': 'Trap Oscuro',
                'chars': ['Melodías menores', '808s pesados', 'Atmósfera dark'],
                'bpm': (140, 160), 'moods': ['agresivo', 'introspectivo', 'urbano'],
                'demographics': {'age': '18-25', 'gender': 'male_dominant'},
                'modifier': 1.15
            },
            {
                'id': 'trap_melodico', 'name': 'Trap Melódico',
                'chars': ['Melodías pegajosas', 'Auto-tune', 'Hooks comerciales'],
                'bpm': (130, 150), 'moods': ['comercial', 'romántico', 'aspiracional'],
                'demographics': {'age': '16-28', 'gender': 'mixed'},
                'modifier': 1.25
            },
            {
                'id': 'trap_latino', 'name': 'Trap Latino',
                'chars': ['Influencias latinas', 'Spanglish', 'Ritmos regionales'],
                'bpm': (135, 155), 'moods': ['cultural', 'festivo', 'orgulloso'],
                'demographics': {'age': '18-30', 'gender': 'mixed'},
                'modifier': 1.30
            }
        ]
        
        # Subgéneros de REGGAETON
        reggaeton_subgenres = [
            {
                'id': 'reggaeton_clasico', 'name': 'Reggaeton Clásico',
                'chars': ['Dembow tradicional', 'Flow agresivo', 'Letras directas'],
                'bpm': (90, 100), 'moods': ['agresivo', 'sexual', 'urbano'],
                'demographics': {'age': '20-35', 'gender': 'male_leaning'},
                'modifier': 1.20
            },
            {
                'id': 'perreo_intenso', 'name': 'Perreo Intenso',
                'chars': ['Ritmo acelerado', 'Letras explícitas', 'Enfoque club'],
                'bpm': (95, 105), 'moods': ['sexual', 'festivo', 'provocativo'],
                'demographics': {'age': '18-28', 'gender': 'mixed'},
                'modifier': 1.35
            },
            {
                'id': 'reggaeton_pop', 'name': 'Reggaeton Pop',
                'chars': ['Melodías comerciales', 'Producción pulida', 'Radio-friendly'],
                'bpm': (85, 95), 'moods': ['comercial', 'romántico', 'mainstream'],
                'demographics': {'age': '16-40', 'gender': 'female_leaning'},
                'modifier': 1.40
            }
        ]
        
        # Subgéneros de RAP
        rap_subgenres = [
            {
                'id': 'rap_hardcore', 'name': 'Rap Hardcore',
                'chars': ['Letras complejas', 'Flow rápido', 'Beats agresivos'],
                'bpm': (80, 100), 'moods': ['agresivo', 'técnico', 'underground'],
                'demographics': {'age': '18-30', 'gender': 'male_dominant'},
                'modifier': 1.10
            },
            {
                'id': 'rap_comercial', 'name': 'Rap Comercial',
                'chars': ['Hooks pegajosos', 'Producción mainstream', 'Temas universales'],
                'bpm': (75, 95), 'moods': ['comercial', 'aspiracional', 'optimista'],
                'demographics': {'age': '16-35', 'gender': 'mixed'},
                'modifier': 1.25
            }
        ]
        
        # Subgéneros de CORRIDO
        corrido_subgenres = [
            {
                'id': 'corrido_tumbado', 'name': 'Corrido Tumbado',
                'chars': ['Fusión moderna', 'Elementos trap', 'Narrativa urbana'],
                'bpm': (70, 90), 'moods': ['narrativo', 'moderno', 'regional'],
                'demographics': {'age': '18-35', 'gender': 'male_leaning'},
                'modifier': 1.15
            },
            {
                'id': 'corrido_alterado', 'name': 'Corrido Alterado',
                'chars': ['Ritmo acelerado', 'Letras explícitas', 'Estilo norteño'],
                'bpm': (90, 110), 'moods': ['agresivo', 'regional', 'auténtico'],
                'demographics': {'age': '20-40', 'gender': 'male_dominant'},
                'modifier': 1.05
            }
        ]
        
        # Crear objetos SubGenreDefinition
        all_subgenres = trap_subgenres + reggaeton_subgenres + rap_subgenres + corrido_subgenres
        
        for sg_data in all_subgenres:
            main_genre_map = {
                'trap_': MainGenre.TRAP,
                'reggaeton_': MainGenre.REGGAETON,
                'perreo_': MainGenre.REGGAETON,
                'rap_': MainGenre.RAP,
                'corrido_': MainGenre.CORRIDO
            }
            
            main_genre = None
            for prefix, genre in main_genre_map.items():
                if sg_data['id'].startswith(prefix):
                    main_genre = genre
                    break
            
            sub_genre = SubGenreDefinition(
                sub_genre_id=sg_data['id'],
                display_name=sg_data['name'],
                main_genre=main_genre,
                characteristics=sg_data['chars'],
                typical_bpm_range=sg_data['bpm'],
                mood_indicators=sg_data['moods'],
                target_demographics=sg_data['demographics'],
                market_performance_modifier=sg_data['modifier']
            )
            
            sub_genres[sg_data['id']] = sub_genre
        
        return sub_genres
    
    def _initialize_collaborators(self) -> Dict[str, CollaboratorProfile]:
        """Inicializa perfiles de colaboradores"""
        collaborators = {}
        
        # Colaboradores de diferentes niveles
        collaborator_data = [
            {
                'id': 'bad_bunny', 'name': 'Bad Bunny',
                'genres': [MainGenre.REGGAETON, MainGenre.TRAP],
                'followers': '10M-50M', 'engagement': 8.5,
                'regions': ['PR', 'ES', 'MX', 'CO', 'AR'],
                'boost': 2.5, 'overlap': {'anuel_aa': 0.45, 'daddy_yankee': 0.35}
            },
            {
                'id': 'anuel_aa', 'name': 'Anuel AA',
                'genres': [MainGenre.TRAP, MainGenre.REGGAETON],
                'followers': '5M-20M', 'engagement': 7.2,
                'regions': ['PR', 'ES', 'MX', 'CO'],
                'boost': 2.0, 'overlap': {'bad_bunny': 0.45, 'ozuna': 0.40}
            },
            {
                'id': 'daddy_yankee', 'name': 'Daddy Yankee',
                'genres': [MainGenre.REGGAETON],
                'followers': '20M-50M', 'engagement': 6.8,
                'regions': ['PR', 'ES', 'MX', 'CO', 'AR', 'CL'],
                'boost': 2.2, 'overlap': {'bad_bunny': 0.35, 'don_omar': 0.50}
            },
            {
                'id': 'j_balvin', 'name': 'J Balvin',
                'genres': [MainGenre.REGGAETON],
                'followers': '15M-40M', 'engagement': 7.5,
                'regions': ['CO', 'MX', 'ES', 'AR', 'PE'],
                'boost': 2.3, 'overlap': {'maluma': 0.55, 'karol_g': 0.40}
            },
            {
                'id': 'peso_pluma', 'name': 'Peso Pluma',
                'genres': [MainGenre.CORRIDO],
                'followers': '2M-10M', 'engagement': 9.2,
                'regions': ['MX', 'US'],
                'boost': 1.8, 'overlap': {'natanael_cano': 0.60, 'junior_h': 0.45}
            }
        ]
        
        for collab_data in collaborator_data:
            collaborator = CollaboratorProfile(
                artist_id=collab_data['id'],
                artist_name=collab_data['name'],
                primary_genres=collab_data['genres'],
                follower_count_range=collab_data['followers'],
                engagement_rate=collab_data['engagement'],
                regional_strength=collab_data['regions'],
                collaboration_boost_factor=collab_data['boost'],
                audience_overlap_estimates=collab_data['overlap']
            )
            collaborators[collab_data['id']] = collaborator
        
        return collaborators
    
    def analyze_musical_content(self, content_data: Dict) -> Dict[str, any]:
        """
        Analiza contenido musical y detecta características granulares
        """
        print("🎵 ANALIZANDO CONTENIDO MUSICAL GRANULAR")
        print("-" * 40)
        
        # Simular análisis de audio (en producción usar librerías de audio ML)
        detected_bpm = random.randint(70, 160)
        detected_key = random.choice(['C', 'D', 'E', 'F', 'G', 'A', 'B']) + random.choice(['', 'm'])
        
        # Análisis de elementos musicales
        musical_elements = {
            'bpm': detected_bpm,
            'key': detected_key,
            'energy_level': random.uniform(0.3, 0.95),
            'danceability': random.uniform(0.4, 0.9),
            'valence': random.uniform(0.2, 0.8),  # Positividad
            'acousticness': random.uniform(0.05, 0.3),
            'instrumentalness': random.uniform(0.0, 0.1),
            'has_vocal_auto_tune': random.random() > 0.4,
            'has_808_drums': random.random() > 0.6,
            'has_reggaeton_dembow': random.random() > 0.3,
            'lyrical_themes': random.sample([
                'amor', 'dinero', 'fiestas', 'calle', 'éxito', 'desamor', 'poder', 'familia'
            ], k=random.randint(2, 4))
        }
        
        print(f"   🎼 BPM detectado: {detected_bpm}")
        print(f"   🎹 Key: {detected_key}")
        print(f"   ⚡ Energy: {musical_elements['energy_level']:.2f}")
        print(f"   💃 Danceability: {musical_elements['danceability']:.2f}")
        print(f"   🎤 Auto-tune: {'Sí' if musical_elements['has_vocal_auto_tune'] else 'No'}")
        print(f"   🥁 808s: {'Sí' if musical_elements['has_808_drums'] else 'No'}")
        print()
        
        return musical_elements
    
    def classify_sub_genre(self, main_genre: MainGenre, 
                          musical_elements: Dict) -> Tuple[str, float]:
        """
        Clasifica subgénero basado en elementos musicales
        """
        print(f"🏷️ CLASIFICANDO SUBGÉNERO DE {main_genre.value.upper()}")
        print("-" * 35)
        
        # Filtrar subgéneros del género principal
        candidate_subgenres = [
            sg for sg in self.sub_genre_definitions.values()
            if sg.main_genre == main_genre
        ]
        
        best_match = None
        best_score = 0
        
        for sub_genre in candidate_subgenres:
            score = 0
            
            # Score por BPM
            bpm = musical_elements.get('bpm', 120)
            if sub_genre.typical_bpm_range[0] <= bpm <= sub_genre.typical_bpm_range[1]:
                score += 0.3
            else:
                # Penalizar según distancia
                distance = min(
                    abs(bpm - sub_genre.typical_bpm_range[0]),
                    abs(bpm - sub_genre.typical_bpm_range[1])
                )
                score += max(0, 0.3 - (distance / 100))
            
            # Score por elementos específicos
            if main_genre == MainGenre.TRAP:
                if musical_elements.get('has_808_drums', False):
                    score += 0.25
                if musical_elements.get('energy_level', 0) > 0.7:
                    score += 0.2
                    
            elif main_genre == MainGenre.REGGAETON:
                if musical_elements.get('has_reggaeton_dembow', False):
                    score += 0.3
                if musical_elements.get('danceability', 0) > 0.7:
                    score += 0.2
            
            # Score por mood indicators
            lyrical_themes = musical_elements.get('lyrical_themes', [])
            mood_matches = len(set(lyrical_themes) & set(['agresivo', 'sexual', 'comercial']))
            score += (mood_matches / len(sub_genre.mood_indicators)) * 0.25
            
            if score > best_score:
                best_score = score
                best_match = sub_genre
        
        confidence = min(best_score, 1.0)
        
        if best_match:
            print(f"   🎯 Subgénero detectado: {best_match.display_name}")
            print(f"   📊 Confianza: {confidence:.3f}")
            print(f"   📈 Multiplicador mercado: {best_match.market_performance_modifier:.2f}x")
            print()
            return best_match.sub_genre_id, confidence
        else:
            print("   ❓ No se pudo clasificar subgénero")
            print()
            return "generico", 0.5
    
    def analyze_collaboration(self, collaboration_data: Dict) -> Dict[str, any]:
        """
        Analiza colaboración y calcula métricas de impacto
        """
        if not collaboration_data or collaboration_data is None:
            return {
                'collaboration_type': 'none',
                'collaborator_profile': None,
                'boost_factor': 1.0,
                'audience_expansion': 0
            }
            
        collaborator_id = collaboration_data.get('artist_id')
        collaboration_type = collaboration_data.get('type', 'featuring')
        
        if not collaborator_id or collaborator_id not in self.collaborator_profiles:
            return {
                'has_collaboration': False,
                'boost_factor': 1.0,
                'confidence': 0.0
            }
        
        print(f"🤝 ANALIZANDO COLABORACIÓN CON {collaborator_id.upper()}")
        print("-" * 40)
        
        collaborator = self.collaborator_profiles[collaborator_id]
        
        # Calcular factores de boost
        base_boost = collaborator.collaboration_boost_factor
        
        # Modificadores por tipo de colaboración
        type_multipliers = {
            'featuring': 1.0,
            'producer': 0.8,
            'songwriter': 0.6,
            'remix': 0.7
        }
        
        type_multiplier = type_multipliers.get(collaboration_type, 1.0)
        final_boost = base_boost * type_multiplier
        
        # Calcular audiencia expandida
        audience_expansion = {
            'estimated_new_reach': int(random.uniform(0.2, 0.4) * 1000000),  # 200K-400K nuevos usuarios
            'cross_audience_percentage': random.uniform(15, 35),  # 15-35% audiencia cruzada
            'engagement_boost': final_boost,
            'regional_expansion': collaborator.regional_strength
        }
        
        print(f"   🎤 Artista: {collaborator.artist_name}")
        print(f"   🔄 Tipo: {collaboration_type}")
        print(f"   🚀 Boost factor: {final_boost:.2f}x")
        print(f"   👥 Audiencia nueva estimada: {audience_expansion['estimated_new_reach']:,}")
        print(f"   🌍 Expansión regional: {', '.join(collaborator.regional_strength[:3])}")
        print()
        
        return {
            'has_collaboration': True,
            'collaborator_profile': collaborator,
            'collaboration_type': collaboration_type,
            'boost_factor': final_boost,
            'audience_expansion': audience_expansion,
            'confidence': 0.9
        }
    
    def create_granular_tags(self, content_data: Dict) -> GranularTags:
        """
        Crea etiquetas granulares completas para contenido
        """
        print("🏗️ CREANDO ETIQUETAS GRANULARES COMPLETAS")
        print("=" * 45)
        
        # 1. Determinar género principal
        main_genre_str = content_data.get('genre', 'trap').lower()
        main_genre = MainGenre(main_genre_str)
        
        # 2. Analizar elementos musicales
        musical_elements = self.analyze_musical_content(content_data)
        
        # 3. Clasificar subgénero
        sub_genre_id, genre_confidence = self.classify_sub_genre(main_genre, musical_elements)
        
        # 4. Analizar colaboración si existe
        collaboration_analysis = {}
        if 'collaboration' in content_data:
            collaboration_analysis = self.analyze_collaboration(content_data['collaboration'])
        else:
            collaboration_analysis = {'has_collaboration': False, 'boost_factor': 1.0, 'confidence': 1.0}
        
        # 5. Generar segmentos de audiencia
        audience_segments = self._generate_audience_segments(
            main_genre, sub_genre_id, collaboration_analysis
        )
        
        # 6. Predecir rendimiento de mercado
        market_predictions = self._predict_market_performance(
            sub_genre_id, collaboration_analysis, musical_elements
        )
        
        # 7. Calcular scores de confianza
        confidence_scores = {
            'genre_classification': genre_confidence,
            'sub_genre_classification': genre_confidence,
            'collaboration_analysis': collaboration_analysis.get('confidence', 1.0),
            'audience_segmentation': random.uniform(0.75, 0.95),
            'market_prediction': random.uniform(0.70, 0.90),
            'overall_confidence': (
                genre_confidence + 
                collaboration_analysis.get('confidence', 1.0) + 
                random.uniform(0.75, 0.95)
            ) / 3
        }
        
        # 8. Generar ID único
        tag_id = hashlib.md5(
            f"{main_genre.value}_{sub_genre_id}_{content_data.get('title', 'untitled')}_{datetime.now()}".encode()
        ).hexdigest()[:16]
        
        # 9. Crear objeto final
        collaborator_profile = collaboration_analysis.get('collaborator_profile')
        artist_name = collaborator_profile.artist_name if collaborator_profile else None
        
        granular_tags = GranularTags(
            tag_id=tag_id,
            main_genre=main_genre,
            sub_genre=sub_genre_id,
            collaboration_artist=artist_name,
            collaboration_type=collaboration_analysis.get('collaboration_type', 'none'),
            musical_elements=musical_elements,
            audience_segments=audience_segments,
            market_predictions=market_predictions,
            confidence_scores=confidence_scores,
            timestamp=datetime.now()
        )
        
        # Guardar en historial
        self.tagging_history.append(granular_tags)
        
        print("✅ ETIQUETAS GRANULARES COMPLETADAS")
        print(f"   🆔 Tag ID: {tag_id}")
        print(f"   🎵 Género: {main_genre.value} → {sub_genre_id}")
        print(f"   🤝 Colaboración: {collaboration_analysis.get('collaboration_type', 'none')}")
        print(f"   🎯 Confianza general: {confidence_scores['overall_confidence']:.3f}")
        print(f"   📊 Segmentos audiencia: {len(audience_segments)}")
        print()
        
        return granular_tags
    
    def _generate_audience_segments(self, main_genre: MainGenre, 
                                  sub_genre_id: str,
                                  collaboration_analysis: Dict) -> Dict[str, float]:
        """Genera segmentos de audiencia específicos"""
        segments = {}
        
        # Segmentos base por género
        base_segments = {
            MainGenre.TRAP: {
                'trap_hardcore_fans': 0.25,
                'urban_music_lovers': 0.30,
                'young_male_18_25': 0.20,
                'night_listeners': 0.15,
                'hip_hop_crossover': 0.10
            },
            MainGenre.REGGAETON: {
                'reggaeton_traditional': 0.20,
                'latino_mainstream': 0.35,
                'party_goers': 0.25,
                'dance_music_fans': 0.15,
                'latin_pride': 0.05
            }
        }
        
        segments = base_segments.get(main_genre, {
            'generic_music_fans': 0.60,
            'genre_explorers': 0.25,
            'trendfollowers': 0.15
        })
        
        # Modificar por colaboración
        if collaboration_analysis.get('has_collaboration', False):
            collaborator = collaboration_analysis.get('collaborator_profile')
            if collaborator:
                # Añadir audiencia del colaborador
                segments[f"{collaborator.artist_id}_fans"] = random.uniform(0.10, 0.25)
                
                # Normalizar para que sume 1.0
                total = sum(segments.values())
                segments = {k: v/total for k, v in segments.items()}
        
        return segments
    
    def _predict_market_performance(self, sub_genre_id: str,
                                  collaboration_analysis: Dict,
                                  musical_elements: Dict) -> Dict[str, float]:
        """Predice rendimiento de mercado"""
        sub_genre_def = self.sub_genre_definitions.get(sub_genre_id)
        base_modifier = sub_genre_def.market_performance_modifier if sub_genre_def else 1.0
        
        # Factor de colaboración
        collab_boost = collaboration_analysis.get('boost_factor', 1.0)
        
        # Factores musicales
        energy_factor = 1.0 + (musical_elements.get('energy_level', 0.5) - 0.5) * 0.3
        dance_factor = 1.0 + (musical_elements.get('danceability', 0.5) - 0.5) * 0.2
        
        # Predicciones finales
        predictions = {
            'ctr_multiplier': base_modifier * collab_boost * energy_factor,
            'engagement_multiplier': base_modifier * collab_boost * dance_factor,
            'virality_score': min((base_modifier * collab_boost * energy_factor * dance_factor) / 2, 2.0),
            'market_penetration': random.uniform(0.15, 0.45),
            'cross_genre_appeal': random.uniform(0.05, 0.25)
        }
        
        return predictions

# Test del módulo
if __name__ == "__main__":
    print("🧪 TEST GRANULAR TAGGING SYSTEM")
    print("=" * 35)
    
    # Crear instancia del sistema
    tagging_system = GranularTaggingSystem()
    
    # Contenido de prueba con colaboración
    content_data = {
        'title': 'Noche de Perreo (feat. Anuel AA)',
        'genre': 'reggaeton',
        'collaboration': {
            'artist_id': 'anuel_aa',
            'type': 'featuring'
        },
        'estimated_duration': 195
    }
    
    # Crear etiquetas granulares
    tags = tagging_system.create_granular_tags(content_data)
    
    print("✅ TEST COMPLETADO")
    print(f"   Tag ID: {tags.tag_id}")
    print(f"   Subgénero: {tags.sub_genre}")
    print(f"   Colaborador: {tags.collaboration_artist}")
    print(f"   Confianza: {tags.confidence_scores['overall_confidence']:.3f}")