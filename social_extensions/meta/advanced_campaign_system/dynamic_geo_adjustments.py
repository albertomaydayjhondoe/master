"""
Advanced Campaign System - Dynamic Geographic Adjustments
Ajustes geográficos dinámicos con redistribución automática basada en performance
"""

import json
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

class AdjustmentTrigger(Enum):
    """Tipos de triggers para ajustes geográficos"""
    PERFORMANCE_THRESHOLD = "performance_threshold"
    ROI_EXCELLENCE = "roi_excellence"
    BUDGET_OPTIMIZATION = "budget_optimization"
    MARKET_SATURATION = "market_saturation"
    COMPETITIVE_PRESSURE = "competitive_pressure"

@dataclass
class CountryPerformance:
    """Métricas de rendimiento por país"""
    country_code: str
    budget_allocated: float
    budget_spent: float
    views_generated: int
    ctr: float
    cpv: float
    cpm: float
    roi: float
    engagement_rate: float
    conversion_count: int
    market_saturation: float  # 0-1
    competitive_pressure: float  # 0-1
    timestamp: datetime

@dataclass
class GeographicAdjustment:
    """Ajuste geográfico aplicado"""
    adjustment_id: str
    trigger: AdjustmentTrigger
    source_country: str
    target_country: str
    budget_moved: float
    expected_improvement: float
    confidence_score: float
    timestamp: datetime
    reason: str

