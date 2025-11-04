"""
🔥 CULTURAL TREND MINER

Detecta microtendencias emergentes en tiempo real desde múltiples fuentes para
anticipar qué contenido será viral antes que la competencia.

CAPACIDADES:
- Scraping de TikTok Creative Center, YouTube Trending, Spotify Charts
- API de Reddit para comunidades musicales (r/hiphopheads, r/trap)
- Detección de sonidos virales y estilos visuales trending
- Análisis de keywords emergentes con tasa de crecimiento
- Scoring de tendencias por fase: emergente → creciendo → pico → decayendo
- Alertas proactivas cuando tendencia coincide con estilo del artista
- Integración con PlatformAlgorithmKnowledge para timing óptimo

ARQUITECTURA:
- TrendScrapers: extractores especializados por plataforma
- TrendAnalyzer: procesamiento y scoring de tendencias
- MicrotrendDetector: identifica patrones emergentes
- TrendScorer: calcula fase y duración estimada
- TrendStorage: persistencia y histórico
- TrendNotifier: alertas proactivas vía Telegram
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import re
import aiohttp
from collections import Counter, defaultdict
import statistics

# Web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup

# Data processing
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN

# APIs
from googleapiclient.discovery import build
import praw
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Database
from sqlalchemy import create_engine, text
import redis

# Internal
from config.app_settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class TrendPhase(Enum):
    """Fases del ciclo de vida de una tendencia"""
    EMERGING = "emergente"      # 0-20% del pico estimado
    GROWING = "creciendo"       # 20-60% del pico estimado  
    PEAK = "pico"              # 60-80% del pico estimado
    DECLINING = "decayendo"     # 80-100% del pico estimado
    DEAD = "muerta"            # Después del pico, trending hacia 0

@dataclass
class TrendData:
    """Estructura de datos para una tendencia"""
    trend_id: str
    keyword: str
    platform: str
    mentions_count: int
    growth_rate: float  # Porcentaje de crecimiento semanal
    phase: TrendPhase
    estimated_peak_date: Optional[datetime]
    estimated_duration_days: int
    related_keywords: List[str]
    sample_content: List[str]  # Ejemplos de contenido con esta tendencia
    confidence_score: float  # 0.0 a 1.0
    detected_at: datetime
    last_updated: datetime
    
@dataclass
class VisualTrend:
    """Tendencia visual específica"""
    trend_id: str
    description: str  # "morado oscuro + drill", "neon verde + trap"
    color_palette: List[str]  # ["#8B00FF", "#4B0082"]
    effects_used: List[str]  # ["glow", "grain", "vhs"]
    popularity_score: float
    platforms: List[str]  # Dónde es más popular
    sample_videos: List[str]  # URLs de ejemplo
    
@dataclass
class SoundTrend:
    """Tendencia de audio específica"""
    trend_id: str
    audio_id: str  # ID del audio en TikTok/IG
    title: str
    artist: Optional[str]
    genre: str
    usage_count: int
    growth_rate: float
    duration_seconds: int
    mood_tags: List[str]  # ["energetic", "dark", "romantic"]
    sample_videos: List[str]

@dataclass
class TrendAlert:
    """Alerta de tendencia relevante"""
    alert_id: str
    trend_data: TrendData
    relevance_score: float  # Qué tan relevante es para el artista
    recommended_action: str
    urgency_level: str  # "high", "medium", "low"
    content_suggestions: List[str]
    created_at: datetime


class TikTokCreativeCenterScraper:
    """Scraper especializado para TikTok Creative Center"""
    
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
    async def scrape_trending_sounds(self, max_sounds: int = 50) -> List[SoundTrend]:
        """Extrae sonidos trending de TikTok Creative Center"""
        sounds = []
        driver = None
        
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get("https://ads.tiktok.com/business/creativecenter/inspiration/popular/music/pc/en")
            
            # Esperar carga
            await asyncio.sleep(5)
            
            # Scroll para cargar más contenido
            for _ in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            # Extraer elementos de música
            music_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='music-card']")[:max_sounds]
            
            for i, element in enumerate(music_elements):
                try:
                    # Extraer datos del sonido
                    title_elem = element.find_element(By.CSS_SELECTOR, ".music-title")
                    artist_elem = element.find_element(By.CSS_SELECTOR, ".music-artist")
                    usage_elem = element.find_element(By.CSS_SELECTOR, ".usage-count")
                    
                    # Calcular growth rate basado en posición (aproximación)
                    growth_rate = max(0, (max_sounds - i) / max_sounds * 100)
                    
                    sound_trend = SoundTrend(
                        trend_id=f"tiktok_sound_{i}_{datetime.now().strftime('%Y%m%d')}",
                        audio_id=f"tiktok_audio_{i}",
                        title=title_elem.text.strip(),
                        artist=artist_elem.text.strip() if artist_elem else None,
                        genre=self._classify_genre(title_elem.text),
                        usage_count=self._parse_usage_count(usage_elem.text),
                        growth_rate=growth_rate,
                        duration_seconds=30,  # TikTok default
                        mood_tags=self._extract_mood_tags(title_elem.text),
                        sample_videos=[]
                    )
                    sounds.append(sound_trend)
                    
                except Exception as e:
                    logger.debug(f"Error extrayendo sonido individual: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping TikTok Creative Center sounds: {e}")
        finally:
            if driver:
                driver.quit()
        
        return sounds

    async def scrape_trending_hashtags(self, max_hashtags: int = 100) -> List[TrendData]:
        """Extrae hashtags trending con datos de crecimiento"""
        trends = []
        driver = None
        
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get("https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en")
            
            await asyncio.sleep(5)
            
            # Scroll para cargar más hashtags
            for _ in range(10):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(1)
            
            hashtag_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='hashtag-card']")[:max_hashtags]
            
            for i, element in enumerate(hashtag_elements):
                try:
                    hashtag_elem = element.find_element(By.CSS_SELECTOR, ".hashtag-name")
                    count_elem = element.find_element(By.CSS_SELECTOR, ".post-count")
                    
                    hashtag = hashtag_elem.text.strip().replace('#', '')
                    count = self._parse_count(count_elem.text)
                    
                    # Estimar growth rate basado en posición
                    growth_rate = max(0, (max_hashtags - i) / max_hashtags * 200)
                    
                    trend = TrendData(
                        trend_id=f"tiktok_hashtag_{hashtag}_{datetime.now().strftime('%Y%m%d')}",
                        keyword=hashtag,
                        platform="tiktok",
                        mentions_count=count,
                        growth_rate=growth_rate,
                        phase=self._determine_phase(growth_rate),
                        estimated_peak_date=self._estimate_peak_date(growth_rate),
                        estimated_duration_days=self._estimate_duration(hashtag),
                        related_keywords=self._find_related_keywords(hashtag),
                        sample_content=[],
                        confidence_score=min(0.9, growth_rate / 100),
                        detected_at=datetime.now(),
                        last_updated=datetime.now()
                    )
                    
                    trends.append(trend)
                    
                except Exception as e:
                    logger.debug(f"Error extrayendo hashtag individual: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping TikTok hashtags: {e}")
        finally:
            if driver:
                driver.quit()
        
        return trends

    def _classify_genre(self, title: str) -> str:
        """Clasifica género musical basado en el título"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['trap', 'drill']):
            return 'trap'
        elif any(word in title_lower for word in ['reggaeton', 'perreo', 'dembow']):
            return 'reggaeton'
        elif any(word in title_lower for word in ['pop', 'mainstream']):
            return 'pop'
        elif any(word in title_lower for word in ['rock', 'metal']):
            return 'rock'
        else:
            return 'urban'

    def _parse_usage_count(self, text: str) -> int:
        """Parsea contador de usos de TikTok"""
        if not text:
            return 0
        text = text.lower().replace(',', '').replace('k', '000').replace('m', '000000')
        try:
            return int(''.join(filter(str.isdigit, text)))
        except:
            return 0

    def _parse_count(self, text: str) -> int:
        """Parsea contadores generales"""
        if not text:
            return 0
        text = text.lower()
        multiplier = 1
        if 'k' in text:
            multiplier = 1000
        elif 'm' in text:
            multiplier = 1000000
        elif 'b' in text:
            multiplier = 1000000000
        
        try:
            number = float(''.join(filter(lambda x: x.isdigit() or x == '.', text)))
            return int(number * multiplier)
        except:
            return 0

    def _extract_mood_tags(self, title: str) -> List[str]:
        """Extrae tags de mood del título"""
        title_lower = title.lower()
        mood_keywords = {
            'energetic': ['energy', 'hype', 'fire', 'pump'],
            'dark': ['dark', 'shadow', 'night', 'devil'],
            'romantic': ['love', 'heart', 'romantic', 'baby'],
            'party': ['party', 'club', 'dance', 'vibe'],
            'chill': ['chill', 'relax', 'smooth', 'calm']
        }
        
        detected_moods = []
        for mood, keywords in mood_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                detected_moods.append(mood)
        
        return detected_moods if detected_moods else ['neutral']

    def _determine_phase(self, growth_rate: float) -> TrendPhase:
        """Determina fase basada en tasa de crecimiento"""
        if growth_rate > 150:
            return TrendPhase.PEAK
        elif growth_rate > 80:
            return TrendPhase.GROWING
        elif growth_rate > 30:
            return TrendPhase.EMERGING
        elif growth_rate > 0:
            return TrendPhase.DECLINING
        else:
            return TrendPhase.DEAD

    def _estimate_peak_date(self, growth_rate: float) -> Optional[datetime]:
        """Estima cuándo llegará al pico"""
        if growth_rate > 100:
            days_to_peak = 3  # Ya está cerca del pico
        elif growth_rate > 50:
            days_to_peak = 7
        elif growth_rate > 20:
            days_to_peak = 14
        else:
            days_to_peak = 30
        
        return datetime.now() + timedelta(days=days_to_peak)

    def _estimate_duration(self, keyword: str) -> int:
        """Estima duración de la tendencia en días"""
        keyword_lower = keyword.lower()
        
        # Tendencias relacionadas con música duran más
        if any(word in keyword_lower for word in ['music', 'song', 'beat', 'remix']):
            return 30
        # Challenges y memes duran menos
        elif any(word in keyword_lower for word in ['challenge', 'trend', 'meme', 'viral']):
            return 14
        # Eventos específicos duran muy poco
        elif any(word in keyword_lower for word in ['event', 'live', 'breaking', 'news']):
            return 7
        else:
            return 21  # Default 3 semanas

    def _find_related_keywords(self, main_keyword: str) -> List[str]:
        """Encuentra keywords relacionadas"""
        # Esto es una implementación básica, en producción se usaría embeddings o API
        music_related = {
            'trap': ['drill', 'beat', 'producer', 'studio'],
            'reggaeton': ['perreo', 'dembow', 'latino', 'urban'],
            'drill': ['trap', 'uk', 'chicago', 'beat'],
            'freestyle': ['cypher', 'battle', 'improv', 'flow']
        }
        
        main_lower = main_keyword.lower()
        for key, related in music_related.items():
            if key in main_lower:
                return related
        
        return []


