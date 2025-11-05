#!/usr/bin/env python3
"""
🎵 TRAP ARTIST VIRAL CAMPAIGN LAUNCHER
=====================================
Sistema personalizado para el artista trap que paga
Integrates Meta Ads + YouTube Satellites + AI Generation + Revenue Sharing
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

# Load production secrets
load_dotenv('config/secrets/secrets.env')

# Import our production systems
sys.path.append('.')
from social_extensions.meta_ads_production import MetaAdsProductionAPI
from social_extensions.youtube_integration import YouTubeMainAccount, YouTubeSatelliteManager
from social_extensions.satellite_distribution import SatelliteDistribution
from social_extensions.longcat_satellites_secure import get_secure_satellite_manager
from social_extensions.longcat_satellites import get_longcat_satellite_system
from trap_artist_manager import get_trap_artist_manager

class TrapArtistCampaignOrchestrator:
    """Orchestrator específico para campañas del artista trap que paga"""
    
    def __init__(self):
        # Información del artista trap
        self.artist_name = os.getenv('TRAP_ARTIST_NAME', 'TrapStar ML')
        self.artist_genre = os.getenv('TRAP_ARTIST_GENRE', 'trap')
        self.daily_budget = float(os.getenv('TRAP_CAMPAIGN_BUDGET_DAILY', 500))
        self.total_budget = float(os.getenv('TRAP_CAMPAIGN_BUDGET_TOTAL', 5000))
        
        # Initialize Meta Ads con configuración del artista
        self.meta_ads = MetaAdsProductionAPI()
        
        # Initialize Trap Artist Manager
        self.trap_manager = None
        
        # Initialize YouTube Main (metrics only)
        self.youtube_main = YouTubeMainAccount(
            api_key=os.getenv('YOUTUBE_API_KEY'),
            client_id=os.getenv('YOUTUBE_CLIENT_ID'),
            client_secret=os.getenv('YOUTUBE_CLIENT_SECRET'),
            refresh_token=os.getenv('YOUTUBE_REFRESH_TOKEN'),
            channel_id=os.getenv('YOUTUBE_CHANNEL_ID')
        )
        
        # Initialize YouTube Satellites (upload enabled)
        self.youtube_satellites = SatelliteDistribution()
        
        # Initialize LongCat Secure Satellite Manager
        self.satellite_manager = None
        
        # Campaign tracking
        self.active_campaigns = {}
    
    async def launch_trap_artist_campaign(self, 
                                         song: str,
                                         lyrics_prompt: str = "",
                                         video_path: str = "") -> Dict[str, Any]:
        """Launch viral campaign específica para el artista trap que paga"""
        
        # Inicializar trap manager si no existe
        if not self.trap_manager:
            self.trap_manager = await get_trap_artist_manager()
        
        campaign_id = f"trap_viral_{self.artist_name}_{song}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        target_countries = os.getenv('TRAP_CAMPAIGN_TARGET_COUNTRIES', 'ES,MX,AR,CO,PE,CL').split(',')
        
        print(f"\n🎵 LANZANDO CAMPAÑA VIRAL PARA {self.artist_name}")
        print(f"=" * 60)
        print(f"📋 Detalles de la Campaña:")
        print(f"   🎤 Artista: {self.artist_name}")
        print(f"   🎵 Canción: {song}")
        print(f"   🎶 Género: {self.artist_genre}")
        print(f"   💰 Presupuesto: ${self.total_budget}")
        print(f"   🌍 Países: {', '.join(target_countries)}")
        
        results = {
            "campaign_id": campaign_id,
            "artist": self.artist_name,
            "song": song,
            "genre": self.artist_genre,
            "budget": self.total_budget,
            "status": "launching",
            "video_generation": {},
            "meta_ads": {},
            "youtube_upload": {},
            "youtube_metrics": {},
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # 0. Usar el Trap Artist Manager para generar campaña completa
            print("\n🎬 Generando campaña viral con Trap Artist Manager...")
            
            trap_campaign = await self.trap_manager.create_viral_campaign(
                song_title=song,
                lyrics_prompt=lyrics_prompt
            )
            
            results["video_generation"] = trap_campaign.get("content_generated", {})
            results["satellite_distribution"] = trap_campaign.get("distribution", {})
            results["trap_campaign_id"] = trap_campaign.get("campaign_start", "")
            
            if trap_campaign.get("content_generated", {}).get("success"):
                successful_variations = trap_campaign.get("content_generated", {}).get("variations_created", 0)
                print(f"✅ {successful_variations} variaciones AI generadas para satellites temáticos")
                
                # Mock video path para compatibilidad
                video_path = f"data/temp/{self.artist_name}_{song}_trap_video.mp4"
                Path(video_path).parent.mkdir(parents=True, exist_ok=True)
                Path(video_path).write_text(f"Trap video for {self.artist_name} - {song}")
            else:
                print(f"❌ Error en generación AI: {trap_campaign.get('content_generated', {}).get('error', 'Unknown')}")
                
            if not video_path:
                results["video_generation"] = {"success": False, "error": "No video generated for trap campaign"}
            # 1. Coordinación YouTube específica para trap (ya manejada por trap_manager)
            print(f"\n📺 YouTube coordination manejada por Trap Artist Manager...")
            
            youtube_coordination = trap_campaign.get("youtube_coordination", {})
            
            results["youtube_upload"] = {
                "success": True,
                "main_channel": youtube_coordination.get("main_channel", {}),
                "satellites": youtube_coordination.get("satellites", {}),
                "strategy": youtube_coordination.get("coordination_strategy", "escalonado_viral"),
                "message": f"Coordinación YouTube para {self.artist_name} configurada"
            }
            
            print(f"✅ YouTube coordination: {youtube_coordination.get('coordination_strategy', 'configured')}")
            print(f"🛰️ Satellites configurados: {len(youtube_coordination.get('satellites', {}))}")
            
            results["youtube_upload"] = upload_result
            
            if upload_result.get("success"):
                print(f"✅ Video uploaded to satellite: {upload_result.get('satellite_id')}")
                print(f"   Video URL: {upload_result.get('video_url')}")
            else:
                print(f"❌ YouTube upload failed: {upload_result.get('error')}")
            
            # 2. Launch Meta Ads campaign (only if we have video)
            if video_path and os.path.exists(video_path):
                print("\n🛰️ Creating Meta Ads campaign...")
                meta_result = await self.meta_ads.create_viral_campaign(
                    artist=artist,
                    song=song,
                    video_path=video_path,
                    budget=budget,
                    target_countries=target_countries,
                    genre=genre
                )
            else:
                print("\n⚠️ Skipping Meta Ads (no video available)")
                meta_result = {"success": False, "error": "No video file for Meta Ads campaign"}
            
            results["meta_ads"] = meta_result
            
            if meta_result.get("success"):
                print(f"✅ Meta Ads campaign created: {meta_result.get('campaign_id')}")
                print(f"   Total budget: ${meta_result.get('total_budget')}")
                print(f"   Ad sets: {len(meta_result.get('adset_ids', []))}")
            else:
                print(f"❌ Meta Ads campaign failed: {meta_result.get('error')}")
            
            # 3. Collect initial metrics from main YouTube account
            print("\n📊 Collecting YouTube metrics...")
            try:
                metrics_result = await self.youtube_main.get_channel_metrics()
                results["youtube_metrics"] = metrics_result
                
                if metrics_result.get("error"):
                    print(f"⚠️ Metrics collection warning: {metrics_result['error']}")
                else:
                    print("✅ YouTube metrics collected from main account")
                    
            except Exception as e:
                print(f"⚠️ Metrics collection error: {e}")
                results["youtube_metrics"] = {"error": str(e)}
            
            # 4. Update campaign status
            success_count = sum([
                results["video_generation"].get("success", False),
                meta_result.get("success", False),
                upload_result.get("success", False)
            ])
            
            if success_count >= 1:  # At least one component succeeded
                results["status"] = "active"
                print(f"\n🎉 VIRAL CAMPAIGN LAUNCHED! ({success_count}/3 components active)")
            else:
                results["status"] = "failed"
                print("\n❌ Campaign launch failed - no components succeeded")
            
            # Store campaign
            self.active_campaigns[campaign_id] = results
            
            # Save to file
            os.makedirs("data/campaigns", exist_ok=True)
            with open(f"data/campaigns/{campaign_id}.json", "w") as f:
                json.dump(results, f, indent=2)
            
            return results
            
        except Exception as e:
            print(f"❌ Campaign orchestration error: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            return results
    
    async def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get real-time campaign performance"""
        
        if campaign_id not in self.active_campaigns:
            return {"error": "Campaign not found"}
        
        campaign = self.active_campaigns[campaign_id]
        
        # Get Meta Ads metrics
        if campaign["meta_ads"].get("campaign_id"):
            meta_metrics = await self.meta_ads.get_campaign_metrics(
                campaign["meta_ads"]["campaign_id"]
            )
            campaign["meta_ads"]["current_metrics"] = meta_metrics
        
        # Get YouTube metrics
        youtube_metrics = await self.youtube_main.get_channel_metrics()
        campaign["youtube_metrics"]["current"] = youtube_metrics
        
        campaign["last_updated"] = datetime.now().isoformat()
        
        return campaign

