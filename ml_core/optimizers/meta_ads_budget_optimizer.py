"""
Algoritmo de optimización matemática de presupuesto y rentabilidad para campañas de Meta Ads.
Basado en el mandato de la rama promocion. Listo para ser optimizado y extendido por modelos ML (Ultralytics, CatBoost, etc).
"""
import numpy as np

class MetaAdsBudgetOptimizer:
    def __init__(self, P_total, LTV_suscriptor=10.0):
        self.P_total = P_total
        self.LTV_suscriptor = LTV_suscriptor
        self.P_reserva = P_total * 0.10
        self.P_fase2 = P_total * 0.30
        self.P_clip = P_total * 0.08
        self.P_min_clip = 20

    def early_stop_clip(self, cpv, ctr, gasto):
        """Condición de parada temprana por bajo rendimiento de un clip."""
        return gasto >= 15 and (cpv > 0.25 and ctr < 0.015)

    def daily_spend_limit_fase2(self, roas_acum):
        if roas_acum >= 1.5:
            return self.P_fase2 / 3
        elif 1.0 <= roas_acum < 1.5:
            return self.P_fase2 / 4
        elif 0.8 <= roas_acum < 1.0:
            return self.P_fase2 / 6
        else:
            return 0  # Pausar campañas

    def cps_max(self):
        return self.LTV_suscriptor * 0.4

    def escalado_increment(self, roas_48h):
        if roas_48h > 1.8:
            return 0.30
        elif 1.5 < roas_48h <= 1.8:
            return 0.20
        elif 1.2 < roas_48h <= 1.5:
            return 0.10
        else:
            return 0.0

    def bayesian_allocation(self, P_disponible, P_opt, alpha=2):
        numeradores = np.power(P_opt, alpha)
        return P_disponible * numeradores / np.sum(numeradores)

    def break_even(self, P_fase, ctr_esp, cr_esp, valor_conv):
        return P_fase / (ctr_esp * cr_esp * valor_conv)

    def ev_decision(self, escenarios):
        # escenarios: lista de tuplas (P, ROAS_esperado, rentabilidad)
        return sum(P * rent for (P, _, rent) in escenarios)

    def sigma_roas(self, P_list, ROAS_list):
        roas_medio = np.average(ROAS_list, weights=P_list)
        return np.sqrt(np.sum([P * (roas - roas_medio) ** 2 for P, roas in zip(P_list, ROAS_list)]))

    def roas_ajustado(self, roas_obs, sigma_roas, lambd=0.3):
        return roas_obs - (lambd * sigma_roas)

    def multiobjective_loss(self, cpv, ctr, roas, freq, w1=0.3, w2=0.25, w3=0.35, w4=0.1):
        return w1 * cpv + w2 * (1/ctr) + w3 * (1/roas) + w4 * freq

    def grad_desc_update(self, param, grad, eta):
        return param - eta * grad

# Ejemplo de uso:
if __name__ == "__main__":
    optimizer = MetaAdsBudgetOptimizer(P_total=1000, LTV_suscriptor=12)
    # Simulación de asignación bayesiana
    P_opt = np.array([0.6, 0.3, 0.1])
    asignaciones = optimizer.bayesian_allocation(300, P_opt, alpha=2)
    print("Asignación bayesiana:", asignaciones)
    # Cálculo de early stop
    print("Early stop:", optimizer.early_stop_clip(0.3, 0.01, 20))
    # Cálculo de ROAS ajustado
    print("ROAS ajustado:", optimizer.roas_ajustado(1.2, 0.6))