class YouTubeTrendingScraper:
    """Scraper para YouTube Trending y datos de música"""
    
    def __init__(self):
        self.youtube_api_key = settings.YOUTUBE_API_KEY
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key) if self.youtube_api_key else None

    async def scrape_trending_music(self, region_code: str = "ES", max_videos: int = 50) -> List[TrendData]:
        """Extrae videos trending de la categoría música"""
        if not self.youtube:
            logger.warning("YouTube API no configurada")
            return []
        
        trends = []
        
        try:
            # Videos trending en categoría música (ID 10)
            request = self.youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode=region_code,
                videoCategoryId="10",  # Música
                maxResults=max_videos
            )
            
            response = request.execute()
            
            for video in response['items']:
                snippet = video['snippet']
                stats = video['statistics']
                
                # Extraer keywords del título y descripción
                title = snippet['title']
                description = snippet.get('description', '')
                keywords = self._extract_youtube_keywords(title, description)
                
                view_count = int(stats.get('viewCount', 0))
                like_count = int(stats.get('likeCount', 0))
                
                # Calcular growth rate basado en ratio views/tiempo
                published_at = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                hours_since_published = (datetime.now(published_at.tzinfo) - published_at).total_seconds() / 3600
                
                if hours_since_published > 0:
                    views_per_hour = view_count / hours_since_published
                    # Normalizar a porcentaje (muy aproximado)
                    growth_rate = min(200, views_per_hour / 10000 * 100)
                else:
                    growth_rate = 0
                
                for keyword in keywords:
                    trend = TrendData(
                        trend_id=f"youtube_music_{keyword}_{video['id']}",
                        keyword=keyword,
                        platform="youtube",
                        mentions_count=view_count,
                        growth_rate=growth_rate,
                        phase=self._determine_phase(growth_rate),
                        estimated_peak_date=self._estimate_peak_date(growth_rate),
                        estimated_duration_days=45,  # Videos de música duran más
                        related_keywords=self._find_related_keywords(keyword),
                        sample_content=[f"https://youtube.com/watch?v={video['id']}"],
                        confidence_score=min(0.95, like_count / max(view_count, 1) * 10),
                        detected_at=datetime.now(),
                        last_updated=datetime.now()
                    )
                    
                    trends.append(trend)
                    
        except Exception as e:
            logger.error(f"Error scraping YouTube trending: {e}")
        
        return trends

    def _extract_youtube_keywords(self, title: str, description: str) -> List[str]:
        """Extrae keywords relevantes de título y descripción"""
        text = f"{title} {description}".lower()
        
        # Keywords musicales relevantes
        music_keywords = [
            'trap', 'drill', 'reggaeton', 'hip hop', 'rap', 'freestyle', 'beat',
            'remix', 'cover', 'acoustic', 'live', 'session', 'cypher', 'battle',
            'producer', 'studio', 'unreleased', 'leaked', 'exclusive', 'premiere'
        ]
        
        found_keywords = []
        for keyword in music_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        # También buscar hashtags
        hashtags = re.findall(r'#(\w+)', text)
        found_keywords.extend([tag for tag in hashtags if len(tag) > 3])
        
        return list(set(found_keywords))  # Remover duplicados

    def _determine_phase(self, growth_rate: float) -> TrendPhase:
        """Determina fase basada en tasa de crecimiento"""
        if growth_rate > 100:
            return TrendPhase.PEAK
        elif growth_rate > 50:
            return TrendPhase.GROWING
        elif growth_rate > 20:
            return TrendPhase.EMERGING
        elif growth_rate > 0:
            return TrendPhase.DECLINING
        else:
            return TrendPhase.DEAD

    def _estimate_peak_date(self, growth_rate: float) -> Optional[datetime]:
        """Estima cuándo llegará al pico"""
        if growth_rate > 80:
            days_to_peak = 2
        elif growth_rate > 40:
            days_to_peak = 7
        elif growth_rate > 15:
            days_to_peak = 14
        else:
            days_to_peak = 21
        
        return datetime.now() + timedelta(days=days_to_peak)

    def _find_related_keywords(self, main_keyword: str) -> List[str]:
        """Encuentra keywords relacionadas"""
        relations = {
            'trap': ['drill', 'mumble rap', 'autotune', 'beat'],
            'drill': ['trap', 'uk drill', 'chicago drill', 'street'],
            'reggaeton': ['perreo', 'dembow', 'moombahton', 'latino'],
            'freestyle': ['battle', 'cypher', 'improv', 'flow'],
            'beat': ['instrumental', 'producer', 'type beat', 'loop']
        }
        
        return relations.get(main_keyword.lower(), [])