class DynamicGeoAdjuster:
    """Sistema de ajustes geográficos dinámicos"""
    
    def __init__(self):
        self.adjustment_history = []
        self.performance_history = {}
        
        # Configuración del sistema
        self.adjustment_config = {
            'spain_minimum_percentage': 27,      # Mínimo fijo para España
            'spain_maximum_percentage': 45,      # Máximo permitido para España
            'adjustment_sensitivity': 0.15,      # Sensibilidad a cambios (0-1)
            'minimum_country_budget': 25,        # Presupuesto mínimo por país
            'roi_excellence_threshold': 200,     # ROI para considerar "excelencia"
            'performance_monitoring_hours': 24,   # Horas para evaluar performance
            'max_adjustments_per_cycle': 3,      # Máximo ajustes por ciclo
            'adjustment_magnitude_limit': 0.20   # Máximo 20% de cambio por ajuste
        }
        
        # Factores de mercado por país
        self.market_factors = {
            'ES': {
                'base_ctr': 3.2, 'base_cpv': 0.45, 'saturation_rate': 0.65,
                'competition_level': 0.7, 'growth_potential': 0.4
            },
            'MX': {
                'base_ctr': 3.8, 'base_cpv': 0.35, 'saturation_rate': 0.45,
                'competition_level': 0.8, 'growth_potential': 0.8
            },
            'CO': {
                'base_ctr': 3.5, 'base_cpv': 0.38, 'saturation_rate': 0.40,
                'competition_level': 0.6, 'growth_potential': 0.7
            },
            'AR': {
                'base_ctr': 3.1, 'base_cpv': 0.42, 'saturation_rate': 0.50,
                'competition_level': 0.7, 'growth_potential': 0.6
            },
            'CL': {
                'base_ctr': 2.9, 'base_cpv': 0.48, 'saturation_rate': 0.55,
                'competition_level': 0.6, 'growth_potential': 0.5
            },
            'PE': {
                'base_ctr': 3.3, 'base_cpv': 0.40, 'saturation_rate': 0.35,
                'competition_level': 0.5, 'growth_potential': 0.9
            },
            'EC': {
                'base_ctr': 3.0, 'base_cpv': 0.44, 'saturation_rate': 0.30,
                'competition_level': 0.4, 'growth_potential': 0.8
            }
        }
    
    def monitor_country_performance(self, campaign_data: Dict, 
                                  hours_elapsed: int = 12) -> Dict[str, CountryPerformance]:
        """
        Simula monitoreo de rendimiento por país en tiempo real
        """
        print(f"📊 MONITOREANDO PERFORMANCE GEOGRÁFICA ({hours_elapsed}h transcurridas)")
        print("-" * 60)
        
        performances = {}
        
        # Obtener distribución geográfica actual
        geo_allocation = campaign_data.get('geo_allocation', {})
        region_budgets = geo_allocation.get('region_budgets', {})
        
        if not region_budgets:
            print("⚠️ No hay datos de distribución geográfica disponibles")
            return {}
        
        for country, allocated_budget in region_budgets.items():
            market_factor = self.market_factors.get(country, self.market_factors['ES'])
            
            # Simular gasto progresivo (más gasto con más tiempo)
            spending_rate = min(hours_elapsed / 24.0, 1.0)  # 100% gastado en 24h
            budget_spent = allocated_budget * spending_rate * random.uniform(0.8, 1.0)
            
            # Simular métricas con variación realista
            base_ctr = market_factor['base_ctr']
            base_cpv = market_factor['base_cpv']
            
            # Variación por saturación (peor performance si más saturado)
            saturation_penalty = market_factor['saturation_rate'] * random.uniform(0.1, 0.3)
            
            actual_ctr = base_ctr * (1 - saturation_penalty) * random.uniform(0.8, 1.2)
            actual_cpv = base_cpv * (1 + saturation_penalty * 0.5) * random.uniform(0.9, 1.1)
            
            # Calcular métricas derivadas
            views_generated = int(budget_spent / actual_cpv) if actual_cpv > 0 else 0
            cpm = actual_cpv * 1000  # Convertir CPV a CPM aproximado
            
            # Engagement varía por país y saturación
            base_engagement = random.uniform(4.5, 7.5)
            actual_engagement = base_engagement * (1 - saturation_penalty * 0.5)
            
            # Conversiones (simuladas a $15 promedio)
            conversion_rate = actual_ctr / 100 * random.uniform(0.8, 1.2)
            conversions = int(views_generated * conversion_rate / 100)
            revenue = conversions * 15
            
            # ROI
            roi = ((revenue - budget_spent) / budget_spent) * 100 if budget_spent > 0 else 0
            
            performance = CountryPerformance(
                country_code=country,
                budget_allocated=allocated_budget,
                budget_spent=budget_spent,
                views_generated=views_generated,
                ctr=actual_ctr,
                cpv=actual_cpv,
                cpm=cpm,
                roi=roi,
                engagement_rate=actual_engagement,
                conversion_count=conversions,
                market_saturation=market_factor['saturation_rate'] + random.uniform(-0.1, 0.1),
                competitive_pressure=market_factor['competition_level'] + random.uniform(-0.1, 0.1),
                timestamp=datetime.now()
            )
            
            performances[country] = performance
            
            print(f"🌍 {country}:")
            print(f"   💰 Gastado: ${budget_spent:.0f}/${allocated_budget:.0f} ({budget_spent/allocated_budget*100:.0f}%)")
            print(f"   📊 ROI: {roi:+.1f}% | CTR: {actual_ctr:.2f}% | CPV: ${actual_cpv:.3f}")
            print(f"   👀 Vistas: {views_generated:,} | Conversiones: {conversions}")
        
        print()
        return performances
    
    def identify_adjustment_opportunities(self, 
                                       performances: Dict[str, CountryPerformance]) -> List[Tuple[AdjustmentTrigger, str, str, float]]:
        """
        Identifica oportunidades de ajuste geográfico
        """
        print("🎯 IDENTIFICANDO OPORTUNIDADES DE AJUSTE")
        print("-" * 45)
        
        opportunities = []
        
        # Ordenar países por ROI
        countries_by_roi = sorted(performances.items(), key=lambda x: x[1].roi, reverse=True)
        
        print("📈 Ranking por ROI:")
        for i, (country, perf) in enumerate(countries_by_roi, 1):
            print(f"   {i}. {country}: {perf.roi:+.1f}% ROI")
        print()
        
        # 1. Detectar países con ROI excepcional
        roi_threshold = self.adjustment_config['roi_excellence_threshold']
        excellent_countries = [
            (country, perf) for country, perf in performances.items()
            if perf.roi > roi_threshold
        ]
        
        if excellent_countries:
            print(f"🏆 Países con ROI excepcional (>{roi_threshold}%):")
            for country, perf in excellent_countries:
                print(f"   • {country}: {perf.roi:+.1f}% ROI")
            print()
        
        # 2. Detectar países con bajo rendimiento
        avg_roi = sum(perf.roi for perf in performances.values()) / len(performances)
        underperforming = [
            (country, perf) for country, perf in performances.items()
            if perf.roi < avg_roi * 0.7  # 30% menos que el promedio
        ]
        
        if underperforming:
            print(f"📉 Países con bajo rendimiento (<{avg_roi*0.7:.0f}% ROI):")
            for country, perf in underperforming:
                print(f"   • {country}: {perf.roi:+.1f}% ROI")
            print()
        
        # 3. Generar oportunidades de redistribución
        spain_performance = performances.get('ES')
        spain_current_budget = spain_performance.budget_allocated if spain_performance else 0
        
        # España puede incrementarse si tiene ROI excepcional
        if (spain_performance and 
            spain_performance.roi > roi_threshold and
            spain_current_budget < self.adjustment_config['spain_maximum_percentage'] / 100 * sum(p.budget_allocated for p in performances.values())):
            
            # Buscar países donantes (bajo rendimiento, no España)
            potential_donors = [
                (country, perf) for country, perf in underperforming
                if country != 'ES' and perf.budget_allocated > self.adjustment_config['minimum_country_budget']
            ]
            
            if potential_donors:
                donor_country, donor_perf = min(potential_donors, key=lambda x: x[1].roi)
                
                # Calcular cantidad a mover (máximo 20% del presupuesto donante)
                max_move = donor_perf.budget_allocated * self.adjustment_config['adjustment_magnitude_limit']
                move_amount = min(max_move, 50)  # Máximo $50 por ajuste
                
                expected_improvement = (spain_performance.roi - donor_perf.roi) / 100 * move_amount
                
                opportunities.append((
                    AdjustmentTrigger.ROI_EXCELLENCE,
                    donor_country,
                    'ES',
                    move_amount
                ))
        
        # 4. Redistribución entre países LATAM por eficiencia
        latam_countries = [(c, p) for c, p in performances.items() if c != 'ES']
        if len(latam_countries) >= 2:
            # Mejor vs peor en LATAM
            best_latam = max(latam_countries, key=lambda x: x[1].roi)
            worst_latam = min(latam_countries, key=lambda x: x[1].roi)
            
            roi_difference = best_latam[1].roi - worst_latam[1].roi
            
            if roi_difference > 50:  # Diferencia significativa de ROI
                move_amount = worst_latam[1].budget_allocated * 0.15  # Mover 15%
                
                opportunities.append((
                    AdjustmentTrigger.BUDGET_OPTIMIZATION,
                    worst_latam[0],
                    best_latam[0],
                    move_amount
                ))
        
        print(f"✅ Oportunidades identificadas: {len(opportunities)}")
        return opportunities
    
    def execute_geographic_adjustment(self, 
                                    opportunity: Tuple[AdjustmentTrigger, str, str, float],
                                    current_allocation: Dict[str, float],
                                    performances: Dict[str, CountryPerformance]) -> GeographicAdjustment:
        """
        Ejecuta un ajuste geográfico específico
        """
        trigger, source_country, target_country, move_amount = opportunity
        
        print(f"🔄 EJECUTANDO AJUSTE GEOGRÁFICO")
        print("-" * 35)
        
        # Validar que el ajuste sea válido
        source_budget = current_allocation.get(source_country, 0)
        target_budget = current_allocation.get(target_country, 0)
        
        # Limitar movimiento para no violar reglas
        if source_country == 'ES':
            # España no puede bajar de su mínimo
            total_budget = sum(current_allocation.values())
            spain_minimum = total_budget * (self.adjustment_config['spain_minimum_percentage'] / 100)
            max_movable_from_spain = max(0, source_budget - spain_minimum)
            move_amount = min(move_amount, max_movable_from_spain)
        
        if target_country == 'ES':
            # España no puede superar su máximo
            total_budget = sum(current_allocation.values())
            spain_maximum = total_budget * (self.adjustment_config['spain_maximum_percentage'] / 100)
            max_movable_to_spain = max(0, spain_maximum - target_budget)
            move_amount = min(move_amount, max_movable_to_spain)
        
        # Asegurar que el país fuente mantenga presupuesto mínimo
        min_budget = self.adjustment_config['minimum_country_budget']
        max_movable = max(0, source_budget - min_budget)
        move_amount = min(move_amount, max_movable)
        
        if move_amount <= 0:
            print("❌ No se puede ejecutar ajuste: violación de límites")
            return None
        
        # Ejecutar movimiento
        current_allocation[source_country] -= move_amount
        current_allocation[target_country] += move_amount
        
        # Calcular mejora esperada
        source_perf = performances.get(source_country)
        target_perf = performances.get(target_country)
        
        if source_perf and target_perf:
            roi_difference = target_perf.roi - source_perf.roi
            expected_improvement = (roi_difference / 100) * move_amount
        else:
            expected_improvement = 0
        
        # Generar razón del ajuste
        reasons = {
            AdjustmentTrigger.ROI_EXCELLENCE: f"{target_country} muestra ROI excepcional ({target_perf.roi:.1f}%)",
            AdjustmentTrigger.BUDGET_OPTIMIZATION: f"Optimización: {target_country} supera a {source_country} por {target_perf.roi - source_perf.roi:.1f}% ROI",
            AdjustmentTrigger.PERFORMANCE_THRESHOLD: f"Performance de {source_country} bajo threshold",
            AdjustmentTrigger.MARKET_SATURATION: f"Saturación detectada en {source_country}",
            AdjustmentTrigger.COMPETITIVE_PRESSURE: f"Presión competitiva alta en {source_country}"
        }
        
        reason = reasons.get(trigger, "Ajuste automático por algoritmo")
        
        # Crear objeto de ajuste
        adjustment = GeographicAdjustment(
            adjustment_id=f"adj_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(100, 999)}",
            trigger=trigger,
            source_country=source_country,
            target_country=target_country,
            budget_moved=move_amount,
            expected_improvement=expected_improvement,
            confidence_score=random.uniform(0.75, 0.95),
            timestamp=datetime.now(),
            reason=reason
        )
        
        print(f"   📤 De: {source_country} (-${move_amount:.0f})")
        print(f"   📥 A: {target_country} (+${move_amount:.0f})")
        print(f"   💡 Razón: {reason}")
        print(f"   📈 Mejora esperada: ${expected_improvement:.0f}")
        print(f"   🎯 Confianza: {adjustment.confidence_score:.3f}")
        print()
        
        return adjustment
    
    def run_dynamic_adjustment_cycle(self, campaign_data: Dict, 
                                   hours_elapsed: int = 12) -> Dict:
        """
        Ejecuta ciclo completo de ajuste dinámico geográfico
        """
        print("🌍 SISTEMA DINÁMICO DE AJUSTES GEOGRÁFICOS")
        print("=" * 50)
        
        # 1. Monitorear performance actual
        performances = self.monitor_country_performance(campaign_data, hours_elapsed)
        
        if not performances:
            return {'adjustments_executed': False, 'reason': 'no_performance_data'}
        
        # 2. Identificar oportunidades
        opportunities = self.identify_adjustment_opportunities(performances)
        
        if not opportunities:
            print("✅ No se requieren ajustes geográficos en este momento")
            return {
                'adjustments_executed': False,
                'reason': 'no_opportunities_identified',
                'current_performance': {
                    country: {
                        'roi': perf.roi,
                        'ctr': perf.ctr,
                        'budget_spent': perf.budget_spent
                    }
                    for country, perf in performances.items()
                }
            }
        
        # 3. Ejecutar ajustes (limitar número máximo)
        max_adjustments = self.adjustment_config['max_adjustments_per_cycle']
        selected_opportunities = opportunities[:max_adjustments]
        
        # Obtener allocación actual
        current_allocation = campaign_data.get('geo_allocation', {}).get('region_budgets', {}).copy()
        
        executed_adjustments = []
        
        print(f"🔧 EJECUTANDO {len(selected_opportunities)} AJUSTES:")
        print("-" * 40)
        
        for i, opportunity in enumerate(selected_opportunities, 1):
            print(f"\nAjuste {i}/{len(selected_opportunities)}:")
            
            adjustment = self.execute_geographic_adjustment(
                opportunity,
                current_allocation,
                performances
            )
            
            if adjustment:
                executed_adjustments.append(adjustment)
                self.adjustment_history.append(adjustment)
        
        # 4. Calcular impacto total
        total_budget_moved = sum(adj.budget_moved for adj in executed_adjustments)
        total_expected_improvement = sum(adj.expected_improvement for adj in executed_adjustments)
        
        # 5. Actualizar datos de campaña
        updated_campaign_data = campaign_data.copy()
        if 'geo_allocation' not in updated_campaign_data:
            updated_campaign_data['geo_allocation'] = {}
        
        updated_campaign_data['geo_allocation']['region_budgets'] = current_allocation
        updated_campaign_data['geo_allocation']['last_adjustment'] = datetime.now().isoformat()
        
        # 6. Compilar resultados
        results = {
            'adjustments_executed': len(executed_adjustments) > 0,
            'adjustments_count': len(executed_adjustments),
            'total_budget_moved': total_budget_moved,
            'total_expected_improvement': total_expected_improvement,
            'executed_adjustments': [
                {
                    'adjustment_id': adj.adjustment_id,
                    'from': adj.source_country,
                    'to': adj.target_country,
                    'amount': adj.budget_moved,
                    'trigger': adj.trigger.value,
                    'reason': adj.reason,
                    'confidence': adj.confidence_score
                }
                for adj in executed_adjustments
            ],
            'updated_allocation': current_allocation,
            'performance_snapshot': {
                country: {
                    'roi': perf.roi,
                    'ctr': perf.ctr,
                    'cpv': perf.cpv,
                    'views': perf.views_generated,
                    'budget_spent': perf.budget_spent
                }
                for country, perf in performances.items()
            },
            'adjustment_timestamp': datetime.now().isoformat()
        }
        
        print("\n📊 RESUMEN DE AJUSTES DINÁMICOS:")
        print(f"   🔄 Ajustes ejecutados: {len(executed_adjustments)}")
        print(f"   💰 Presupuesto reubicado: ${total_budget_moved:.0f}")
        print(f"   📈 Mejora esperada: ${total_expected_improvement:.0f}")
        
        if current_allocation:
            spain_percentage = (current_allocation.get('ES', 0) / sum(current_allocation.values())) * 100
            print(f"   🇪🇸 España ajustada a: {spain_percentage:.1f}%")
        
        print()
        
        return results

