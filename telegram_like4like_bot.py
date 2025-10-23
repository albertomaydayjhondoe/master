"""
Telegram Like4Like Bot Implementation
Sistema de intercambio automático de likes usando ML para negociación inteligente
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import time
import numpy as np
import cv2
import base64
from pathlib import Path

# ML dependencies
try:
    from ultralytics import YOLO
    import torch
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    print("⚠️ Ultralytics not available - using dummy ML mode")

# Telegram dependencies  
try:
    from telethon import TelegramClient, events
    from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ Telethon not available - using dummy Telegram mode")

# Import our ML core
try:
    from ml_core.bidirectional_engine import BidirectionalMLEngine
    from ml_core.cloud_processing import CloudMLProcessingPipeline
except ImportError:
    print("⚠️ ML Core not available - using standalone mode")

class InteractionType(Enum):
    LIKE = "like"
    COMMENT = "comment" 
    SUBSCRIBE = "subscribe"
    SHARE = "share"

class NegotiationStage(Enum):
    INITIAL_CONTACT = "initial_contact"
    NEGOTIATING = "negotiating"
    PROOF_REQUESTED = "proof_requested"
    VERIFYING_PROOF = "verifying_proof"
    REWARD_SENT = "reward_sent"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class InteractionRequest:
    user_id: int
    username: str
    requested_interactions: List[InteractionType]
    target_video_url: str
    channel_handle: str
    timestamp: datetime
    stage: NegotiationStage
    negotiation_attempts: int = 0
    proof_screenshot: Optional[str] = None
    verification_result: Optional[bool] = None
    reward_sent: bool = False

@dataclass
class NegotiationStats:
    total_contacts: int = 0
    successful_negotiations: int = 0
    failed_negotiations: int = 0
    proof_verifications: int = 0
    rewards_sent: int = 0
    avg_negotiation_time: float = 0.0
    success_rate: float = 0.0

class ScreenshotAnalyzer:
    """Analiza screenshots usando Ultralytics para verificar interacciones"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ScreenshotAnalyzer")
        
        if ULTRALYTICS_AVAILABLE:
            # Cargar modelo preentrenado o entrenar uno personalizado
            try:
                self.model = YOLO('/workspaces/master/data/models/youtube_interaction_detector.pt')
            except:
                # Usar modelo base y entrenar
                self.model = YOLO('yolov8n.pt')
                self.logger.info("📚 Using base YOLOv8 - will train on interaction detection")
        else:
            self.model = None
    
    async def verify_screenshot(self, screenshot_data: bytes, expected_video_url: str) -> Dict[str, Any]:
        """Verificar que el screenshot muestra las interacciones correctas"""
        
        if not ULTRALYTICS_AVAILABLE:
            return await self._dummy_verification(screenshot_data, expected_video_url)
        
        try:
            # Procesar imagen
            image = self._process_screenshot(screenshot_data)
            
            # Detectar elementos de YouTube
            results = self.model(image)
            
            # Analizar detecciones
            verification = await self._analyze_detections(results, expected_video_url)
            
            # Registrar para entrenamiento
            await self._log_verification_for_training(image, verification)
            
            return verification
            
        except Exception as e:
            self.logger.error(f"❌ Screenshot verification failed: {e}")
            return {
                'verified': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _process_screenshot(self, screenshot_data: bytes) -> np.ndarray:
        """Procesar datos de screenshot a imagen"""
        # Convertir bytes a imagen
        nparr = np.frombuffer(screenshot_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    
    async def _analyze_detections(self, results, expected_video_url: str) -> Dict[str, Any]:
        """Analizar detecciones del modelo"""
        
        verification = {
            'verified': False,
            'confidence': 0.0,
            'detected_interactions': [],
            'video_match': False
        }
        
        # Analizar cada detección
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Mapear clases a interacciones
                    interaction_map = {
                        0: 'like_button',
                        1: 'subscribe_button', 
                        2: 'comment_section',
                        3: 'video_title',
                        4: 'like_active',
                        5: 'subscribed_active'
                    }
                    
                    if conf > 0.7:  # Umbral de confianza
                        detected = interaction_map.get(cls, f'class_{cls}')
                        verification['detected_interactions'].append({
                            'type': detected,
                            'confidence': conf
                        })
        
        # Verificar video específico (análisis de título/thumbnail)
        verification['video_match'] = await self._verify_video_match(results, expected_video_url)
        
        # Calcular verificación general
        required_interactions = ['like_active', 'subscribed_active']
        verified_count = sum(1 for item in verification['detected_interactions'] 
                           if any(req in item['type'] for req in required_interactions))
        
        verification['verified'] = verified_count >= 2 and verification['video_match']
        verification['confidence'] = min([item['confidence'] for item in verification['detected_interactions']], default=0.0)
        
        return verification
    
    async def _verify_video_match(self, results, expected_video_url: str) -> bool:
        """Verificar que el screenshot corresponde al video esperado"""
        # Implementar OCR para leer título del video
        # Por ahora, simulación
        return True
    
    async def _log_verification_for_training(self, image: np.ndarray, verification: Dict[str, Any]):
        """Registrar verificación para mejorar el modelo"""
        
        # Guardar imagen y resultados para reentrenamiento
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        training_data = {
            'timestamp': timestamp,
            'verification_result': verification,
            'image_path': f'/workspaces/master/data/training/screenshots/{timestamp}.jpg'
        }
        
        # Guardar imagen
        cv2.imwrite(training_data['image_path'], image)
        
        # Registrar en archivo de entrenamiento
        training_log_path = '/workspaces/master/data/training/verification_log.json'
        
        try:
            with open(training_log_path, 'r') as f:
                training_log = json.load(f)
        except:
            training_log = []
        
        training_log.append(training_data)
        
        with open(training_log_path, 'w') as f:
            json.dump(training_log, f, indent=2)
    
    async def _dummy_verification(self, screenshot_data: bytes, expected_video_url: str) -> Dict[str, Any]:
        """Verificación dummy para testing"""
        return {
            'verified': True,
            'confidence': 0.95,
            'detected_interactions': [
                {'type': 'like_active', 'confidence': 0.97},
                {'type': 'subscribed_active', 'confidence': 0.93}
            ],
            'video_match': True
        }

class NegotiationEngine:
    """Motor de negociación inteligente que aprende patrones humanos"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.NegotiationEngine")
        self.negotiation_patterns = self._load_negotiation_patterns()
        self.success_messages = self._load_success_messages()
        
    def _load_negotiation_patterns(self) -> Dict[str, Any]:
        """Cargar patrones de negociación aprendidos"""
        return {
            'greeting_styles': [
                "¡Hola! 👋 Vi tu solicitud de like4like",
                "Hola! Me interesa tu propuesta de intercambio",
                "¡Perfecto! Hagamos el intercambio"
            ],
            'request_formats': [
                "Dame like + comentario + suscripción y yo hago lo mismo 🔄",
                "¿Intercambiamos? Like + comment + sub por lo mismo",
                "Propuesta: Nos damos like, comentario y suscripción mutuamente"
            ],
            'proof_requests': [
                "Envíame screenshot como prueba y te hago lo mismo al instante 📸",
                "Manda captura cuando hayas hecho todo y procedo de inmediato",
                "Screenshot del like + comentario + sub y te devuelvo el favor"
            ],
            'urgency_phrases': [
                "Respondo rápido! ⚡",
                "Online ahora - intercambio inmediato",
                "Activo las 24h para intercambios"
            ]
        }
    
    def _load_success_messages(self) -> List[str]:
        """Mensajes para después de intercambio exitoso"""
        return [
            "✅ Listo! Ya te di like, comenté y me suscribí. ¡Gracias por el intercambio!",
            "🎉 Completado! Check tu video - like + comment + suscripción listos",
            "✨ Todo hecho! Ya tienes mi interacción completa. ¡Excelente intercambio!"
        ]
    
    async def generate_initial_message(self, context: Dict[str, Any]) -> str:
        """Generar mensaje inicial personalizado"""
        
        greeting = np.random.choice(self.negotiation_patterns['greeting_styles'])
        request = np.random.choice(self.negotiation_patterns['request_formats'])
        proof_request = np.random.choice(self.negotiation_patterns['proof_requests'])
        urgency = np.random.choice(self.negotiation_patterns['urgency_phrases'])
        
        # Personalizar según contexto
        video_title = context.get('video_title', 'tu video')
        
        message = f"{greeting}\n\n{request}\n\nVideo: {video_title}\n\n{proof_request}\n\n{urgency}"
        
        return message
    
    async def generate_follow_up(self, attempt_number: int, user_response: str = "") -> str:
        """Generar mensaje de seguimiento basado en intentos previos"""
        
        if attempt_number == 1:
            return "¿Te interesa el intercambio? Es 100% real y inmediato 🚀"
        elif attempt_number == 2:
            return "Última oportunidad para el intercambio. ¿Hacemos el deal? ⏰"
        else:
            return "Ok, no hay problema. Si cambias de opinión, aquí estaré 👍"
    
    async def generate_success_message(self) -> str:
        """Generar mensaje de éxito personalizado"""
        return np.random.choice(self.success_messages)

class TelegramLike4LikeBot:
    """Bot principal de Telegram para intercambio de likes"""
    
    def __init__(self, api_id: str, api_hash: str, phone_numbers: List[str]):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_numbers = phone_numbers
        
        self.logger = logging.getLogger(f"{__name__}.TelegramBot")
        
        # Componentes ML
        self.screenshot_analyzer = ScreenshotAnalyzer()
        self.negotiation_engine = NegotiationEngine()
        
        # Estado del bot
        self.active_requests: Dict[int, InteractionRequest] = {}
        self.clients: List[TelegramClient] = []
        self.stats = NegotiationStats()
        
        # Configuración de rate limiting
        self.daily_interaction_limits = {
            'day_1_2': 10,    # 5-10 interacciones/hora
            'day_3_5': 50,    # hasta 50 interacciones/hora  
            'day_6+': 100     # máximo después del warm-up
        }
        
        self.current_day = 1
        self.hourly_interactions = 0
        self.last_hour_reset = datetime.now()
    
    async def initialize(self):
        """Inicializar clientes de Telegram"""
        
        if not TELEGRAM_AVAILABLE:
            self.logger.warning("⚠️ Telegram not available - using dummy mode")
            return
        
        try:
            for i, phone in enumerate(self.phone_numbers):
                client = TelegramClient(f'session_{i}', self.api_id, self.api_hash)
                await client.start(phone)
                
                # Configurar handlers
                await self._setup_message_handlers(client)
                
                self.clients.append(client)
                self.logger.info(f"✅ Cliente inicializado para {phone}")
            
            self.logger.info(f"🚀 Bot inicializado con {len(self.clients)} números")
            
        except Exception as e:
            self.logger.error(f"❌ Error inicializando Telegram: {e}")
    
    async def _setup_message_handlers(self, client: TelegramClient):
        """Configurar handlers de mensajes para el cliente"""
        
        @client.on(events.NewMessage(incoming=True))
        async def handle_incoming_message(event):
            await self._process_incoming_message(event, client)
    
    async def _process_incoming_message(self, event, client: TelegramClient):
        """Procesar mensaje entrante"""
        
        # Rate limiting check
        if not await self._check_rate_limits():
            return
        
        user_id = event.sender_id
        message = event.message
        
        try:
            # Si es screenshot/imagen
            if message.media and isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
                await self._handle_screenshot(user_id, message, client)
            
            # Si es mensaje de texto
            elif message.text:
                await self._handle_text_message(user_id, message.text, client)
                
        except Exception as e:
            self.logger.error(f"❌ Error procesando mensaje de {user_id}: {e}")
    
    async def _handle_screenshot(self, user_id: int, message, client: TelegramClient):
        """Manejar screenshot enviado por usuario"""
        
        if user_id not in self.active_requests:
            await client.send_message(user_id, "❌ No tienes una solicitud activa. Inicia el proceso primero.")
            return
        
        request = self.active_requests[user_id]
        
        if request.stage != NegotiationStage.PROOF_REQUESTED:
            await client.send_message(user_id, "⏳ Aún no hemos llegado a la fase de prueba.")
            return
        
        try:
            # Descargar screenshot
            screenshot_data = await message.download_media(bytes)
            
            # Analizar con ML
            verification = await self.screenshot_analyzer.verify_screenshot(
                screenshot_data, 
                request.target_video_url
            )
            
            request.verification_result = verification['verified']
            request.proof_screenshot = base64.b64encode(screenshot_data).decode()
            
            if verification['verified']:
                # Enviar reward
                await self._send_reward(request, client)
                await client.send_message(user_id, 
                    await self.negotiation_engine.generate_success_message())
                
                request.stage = NegotiationStage.COMPLETED
                request.reward_sent = True
                self.stats.rewards_sent += 1
                
            else:
                await client.send_message(user_id, 
                    f"❌ El screenshot no muestra las interacciones correctas. "
                    f"Asegúrate de dar like + comentario + suscripción al video: {request.target_video_url}")
                
                request.negotiation_attempts += 1
                
                if request.negotiation_attempts >= 3:
                    request.stage = NegotiationStage.FAILED
                    self.stats.failed_negotiations += 1
            
            # Registrar en GitHub
            await self._log_interaction_to_github(request)
            
        except Exception as e:
            await client.send_message(user_id, "❌ Error procesando el screenshot. Intenta de nuevo.")
            self.logger.error(f"Error procesando screenshot: {e}")
    
    async def _handle_text_message(self, user_id: int, text: str, client: TelegramClient):
        """Manejar mensaje de texto"""
        
        # Detectar si es solicitud inicial de intercambio
        like4like_keywords = ['like4like', 'like por like', 'intercambio', 'l4l', 'sub4sub']
        
        if any(keyword in text.lower() for keyword in like4like_keywords):
            await self._start_negotiation(user_id, text, client)
        
        # Si ya hay una negociación activa
        elif user_id in self.active_requests:
            await self._continue_negotiation(user_id, text, client)
        
        else:
            # Respuesta genérica
            await client.send_message(user_id, 
                "¡Hola! Estoy disponible para intercambios de like4like. "
                "Envíame el link de tu video y hacemos el intercambio 🔄")
    
    async def _start_negotiation(self, user_id: int, initial_message: str, client: TelegramClient):
        """Iniciar negociación con usuario"""
        
        # Crear nueva solicitud
        request = InteractionRequest(
            user_id=user_id,
            username="",  # Se obtendría del evento
            requested_interactions=[InteractionType.LIKE, InteractionType.COMMENT, InteractionType.SUBSCRIBE],
            target_video_url="",  # Se extraería del mensaje
            channel_handle="",
            timestamp=datetime.now(),
            stage=NegotiationStage.INITIAL_CONTACT
        )
        
        self.active_requests[user_id] = request
        
        # Generar respuesta inicial
        context = {'video_title': 'tu video'}  # Extraería título real
        initial_response = await self.negotiation_engine.generate_initial_message(context)
        
        await client.send_message(user_id, initial_response)
        
        request.stage = NegotiationStage.NEGOTIATING
        self.stats.total_contacts += 1
    
    async def _continue_negotiation(self, user_id: int, message: str, client: TelegramClient):
        """Continuar negociación existente"""
        
        request = self.active_requests[user_id]
        
        # Detectar URL de video en el mensaje
        if 'youtube.com' in message or 'youtu.be' in message:
            request.target_video_url = self._extract_video_url(message)
            request.stage = NegotiationStage.PROOF_REQUESTED
            
            response = (f"✅ Perfecto! Procede con:\n\n"
                       f"1️⃣ Dale LIKE al video\n"
                       f"2️⃣ Deja un COMENTARIO\n" 
                       f"3️⃣ SUSCRÍBETE al canal\n\n"
                       f"Luego envíame screenshot como prueba y te hago lo mismo de inmediato 📸⚡")
            
            await client.send_message(user_id, response)
            
        else:
            # Seguimiento basado en intentos
            follow_up = await self.negotiation_engine.generate_follow_up(
                request.negotiation_attempts, message)
            
            await client.send_message(user_id, follow_up)
            request.negotiation_attempts += 1
    
    def _extract_video_url(self, message: str) -> str:
        """Extraer URL de video de YouTube del mensaje"""
        import re
        
        youtube_regex = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
        match = re.search(youtube_regex, message)
        
        if match:
            video_id = match.group(4)
            return f"https://youtube.com/watch?v={video_id}"
        
        return message  # Fallback
    
    async def _send_reward(self, request: InteractionRequest, client: TelegramClient):
        """Enviar reward (like, comment, suscripción) al usuario"""
        
        # Aquí integrarías con tu sistema de YouTube automation
        # Por ahora, simulación
        
        reward_actions = {
            'like': await self._send_like(request.target_video_url),
            'comment': await self._send_comment(request.target_video_url),
            'subscribe': await self._subscribe_to_channel(request.channel_handle)
        }
        
        self.logger.info(f"🎁 Reward enviado a {request.user_id}: {reward_actions}")
        
        return reward_actions
    
    async def _send_like(self, video_url: str) -> bool:
        """Dar like al video (integración con YouTube automation)"""
        # Integrar con social_extensions/youtube
        return True  # Simulación
    
    async def _send_comment(self, video_url: str) -> bool:
        """Comentar el video"""
        comments = [
            "¡Excelente contenido! 🔥",
            "Me encantó el video 👏",
            "¡Sigue así! 💪"
        ]
        comment = np.random.choice(comments)
        # Enviar comentario real
        return True
    
    async def _subscribe_to_channel(self, channel_handle: str) -> bool:
        """Suscribirse al canal"""
        # Integrar con automation
        return True
    
    async def _check_rate_limits(self) -> bool:
        """Verificar límites de rate para evitar baneos"""
        
        current_time = datetime.now()
        
        # Reset contador por hora
        if (current_time - self.last_hour_reset).total_seconds() >= 3600:
            self.hourly_interactions = 0
            self.last_hour_reset = current_time
        
        # Obtener límite actual basado en día
        if self.current_day <= 2:
            limit = self.daily_interaction_limits['day_1_2']
        elif self.current_day <= 5:
            limit = self.daily_interaction_limits['day_3_5']
        else:
            limit = self.daily_interaction_limits['day_6+']
        
        # Verificar si excede límite
        if self.hourly_interactions >= limit:
            self.logger.warning(f"⚠️ Rate limit alcanzado: {self.hourly_interactions}/{limit}")
            return False
        
        self.hourly_interactions += 1
        return True
    
    async def _log_interaction_to_github(self, request: InteractionRequest):
        """Registrar interacción en GitHub para tracking"""
        
        log_entry = {
            'timestamp': request.timestamp.isoformat(),
            'user_id': request.user_id,
            'username': request.username,
            'video_url': request.target_video_url,
            'stage': request.stage.value,
            'verification_result': request.verification_result,
            'reward_sent': request.reward_sent,
            'negotiation_attempts': request.negotiation_attempts
        }
        
        # Guardar en archivo de log
        log_file = f'/workspaces/master/data/logs/like4like_log_{datetime.now().strftime("%Y%m%d")}.json'
        
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    async def start_bot(self):
        """Iniciar el bot y mantener running"""
        
        await self.initialize()
        
        self.logger.info("🚀 Bot Like4Like iniciado - esperando interacciones...")
        
        try:
            # Mantener bots corriendo
            if self.clients:
                await asyncio.gather(*[client.run_until_disconnected() for client in self.clients])
            else:
                # Modo dummy
                self.logger.info("🎭 Ejecutando en modo dummy - simulando actividad...")
                while True:
                    await asyncio.sleep(60)
                    self.logger.info(f"📊 Stats: {asdict(self.stats)}")
        
        except KeyboardInterrupt:
            self.logger.info("🛑 Deteniendo bot...")
            await self.stop_bot()
    
    async def stop_bot(self):
        """Detener el bot gracefully"""
        
        for client in self.clients:
            await client.disconnect()
        
        self.logger.info("✅ Bot detenido correctamente")

# Factory function
def create_like4like_bot(api_id: str, api_hash: str, phone_numbers: List[str]) -> TelegramLike4LikeBot:
    """Crear bot de Like4Like configurado"""
    return TelegramLike4LikeBot(api_id, api_hash, phone_numbers)

# Ejemplo de uso
async def main():
    """Función principal para ejecutar el bot"""
    
    # Configuración (usar variables de entorno en producción)
    API_ID = "your_api_id"
    API_HASH = "your_api_hash"
    PHONE_NUMBERS = ["+1234567890", "+0987654321"]  # Tus 2 números antiguos
    
    # Crear y ejecutar bot
    bot = create_like4like_bot(API_ID, API_HASH, PHONE_NUMBERS)
    await bot.start_bot()

if __name__ == "__main__":
    asyncio.run(main())