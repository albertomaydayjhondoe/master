# 👤 Identity Management System

## 📋 Resumen Ejecutivo
- **Propósito**: Gestión centralizada de identidades, cuentas y perfiles para automatización social media
- **Estado**: 🟡 Durmiente - Gestores mock con rotación simulada
- **Complejidad**: Avanzado
- **Dependencias**: `cryptography`, `faker`, `pydantic`, `sqlalchemy`

## 🚀 Inicio Rápido

### 1. Gestión Básica de Identidades (Dummy Mode)
```python
from identity_management.core.identity_manager import IdentityManager

# Crear manager en modo dummy
identity_manager = IdentityManager(dummy_mode=True)

# Generar nueva identidad
new_identity = await identity_manager.create_identity()
print(f"Identity created: {new_identity.username}")
print(f"Profile: {new_identity.profile.full_name}")
print(f"Location: {new_identity.profile.location}")
```

### 2. Rotación de Cuentas
```python
import asyncio

async def test_account_rotation():
    # Obtener cuenta disponible
    account = await identity_manager.get_available_account("tiktok")
    print(f"Using account: {account.username}")
    
    # Marcar como en uso
    await identity_manager.mark_account_busy(account.id, duration_hours=2)
    
    # Simular actividad
    await asyncio.sleep(1)  # Simula trabajo
    
    # Liberar cuenta
    await identity_manager.release_account(account.id)
    print("Account released and ready for rotation")

asyncio.run(test_account_rotation())
```

### 3. Perfiles Auténticos
```python
# Generar perfil realista
profile = await identity_manager.generate_authentic_profile(
    age_range=(18, 30),
    location="United States",
    interests=["music", "fashion", "travel"]
)

print(f"Profile generated:")
print(f"  Name: {profile.full_name}")
print(f"  Age: {profile.age}")
print(f"  Bio: {profile.bio}")
print(f"  Interests: {', '.join(profile.interests)}")
print(f"  Avatar URL: {profile.avatar_url}")
```

## ⚙️ Configuración Detallada

### Instalación de Dependencias
```bash
# Dependencias de seguridad
pip install cryptography
pip install pycryptodome

# Generación de datos
pip install faker
pip install names
pip install random-username

# Validación y modelos
pip install pydantic
pip install email-validator

# Base de datos
pip install sqlalchemy
pip install alembic
```

### Variables de Entorno
```bash
# En .env
IDENTITY_MODE=dummy                    # dummy/production
ENCRYPTION_KEY=your-256-bit-key-here   # Para encriptar datos sensibles
IDENTITY_DB_URL=sqlite:///identities.db # Base de datos de identidades
MAX_ACCOUNTS_PER_PLATFORM=50          # Límite de cuentas por plataforma
ACCOUNT_ROTATION_INTERVAL=3600         # Rotación cada hora
PROFILE_AUTHENTICITY_LEVEL=high        # low/medium/high
GENERATE_REAL_AVATARS=false           # Generar avatares reales
```

### Configuración de Perfiles
```yaml
# config/identity_management/profile_config.yaml
profile_generation:
  demographics:
    age_ranges:
      - min: 16
        max: 25
        weight: 0.4  # 40% Gen Z
      - min: 26
        max: 35
        weight: 0.3  # 30% Millennials
      - min: 36
        max: 50
        weight: 0.3  # 30% Gen X+
    
  locations:
    primary_countries: ["US", "GB", "CA", "AU"]
    city_distribution: "realistic"  # realistic/random
    
  interests:
    categories:
      - entertainment: ["music", "movies", "gaming", "comedy"]
      - lifestyle: ["fashion", "fitness", "food", "travel"]
      - creative: ["art", "photography", "writing", "design"]
    max_per_profile: 5

platforms:
  tiktok:
    username_format: "{adjective}_{noun}{number}"
    bio_max_length: 150
    required_fields: ["username", "bio", "avatar"]
    
  instagram:
    username_format: "{firstname}.{lastname}{number}"
    bio_max_length: 150
    required_fields: ["username", "full_name", "bio", "avatar"]
```

## 📚 API Reference

### Core Classes

#### `IdentityManager`
Gestor principal del sistema de identidades.

