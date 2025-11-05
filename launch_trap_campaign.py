#!/usr/bin/env python3
"""
🎵 TRAP ARTIST CAMPAIGN LAUNCHER - CLEAN VERSION
===============================================
Launcher específico y limpio para el artista trap que paga
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv

# Cargar configuración específica del artista trap
load_dotenv('/workspaces/master/config/trap_artist_config.env')
load_dotenv('/workspaces/master/.env')

# Import systems
sys.path.append('.')
from trap_artist_manager import get_trap_artist_manager

class TrapArtistLauncher:
    """Launcher limpio específico para el artista trap"""
    
    def __init__(self):
        self.artist_name = os.getenv('TRAP_ARTIST_NAME', 'TrapStar ML')
        self.artist_genre = os.getenv('TRAP_ARTIST_GENRE', 'trap')
        self.total_budget = float(os.getenv('TRAP_CAMPAIGN_BUDGET_TOTAL', 5000))
        self.trap_manager = None
    
    async def launch_trap_campaign(self, song_title: str, lyrics_prompt: str = "") -> Dict[str, Any]:
        """Lanzar campaña viral completa para el artista trap"""
        
        print(f"\n🎵 NEURAL FORGE - TRAP ARTIST CAMPAIGN LAUNCHER")
        print(f"=" * 70)
        print(f"🎤 Artista: {self.artist_name}")
        print(f"🎵 Canción: {song_title}")
        print(f"💰 Presupuesto: ${self.total_budget}")
        print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Inicializar trap manager
        if not self.trap_manager:
            print("\n🔧 Inicializando Trap Artist Manager...")
            self.trap_manager = await get_trap_artist_manager()
        
        # Crear campaña viral completa usando el trap manager
        print("\n🚀 Creando campaña viral completa...")
        campaign_result = await self.trap_manager.create_viral_campaign(
            song_title=song_title,
            lyrics_prompt=lyrics_prompt
        )
        
        # Mostrar resultados detallados
        self._display_campaign_results(campaign_result)
        
        # Guardar reporte de campaña
        report_file = self._save_campaign_report(song_title, campaign_result)
        
        return {
            "success": True,
            "artist": self.artist_name,
            "song": song_title,
            "campaign_data": campaign_result,
            "report_file": report_file,
            "launch_time": datetime.now().isoformat()
        }
    
    def _display_campaign_results(self, campaign_result: Dict[str, Any]):
        """Mostrar resultados detallados de la campaña"""
        
        print(f"\n📊 RESULTADOS DE LA CAMPAÑA")
        print(f"=" * 50)
        
        # Contenido generado
        content = campaign_result.get("content_generated", {})
        if content.get("success"):
            print(f"✅ Contenido AI: {content.get('variations_created', 0)} variaciones creadas")
            print(f"   Tipo: {content.get('content_type', 'N/A')}")
            print(f"   AI Enhanced: {'Sí' if content.get('ai_enhanced') else 'No'}")
        else:
            print(f"❌ Contenido AI: {content.get('error', 'Error desconocido')}")
        
        # Distribución satellites
        distribution = campaign_result.get("distribution", {})
        if distribution:
            satellites_count = distribution.get("satellites_configured", 0)
            print(f"✅ Satellites: {satellites_count} configurados")
            print(f"   Estrategia: {distribution.get('coordination', 'simultaneous')}")
            
            # Mostrar satellites específicos
            satellite_map = distribution.get("distribution_map", {})
            for sat_id, sat_info in list(satellite_map.items())[:3]:  # Mostrar primeros 3
                print(f"   🛰️ Satellite {sat_id}: {sat_info.get('satellite_name', 'N/A')}")
                print(f"      Tema: {sat_info.get('theme', 'N/A')}")
        
        # Meta Ads
        meta_ads = campaign_result.get("meta_ads", {})
        if meta_ads.get("campaign_configured"):
            config = meta_ads.get("config", {})
            print(f"✅ Meta Ads: Campaña configurada")
            print(f"   Presupuesto: ${config.get('total_budget', 0)}")
            print(f"   Países: {', '.join(config.get('target_countries', []))}")
            print(f"   Reach estimado: {meta_ads.get('estimated_reach', 'N/A')}")
        
        # YouTube
        youtube = campaign_result.get("youtube_coordination", {})
        if youtube:
            satellites_yt = youtube.get("satellites", {})
            print(f"✅ YouTube: {len(satellites_yt)} satellites coordinados")
            print(f"   Estrategia: {youtube.get('coordination_strategy', 'N/A')}")
            print(f"   Cross-promotion: {'Sí' if youtube.get('cross_promotion') else 'No'}")
        
        # Revenue Sharing
        revenue = campaign_result.get("revenue_sharing", {})
        if revenue:
            print(f"✅ Revenue Sharing: {revenue.get('artist_percentage', 0)}% artista")
            print(f"   Método pago: {revenue.get('payment_method', 'N/A')}")
            print(f"   Frecuencia: {revenue.get('payout_frequency', 'N/A')}")
    
    def _save_campaign_report(self, song_title: str, campaign_result: Dict[str, Any]) -> str:
        """Guardar reporte detallado de la campaña"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"logs/trap_campaigns/{self.artist_name}_{song_title}_{timestamp}.json"
        
        Path(report_file).parent.mkdir(parents=True, exist_ok=True)
        
        report_data = {
            "campaign_info": {
                "artist": self.artist_name,
                "song": song_title,
                "genre": self.artist_genre,
                "budget": self.total_budget,
                "launch_time": datetime.now().isoformat()
            },
            "campaign_results": campaign_result,
            "system_info": {
                "launcher_version": "trap_artist_v1.0",
                "neural_forge_version": "2.0",
                "dummy_mode": os.getenv('DUMMY_MODE', 'true')
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado: {report_file}")
        return report_file

async def interactive_trap_launcher():
    """Launcher interactivo para el artista trap"""
    
    launcher = TrapArtistLauncher()
    
    print(f"\n🎵 TRAP ARTIST CAMPAIGN LAUNCHER")
    print(f"Artista configurado: {launcher.artist_name}")
    print(f"Presupuesto disponible: ${launcher.total_budget}")
    
    # Input de canción
    print(f"\n📝 CONFIGURACIÓN DE CAMPAÑA")
    song_title = input("🎵 Nombre de la canción: ").strip()
    if not song_title:
        song_title = "Neural Trap Symphony"
        print(f"   Usando título por defecto: {song_title}")
    
    # Input de prompt de letras
    lyrics_prompt = input("📝 Prompt para las letras (opcional): ").strip()
    if not lyrics_prompt:
        lyrics_prompt = "Letra sobre AI y tecnología en el trap, con referencias urbanas y futuristas"
        print(f"   Usando prompt por defecto")
    
    # Confirmación
    print(f"\n🎯 RESUMEN DE CAMPAÑA:")
    print(f"   Artista: {launcher.artist_name}")
    print(f"   Canción: {song_title}")
    print(f"   Presupuesto: ${launcher.total_budget}")
    print(f"   Lyrics prompt: {lyrics_prompt[:50]}{'...' if len(lyrics_prompt) > 50 else ''}")
    
    confirm = input(f"\n¿Proceder con el lanzamiento? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Campaña cancelada por el usuario")
        return False
    
    # Lanzar campaña
    try:
        result = await launcher.launch_trap_campaign(song_title, lyrics_prompt)
        
        if result.get("success"):
            print(f"\n🎉 ¡CAMPAÑA LANZADA EXITOSAMENTE!")
            print(f"📄 Reporte completo: {result.get('report_file')}")
            return True
        else:
            print(f"\n❌ Error en la campaña: {result.get('error', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        return False

async def demo_trap_launcher():
    """Demo automático del launcher"""
    
    launcher = TrapArtistLauncher()
    
    # Campaña demo
    demo_songs = [
        {
            "title": "Neural Trap Symphony",
            "lyrics": "Letra sobre AI y tecnología en el trap, ritmos futuristas, beats pesados"
        },
        {
            "title": "Dark Code Beats",
            "lyrics": "Trap oscuro sobre programación y hacking, estética cyberpunk"
        },
        {
            "title": "Algoritmo Urbano",
            "lyrics": "Fusión de trap urbano con referencias a machine learning"
        }
    ]
    
    print(f"\n🎬 DEMO - TRAP ARTIST LAUNCHER")
    print(f"Ejecutando {len(demo_songs)} campañas demo...")
    
    results = []
    
    for i, song_data in enumerate(demo_songs, 1):
        print(f"\n{'='*20} CAMPAÑA {i}/{len(demo_songs)} {'='*20}")
        
        try:
            result = await launcher.launch_trap_campaign(
                song_title=song_data["title"],
                lyrics_prompt=song_data["lyrics"]
            )
            results.append(result)
            
            print(f"✅ Campaña {i} completada")
            
        except Exception as e:
            print(f"❌ Error en campaña {i}: {e}")
            results.append({"success": False, "error": str(e)})
    
    # Resumen final
    successful = len([r for r in results if r.get("success")])
    print(f"\n🏆 RESUMEN DEMO:")
    print(f"   Campañas exitosas: {successful}/{len(demo_songs)}")
    print(f"   Artista: {launcher.artist_name}")
    print(f"   Presupuesto total usado: ${launcher.total_budget * len(demo_songs)}")
    
    return successful == len(demo_songs)

async def main():
    """Main function"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        success = await demo_trap_launcher()
    else:
        success = await interactive_trap_launcher()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())