# Test del módulo
if __name__ == "__main__":
    print("🧪 TEST DYNAMIC GEOGRAPHIC ADJUSTMENTS")
    print("=" * 40)
    
    # Crear instancia del ajustador
    geo_adjuster = DynamicGeoAdjuster()
    
    # Datos simulados de campaña con distribución geográfica
    campaign_data = {
        'campaign_id': 'camp_test_001',
        'geo_allocation': {
            'region_budgets': {
                'ES': 122,  # 27%
                'MX': 89,   # 19.8%
                'CO': 66,   # 14.7%
                'AR': 50,   # 11.1%
                'CL': 34,   # 7.6%
                'PE': 46,   # 10.2%
                'EC': 43    # 9.6%
            },
            'total_allocated': 450
        }
    }
    
    # Ejecutar ciclo de ajuste dinámico
    results = geo_adjuster.run_dynamic_adjustment_cycle(
        campaign_data,
        hours_elapsed=18  # 18 horas transcurridas
    )
    
    print("✅ TEST COMPLETADO")
    if results['adjustments_executed']:
        print(f"   Ajustes realizados: {results['adjustments_count']}")
        print(f"   Presupuesto movido: ${results['total_budget_moved']:.0f}")
        print(f"   España final: {(results['updated_allocation']['ES']/sum(results['updated_allocation'].values()))*100:.1f}%")
    else:
        print(f"   No se requirieron ajustes: {results.get('reason', 'unknown')}")