```python
# Crear manager
identity_manager = IdentityManager(
    dummy_mode=True,
    encryption_enabled=True,
    auto_rotation=True
)

# Verificar inicialización
print(f"Manager ready: {identity_manager.is_initialized}")
print(f"Encryption active: {identity_manager.encryption_enabled}")
print(f"Total identities: {await identity_manager.count_identities()}")
```

#### `Identity`
Modelo de identidad completa.

```python
from identity_management.models.identity import Identity, Profile

@dataclass
class Identity:
    id: str
    username: str
    email: str
    password: str  # Encriptado
    profile: Profile
    platform_accounts: Dict[str, PlatformAccount]
    created_at: datetime
    last_used: datetime
    status: str  # active/suspended/banned
    metadata: Dict[str, Any]
```

#### `Profile`
Información del perfil de usuario.

```python
@dataclass  
class Profile:
    full_name: str
    first_name: str
    last_name: str
    age: int
    gender: str
    location: str
    country: str
    bio: str
    interests: List[str]
    avatar_url: str
    cover_url: str
    phone: str
    authenticity_score: float  # 0-1
```

### Methods Principales

#### `create_identity(platform: str = None) -> Identity`
Crea nueva identidad completa.

```python
# Crear identidad genérica
identity = await identity_manager.create_identity()

# Crear para plataforma específica
tiktok_identity = await identity_manager.create_identity(
    platform="tiktok",
    profile_config={
        "age_range": (16, 24),
        "interests": ["music", "dance", "comedy"],
        "location": "United States"
    }
)

print(f"TikTok identity: @{tiktok_identity.username}")
print(f"Bio: {tiktok_identity.profile.bio}")
```

#### `get_available_account(platform: str) -> PlatformAccount`
Obtiene cuenta disponible para uso.

```python
# Obtener cuenta TikTok disponible
account = await identity_manager.get_available_account("tiktok")

if account:
    print(f"Account available: @{account.username}")
    print(f"Status: {account.status}")
    print(f"Last used: {account.last_used}")
    
    # Marcar como en uso
    await identity_manager.mark_account_busy(account.id)
else:
    print("No accounts available, creating new one...")
    new_identity = await identity_manager.create_identity("tiktok")
    account = new_identity.platform_accounts["tiktok"]
```

#### `rotate_accounts(platform: str) -> List[PlatformAccount]`
Rotación automática de cuentas.

```python
# Rotar cuentas TikTok
rotated_accounts = await identity_manager.rotate_accounts("tiktok")

print(f"Rotated {len(rotated_accounts)} accounts")
for account in rotated_accounts:
    print(f"  @{account.username}: {account.status}")

# Rotación con criterios específicos
rotation_result = await identity_manager.rotate_accounts(
    platform="instagram", 
    criteria={
        "min_idle_hours": 6,        # Mínimo 6h sin uso
        "max_daily_actions": 100,   # Máximo 100 acciones/día
        "avoid_flagged": True       # Evitar cuentas flagged
    }
)
```

#### `generate_authentic_profile(**kwargs) -> Profile`
Genera perfil auténtico y coherente.

```python
# Perfil para target joven
young_profile = await identity_manager.generate_authentic_profile(
    age_range=(16, 22),
    interests=["music", "fashion", "social_media"],
    authenticity_level="high"
)

# Perfil profesional
professional_profile = await identity_manager.generate_authentic_profile(
    age_range=(25, 35),
    interests=["business", "technology", "productivity"],
    location="New York, NY",
    tone="professional"
)

# Perfil con personalidad específica
creative_profile = await identity_manager.generate_authentic_profile(
    personality_traits=["creative", "outgoing", "artistic"],
    bio_style="casual_creative",
    avatar_style="artistic"
)
```

### Account Management

#### `PlatformAccount`
Cuenta específica de una plataforma.

```python
@dataclass
class PlatformAccount:
    id: str
    platform: str
    username: str
    display_name: str
    bio: str
    avatar_url: str
    follower_count: int
    following_count: int
    posts_count: int
    status: str  # active/suspended/shadowbanned/banned
    created_at: datetime
    last_active: datetime
    daily_actions: int
    metadata: Dict[str, Any]
```

