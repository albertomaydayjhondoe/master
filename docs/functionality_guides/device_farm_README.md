# 📱 Device Farm Management

## 📋 Resumen Ejecutivo
- **Propósito**: Gestión y automatización de farm de dispositivos Android via ADB/Appium
- **Estado**: 🟡 Durmiente - Controllers dummy activos
- **Complejidad**: Avanzado
- **Dependencias**: `appium-python-client`, `selenium`, `adb-shell`

## 🚀 Inicio Rápido

### 1. Verificar Estado Actual (Dummy Mode)
```python
from device_farm.controllers.factory import create_device_manager

# Crear device manager en modo dummy
device_manager = create_device_manager()
print(f"Device Manager Mode: {'Dummy' if device_manager.dummy_mode else 'Production'}")

# Verificar dispositivos "disponibles"
devices = await device_manager.get_available_devices()
print(f"Devices detected: {len(devices)}")
```

### 2. Test de Conexión
```python
import asyncio

async def test_device_connection():
    # Listar dispositivos dummy
    devices = await device_manager.get_available_devices()
    
    for device in devices:
        print(f"Device: {device['id']}")
        print(f"  Status: {device['status']}")
        print(f"  Model: {device['model']}")
        print(f"  Android: {device['android_version']}")
```

### 3. Simulación de Automatización
```python
# Ejecutar acción dummy en dispositivo
async def simulate_automation():
    device_id = "dummy_device_001"
    
    # Conectar a dispositivo
    session = await device_manager.connect_device(device_id)
    
    # Ejecutar acciones (dummy)
    await session.open_app("com.zhiliaoapp.musically")  # TikTok
    await session.scroll_down(duration=2)
    await session.tap_element("like_button")
    
    # Obtener estado
    status = await session.get_device_status()
    print(f"Session Status: {status}")
    
    # Desconectar
    await device_manager.disconnect_device(device_id)

asyncio.run(simulate_automation())
```

## ⚙️ Configuración Detallada

### Instalación de Dependencias (Para Activación)
```bash
# Instalar ADB
sudo apt update
sudo apt install android-tools-adb android-tools-fastboot

# Verificar ADB
adb version

# Instalar Appium Server
npm install -g appium
appium driver install uiautomator2

# Dependencias Python
pip install appium-python-client
pip install selenium
pip install adb-shell
```

### Variables de Entorno
```bash
# En .env para activación
DEVICE_FARM_MODE=production           # production/dummy
ADB_SERVER_PORT=5037                  # Puerto ADB server
APPIUM_SERVER_URL=http://localhost:4723  # URL Appium server
DEVICE_CONNECTION_TIMEOUT=30          # Timeout conexión (segundos)
MAX_PARALLEL_SESSIONS=5               # Max sesiones paralelas
DEVICE_HEARTBEAT_INTERVAL=60          # Heartbeat cada 60s
```

### Configuración de Dispositivos
```yaml
# config/device_farm/devices.yaml
devices:
  android_device_001:
    udid: "192.168.1.100:5555"
    model: "Samsung Galaxy S21"
    android_version: "12"
    capabilities:
      platformName: "Android"
      deviceName: "Galaxy S21"
      automationName: "UiAutomator2"
    apps:
      tiktok: "com.zhiliaoapp.musically"
      instagram: "com.instagram.android"
    
  android_device_002:
    udid: "192.168.1.101:5555"
    model: "Google Pixel 6"
    android_version: "13"
    capabilities:
      platformName: "Android"
      deviceName: "Pixel 6"
      automationName: "UiAutomator2"
```

## 📚 API Reference

### Core Classes

#### `DeviceManager`
Gestor principal de la farm de dispositivos.

```python
# Crear instancia
from device_farm.controllers.factory import create_device_manager

device_manager = create_device_manager(dummy_mode=False)  # Modo producción

# Verificar inicialización
print(f"Initialized: {device_manager.is_initialized}")
print(f"ADB connected: {device_manager.adb_connected}")
```

#### `DeviceSession`
Sesión activa con un dispositivo específico.

```python
# Obtener sesión activa
session = await device_manager.get_session(device_id)

# Información de la sesión
print(f"Device ID: {session.device_id}")  
print(f"Connected: {session.is_connected}")
print(f"App running: {session.current_app}")
```

### Methods Principales

#### `get_available_devices() -> List[Dict]`
Lista todos los dispositivos disponibles.

