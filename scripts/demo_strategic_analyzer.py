#!/usr/bin/env python3
"""
Demo automático del Strategic Branch Analyzer
Muestra la inteligencia de selección sin interacción
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.strategic_branch_analyzer import BandwidthOptimizationAnalyzer

def demo_analysis():
    """Ejecuta demo automático de análisis de ramas"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                    🎯 DEMO AUTOMÁTICO - STRATEGIC ANALYZER                      ║  
║                                                                                  ║
║  Simulación de selección inteligente de ramas por restricciones                 ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
    """)
    
    analyzer = BandwidthOptimizationAnalyzer()
    
    # Mostrar comparación de ramas
    analyzer.display_branch_comparison()
    
    # Casos de uso típicos
    scenarios = [
        {
            "name": "🌍 Deployment IoT Edge",
            "bandwidth": 0.5,
            "ram": 1.0,
            "cpu": 2,
            "storage": 5.0
        },
        {
            "name": "📱 Red Móvil 3G/4G",
            "bandwidth": 3.0,
            "ram": 4.0,
            "cpu": 4,
            "storage": 15.0
        },
        {
            "name": "☁️  Cloud Distribuido",
            "bandwidth": 25.0,
            "ram": 8.0,
            "cpu": 16,
            "storage": 50.0
        },
        {
            "name": "🏢 Producción Enterprise",
            "bandwidth": 100.0,
            "ram": 32.0,
            "cpu": 64,
            "storage": 200.0
        }
    ]
    
    print("\n🎭 SIMULACIÓN DE ESCENARIOS REALES")
    print("="*80)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print("-" * 60)
        print(f"   📊 Bandwidth: {scenario['bandwidth']} Mbps")
        print(f"   💻 RAM: {scenario['ram']} GB")
        print(f"   ⚙️  CPU: {scenario['cpu']} cores")
        print(f"   💾 Storage: {scenario['storage']} GB")
        
        # Obtener recomendación
        optimal = analyzer.get_optimal_branch(
            scenario['bandwidth'],
            scenario['ram'], 
            scenario['cpu'],
            scenario['storage']
        )
        
        print(f"   🎯 RAMA RECOMENDADA: {optimal}")
        
        # Mostrar análisis detallado
        analyzer.display_detailed_analysis(optimal)
        
        print("\n" + "="*80)
    
    # Resumen final
    print(f"""
🎊 ANÁLISIS ESTRATÉGICO COMPLETADO

📈 EFICIENCIAS LOGRADAS:
   • Edge Deployment: 75% reducción bandwidth, ideal para IoT
   • Bandwidth Optimized: 70% reducción bandwidth, perfecto para redes limitadas  
   • Micro Services: 60% reducción + escalabilidad distribuida
   • Full Version: Características completas para alta capacidad

🚀 DEPLOY AUTOMÁTICO:
   python scripts/strategic_branch_analyzer.py
   
   O usar directamente:
   git checkout <rama-optima>
   docker-compose -f docker-compose.v6.yml up -d
    """)

if __name__ == "__main__":
    demo_analysis()