#### Account Status Management
```python
# Verificar estado de cuenta
status = await identity_manager.check_account_status(account_id)
print(f"Account status: {status.current_status}")
print(f"Risk level: {status.risk_level}")
print(f"Actions today: {status.daily_actions}")

# Actualizar estado manual
await identity_manager.update_account_status(
    account_id, 
    status="shadowbanned",
    reason="Engagement drop detected",
    cooldown_hours=24
)

# Recuperación automática
recovery_plan = await identity_manager.create_recovery_plan(account_id)
print(f"Recovery steps: {len(recovery_plan.steps)}")
for step in recovery_plan.steps:
    print(f"  - {step.action}: {step.description}")
```

### Security & Encryption

#### `encrypt_sensitive_data(data: str) -> str`
Encripta datos sensibles.

```python
# Encriptar password
encrypted_password = identity_manager.encrypt_sensitive_data("user_password123")

# Desencriptar cuando necesario
decrypted_password = identity_manager.decrypt_sensitive_data(encrypted_password)

# Verificar integridad
is_valid = identity_manager.verify_data_integrity(encrypted_password)
print(f"Data integrity: {'✅' if is_valid else '❌'}")
```

#### `generate_secure_credentials() -> Dict`
Genera credenciales seguras.

```python
# Generar credenciales completas
credentials = identity_manager.generate_secure_credentials()

print(f"Username: {credentials['username']}")
print(f"Email: {credentials['email']}")  
print(f"Password strength: {credentials['password_strength']}")
print(f"Recovery email: {credentials['recovery_email']}")

# Credenciales con requisitos específicos
custom_credentials = identity_manager.generate_secure_credentials(
    username_style="realistic",      # realistic/random/branded
    password_complexity="high",      # low/medium/high
    include_recovery=True,          # Generar email de recuperación
    domain_preference=["gmail.com", "yahoo.com"]
)
```

## 🔧 Troubleshooting

### Problemas de Generación

#### 1. **Perfiles poco auténticos**
```python
# Verificar configuración de autenticidad
config = identity_manager.get_authenticity_config()
print("Authenticity settings:")
import pprint
pprint.pprint(config)

# Ajustar nivel de autenticidad
identity_manager.set_authenticity_level("high")

# Generar con seed específico para consistencia
profile = await identity_manager.generate_authentic_profile(
    seed=12345,  # Para perfiles reproducibles
    authenticity_checks=True
)

# Validar autenticidad
score = identity_manager.calculate_authenticity_score(profile)
print(f"Authenticity score: {score:.2f}/1.0")
```

#### 2. **Usernames duplicados**
```python
# Verificar disponibilidad antes de crear
username = "test_user123"
is_available = await identity_manager.check_username_availability(
    username, 
    platform="tiktok"
)

if not is_available:
    # Generar alternativas
    alternatives = await identity_manager.generate_username_alternatives(
        base_username=username,
        count=5
    )
    print(f"Alternative usernames: {alternatives}")

# Crear con validación automática
identity = await identity_manager.create_identity(
    platform="tiktok",
    ensure_unique_username=True,
    max_retries=10
)
```

#### 3. **Datos encriptados corruptos**
```python
# Verificar integridad de datos encriptados
corrupt_identities = await identity_manager.check_data_integrity()

if corrupt_identities:
    print(f"Found {len(corrupt_identities)} corrupt identities")
    
    for identity_id in corrupt_identities:
        try:
            # Intentar recuperación
            await identity_manager.recover_identity(identity_id)
            print(f"✅ Recovered identity {identity_id}")
        except Exception as e:
            print(f"❌ Failed to recover {identity_id}: {e}")
            
            # Crear backup antes de eliminar
            await identity_manager.backup_identity(identity_id)
            await identity_manager.delete_identity(identity_id)
```

### Problemas de Rotación

#### 4. **Rotación muy frecuente**
```python
# Ajustar configuración de rotación
identity_manager.set_rotation_config({
    "min_idle_time": 3600,      # Mínimo 1 hora entre rotaciones
    "max_daily_rotations": 5,   # Máximo 5 rotaciones por día
    "cooldown_period": 1800     # 30 min cooldown después de rotación
})

# Verificar métricas de rotación
rotation_stats = await identity_manager.get_rotation_stats()
print(f"Rotations today: {rotation_stats['today_count']}")
print(f"Average interval: {rotation_stats['avg_interval']} minutes")
```

