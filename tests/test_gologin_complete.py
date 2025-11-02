"""
Test Suite para GoLogin Automation System

Tests completos para validar todas las funcionalidades del sistema de anonimato GoLogin,
incluyendo contexto de anonimato, cliente API, automatización del navegador y configuración.
"""

import asyncio
import pytest
import time
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Importaciones del sistema GoLogin
from gologin_automation.anonymity_context import (
    GoLoginAnonymityContext, AnonymityProfile, AnonymityStats, anonymous_context
)
from gologin_automation.api_client import (
    GoLoginAPIClient, GoLoginProfile, BrowserSession
)
from gologin_automation.config import (
    GoLoginConfig, ConfigManager, get_gologin_config
)

class TestAnonymityProfile:
    """Tests para AnonymityProfile."""
    
    def test_profile_creation(self):
        """Test creación básica de perfil."""
        profile = AnonymityProfile(
            profile_id="test_123",
            name="Test Profile",
            country="US",
            city="New York",
            timezone="America/New_York",
            user_agent="Mozilla/5.0...",
            screen_resolution="1920x1080",
            language="en-US",
            proxy_type="http",
            proxy_host="proxy.example.com",
            proxy_port=8080
        )
        
        assert profile.profile_id == "test_123"
        assert profile.country == "US"
        assert profile.can_use() == True
        assert profile.is_expired() == False
    
    def test_profile_usage_tracking(self):
        """Test seguimiento de uso del perfil."""
        profile = AnonymityProfile(
            profile_id="test_usage",
            name="Usage Test",
            country="US",
            city="New York",
            timezone="America/New_York",
            user_agent="test",
            screen_resolution="1920x1080",
            language="en-US",
            proxy_type="http",
            proxy_host="test",
            proxy_port=8080,
            max_usage=2
        )
        
        # Usar perfil
        profile.mark_used()
        assert profile.usage_count == 1
        assert profile.can_use() == True
        
        # Usar hasta límite
        profile.mark_used()
        assert profile.usage_count == 2
        assert profile.is_expired() == True
        assert profile.can_use() == False
    
    def test_profile_serialization(self):
        """Test serialización de perfil."""
        profile = AnonymityProfile(
            profile_id="test_serial",
            name="Serial Test",
            country="GB",
            city="London",
            timezone="Europe/London",
            user_agent="test",
            screen_resolution="1366x768",
            language="en-GB",
            proxy_type="socks5",
            proxy_host="socks.example.com",
            proxy_port=1080
        )
        
        # Convertir a dict
        profile_dict = profile.to_dict()
        assert profile_dict['profile_id'] == "test_serial"
        assert profile_dict['country'] == "GB"
        
        # Recrear desde dict
        restored_profile = AnonymityProfile.from_dict(profile_dict)
        assert restored_profile.profile_id == profile.profile_id
        assert restored_profile.country == profile.country

