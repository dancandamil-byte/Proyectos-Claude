"""Detección de valor: cuotas justas, EV y criterio de Kelly fraccionado."""

KELLY_FRACCION = 0.25   # Kelly al 25 %: reduce varianza y el impacto de errores del modelo
EV_MINIMO = 0.03        # solo se recomienda apostar con ventaja esperada >= 3 %


def analizar_mercado(probs, cuotas):
    """probs: {'1': p, 'X': p, '2': p}; cuotas: {'1': c, 'X': c, '2': c}."""
    resultados = []
    margen = sum(1 / cuotas[s] for s in ("1", "X", "2")) - 1
    for signo in ("1", "X", "2"):
        p, c = probs[signo], cuotas[signo]
        ev = p * c - 1
        kelly = max(0.0, (p * c - 1) / (c - 1)) if c > 1 else 0.0
        resultados.append({
            "signo": signo,
            "prob_modelo": p,
            "cuota_justa": 1 / p if p > 0 else float("inf"),
            "cuota_mercado": c,
            "ev": ev,
            "kelly_pct": kelly * KELLY_FRACCION * 100,
            "apostar": ev >= EV_MINIMO,
        })
    return {"margen_casa": margen, "selecciones": resultados}