#### 5. **Cuentas no disponibles**
```python
# Diagnóstico de disponibilidad
availability_report = await identity_manager.get_availability_report("tiktok")

print(f"Total accounts: {availability_report['total']}")
print(f"Available: {availability_report['available']}")
print(f"Busy: {availability_report['busy']}")  
print(f"Suspended: {availability_report['suspended']}")
print(f"Banned: {availability_report['banned']}")

# Crear cuentas adicionales si es necesario
if availability_report['available'] < 3:
    print("Creating additional accounts...")
    for _ in range(5):
        new_identity = await identity_manager.create_identity("tiktok")
        print(f"Created account: @{new_identity.username}")
```

### Debug Mode
```python
# Activar logging detallado
import logging
logging.getLogger("identity_management").setLevel(logging.DEBUG)

# Debug de identidad específica
debug_info = await identity_manager.get_debug_info(identity_id)
print("Identity Debug Info:")
import pprint
pprint.pprint(debug_info)

# Test de funciones críticas
health_check = await identity_manager.run_health_check()
print(f"System health: {health_check}")
```

## 🔗 Integraciones

### Con Sistema de Monitoring
```python
# Monitorear uso de identidades
from social_extensions.telegram.monitoring import ActivityMetric

async def monitor_identity_usage(identity_id, action_type):
    start_time = time.time()
    
    try:
        # Ejecutar acción con identidad
        result = await execute_action_with_identity(identity_id, action_type)
        success = True
        
    except Exception as e:
        success = False
        result = {"error": str(e)}
    
    # Log actividad
    duration_ms = (time.time() - start_time) * 1000
    
    activity = ActivityMetric(
        timestamp=datetime.now(),
        type=f"identity_{action_type}",
        group_id=identity_id,
        success=success,
        duration_ms=duration_ms,
        metadata={
            "identity_id": identity_id,
            "action": action_type,
            "platform": result.get('platform'),
            "account_status": result.get('status')
        }
    )
    
    await monitor.log_activity(activity)

# Alertas de seguridad
async def setup_security_alerts():
    # Alerta por múltiples fallos de login
    await monitor.create_alert_rule({
        "name": "Multiple login failures",
        "condition": "identity_login failures > 3 in 1 hour",
        "action": "suspend_identity",
        "severity": "high"
    })
    
    # Alerta por detección de shadowban
    await monitor.create_alert_rule({
        "name": "Shadowban detected", 
        "condition": "engagement_drop > 70% in 24 hours",
        "action": "mark_shadowbanned",
        "severity": "medium"
    })
```

### Con Device Farm
```python
# Asignar identidades a dispositivos
async def assign_identity_to_device(device_id, platform):
    # Obtener cuenta disponible
    account = await identity_manager.get_available_account(platform)
    
    if not account:
        # Crear nueva identidad si no hay disponibles
        new_identity = await identity_manager.create_identity(platform)
        account = new_identity.platform_accounts[platform]
    
    # Asignar al dispositivo
    assignment = await device_manager.assign_account(device_id, account)
    
    # Log asignación
    await identity_manager.log_assignment(
        account.id,
        device_id,
        assignment_type="automation"
    )
    
    return assignment

# Rotación basada en actividad del dispositivo
async def smart_device_rotation():
    devices = await device_manager.get_active_devices()
    
    for device in devices:
        # Verificar tiempo de uso actual
        usage_time = await device_manager.get_current_usage_time(device.id)
        
        if usage_time > 3600:  # Más de 1 hora
            # Rotar identidad
            current_account = await device_manager.get_assigned_account(device.id)
            
            if current_account:
                # Liberar cuenta actual
                await identity_manager.release_account(current_account.id)
                
                # Asignar nueva cuenta
                await assign_identity_to_device(device.id, current_account.platform)
                
                print(f"Rotated account on device {device.id}")
```