class TestGoLoginAnonymityContext:
    """Tests para GoLoginAnonymityContext."""
    
    @pytest.fixture
    def temp_profiles_dir(self, tmp_path):
        """Directorio temporal para perfiles."""
        return str(tmp_path / "test_profiles")
    
    @pytest.mark.asyncio
    async def test_context_initialization(self, temp_profiles_dir):
        """Test inicialización del contexto."""
        ctx = GoLoginAnonymityContext(
            profiles_dir=temp_profiles_dir,
            max_profiles=5
        )
        
        await ctx.initialize()
        
        assert ctx.profiles_dir.exists()
        assert ctx.max_profiles == 5
        assert ctx.session is not None
        
        await ctx.cleanup()
    
    @pytest.mark.asyncio
    async def test_profile_creation(self, temp_profiles_dir):
        """Test creación de perfiles."""
        async with GoLoginAnonymityContext(profiles_dir=temp_profiles_dir) as ctx:
            # Crear perfil
            profile = await ctx.create_profile(country="DE")
            
            assert profile.country == "DE"
            assert profile.profile_id.startswith("anon_")
            assert profile.profile_id in ctx.profiles
            assert ctx.stats.profiles_created >= 1
    
    @pytest.mark.asyncio
    async def test_anonymous_context_manager(self, temp_profiles_dir):
        """Test context manager."""
        async with anonymous_context(profiles_dir=temp_profiles_dir) as ctx:
            profile = await ctx.get_anonymous_context()
            
            assert profile is not None
            assert isinstance(profile, AnonymityProfile)
            assert ctx.active_profile == profile
    
    @pytest.mark.asyncio
    async def test_profile_rotation(self, temp_profiles_dir):
        """Test rotación de perfiles."""
        async with GoLoginAnonymityContext(profiles_dir=temp_profiles_dir) as ctx:
            # Crear perfiles iniciales
            profile1 = await ctx.get_anonymous_context()
            
            # Rotar perfil
            profile2 = await ctx.rotate_profile()
            
            assert profile2.profile_id != profile1.profile_id
            assert ctx.active_profile == profile2
            assert ctx.stats.proxy_rotations >= 1
    
    def test_browser_config_generation(self, temp_profiles_dir):
        """Test generación de configuración del navegador."""
        ctx = GoLoginAnonymityContext(profiles_dir=temp_profiles_dir)
        
        # Crear perfil activo
        profile = AnonymityProfile(
            profile_id="test_config",
            name="Config Test",
            country="FR",
            city="Paris",
            timezone="Europe/Paris",
            user_agent="Mozilla/5.0 (Test)",
            screen_resolution="1440x900",
            language="fr-FR",
            proxy_type="http",
            proxy_host="french.proxy.com",
            proxy_port=8080,
            proxy_username="user",
            proxy_password="pass"
        )
        ctx.active_profile = profile
        
        config = ctx.get_browser_config()
        
        assert config['user_agent'] == "Mozilla/5.0 (Test)"
        assert config['viewport']['width'] == 1440
        assert config['viewport']['height'] == 900
        assert config['locale'] == "fr-FR"
        assert config['timezone_id'] == "Europe/Paris"
        assert config['proxy']['server'] == "http://french.proxy.com:8080"
    
    def test_anonymity_stats(self, temp_profiles_dir):
        """Test estadísticas de anonimato."""
        ctx = GoLoginAnonymityContext(profiles_dir=temp_profiles_dir)
        
        # Simular actividad
        ctx.stats.profiles_created = 5
        ctx.stats.sessions_started = 10
        ctx.stats.detection_events = 2
        ctx.stats.proxy_rotations = 3
        
        stats = ctx.get_anonymity_stats()
        
        assert stats['profiles_created'] == 5
        assert stats['sessions_started'] == 10
        assert stats['detection_events'] == 2
        assert stats['rotation_rate'] == 0.3  # 3/10
    
    def test_detection_handling(self, temp_profiles_dir):
        """Test manejo de detección."""
        ctx = GoLoginAnonymityContext(
            profiles_dir=temp_profiles_dir,
            auto_rotate=True
        )
        
        # Simular detección
        indicators = ["canvas_fingerprint", "webgl_fingerprint"]
        detected = ctx.detect_fingerprinting_attempt(indicators)
        
        assert detected == True
        assert ctx.stats.detection_events == 1

