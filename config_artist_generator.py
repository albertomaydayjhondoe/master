#!/usr/bin/env python3
"""
🎵 DISCOGRÁFICA ML SYSTEM - GENERADOR DE CONFIGURACIÓN POR GÉNERO
================================================================

Este script permite crear configuraciones específicas para cada género musical
que maneja la discográfica, optimizando campañas según el estilo musical.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any

class GenreConfigGenerator:
    def __init__(self):
        self.config_dir = Path("config/genres")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Cargar configuración de géneros
        with open("config/genres/genre_config.yaml", "r", encoding="utf-8") as f:
            self.genre_config = yaml.safe_load(f)
    
    def generate_artist_config(self, artist_name: str, genre: str, custom_settings: Dict = None) -> Dict:
        """Genera configuración específica para un artista"""
        
        if genre not in self.genre_config["genres"]:
            raise ValueError(f"Género '{genre}' no soportado")
        
        genre_config = self.genre_config["genres"][genre]
        
        config = {
            "artist_info": {
                "name": artist_name,
                "genre": genre,
                "created_at": "2024-11-03"
            },
            "genre_settings": genre_config,
            "campaign_defaults": {
                "budget": 100 * genre_config["campaign_settings"]["budget_multiplier"],
                "duration_days": self.genre_config["global_settings"]["default_campaign_duration"],
                "target_engagement": genre_config["campaign_settings"]["engagement_target"],
                "viral_threshold": genre_config["campaign_settings"]["viral_threshold"]
            },
            "platform_distribution": {
                "tiktok": self.genre_config["platform_weights"]["tiktok"][genre],
                "instagram": self.genre_config["platform_weights"]["instagram"][genre],
                "youtube": self.genre_config["platform_weights"]["youtube"][genre],
                "facebook": self.genre_config["platform_weights"]["facebook"][genre]
            },
            "content_strategy": {
                "hashtags": genre_config["hashtags"],
                "posting_times": genre_config["posting_times"],
                "target_audience": genre_config["target_audience"]
            }
        }
        
        # Aplicar configuraciones personalizadas
        if custom_settings:
            config.update(custom_settings)
        
        return config
    
    def save_artist_config(self, artist_name: str, config: Dict):
        """Guarda configuración de artista"""
        artist_file = self.config_dir / f"{artist_name.lower().replace(' ', '_')}_config.json"
        
        with open(artist_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuración guardada: {artist_file}")
    
    def list_available_genres(self) -> List[str]:
        """Lista géneros disponibles"""
        return list(self.genre_config["genres"].keys())
    
    def create_campaign_template(self, genre: str) -> Dict:
        """Crea template de campaña para un género"""
        
        if genre not in self.genre_config["genres"]:
            raise ValueError(f"Género '{genre}' no soportado")
        
        genre_data = self.genre_config["genres"][genre]
        
        template = {
            "campaign_name": f"Nueva Campaña {genre_data['name']}",
            "genre": genre,
            "description": genre_data["description"],
            "duration_days": 30,
            "budget": 100 * genre_data["campaign_settings"]["budget_multiplier"],
            "platforms": {
                "tiktok": {
                    "active": True,
                    "budget_percentage": self.genre_config["platform_weights"]["tiktok"][genre],
                    "content_types": ["video_clip", "behind_scenes"],
                    "hashtags": genre_data["hashtags"]["primary"][:5]
                },
                "instagram": {
                    "active": True,
                    "budget_percentage": self.genre_config["platform_weights"]["instagram"][genre],
                    "content_types": ["video_clip", "audio_preview", "behind_scenes"],
                    "hashtags": genre_data["hashtags"]["primary"][:5]
                },
                "youtube": {
                    "active": True,
                    "budget_percentage": self.genre_config["platform_weights"]["youtube"][genre],
                    "content_types": ["lyrics_video", "live_performance"],
                    "hashtags": genre_data["hashtags"]["secondary"][:5]
                }
            },
            "target_audience": genre_data["target_audience"],
            "optimal_posting_times": genre_data["posting_times"]["optimal"],
            "success_metrics": {
                "engagement_target": genre_data["campaign_settings"]["engagement_target"],
                "viral_threshold": genre_data["campaign_settings"]["viral_threshold"]
            }
        }
        
        return template

def interactive_setup():
    """Setup interactivo para crear configuración de artista"""
    
    generator = GenreConfigGenerator()
    
    print("🎵 CONFIGURADOR DE ARTISTA - DISCOGRÁFICA ML")
    print("=" * 50)
    print()
    
    # Solicitar información del artista
    artist_name = input("📝 Nombre del artista: ").strip()
    if not artist_name:
        print("❌ Nombre del artista requerido")
        return
    
    # Mostrar géneros disponibles
    genres = generator.list_available_genres()
    print("\n🎼 Géneros disponibles:")
    for i, genre in enumerate(genres, 1):
        genre_info = generator.genre_config["genres"][genre]
        print(f"  {i}. {genre_info['name']} - {genre_info['description']}")
    
    # Seleccionar género
    while True:
        try:
            selection = int(input(f"\n🎯 Selecciona género (1-{len(genres)}): "))
            if 1 <= selection <= len(genres):
                selected_genre = genres[selection - 1]
                break
            else:
                print(f"❌ Selección inválida. Usa 1-{len(genres)}")
        except ValueError:
            print("❌ Por favor ingresa un número válido")
    
    # Generar configuración
    print(f"\n🔧 Generando configuración para {artist_name} ({selected_genre})...")
    
    config = generator.generate_artist_config(artist_name, selected_genre)
    generator.save_artist_config(artist_name, config)
    
    # Crear template de campaña
    campaign_template = generator.create_campaign_template(selected_genre)
    campaign_file = generator.config_dir / f"{artist_name.lower().replace(' ', '_')}_campaign_template.json"
    
    with open(campaign_file, "w", encoding="utf-8") as f:
        json.dump(campaign_template, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Template de campaña guardado: {campaign_file}")
    print()
    print("🎵 CONFIGURACIÓN COMPLETADA")
    print("=" * 30)
    print(f"📁 Archivos generados:")
    print(f"  - Configuración: config/genres/{artist_name.lower().replace(' ', '_')}_config.json")
    print(f"  - Template campaña: config/genres/{artist_name.lower().replace(' ', '_')}_campaign_template.json")
    print()
    print("🚀 ¡Listo para crear campañas virales!")

if __name__ == "__main__":
    try:
        interactive_setup()
    except KeyboardInterrupt:
        print("\n\n❌ Configuración cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")