class SpotifyChartsScraper:
    """Scraper para Spotify Charts y datos de popularidad"""
    
    def __init__(self):
        if settings.SPOTIFY_CLIENT_ID and settings.SPOTIFY_CLIENT_SECRET:
            credentials = SpotifyClientCredentials(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET
            )
            self.spotify = spotipy.Spotify(client_credentials_manager=credentials)
        else:
            self.spotify = None
            logger.warning("Spotify credentials no configuradas")

    async def scrape_viral_tracks(self, country: str = "ES", max_tracks: int = 50) -> List[TrendData]:
        """Extrae tracks virales de Spotify Charts"""
        if not self.spotify:
            return []
        
        trends = []
        
        try:
            # Obtener playlist "Viral 50"
            viral_playlists = self.spotify.search(q=f"Viral 50 {country}", type='playlist', limit=1)
            
            if viral_playlists['playlists']['items']:
                playlist_id = viral_playlists['playlists']['items'][0]['id']
                tracks = self.spotify.playlist_tracks(playlist_id, limit=max_tracks)
                
                for i, item in enumerate(tracks['items']):
                    if not item['track']:
                        continue
                    
                    track = item['track']
                    artists = ', '.join([artist['name'] for artist in track['artists']])
                    
                    # Obtener audio features para clasificar género/mood
                    try:
                        audio_features = self.spotify.audio_features(track['id'])[0]
                        genre_tags = self._classify_spotify_genre(audio_features, track['name'])
                    except:
                        genre_tags = ['unknown']
                    
                    # Position-based growth rate estimation
                    growth_rate = max(10, (max_tracks - i) / max_tracks * 150)
                    
                    for genre in genre_tags:
                        trend = TrendData(
                            trend_id=f"spotify_viral_{genre}_{track['id']}",
                            keyword=genre,
                            platform="spotify",
                            mentions_count=track['popularity'],
                            growth_rate=growth_rate,
                            phase=self._determine_phase(growth_rate),
                            estimated_peak_date=self._estimate_peak_date(growth_rate),
                            estimated_duration_days=60,  # Spotify trends duran más
                            related_keywords=self._get_related_genres(genre),
                            sample_content=[track['external_urls']['spotify']],
                            confidence_score=track['popularity'] / 100,
                            detected_at=datetime.now(),
                            last_updated=datetime.now()
                        )
                        
                        trends.append(trend)
                        
        except Exception as e:
            logger.error(f"Error scraping Spotify viral tracks: {e}")
        
        return trends

    def _classify_spotify_genre(self, audio_features: dict, track_name: str) -> List[str]:
        """Clasifica género basado en audio features"""
        if not audio_features:
            return ['unknown']
        
        genres = []
        
        # Análisis de audio features
        energy = audio_features['energy']
        danceability = audio_features['danceability']
        valence = audio_features['valence']
        tempo = audio_features['tempo']
        
        # Reglas de clasificación
        if energy > 0.7 and tempo > 120:
            if danceability > 0.7:
                genres.append('reggaeton')
            else:
                genres.append('trap')
        elif energy > 0.6 and tempo > 140:
            genres.append('drill')
        elif danceability > 0.8:
            genres.append('dance')
        elif valence < 0.4 and energy > 0.6:
            genres.append('dark trap')
        elif valence > 0.7:
            genres.append('pop')
        else:
            genres.append('urban')
        
        # También analizar nombre de la canción
        track_lower = track_name.lower()
        if any(word in track_lower for word in ['trap', 'drill']):
            genres.append('trap')
        elif any(word in track_lower for word in ['reggaeton', 'perreo']):
            genres.append('reggaeton')
        
        return list(set(genres))

    def _determine_phase(self, growth_rate: float) -> TrendPhase:
        """Determina fase basada en tasa de crecimiento"""
        if growth_rate > 120:
            return TrendPhase.PEAK
        elif growth_rate > 70:
            return TrendPhase.GROWING
        elif growth_rate > 30:
            return TrendPhase.EMERGING
        else:
            return TrendPhase.DECLINING

    def _estimate_peak_date(self, growth_rate: float) -> Optional[datetime]:
        """Estima fecha de pico"""
        if growth_rate > 100:
            days = 5
        elif growth_rate > 60:
            days = 14
        else:
            days = 30
        
        return datetime.now() + timedelta(days=days)

    def _get_related_genres(self, genre: str) -> List[str]:
        """Obtiene géneros relacionados"""
        relations = {
            'trap': ['drill', 'mumble rap', 'cloud rap'],
            'reggaeton': ['dembow', 'moombahton', 'latin trap'],
            'drill': ['trap', 'grime', 'uk rap'],
            'pop': ['mainstream', 'radio', 'commercial']
        }
        
        return relations.get(genre.lower(), [])


