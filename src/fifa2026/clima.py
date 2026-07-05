"""Clima por partido: override manual > API Open-Meteo (si hay red) > climatología de julio.

El techo cerrado con A/C (Dallas, Houston, Atlanta) neutraliza el clima exterior:
esos partidos se juegan a ~22 C sin viento ni lluvia.
"""

import json
import urllib.request

TEMP_INTERIOR_AC = 22.0


def _api_open_meteo(lat, lon, fecha):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,precipitation_probability_max,wind_speed_10m_max"
        f"&start_date={fecha}&end_date={fecha}&timezone=auto"
    )
    with urllib.request.urlopen(url, timeout=6) as resp:
        d = json.load(resp)["daily"]
    prob_lluvia = d["precipitation_probability_max"][0] or 0
    return {
        "temp_c": d["temperature_2m_max"][0],
        "humedad_pct": None,
        "viento_kmh": d["wind_speed_10m_max"][0],
        "lluvia": "rain" if prob_lluvia >= 50 else "none",
        "fuente": "Open-Meteo (pronóstico en vivo)",
    }


def clima_del_partido(partido, estadio, overrides):
    techo_cerrado = "A/C" in estadio["techo"]
    if techo_cerrado:
        return {
            "temp_c": TEMP_INTERIOR_AC,
            "humedad_pct": 50.0,
            "viento_kmh": 0.0,
            "lluvia": "none",
            "fuente": f'Interior climatizado ({estadio["techo"]})',
        }
    if partido["match_id"] in overrides:
        return overrides[partido["match_id"]]
    try:
        return _api_open_meteo(estadio["lat"], estadio["lon"], partido["fecha"])
    except Exception:
        return {
            "temp_c": estadio["julio_max_c"],
            "humedad_pct": estadio["humedad_pct"],
            "viento_kmh": 10.0,
            "lluvia": "none",
            "fuente": "Climatología media de julio (sin conexión a la API)",
        }