```python
# Obtener dispositivos disponibles
devices = await device_manager.get_available_devices()

for device in devices:
    print(f"ID: {device['id']}")
    print(f"Status: {device['status']}")  # connected/disconnected/busy
    print(f"Model: {device['model']}")
    print(f"Battery: {device['battery_level']}%")
```

#### `connect_device(device_id: str) -> DeviceSession`
Conecta a un dispositivo específico.

```python
# Conectar dispositivo
try:
    session = await device_manager.connect_device("android_device_001")
    print(f"Connected to {session.device_id}")
    
    # Obtener capabilities
    caps = await session.get_capabilities()
    print(f"Platform: {caps['platformName']}")
    print(f"Version: {caps['platformVersion']}")
    
except DeviceConnectionError as e:
    print(f"Connection failed: {e}")
```

#### `execute_automation_script(device_id, script) -> Dict`
Ejecuta script de automatización en dispositivo.

```python
# Script de automatización
automation_script = {
    "steps": [
        {"action": "open_app", "package": "com.zhiliaoapp.musically"},
        {"action": "wait", "duration": 3},
        {"action": "swipe", "direction": "up", "duration": 2},
        {"action": "tap", "element": "like_button"},
        {"action": "wait", "duration": 1},
        {"action": "tap", "element": "follow_button"}
    ],
    "timeout": 60,
    "retry_on_error": True
}

# Ejecutar script
result = await device_manager.execute_automation_script(
    "android_device_001", 
    automation_script
)

print(f"Script executed: {result['success']}")
print(f"Steps completed: {result['steps_completed']}/{result['total_steps']}")
if result['error']:
    print(f"Error: {result['error']}")
```

### Device Session Methods

#### `open_app(package_name: str)`
Abre aplicación en el dispositivo.

```python
# Abrir TikTok
await session.open_app("com.zhiliaoapp.musically")

# Verificar que la app se abrió
current_app = await session.get_current_app()
print(f"Current app: {current_app}")
```

#### `tap_element(element_locator: str)`
Hace tap en un elemento.

```python
# Tap por ID de recurso
await session.tap_element("com.zhiliaoapp.musically:id/like_button")

# Tap por texto
await session.tap_element_by_text("Follow")

# Tap por coordenadas
await session.tap_coordinate(500, 1000)
```

#### `swipe/scroll Actions`
Acciones de deslizamiento y scroll.

```python
# Scroll hacia abajo (feed de TikTok)
await session.scroll_down(duration=2)

# Swipe horizontal (cambiar video)  
await session.swipe_left()

# Scroll personalizado
await session.swipe(
    start_x=500, start_y=1000,
    end_x=500, end_y=500,
    duration=1500
)
```

#### `get_screen_info() -> Dict`
Obtiene información de la pantalla actual.

```python
# Información de pantalla
screen_info = await session.get_screen_info()

print(f"Resolution: {screen_info['width']}x{screen_info['height']}")
print(f"Orientation: {screen_info['orientation']}")
print(f"Current activity: {screen_info['current_activity']}")

# Screenshot
screenshot = await session.take_screenshot()
with open("screenshot.png", "wb") as f:
    f.write(screenshot)
```

## 🔧 Troubleshooting

### Problemas de Conexión

#### 1. **ADB no detecta dispositivos**
```bash
# Reiniciar ADB server
adb kill-server
adb start-server

# Listar dispositivos
adb devices

# Conectar dispositivo por TCP/IP
adb connect 192.168.1.100:5555
```

#### 2. **Appium connection failed**
```bash
# Verificar que Appium esté corriendo
ps aux | grep appium

# Iniciar Appium server
appium --port 4723 --log-level debug

# Test de conexión
curl http://localhost:4723/wd/hub/status
```

#### 3. **Device authorization required**
```bash
# Autorizar dispositivo (aparecerá popup en el teléfono)
adb devices
# List of devices attached
# 192.168.1.100:5555    unauthorized

# Después de aceptar en el teléfono
adb devices
# List of devices attached  
# 192.168.1.100:5555    device
```

### Problemas de Automatización

#### 4. **Element not found**
```python
# Esperar elemento antes de interactuar
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Esperar hasta que elemento esté presente
element = WebDriverWait(session.driver, 10).until(
    EC.presence_of_element_located(("id", "like_button"))
)
await session.tap_element_object(element)
```