class RedditMusicScraper:
    """Scraper para comunidades musicales de Reddit"""
    
    def __init__(self):
        if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET:
            self.reddit = praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent="CulturalTrendMiner/1.0"
            )
        else:
            self.reddit = None
            logger.warning("Reddit credentials no configuradas")

    async def scrape_music_discussions(self, subreddits: List[str] = None, max_posts: int = 100) -> List[TrendData]:
        """Extrae discusiones trending de subreddits musicales"""
        if not self.reddit:
            return []
        
        if not subreddits:
            subreddits = ['hiphopheads', 'trap', 'makinghiphop', 'trapproduction', 'WeAreTheMusicMakers']
        
        trends = []
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Obtener posts hot (trending)
                hot_posts = subreddit.hot(limit=max_posts // len(subreddits))
                
                for post in hot_posts:
                    if post.stickied:  # Ignorar posts stickied
                        continue
                    
                    keywords = self._extract_reddit_keywords(post.title, post.selftext if hasattr(post, 'selftext') else '')
                    
                    # Calcular growth rate basado en score y tiempo
                    hours_since_created = (datetime.now() - datetime.fromtimestamp(post.created_utc)).total_seconds() / 3600
                    
                    if hours_since_created > 0:
                        score_per_hour = post.score / hours_since_created
                        growth_rate = min(100, score_per_hour * 2)  # Escalado para Reddit
                    else:
                        growth_rate = 0
                    
                    for keyword in keywords:
                        trend = TrendData(
                            trend_id=f"reddit_{subreddit_name}_{keyword}_{post.id}",
                            keyword=keyword,
                            platform="reddit",
                            mentions_count=post.score,
                            growth_rate=growth_rate,
                            phase=self._determine_phase(growth_rate),
                            estimated_peak_date=self._estimate_peak_date(growth_rate),
                            estimated_duration_days=14,  # Reddit discussions son más cortas
                            related_keywords=self._find_related_keywords(keyword),
                            sample_content=[f"https://reddit.com{post.permalink}"],
                            confidence_score=min(0.8, post.upvote_ratio),
                            detected_at=datetime.now(),
                            last_updated=datetime.now()
                        )
                        
                        trends.append(trend)
                        
            except Exception as e:
                logger.error(f"Error scraping subreddit {subreddit_name}: {e}")
        
        return trends

    def _extract_reddit_keywords(self, title: str, text: str) -> List[str]:
        """Extrae keywords de posts de Reddit"""
        content = f"{title} {text}".lower()
        
        # Keywords musicales específicas de Reddit
        reddit_keywords = [
            'beat', 'producer', 'sample', 'mix', 'master', 'collab', 'feedback',
            'trap', 'drill', 'boom bap', 'lo-fi', 'type beat', 'free beat',
            'rapper', 'mc', 'flow', 'bars', 'cypher', 'freestyle', 'battle',
            'studio', 'daw', 'fl studio', 'ableton', 'logic', 'pro tools'
        ]
        
        found_keywords = []
        for keyword in reddit_keywords:
            if keyword in content:
                found_keywords.append(keyword)
        
        # Buscar menciones de artistas populares
        artist_mentions = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', title)  # Nombres propios
        found_keywords.extend([name.lower() for name in artist_mentions[:3]])  # Máximo 3
        
        return list(set(found_keywords))

    def _determine_phase(self, growth_rate: float) -> TrendPhase:
        """Determina fase para tendencias de Reddit"""
        if growth_rate > 50:
            return TrendPhase.PEAK
        elif growth_rate > 25:
            return TrendPhase.GROWING
        elif growth_rate > 10:
            return TrendPhase.EMERGING
        else:
            return TrendPhase.DECLINING

    def _estimate_peak_date(self, growth_rate: float) -> Optional[datetime]:
        """Estima fecha de pico para Reddit"""
        if growth_rate > 40:
            days = 1  # Reddit es muy rápido
        elif growth_rate > 20:
            days = 3
        else:
            days = 7
        
        return datetime.now() + timedelta(days=days)

    def _find_related_keywords(self, keyword: str) -> List[str]:
        """Encuentra keywords relacionadas específicas de Reddit"""
        reddit_relations = {
            'beat': ['producer', 'sample', 'loop', 'drum'],
            'producer': ['beat', 'mix', 'master', 'studio'],
            'trap': ['drill', '808', 'hi-hat', 'snare'],
            'freestyle': ['cypher', 'battle', 'flow', 'bars'],
            'sample': ['flip', 'chop', 'loop', 'vinyl']
        }
        
        return reddit_relations.get(keyword.lower(), [])


class TrendAnalyzer:
    """Analizador principal de tendencias que combina todas las fuentes"""
    
    def __init__(self):
        self.tiktok_scraper = TikTokCreativeCenterScraper()
        self.youtube_scraper = YouTubeTrendingScraper()
        self.spotify_scraper = SpotifyChartsScraper()
        self.reddit_scraper = RedditMusicScraper()
        
    async def analyze_all_trends(self) -> Dict[str, List[TrendData]]:
        """Ejecuta análisis completo de todas las fuentes"""
        logger.info("🔍 Iniciando análisis completo de tendencias...")
        
        # Ejecutar scrapers en paralelo
        tasks = [
            self.tiktok_scraper.scrape_trending_hashtags(),
            self.youtube_scraper.scrape_trending_music(),
            self.spotify_scraper.scrape_viral_tracks(),
            self.reddit_scraper.scrape_music_discussions()
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            trends_by_platform = {
                'tiktok': results[0] if not isinstance(results[0], Exception) else [],
                'youtube': results[1] if not isinstance(results[1], Exception) else [],
                'spotify': results[2] if not isinstance(results[2], Exception) else [],
                'reddit': results[3] if not isinstance(results[3], Exception) else []
            }
            
            # Log errores
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    platform = ['tiktok', 'youtube', 'spotify', 'reddit'][i]
                    logger.error(f"Error en {platform}: {result}")
            
            total_trends = sum(len(trends) for trends in trends_by_platform.values())
            logger.info(f"✅ Análisis completado: {total_trends} tendencias detectadas")
            
            return trends_by_platform
            
        except Exception as e:
            logger.error(f"Error en análisis de tendencias: {e}")
            return {}

    def merge_cross_platform_trends(self, trends_by_platform: Dict[str, List[TrendData]]) -> List[TrendData]:
        """Fusiona tendencias que aparecen en múltiples plataformas"""
        # Agrupar por keyword similar
        keyword_groups = defaultdict(list)
        
        for platform, trends in trends_by_platform.items():
            for trend in trends:
                # Normalizar keyword para agrupación
                normalized_keyword = self._normalize_keyword(trend.keyword)
                keyword_groups[normalized_keyword].append(trend)
        
        merged_trends = []
        
        for normalized_keyword, trend_group in keyword_groups.items():
            if len(trend_group) == 1:
                # Solo en una plataforma
                merged_trends.append(trend_group[0])
            else:
                # Presente en múltiples plataformas - crear tendencia fusionada
                merged_trend = self._merge_trend_group(trend_group, normalized_keyword)
                merged_trends.append(merged_trend)
        
        return merged_trends

    def _normalize_keyword(self, keyword: str) -> str:
        """Normaliza keywords para detectar similares"""
        normalized = keyword.lower().strip()
        
        # Remover variaciones comunes
        normalized = re.sub(r'#', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Manejar sinónimos
        synonyms = {
            'hip hop': 'hiphop',
            'hip-hop': 'hiphop',
            'type beat': 'beat',
            'free beat': 'beat'
        }
        
        for original, replacement in synonyms.items():
            if original in normalized:
                normalized = normalized.replace(original, replacement)
        
        return normalized

    def _merge_trend_group(self, trend_group: List[TrendData], normalized_keyword: str) -> TrendData:
        """Fusiona grupo de tendencias similares"""
        # Usar la tendencia con mayor confidence como base
        base_trend = max(trend_group, key=lambda t: t.confidence_score)
        
        # Agregar estadísticas
        total_mentions = sum(t.mentions_count for t in trend_group)
        avg_growth_rate = statistics.mean([t.growth_rate for t in trend_group])
        platforms = list(set(t.platform for t in trend_group))
        all_related_keywords = []
        all_sample_content = []
        
        for trend in trend_group:
            all_related_keywords.extend(trend.related_keywords)
            all_sample_content.extend(trend.sample_content)
        
        # Determinar fase más avanzada
        phases_order = [TrendPhase.EMERGING, TrendPhase.GROWING, TrendPhase.PEAK, TrendPhase.DECLINING, TrendPhase.DEAD]
        max_phase = max(trend_group, key=lambda t: phases_order.index(t.phase)).phase
        
        # Calcular confidence promedio ponderado por mentions
        total_weighted_confidence = sum(t.confidence_score * t.mentions_count for t in trend_group)
        avg_confidence = total_weighted_confidence / max(total_mentions, 1)
        
        merged_trend = TrendData(
            trend_id=f"merged_{normalized_keyword}_{datetime.now().strftime('%Y%m%d_%H%M')}",
            keyword=normalized_keyword,
            platform=",".join(platforms),
            mentions_count=total_mentions,
            growth_rate=avg_growth_rate,
            phase=max_phase,
            estimated_peak_date=base_trend.estimated_peak_date,
            estimated_duration_days=max(t.estimated_duration_days for t in trend_group),
            related_keywords=list(set(all_related_keywords)),
            sample_content=all_sample_content[:5],  # Máximo 5 ejemplos
            confidence_score=min(0.95, avg_confidence * 1.2),  # Boost por estar en múltiples plataformas
            detected_at=min(t.detected_at for t in trend_group),
            last_updated=datetime.now()
        )
        
        return merged_trend


class TrendStorage:
    """Gestor de persistencia para datos de tendencias"""
    
    def __init__(self):
        self.db_url = settings.DATABASE_URL
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None
        self.engine = create_engine(self.db_url) if self.db_url else None
        
    async def create_tables(self):
        """Crea tablas para almacenar datos de tendencias"""
        if not self.engine:
            return
            
        create_tables_sql = """
        -- Tabla principal de tendencias
        CREATE TABLE IF NOT EXISTS cultural_trends (
            trend_id VARCHAR(255) PRIMARY KEY,
            keyword VARCHAR(255) NOT NULL,
            platform VARCHAR(100) NOT NULL,
            mentions_count INTEGER DEFAULT 0,
            growth_rate FLOAT DEFAULT 0,
            phase VARCHAR(50) NOT NULL,
            estimated_peak_date TIMESTAMP,
            estimated_duration_days INTEGER,
            related_keywords TEXT[], -- Array de keywords relacionadas
            sample_content TEXT[], -- Array de enlaces de ejemplo
            confidence_score FLOAT DEFAULT 0,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de tendencias visuales
        CREATE TABLE IF NOT EXISTS visual_trends (
            trend_id VARCHAR(255) PRIMARY KEY,
            description TEXT NOT NULL,
            color_palette TEXT[], -- Colores hex
            effects_used TEXT[], -- Efectos visuales
            popularity_score FLOAT DEFAULT 0,
            platforms TEXT[], -- Plataformas donde es popular
            sample_videos TEXT[], -- URLs de ejemplo
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de tendencias de audio
        CREATE TABLE IF NOT EXISTS sound_trends (
            trend_id VARCHAR(255) PRIMARY KEY,
            audio_id VARCHAR(255),
            title VARCHAR(500),
            artist VARCHAR(255),
            genre VARCHAR(100),
            usage_count INTEGER DEFAULT 0,
            growth_rate FLOAT DEFAULT 0,
            duration_seconds INTEGER,
            mood_tags TEXT[], -- Tags de mood
            sample_videos TEXT[], -- URLs donde se usa
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla de alertas generadas
        CREATE TABLE IF NOT EXISTS trend_alerts (
            alert_id VARCHAR(255) PRIMARY KEY,
            trend_id VARCHAR(255) REFERENCES cultural_trends(trend_id),
            relevance_score FLOAT NOT NULL,
            recommended_action TEXT,
            urgency_level VARCHAR(50),
            content_suggestions TEXT[],
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged BOOLEAN DEFAULT FALSE
        );
        
        -- Índices para optimizar consultas
        CREATE INDEX IF NOT EXISTS idx_trends_keyword ON cultural_trends(keyword);
        CREATE INDEX IF NOT EXISTS idx_trends_platform ON cultural_trends(platform);
        CREATE INDEX IF NOT EXISTS idx_trends_phase ON cultural_trends(phase);
        CREATE INDEX IF NOT EXISTS idx_trends_growth_rate ON cultural_trends(growth_rate DESC);
        CREATE INDEX IF NOT EXISTS idx_trends_detected_at ON cultural_trends(detected_at DESC);
        CREATE INDEX IF NOT EXISTS idx_alerts_urgency ON trend_alerts(urgency_level, sent_at DESC);
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(create_tables_sql))
                conn.commit()
            logger.info("✅ Tablas de cultural trends creadas correctamente")
        except Exception as e:
            logger.error(f"❌ Error creando tablas de trends: {e}")

    async def save_trends(self, trends: List[TrendData]) -> bool:
        """Guarda tendencias en la base de datos"""
        if not self.engine or not trends:
            return False
        
        try:
            data = []
            for trend in trends:
                data.append({
                    'trend_id': trend.trend_id,
                    'keyword': trend.keyword,
                    'platform': trend.platform,
                    'mentions_count': trend.mentions_count,
                    'growth_rate': trend.growth_rate,
                    'phase': trend.phase.value,
                    'estimated_peak_date': trend.estimated_peak_date,
                    'estimated_duration_days': trend.estimated_duration_days,
                    'related_keywords': trend.related_keywords,
                    'sample_content': trend.sample_content,
                    'confidence_score': trend.confidence_score,
                    'detected_at': trend.detected_at,
                    'last_updated': trend.last_updated
                })
            
            df = pd.DataFrame(data)
            df.to_sql('cultural_trends', self.engine, if_exists='append', index=False)
            
            # Cache en Redis para acceso rápido
            if self.redis_client:
                for trend in trends:
                    key = f"trend:{trend.keyword}:{trend.platform}"
                    self.redis_client.setex(key, 3600, json.dumps(asdict(trend), default=str))  # 1 hora TTL
            
            logger.info(f"✅ Guardadas {len(trends)} tendencias")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando tendencias: {e}")
            return False

    async def get_trending_keywords(self, limit: int = 20, phase_filter: TrendPhase = None) -> List[TrendData]:
        """Obtiene keywords más trending actualmente"""
        if not self.engine:
            return []
        
        try:
            query = """
            SELECT * FROM cultural_trends 
            WHERE detected_at > NOW() - INTERVAL '24 hours'
            """
            
            if phase_filter:
                query += f" AND phase = '{phase_filter.value}'"
            
            query += """
            ORDER BY growth_rate DESC, confidence_score DESC
            LIMIT %s
            """
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), (limit,))
                rows = result.fetchall()
            
            trends = []
            for row in rows:
                trend = TrendData(
                    trend_id=row.trend_id,
                    keyword=row.keyword,
                    platform=row.platform,
                    mentions_count=row.mentions_count,
                    growth_rate=row.growth_rate,
                    phase=TrendPhase(row.phase),
                    estimated_peak_date=row.estimated_peak_date,
                    estimated_duration_days=row.estimated_duration_days,
                    related_keywords=row.related_keywords or [],
                    sample_content=row.sample_content or [],
                    confidence_score=row.confidence_score,
                    detected_at=row.detected_at,
                    last_updated=row.last_updated
                )
                trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo trending keywords: {e}")
            return []


class CulturalTrendMiner:
    """Motor principal de detección de tendencias culturales"""
    
    def __init__(self):
        self.analyzer = TrendAnalyzer()
        self.storage = TrendStorage()
        
    async def initialize(self):
        """Inicializa el motor y crea tablas"""
        await self.storage.create_tables()
        logger.info("🔥 Cultural Trend Miner inicializado")

    async def mine_daily_trends(self) -> Dict[str, Any]:
        """Ejecuta minería diaria de tendencias"""
        logger.info("⛏️ Iniciando minería diaria de tendencias...")
        
        # 1. Analizar todas las fuentes
        trends_by_platform = await self.analyzer.analyze_all_trends()
        
        # 2. Fusionar tendencias cross-platform
        merged_trends = self.analyzer.merge_cross_platform_trends(trends_by_platform)
        
        # 3. Guardar en base de datos
        await self.storage.save_trends(merged_trends)
        
        # 4. Generar estadísticas
        stats = self._generate_mining_stats(trends_by_platform, merged_trends)
        
        logger.info(f"✅ Minería completada: {stats['total_trends']} tendencias, {stats['emerging_count']} emergentes")
        
        return {
            'timestamp': datetime.now(),
            'trends_by_platform': {k: len(v) for k, v in trends_by_platform.items()},
            'merged_trends_count': len(merged_trends),
            'stats': stats,
            'top_emerging': [t for t in merged_trends if t.phase == TrendPhase.EMERGING][:10]
        }

    async def get_artist_relevant_trends(self, artist_profile: Dict[str, Any], max_trends: int = 10) -> List[TrendData]:
        """Obtiene tendencias relevantes para un artista específico"""
        # Obtener tendencias emergentes y en crecimiento
        emerging_trends = await self.storage.get_trending_keywords(limit=50, phase_filter=TrendPhase.EMERGING)
        growing_trends = await self.storage.get_trending_keywords(limit=50, phase_filter=TrendPhase.GROWING)
        
        all_trends = emerging_trends + growing_trends
        
        # Filtrar por relevancia al artista
        relevant_trends = []
        artist_genres = artist_profile.get('genres', ['urban', 'trap'])
        artist_keywords = artist_profile.get('keywords', [])
        
        for trend in all_trends:
            relevance_score = self._calculate_relevance_score(trend, artist_genres, artist_keywords)
            if relevance_score > 0.3:  # Threshold de relevancia
                trend.confidence_score = relevance_score  # Usar como relevance score
                relevant_trends.append(trend)
        
        # Ordenar por relevancia y devolver top N
        relevant_trends.sort(key=lambda t: t.confidence_score, reverse=True)
        return relevant_trends[:max_trends]

    def _calculate_relevance_score(self, trend: TrendData, artist_genres: List[str], artist_keywords: List[str]) -> float:
        """Calcula score de relevancia de una tendencia para un artista"""
        score = 0.0
        
        # Score base por confidence de la tendencia
        score += trend.confidence_score * 0.3
        
        # Score por género matching
        trend_keyword_lower = trend.keyword.lower()
        for genre in artist_genres:
            if genre.lower() in trend_keyword_lower:
                score += 0.4
            if genre.lower() in [k.lower() for k in trend.related_keywords]:
                score += 0.2
        
        # Score por keywords del artista
        for keyword in artist_keywords:
            if keyword.lower() in trend_keyword_lower:
                score += 0.3
            if keyword.lower() in [k.lower() for k in trend.related_keywords]:
                score += 0.1
        
        # Bonus por fase emergente (timing importante)
        if trend.phase == TrendPhase.EMERGING:
            score += 0.2
        elif trend.phase == TrendPhase.GROWING:
            score += 0.1
        
        # Bonus por múltiples plataformas
        if ',' in trend.platform:  # Cross-platform trend
            score += 0.15
        
        return min(1.0, score)

    def _generate_mining_stats(self, trends_by_platform: Dict, merged_trends: List[TrendData]) -> Dict[str, Any]:
        """Genera estadísticas del proceso de minería"""
        total_trends = sum(len(trends) for trends in trends_by_platform.values())
        
        phase_counts = Counter(trend.phase for trend in merged_trends)
        platform_counts = Counter()
        
        for trend in merged_trends:
            platforms = trend.platform.split(',')
            for platform in platforms:
                platform_counts[platform.strip()] += 1
        
        return {
            'total_trends': total_trends,
            'merged_trends': len(merged_trends),
            'emerging_count': phase_counts.get(TrendPhase.EMERGING, 0),
            'growing_count': phase_counts.get(TrendPhase.GROWING, 0),
            'peak_count': phase_counts.get(TrendPhase.PEAK, 0),
            'platform_distribution': dict(platform_counts),
            'avg_confidence': statistics.mean([t.confidence_score for t in merged_trends]) if merged_trends else 0,
            'top_keywords': [t.keyword for t in sorted(merged_trends, key=lambda x: x.growth_rate, reverse=True)[:10]]
        }


# Factory function
def create_trend_miner() -> CulturalTrendMiner:
    """Factory para crear detector de tendencias culturales"""
    return CulturalTrendMiner()