"""
Tests automáticos para MetaAdsBudgetOptimizer y el endpoint /api/v1/meta_ads/optimize
"""
import pytest
from fastapi.testclient import TestClient
from ml_core.api.main import app
from ml_core.optimizers.meta_ads_budget_optimizer import MetaAdsBudgetOptimizer
import numpy as np

client = TestClient(app)

def test_optimizer_logic():
    optimizer = MetaAdsBudgetOptimizer(P_total=1000, LTV_suscriptor=10)
    assert optimizer.P_clip == 80
    assert optimizer.P_fase2 == 300
    assert optimizer.cps_max() == 4
    assert optimizer.early_stop_clip(0.3, 0.01, 20) is True
    asignaciones = optimizer.bayesian_allocation(300, np.array([0.6, 0.3, 0.1]), alpha=2)
    assert np.isclose(sum(asignaciones), 300)
    assert optimizer.escalado_increment(1.9) == 0.30
    assert optimizer.escalado_increment(1.6) == 0.20
    assert optimizer.escalado_increment(1.3) == 0.10
    assert optimizer.escalado_increment(1.1) == 0.0

def test_api_optimize_budget():
    payload = {
        "P_total": 1000,
        "LTV_suscriptor": 10,
        "roas_acum": 1.6,
        "roas_48h": 1.7,
        "cpv": 0.12,
        "ctr": 0.03,
        "gasto": 25,
        "freq": 1.5,
        "P_opt": [0.5, 0.3, 0.2],
        "metricas_ml": {"ctr": 0.03, "cpv": 0.12, "roas": 1.5, "freq": 1.5}
    }
    response = client.post("/api/v1/meta_ads/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "early_stop" in data
    assert "daily_limit" in data
    assert "cps_max" in data
    assert "escalado_increment" in data
    assert "bayesian_allocation" in data
    assert "roas_ajustado" in data
    assert "multiobjective_loss" in data
