#!/usr/bin/env python3
"""
Strategic Branch Analysis & Deployment Script
Analyzes and deploys the most efficient branch based on bandwidth constraints
"""

import os
import sys
import subprocess
import json
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class BranchMetrics:
    """Metrics for branch efficiency analysis"""
    name: str
    bandwidth_reduction: float
    memory_reduction: float
    startup_speedup: float
    deployment_size_mb: float
    target_environment: str
    resource_requirements: Dict[str, str]
    optimization_features: List[str]

class BandwidthOptimizationAnalyzer:
    """Analyzes and recommends optimal branch based on constraints"""
    
    def __init__(self):
        self.branches = self._initialize_branch_metrics()
        self.current_branch = self._get_current_branch()
    
    def _initialize_branch_metrics(self) -> Dict[str, BranchMetrics]:
        """Initialize metrics for all optimized branches"""
        return {
            "bandwidth-optimized": BranchMetrics(
                name="bandwidth-optimized",
                bandwidth_reduction=70.0,
                memory_reduction=60.0,
                startup_speedup=80.0,
                deployment_size_mb=500,
                target_environment="Low bandwidth networks",
                resource_requirements={
                    "RAM": "1-2GB",
                    "CPU": "2-4 cores", 
                    "Storage": "2-5GB",
                    "Bandwidth": "1-10 Mbps"
                },
                optimization_features=[
                    "CPU-only ML inference",
                    "Quantized models",
                    "Compressed image processing", 
                    "Aggressive HTTP caching",
                    "SQLite memory database",
                    "Minimal dependencies"
                ]
            ),
            
            "edge-deployment": BranchMetrics(
                name="edge-deployment",
                bandwidth_reduction=75.0,
                memory_reduction=65.0,
                startup_speedup=85.0,
                deployment_size_mb=200,
                target_environment="IoT/Edge devices",
                resource_requirements={
                    "RAM": "512MB-1GB",
                    "CPU": "1-2 cores",
                    "Storage": "1-3GB", 
                    "Bandwidth": "0.5-5 Mbps"
                },
                optimization_features=[
                    "Alpine Linux base",
                    "ARM architecture ready",
                    "Offline-first operation",
                    "Local SQLite database",
                    "Minimal container orchestra",
                    "Edge-optimized health checks"
                ]
            ),
            
            "micro-services": BranchMetrics(
                name="micro-services", 
                bandwidth_reduction=60.0,
                memory_reduction=50.0,
                startup_speedup=70.0,
                deployment_size_mb=150,
                target_environment="Distributed systems",
                resource_requirements={
                    "RAM": "4-8GB total",
                    "CPU": "8-16 cores total",
                    "Storage": "10-20GB",
                    "Bandwidth": "10-100 Mbps"
                },
                optimization_features=[
                    "Multi-stage Docker builds",
                    "Service mesh ready",
                    "Horizontal scaling",
                    "Load balancing",
                    "Service discovery", 
                    "Circuit breakers"
                ]
            ),
            
            "device-farm-v5-integration": BranchMetrics(
                name="device-farm-v5-integration",
                bandwidth_reduction=0.0,  # Baseline
                memory_reduction=0.0,     # Baseline
                startup_speedup=0.0,      # Baseline
                deployment_size_mb=2000,  # Full version
                target_environment="High-resource production",
                resource_requirements={
                    "RAM": "8-16GB",
                    "CPU": "16-32 cores",
                    "Storage": "50-100GB",
                    "Bandwidth": "100+ Mbps"
                },
                optimization_features=[
                    "Full feature set",
                    "GPU acceleration",
                    "Complete monitoring stack",
                    "Advanced ML models",
                    "Full device farm integration"
                ]
            )
        }
    
    def _get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"
    
    def analyze_bandwidth_requirements(self, max_bandwidth_mbps: float) -> str:
        """Recommend best branch based on bandwidth constraints"""
        
        print(f"🔍 Analyzing bandwidth requirements: {max_bandwidth_mbps} Mbps")
        
        # Bandwidth-based recommendations
        if max_bandwidth_mbps <= 1:
            return "edge-deployment"
        elif max_bandwidth_mbps <= 5:
            return "bandwidth-optimized"  
        elif max_bandwidth_mbps <= 20:
            return "micro-services"
        else:
            return "device-farm-v5-integration"
    
    def analyze_resource_constraints(self, 
                                   max_ram_gb: float, 
                                   max_cpu_cores: int,
                                   max_storage_gb: float) -> str:
        """Recommend best branch based on resource constraints"""
        
        print(f"💻 Analyzing resource constraints:")
        print(f"   • RAM: {max_ram_gb}GB")
        print(f"   • CPU: {max_cpu_cores} cores")
        print(f"   • Storage: {max_storage_gb}GB")
        
        # Resource-based recommendations
        if max_ram_gb <= 1 or max_cpu_cores <= 2:
            return "edge-deployment"
        elif max_ram_gb <= 4 or max_cpu_cores <= 8:
            return "bandwidth-optimized"
        elif max_ram_gb <= 8 or max_cpu_cores <= 16:
            return "micro-services"
        else:
            return "device-farm-v5-integration"
    
    def get_optimal_branch(self, 
                          bandwidth_mbps: float = 10.0,
                          ram_gb: float = 4.0,
                          cpu_cores: int = 4,
                          storage_gb: float = 20.0) -> str:
        """Get optimal branch based on all constraints"""
        
        print("="*80)
        print("🎯 STRATEGIC BRANCH ANALYSIS")
        print("="*80)
        
        # Analyze each constraint
        bandwidth_recommendation = self.analyze_bandwidth_requirements(bandwidth_mbps)
        resource_recommendation = self.analyze_resource_constraints(
            ram_gb, cpu_cores, storage_gb
        )
        
        # Priority: bandwidth is usually the most limiting factor
        recommendations = [bandwidth_recommendation, resource_recommendation]
        
        # Find the most restrictive (edge > bandwidth > micro > full)
        priority_order = [
            "edge-deployment",
            "bandwidth-optimized", 
            "micro-services",
            "device-farm-v5-integration"
        ]
        
        for branch in priority_order:
            if branch in recommendations:
                optimal_branch = branch
                break
        else:
            optimal_branch = "bandwidth-optimized"  # Default fallback
        
        print(f"\n🎯 OPTIMAL BRANCH: {optimal_branch}")
        return optimal_branch
    
    def display_branch_comparison(self):
        """Display detailed comparison of all branches"""
        
        print("\n" + "="*100)
        print("📊 COMPREHENSIVE BRANCH COMPARISON")
        print("="*100)
        
        # Table header
        print(f"{'Branch':<25} {'Bandwidth ↓':<12} {'Memory ↓':<10} {'Startup ↑':<10} {'Size (MB)':<10} {'Target Environment':<25}")
        print("-" * 100)
        
        # Table rows
        for branch_name, metrics in self.branches.items():
            print(f"{branch_name:<25} {metrics.bandwidth_reduction:>8.0f}% "
                  f"{metrics.memory_reduction:>6.0f}% {metrics.startup_speedup:>6.0f}% "
                  f"{metrics.deployment_size_mb:>7.0f} {metrics.target_environment:<25}")
        
        print("\n" + "="*100)
    
    def display_detailed_analysis(self, branch_name: str):
        """Display detailed analysis for specific branch"""
        
        if branch_name not in self.branches:
            print(f"❌ Branch '{branch_name}' not found")
            return
        
        metrics = self.branches[branch_name]
        
        print(f"\n🔍 DETAILED ANALYSIS: {branch_name.upper()}")
        print("="*60)
        print(f"🎯 Target Environment: {metrics.target_environment}")
        print(f"📊 Performance Improvements:")
        print(f"   • Bandwidth reduction: {metrics.bandwidth_reduction}%")
        print(f"   • Memory reduction: {metrics.memory_reduction}%") 
        print(f"   • Startup speedup: {metrics.startup_speedup}%")
        print(f"   • Deployment size: {metrics.deployment_size_mb}MB")
        
        print(f"\n💻 Resource Requirements:")
        for resource, requirement in metrics.resource_requirements.items():
            print(f"   • {resource}: {requirement}")
        
        print(f"\n⚡ Optimization Features:")
        for feature in metrics.optimization_features:
            print(f"   ✅ {feature}")
    
    def deploy_optimal_branch(self, branch_name: str, deployment_mode: str = "docker"):
        """Deploy the optimal branch"""
        
        print(f"\n🚀 DEPLOYING BRANCH: {branch_name}")
        print("="*50)
        
        try:
            # Checkout optimal branch
            print(f"📦 Switching to branch: {branch_name}")
            subprocess.run(["git", "checkout", branch_name], check=True)
            
            # Deploy based on branch type
            if branch_name == "edge-deployment":
                self._deploy_edge(deployment_mode)
            elif branch_name == "bandwidth-optimized":
                self._deploy_bandwidth_optimized(deployment_mode)
            elif branch_name == "micro-services":
                self._deploy_microservices(deployment_mode)
            else:
                self._deploy_full_version(deployment_mode)
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            return False
        
        return True
    
    def _deploy_edge(self, mode: str):
        """Deploy edge-optimized version"""
        print("🏭 Deploying Edge-Optimized Version...")
        
        if mode == "docker":
            cmd = ["docker-compose", "-f", "docker-compose.edge.yml", "up", "-d"]
        else:
            cmd = ["python", "scripts/bandwidth_launcher.py", "--edge-mode"]
        
        subprocess.run(cmd, check=True)
        print("✅ Edge deployment completed")
    
    def _deploy_bandwidth_optimized(self, mode: str):
        """Deploy bandwidth-optimized version"""
        print("🌐 Deploying Bandwidth-Optimized Version...")
        
        # Apply bandwidth optimizations
        subprocess.run(["python", "config/bandwidth_optimization.py"], check=True)
        
        if mode == "docker":
            cmd = ["docker-compose", "-f", "docker-compose.v6.yml", "up", "-d"] 
        else:
            cmd = ["python", "device_farm_v5/src/main.py", "--bandwidth-mode"]
        
        subprocess.run(cmd, check=True)
        print("✅ Bandwidth-optimized deployment completed")
    
    def _deploy_microservices(self, mode: str):
        """Deploy microservices version"""  
        print("🔧 Deploying Microservices Version...")
        
        if mode == "docker":
            cmd = ["docker-compose", "-f", "docker-compose.v6.yml", "up", "-d"]
        else:
            cmd = ["python", "device_farm_v5/src/main.py", "--micro-services"]
            
        subprocess.run(cmd, check=True)
        print("✅ Microservices deployment completed")
    
    def _deploy_full_version(self, mode: str):
        """Deploy full-featured version"""
        print("🚀 Deploying Full-Featured Version...")
        
        if mode == "docker":
            cmd = ["docker-compose", "-f", "docker-compose.v4.yml", "up", "-d"]
        else:
            cmd = ["python", "device_farm_v5/src/main.py", "--full-features"]
            
        subprocess.run(cmd, check=True)
        print("✅ Full version deployment completed")

