#!/usr/bin/env python3
"""CLI del modelo de predicción del Mundial FIFA 2026.

Uso:
    python predict.py                # reporte completo (hoy + pendientes + simulación)
    python predict.py --hoy          # solo los partidos de hoy pendientes
    python predict.py --sin-simular  # omite la simulación Monte Carlo (más rápido)
    python predict.py --fecha 2026-07-06
    python predict.py --salida reports/mi_reporte.md
"""

import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from fifa2026 import datos, reporte, simulacion  # noqa: E402

DISCLAIMER = (
    "> ⚠️ **Aviso:** este modelo es una herramienta estadística con fines "
    "informativos. Ninguna apuesta es segura: las probabilidades tienen un "
    "margen de error inherente y las cuotas de ejemplo deben sustituirse por "
    "cuotas reales. Apuesta solo dinero que puedas permitirte perder y usa "
    "siempre una fracción conservadora del bank (Kelly 25 % ya incluido). "
    "Si el juego deja de ser un entretenimiento, busca ayuda "
    "(en España: 900 200 225 — Jugadores Anónimos)."
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hoy", action="store_true",
                        help="solo los partidos de hoy sin jugar")
    parser.add_argument("--fecha", default=None,
                        help="fecha de referencia AAAA-MM-DD (por defecto, hoy)")
    parser.add_argument("--sin-simular", action="store_true",
                        help="omitir la simulación Monte Carlo")
    parser.add_argument("--sims", type=int, default=20000,
                        help="número de simulaciones (por defecto 20000)")
    parser.add_argument("--salida", default=None,
                        help="ruta del reporte Markdown a generar")
    args = parser.parse_args()

    hoy = args.fecha or datetime.date.today().isoformat()

    equipos = datos.cargar_equipos()
    estadios = datos.cargar_estadios()
    partidos = datos.cargar_partidos()
    cuotas = datos.cargar_cuotas()
    overrides = datos.cargar_clima_override()
    h2h = datos.cargar_h2h()

    # Solo se pueden analizar partidos con ambos equipos ya definidos
    pendientes = [p for p in partidos
                  if p["estado"] == "por_jugar"
                  and not p["local"].startswith(("W:", "L:"))
                  and not p["visitante"].startswith(("W:", "L:"))]
    if args.hoy:
        pendientes = [p for p in pendientes if p["fecha"] == hoy]

    jugados = [p for p in partidos if p["estado"] == "finalizado"]

    lineas = [
        f"# Predicciones Mundial FIFA 2026 — {hoy}",
        "",
        DISCLAIMER,
        "",
        "## Resultados recientes de la fase eliminatoria",
        "",
    ]
    for p in jugados:
        lineas.append(
            f"- **{p['local']} {p['goles_local']}-{p['goles_visitante']} "
            f"{p['visitante']}** ({p['fase']}, {p['fecha']}, "
            f"{estadios[p['estadio_id']]['ciudad']})"
            + (f" — {p['notas']}" if p["notas"] else ""))
    lineas += ["", "## Predicciones de partidos con cruce definido", ""]

    for p in pendientes:
        analisis = reporte.analizar_partido(p, equipos, estadios, overrides, h2h, cuotas)
        lineas.append(reporte.seccion_partido(analisis))

    if not args.sin_simular:
        resultados = simulacion.simular_torneo(
            partidos, equipos, estadios, overrides, n_sims=args.sims)
        lineas.append(reporte.seccion_simulacion(resultados, equipos))

    lineas += [
        "---",
        "",
        "**Metodología:** Elo base (junio 2026) + forma en el torneo + bonus de "
        "anfitrión y altitud → superioridad esperada de goles → Poisson bivariado "
        "con corrección Dixon-Coles (ρ = -0.11). El total de goles se ajusta por "
        "calor, lluvia/tormenta, altitud y techo climatizado. La clasificación "
        "incluye prórroga y penales (la diferencia de fuerza pesa un 45 % en esa "
        "fase). Valor = probabilidad del modelo × cuota - 1; se recomienda solo "
        "con EV ≥ 3 % y stake de Kelly al 25 %.",
    ]

    texto = "\n".join(lineas)
    print(texto)

    salida = args.salida or os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "reports", f"predicciones_{hoy}.md")
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    with open(salida, "w", encoding="utf-8") as f:
        f.write(texto + "\n")
    print(f"\n[Reporte guardado en {salida}]", file=sys.stderr)


if __name__ == "__main__":
    main()
