from fastapi import APIRouter
from typing import Dict, Any, List
import random

router = APIRouter()

def generate_dummy_affinity_scores(account_ids: List[str]) -> Dict[str, float]:
    return {
        account_id: round(random.uniform(0.1, 1.0), 2)
        for account_id in account_ids
    }

@router.post("/calculate_affinity", response_model=Dict[str, Any])
async def calculate_affinity(
    data: Dict[str, Any]
) -> Dict[str, Any]:
    account_ids = data.get("account_ids", [])
    if not account_ids:
        account_ids = [f"dummy_account_{i}" for i in range(5)]
        
    return {
        "affinity_scores": generate_dummy_affinity_scores(account_ids),
        "engagement_recommendations": [
            {
                "account_id": acc_id,
                "recommended_actions": random.sample([
                    "like", "follow", "comment", "share", "watch_full"
                ], k=random.randint(1, 3)),
                "engagement_score": round(random.uniform(0.5, 0.95), 2)
            }
            for acc_id in account_ids
        ],
        "cluster_info": {
            "cluster_id": random.randint(1, 5),
            "cluster_size": random.randint(10, 30),
            "cluster_theme": random.choice([
                "music", "dance", "comedy", "lifestyle", "gaming"
            ])
        }
    }