"""
💭 FEEDBACK SENTIMENT ENGINE

Analiza sentimientos y emociones en comentarios de redes sociales para entender
la recepción real del contenido y optimizar estrategias futuras.

CAPACIDADES:
- Scraping de comentarios (YouTube, Instagram, TikTok)
- Análisis de sentimientos con transformers (DistilBERT)  
- Detección emocional avanzada (🔥💔💪💃🎭)
- Topic modeling con BERTopic
- Extracción de keywords y temas dominantes
- Integración con SocialSyncLedger para filtrar bots

ARQUITECTURA:
- CommentScraper: extrae comentarios de plataformas
- SentimentAnalyzer: procesamiento NLP con transformers
- EmotionClassifier: clasifica emociones específicas
- TopicExtractor: identifica temas dominantes con BERTopic
- FeedbackStorage: persistencia en PostgreSQL
- SentimentReporter: dashboards y reportes
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import re

# ML and NLP
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np

# Web scraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup

# Database
import psycopg2
from sqlalchemy import create_engine, text
import redis

# APIs
from googleapiclient.discovery import build
from instagram_private_api import Client as InstagramAPI
import praw

# Internal
from config.app_settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class CommentData:
    """Estructura de datos para un comentario"""
    comment_id: str
    video_id: str
    platform: str  # youtube, instagram, tiktok
    author: str
    text: str
    likes: int
    replies: int
    timestamp: datetime
    parent_id: Optional[str] = None  # Para replies
    is_bot: bool = False  # Detectado por SocialSyncLedger

@dataclass
class SentimentResult:
    """Resultado del análisis de sentimiento"""
    comment_id: str
    sentiment: str  # positive, negative, neutral
    confidence: float  # 0.0 a 1.0
    emotion: str  # 🔥💔💪💃🎭
    emotion_confidence: float
    keywords: List[str]
    topics: List[str]
    
@dataclass
class VideoSentimentSummary:
    """Resumen de sentimientos para un video"""
    video_id: str
    platform: str
    total_comments: int
    organic_comments: int  # Excluyendo bots
    sentiment_distribution: Dict[str, float]  # {positive: 0.6, negative: 0.2, neutral: 0.2}
    emotion_distribution: Dict[str, float]  # {🔥: 0.4, 💪: 0.3, ...}
    dominant_topics: List[Tuple[str, float]]  # [(topic, score), ...]
    top_keywords: List[Tuple[str, int]]  # [(keyword, frequency), ...]
    engagement_sentiment_correlation: float  # Correlación entre likes y sentimiento
    recommendation: str  # Texto con recomendaciones actionables


class CommentScraper:
    """Scraper unificado para comentarios de múltiples plataformas"""
    
    def __init__(self):
        self.youtube_api_key = settings.YOUTUBE_API_KEY
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key) if self.youtube_api_key else None
        self.reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent="TrendMiner/1.0"
        ) if settings.REDDIT_CLIENT_ID else None
        
        # Chrome options for scraping
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox") 
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    async def scrape_youtube_comments(self, video_id: str, max_comments: int = 500) -> List[CommentData]:
        """Extrae comentarios de YouTube usando API oficial"""
        if not self.youtube:
            logger.warning("YouTube API no configurada")
            return []
            
        comments = []
        try:
            # Obtener comentarios principales
            request = self.youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=min(max_comments, 100),
                order="relevance"
            )
            
            while request and len(comments) < max_comments:
                response = request.execute()
                
                for item in response['items']:
                    # Comentario principal
                    comment_snippet = item['snippet']['topLevelComment']['snippet']
                    
                    comment_data = CommentData(
                        comment_id=item['snippet']['topLevelComment']['id'],
                        video_id=video_id,
                        platform="youtube",
                        author=comment_snippet['authorDisplayName'],
                        text=comment_snippet['textDisplay'],
                        likes=comment_snippet.get('likeCount', 0),
                        replies=item['snippet']['totalReplyCount'],
                        timestamp=datetime.fromisoformat(comment_snippet['publishedAt'].replace('Z', '+00:00'))
                    )
                    comments.append(comment_data)
                    
                    # Replies si existen
                    if 'replies' in item:
                        for reply in item['replies']['comments'][:10]:  # Máximo 10 replies por comentario
                            reply_snippet = reply['snippet']
                            
                            reply_data = CommentData(
                                comment_id=reply['id'],
                                video_id=video_id,
                                platform="youtube",
                                author=reply_snippet['authorDisplayName'],
                                text=reply_snippet['textDisplay'],
                                likes=reply_snippet.get('likeCount', 0),
                                replies=0,
                                timestamp=datetime.fromisoformat(reply_snippet['publishedAt'].replace('Z', '+00:00')),
                                parent_id=comment_data.comment_id
                            )
                            comments.append(reply_data)
                
                # Siguiente página
                request = self.youtube.commentThreads().list_next(request, response) if 'nextPageToken' in response else None
                
        except Exception as e:
            logger.error(f"Error scraping YouTube comments para {video_id}: {e}")
        
        return comments[:max_comments]

    async def scrape_tiktok_comments(self, video_url: str, max_comments: int = 300) -> List[CommentData]:
        """Extrae comentarios de TikTok usando web scraping"""
        comments = []
        driver = None
        
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(video_url)
            
            # Esperar que carguen los comentarios
            await asyncio.sleep(5)
            
            # Scroll para cargar más comentarios
            for _ in range(10):  # 10 scrolls máximo
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
            
            # Extraer video ID de la URL
            video_id = re.search(r'/video/(\d+)', video_url)
            video_id = video_id.group(1) if video_id else video_url.split('/')[-1]
            
            # Buscar elementos de comentarios (selectores pueden cambiar)
            comment_elements = driver.find_elements(By.CSS_SELECTOR, "[data-e2e='comment-item']")
            
            for element in comment_elements[:max_comments]:
                try:
                    # Extraer datos del comentario
                    author_elem = element.find_element(By.CSS_SELECTOR, "[data-e2e='comment-username']")
                    text_elem = element.find_element(By.CSS_SELECTOR, "[data-e2e='comment-text']")
                    likes_elem = element.find_element(By.CSS_SELECTOR, "[data-e2e='comment-like-count']")
                    
                    comment_data = CommentData(
                        comment_id=f"tiktok_{len(comments)}_{video_id}",
                        video_id=video_id,
                        platform="tiktok",
                        author=author_elem.text.strip(),
                        text=text_elem.text.strip(),
                        likes=self._parse_number(likes_elem.text),
                        replies=0,  # TikTok replies son difíciles de extraer
                        timestamp=datetime.now()  # TikTok no expone timestamp fácilmente
                    )
                    comments.append(comment_data)
                    
                except Exception as e:
                    logger.debug(f"Error extrayendo comentario individual: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping TikTok comments para {video_url}: {e}")
        finally:
            if driver:
                driver.quit()
        
        return comments

    def _parse_number(self, text: str) -> int:
        """Parsea números con sufijos (1K, 2.3M, etc.)"""
        if not text or text == '':
            return 0
        text = text.lower().replace(',', '')
        if 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        elif 'm' in text:
            return int(float(text.replace('m', '')) * 1000000)
        else:
            try:
                return int(text)
            except:
                return 0


class SentimentAnalyzer:
    """Analizador de sentimientos usando transformers"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Inicializando SentimentAnalyzer en {self.device}")
        
        # Modelo principal para sentimiento
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=0 if self.device == "cuda" else -1
        )
        
        # Clasificador de emociones personalizado
        emotion_model = "j-hartmann/emotion-english-distilroberta-base"
        self.emotion_pipeline = pipeline(
            "text-classification",
            model=emotion_model,
            device=0 if self.device == "cuda" else -1
        )
        
        # Mapeo de emociones a emojis
        self.emotion_emojis = {
            'joy': '🔥',
            'love': '💖', 
            'excitement': '🚀',
            'admiration': '👏',
            'optimism': '💪',
            'approval': '✅',
            'amusement': '😂',
            'desire': '💃',
            'sadness': '💔',
            'disappointment': '😞',
            'anger': '😡',
            'disgust': '🤮',
            'fear': '😨',
            'surprise': '😮',
            'neutral': '😐'
        }

    async def analyze_sentiment(self, comment: CommentData) -> SentimentResult:
        """Analiza sentimiento y emoción de un comentario"""
        text = self._clean_text(comment.text)
        
        # Análisis de sentimiento
        sentiment_result = self.sentiment_pipeline(text)[0]
        sentiment = "positive" if sentiment_result['label'] == 'POSITIVE' else "negative"
        sentiment_confidence = sentiment_result['score']
        
        # Análisis de emoción
        emotion_result = self.emotion_pipeline(text)[0]
        emotion_label = emotion_result['label'].lower()
        emotion_emoji = self.emotion_emojis.get(emotion_label, '😐')
        emotion_confidence = emotion_result['score']
        
        # Extracción de keywords
        keywords = self._extract_keywords(text)
        
        return SentimentResult(
            comment_id=comment.comment_id,
            sentiment=sentiment,
            confidence=sentiment_confidence,
            emotion=emotion_emoji,
            emotion_confidence=emotion_confidence,
            keywords=keywords,
            topics=[]  # Se llenan después con topic modeling
        )

    def _clean_text(self, text: str) -> str:
        """Limpia texto para análisis"""
        # Remover URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        # Remover mentions y hashtags pero mantener el texto
        text = re.sub(r'@\w+|#\w+', '', text)
        # Remover caracteres especiales excesivos
        text = re.sub(r'[^\w\s!?.,]', '', text)
        # Normalizar espacios
        text = ' '.join(text.split())
        return text.strip()

    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae keywords relevantes del texto"""
        # Palabras clave relacionadas con música
        music_keywords = [
            'beat', 'ritmo', 'flow', 'letra', 'voz', 'producción', 'instrumental',
            'melodía', 'hook', 'verso', 'estribillo', 'trap', 'reggaeton', 'drill',
            'fuego', 'fire', 'sick', 'duro', 'brutal', 'bestial', 'increíble'
        ]
        
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in music_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        # Añadir palabras con alta carga emocional
        emotional_words = ['amor', 'odio', 'increíble', 'terrible', 'perfecto', 'horrible', 'amazing', 'awful']
        for word in emotional_words:
            if word in text_lower:
                found_keywords.append(word)
        
        return list(set(found_keywords))  # Remover duplicados


class TopicExtractor:
    """Extractor de temas dominantes usando BERTopic"""
    
    def __init__(self):
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.topic_model = None
        self.is_fitted = False

    async def extract_topics(self, comments: List[CommentData], min_topic_size: int = 5) -> Dict[str, Any]:
        """Extrae temas dominantes de una colección de comentarios"""
        if len(comments) < min_topic_size:
            return {"topics": [], "topic_words": {}, "document_topics": []}
        
        # Preparar documentos
        documents = [self._clean_text(comment.text) for comment in comments]
        documents = [doc for doc in documents if len(doc.strip()) > 10]  # Filtrar comentarios muy cortos
        
        if len(documents) < min_topic_size:
            return {"topics": [], "topic_words": {}, "document_topics": []}
        
        try:
            # Crear modelo BERTopic
            self.topic_model = BERTopic(
                embedding_model=self.sentence_model,
                min_topic_size=min_topic_size,
                nr_topics=min(10, len(documents) // 3),  # Máximo 10 temas
                language="multilingual",
                calculate_probabilities=True,
                verbose=False
            )
            
            # Fit y predecir temas
            topics, probabilities = self.topic_model.fit_transform(documents)
            self.is_fitted = True
            
            # Obtener información de temas
            topic_info = self.topic_model.get_topic_info()
            topic_words = {}
            
            for topic_id in topic_info['Topic'].unique():
                if topic_id != -1:  # Excluir outliers
                    words = self.topic_model.get_topic(topic_id)
                    topic_words[f"Topic_{topic_id}"] = [word for word, score in words[:5]]
            
            # Asignar temas a documentos
            document_topics = []
            for i, (topic, prob) in enumerate(zip(topics, probabilities)):
                if i < len(comments):
                    topic_name = f"Topic_{topic}" if topic != -1 else "Outlier"
                    document_topics.append({
                        "comment_id": comments[i].comment_id,
                        "topic": topic_name,
                        "probability": max(prob) if isinstance(prob, (list, np.ndarray)) else prob
                    })
            
            return {
                "topics": topic_info.to_dict('records'),
                "topic_words": topic_words,
                "document_topics": document_topics
            }
            
        except Exception as e:
            logger.error(f"Error en topic extraction: {e}")
            return {"topics": [], "topic_words": {}, "document_topics": []}

    def _clean_text(self, text: str) -> str:
        """Limpia texto para topic modeling"""
        # Remover URLs, mentions, hashtags
        text = re.sub(r'http\S+|www.\S+|@\w+|#\w+', '', text)
        # Remover caracteres especiales
        text = re.sub(r'[^\w\s]', ' ', text)
        # Normalizar espacios
        text = ' '.join(text.split())
        return text.strip().lower()


class FeedbackStorage:
    """Gestor de persistencia para análisis de feedback"""
    
    def __init__(self):
        self.db_url = settings.DATABASE_URL
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None
        self.engine = create_engine(self.db_url) if self.db_url else None
        
    async def create_tables(self):
        """Crea tablas necesarias para almacenar análisis de feedback"""
        if not self.engine:
            return
            
        create_tables_sql = """
        -- Tabla para comentarios
        CREATE TABLE IF NOT EXISTS comments_raw (
            comment_id VARCHAR(255) PRIMARY KEY,
            video_id VARCHAR(255) NOT NULL,
            platform VARCHAR(50) NOT NULL,
            author VARCHAR(255),
            text TEXT,
            likes INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            timestamp TIMESTAMP,
            parent_id VARCHAR(255),
            is_bot BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla para análisis de sentimientos
        CREATE TABLE IF NOT EXISTS sentiment_analysis (
            id SERIAL PRIMARY KEY,
            comment_id VARCHAR(255) REFERENCES comments_raw(comment_id),
            sentiment VARCHAR(50),
            confidence FLOAT,
            emotion VARCHAR(10),
            emotion_confidence FLOAT,
            keywords TEXT[], -- Array de keywords
            topics TEXT[], -- Array de topics
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Tabla para resúmenes por video
        CREATE TABLE IF NOT EXISTS video_sentiment_summary (
            id SERIAL PRIMARY KEY,
            video_id VARCHAR(255) NOT NULL,
            platform VARCHAR(50) NOT NULL,
            total_comments INTEGER,
            organic_comments INTEGER,
            sentiment_distribution JSONB,
            emotion_distribution JSONB,
            dominant_topics JSONB,
            top_keywords JSONB,
            engagement_sentiment_correlation FLOAT,
            recommendation TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(video_id, platform, analyzed_at::date)
        );
        
        -- Índices para optimizar consultas
        CREATE INDEX IF NOT EXISTS idx_comments_video_platform ON comments_raw(video_id, platform);
        CREATE INDEX IF NOT EXISTS idx_comments_timestamp ON comments_raw(timestamp);
        CREATE INDEX IF NOT EXISTS idx_sentiment_comment ON sentiment_analysis(comment_id);
        CREATE INDEX IF NOT EXISTS idx_video_summary_date ON video_sentiment_summary(analyzed_at::date);
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(create_tables_sql))
                conn.commit()
            logger.info("✅ Tablas de feedback sentiment creadas correctamente")
        except Exception as e:
            logger.error(f"❌ Error creando tablas: {e}")

    async def save_comments(self, comments: List[CommentData]) -> bool:
        """Guarda comentarios en la base de datos"""
        if not self.engine or not comments:
            return False
        
        try:
            df = pd.DataFrame([asdict(comment) for comment in comments])
            df.to_sql('comments_raw', self.engine, if_exists='append', index=False)
            logger.info(f"✅ Guardados {len(comments)} comentarios")
            return True
        except Exception as e:
            logger.error(f"❌ Error guardando comentarios: {e}")
            return False

    async def save_sentiment_analysis(self, results: List[SentimentResult]) -> bool:
        """Guarda resultados de análisis de sentimiento"""
        if not self.engine or not results:
            return False
        
        try:
            data = []
            for result in results:
                data.append({
                    'comment_id': result.comment_id,
                    'sentiment': result.sentiment,
                    'confidence': result.confidence,
                    'emotion': result.emotion,
                    'emotion_confidence': result.emotion_confidence,
                    'keywords': result.keywords,
                    'topics': result.topics
                })
            
            df = pd.DataFrame(data)
            df.to_sql('sentiment_analysis', self.engine, if_exists='append', index=False)
            logger.info(f"✅ Guardados {len(results)} análisis de sentimiento")
            return True
        except Exception as e:
            logger.error(f"❌ Error guardando análisis: {e}")
            return False

    async def save_video_summary(self, summary: VideoSentimentSummary) -> bool:
        """Guarda resumen de sentimientos por video"""
        if not self.engine:
            return False
        
        try:
            data = {
                'video_id': summary.video_id,
                'platform': summary.platform,
                'total_comments': summary.total_comments,
                'organic_comments': summary.organic_comments,
                'sentiment_distribution': json.dumps(summary.sentiment_distribution),
                'emotion_distribution': json.dumps(summary.emotion_distribution),
                'dominant_topics': json.dumps(summary.dominant_topics),
                'top_keywords': json.dumps(summary.top_keywords),
                'engagement_sentiment_correlation': summary.engagement_sentiment_correlation,
                'recommendation': summary.recommendation
            }
            
            df = pd.DataFrame([data])
            df.to_sql('video_sentiment_summary', self.engine, if_exists='append', index=False)
            logger.info(f"✅ Guardado resumen para video {summary.video_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error guardando resumen: {e}")
            return False


class FeedbackSentimentEngine:
    """Motor principal de análisis de sentimientos de feedback"""
    
    def __init__(self):
        self.scraper = CommentScraper()
        self.analyzer = SentimentAnalyzer()
        self.topic_extractor = TopicExtractor()
        self.storage = FeedbackStorage()
        
    async def initialize(self):
        """Inicializa el motor y crea tablas"""
        await self.storage.create_tables()
        logger.info("🧠 Feedback Sentiment Engine inicializado")

    async def analyze_video_feedback(self, video_id: str, platform: str = "youtube", max_comments: int = 500) -> VideoSentimentSummary:
        """Analiza feedback completo de un video"""
        logger.info(f"🔍 Analizando feedback de {platform} video: {video_id}")
        
        # 1. Scraping de comentarios
        if platform == "youtube":
            comments = await self.scraper.scrape_youtube_comments(video_id, max_comments)
        elif platform == "tiktok":
            comments = await self.scraper.scrape_tiktok_comments(video_id, max_comments)
        else:
            logger.error(f"Plataforma {platform} no soportada")
            return None
        
        if not comments:
            logger.warning(f"No se encontraron comentarios para {video_id}")
            return None
        
        # 2. Guardar comentarios
        await self.storage.save_comments(comments)
        
        # 3. Análisis de sentimientos
        sentiment_results = []
        for comment in comments:
            if not comment.is_bot:  # Solo analizar comentarios orgánicos
                result = await self.analyzer.analyze_sentiment(comment)
                sentiment_results.append(result)
        
        # 4. Topic modeling
        topic_data = await self.topic_extractor.extract_topics(comments)
        
        # Asignar topics a resultados
        topic_map = {doc["comment_id"]: doc["topic"] for doc in topic_data["document_topics"]}
        for result in sentiment_results:
            result.topics = [topic_map.get(result.comment_id, "Unknown")]
        
        # 5. Guardar análisis
        await self.storage.save_sentiment_analysis(sentiment_results)
        
        # 6. Generar resumen
        summary = self._generate_video_summary(video_id, platform, comments, sentiment_results, topic_data)
        
        # 7. Guardar resumen
        await self.storage.save_video_summary(summary)
        
        logger.info(f"✅ Análisis completado para {video_id}: {summary.total_comments} comentarios, {summary.organic_comments} orgánicos")
        return summary

    def _generate_video_summary(self, video_id: str, platform: str, comments: List[CommentData], 
                               sentiment_results: List[SentimentResult], topic_data: Dict) -> VideoSentimentSummary:
        """Genera resumen estadístico del feedback"""
        
        organic_comments = [c for c in comments if not c.is_bot]
        
        # Distribución de sentimientos
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        emotion_counts = {}
        all_keywords = []
        
        for result in sentiment_results:
            sentiment_counts[result.sentiment] += 1
            if result.emotion in emotion_counts:
                emotion_counts[result.emotion] += 1
            else:
                emotion_counts[result.emotion] = 1
            all_keywords.extend(result.keywords)
        
        total_organic = len(sentiment_results) or 1
        sentiment_dist = {k: v/total_organic for k, v in sentiment_counts.items()}
        emotion_dist = {k: v/total_organic for k, v in emotion_counts.items()}
        
        # Top keywords
        from collections import Counter
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(10)
        
        # Temas dominantes
        dominant_topics = []
        if topic_data["topics"]:
            for topic in topic_data["topics"][:5]:  # Top 5 temas
                topic_id = topic.get("Topic", -1)
                if topic_id != -1:
                    topic_words = topic_data["topic_words"].get(f"Topic_{topic_id}", [])
                    dominant_topics.append((", ".join(topic_words), topic.get("Count", 0)))
        
        # Correlación engagement-sentimiento
        correlation = self._calculate_engagement_sentiment_correlation(comments, sentiment_results)
        
        # Generar recomendación
        recommendation = self._generate_recommendation(sentiment_dist, emotion_dist, dominant_topics, top_keywords)
        
        return VideoSentimentSummary(
            video_id=video_id,
            platform=platform,
            total_comments=len(comments),
            organic_comments=len(organic_comments),
            sentiment_distribution=sentiment_dist,
            emotion_distribution=emotion_dist,
            dominant_topics=dominant_topics,
            top_keywords=top_keywords,
            engagement_sentiment_correlation=correlation,
            recommendation=recommendation
        )

    def _calculate_engagement_sentiment_correlation(self, comments: List[CommentData], 
                                                  sentiment_results: List[SentimentResult]) -> float:
        """Calcula correlación entre engagement (likes) y sentimiento"""
        if len(comments) < 10:
            return 0.0
        
        # Crear mapeo de comentario a sentimiento
        sentiment_map = {r.comment_id: 1 if r.sentiment == "positive" else -1 if r.sentiment == "negative" else 0 
                        for r in sentiment_results}
        
        likes = []
        sentiments = []
        
        for comment in comments:
            if comment.comment_id in sentiment_map and not comment.is_bot:
                likes.append(comment.likes)
                sentiments.append(sentiment_map[comment.comment_id])
        
        if len(likes) < 10:
            return 0.0
        
        try:
            correlation = np.corrcoef(likes, sentiments)[0, 1]
            return correlation if not np.isnan(correlation) else 0.0
        except:
            return 0.0

    def _generate_recommendation(self, sentiment_dist: Dict, emotion_dist: Dict, 
                               dominant_topics: List, top_keywords: List) -> str:
        """Genera recomendación actionable basada en el análisis"""
        recommendations = []
        
        # Análisis de sentimiento general
        positive_ratio = sentiment_dist.get("positive", 0)
        negative_ratio = sentiment_dist.get("negative", 0)
        
        if positive_ratio > 0.7:
            recommendations.append("🔥 EXCELENTE recepción! Replica esta fórmula en futuros contenidos.")
        elif positive_ratio > 0.5:
            recommendations.append("✅ Buena recepción general. Identifica qué aspectos gustaron más.")
        elif negative_ratio > 0.4:
            recommendations.append("⚠️ Alta negatividad detectada. Revisa comentarios para mejoras.")
        
        # Análisis emocional
        top_emotion = max(emotion_dist.items(), key=lambda x: x[1]) if emotion_dist else ("😐", 0)
        if top_emotion[0] == "🔥" and top_emotion[1] > 0.3:
            recommendations.append("🔥 Gran energía en comentarios! Sigue con este nivel de intensidad.")
        elif top_emotion[0] == "💔" and top_emotion[1] > 0.2:
            recommendations.append("💔 Detectada tristeza. Considera contenido más motivacional.")
        
        # Análisis de temas
        if dominant_topics:
            main_topic = dominant_topics[0][0] if dominant_topics[0][1] > 5 else None
            if main_topic:
                recommendations.append(f"💭 Tema dominante: '{main_topic}'. Profundiza en este aspecto.")
        
        # Análisis de keywords
        if top_keywords:
            top_keyword = top_keywords[0][0]
            if top_keyword in ['beat', 'ritmo', 'instrumental']:
                recommendations.append("🎵 La producción musical es muy comentada. Destaca más este aspecto.")
            elif top_keyword in ['letra', 'flow', 'verso']:
                recommendations.append("📝 Las letras generan conversación. Promociona más el contenido lírico.")
        
        return " | ".join(recommendations) if recommendations else "📊 Análisis completado. Revisa métricas detalladas para insights específicos."


# Factory function para crear instancia
def create_sentiment_engine() -> FeedbackSentimentEngine:
    """Factory para crear motor de análisis de sentimientos"""
    return FeedbackSentimentEngine()