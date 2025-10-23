"""
Implementaciones Dummy para Dependencies Externas
Permite ejecutar el sistema sin instalar dependencias reales
"""

import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import json
import random
import time

logger = logging.getLogger(__name__)

# ============================================================================
# TELEGRAM DUMMY IMPLEMENTATIONS
# ============================================================================

class DummyTelegramClient:
    """Implementación dummy de TelegramClient"""
    
    def __init__(self, session_name: str, api_id: int, api_hash: str):
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.connected = False
        logger.info(f"DummyTelegramClient iniciado: {session_name}")
    
    async def start(self, phone: str = None, password: str = None):
        """Simula inicio de sesión"""
        self.connected = True
        logger.info("Dummy Telegram: Sesión iniciada")
        return True
    
    async def disconnect(self):
        """Simula desconexión"""
        self.connected = False
        logger.info("Dummy Telegram: Desconectado")
    
    async def send_message(self, entity: str, message: str):
        """Simula envío de mensaje"""
        logger.info(f"Dummy Telegram: Mensaje enviado a {entity}: {message[:50]}...")
        return {"id": random.randint(1000, 9999), "date": time.time()}
    
    async def get_messages(self, entity: str, limit: int = 10):
        """Simula obtención de mensajes"""
        messages = []
        for i in range(limit):
            messages.append({
                "id": random.randint(1000, 9999),
                "text": f"Mensaje dummy {i+1}",
                "date": time.time() - (i * 3600)
            })
        logger.info(f"Dummy Telegram: {len(messages)} mensajes obtenidos de {entity}")
        return messages

# Clases adicionales de telethon
class events:
    class NewMessage:
        def __init__(self, pattern=None, chats=None):
            self.pattern = pattern
            self.chats = chats

class MessageMediaPhoto:
    def __init__(self):
        self.photo = {"id": random.randint(1000, 9999)}

class MessageMediaDocument:
    def __init__(self):
        self.document = {"id": random.randint(1000, 9999)}

# ============================================================================
# INSTAGRAM DUMMY IMPLEMENTATIONS  
# ============================================================================

class DummyInstagramAPI:
    """Implementación dummy de Instagram API"""
    
    def __init__(self):
        self.logged_in = False
        logger.info("DummyInstagramAPI iniciado")
    
    def login(self, username: str, password: str):
        """Simula login"""
        self.logged_in = True
        logger.info(f"Dummy Instagram: Login exitoso para {username}")
        return True
    
    def upload_photo(self, photo_path: str, caption: str = ""):
        """Simula subida de foto"""
        logger.info(f"Dummy Instagram: Foto subida: {photo_path}")
        return {"media": {"id": random.randint(1000, 9999)}}
    
    def get_user_info(self, username: str):
        """Simula obtención de info de usuario"""
        return {
            "pk": random.randint(1000, 9999),
            "username": username,
            "followers": random.randint(100, 10000),
            "following": random.randint(50, 1000)
        }

# Alias para compatibilidad
Client = DummyInstagramAPI

# ============================================================================
# TWITTER DUMMY IMPLEMENTATIONS
# ============================================================================

class DummyTwitterAPI:
    """Implementación dummy de Twitter API"""
    
    def __init__(self, consumer_key: str, consumer_secret: str, 
                 access_token: str, access_token_secret: str):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        logger.info("DummyTwitterAPI iniciado")
    
    def update_status(self, status: str):
        """Simula tweet"""
        logger.info(f"Dummy Twitter: Tweet enviado: {status[:50]}...")
        return {"id": random.randint(1000, 9999), "text": status}
    
    def get_user(self, username: str):
        """Simula obtención de usuario"""
        return {
            "id": random.randint(1000, 9999),
            "screen_name": username,
            "followers_count": random.randint(100, 10000)
        }

# Clase API para compatibilidad con tweepy
class API:
    def __init__(self, auth):
        self.auth = auth
        logger.info("Dummy Twitter API wrapper iniciado")
    
    def update_status(self, status: str):
        return DummyTwitterAPI("", "", "", "").update_status(status)

# ============================================================================
# LINKEDIN DUMMY IMPLEMENTATIONS
# ============================================================================

