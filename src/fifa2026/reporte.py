"""Generación del reporte de predicciones en Markdown."""

from . import ajustes, clima, poisson, valor

SIGNOS = {"1": "Gana local", "X": "Empate", "2": "Gana visitante"}


def analizar_partido(partido, equipos, estadios, overrides, h2h, cuotas):
    estadio = estadios[partido["estadio_id"]]
    condiciones = clima.clima_del_partido(partido, estadio, overrides)
    local, visita = partido["local"], partido["visitante"]

    elo_l, razones_l = ajustes.elo_ajustado(local, equipos[local], estadio, True)
    elo_v, razones_v = ajustes.elo_ajustado(visita, equipos[visita], estadio, False)
    total, razones_total = ajustes.total_goles_ajustado(estadio, condiciones)
    pred = poisson.predecir(elo_l, elo_v, total)

    analisis_valor = None
    if partido["match_id"] in cuotas:
        analisis_valor = valor.analizar_mercado(
            {"1": pred["p1"], "X": pred["px"], "2": pred["p2"]},
            cuotas[partido["match_id"]])
        analisis_valor["fuente"] = cuotas[partido["match_id"]]["fuente"]

    return {
        "partido": partido, "estadio": estadio, "clima": condiciones,
        "elo_local": elo_l, "elo_visitante": elo_v,
        "razones_local": razones_l, "razones_visitante": razones_v,
        "total_goles": total, "razones_total": razones_total,
        "prediccion": pred,
        "h2h": h2h.get(f"{local} vs {visita}", []),
        "valor": analisis_valor,
    }


def seccion_partido(a):
    p, e, c, pred = a["partido"], a["estadio"], a["clima"], a["prediccion"]
    lineas = [
        f"### {p['local']} vs {p['visitante']} — {p['fase']} ({p['match_id']})",
        "",
        f"- **Fecha:** {p['fecha']} {p['hora_local']} (hora local)",
        f"- **Estadio:** {e['nombre']}, {e['ciudad']} ({e['pais']}) — "
        f"{e['capacidad']:,} espectadores, altitud {e['altitud_m']} m, techo {e['techo']}",
        f"- **Clima previsto:** {c['temp_c']:.0f} °C"
        + (f", humedad {c['humedad_pct']:.0f} %" if c["humedad_pct"] else "")
        + f", viento {c['viento_kmh']:.0f} km/h, precipitación: {c['lluvia']}"
        + f" _(fuente: {c['fuente']})_",
    ]
    if p["notas"]:
        lineas.append(f"- **Nota:** {p['notas']}")
    for antecedente in a["h2h"]:
        lineas.append(f"- **Historial en mundiales:** {antecedente}")

    lineas += [
        "",
        f"**Fuerza ajustada:** {p['local']} {a['elo_local']:.0f} "
        f"({', '.join(a['razones_local']) or 'sin ajustes'}) · "
        f"{p['visitante']} {a['elo_visitante']:.0f} "
        f"({', '.join(a['razones_visitante']) or 'sin ajustes'})",
        f"**Goles esperados:** {pred['lambda_local']:.2f} - {pred['lambda_visitante']:.2f}"
        + (f" _(ajustes al total: {', '.join(a['razones_total'])})_"
           if a["razones_total"] else ""),
        "",
        "| Mercado | Probabilidad | Cuota justa |",
        "|---|---|---|",
        f"| Gana {p['local']} (90') | {pred['p1']:.1%} | {1/pred['p1']:.2f} |",
        f"| Empate (90') | {pred['px']:.1%} | {1/pred['px']:.2f} |",
        f"| Gana {p['visitante']} (90') | {pred['p2']:.1%} | {1/pred['p2']:.2f} |",
        f"| {p['local']} clasifica | {pred['avanza_local']:.1%} | {1/pred['avanza_local']:.2f} |",
        f"| {p['visitante']} clasifica | {pred['avanza_visitante']:.1%} | {1/pred['avanza_visitante']:.2f} |",
        f"| Más de 2.5 goles | {pred['over25']:.1%} | {1/pred['over25']:.2f} |",
        f"| Menos de 2.5 goles | {pred['under25']:.1%} | {1/pred['under25']:.2f} |",
        f"| Ambos marcan | {pred['btts']:.1%} | {1/pred['btts']:.2f} |",
        "",
        "**Marcadores más probables:** "
        + " · ".join(f"{x}-{y} ({prob:.1%})" for (x, y), prob in pred["marcadores_top"]),
    ]

    if a["valor"]:
        v = a["valor"]
        lineas += [
            "",
            f"**Análisis de valor** (cuotas: {v['fuente']}; "
            f"margen de la casa {v['margen_casa']:.1%}):",
            "",
            "| Signo | Prob. modelo | Cuota justa | Cuota mercado | EV | Kelly 25 % |",
            "|---|---|---|---|---|---|",
        ]
        for s in v["selecciones"]:
            marca = " ⭐ **VALOR**" if s["apostar"] else ""
            lineas.append(
                f"| {SIGNOS[s['signo']]} | {s['prob_modelo']:.1%} | "
                f"{s['cuota_justa']:.2f} | {s['cuota_mercado']:.2f} | "
                f"{s['ev']:+.1%}{marca} | {s['kelly_pct']:.1f} % del bank |")
    lineas.append("")
    return "\n".join(lineas)


def seccion_simulacion(resultados, equipos):
    orden = sorted(resultados.items(),
                   key=lambda kv: kv[1].get("campeon", 0), reverse=True)
    lineas = [
        "## Simulación Monte Carlo del torneo (20 000 iteraciones)",
        "",
        "| Equipo | Cuartos | Semifinal | Final | Campeón | Cuota justa campeón |",
        "|---|---|---|---|---|---|",
    ]
    for eq, h in orden:
        pc = h.get("campeon", 0)
        cuota = f"{1/pc:.1f}" if pc > 0 else "—"
        lineas.append(
            f"| {eq} | {h.get('cuartos', 0):.1%} | {h.get('semifinal', 0):.1%} "
            f"| {h.get('final', 0):.1%} | {pc:.1%} | {cuota} |")
    lineas.append("")
    return "\n".join(lineas)
