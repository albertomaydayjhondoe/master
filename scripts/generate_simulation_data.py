#!/usr/bin/env python3
"""
Generador de Datos Simulados para Sistema de Documentación

Genera datos realistas para testing y demostración del sistema de documentación
cuando se sale del modo dummy o cuando no hay datos reales disponibles.

Autor: Sistema de Documentación Automática
Fecha: 2024
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class SimulatedMetric:
    """Métrica simulada para analytics"""
    name: str
    value: float
    trend: str  # up/down/stable
    change_percent: float
    timestamp: str

@dataclass 
class SimulatedUsageData:
    """Datos de uso simulados"""
    document: str
    views: int
    unique_visitors: int
    avg_time_seconds: float
    bounce_rate: float
    search_queries: List[str]
    popular_sections: List[str]

class DocumentationDataSimulator:
    """Generador de datos simulados para el sistema de documentación"""
    
    def __init__(self, repo_path: str = "/workspaces/master"):
        self.repo_path = Path(repo_path)
        self.data_dir = self.repo_path / "data" / "simulated"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Templates de contenido
        self.sample_documents = [
            "monitoring_system_README.md",
            "ml_integration_README.md", 
            "device_farm_README.md",
            "analytics_dashboard_README.md",
            "identity_management_README.md",
            "platform_publishing_README.md",
            "meta_ads_integration_README.md",
            "gologin_automation_README.md"
        ]
        
        self.sample_sections = [
            "Quick Start",
            "API Reference", 
            "Configuration",
            "Examples",
            "Troubleshooting",
            "Best Practices",
            "Integration",
            "Advanced Features"
        ]
        
        self.sample_search_queries = [
            "ML model configuration",
            "device setup guide",
            "API authentication", 
            "error troubleshooting",
            "environment variables",
            "database connection",
            "telegram bot setup",
            "automated testing",
            "deployment guide",
            "performance optimization",
            "monitoring alerts",
            "data analysis",
            "user management",
            "security settings"
        ]
    
    def generate_usage_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Generar analytics de uso simulados"""
        
        analytics = {
            "overview": {
                "total_views": random.randint(800, 1500),
                "unique_visitors": random.randint(50, 120),
                "avg_session_duration": random.uniform(180, 450),
                "bounce_rate": random.uniform(0.25, 0.45),
                "search_queries": random.randint(150, 300)
            },
            "trends": self._generate_daily_trends(days),
            "popular_documents": self._generate_document_popularity(),
            "search_trends": self._generate_search_trends(),
            "section_heatmap": self._generate_section_heatmap(),
            "user_behavior": self._generate_user_behavior()
        }
        
        return analytics
    
    def _generate_daily_trends(self, days: int) -> List[Dict[str, Any]]:
        """Generar tendencias diarias"""
        
        trends = []
        base_views = 45
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            
            # Simular variación realista (más actividad en días laborales)
            if date.weekday() < 5:  # Lunes a Viernes
                multiplier = random.uniform(0.8, 1.3)
            else:  # Fin de semana
                multiplier = random.uniform(0.3, 0.7)
            
            # Tendencia general creciente
            growth = 1 + (i / days) * 0.2
            
            views = int(base_views * multiplier * growth)
            unique_visitors = int(views * random.uniform(0.3, 0.6))
            
            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "views": views,
                "unique_visitors": unique_visitors,
                "search_queries": int(views * random.uniform(0.15, 0.25)),
                "avg_session_time": random.uniform(120, 300)
            })
        
        return trends
    
    def _generate_document_popularity(self) -> List[Dict[str, Any]]:
        """Generar popularidad de documentos"""
        
        popular_docs = []
        
        for i, doc in enumerate(self.sample_documents):
            # Simular popularidad decreciente con variación
            base_popularity = 100 - (i * 8) + random.randint(-15, 15)
            
            doc_data = {
                "name": doc.replace("_README.md", "").replace("_", " ").title(),
                "filename": doc,
                "views": max(base_popularity, 10),
                "unique_visitors": int(base_popularity * random.uniform(0.4, 0.7)),
                "avg_time_seconds": random.uniform(90, 300),
                "bounce_rate": random.uniform(0.2, 0.6),
                "last_updated": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "quality_score": random.uniform(75, 95)
            }
            
            popular_docs.append(doc_data)
        
        # Ordenar por vistas
        popular_docs.sort(key=lambda x: x["views"], reverse=True)
        
        return popular_docs
    
    def _generate_search_trends(self) -> List[Dict[str, Any]]:
        """Generar tendencias de búsqueda"""
        
        search_trends = []
        
        # Top 10 búsquedas
        selected_queries = random.sample(self.sample_search_queries, 10)
        
        for i, query in enumerate(selected_queries):
            trend_data = {
                "query": query,
                "count": random.randint(25, 80) - (i * 3),
                "trend": random.choice(["up", "down", "stable"]),
                "avg_results": random.randint(3, 15),
                "success_rate": random.uniform(0.6, 0.9)
            }
            
            search_trends.append(trend_data)
        
        return sorted(search_trends, key=lambda x: x["count"], reverse=True)
    
    def _generate_section_heatmap(self) -> Dict[str, Any]:
        """Generar heatmap de secciones"""
        
        heatmap_data = []
        documents = [doc.replace("_README.md", "") for doc in self.sample_documents[:6]]
        
        for doc in documents:
            doc_values = []
            for section in self.sample_sections:
                # Simular popularidad de secciones
                if section in ["Quick Start", "Examples"]:
                    base_value = random.randint(40, 80)
                elif section in ["API Reference", "Configuration"]:
                    base_value = random.randint(20, 60)
                else:
                    base_value = random.randint(10, 40)
                
                doc_values.append(base_value)
            
            heatmap_data.append(doc_values)
        
        return {
            "values": heatmap_data,
            "documents": documents,
            "sections": self.sample_sections
        }
    
    def _generate_user_behavior(self) -> Dict[str, Any]:
        """Generar comportamiento de usuarios"""
        
        behavior = {
            "top_entry_pages": [
                {"page": "ML Integration", "percentage": 28.5},
                {"page": "Device Farm", "percentage": 22.1}, 
                {"page": "Analytics Dashboard", "percentage": 18.7},
                {"page": "Monitoring System", "percentage": 15.3},
                {"page": "Others", "percentage": 15.4}
            ],
            "common_paths": [
                ["Home", "ML Integration", "Examples", "API Reference"],
                ["Search", "Device Farm", "Quick Start", "Configuration"],
                ["Home", "Analytics Dashboard", "Installation", "Troubleshooting"],
                ["Browse", "Monitoring System", "Telegram Setup", "Best Practices"]
            ],
            "exit_pages": [
                {"page": "Examples", "percentage": 25.2},
                {"page": "API Reference", "percentage": 19.8},
                {"page": "Troubleshooting", "percentage": 16.5},
                {"page": "Configuration", "percentage": 14.1},
                {"page": "Others", "percentage": 24.4}
            ]
        }
        
        return behavior
    
    def generate_system_health(self) -> Dict[str, Any]:
        """Generar métricas de salud del sistema"""
        
        health = {
            "overall_score": random.uniform(82, 94),
            "components": {
                "content_quality": random.uniform(85, 95),
                "link_integrity": random.uniform(90, 98),
                "freshness": random.uniform(75, 90),
                "coverage": random.uniform(80, 92),
                "searchability": random.uniform(88, 96)
            },
            "issues": self._generate_health_issues(),
            "recommendations": [
                "Update outdated documentation sections",
                "Add more code examples to configuration guides",
                "Improve cross-linking between related documents",
                "Standardize section structures across all docs"
            ],
            "last_check": datetime.now().isoformat()
        }
        
        return health
    
    def _generate_health_issues(self) -> List[Dict[str, Any]]:
        """Generar problemas de salud simulados"""
        
        possible_issues = [
            {
                "type": "content",
                "severity": "low",
                "description": "Some documents have less than optimal word count",
                "affected_files": random.sample(self.sample_documents, 2)
            },
            {
                "type": "links", 
                "severity": "medium",
                "description": "Few broken internal links detected",
                "affected_files": random.sample(self.sample_documents, 1)
            },
            {
                "type": "freshness",
                "severity": "low", 
                "description": "Some documentation hasn't been updated in 60+ days",
                "affected_files": random.sample(self.sample_documents, 3)
            }
        ]
        
        # Retornar 0-2 problemas aleatorios
        return random.sample(possible_issues, random.randint(0, 2))
    
    def generate_code_analysis(self) -> Dict[str, Any]:
        """Generar análisis de código simulado"""
        
        analysis = {
            "files_analyzed": random.randint(25, 45),
            "functions_detected": random.randint(150, 280),
            "classes_detected": random.randint(30, 65),
            "documentation_coverage": random.uniform(75, 90),
            "recent_changes": [
                {
                    "file": "social_extensions/telegram/monitoring.py",
                    "functions_added": ["send_alert", "track_metric"],
                    "classes_modified": ["TelegramMonitor"],
                    "impact": "medium"
                },
                {
                    "file": "ml_integration/ultralytics_bridge.py", 
                    "functions_added": ["predict_viral_content"],
                    "classes_modified": ["UltralyticsMLBridge"],
                    "impact": "high"
                },
                {
                    "file": "device_farm/controllers/device_manager.py",
                    "functions_added": ["connect_device", "execute_action"],
                    "classes_added": ["DeviceController"], 
                    "impact": "high"
                }
            ],
            "suggestions": [
                "Add docstrings to newly created functions",
                "Update API documentation for modified classes", 
                "Create examples for new device management features",
                "Document viral prediction model parameters"
            ]
        }
        
        return analysis
    
    def save_simulated_data(self):
        """Guardar todos los datos simulados"""
        
        print("🎭 Generando datos simulados...")
        
        # Analytics data
        analytics = self.generate_usage_analytics(30)
        with open(self.data_dir / "analytics.json", "w") as f:
            json.dump(analytics, f, indent=2, default=str)
        
        # System health
        health = self.generate_system_health()
        with open(self.data_dir / "health.json", "w") as f:
            json.dump(health, f, indent=2, default=str)
        
        # Code analysis
        code_analysis = self.generate_code_analysis()
        with open(self.data_dir / "code_analysis.json", "w") as f:
            json.dump(code_analysis, f, indent=2, default=str)
        
        # Usage metrics for individual documents
        usage_metrics = {}
        for doc in self.sample_documents:
            usage_metrics[doc] = {
                "views": random.randint(50, 200),
                "searches": random.randint(10, 50),
                "last_accessed": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
                "avg_time_spent": random.uniform(120, 400),
                "bounce_rate": random.uniform(0.2, 0.5)
            }
        
        with open(self.data_dir / "usage_metrics.json", "w") as f:
            json.dump(usage_metrics, f, indent=2, default=str)
        
        print(f"✅ Datos simulados guardados en: {self.data_dir}")
        print("📊 Archivos generados:")
        print(f"   • analytics.json - Analytics y métricas de uso")
        print(f"   • health.json - Métricas de salud del sistema")
        print(f"   • code_analysis.json - Análisis de código")
        print(f"   • usage_metrics.json - Métricas por documento")
        
        return {
            "analytics": analytics,
            "health": health, 
            "code_analysis": code_analysis,
            "usage_metrics": usage_metrics
        }
    
    def load_simulated_data(self, data_type: str = "all") -> Dict[str, Any]:
        """Cargar datos simulados existentes"""
        
        data = {}
        
        if data_type in ["all", "analytics"]:
            analytics_file = self.data_dir / "analytics.json"
            if analytics_file.exists():
                with open(analytics_file, "r") as f:
                    data["analytics"] = json.load(f)
        
        if data_type in ["all", "health"]:
            health_file = self.data_dir / "health.json" 
            if health_file.exists():
                with open(health_file, "r") as f:
                    data["health"] = json.load(f)
        
        if data_type in ["all", "code_analysis"]:
            code_file = self.data_dir / "code_analysis.json"
            if code_file.exists():
                with open(code_file, "r") as f:
                    data["code_analysis"] = json.load(f)
        
        if data_type in ["all", "usage_metrics"]:
            usage_file = self.data_dir / "usage_metrics.json"
            if usage_file.exists():
                with open(usage_file, "r") as f:
                    data["usage_metrics"] = json.load(f)
        
        return data

