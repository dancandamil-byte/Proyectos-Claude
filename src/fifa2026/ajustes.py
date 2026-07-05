"""Ajustes contextuales al rating y al total de goles esperado.

Cada ajuste devuelve puntos Elo (fuerza relativa) o goles (ritmo del partido),
y una lista de explicaciones legibles para el reporte.
"""

BONUS_ANFITRION = {"México": 85, "Estados Unidos": 50, "Canadá": 50}
BONUS_ALTITUD_ELO = 35      # equipo aclimatado en estadio a más de 1500 m
UMBRAL_ALTITUD_M = 1500

TOTAL_BASE_ELIMINATORIA = 2.45   # goles esperados en 90' en eliminatorias de mundial


def elo_ajustado(equipo, datos_eq, estadio, es_local_del_cuadro):
    """Elo efectivo del equipo para este partido concreto."""
    razones = []
    elo = datos_eq["elo"] + datos_eq["forma"]
    if datos_eq["forma"]:
        razones.append(f"forma en el torneo {datos_eq['forma']:+.0f}")

    pais_estadio = estadio["pais"]
    es_anfitrion_en_casa = (
        datos_eq["anfitrion"]
        and equipo in BONUS_ANFITRION
        and (
            (equipo == "México" and pais_estadio == "México")
            or (equipo == "Estados Unidos" and pais_estadio == "Estados Unidos")
            or (equipo == "Canadá" and pais_estadio == "Canadá")
        )
    )
    if es_anfitrion_en_casa:
        elo += BONUS_ANFITRION[equipo]
        razones.append(f"anfitrión en casa {BONUS_ANFITRION[equipo]:+d}")

    if estadio["altitud_m"] >= UMBRAL_ALTITUD_M and datos_eq["altitud"]:
        elo += BONUS_ALTITUD_ELO
        razones.append(
            f"aclimatado a la altitud ({estadio['altitud_m']} m) {BONUS_ALTITUD_ELO:+d}")

    return elo, razones


def total_goles_ajustado(estadio, clima):
    """Total de goles esperado en 90', ajustado por clima y altitud."""
    total = TOTAL_BASE_ELIMINATORIA
    razones = []
    if clima["temp_c"] >= 33:
        total -= 0.15
        razones.append("calor extremo (-0.15 goles)")
    elif clima["temp_c"] >= 30:
        total -= 0.10
        razones.append("calor fuerte (-0.10 goles)")
    if clima["lluvia"] == "storm":
        total -= 0.10
        razones.append("tormenta / campo pesado (-0.10 goles)")
    elif clima["lluvia"] == "rain":
        total -= 0.05
        razones.append("lluvia (-0.05 goles)")
    if estadio["altitud_m"] >= 2000:
        total += 0.10
        razones.append("altitud >2000 m: balón más rápido (+0.10 goles)")
    return total, razones
