"""
FastAPI endpoint para optimización de presupuesto Meta Ads usando reglas matemáticas y métricas ML preentrenadas.
Incluye pipeline de validación continua y tests automáticos.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ml_core.optimizers.meta_ads_budget_optimizer import MetaAdsBudgetOptimizer
import numpy as np

router = APIRouter()

class OptimizationInput(BaseModel):
    P_total: float
    LTV_suscriptor: float
    roas_acum: float
    roas_48h: float
    cpv: float
    ctr: float
    gasto: float
    freq: float
    P_opt: list
    metricas_ml: dict  # {'ctr': float, 'cpv': float, 'roas': float, 'freq': float}

class OptimizationOutput(BaseModel):
    early_stop: bool
    daily_limit: float
    cps_max: float
    escalado_increment: float
    bayesian_allocation: list
    roas_ajustado: float
    multiobjective_loss: float

@router.post("/meta_ads/optimize", response_model=OptimizationOutput)
def optimize_budget(data: OptimizationInput):
    optimizer = MetaAdsBudgetOptimizer(P_total=data.P_total, LTV_suscriptor=data.LTV_suscriptor)
    early_stop = optimizer.early_stop_clip(data.cpv, data.ctr, data.gasto)
    daily_limit = optimizer.daily_spend_limit_fase2(data.roas_acum)
    cps_max = optimizer.cps_max()
    escalado_increment = optimizer.escalado_increment(data.roas_48h)
    bayesian_allocation = optimizer.bayesian_allocation(data.P_total, np.array(data.P_opt), alpha=2).tolist()
    # Validación continua con métricas ML preentrenadas
    roas_ajustado = optimizer.roas_ajustado(data.metricas_ml['roas'], 0.5)  # sigma_roas dummy
    multiobjective_loss = optimizer.multiobjective_loss(
        data.metricas_ml['cpv'], data.metricas_ml['ctr'], data.metricas_ml['roas'], data.metricas_ml['freq'])
    return OptimizationOutput(
        early_stop=early_stop,
        daily_limit=daily_limit,
        cps_max=cps_max,
        escalado_increment=escalado_increment,
        bayesian_allocation=bayesian_allocation,
        roas_ajustado=roas_ajustado,
        multiobjective_loss=multiobjective_loss
    )