### Con ML Integration
```python
# ML para optimizar perfiles
async def ml_optimized_profile_generation():
    from ml_integration.ultralytics_bridge import create_ml_bridge
    
    ml_bridge = create_ml_bridge()
    
    # Obtener tendencias actuales
    trending_elements = ml_bridge.get_trending_elements()
    
    # Generar perfil basado en tendencias
    trending_interests = [elem['element'] for elem in trending_elements 
                         if elem['category'] == 'interest'][:5]
    
    optimized_profile = await identity_manager.generate_authentic_profile(
        interests=trending_interests,
        bio_style="trendy",
        authenticity_level="high"
    )
    
    # Predicción de efectividad del perfil
    effectiveness_score = await ml_bridge.predict_profile_effectiveness(
        optimized_profile
    )
    
    print(f"Generated profile effectiveness: {effectiveness_score:.2f}")
    
    return optimized_profile

# Análisis de riesgo de identidades
async def ml_risk_assessment(identity_id):
    identity = await identity_manager.get_identity(identity_id)
    
    # Características para análisis de riesgo
    risk_features = {
        "account_age": (datetime.now() - identity.created_at).days,
        "daily_actions": identity.metadata.get('daily_actions', 0),
        "engagement_rate": identity.metadata.get('engagement_rate', 0),
        "follower_growth": identity.metadata.get('follower_growth', 0),
        "platform_diversity": len(identity.platform_accounts)
    }
    
    # Predicción de riesgo (dummy en modo dormant)
    if ml_bridge.dummy_mode:
        risk_score = random.uniform(0.1, 0.8)
    else:
        risk_score = await ml_bridge.predict_account_risk(risk_features)
    
    # Acciones basadas en riesgo
    if risk_score > 0.7:
        await identity_manager.apply_cooling_period(identity_id, hours=24)
    elif risk_score > 0.5:
        await identity_manager.reduce_activity_level(identity_id, factor=0.5)
    
    return risk_score
```

## 📈 Métricas y Monitoring

### KPIs Identity Management
- **Identity Success Rate**: % identidades que permanecen activas (target: >90%)
- **Account Rotation Efficiency**: Tiempo promedio entre rotaciones (target: 2-4h)
- **Authentication Success**: % logins exitosos (target: >95%)
- **Profile Authenticity**: Score promedio de autenticidad (target: >0.8)

### Identity Analytics
```python
# Analytics completos de identidades
async def generate_identity_analytics():
    analytics = {
        "overview": {
            "total_identities": await identity_manager.count_identities(),
            "active_accounts": await identity_manager.count_active_accounts(),
            "platforms_covered": await identity_manager.get_platform_coverage(),
            "daily_rotations": await identity_manager.get_daily_rotations()
        },
        
        "performance": {
            "avg_authenticity_score": await identity_manager.get_avg_authenticity(),
            "success_rate_by_platform": await identity_manager.get_platform_success_rates(),
            "risk_distribution": await identity_manager.get_risk_distribution(),
            "rotation_efficiency": await identity_manager.get_rotation_efficiency()
        },
        
        "security": {
            "encryption_status": identity_manager.encryption_enabled,
            "failed_logins_24h": await identity_manager.get_failed_logins(),
            "suspicious_activities": await identity_manager.get_suspicious_activities(),
            "data_integrity_score": await identity_manager.check_data_integrity_score()
        }
    }
    
    return analytics

# Reportes automáticos
async def daily_identity_report():
    analytics = await generate_identity_analytics()
    
    report = f"""
📊 Daily Identity Management Report - {datetime.now().strftime('%Y-%m-%d')}

🎯 Overview:
  • Total Identities: {analytics['overview']['total_identities']}
  • Active Accounts: {analytics['overview']['active_accounts']}  
  • Daily Rotations: {analytics['overview']['daily_rotations']}

📈 Performance:
  • Authenticity Score: {analytics['performance']['avg_authenticity_score']:.2f}
  • Success Rate: {analytics['performance'].get('overall_success_rate', 0):.1f}%
  • Rotation Efficiency: {analytics['performance']['rotation_efficiency']:.1f} min

🔒 Security:
  • Encryption: {'✅' if analytics['security']['encryption_status'] else '❌'}
  • Failed Logins: {analytics['security']['failed_logins_24h']}
  • Data Integrity: {analytics['security']['data_integrity_score']:.2f}
    """
    
    # Enviar reporte via monitoring
    await monitor.send_daily_report("identity_management", report)
```

