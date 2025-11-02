# 🔒 GoLogin Automation System

Sistema completo de automatización de navegadores con anonimato avanzado usando GoLogin. Proporciona perfiles anónimos, anti-detección, patrones humanos y gestión inteligente de sesiones.

## 🌟 Características Principales

### 🎭 Anonimato Completo
- **Perfiles múltiples**: Gestión automática de hasta 30 perfiles anónimos
- **Rotación inteligente**: Cambio automático de perfiles basado en uso y detección
- **Fingerprinting avanzado**: WebRTC, Canvas, WebGL, Audio Context modificados
- **Proxies integrados**: Soporte completo para HTTP/SOCKS con rotación automática

### 🤖 Comportamiento Humano
- **Patrones naturales**: Delays, velocidad de escritura, movimientos de mouse
- **Scroll orgánico**: Simulación de lectura y navegación humana
- **Interacciones realistas**: Pausas, clicks graduales, comportamiento errático

### 🛡️ Anti-Detección
- **Stealth avanzado**: Ocultación de properties de automatización
- **Evasión automática**: Detección y respuesta a intentos de fingerprinting
- **Configuración dinámica**: Adaptación automática a cambios de detección

### 🔧 Integración Flexible
- **Dual Engine**: Soporte para Playwright y Selenium
- **API REST**: Endpoints completos para gestión remota
- **Modo Dummy**: Desarrollo sin dependencias externas
- **Factory Pattern**: Intercambio fácil entre implementaciones

## 🏗️ Arquitectura del Sistema

```
gologin_automation/
├── 📁 api/                     # API Client para GoLogin
│   └── api_client.py          # Cliente HTTP completo
├── 📁 browser/                # Automatización del navegador
│   ├── browser_automation.py  # Motor principal de automatización
│   └── selenium_wrapper.py    # Wrapper especializado Selenium
├── anonymity_context.py       # Contexto de anonimato
├── config.py                  # Sistema de configuración
└── README.md                  # Esta documentación
```

## 🚀 Inicio Rápido

### Instalación

```bash
# Dependencias básicas
pip install aiohttp requests

# Para Selenium (opcional)
pip install selenium

# Para Playwright (recomendado)
pip install playwright
playwright install chromium
```

### Uso Básico

```python
from gologin_automation import anonymous_context

# Crear contexto anónimo automático
async with anonymous_context() as ctx:
    # Obtener perfil anónimo
    profile = await ctx.get_anonymous_context()
    print(f"Perfil activo: {profile.profile_id} ({profile.country})")
    
    # Configuración del navegador
    browser_config = ctx.get_browser_config()
    print(f"User-Agent: {browser_config['user_agent']}")
```

### Automatización del Navegador

```python
from gologin_automation.browser import GoLoginBrowserAutomation

# Crear automatización completa
async with GoLoginBrowserAutomation(automation_engine="playwright") as browser:
    # Iniciar sesión anónima
    session = await browser.start_anonymous_session(country_preference="US")
    
    # Navegar con comportamiento humano
    await browser.navigate_to("https://example.com")
    
    # Interacciones naturales
    await browser.click_element("#login-button")
    await browser.type_text("#username", "usuario", human_like=True)
    await browser.scroll_page("down", amount=3)
    
    # Tomar captura
    screenshot = await browser.take_screenshot()
```

### Cliente API de GoLogin

```python
from gologin_automation.api_client import GoLoginAPIClient

async with GoLoginAPIClient(api_token="tu_token") as client:
    # Listar perfiles
    profiles = await client.list_profiles()
    
    # Crear nuevo perfil
    new_profile = await client.create_profile(profile_data)
    
    # Iniciar sesión de navegador
    session = await client.start_browser_session(profile.id)
    print(f"Navegador iniciado en puerto: {session.port}")
```

## 📋 Configuración

### Variables de Entorno

```bash
# API de GoLogin
GOLOGIN_API_TOKEN=tu_token_aqui

# Modo de operación
DUMMY_MODE=true          # false para producción
DEBUG=false
GOLOGIN_ENV=development  # staging, production

# Límites
MAX_PROFILES=30
MAX_CONCURRENT_SESSIONS=5
```

## 🎯 Casos de Uso

### 1. Automatización de Redes Sociales

```python
async def automate_social_media():
    async with GoLoginBrowserAutomation() as browser:
        # Sesión anónima para redes sociales
        await browser.start_anonymous_session(country_preference="US")
        
        # Login automático
        await browser.navigate_to("https://platform.com/login")
        await browser.type_text("#email", "user@example.com")
        await browser.type_text("#password", "password", human_like=True)
        await browser.click_element("#login-btn")
        
        # Comportamiento humano
        await browser.scroll_page("down", amount=5)
        await asyncio.sleep(random.uniform(2, 5))
        
        # Interacciones naturales
        await browser.click_element(".post-like")
        await browser.type_text(".comment-box", "¡Excelente post!")
```

### 2. Web Scraping Anónimo

```python
async def scrape_with_anonymity():
    async with anonymous_context(api_token="token") as ctx:
        # Rotar perfil automáticamente
        profile = await ctx.get_anonymous_context(force_new=True)
        
        # Múltiples requests con mismo perfil
        for url in urls_to_scrape:
            async with aiohttp.ClientSession() as session:
                # Usar configuración del perfil
                headers = {"User-Agent": profile.user_agent}
                proxy = f"{profile.proxy_type}://{profile.proxy_host}:{profile.proxy_port}"
                
                async with session.get(url, headers=headers, proxy=proxy) as response:
                    data = await response.text()
                    # Procesar datos...
                    
            # Pausa humana entre requests
            await asyncio.sleep(random.uniform(1, 3))
```

## 🔄 Modo Dummy vs Producción

### Modo Dummy (Desarrollo)
- ✅ Sin dependencias externas
- ✅ Respuestas simuladas instantáneas  
- ✅ Perfiles y proxies ficticios
- ✅ Ideal para desarrollo y testing

### Modo Producción
- 🔑 Requiere token API GoLogin válido
- 🌐 Conexión real a API GoLogin
- 🖥️ Navegadores reales con perfiles
- 📊 Métricas y estadísticas reales

### Cambiar de Modo

```bash
# Activar modo producción
export DUMMY_MODE=false
export GOLOGIN_API_TOKEN=tu_token_real

# Volver a modo dummy
export DUMMY_MODE=true
```

## 🧪 Testing

### Test Manual

```python
# Test rápido del sistema
from gologin_automation import anonymous_context

async def quick_test():
    async with anonymous_context() as ctx:
        profile = await ctx.get_anonymous_context()
        config = ctx.get_browser_config()
        stats = ctx.get_anonymity_stats()
        
        print(f"✅ Perfil: {profile.profile_id}")
        print(f"✅ País: {profile.country}")
        print(f"✅ Proxy: {profile.proxy_host}")
        print(f"✅ Stats: {stats}")

asyncio.run(quick_test())
```

## 🛠️ Troubleshooting

### Problemas Comunes

**Error: "Selenium/Playwright no disponible"**
```bash
pip install selenium playwright
playwright install chromium
```

**Error: "Token API inválido"**
```bash
export GOLOGIN_API_TOKEN=tu_token_correcto
```

## 📄 Licencia

Este proyecto está bajo licencia MIT.

---

<div align="center">

**🔒 GoLogin Automation System**  
*Automatización web anónima de próxima generación*

</div>
