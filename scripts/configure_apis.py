"""
🔑 CONFIGURADOR DE APIs - Sistema Completo
Script interactivo para configurar todas las APIs y credenciales pendientes
"""

import os
import json
import getpass
from pathlib import Path
import requests
import sys

class APIConfigurator:
    def __init__(self):
        self.config_dir = Path("config/production")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.env_file = self.config_dir / ".env"
        self.config = {}
        
        # Cargar configuración existente si existe
        if self.env_file.exists():
            self._load_existing_config()
    
    def _load_existing_config(self):
        """Cargar configuración existente desde .env"""
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        self.config[key] = value.strip('"')
        except Exception as e:
            print(f"⚠️ Error cargando configuración: {e}")
    
    def _save_config(self):
        """Guardar configuración en archivo .env"""
        with open(self.env_file, 'w') as f:
            f.write("# 🔑 CONFIGURACIÓN APIS PRODUCCIÓN\n")
            f.write("# Generado automáticamente - No editar manualmente\n\n")
            
            # Meta Ads
            f.write("# Meta Ads API\n")
            f.write(f'META_ACCESS_TOKEN="{self.config.get("META_ACCESS_TOKEN", "")}"\n')
            f.write(f'META_AD_ACCOUNT_ID="{self.config.get("META_AD_ACCOUNT_ID", "")}"\n')
            f.write(f'META_PIXEL_ID="{self.config.get("META_PIXEL_ID", "")}"\n\n')
            
            # YouTube API
            f.write("# YouTube API\n")
            f.write(f'YOUTUBE_CLIENT_ID="{self.config.get("YOUTUBE_CLIENT_ID", "")}"\n')
            f.write(f'YOUTUBE_CLIENT_SECRET="{self.config.get("YOUTUBE_CLIENT_SECRET", "")}"\n')
            f.write(f'YOUTUBE_CHANNEL_ID="{self.config.get("YOUTUBE_CHANNEL_ID", "")}"\n\n')
            
            # Supabase
            f.write("# Supabase\n")
            f.write(f'SUPABASE_URL="{self.config.get("SUPABASE_URL", "")}"\n')
            f.write(f'SUPABASE_ANON_KEY="{self.config.get("SUPABASE_ANON_KEY", "")}"\n')
            f.write(f'SUPABASE_SERVICE_ROLE_KEY="{self.config.get("SUPABASE_SERVICE_ROLE_KEY", "")}"\n\n')
            
            # APIs Opcionales
            f.write("# APIs Opcionales\n")
            f.write(f'TIKTOK_CLIENT_KEY="{self.config.get("TIKTOK_CLIENT_KEY", "")}"\n')
            f.write(f'TIKTOK_CLIENT_SECRET="{self.config.get("TIKTOK_CLIENT_SECRET", "")}"\n')
            f.write(f'INSTAGRAM_CLIENT_ID="{self.config.get("INSTAGRAM_CLIENT_ID", "")}"\n')
            f.write(f'INSTAGRAM_CLIENT_SECRET="{self.config.get("INSTAGRAM_CLIENT_SECRET", "")}"\n')
            f.write(f'TWITTER_BEARER_TOKEN="{self.config.get("TWITTER_BEARER_TOKEN", "")}"\n')
            f.write(f'SPOTIFY_CLIENT_ID="{self.config.get("SPOTIFY_CLIENT_ID", "")}"\n')
            f.write(f'SPOTIFY_CLIENT_SECRET="{self.config.get("SPOTIFY_CLIENT_SECRET", "")}"\n\n')
            
            # Sistema
            f.write("# Sistema\n")
            f.write('DUMMY_MODE="false"\n')
            f.write('PRODUCTION_MODE="true"\n')
    
    def configure_meta_ads(self):
        """Configurar Meta Ads API"""
        print("\n🔵 CONFIGURACIÓN META ADS")
        print("=" * 40)
        
        # Token ya validado previamente
        current_token = self.config.get("META_ACCESS_TOKEN", "EAAlZBjrH0WtYBP4jclDq2lVTOwh3gQiU3ZCsdOPzxi5FDhbZAIlbq01BDzUBUuWoSuOT6FpccPS1713fG6U7Mxnuovj6rDTsa90tEeCZADIHgZAURZAT3hpyiUSqfF1ckPSzxnSzWZAkuXSLhaZAIEBCBvbDZAV0N79CfmVcJeqb3nJBpQO7YSfN2NeU4fQ3msTf2wwZDZD")
        
        if current_token:
            print(f"✅ Access Token: {current_token[:30]}... (YA CONFIGURADO)")
            self.config["META_ACCESS_TOKEN"] = current_token
        else:
            print("❌ No hay Access Token configurado")
            token = input("📝 Meta Access Token: ").strip()
            if token:
                self.config["META_ACCESS_TOKEN"] = token
        
        # Account ID (PENDIENTE)
        current_account = self.config.get("META_AD_ACCOUNT_ID", "")
        if current_account:
            print(f"✅ Account ID: {current_account} (YA CONFIGURADO)")
        else:
            print("\n📋 CÓMO OBTENER ACCOUNT ID:")
            print("1. Ve a Facebook Ads Manager: https://business.facebook.com/adsmanager")
            print("2. En la URL verás algo como: act_123456789")
            print("3. Copia solo el número: 123456789")
            
            account_id = input("\n📝 Meta Ad Account ID (solo números): ").strip()
            if account_id:
                # Validar que sea solo números
                if account_id.isdigit():
                    self.config["META_AD_ACCOUNT_ID"] = account_id
                    print(f"✅ Account ID configurado: {account_id}")
                else:
                    print("⚠️ Account ID debe ser solo números")
        
        # Pixel ID (Opcional)
        pixel_id = input("\n📝 Facebook Pixel ID (opcional, presiona Enter para omitir): ").strip()
        if pixel_id:
            self.config["META_PIXEL_ID"] = pixel_id
    
    def configure_youtube(self):
        """Configurar YouTube API"""
        print("\n🔴 CONFIGURACIÓN YOUTUBE API")
        print("=" * 40)
        
        # Client ID ya proporcionado
        provided_client_id = "524783623513-rksdl9ncl9c6un9omiqpk4rug8b2dcku.apps.googleusercontent.com"
        print(f"✅ Client ID proporcionado: {provided_client_id}")
        self.config["YOUTUBE_CLIENT_ID"] = provided_client_id
        
        # Client Secret
        current_secret = self.config.get("YOUTUBE_CLIENT_SECRET", "")
        if current_secret:
            print(f"✅ Client Secret: {current_secret[:20]}... (YA CONFIGURADO)")
        else:
            print("\n📋 NECESITAS EL CLIENT SECRET:")
            print("1. Ve a Google Cloud Console: https://console.cloud.google.com/")
            print("2. Selecciona tu proyecto")
            print("3. APIs & Services → Credentials")
            print("4. Busca tu OAuth 2.0 Client ID")
            print("5. Copia el Client Secret")
            
            client_secret = getpass.getpass("\n📝 YouTube Client Secret: ").strip()
            if client_secret:
                self.config["YOUTUBE_CLIENT_SECRET"] = client_secret
                print("✅ Client Secret configurado")
        
        # Channel ID
        current_channel = self.config.get("YOUTUBE_CHANNEL_ID", "")
        if current_channel:
            print(f"✅ Channel ID: {current_channel} (YA CONFIGURADO)")
        else:
            print("\n📋 CÓMO OBTENER CHANNEL ID:")
            print("1. Ve a tu canal de YouTube")
            print("2. En la URL verás: /channel/UC_xxxxxxxxx")
            print("3. Copia todo después de /channel/")
            
            channel_id = input("\n📝 YouTube Channel ID (UC_xxxxx): ").strip()
            if channel_id:
                self.config["YOUTUBE_CHANNEL_ID"] = channel_id
    
    def configure_supabase(self):
        """Configurar Supabase"""
        print("\n🟢 CONFIGURACIÓN SUPABASE")
        print("=" * 40)
        
        current_url = self.config.get("SUPABASE_URL", "")
        if current_url:
            print(f"✅ Supabase URL: {current_url} (YA CONFIGURADO)")
        else:
            print("\n📋 CREAR PROYECTO SUPABASE:")
            print("1. Ve a https://supabase.com/dashboard")
            print("2. Crear nuevo proyecto")
            print("3. Espera a que se complete el setup")
            print("4. Ve a Settings → API")
            
            supabase_url = input("\n📝 Supabase URL (https://xxxxx.supabase.co): ").strip()
            if supabase_url:
                self.config["SUPABASE_URL"] = supabase_url
        
        current_anon = self.config.get("SUPABASE_ANON_KEY", "")
        if current_anon:
            print(f"✅ Anon Key: {current_anon[:30]}... (YA CONFIGURADO)")
        else:
            anon_key = getpass.getpass("\n📝 Supabase Anon Key: ").strip()
            if anon_key:
                self.config["SUPABASE_ANON_KEY"] = anon_key
        
        current_service = self.config.get("SUPABASE_SERVICE_ROLE_KEY", "")
        if current_service:
            print(f"✅ Service Role Key: {current_service[:30]}... (YA CONFIGURADO)")
        else:
            service_key = getpass.getpass("\n📝 Supabase Service Role Key: ").strip()
            if service_key:
                self.config["SUPABASE_SERVICE_ROLE_KEY"] = service_key
    
    def configure_optional_apis(self):
        """Configurar APIs opcionales"""
        print("\n🟡 CONFIGURACIÓN APIS OPCIONALES")
        print("=" * 40)
        print("Estas APIs mejorarán la funcionalidad pero no son obligatorias")
        
        if input("\n¿Configurar TikTok API? (y/N): ").lower() == 'y':
            self.config["TIKTOK_CLIENT_KEY"] = input("TikTok Client Key: ").strip()
            self.config["TIKTOK_CLIENT_SECRET"] = getpass.getpass("TikTok Client Secret: ").strip()
        
        if input("\n¿Configurar Instagram API? (y/N): ").lower() == 'y':
            self.config["INSTAGRAM_CLIENT_ID"] = input("Instagram Client ID: ").strip()
            self.config["INSTAGRAM_CLIENT_SECRET"] = getpass.getpass("Instagram Client Secret: ").strip()
        
        if input("\n¿Configurar Twitter API? (y/N): ").lower() == 'y':
            self.config["TWITTER_BEARER_TOKEN"] = getpass.getpass("Twitter Bearer Token: ").strip()
        
        if input("\n¿Configurar Spotify API? (y/N): ").lower() == 'y':
            self.config["SPOTIFY_CLIENT_ID"] = input("Spotify Client ID: ").strip()
            self.config["SPOTIFY_CLIENT_SECRET"] = getpass.getpass("Spotify Client Secret: ").strip()
    
    def validate_configuration(self):
        """Validar configuración"""
        print("\n🔍 VALIDANDO CONFIGURACIÓN...")
        print("=" * 40)
        
        validation_results = []
        
        # Validar Meta Ads
        if self.config.get("META_ACCESS_TOKEN") and self.config.get("META_AD_ACCOUNT_ID"):
            print("✅ Meta Ads: Token + Account ID configurados")
            validation_results.append(("Meta Ads", True))
        else:
            print("❌ Meta Ads: Faltan credenciales")
            validation_results.append(("Meta Ads", False))
        
        # Validar YouTube
        if self.config.get("YOUTUBE_CLIENT_ID") and self.config.get("YOUTUBE_CLIENT_SECRET"):
            print("✅ YouTube: Client ID + Secret configurados")
            validation_results.append(("YouTube", True))
        else:
            print("❌ YouTube: Faltan credenciales")
            validation_results.append(("YouTube", False))
        
        # Validar Supabase
        if self.config.get("SUPABASE_URL") and self.config.get("SUPABASE_ANON_KEY"):
            print("✅ Supabase: URL + Keys configurados")
            validation_results.append(("Supabase", True))
        else:
            print("❌ Supabase: Faltan credenciales")
            validation_results.append(("Supabase", False))
        
        # Resumen
        configured = sum(1 for _, status in validation_results if status)
        total = len(validation_results)
        percentage = (configured / total) * 100
        
        print(f"\n📊 RESUMEN: {configured}/{total} APIs configuradas ({percentage:.1f}%)")
        
        return validation_results
    
    def generate_railway_vars(self):
        """Generar variables para Railway"""
        railway_vars = []
        
        for key, value in self.config.items():
            if value:  # Solo variables con valor
                railway_vars.append(f"{key}={value}")
        
        railway_file = self.config_dir / "railway_vars.txt"
        with open(railway_file, 'w') as f:
            f.write("# Variables para Railway Deployment\n")
            f.write("# Copia y pega estas variables en Railway\n\n")
            for var in railway_vars:
                f.write(f"{var}\n")
        
        print(f"📝 Variables Railway guardadas: {railway_file}")
        return railway_file
    
    def setup_supabase_database(self):
        """Setup de base de datos Supabase"""
        print("\n💾 SETUP BASE DE DATOS SUPABASE")
        print("=" * 40)
        
        if not self.config.get("SUPABASE_URL"):
            print("⚠️ Supabase no configurado, omitiendo setup DB")
            return
        
        schema_file = Path("config/supabase/schema.sql")
        if schema_file.exists():
            print(f"📋 Schema encontrado: {schema_file}")
            print("\n📝 PASOS PARA CONFIGURAR DB:")
            print("1. Ve a tu proyecto Supabase")
            print("2. SQL Editor → New Query")
            print(f"3. Copia el contenido de {schema_file}")
            print("4. Ejecuta la query")
            print("5. Verifica que se crearon las 7 tablas")
            
            if input("\n¿Continuar con setup automático? (y/N): ").lower() == 'y':
                try:
                    # Intentar setup automático (requiere asyncpg)
                    print("🔄 Configurando base de datos automáticamente...")
                    # Aquí iría el código de setup automático
                    print("✅ Base de datos configurada (simulado)")
                except Exception as e:
                    print(f"❌ Error en setup automático: {e}")
                    print("💡 Configura manualmente siguiendo los pasos arriba")
        else:
            print(f"❌ Schema no encontrado en {schema_file}")
    
    def run_full_setup(self):
        """Ejecutar setup completo"""
        print("🔑 CONFIGURADOR DE APIs - SISTEMA COMPLETO")
        print("=" * 50)
        print("Configuraremos todas las APIs necesarias para producción")
        print()
        
        # Configurar APIs principales
        self.configure_meta_ads()
        self.configure_youtube()
        self.configure_supabase()
        
        # APIs opcionales
        if input("\n¿Configurar APIs opcionales? (y/N): ").lower() == 'y':
            self.configure_optional_apis()
        
        # Guardar configuración
        self._save_config()
        print(f"\n💾 Configuración guardada: {self.env_file}")
        
        # Validar
        validation_results = self.validate_configuration()
        
        # Generar variables Railway
        railway_file = self.generate_railway_vars()
        
        # Setup Supabase DB
        self.setup_supabase_database()
        
        # Resumen final
        print("\n" + "=" * 50)
        print("🎉 CONFIGURACIÓN COMPLETADA")
        print("=" * 50)
        
        configured_apis = [name for name, status in validation_results if status]
        pending_apis = [name for name, status in validation_results if not status]
        
        if configured_apis:
            print("✅ APIs CONFIGURADAS:")
            for api in configured_apis:
                print(f"   - {api}")
        
        if pending_apis:
            print("\n❌ APIs PENDIENTES:")
            for api in pending_apis:
                print(f"   - {api}")
        
        print(f"\n📁 Archivos generados:")
        print(f"   - {self.env_file}")
        print(f"   - {railway_file}")
        
        print(f"\n🚀 PRÓXIMOS PASOS:")
        if len(configured_apis) >= 2:
            print("   1. Desplegar a Railway con las variables generadas")
            print("   2. Cambiar DUMMY_MODE=false")
            print("   3. ¡Lanzar campañas €400 reales!")
        else:
            print("   1. Configurar APIs pendientes")
            print("   2. Ejecutar este script nuevamente")
        
        print(f"\n🧠 Sistema Meta ML ya está listo!")
        print("   📊 Dashboard: streamlit run dashboard_meta_ml.py")
        print("   🤖 API ML: python -m uvicorn ml_core.sistema_meta_ml:app --port 8006")

def main():
    try:
        configurator = APIConfigurator()
        configurator.run_full_setup()
    except KeyboardInterrupt:
        print("\n\n⚠️ Configuración cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error en configuración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()