### Alertas Automáticas
```python
# Sistema de alertas para identity management
class IdentityAlertSystem:
    def __init__(self, identity_manager, monitor):
        self.identity_manager = identity_manager
        self.monitor = monitor
    
    async def check_critical_alerts(self):
        """Verifica condiciones críticas"""
        alerts = []
        
        # Alerta: Pocas cuentas disponibles
        available_accounts = await self.identity_manager.count_available_accounts()
        if available_accounts < 5:
            alerts.append({
                "type": "low_account_availability",
                "severity": "high",
                "message": f"Only {available_accounts} accounts available",
                "action": "create_new_identities"
            })
        
        # Alerta: Múltiples cuentas baneadas
        banned_today = await self.identity_manager.count_banned_accounts(hours=24)
        if banned_today > 3:
            alerts.append({
                "type": "multiple_bans",
                "severity": "critical", 
                "message": f"{banned_today} accounts banned in 24h",
                "action": "review_automation_patterns"
            })
        
        # Alerta: Fallo de encriptación
        if not await self.identity_manager.verify_encryption_health():
            alerts.append({
                "type": "encryption_failure",
                "severity": "critical",
                "message": "Encryption system compromised",
                "action": "immediate_security_review"
            })
        
        # Enviar alertas
        for alert in alerts:
            await self.monitor.send_alert(alert)
        
        return alerts
```

## 💡 Buenas Prácticas

### 1. Seguridad de Identidades
```python
# Rotación segura de credentials
async def secure_credential_rotation():
    # Cambiar passwords periódicamente
    old_identities = await identity_manager.get_identities_older_than(days=90)
    
    for identity in old_identities:
        # Generar nuevo password
        new_password = identity_manager.generate_secure_password()
        
        # Actualizar en la plataforma (si es posible)
        for platform, account in identity.platform_accounts.items():
            try:
                success = await platform_manager.update_password(
                    platform, account.id, new_password
                )
                
                if success:
                    # Actualizar en DB encriptado
                    await identity_manager.update_password(
                        identity.id, new_password
                    )
                    
                    await identity_manager.log_security_event(
                        identity.id, "password_rotated"
                    )
                    
            except Exception as e:
                await identity_manager.log_security_event(
                    identity.id, "password_rotation_failed", str(e)
                )

# Backup de identidades críticas
async def backup_critical_identities():
    # Identidades con alta performance
    high_performers = await identity_manager.get_high_performing_identities()
    
    for identity in high_performers:
        # Crear backup encriptado
        backup_data = await identity_manager.create_encrypted_backup(identity.id)
        
        # Almacenar en múltiples ubicaciones
        await identity_manager.store_backup(backup_data, locations=[
            "local_encrypted",
            "secure_cloud",  
            "offline_storage"
        ])
```

### 2. Optimización de Performance
```python
# Cache de identidades activas
from functools import lru_cache
import asyncio

class IdentityCache:
    def __init__(self, max_size=100, ttl=3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
    
    async def get_identity(self, identity_id):
        now = time.time()
        
        if identity_id in self.cache:
            identity, timestamp = self.cache[identity_id]
            if now - timestamp < self.ttl:
                return identity
        
        # Cargar desde DB
        identity = await identity_manager.load_identity(identity_id)
        
        # Limpiar cache si está lleno
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        # Añadir a cache
        self.cache[identity_id] = (identity, now)
        return identity

# Pool de identidades precargadas
class IdentityPool:
    def __init__(self, pool_size=20):
        self.pool_size = pool_size
        self.pools = {
            "tiktok": asyncio.Queue(maxsize=pool_size),
            "instagram": asyncio.Queue(maxsize=pool_size),
            "youtube": asyncio.Queue(maxsize=pool_size)
        }
    
    async def initialize_pools(self):
        """Precarga pools con identidades"""
        for platform in self.pools:
            for _ in range(self.pool_size):
                identity = await identity_manager.create_identity(platform)
                await self.pools[platform].put(identity)
    
    async def get_identity(self, platform):
        """Obtiene identidad del pool"""
        try:
            # Obtener identidad disponible
            identity = await asyncio.wait_for(
                self.pools[platform].get(), 
                timeout=1.0
            )
            
            # Crear nueva identidad para reemplazar
            asyncio.create_task(self._refill_pool(platform))
            
            return identity
            
        except asyncio.TimeoutError:
            # Pool vacío, crear identidad directamente  
            return await identity_manager.create_identity(platform)
    
    async def _refill_pool(self, platform):
        """Rellena pool con nueva identidad"""
        new_identity = await identity_manager.create_identity(platform)
        
        try:
            await self.pools[platform].put_nowait(new_identity)
        except asyncio.QueueFull:
            # Pool ya está lleno, no hacer nada
            pass
```