class DummyLinkedInAPI:
    """Implementación dummy de LinkedIn API"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        logger.info("DummyLinkedInAPI iniciado")
    
    def post_update(self, text: str):
        """Simula post en LinkedIn"""
        logger.info(f"Dummy LinkedIn: Post publicado: {text[:50]}...")
        return {"id": f"post_{random.randint(1000, 9999)}"}
    
    def get_profile(self, public_id: str):
        """Simula obtención de perfil"""
        return {
            "id": random.randint(1000, 9999),
            "public_id": public_id,
            "firstName": "Usuario",
            "lastName": "Dummy"
        }

# Alias para compatibilidad
Linkedin = DummyLinkedInAPI

# ============================================================================
# META/FACEBOOK DUMMY IMPLEMENTATIONS
# ============================================================================

class DummyFacebookAdsApi:
    """Implementación dummy de Facebook Ads API"""
    
    @classmethod
    def init(cls, app_id: str, app_secret: str, access_token: str):
        logger.info("Dummy Facebook Ads API inicializado")
        return cls()

class DummyAdAccount:
    """Implementación dummy de AdAccount"""
    
    def __init__(self, account_id: str):
        self.account_id = account_id
    
    def get_campaigns(self, fields: List[str] = None):
        """Simula obtención de campañas"""
        campaigns = []
        for i in range(3):
            campaigns.append({
                "id": f"campaign_{random.randint(1000, 9999)}",
                "name": f"Campaña Dummy {i+1}",
                "status": "ACTIVE"
            })
        return campaigns
    
    def create_campaign(self, params: Dict):
        """Simula creación de campaña"""
        logger.info(f"Dummy Meta: Campaña creada: {params.get('name', 'Sin nombre')}")
        return {"id": f"campaign_{random.randint(1000, 9999)}"}

class DummyCampaign:
    """Implementación dummy de Campaign"""
    
    def __init__(self, campaign_id: str = None):
        self.campaign_id = campaign_id or f"campaign_{random.randint(1000, 9999)}"
    
    def api_create(self, parent_id: str, fields: List[str] = None):
        logger.info(f"Dummy Meta: Campaña API creada: {self.campaign_id}")
        return self

class DummyAdSet:
    """Implementación dummy de AdSet"""
    
    def __init__(self, adset_id: str = None):
        self.adset_id = adset_id or f"adset_{random.randint(1000, 9999)}"
    
    def api_create(self, parent_id: str, fields: List[str] = None):
        logger.info(f"Dummy Meta: AdSet API creado: {self.adset_id}")
        return self

class DummyAd:
    """Implementación dummy de Ad"""
    
    def __init__(self, ad_id: str = None):
        self.ad_id = ad_id or f"ad_{random.randint(1000, 9999)}"
    
    def api_create(self, parent_id: str, fields: List[str] = None):
        logger.info(f"Dummy Meta: Ad API creado: {self.ad_id}")
        return self

class DummyAdCreative:
    """Implementación dummy de AdCreative"""
    
    def __init__(self, creative_id: str = None):
        self.creative_id = creative_id or f"creative_{random.randint(1000, 9999)}"
    
    def api_create(self, parent_id: str, fields: List[str] = None):
        logger.info(f"Dummy Meta: Creative API creado: {self.creative_id}")
        return self

class DummyAdImage:
    """Implementación dummy de AdImage"""
    
    def __init__(self, image_hash: str = None):
        self.image_hash = image_hash or f"hash_{random.randint(1000, 9999)}"
    
    def api_create(self, parent_id: str, fields: List[str] = None):
        logger.info(f"Dummy Meta: Imagen API creada: {self.image_hash}")
        return self

class DummyAdVideo:
    """Implementación dummy de AdVideo"""
    
    def __init__(self, video_id: str = None):
        self.video_id = video_id or f"video_{random.randint(1000, 9999)}"
    
    def api_create(self, parent_id: str, fields: List[str] = None):
        logger.info(f"Dummy Meta: Video API creado: {self.video_id}")
        return self

class FacebookRequestError(Exception):
    """Dummy exception para Facebook"""
    pass

# Aliases para compatibilidad con facebook_business
FacebookAdsApi = DummyFacebookAdsApi
AdAccount = DummyAdAccount
Campaign = DummyCampaign
AdSet = DummyAdSet
Ad = DummyAd
AdCreative = DummyAdCreative
AdImage = DummyAdImage
AdVideo = DummyAdVideo

# ============================================================================
# ML/AI DUMMY IMPLEMENTATIONS
# ============================================================================

class DummyYOLO:
    """Implementación dummy de YOLO"""
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        self.model_path = model_path
        logger.info(f"Dummy YOLO modelo cargado: {model_path}")
    
    def predict(self, source: str, save: bool = False, conf: float = 0.5):
        """Simula predicción YOLO"""
        logger.info(f"Dummy YOLO: Predicción en {source}")
        
        # Simular resultados
        results = []
        for i in range(random.randint(1, 5)):
            results.append({
                "class": random.choice(["person", "car", "phone", "laptop"]),
                "confidence": random.uniform(0.5, 0.95),
                "bbox": [random.randint(0, 640), random.randint(0, 480), 
                        random.randint(50, 200), random.randint(50, 200)]
            })
        
        return results
    
    def train(self, data: str, epochs: int = 100):
        """Simula entrenamiento"""
        logger.info(f"Dummy YOLO: Entrenamiento iniciado - {epochs} épocas")
        return {"best_model": f"best_dummy_{random.randint(1000, 9999)}.pt"}

# ============================================================================
# OPENCV DUMMY IMPLEMENTATIONS
# ============================================================================

class DummyCV2:
    """Implementación dummy de OpenCV"""
    
    @staticmethod
    def imread(path: str, flags: int = 1):
        """Simula lectura de imagen"""
        logger.info(f"Dummy CV2: Imagen leída: {path}")
        # Simular array de imagen (altura, ancho, canales)
        import numpy as np
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    @staticmethod
    def imwrite(path: str, img):
        """Simula escritura de imagen"""
        logger.info(f"Dummy CV2: Imagen guardada: {path}")
        return True
    
    @staticmethod
    def resize(img, dsize, interpolation=None):
        """Simula redimensionamiento"""
        import numpy as np
        return np.random.randint(0, 255, (*dsize[::-1], 3), dtype=np.uint8)
    
    @staticmethod
    def cvtColor(img, code):
        """Simula conversión de color"""
        import numpy as np
        # Simular conversión (mantener dimensiones)
        if len(img.shape) == 3 and img.shape[2] == 3:
            return np.random.randint(0, 255, img.shape[:2], dtype=np.uint8)
        return img

# Constantes de OpenCV
INTER_LINEAR = 1
COLOR_BGR2GRAY = 6
COLOR_RGB2BGR = 4

# ============================================================================
# AWS BOTO3 DUMMY IMPLEMENTATIONS
# ============================================================================

class DummyBoto3Client:
    """Implementación dummy de cliente boto3"""
    
    def __init__(self, service_name: str, region_name: str = "us-east-1"):
        self.service_name = service_name
        self.region_name = region_name
        logger.info(f"Dummy Boto3: Cliente {service_name} creado")
    
    def upload_file(self, filename: str, bucket: str, key: str):
        """Simula subida de archivo a S3"""
        logger.info(f"Dummy S3: Archivo subido {filename} -> s3://{bucket}/{key}")
        return True
    
    def download_file(self, bucket: str, key: str, filename: str):
        """Simula descarga de archivo de S3"""
        logger.info(f"Dummy S3: Archivo descargado s3://{bucket}/{key} -> {filename}")
        return True
    
    def invoke(self, FunctionName: str, Payload: bytes):
        """Simula invocación de Lambda"""
        logger.info(f"Dummy Lambda: Función invocada: {FunctionName}")
        return {
            "StatusCode": 200,
            "Payload": b'{"result": "dummy_success"}'
        }

class DummyBoto3:
    """Clase principal dummy de boto3"""
    
    @staticmethod
    def client(service_name: str, region_name: str = "us-east-1", **kwargs):
        """Crea cliente dummy"""
        return DummyBoto3Client(service_name, region_name)
    
    @staticmethod
    def resource(service_name: str, region_name: str = "us-east-1", **kwargs):
        """Crea recurso dummy"""
        logger.info(f"Dummy Boto3: Recurso {service_name} creado")
        return DummyBoto3Client(service_name, region_name)

# ============================================================================
# NUMPY DUMMY (para casos extremos donde numpy no esté disponible)
# ============================================================================

class DummyNumpyRandom:
    """Implementación dummy de numpy.random"""
    
    @staticmethod
    def randint(low: int, high: int, size=None):
        """Simula numpy random randint"""
        if size is None:
            return random.randint(low, high-1)
        elif isinstance(size, int):
            return [random.randint(low, high-1) for _ in range(size)]
        else:
            # Para tuplas de tamaño
            total_elements = 1
            for dim in size:
                total_elements *= dim
            return [random.randint(low, high-1) for _ in range(total_elements)]
    
    @staticmethod
    def uniform(low: float, high: float, size=None):
        """Simula numpy random uniform"""
        if size is None:
            return random.uniform(low, high)
        elif isinstance(size, int):
            return [random.uniform(low, high) for _ in range(size)]
        else:
            total_elements = 1
            for dim in size:
                total_elements *= dim
            return [random.uniform(low, high) for _ in range(total_elements)]

class DummyNumpy:
    """Implementación dummy básica de numpy (solo para emergencias)"""
    
    # Instancia de random
    random = DummyNumpyRandom()
    
    @staticmethod
    def array(data):
        """Simula numpy array"""
        return data  # Devolver datos originales
    
    @staticmethod
    def zeros(shape):
        """Simula numpy zeros"""
        if isinstance(shape, int):
            return [0] * shape
        else:
            total_elements = 1
            for dim in shape:
                total_elements *= dim
            return [0] * total_elements
    
    @staticmethod
    def ones(shape):
        """Simula numpy ones"""
        if isinstance(shape, int):
            return [1] * shape
        else:
            total_elements = 1
            for dim in shape:
                total_elements *= dim
            return [1] * total_elements

# Crear instancia global para compatibilidad
np = DummyNumpy()

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_dummy_implementation(module_name: str):
    """Obtiene la implementación dummy para un módulo específico"""
    dummy_mapping = {
        "telethon": {
            "TelegramClient": DummyTelegramClient,
            "events": events,
            "MessageMediaPhoto": MessageMediaPhoto,
            "MessageMediaDocument": MessageMediaDocument
        },
        "instagrapi": {
            "Client": DummyInstagramAPI
        },
        "tweepy": {
            "API": API
        },
        "linkedin_api": {
            "Linkedin": DummyLinkedInAPI
        },
        "facebook_business": {
            "FacebookAdsApi": DummyFacebookAdsApi,
            "AdAccount": DummyAdAccount,
            "Campaign": DummyCampaign,
            "AdSet": DummyAdSet,
            "Ad": DummyAd,
            "AdCreative": DummyAdCreative,
            "AdImage": DummyAdImage,
            "AdVideo": DummyAdVideo,
            "FacebookRequestError": FacebookRequestError
        },
        "ultralytics": {
            "YOLO": DummyYOLO
        },
        "cv2": DummyCV2,
        "boto3": DummyBoto3,
        "numpy": DummyNumpy
    }
    
    return dummy_mapping.get(module_name, {})

def install_dummy_modules():
    """Instala módulos dummy en sys.modules para importación automática"""
    import sys
    
    # Instalar módulos dummy
    dummy_modules = {
        "telethon": type("telethon", (), {
            "TelegramClient": DummyTelegramClient,
            "events": events
        }),
        "telethon.tl.types": type("types", (), {
            "MessageMediaPhoto": MessageMediaPhoto,
            "MessageMediaDocument": MessageMediaDocument
        }),
        "instagrapi": type("instagrapi", (), {
            "Client": DummyInstagramAPI
        }),
        "tweepy": type("tweepy", (), {
            "API": API
        }),
        "linkedin_api": type("linkedin_api", (), {
            "Linkedin": DummyLinkedInAPI
        }),
        "facebook_business.api": type("api", (), {
            "FacebookAdsApi": DummyFacebookAdsApi
        }),
        "facebook_business.adobjects.adaccount": type("adaccount", (), {
            "AdAccount": DummyAdAccount
        }),
        "facebook_business.adobjects.campaign": type("campaign", (), {
            "Campaign": DummyCampaign
        }),
        "facebook_business.adobjects.adset": type("adset", (), {
            "AdSet": DummyAdSet
        }),
        "facebook_business.adobjects.ad": type("ad", (), {
            "Ad": DummyAd
        }),
        "facebook_business.adobjects.adcreative": type("adcreative", (), {
            "AdCreative": DummyAdCreative
        }),
        "facebook_business.adobjects.adimage": type("adimage", (), {
            "AdImage": DummyAdImage
        }),
        "facebook_business.adobjects.advideo": type("advideo", (), {
            "AdVideo": DummyAdVideo
        }),
        "facebook_business.exceptions": type("exceptions", (), {
            "FacebookRequestError": FacebookRequestError
        }),
        "ultralytics": type("ultralytics", (), {
            "YOLO": DummyYOLO
        }),
        "cv2": DummyCV2,
        "boto3": DummyBoto3
    }
    
    for module_name, module_obj in dummy_modules.items():
        if module_name not in sys.modules:
            sys.modules[module_name] = module_obj
            logger.info(f"Módulo dummy instalado: {module_name}")

# Auto-instalar módulos dummy si DUMMY_MODE está activo
import os
if os.getenv("DUMMY_MODE", "true").lower() == "true":
    install_dummy_modules()
    logger.info("🎭 Módulos dummy instalados automáticamente")