"""
Message Generator Module
Generates contextual, personalized messages for user interactions.
Creates dynamic responses based on user behavior and system state.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import random
import json
from dataclasses import dataclass
from enum import Enum

from ..config.telegram_config import TelegramConfig

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages generated."""
    WELCOME = "welcome"
    HELP = "help"
    STATUS = "status"
    STATS = "stats"
    QUEUE = "queue"
    PRIORITY = "priority"
    ACCOUNTS = "accounts"
    SUCCESS = "success"
    ERROR = "error"
    NOTIFICATION = "notification"
    CONTEXTUAL = "contextual"

@dataclass
class MessageTemplate:
    """Template for message generation."""
    template: str
    variables: List[str]
    conditions: Optional[Dict[str, Any]] = None
    emoji_patterns: Optional[List[str]] = None

class MessageGenerator:
    """
    Generates dynamic, contextual messages for user interactions.
    Personalizes responses based on user history and system state.
    """
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.is_initialized = False
        
        # Message templates
        self.templates: Dict[MessageType, List[MessageTemplate]] = {}
        
        # User context cache
        self.user_contexts: Dict[int, Dict[str, Any]] = {}
        
        # Message statistics for A/B testing
        self.message_stats: Dict[str, Dict[str, int]] = {}
        
        # Dynamic content generators
        self.emoji_patterns = {
            'success': ['🎉', '✅', '🚀', '💪', '⭐'],
            'warning': ['⚠️', '❌', '🔴', '⏰', '📊'],
            'info': ['ℹ️', '📋', '📊', '🔍', '💡'],
            'celebration': ['🎊', '🥳', '🌟', '💫', '🔥'],
            'platforms': {
                'youtube': '📺',
                'instagram': '📷', 
                'tiktok': '🎵',
                'telegram': '📱'
            }
        }
        
    async def initialize(self):
        """Initialize the message generator with templates."""
        try:
            logger.info("Initializing message generator...")
            
            # Load message templates
            await self._load_message_templates()
            
            # Load user contexts
            await self._load_user_contexts()
            
            self.is_initialized = True
            logger.info("Message generator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize message generator: {e}")
            raise
    
    async def _load_message_templates(self):
        """Load message templates for different types."""
        
        # Welcome messages
        self.templates[MessageType.WELCOME] = [
            MessageTemplate(
                template="¡Hola {username}! 👋\n\n¡Bienvenido al sistema de intercambio de engagement más avanzado! 🚀\n\nAquí puedes intercambiar likes, suscripciones y comentarios en YouTube, Instagram y TikTok de forma totalmente automatizada.\n\n🔥 **¿Cómo funciona?**\n• Compartes tu contenido\n• Otros usuarios interactúan con él\n• Tú interactúas con contenido de otros\n• ¡Todos crecemos juntos!\n\n💎 **Características premium:**\n• Algoritmo de prioridad inteligente\n• Detección automática de contenido viral\n• Balance de reciprocidad justo\n• Métricas detalladas en tiempo real\n\n¡Usa los botones de abajo para comenzar! ⬇️",
                variables=['username']
            ),
            MessageTemplate(
                template="¡{username}, bienvenido a la revolución del engagement! 🌟\n\nEste bot utiliza IA avanzada para maximizar el crecimiento de tu contenido en redes sociales.\n\n🎯 **Tu éxito es nuestra misión:**\n• Intercambios inteligentes y seguros\n• Crecimiento orgánico y auténtico\n• Análisis predictivo de tendencias\n• Red de creadores de contenido premium\n\n¡Comienza tu primera campaña ahora! 🚀",
                variables=['username']
            )
        ]
        
        # Help messages
        self.templates[MessageType.HELP] = [
            MessageTemplate(
                template="<b>🔧 Guía Completa del Sistema</b>\n\n<b>📱 Comandos Principales:</b>\n• <code>/start</code> - Menú principal\n• <code>/exchange</code> - Iniciar intercambio\n• <code>/stats</code> - Ver estadísticas\n• <code>/accounts</code> - Gestionar cuentas\n• <code>/queue</code> - Estado de la cola\n• <code>/priority</code> - Info de prioridad\n\n<b>🔄 Proceso de Intercambio:</b>\n1️⃣ Selecciona plataforma (YouTube/Instagram/TikTok)\n2️⃣ Ingresa tu cuenta/canal\n3️⃣ Comparte enlace del contenido\n4️⃣ El sistema calcula prioridad automáticamente\n5️⃣ ¡Recibe engagement real en minutos!\n\n<b>⚡ Sistema de Prioridad:</b>\n• <b>Alta:</b> Contenido viral, usuarios activos\n• <b>Media:</b> Contenido estándar, balance justo\n• <b>Baja:</b> Usuarios nuevos, contenido antiguo\n\n<b>🎯 Consejos Pro:</b>\n• Mantén balance de reciprocidad > 0.8\n• Comparte contenido reciente (< 24h)\n• Usa formatos virales (Shorts, Reels)\n• Participa activamente en la comunidad\n\n<b>💬 Soporte:</b>\nSi necesitas ayuda, usa /status para diagnósticos automáticos.",
                variables=[]
            )
        ]
        
        # Status messages
        self.templates[MessageType.STATUS] = [
            MessageTemplate(
                template="<b>📊 Estado del Sistema</b>\n\n<b>🟢 Sistema Operativo</b>\n• Tareas activas: {active_tasks}\n• Cola de espera: {queue_length}\n• Usuarios conectados: {total_users}\n• Intercambios hoy: {exchanges_today}\n• Tasa de éxito: {success_rate}%\n• Tiempo promedio: {avg_completion_time}\n\n<b>👤 Tu Estado Personal:</b>\n• Intercambios totales: {user_total_exchanges}\n• Intercambios exitosos: {user_successful_exchanges}\n• Tu tasa de éxito: {user_success_rate}%\n• Balance reciprocidad: {user_reciprocity_ratio}\n• Ranking: #{user_rank}\n\n<b>🎯 Recomendación:</b>\n{recommendation}",
                variables=[
                    'active_tasks', 'queue_length', 'total_users', 'exchanges_today',
                    'success_rate', 'avg_completion_time', 'user_total_exchanges',
                    'user_successful_exchanges', 'user_success_rate', 'user_reciprocity_ratio',
                    'user_rank', 'recommendation'
                ]
            )
        ]
        
        # Stats messages
        self.templates[MessageType.STATS] = [
            MessageTemplate(
                template="<b>📈 Tus Estadísticas Detalladas</b>\n\n<b>🎯 Rendimiento General:</b>\n• Total intercambios: {total_exchanges}\n• Exitosos: {successful_exchanges} ({success_rate}%)\n• Engagement dado: {given_engagement}\n• Engagement recibido: {received_engagement}\n• Ratio reciprocidad: {reciprocity_ratio}\n\n<b>📱 Plataforma Favorita:</b>\n{favorite_platform} {platform_emoji}\n\n<b>📅 Actividad:</b>\n• Miembro desde: {join_date}\n• Última actividad: {last_activity}\n• Actividad semanal: {weekly_activity} acciones\n\n<b>🏆 Ranking:</b>\n• Posición: #{rank} de {total_users}\n• Tendencia: {trend_emoji} {trend_description}\n\n<b>📊 Evolución (últimos 10 intercambios):</b>\n{engagement_trend_chart}\n\n<b>💡 Sugerencias personalizadas:</b>\n{personalized_tips}",
                variables=[
                    'total_exchanges', 'successful_exchanges', 'success_rate',
                    'given_engagement', 'received_engagement', 'reciprocity_ratio',
                    'favorite_platform', 'platform_emoji', 'join_date', 'last_activity',
                    'weekly_activity', 'rank', 'total_users', 'trend_emoji',
                    'trend_description', 'engagement_trend_chart', 'personalized_tips'
                ]
            )
        ]
        
        # Queue messages
        self.templates[MessageType.QUEUE] = [
            MessageTemplate(
                template="<b>⏳ Estado de tu Cola</b>\n\n<b>📋 Tus Tareas:</b>\n• En cola: {queued_tasks}\n• En proceso: {active_tasks}\n• Posición en cola: #{queue_position}\n• Tiempo estimado: {estimated_wait_time}\n\n<b>🎯 Próxima tarea:</b>\n{next_task_info}\n\n<b>⚡ Consejos para reducir espera:</b>\n• Mantén alto tu ratio de reciprocidad\n• Comparte contenido de calidad\n• Intercambia en horarios pico\n• Participa activamente en la comunidad\n\n<i>El sistema prioriza usuarios comprometidos y contenido de calidad. ¡Tu engagement importa!</i>",
                variables=[
                    'queued_tasks', 'active_tasks', 'queue_position',
                    'estimated_wait_time', 'next_task_info'
                ]
            )
        ]
        
        # Priority messages
        self.templates[MessageType.PRIORITY] = [
            MessageTemplate(
                template="<b>🎯 Tu Perfil de Prioridad</b>\n\n<b>📊 Puntuación Actual:</b>\n• Engagement histórico: {user_engagement_score}/10\n• Balance reciprocidad: {reciprocity_score}/10\n• Prioridad promedio: {average_priority}/10\n\n<b>📈 Estadísticas:</b>\n• Intercambios completados: {total_completed}\n• Intercambios recibidos: {total_received}\n• Ratio balance: {ratio_balance}\n\n<b>💡 Recomendación personalizada:</b>\n{recommendation}\n\n<b>🚀 Cómo mejorar tu prioridad:</b>\n• ✅ Completa más intercambios\n• 🔄 Mantén balance justo (dar/recibir)\n• 📱 Usa múltiples plataformas\n• ⏰ Intercambia en horarios pico\n• 🎯 Comparte contenido de calidad",
                variables=[
                    'user_engagement_score', 'reciprocity_score', 'average_priority',
                    'total_completed', 'total_received', 'ratio_balance', 'recommendation'
                ]
            )
        ]
        
        # Success messages
        self.templates[MessageType.SUCCESS] = [
            MessageTemplate(
                template="🎉 <b>¡Intercambio Completado Exitosamente!</b>\n\n✅ <b>Detalles del intercambio:</b>\n• Plataforma: {platform} {platform_emoji}\n• Acciones realizadas: {actions_performed}\n• Tiempo de ejecución: {execution_time}\n• Engagement recibido: +{engagement_received}\n\n📈 <b>Tu progreso:</b>\n• Intercambios totales: {total_exchanges}\n• Tasa de éxito: {success_rate}%\n• Nuevo ranking: #{new_rank}\n\n🚀 <b>¡Sigue así!</b> Tu contenido está recibiendo el impulso que merece.\n\n💡 <b>Próximo paso:</b> {next_recommendation}",
                variables=[
                    'platform', 'platform_emoji', 'actions_performed', 'execution_time',
                    'engagement_received', 'total_exchanges', 'success_rate',
                    'new_rank', 'next_recommendation'
                ]
            )
        ]
        
        # Error messages
        self.templates[MessageType.ERROR] = [
            MessageTemplate(
                template="❌ <b>Error en el Intercambio</b>\n\n🔍 <b>Detalles del problema:</b>\n• Tipo: {error_type}\n• Plataforma: {platform}\n• Descripción: {error_description}\n\n🛠️ <b>Soluciones recomendadas:</b>\n{solutions}\n\n⏰ <b>Próximo intento:</b>\n{retry_info}\n\n💬 <b>¿Necesitas ayuda?</b>\nUsa /help para consultar la guía completa o /status para diagnósticos.",
                variables=[
                    'error_type', 'platform', 'error_description', 'solutions', 'retry_info'
                ]
            )
        ]
        
        # Contextual response templates
        self.contextual_templates = {
            'greeting': [
                "¡Hola! 👋 ¿En qué puedo ayudarte?",
                "¡Qué tal! 😊 ¿Listo para hacer crecer tu contenido?",
                "¡Saludos! 🌟 ¿Quieres iniciar un intercambio?"
            ],
            'thanks': [
                "¡De nada! 😊 Estoy aquí para ayudarte a crecer.",
                "¡Un placer ayudarte! 🚀 ¿Algo más?",
                "¡Para eso estoy! 💪 ¿Necesitas algo más?"
            ],
            'url_shared': [
                "👀 Veo que compartiste un enlace. ¿Quieres iniciar un intercambio con /exchange?",
                "🔗 ¡Genial! Ese contenido se ve prometedor. ¿Hacemos un intercambio?",
                "📱 Excelente contenido. Usa /exchange para promocionarlo."
            ],
            'encouragement': [
                "¡Sigue así! 💪 Tu constancia será recompensada.",
                "¡Excelente trabajo! 🌟 Cada intercambio te acerca al éxito.",
                "¡Vas por buen camino! 🚀 La persistencia es clave."
            ]
        }
        
        logger.info("Message templates loaded successfully")
    
    async def _load_user_contexts(self):
        """Load user context data for personalization."""
        try:
            # This would typically load from database
            self.user_contexts = {}
            logger.info("User contexts loaded")
            
        except Exception as e:
            logger.warning(f"Could not load user contexts: {e}")
    
    async def generate_welcome_message(self, username: str) -> str:
        """Generate a personalized welcome message."""
        
        template = random.choice(self.templates[MessageType.WELCOME])
        
        message = template.template.format(
            username=username
        )
        
        await self._track_message_usage(MessageType.WELCOME, template.template)
        
        return message
    
    async def generate_help_message(self) -> str:
        """Generate help message."""
        
        template = random.choice(self.templates[MessageType.HELP])
        return template.template
    
    async def generate_status_message(self, status_info: Dict[str, Any], user_stats: Optional[Dict[str, Any]] = None) -> str:
        """Generate status message with system and user info."""
        
        template = self.templates[MessageType.STATUS][0]
        
        # Generate recommendation based on user stats
        recommendation = await self._generate_status_recommendation(user_stats) if user_stats else "¡Usa /exchange para comenzar tu primer intercambio!"
        
        message = template.template.format(
            active_tasks=status_info.get('active_tasks', 0),
            queue_length=status_info.get('queue_length', 0),
            total_users=status_info.get('total_users', 0),
            exchanges_today=status_info.get('exchanges_today', 0),
            success_rate=round(status_info.get('success_rate', 0), 1),
            avg_completion_time=status_info.get('average_completion_time', 'N/A'),
            user_total_exchanges=user_stats.get('total_exchanges', 0) if user_stats else 0,
            user_successful_exchanges=user_stats.get('successful_exchanges', 0) if user_stats else 0,
            user_success_rate=round(user_stats.get('success_rate', 0), 1) if user_stats else 0,
            user_reciprocity_ratio=round(user_stats.get('reciprocity_ratio', 0), 2) if user_stats else 0,
            user_rank=user_stats.get('rank', 'N/A') if user_stats else 'N/A',
            recommendation=recommendation
        )
        
        return message
    
    async def _generate_status_recommendation(self, user_stats: Dict[str, Any]) -> str:
        """Generate personalized status recommendation."""
        
        success_rate = user_stats.get('success_rate', 0)
        reciprocity_ratio = user_stats.get('reciprocity_ratio', 0)
        total_exchanges = user_stats.get('total_exchanges', 0)
        
        if total_exchanges == 0:
            return "¡Comienza tu primer intercambio con /exchange! 🚀"
        elif success_rate < 50:
            return "Mejora la calidad de tu contenido para mayor éxito 📈"
        elif reciprocity_ratio < 0.5:
            return "Completa más intercambios para mejorar tu balance ⚖️"
        elif success_rate > 80 and reciprocity_ratio > 0.8:
            return "¡Excelente rendimiento! Sigue así campeón 🏆"
        else:
            return "Buen progreso. Mantén la constancia para mejores resultados 💪"
    
    async def generate_stats_message(self, user_stats: Dict[str, Any]) -> str:
        """Generate detailed stats message."""
        
        template = self.templates[MessageType.STATS][0]
        
        # Format join date and last activity
        join_date = "N/A"
        last_activity = "N/A"
        
        if user_stats.get('join_date'):
            join_date = datetime.fromisoformat(user_stats['join_date']).strftime("%d/%m/%Y")
        
        if user_stats.get('last_activity'):
            last_activity_date = datetime.fromisoformat(user_stats['last_activity'])
            time_diff = datetime.now() - last_activity_date
            if time_diff.days == 0:
                last_activity = "Hoy"
            elif time_diff.days == 1:
                last_activity = "Ayer"
            else:
                last_activity = f"Hace {time_diff.days} días"
        
        # Get platform emoji
        favorite_platform = user_stats.get('favorite_platform', 'N/A')
        platform_emoji = self.emoji_patterns['platforms'].get(favorite_platform, '📱')
        
        # Generate trend info
        trend_emoji, trend_description = await self._analyze_user_trend(user_stats)
        
        # Create engagement trend chart
        engagement_trend_chart = await self._create_trend_chart(user_stats.get('engagement_trend', []))
        
        # Generate personalized tips
        personalized_tips = await self._generate_personalized_tips(user_stats)
        
        message = template.template.format(
            total_exchanges=user_stats.get('total_exchanges', 0),
            successful_exchanges=user_stats.get('successful_exchanges', 0),
            success_rate=round(user_stats.get('success_rate', 0), 1),
            given_engagement=user_stats.get('given_engagement', 0),
            received_engagement=user_stats.get('received_engagement', 0),
            reciprocity_ratio=round(user_stats.get('reciprocity_ratio', 0), 2),
            favorite_platform=favorite_platform,
            platform_emoji=platform_emoji,
            join_date=join_date,
            last_activity=last_activity,
            weekly_activity=user_stats.get('weekly_activity', 0),
            rank=user_stats.get('rank', 'N/A'),
            total_users=1000,  # Would get from system stats
            trend_emoji=trend_emoji,
            trend_description=trend_description,
            engagement_trend_chart=engagement_trend_chart,
            personalized_tips=personalized_tips
        )
        
        return message
    
    async def _analyze_user_trend(self, user_stats: Dict[str, Any]) -> Tuple[str, str]:
        """Analyze user engagement trend."""
        
        engagement_trend = user_stats.get('engagement_trend', [])
        
        if len(engagement_trend) < 2:
            return "📊", "Datos insuficientes para análisis"
        
        recent_avg = sum(engagement_trend[-3:]) / min(len(engagement_trend), 3)
        older_avg = sum(engagement_trend[:-3]) / max(len(engagement_trend) - 3, 1)
        
        if recent_avg > older_avg * 1.1:
            return "📈", "Tendencia ascendente"
        elif recent_avg < older_avg * 0.9:
            return "📉", "Necesita mejorar"
        else:
            return "➡️", "Estable"
    
    async def _create_trend_chart(self, trend_data: List[float]) -> str:
        """Create a simple ASCII trend chart."""
        
        if not trend_data:
            return "Sin datos disponibles"
        
        # Normalize data to 0-10 scale for chart
        if max(trend_data) > 0:
            normalized = [int(x / max(trend_data) * 10) for x in trend_data]
        else:
            normalized = [0] * len(trend_data)
        
        chart_symbols = {
            0: '▁', 1: '▁', 2: '▂', 3: '▃', 4: '▄',
            5: '▅', 6: '▆', 7: '▇', 8: '█', 9: '█', 10: '█'
        }
        
        chart = ''.join(chart_symbols.get(level, '▁') for level in normalized)
        return f"`{chart}`"
    
    async def _generate_personalized_tips(self, user_stats: Dict[str, Any]) -> str:
        """Generate personalized improvement tips."""
        
        tips = []
        
        success_rate = user_stats.get('success_rate', 0)
        reciprocity_ratio = user_stats.get('reciprocity_ratio', 0)
        total_exchanges = user_stats.get('total_exchanges', 0)
        favorite_platform = user_stats.get('favorite_platform')
        
        if success_rate < 70:
            tips.append("• Comparte contenido más reciente (< 24 horas)")
        
        if reciprocity_ratio < 0.8:
            tips.append("• Mejora tu balance dando más engagement")
        
        if total_exchanges < 10:
            tips.append("• Realiza más intercambios para mejorar tu ranking")
        
        if favorite_platform == 'youtube':
            tips.append("• Prueba también Instagram y TikTok para diversificar")
        
        if not tips:
            tips.append("• ¡Excelente rendimiento! Mantén la constancia")
        
        return '\n'.join(tips[:3])  # Max 3 tips
    
    async def generate_queue_message(self, queue_info: Dict[str, Any]) -> str:
        """Generate queue status message."""
        
        template = self.templates[MessageType.QUEUE][0]
        
        # Generate next task info
        next_task_info = "Sin tareas pendientes"
        if queue_info.get('queued_tasks', 0) > 0:
            position = queue_info.get('queue_position', 'N/A')
            wait_time = queue_info.get('estimated_wait_time', 'N/A')
            next_task_info = f"Posición #{position}, espera estimada: {wait_time}"
        
        message = template.template.format(
            queued_tasks=queue_info.get('queued_tasks', 0),
            active_tasks=queue_info.get('active_tasks', 0),
            queue_position=queue_info.get('queue_position', 'N/A'),
            estimated_wait_time=queue_info.get('estimated_wait_time', 'N/A'),
            next_task_info=next_task_info
        )
        
        return message
    
    async def generate_priority_message(self, priority_info: Dict[str, Any]) -> str:
        """Generate priority information message."""
        
        template = self.templates[MessageType.PRIORITY][0]
        
        message = template.template.format(
            user_engagement_score=round(priority_info.get('user_engagement_score', 0), 1),
            reciprocity_score=round(priority_info.get('reciprocity_score', 0), 1),
            average_priority=round(priority_info.get('average_priority', 0), 1),
            total_completed=priority_info.get('total_tasks_completed', 0),
            total_received=priority_info.get('total_tasks_received', 0),
            ratio_balance=round(priority_info.get('reciprocity_score', 0) / 10, 2),
            recommendation=priority_info.get('recommendation', 'Continúa con el buen trabajo')
        )
        
        return message
    
    async def generate_accounts_message(self, accounts: List[Dict[str, Any]]) -> str:
        """Generate accounts management message."""
        
        if not accounts:
            return (
                "<b>👤 Gestión de Cuentas</b>\n\n"
                "No tienes cuentas configuradas aún.\n\n"
                "💡 <b>Agrega tus cuentas para:</b>\n"
                "• Automatizar intercambios\n"
                "• Recibir engagement directo\n"
                "• Mejorar tu prioridad en el sistema\n\n"
                "Usa el botón de abajo para comenzar. 👇"
            )
        
        accounts_list = []
        for i, account in enumerate(accounts, 1):
            platform = account.get('platform', 'N/A')
            username = account.get('username', 'N/A')
            status = account.get('status', 'unknown')
            
            platform_emoji = self.emoji_patterns['platforms'].get(platform, '📱')
            status_emoji = '🟢' if status == 'active' else '🔴' if status == 'error' else '🟡'
            
            accounts_list.append(f"{i}. {platform_emoji} {platform.title()}: @{username} {status_emoji}")
        
        accounts_text = '\n'.join(accounts_list)
        
        return (
            f"<b>👤 Tus Cuentas Configuradas</b>\n\n"
            f"{accounts_text}\n\n"
            f"<b>📊 Estado:</b>\n"
            f"• Total: {len(accounts)} cuentas\n"
            f"• Activas: {sum(1 for acc in accounts if acc.get('status') == 'active')}\n"
            f"• Con errores: {sum(1 for acc in accounts if acc.get('status') == 'error')}\n\n"
            f"💡 <b>Consejo:</b> Mantén tus cuentas activas para mejores resultados."
        )
    
    async def generate_success_message(self, task_result: Dict[str, Any]) -> str:
        """Generate success message for completed task."""
        
        template = random.choice(self.templates[MessageType.SUCCESS])
        
        platform = task_result.get('platform', 'N/A')
        platform_emoji = self.emoji_patterns['platforms'].get(platform, '📱')
        
        actions = task_result.get('details', {}).get('actions_performed', [])
        actions_text = ', '.join(actions) if actions else 'Engagement estándar'
        
        # Generate next recommendation
        next_recommendations = [
            "Comparte más contenido para mantener el momentum",
            "Ayuda a otros usuarios para mejorar tu reciprocidad",
            "Prueba diferentes horarios para mejor engagement",
            "Experimenta con contenido de formato corto"
        ]
        next_recommendation = random.choice(next_recommendations)
        
        message = template.template.format(
            platform=platform.title(),
            platform_emoji=platform_emoji,
            actions_performed=actions_text,
            execution_time=str(task_result.get('execution_time', 'N/A')),
            engagement_received=len(actions),
            total_exchanges=task_result.get('user_total_exchanges', 'N/A'),
            success_rate=task_result.get('user_success_rate', 'N/A'),
            new_rank=task_result.get('user_new_rank', 'N/A'),
            next_recommendation=next_recommendation
        )
        
        return message
    
    async def generate_error_message(self, error_info: Dict[str, Any]) -> str:
        """Generate error message with solutions."""
        
        template = self.templates[MessageType.ERROR][0]
        
        error_type = error_info.get('error_type', 'Error desconocido')
        platform = error_info.get('platform', 'N/A')
        error_description = error_info.get('error_message', 'Sin descripción disponible')
        
        # Generate solutions based on error type
        solutions = await self._generate_error_solutions(error_type, platform)
        
        # Generate retry info
        retry_count = error_info.get('retry_count', 0)
        max_retries = error_info.get('max_retries', 3)
        
        if retry_count < max_retries:
            retry_info = f"Reintento automático {retry_count + 1}/{max_retries} en proceso"
        else:
            retry_info = "Máximo de reintentos alcanzado. Intenta con nuevo contenido."
        
        message = template.template.format(
            error_type=error_type,
            platform=platform.title(),
            error_description=error_description,
            solutions=solutions,
            retry_info=retry_info
        )
        
        return message
    
    async def _generate_error_solutions(self, error_type: str, platform: str) -> str:
        """Generate specific solutions for different error types."""
        
        solutions_map = {
            'url_invalid': [
                "• Verifica que el enlace sea válido y público",
                "• Asegúrate de que el contenido no esté privado",
                "• Copia el enlace directamente desde la app"
            ],
            'account_not_found': [
                "• Confirma que el nombre de usuario sea correcto",
                "• Verifica que la cuenta sea pública",
                "• Intenta con @ al inicio del nombre"
            ],
            'rate_limit': [
                "• El sistema respeta los límites de la plataforma",
                "• Tu intercambio se procesará automáticamente",
                "• Evita hacer múltiples solicitudes seguidas"
            ],
            'network_error': [
                "• Problema temporal de conexión",
                "• Se reintentará automáticamente",
                "• Verifica tu conexión a internet"
            ]
        }
        
        solutions = solutions_map.get(error_type, [
            "• Contacta soporte si el problema persiste",
            "• Intenta con contenido diferente",
            "• Verifica tu configuración de cuenta"
        ])
        
        return '\n'.join(solutions)
    
    async def generate_contextual_response(self, user_id: int, message_text: str) -> str:
        """Generate contextual response based on user message."""
        
        message_lower = message_text.lower()
        
        # Detect greeting patterns
        greetings = ['hola', 'hello', 'hi', 'hey', 'buenas', 'saludos']
        if any(greeting in message_lower for greeting in greetings):
            return random.choice(self.contextual_templates['greeting'])
        
        # Detect thanks patterns
        thanks = ['gracias', 'thanks', 'thank you', 'thx']
        if any(thank in message_lower for thank in thanks):
            return random.choice(self.contextual_templates['thanks'])
        
        # Detect URL sharing
        if 'http' in message_text or 'www.' in message_text:
            return random.choice(self.contextual_templates['url_shared'])
        
        # Detect questions
        questions = ['?', 'como', 'que', 'how', 'what', 'when', 'where']
        if any(question in message_lower for question in questions):
            return "🤔 Para obtener ayuda detallada, usa el comando /help. También puedes usar /status para ver el estado del sistema."
        
        # Default encouraging response
        return random.choice(self.contextual_templates['encouragement'])
    
    async def _track_message_usage(self, message_type: MessageType, template: str):
        """Track message template usage for A/B testing."""
        
        template_hash = str(hash(template))
        
        if template_hash not in self.message_stats:
            self.message_stats[template_hash] = {
                'usage_count': 0,
                'positive_feedback': 0,
                'negative_feedback': 0,
                'message_type': message_type.value
            }
        
        self.message_stats[template_hash]['usage_count'] += 1
    
    async def track_message_feedback(self, message_hash: str, positive: bool):
        """Track user feedback on messages for optimization."""
        
        if message_hash in self.message_stats:
            if positive:
                self.message_stats[message_hash]['positive_feedback'] += 1
            else:
                self.message_stats[message_hash]['negative_feedback'] += 1
    
    async def get_message_analytics(self) -> Dict[str, Any]:
        """Get message performance analytics."""
        
        total_messages = sum(stats['usage_count'] for stats in self.message_stats.values())
        total_positive = sum(stats['positive_feedback'] for stats in self.message_stats.values())
        total_negative = sum(stats['negative_feedback'] for stats in self.message_stats.values())
        
        return {
            'total_messages_generated': total_messages,
            'positive_feedback_rate': (total_positive / max(total_positive + total_negative, 1)) * 100,
            'template_performance': {
                template_hash: {
                    'usage_count': stats['usage_count'],
                    'feedback_score': (stats['positive_feedback'] - stats['negative_feedback']),
                    'message_type': stats['message_type']
                }
                for template_hash, stats in self.message_stats.items()
            }
        }
    
    async def start(self):
        """Start the message generator."""
        if not self.is_initialized:
            await self.initialize()
        
        logger.info("Message generator started")
    
    async def stop(self):
        """Stop the message generator."""
        # Save analytics data
        analytics = await self.get_message_analytics()
        logger.info(f"Message analytics: {json.dumps(analytics, indent=2)}")
        
        logger.info("Message generator stopped")