# Utilidad para generar datos on-the-fly
def get_simulated_analytics(repo_path: str = "/workspaces/master") -> Dict[str, Any]:
    """Obtener analytics simulados (genera si no existen)"""
    
    simulator = DocumentationDataSimulator(repo_path)
    
    # Intentar cargar datos existentes
    data = simulator.load_simulated_data("analytics")
    
    if "analytics" not in data:
        # Generar nuevos datos
        analytics = simulator.generate_usage_analytics()
        return analytics
    
    return data["analytics"]

def get_simulated_health(repo_path: str = "/workspaces/master") -> Dict[str, Any]:
    """Obtener health metrics simulados"""
    
    simulator = DocumentationDataSimulator(repo_path)
    
    data = simulator.load_simulated_data("health")
    
    if "health" not in data:
        health = simulator.generate_system_health()
        return health
    
    return data["health"]

# CLI para generar datos
def main():
    """Función principal para generar datos desde CLI"""
    
    print("🎭 Documentation Data Simulator")
    print("=" * 40)
    
    simulator = DocumentationDataSimulator()
    
    try:
        # Generar y guardar todos los datos
        all_data = simulator.save_simulated_data()
        
        print(f"\n📈 Resumen de datos generados:")
        print(f"   📊 Analytics: {len(all_data['analytics']['popular_documents'])} documentos")
        print(f"   🏥 Health Score: {all_data['health']['overall_score']:.1f}/100")
        print(f"   💻 Código: {all_data['code_analysis']['files_analyzed']} archivos analizados")
        print(f"   📝 Uso: {len(all_data['usage_metrics'])} documentos trackeados")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generando datos simulados: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())