#### 5. **App crashes durante automatización**
```python
# Detectar y recuperar de crashes
async def safe_automation_step(session, action):
    try:
        await action()
    except Exception as e:
        # Verificar si app sigue corriendo
        current_app = await session.get_current_app()
        if current_app != "com.zhiliaoapp.musically":
            # App crasheó, reiniciar
            await session.open_app("com.zhiliaoapp.musically")
            await asyncio.sleep(3)
            # Reintentar acción
            await action()
        else:
            raise e
```

### Debug Mode

```python
# Activar logging detallado
import logging
logging.getLogger("appium").setLevel(logging.DEBUG)
logging.getLogger("selenium").setLevel(logging.DEBUG)

# Debug de sesión
debug_info = await session.get_debug_info()
print("Session Debug Info:")
import pprint
pprint.pprint(debug_info)

# Test de conectividad
connectivity = await device_manager.test_device_connectivity("android_device_001")
print(f"Connectivity test: {connectivity}")
```

## 🔗 Integraciones

### Con Sistema de Monitoring
```python
from social_extensions.telegram.monitoring import ActivityMetric

# Monitorear actividad de dispositivos
async def monitor_device_activity(device_id, action_type):
    start_time = time.time()
    
    try:
        # Ejecutar acción
        result = await device_manager.execute_action(device_id, action_type)
        success = result['success']
        
    except Exception as e:
        success = False
        result = {"error": str(e)}
    
    # Log actividad
    duration_ms = (time.time() - start_time) * 1000
    
    activity = ActivityMetric(
        timestamp=datetime.now(),
        type=f"device_{action_type}",
        group_id=device_id,
        success=success,
        duration_ms=duration_ms,
        metadata={
            "device_id": device_id,
            "action": action_type,
            "result": result
        }
    )
    
    await monitor.log_activity(activity)
```

### Con ML Integration
```python
# Usar ML para guiar automatización
async def ml_guided_automation(session, content_context):
    # Obtener predicciones ML sobre qué acciones tomar
    from ml_integration.ultralytics_bridge import create_ml_bridge
    
    ml_bridge = create_ml_bridge()
    
    # Analizar contexto actual
    screenshot = await session.take_screenshot()
    analysis = await ml_bridge.analyze_screenshot(screenshot)
    
    # Decidir acción basada en análisis
    if analysis.engagement_prediction > 0.7:
        # Alto potencial - hacer like y seguir
        await session.tap_element("like_button")
        await asyncio.sleep(1)
        await session.tap_element("follow_button")
    else:
        # Bajo potencial - solo scroll
        await session.scroll_down(duration=2)
```

### Con Content Pipeline
```python  
# Pipeline automatizado de interacción con contenido
async def automated_content_interaction():
    devices = await device_manager.get_available_devices()
    
    # Distribuir trabajo entre dispositivos
    for i, device in enumerate(devices[:3]):  # Usar max 3 dispositivos
        session = await device_manager.connect_device(device['id'])
        
        # Cada dispositivo maneja diferentes hashtags/creators
        hashtags = ["#viral", "#trending", "#fyp"][i % 3]
        
        await asyncio.create_task(
            interact_with_hashtag(session, hashtags)
        )

async def interact_with_hashtag(session, hashtag):
    # Buscar hashtag
    await session.open_app("com.zhiliaoapp.musically")
    await session.tap_element("search_button")
    await session.type_text(hashtag)
    await session.tap_element("search_confirm")
    
    # Interactuar con primeros 10 videos
    for _ in range(10):
        await asyncio.sleep(random.uniform(3, 7))  # Delay natural
        
        # Decidir acción aleatoriamente (más humano)
        action = random.choices(
            ["like", "comment", "follow", "scroll"],
            weights=[0.3, 0.1, 0.1, 0.5]  # 50% scroll, 30% like, etc.
        )[0]
        
        if action == "like":
            await session.tap_element("like_button")
        elif action == "follow":  
            await session.tap_element("follow_button")
        elif action == "comment":
            await session.tap_element("comment_button")
            await session.type_text("Great content! 🔥")
            await session.tap_element("send_comment")
        
        # Siempre scroll al siguiente video
        await session.scroll_down(duration=2)
```

## 📈 Métricas y Monitoring

### KPIs Device Farm
- **Device Uptime**: % tiempo dispositivos disponibles (target: >95%)
- **Success Rate**: % acciones exitosas (target: >90%)
- **Response Time**: Tiempo promedio de respuesta (target: <3s)
- **Parallel Sessions**: Sesiones simultáneas activas (target: 5-10)

