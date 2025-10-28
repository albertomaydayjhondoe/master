#!/usr/bin/env python3
"""
Script para verificar las estadísticas actuales del canal de YouTube
Channel ID: UCgohgqLVu1QPdfa64Vkrgeg
"""

import requests
import json
from datetime import datetime
import re

def get_channel_stats_alternative():
    """
    Intenta obtener estadísticas del canal usando métodos alternativos
    """
    channel_id = "UCgohgqLVu1QPdfa64Vkrgeg"
    
    # Método 1: Usar diferentes URLs públicas
    methods = [
        f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}",
        f"https://www.youtube.com/c/{channel_id}/about",
        f"https://socialblade.com/youtube/channel/{channel_id}",
        f"https://noxinfluencer.com/youtube/channel/{channel_id}"
    ]
    
    results = {}
    
    for i, url in enumerate(methods, 1):
        try:
            print(f"\n🔍 Método {i}: Verificando {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Buscar patrones de suscriptores
                subscriber_patterns = [
                    r'(\d+(?:,\d{3})*)\s*subscribers?',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*subscribers?',
                    r'"subscriberCountText":{"simpleText":"([^"]+)"',
                    r'subscribers.*?(\d+(?:,\d{3})*)',
                    r'(\d+(?:,\d{3})*)\s*suscriptores?'
                ]
                
                for pattern in subscriber_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        results[f'method_{i}'] = {
                            'url': url,
                            'subscribers_found': matches,
                            'status': 'success'
                        }
                        print(f"✅ Encontrado: {matches}")
                        break
                else:
                    results[f'method_{i}'] = {
                        'url': url,
                        'status': 'no_data_found',
                        'content_length': len(content)
                    }
                    print(f"⚠️  Sin datos específicos encontrados")
            else:
                results[f'method_{i}'] = {
                    'url': url,
                    'status': f'http_error_{response.status_code}'
                }
                print(f"❌ Error HTTP {response.status_code}")
                
        except Exception as e:
            results[f'method_{i}'] = {
                'url': url,
                'status': 'error',
                'error': str(e)
            }
            print(f"❌ Error: {e}")
    
    return results

def analyze_previous_projections():
    """
    Analiza las proyecciones previas y compara con datos disponibles
    """
    print("\n" + "="*60)
    print("📊 ANÁLISIS DE PROYECCIONES PREVIAS")
    print("="*60)
    
    # Datos de nuestro análisis anterior
    previous_analysis = {
        'baseline_subscribers': 15200,
        'monthly_views': 42000,
        'engagement_rate': 3.2,
        'projected_growth_with_500_meta_ads': {
            'new_subscribers_month': '410-600',
            'additional_views': '22500-37000',
            'roi_percentage': '70-140%'
        }
    }
    
    print(f"🔢 Línea Base Anterior:")
    print(f"   • Suscriptores: {previous_analysis['baseline_subscribers']:,}")
    print(f"   • Vistas mensuales: {previous_analysis['monthly_views']:,}")
    print(f"   • Engagement rate: {previous_analysis['engagement_rate']}%")
    
    print(f"\n🚀 Proyecciones con Meta Ads (€500/mes):")
    print(f"   • Nuevos suscriptores/mes: {previous_analysis['projected_growth_with_500_meta_ads']['new_subscribers_month']}")
    print(f"   • Vistas adicionales: {previous_analysis['projected_growth_with_500_meta_ads']['additional_views']}")
    print(f"   • ROI esperado: {previous_analysis['projected_growth_with_500_meta_ads']['roi_percentage']}")
    
    return previous_analysis

def check_channel_validity():
    """
    Verifica si el canal existe y está activo
    """
    channel_id = "UCgohgqLVu1QPdfa64Vkrgeg"
    
    # URLs básicas para verificar existencia
    test_urls = [
        f"https://www.youtube.com/channel/{channel_id}",
        f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    ]
    
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DE EXISTENCIA DEL CANAL")
    print("="*60)
    
    for url in test_urls:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Canal existe: {url}")
                return True
            else:
                print(f"❌ Error {response.status_code}: {url}")
        except:
            print(f"❌ No accesible: {url}")
    
    return False

def main():
    print("="*80)
    print("🎯 VERIFICACIÓN DEL CANAL DE YOUTUBE")
    print("📺 Channel ID: UCgohgqLVu1QPdfa64Vkrgeg")
    print("📅 Análisis realizado:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80)
    
    # 1. Verificar existencia del canal
    channel_exists = check_channel_validity()
    
    # 2. Intentar obtener estadísticas actuales
    if channel_exists:
        current_stats = get_channel_stats_alternative()
    else:
        current_stats = {}
    
    # 3. Analizar proyecciones previas
    previous_data = analyze_previous_projections()
    
    # 4. Generar reporte final
    print("\n" + "="*60)
    print("📋 REPORTE FINAL")
    print("="*60)
    
    print(f"\n🔍 Estado del Canal:")
    if channel_exists:
        print("   ✅ Canal existe y es accesible")
    else:
        print("   ❌ Canal no accesible o no existe")
    
    print(f"\n📊 Datos Obtenidos:")
    for method, data in current_stats.items():
        if data.get('status') == 'success':
            print(f"   ✅ {method}: {data.get('subscribers_found', 'N/A')}")
        else:
            print(f"   ❌ {method}: {data.get('status', 'Error')}")
    
    print(f"\n⚠️  NOTA IMPORTANTE:")
    print(f"   • Las restricciones de cookies y APIs limitan el acceso directo")
    print(f"   • Los datos del análisis anterior (15,200 subs) necesitan verificación")
    print(f"   • Se recomienda verificación manual del canal")
    
    print(f"\n🎯 RECOMENDACIONES:")
    print(f"   1. Verificar manualmente el canal en YouTube")
    print(f"   2. Usar herramientas como Social Blade para estadísticas")
    print(f"   3. Ajustar proyecciones según datos reales actuales")
    print(f"   4. El sistema automatizado sigue siendo válido independientemente")
    
    # Guardar resultados
    report = {
        'timestamp': datetime.now().isoformat(),
        'channel_id': 'UCgohgqLVu1QPdfa64Vkrgeg',
        'channel_exists': channel_exists,
        'stats_attempts': current_stats,
        'previous_analysis': previous_data,
        'status': 'needs_manual_verification'
    }
    
    with open('channel_verification_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Reporte guardado en: channel_verification_report.json")
    
    return report

if __name__ == "__main__":
    main()