class TestGoLoginAPIClient:
    """Tests para GoLoginAPIClient."""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test inicialización del cliente."""
        client = GoLoginAPIClient(api_token="test_token")
        
        await client.initialize()
        
        assert client.session is not None
        assert client.api_token == "test_token"
        
        await client.cleanup()
    
    @pytest.mark.asyncio
    async def test_dummy_mode_responses(self):
        """Test respuestas en modo dummy."""
        async with GoLoginAPIClient(api_token="dummy") as client:
            # Test health check
            health = await client.health_check()
            assert health['status'] == 'healthy'
            assert health['dummy_mode'] == True
            
            # Test user info
            user_info = await client.get_user_info()
            assert 'id' in user_info
            assert user_info['email'] == 'test@example.com'
            
            # Test list profiles
            profiles = await client.list_profiles(limit=3)
            assert len(profiles) == 3
            assert all(isinstance(p, GoLoginProfile) for p in profiles)
    
    @pytest.mark.asyncio
    async def test_profile_management(self):
        """Test gestión de perfiles."""
        async with GoLoginAPIClient() as client:
            # Crear perfil
            test_profile = GoLoginProfile(
                id="",  # Se asignará automáticamente
                name="Test Profile API",
                country="CA",
                user_agent="Mozilla/5.0 (Test)"
            )
            
            created_profile = await client.create_profile(test_profile)
            assert created_profile.id.startswith("dummy_profile_")
            assert created_profile.name == "Test Profile API"
            
            # Obtener perfil
            retrieved_profile = await client.get_profile(created_profile.id)
            assert retrieved_profile.id == created_profile.id
    
    @pytest.mark.asyncio
    async def test_browser_session_management(self):
        """Test gestión de sesiones del navegador."""
        async with GoLoginAPIClient() as client:
            profile_id = "test_session_profile"
            
            # Iniciar sesión
            session = await client.start_browser_session(profile_id)
            assert isinstance(session, BrowserSession)
            assert session.profile_id == profile_id
            assert session.port == 3001
            assert session.status == "running"
            
            # Verificar sesión activa
            active_session = await client.get_session_status(profile_id)
            assert active_session == session
            
            # Listar sesiones activas
            active_sessions = await client.list_active_sessions()
            assert len(active_sessions) == 1
            assert active_sessions[0] == session
            
            # Detener sesión
            stopped = await client.stop_browser_session(profile_id)
            assert stopped == True
            
            # Verificar que se detuvo
            remaining_sessions = await client.list_active_sessions()
            assert len(remaining_sessions) == 0

class TestGoLoginConfig:
    """Tests para configuración."""
    
    def test_default_config_creation(self):
        """Test creación de configuración por defecto."""
        config = GoLoginConfig()
        
        assert config.dummy_mode == True  # Por defecto desde env
        assert config.max_profiles == 30
        assert config.automation_engine == "playwright"
        assert config.proxy.enabled == True
        assert config.fingerprint.webrtc_mode == "altered"
    
    def test_config_validation(self):
        """Test validación de configuración."""
        # Configuración válida
        valid_config = GoLoginConfig(
            dummy_mode=True,
            max_profiles=10,
            automation_engine="playwright"
        )
        
        errors = valid_config.validate()
        assert len(errors) == 0
        
        # Configuración inválida
        invalid_config = GoLoginConfig(
            max_profiles=0,  # Inválido
            automation_engine="invalid_engine"  # Inválido
        )
        
        errors = invalid_config.validate()
        assert len(errors) >= 2
        assert any("max_profiles" in error for error in errors)
        assert any("automation_engine" in error for error in errors)
    
    def test_browser_args_generation(self):
        """Test generación de argumentos del navegador."""
        config = GoLoginConfig(
            headless_mode=True,
            browser=GoLoginConfig().browser  # Usar defaults
        )
        
        args = config.get_browser_args()
        
        assert "--headless" in args
        assert "--no-first-run" in args
        assert "--disable-dev-shm-usage" in args
    
    def test_proxy_url_generation(self):
        """Test generación de URL de proxy."""
        config = GoLoginConfig()
        config.proxy.enabled = True
        config.proxy.host = "proxy.example.com"
        config.proxy.port = 8080
        config.proxy.username = "user"
        config.proxy.password = "pass"
        
        proxy_url = config.get_proxy_url()
        assert proxy_url == "http://user:pass@proxy.example.com:8080"
        
        # Sin autenticación
        config.proxy.username = None
        config.proxy.password = None
        proxy_url = config.get_proxy_url()
        assert proxy_url == "http://proxy.example.com:8080"
        
        # Proxy deshabilitado
        config.proxy.enabled = False
        proxy_url = config.get_proxy_url()
        assert proxy_url is None
    
    def test_config_file_operations(self, tmp_path):
        """Test operaciones con archivos de configuración."""
        config_file = tmp_path / "test_config.json"
        
        # Crear configuración
        original_config = GoLoginConfig(
            api_token="test_token",
            max_profiles=15,
            dummy_mode=False
        )
        
        # Guardar a archivo
        original_config.save_to_file(config_file)
        assert config_file.exists()
        
        # Cargar desde archivo
        loaded_config = GoLoginConfig.from_file(config_file)
        assert loaded_config.api_token == "test_token"
        assert loaded_config.max_profiles == 15
        assert loaded_config.dummy_mode == False
    
    def test_config_manager(self, tmp_path):
        """Test gestor de configuración."""
        manager = ConfigManager(config_dir=str(tmp_path))
        
        # Crear configuraciones default
        manager.create_default_configs()
        
        # Verificar archivos creados
        dev_config_file = tmp_path / "gologin_dev.yaml"
        prod_config_file = tmp_path / "gologin_prod.yaml"
        
        assert dev_config_file.exists()
        assert prod_config_file.exists()
        
        # Cargar configuración de desarrollo
        dev_config = manager.get_config("development")
        assert dev_config.dummy_mode == True
        assert dev_config.debug_mode == True
        
        # Template de perfil
        template = manager.get_profile_template("high_anonymity")
        assert template["webRTC"]["mode"] == "disabled"
        assert template["canvas"]["mode"] == "block"

class TestIntegration:
    """Tests de integración completa."""
    
    @pytest.mark.asyncio
    async def test_full_anonymity_workflow(self, tmp_path):
        """Test flujo completo de anonimato."""
        profiles_dir = str(tmp_path / "integration_profiles")
        
        # Crear contexto completo
        async with anonymous_context(profiles_dir=profiles_dir) as ctx:
            # Obtener perfil anónimo
            profile = await ctx.get_anonymous_context(country_preference="JP")
            
            assert profile.country == "JP"
            assert profile.profile_id is not None
            
            # Obtener configuración del navegador
            browser_config = ctx.get_browser_config()
            
            assert browser_config['user_agent'] is not None
            assert browser_config['locale'] == "ja-JP"
            assert browser_config['timezone_id'] == "Asia/Tokyo"
            
            # Rotar perfil
            new_profile = await ctx.rotate_profile()
            assert new_profile.profile_id != profile.profile_id
            
            # Verificar estadísticas
            stats = ctx.get_anonymity_stats()
            assert stats['profiles_created'] >= 2
            assert stats['sessions_started'] >= 1
            assert stats['proxy_rotations'] >= 1
    
    @pytest.mark.asyncio
    async def test_api_client_integration(self):
        """Test integración del cliente API."""
        async with GoLoginAPIClient() as client:
            # Health check
            health = await client.health_check()
            assert health['status'] == 'healthy'
            
            # Gestión de perfiles
            profiles = await client.list_profiles(limit=2)
            assert len(profiles) <= 2
            
            if profiles:
                profile = profiles[0]
                
                # Gestión de sesiones
                session = await client.start_browser_session(profile.id)
                assert session.profile_id == profile.id
                
                # Información de proxy
                proxy_info = await client.get_proxy_info(profile.id)
                assert 'enabled' in proxy_info
                assert 'host' in proxy_info
                
                # Detener sesión
                stopped = await client.stop_browser_session(profile.id)
                assert stopped == True
    
    def test_performance_metrics(self, tmp_path):
        """Test métricas de rendimiento."""
        profiles_dir = str(tmp_path / "perf_profiles")
        
        # Medir tiempo de inicialización
        start_time = time.time()
        
        ctx = GoLoginAnonymityContext(profiles_dir=profiles_dir)
        
        init_time = time.time() - start_time
        
        # Debería ser rápido (< 1 segundo en modo dummy)
        assert init_time < 1.0
        
        # Verificar uso de memoria básico
        import sys
        initial_size = sys.getsizeof(ctx)
        assert initial_size > 0

class TestErrorHandling:
    """Tests para manejo de errores."""
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test manejo de errores de API."""
        # Cliente con configuración inválida
        client = GoLoginAPIClient(
            api_token="invalid_token",
            base_url="https://invalid.url"
        )
        
        # En modo dummy, no debería fallar
        async with client:
            health = await client.health_check()
            assert health['dummy_mode'] == True
    
    def test_config_error_handling(self, tmp_path):
        """Test manejo de errores de configuración."""
        # Archivo inexistente
        nonexistent_file = tmp_path / "nonexistent.json"
        config = GoLoginConfig.from_file(nonexistent_file)
        
        # Debería crear configuración por defecto
        assert isinstance(config, GoLoginConfig)
        assert config.dummy_mode == True
        
        # Archivo corrupto
        corrupt_file = tmp_path / "corrupt.json"
        corrupt_file.write_text("invalid json content")
        
        config = GoLoginConfig.from_file(corrupt_file)
        assert isinstance(config, GoLoginConfig)
    
    @pytest.mark.asyncio
    async def test_profile_persistence_errors(self, tmp_path):
        """Test errores de persistencia de perfiles."""
        # Directorio sin permisos (simulado)
        profiles_dir = str(tmp_path / "restricted_profiles")
        
        ctx = GoLoginAnonymityContext(profiles_dir=profiles_dir)
        
        # Debería manejar errores graciosamente
        await ctx.initialize()
        profile = await ctx.create_profile()
        
        assert profile is not None
        await ctx.cleanup()