### Health Checks Automáticos
```python
# Health check periódico
async def device_farm_health_check():
    health_report = {
        "timestamp": datetime.now(),
        "devices": {},
        "overall_health": "healthy"
    }
    
    devices = await device_manager.get_available_devices()
    
    for device in devices:
        try:
            # Test conectividad
            session = await device_manager.connect_device(device['id'])
            
            # Test básico
            await session.get_device_status()
            
            health_report["devices"][device['id']] = {
                "status": "healthy",
                "last_seen": datetime.now(),
                "battery": device.get('battery_level', 'unknown')
            }
            
            await device_manager.disconnect_device(device['id'])
            
        except Exception as e:
            health_report["devices"][device['id']] = {
                "status": "unhealthy",
                "error": str(e),
                "last_seen": device.get('last_seen', 'never')
            }
            health_report["overall_health"] = "degraded"
    
    return health_report
```

### Monitoring Dashboards
1. **Device Status**: Estado en tiempo real de cada dispositivo
2. **Session Activity**: Actividad de automatización por dispositivo
3. **Error Tracking**: Errores de conexión y automatización
4. **Performance Metrics**: Tiempos de respuesta y throughput

## 💡 Buenas Prácticas

### 1. Gestión de Sesiones
```python
# Context manager para sesiones
from contextlib import asynccontextmanager

@asynccontextmanager
async def device_session(device_id):
    session = None
    try:
        session = await device_manager.connect_device(device_id)
        yield session
    finally:
        if session:
            await device_manager.disconnect_device(device_id)

# Uso
async with device_session("android_device_001") as session:
    await session.open_app("com.zhiliaoapp.musically")
    # Session se cierra automáticamente
```

### 2. Rate Limiting y Delays Naturales
```python
import random

# Delays más humanos
async def natural_delay(base_seconds=2):
    # Variación natural entre 0.5x y 2x el tiempo base
    delay = base_seconds * random.uniform(0.5, 2.0)
    await asyncio.sleep(delay)

# Rate limiting por dispositivo
class DeviceRateLimiter:
    def __init__(self):
        self.last_action = {}
        self.min_interval = 1.5  # Mínimo 1.5s entre acciones
    
    async def wait_if_needed(self, device_id):
        now = time.time()
        if device_id in self.last_action:
            elapsed = now - self.last_action[device_id]
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
        
        self.last_action[device_id] = time.time()

rate_limiter = DeviceRateLimiter()

# Usar antes de cada acción
await rate_limiter.wait_if_needed(device_id)
await session.tap_element("like_button")
```

### 3. Error Recovery
```python
# Recovery automático de errores
async def robust_automation_step(session, action_func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await action_func()
        
        except ElementNotFoundError:
            if attempt < max_retries - 1:
                # Esperar y reintentar
                await asyncio.sleep(2 ** attempt)  # Backoff exponencial
                continue
            raise
        
        except AppCrashError:
            # Reiniciar app
            await session.open_app("com.zhiliaoapp.musically")
            await asyncio.sleep(3)
            
            if attempt < max_retries - 1:
                continue
            raise
        
        except DeviceDisconnectedError:
            # Reconectar dispositivo
            await device_manager.reconnect_device(session.device_id)
            session = await device_manager.get_session(session.device_id)
            
            if attempt < max_retries - 1:
                continue
            raise
```

## 🚀 Activación del Sistema

### Checklist para Salir de Modo Dormant

- [ ] 🔧 Instalar ADB y configurar dispositivos Android
- [ ] 📱 Configurar dispositivos con USB debugging habilitado  
- [ ] 🚀 Instalar y configurar Appium server
- [ ] 📦 Instalar dependencias Python (`appium-python-client`, etc.)
- [ ] ⚙️ Configurar archivo `devices.yaml` con dispositivos reales
- [ ] 🔐 Configurar variables de entorno de producción
- [ ] 🧪 Ejecutar tests de conectividad con dispositivos reales
- [ ] 📊 Configurar monitoring de dispositivos

### Comando de Activación
```python
# Activar device farm
device_manager = create_device_manager(dummy_mode=False)

# Health check completo
health = await device_manager.system_health_check()
print(f"Device Farm Ready: {health['ready']}")
print(f"Devices available: {health['devices_count']}")
```

---

## 📞 Soporte

- **Device Issues**: Problemas de conectividad y configuración
- **Automation**: Optimización de scripts y patrones  
- **Performance**: Mejoras de velocidad y estabilidad
- **Scaling**: Añadir más dispositivos a la farm