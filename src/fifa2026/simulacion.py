"""Simulación Monte Carlo del cuadro restante hasta la final."""

import random

from . import ajustes, clima, poisson


def _prob_avance(equipo_l, equipo_v, estadio, condiciones, equipos):
    elo_l, _ = ajustes.elo_ajustado(equipo_l, equipos[equipo_l], estadio, True)
    elo_v, _ = ajustes.elo_ajustado(equipo_v, equipos[equipo_v], estadio, False)
    total, _ = ajustes.total_goles_ajustado(estadio, condiciones)
    pred = poisson.predecir(elo_l, elo_v, total)
    return pred["avanza_local"]


def simular_torneo(partidos, equipos, estadios, overrides, n_sims=20000, semilla=42):
    """Devuelve, por equipo, la probabilidad de llegar a cada ronda y de ser campeón."""
    rng = random.Random(semilla)
    conteo = {}

    def anotar(equipo, hito):
        conteo.setdefault(equipo, {}).setdefault(hito, 0)
        conteo[equipo][hito] += 1

    # El clima por partido es fijo dentro de la simulación (media esperada)
    clima_por_partido = {
        p["match_id"]: clima.clima_del_partido(p, estadios[p["estadio_id"]], overrides)
        for p in partidos
    }

    for _ in range(n_sims):
        ganadores, perdedores = {}, {}
        for p in partidos:
            mid = p["match_id"]
            local = _resolver(p["local"], ganadores, perdedores)
            visita = _resolver(p["visitante"], ganadores, perdedores)

            if p["estado"] == "finalizado":
                # Se usa el campo "ganador" explícito (no el marcador) porque un
                # empate en 90'/prórroga puede resolverse por penales.
                gano_local = p["ganador"] == local
                ganadores[mid] = local if gano_local else visita
                perdedores[mid] = visita if gano_local else local
            else:
                prob_l = _prob_avance(local, visita, estadios[p["estadio_id"]],
                                      clima_por_partido[mid], equipos)
                if rng.random() < prob_l:
                    ganadores[mid], perdedores[mid] = local, visita
                else:
                    ganadores[mid], perdedores[mid] = visita, local

            hito = {"Octavos": "cuartos", "Cuartos": "semifinal",
                    "Semifinal": "final", "Final": "campeon"}.get(p["fase"])
            if hito:
                anotar(ganadores[mid], hito)

    return {
        eq: {hito: n / n_sims for hito, n in hitos.items()}
        for eq, hitos in conteo.items()
    }


def _resolver(ref, ganadores, perdedores):
    if ref.startswith("W:"):
        return ganadores[ref[2:]]
    if ref.startswith("L:"):
        return perdedores[ref[2:]]
    return ref
