"""Carga de los CSV de datos (equipos, estadios, partidos, cuotas, clima)."""

import csv
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def _leer_csv(nombre):
    ruta = os.path.join(DATA_DIR, nombre)
    with open(ruta, newline="", encoding="utf-8") as f:
        filas = [fila for fila in csv.DictReader(
            linea for linea in f if not linea.startswith("#"))]
    return filas


def cargar_equipos():
    equipos = {}
    for fila in _leer_csv("ratings_equipos.csv"):
        equipos[fila["equipo"]] = {
            "confederacion": fila["confederacion"],
            "elo": float(fila["elo_base"]),
            "forma": float(fila["forma_2026"]),
            "anfitrion": fila["pais_anfitrion"] == "si",
            "altitud": fila["adaptado_altitud"] == "si",
            "notas": fila["notas"],
        }
    return equipos


def cargar_estadios():
    estadios = {}
    for fila in _leer_csv("estadios.csv"):
        estadios[fila["estadio_id"]] = {
            "nombre": fila["nombre"],
            "ciudad": fila["ciudad"],
            "pais": fila["pais"],
            "capacidad": int(fila["capacidad"]),
            "altitud_m": int(fila["altitud_m"]),
            "techo": fila["techo"],
            "cesped": fila["cesped"],
            "lat": float(fila["lat"]),
            "lon": float(fila["lon"]),
            "julio_max_c": float(fila["julio_max_c"]),
            "julio_min_c": float(fila["julio_min_c"]),
            "humedad_pct": float(fila["humedad_pct"]),
            "clima_notas": fila["clima_notas"],
        }
    return estadios


def cargar_partidos():
    partidos = []
    for fila in _leer_csv("partidos_2026.csv"):
        fila["goles_local"] = int(fila["goles_local"]) if fila["goles_local"] else None
        fila["goles_visitante"] = (
            int(fila["goles_visitante"]) if fila["goles_visitante"] else None)
        partidos.append(fila)
    return partidos


def cargar_cuotas():
    cuotas = {}
    for fila in _leer_csv("cuotas_mercado.csv"):
        cuotas[fila["match_id"]] = {
            "1": float(fila["cuota_local"]),
            "X": float(fila["cuota_empate"]),
            "2": float(fila["cuota_visitante"]),
            "fuente": fila["fuente"],
        }
    return cuotas


def cargar_clima_override():
    overrides = {}
    for fila in _leer_csv("clima_override.csv"):
        overrides[fila["match_id"]] = {
            "temp_c": float(fila["temp_c"]),
            "humedad_pct": float(fila["humedad_pct"]),
            "viento_kmh": float(fila["viento_kmh"]),
            "lluvia": fila["lluvia"],
            "fuente": fila["fuente"],
        }
    return overrides


def cargar_historial():
    return {fila["equipo"]: fila for fila in _leer_csv("historial_equipos.csv")}


def cargar_h2h():
    h2h = {}
    for fila in _leer_csv("h2h_mundiales.csv"):
        h2h.setdefault(fila["partido"], []).append(
            f'{fila["antecedente"]}: {fila["detalle"]}')
    return h2h