### 3. Gestión de Riesgos
```python
# Sistema de scoring de riesgo
class RiskScorer:
    def __init__(self):
        self.risk_factors = {
            "account_age": {"weight": 0.2, "threshold": 30},      # días
            "daily_actions": {"weight": 0.3, "threshold": 50},    # acciones/día
            "ban_history": {"weight": 0.4, "threshold": 1},       # bans previos
            "engagement_drop": {"weight": 0.1, "threshold": 0.5}  # drop rate
        }
    
    async def calculate_risk_score(self, identity_id):
        identity = await identity_manager.get_identity(identity_id)
        risk_score = 0.0
        
        # Factor: Edad de cuenta (cuentas nuevas = mayor riesgo)
        account_age = (datetime.now() - identity.created_at).days
        age_risk = max(0, 1 - account_age / self.risk_factors["account_age"]["threshold"])
        risk_score += age_risk * self.risk_factors["account_age"]["weight"]
        
        # Factor: Acciones diarias (muchas acciones = mayor riesgo)
        daily_actions = identity.metadata.get("daily_actions", 0)
        actions_risk = min(1, daily_actions / self.risk_factors["daily_actions"]["threshold"])
        risk_score += actions_risk * self.risk_factors["daily_actions"]["weight"]
        
        # Factor: Historial de bans
        ban_count = identity.metadata.get("ban_count", 0)
        ban_risk = min(1, ban_count / self.risk_factors["ban_history"]["threshold"])
        risk_score += ban_risk * self.risk_factors["ban_history"]["weight"]
        
        # Factor: Caída de engagement
        engagement_drop = identity.metadata.get("engagement_drop", 0)
        drop_risk = min(1, engagement_drop / self.risk_factors["engagement_drop"]["threshold"])
        risk_score += drop_risk * self.risk_factors["engagement_drop"]["weight"]
        
        return min(1.0, risk_score)  # Normalizar a 0-1
    
    async def apply_risk_mitigation(self, identity_id, risk_score):
        """Aplica medidas de mitigación basadas en riesgo"""
        if risk_score > 0.8:
            # Riesgo muy alto - pausa completa
            await identity_manager.pause_identity(identity_id, hours=48)
            
        elif risk_score > 0.6:
            # Riesgo alto - reducir actividad
            await identity_manager.reduce_activity(identity_id, factor=0.3)
            
        elif risk_score > 0.4:
            # Riesgo medio - aumentar intervalos
            await identity_manager.increase_intervals(identity_id, factor=1.5)
        
        # Log decisión de mitigación
        await identity_manager.log_risk_mitigation(
            identity_id, risk_score, "automatic"
        )
```

## 🚀 Activación del Sistema

### Checklist para Salir de Modo Dormant

- [ ] 🔐 Configurar sistema de encriptación con claves seguras
- [ ] 🗄️ Configurar base de datos de producción con backups  
- [ ] 👤 Implementar generadores de perfiles auténticos
- [ ] 📱 Integrar con APIs reales de plataformas para validación
- [ ] 🔄 Configurar rotación automática con criterios de seguridad
- [ ] 📊 Implementar monitoring y alertas de seguridad
- [ ] 🧪 Ejecutar tests de autenticidad y seguridad
- [ ] 📋 Crear identidades iniciales para cada plataforma

### Comando de Activación
```python
# Activar identity management
identity_manager = IdentityManager(
    dummy_mode=False,
    encryption_enabled=True,
    auto_rotation=True
)

# Health check completo
health = await identity_manager.system_health_check()
print(f"Identity Management Ready: {health['ready']}")
print(f"Identities available: {health['identities_count']}")
print(f"Security status: {health['security_status']}")
```

---

## 📞 Soporte

- **Security Issues**: Problemas de encriptación y autenticación
- **Profile Generation**: Optimización de perfiles auténticos  
- **Account Management**: Gestión de rotación y disponibilidad
- **Integration**: Conexión con plataformas y otros sistemas