from fastapi import APIRouter
from typing import Dict, Any, List
import random
from datetime import datetime, timedelta

router = APIRouter()

def generate_dummy_time_slots() -> List[Dict[str, Any]]:
    now = datetime.now()
    time_slots = []
    
    for hour in range(24):
        score = random.uniform(0.1, 1.0)
        # Prime times get higher scores
        if hour in [9, 10, 18, 19, 20]:
            score = random.uniform(0.7, 1.0)
            
        time_slots.append({
            "hour": hour,
            "score": round(score, 2),
            "estimated_reach": int(score * random.randint(1000, 10000)),
            "confidence": round(random.uniform(0.6, 0.95), 2)
        })
    
    return time_slots

@router.post("/predict_posting_time", response_model=Dict[str, Any])
async def predict_posting_time(
    data: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "best_times": generate_dummy_time_slots(),
        "recommended_next_post": {
            "timestamp": (datetime.now() + timedelta(hours=random.randint(1, 8))).isoformat(),
            "confidence": round(random.uniform(0.7, 0.95), 2),
            "estimated_views": random.randint(5000, 50000)
        },
        "account_momentum": round(random.uniform(0.3, 0.9), 2),
        "daily_post_limit": random.randint(2, 4)
    }