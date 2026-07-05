"""Modelo Poisson bivariado con corrección Dixon-Coles.

La diferencia de Elo ajustado se convierte en superioridad esperada de goles;
el total ajustado por clima/altitud fija el ritmo. La matriz de marcadores
produce probabilidades 1X2, más/menos 2.5, ambos marcan y marcadores exactos.
"""

import math

MAX_GOLES = 10
RHO_DIXON_COLES = -0.11
ELO_POR_GOL = 170.0          # puntos Elo equivalentes a 1 gol de superioridad
FACTOR_PRORROGA = 0.45       # la diferencia de fuerza pesa menos en prórroga/penales


def _poisson_pmf(k, lam):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def _tau(x, y, lam_l, lam_v, rho):
    """Corrección Dixon-Coles para marcadores bajos."""
    if x == 0 and y == 0:
        return 1 - lam_l * lam_v * rho
    if x == 0 and y == 1:
        return 1 + lam_l * rho
    if x == 1 and y == 0:
        return 1 + lam_v * rho
    if x == 1 and y == 1:
        return 1 - rho
    return 1.0


def lambdas_desde_elo(elo_local, elo_visitante, total_goles):
    diff = elo_local - elo_visitante
    superioridad = max(-2.5, min(2.5, diff / ELO_POR_GOL))
    lam_local = max(0.15, (total_goles + superioridad) / 2)
    lam_visitante = max(0.10, (total_goles - superioridad) / 2)
    return lam_local, lam_visitante


def matriz_marcadores(lam_local, lam_visitante):
    matriz = {}
    total = 0.0
    for x in range(MAX_GOLES + 1):
        for y in range(MAX_GOLES + 1):
            p = (_poisson_pmf(x, lam_local) * _poisson_pmf(y, lam_visitante)
                 * _tau(x, y, lam_local, lam_visitante, RHO_DIXON_COLES))
            matriz[(x, y)] = p
            total += p
    return {k: v / total for k, v in matriz.items()}


def prob_penales(elo_local, elo_visitante):
    """Probabilidad de que el local avance si se llega a prórroga/penales."""
    diff = (elo_local - elo_visitante) * FACTOR_PRORROGA
    return 1 / (1 + 10 ** (-diff / 400))


def predecir(elo_local, elo_visitante, total_goles):
    lam_l, lam_v = lambdas_desde_elo(elo_local, elo_visitante, total_goles)
    matriz = matriz_marcadores(lam_l, lam_v)

    p1 = sum(p for (x, y), p in matriz.items() if x > y)
    px = sum(p for (x, y), p in matriz.items() if x == y)
    p2 = sum(p for (x, y), p in matriz.items() if x < y)
    over25 = sum(p for (x, y), p in matriz.items() if x + y > 2.5)
    btts = sum(p for (x, y), p in matriz.items() if x > 0 and y > 0)

    p_pen = prob_penales(elo_local, elo_visitante)
    avanza_local = p1 + px * p_pen

    marcadores = sorted(matriz.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {
        "lambda_local": lam_l,
        "lambda_visitante": lam_v,
        "p1": p1, "px": px, "p2": p2,
        "over25": over25, "under25": 1 - over25, "btts": btts,
        "avanza_local": avanza_local, "avanza_visitante": 1 - avanza_local,
        "marcadores_top": marcadores,
        "matriz": matriz,
    }