def main():
    """Main entry point for strategic deployment"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                      🎯 STRATEGIC BRANCH ANALYZER V6                           ║  
║                                                                                  ║
║  Intelligent branch selection based on bandwidth and resource constraints       ║
║  • bandwidth-optimized: 70% bandwidth reduction                                 ║
║  • edge-deployment: 75% bandwidth reduction + IoT ready                        ║
║  • micro-services: Distributed architecture                                     ║
║  • device-farm-v5-integration: Full-featured production                        ║
║                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝
    """)
    
    analyzer = BandwidthOptimizationAnalyzer()
    
    # Display branch comparison
    analyzer.display_branch_comparison()
    
    # Interactive mode
    print("\n🔧 DEPLOYMENT CONFIGURATION")
    print("-" * 40)
    
    try:
        bandwidth = float(input("📊 Available bandwidth (Mbps): ") or "10")
        ram = float(input("💻 Available RAM (GB): ") or "4") 
        cpu = int(input("⚙️  Available CPU cores: ") or "4")
        storage = float(input("💾 Available storage (GB): ") or "20")
        
        # Analyze and recommend
        optimal_branch = analyzer.get_optimal_branch(bandwidth, ram, cpu, storage)
        
        # Show detailed analysis
        analyzer.display_detailed_analysis(optimal_branch)
        
        # Deploy option
        deploy = input(f"\n🚀 Deploy {optimal_branch}? (y/N): ").lower() == 'y'
        
        if deploy:
            mode = input("📦 Deployment mode (docker/native): ") or "docker"
            success = analyzer.deploy_optimal_branch(optimal_branch, mode)
            
            if success:
                print("\n🎉 DEPLOYMENT SUCCESSFUL!")
                print(f"🌐 Access dashboard at: http://localhost:5000")
                print(f"📊 Monitoring at: http://localhost:3000")
            else:
                print("\n❌ DEPLOYMENT FAILED")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Analysis interrupted by user")
    except ValueError:
        print("\n❌ Invalid input. Using defaults...")
        optimal_branch = analyzer.get_optimal_branch()
        analyzer.display_detailed_analysis(optimal_branch)

if __name__ == "__main__":
    main()