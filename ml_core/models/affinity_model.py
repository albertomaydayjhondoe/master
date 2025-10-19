from typing import Dict, List
import random

class AffinityModel:
    """Dummy affinity model that scores account pairs.

    Replace with a model that computes real affinity matrices from embeddings.
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path

    def score(self, account_ids: List[str]) -> Dict[str, float]:
        return {aid: round(random.uniform(0.1, 1.0), 2) for aid in account_ids}