# Funciones de utilidad para tests

def create_test_profile(profile_id: str = "test", country: str = "US") -> AnonymityProfile:
    """Crear perfil de prueba."""
    return AnonymityProfile(
        profile_id=profile_id,
        name=f"Test Profile {profile_id}",
        country=country,
        city="Test City",
        timezone="America/New_York",
        user_agent="Mozilla/5.0 (Test)",
        screen_resolution="1920x1080",
        language="en-US",
        proxy_type="http",
        proxy_host="test.proxy.com",
        proxy_port=8080
    )

def assert_valid_profile(profile: AnonymityProfile):
    """Validar que un perfil sea válido."""
    assert profile.profile_id is not None
    assert len(profile.profile_id) > 0
    assert profile.country is not None
    assert profile.user_agent is not None
    assert profile.screen_resolution is not None
    assert profile.proxy_host is not None
    assert profile.proxy_port > 0

def assert_valid_browser_config(config: dict):
    """Validar configuración del navegador."""
    required_keys = ['user_agent', 'viewport', 'locale', 'timezone_id']
    for key in required_keys:
        assert key in config
        assert config[key] is not None


if __name__ == "__main__":
    # Ejecutar tests básicos
    import sys
    
    print("🧪 Ejecutando tests básicos del sistema GoLogin...")
    
    # Test 1: Creación de perfil
    try:
        profile = create_test_profile("basic_test", "DE")
        assert_valid_profile(profile)
        print("✅ Test 1: Creación de perfil - PASADO")
    except Exception as e:
        print(f"❌ Test 1: Creación de perfil - FALLIDO: {e}")
    
    # Test 2: Configuración
    try:
        config = GoLoginConfig()
        errors = config.validate()
        assert len(errors) == 0, f"Errores de validación: {errors}"
        print("✅ Test 2: Configuración - PASADO")
    except Exception as e:
        print(f"❌ Test 2: Configuración - FALLIDO: {e}")
    
    # Test 3: Context manager (async)
    async def test_async():
        try:
            async with anonymous_context() as ctx:
                profile = await ctx.get_anonymous_context()
                assert_valid_profile(profile)
                
                browser_config = ctx.get_browser_config()
                assert_valid_browser_config(browser_config)
                
                stats = ctx.get_anonymity_stats()
                assert isinstance(stats, dict)
                
            print("✅ Test 3: Context manager - PASADO")
        except Exception as e:
            print(f"❌ Test 3: Context manager - FALLIDO: {e}")
    
    asyncio.run(test_async())
    
    # Test 4: Cliente API (async)
    async def test_api_client():
        try:
            async with GoLoginAPIClient() as client:
                health = await client.health_check()
                assert health['status'] == 'healthy'
                
                profiles = await client.list_profiles(limit=2)
                assert isinstance(profiles, list)
                
            print("✅ Test 4: Cliente API - PASADO")
        except Exception as e:
            print(f"❌ Test 4: Cliente API - FALLIDO: {e}")
    
    asyncio.run(test_api_client())
    
    print("\n🎉 Tests básicos completados!")
    print("\nPara ejecutar tests completos:")
    print("pip install pytest pytest-asyncio")
    print("python -m pytest test_gologin_complete.py -v")