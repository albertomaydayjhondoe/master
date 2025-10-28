"""
Database Mock Infrastructure for Simulation
Provides simulated database functions to avoid external dependencies during testing.
"""

import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
import numpy as np


class MockDatabase:
    """Mock database for simulation purposes"""
    
    def __init__(self):
        self.campaigns = {}
        self.metrics = {}
        self.clips = {}
        self.users = {}
        print("🗃️ [SIM] Mock database initialized")
    
    def store_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]):
        """Store campaign data"""
        self.campaigns[campaign_id] = {
            **campaign_data,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        print(f"💾 [SIM] Stored campaign: {campaign_id}")
    
    def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Retrieve campaign data"""
        return self.campaigns.get(campaign_id, {})
    
    def store_metrics(self, campaign_id: str, metrics: Dict[str, Any]):
        """Store campaign metrics"""
        if campaign_id not in self.metrics:
            self.metrics[campaign_id] = []
        
        metrics['timestamp'] = datetime.now()
        self.metrics[campaign_id].append(metrics)
        print(f"📊 [SIM] Stored metrics for: {campaign_id}")
    
    def get_metrics(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Retrieve campaign metrics"""
        return self.metrics.get(campaign_id, [])


# Global mock database instance
_mock_db = MockDatabase()


def get_clip_metrics(clip_id: str) -> Dict[str, Any]:
    """
    Get clip performance metrics
    Returns simulated metrics for testing without external API calls
    """
    print(f"📈 [SIM] Getting metrics for clip: {clip_id}")
    
    # Simulate realistic TikTok metrics
    base_performance = np.random.uniform(0.8, 1.2)  # Performance multiplier
    
    metrics = {
        "clip_id": clip_id,
        "CTR": round(0.035 * base_performance, 4),  # 3.5% base CTR
        "CPV": round(0.08 * (2 - base_performance), 3),  # Lower CPV = better performance
        "watch_time": round(15.0 * base_performance, 1),  # Average watch time
        "conversions": int(5 * base_performance),
        "views": int(np.random.randint(1000, 50000) * base_performance),
        "likes": int(np.random.randint(50, 2000) * base_performance),
        "shares": int(np.random.randint(10, 500) * base_performance),
        "comments": int(np.random.randint(5, 200) * base_performance),
        "engagement_rate": round(np.random.uniform(0.02, 0.08) * base_performance, 4),
        "completion_rate": round(np.random.uniform(0.3, 0.7) * base_performance, 3),
        "timestamp": datetime.now().isoformat(),
        "simulation": True
    }
    
    # Store in mock database
    _mock_db.store_metrics(clip_id, metrics)
    
    print(f"✅ [SIM] Metrics: CTR={metrics['CTR']}, CPV=${metrics['CPV']}, Views={metrics['views']:,}")
    return metrics


def get_campaign_performance(campaign_id: str, days: int = 7) -> Dict[str, Any]:
    """Get campaign performance over time period"""
    print(f"📊 [SIM] Getting campaign performance: {campaign_id} ({days} days)")
    
    # Generate daily performance data
    daily_data = []
    base_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        date = base_date + timedelta(days=day)
        performance_trend = 1 + (day * 0.1)  # Improving trend
        
        daily_metrics = {
            "date": date.strftime("%Y-%m-%d"),
            "spend": round(np.random.uniform(50, 200) * performance_trend, 2),
            "impressions": int(np.random.randint(5000, 25000) * performance_trend),
            "clicks": int(np.random.randint(100, 1000) * performance_trend),
            "conversions": int(np.random.randint(5, 50) * performance_trend),
            "revenue": round(np.random.uniform(200, 800) * performance_trend, 2)
        }
        daily_data.append(daily_metrics)
    
    # Calculate aggregated metrics
    total_spend = sum(d["spend"] for d in daily_data)
    total_revenue = sum(d["revenue"] for d in daily_data)
    total_conversions = sum(d["conversions"] for d in daily_data)
    
    performance = {
        "campaign_id": campaign_id,
        "period_days": days,
        "daily_data": daily_data,
        "totals": {
            "spend": round(total_spend, 2),
            "revenue": round(total_revenue, 2),
            "conversions": total_conversions,
            "roas": round(total_revenue / total_spend if total_spend > 0 else 0, 2),
            "cpa": round(total_spend / total_conversions if total_conversions > 0 else 0, 2)
        },
        "simulation": True
    }
    
    print(f"💰 [SIM] Campaign ROAS: {performance['totals']['roas']}x, CPA: ${performance['totals']['cpa']}")
    return performance


def get_user_data(user_id: str) -> Dict[str, Any]:
    """Get user profile and behavior data"""
    print(f"👤 [SIM] Getting user data: {user_id}")
    
    # Simulate user demographics
    countries = ['ES', 'MX', 'AR', 'CO', 'CL', 'PE']
    ages = [18, 25, 35, 45, 55]
    
    user_data = {
        "user_id": user_id,
        "country": np.random.choice(countries),
        "age": np.random.choice(ages),
        "gender": np.random.choice(['M', 'F', 'O']),
        "interests": np.random.choice([
            'Technology', 'Fashion', 'Sports', 'Music', 'Food', 'Travel'
        ], size=np.random.randint(1, 4), replace=False).tolist(),
        "lifetime_value": round(np.random.uniform(10, 500), 2),
        "engagement_score": round(np.random.uniform(0.1, 1.0), 2),
        "is_follower": np.random.choice([True, False], p=[0.3, 0.7]),  # 30% followers
        "last_seen": (datetime.now() - timedelta(hours=np.random.randint(1, 72))).isoformat(),
        "simulation": True
    }
    
    return user_data


def save_optimization_result(campaign_id: str, optimization_data: Dict[str, Any]):
    """Save ML optimization results"""
    print(f"💾 [SIM] Saving optimization result for: {campaign_id}")
    
    optimization_record = {
        "campaign_id": campaign_id,
        "optimization_data": optimization_data,
        "applied_at": datetime.now().isoformat(),
        "simulation": True
    }
    
    # Store in mock database
    if not hasattr(_mock_db, 'optimizations'):
        _mock_db.optimizations = {}
    
    if campaign_id not in _mock_db.optimizations:
        _mock_db.optimizations[campaign_id] = []
    
    _mock_db.optimizations[campaign_id].append(optimization_record)
    print(f"✅ [SIM] Optimization saved - Actions: {len(optimization_data.get('actions', []))}")


def get_geographic_distribution() -> Dict[str, float]:
    """Get current geographic budget distribution"""
    return {
        "ES": 0.35,  # Spain: 35%
        "LATAM": 0.65  # Latin America: 65%
    }


def update_geographic_distribution(new_distribution: Dict[str, float]):
    """Update geographic distribution based on performance"""
    print(f"🌍 [SIM] Updating geographic distribution: {new_distribution}")
    
    # Simulate saving to database
    _mock_db.geo_distribution = {
        **new_distribution,
        "updated_at": datetime.now().isoformat(),
        "simulation": True
    }
    
    print(f"✅ [SIM] Geographic distribution updated")


# Export mock database for external access
def get_mock_database():
    """Get access to mock database instance"""
    return _mock_db


if __name__ == "__main__":
    # Test the mock database functions
    print("🧪 Testing mock database functions...")
    
    # Test clip metrics
    clip_metrics = get_clip_metrics("test_clip_001")
    print(f"Clip metrics: {json.dumps(clip_metrics, indent=2, default=str)}")
    
    # Test campaign performance
    campaign_perf = get_campaign_performance("test_campaign_001", 7)
    print(f"Campaign ROAS: {campaign_perf['totals']['roas']}x")
    
    # Test user data
    user = get_user_data("test_user_001")
    print(f"User from {user['country']}, age {user['age']}")
    
    print("✅ Mock database tests completed")