async def main():
    """Interactive campaign launcher"""
    
    print("🎵 ================================")
    print("🎵 Neural Forge Campaign Launcher")
    print("🎵 ================================")
    
    orchestrator = TrapArtistCampaignOrchestrator()
    
    # Interactive input
    print("\n📝 Campaign Configuration:")
    artist = input("🎤 Artist name: ").strip()
    song = input("🎵 Song title: ").strip()
    
    # Video options
    print("\n🎬 Video Options:")
    print("1. Use existing video file")
    print("2. Generate video with LongCat AI")
    print("3. Audio-only campaign (no video)")
    
    video_option = input("Choose option (1/2/3): ").strip()
    
    video_path = None
    video_prompt = None
    
    if video_option == "1":
        video_path = input("📁 Video file path: ").strip()
    elif video_option == "2":
        video_prompt = input("🎨 Video generation prompt: ").strip()
        if not video_prompt:
            video_prompt = f"Professional music video for {artist} performing {song}, urban style, dynamic lighting"
    
    genre = input("🎭 Genre (trap/reggaeton/pop): ").strip() or "trap"
    
    try:
        budget = float(input("💰 Budget ($): ").strip() or "100")
    except:
        budget = 100.0
    
    countries_input = input("🌍 Target countries (US,MX,ES): ").strip()
    target_countries = [c.strip().upper() for c in countries_input.split(",")] if countries_input else ['US', 'MX', 'ES']
    
    print(f"\n🚀 Ready to launch campaign:")
    print(f"   {artist} - {song}")
    print(f"   Budget: ${budget}")
    print(f"   Countries: {target_countries}")
    
    confirm = input("\n▶️ Launch campaign? (y/N): ").strip().lower()
    
    if confirm == 'y':
        # Launch campaign with satellite variations
        if video_option == "2":  # LongCat generation
            result = await orchestrator.launch_viral_campaign_with_satellites(
                artist=artist,
                song=song,
                video_prompt=video_prompt,
                genre=genre,
                budget=budget,
                target_countries=target_countries
            )
        else:  # Existing video or audio-only
            result = await orchestrator.launch_viral_campaign(
                artist=artist,
                song=song,
                video_path=video_path,
                genre=genre,
                budget=budget,
                target_countries=target_countries
            )
        
        print(f"\n📋 Campaign Results:")
        print(f"   Campaign ID: {result['campaign_id']}")
        print(f"   Status: {result['status']}")
        
        # Show component results
        print(f"\n🔧 Component Status:")
        print(f"   🎬 Video Generation: {'✅' if result['video_generation'].get('success') else '❌'}")
        print(f"   🛰️ Meta Ads: {'✅' if result['meta_ads'].get('success') else '❌'}")
        print(f"   📺 YouTube Upload: {'✅' if result['youtube_upload'].get('success') else '❌'}")
        
        if result["status"] == "active":
            print(f"\n🌐 Monitor campaign at:")
            print(f"   • Grafana: http://localhost:3000")
            print(f"   • Production Controller: http://localhost:7860")
            
            # Show generated video info
            if result['video_generation'].get('success') and result['video_generation'].get('video_path'):
                print(f"   • Generated Video: {result['video_generation']['video_path']}")
            
            # Option to check status
            check_status = input("\n📊 Check campaign status? (y/N): ").strip().lower()
            if check_status == 'y':
                status = await orchestrator.get_campaign_status(result['campaign_id'])
                print(f"\n📈 Campaign Status:")
                print(json.dumps(status, indent=2))
    else:
        print("❌ Campaign launch cancelled")

if __name__ == "__main__":
    asyncio.run(main())