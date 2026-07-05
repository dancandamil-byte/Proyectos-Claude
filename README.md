# Modelo de apuestas — Mundial FIFA 2026 ⚽

Modelo estadístico completo para estimar probabilidades y detectar valor en las
apuestas de los partidos restantes del Mundial FIFA 2026 (Canadá–México–Estados
Unidos). Incluye históricos de los 22 mundiales, los 16 estadios con altitud y
clima de julio, ratings de fuerza, forma del torneo en curso, simulación Monte
Carlo del cuadro y análisis de valor frente a las cuotas del mercado.

**Sin dependencias:** funciona con Python 3.9+ estándar (no requiere numpy ni pandas).

## Uso rápido

```bash
python predict.py                      # reporte completo: pendientes + simulación
python predict.py --hoy                # solo los partidos de hoy
python predict.py --fecha 2026-07-06   # fija la fecha de referencia
python predict.py --sin-simular        # más rápido, sin Monte Carlo
python predict.py --sims 50000         # más precisión en la simulación
```

El reporte se imprime en pantalla y se guarda en `reports/predicciones_<fecha>.md`.

## Estructura

```
data/
  mundiales_historicos.csv   # 22 mundiales 1930-2022: sedes, campeones, goles/partido
  historial_equipos.csv      # historial mundialista de los 16 equipos de octavos
  ratings_equipos.csv        # Elo base + forma 2026 + flags de anfitrión/altitud
  estadios.csv               # 16 sedes: capacidad, altitud, techo, coordenadas, clima julio
  partidos_2026.csv          # cuadro eliminatorio: resultados y partidos por jugar
  h2h_mundiales.csv          # antecedentes directos en mundiales
  cuotas_mercado.csv         # cuotas 1X2 del mercado (EJEMPLO: pon las reales)
  clima_override.csv         # clima manual por partido (prioridad máxima)
src/fifa2026/
  datos.py        # carga de CSV
  clima.py        # override manual > API Open-Meteo > climatología de julio
  ajustes.py      # bonus anfitrión, altitud, calor, tormenta, techo con A/C
  poisson.py      # Poisson bivariado + corrección Dixon-Coles; prórroga y penales
  simulacion.py   # Monte Carlo del cuadro hasta el campeón
  valor.py        # EV, cuota justa y Kelly fraccionado (25 %)
  reporte.py      # generación del reporte Markdown
predict.py        # CLI
```

## Metodología

1. **Fuerza:** Elo base (junio 2026) + ajuste de forma por el rendimiento en el
   torneo (p. ej. Noruega +70 tras eliminar a Brasil con doblete de Haaland).
2. **Contexto del estadio:** bonus de anfitrión (México +85 en el Azteca,
   EE. UU. +50 en casa), bonus de aclimatación en altitud (+35 por encima de
   1500 m: aplica a México, Colombia, Argentina), y ajuste del ritmo de goles
   por calor extremo, tormenta o altitud. Los estadios con techo y aire
   acondicionado (Dallas, Houston, Atlanta) neutralizan el clima.
3. **Goles:** la diferencia de Elo se convierte en superioridad esperada
   (170 puntos Elo ≈ 1 gol) y se reparte sobre un total base de 2.45 goles.
   Matriz de marcadores Poisson con corrección Dixon-Coles (ρ = −0.11) para
   marcadores bajos.
4. **Clasificación:** probabilidad de ganar en 90' + empate × probabilidad en
   prórroga/penales (la ventaja de fuerza pesa solo un 45 % en esa lotería).
5. **Simulación:** 20 000 torneos simulados desde el cuadro actual hasta la
   final del 19 de julio en el MetLife Stadium.
6. **Valor:** EV = probabilidad × cuota − 1. Solo se marca ⭐ VALOR con EV ≥ 3 %,
   con stake sugerido de Kelly al 25 % del criterio completo.

## Cómo mantenerlo al día

- **Resultados:** cuando termine un partido, rellena `goles_local`,
  `goles_visitante` y cambia `estado` a `finalizado` en `data/partidos_2026.csv`.
- **Cuotas reales:** sustituye las filas EJEMPLO de `data/cuotas_mercado.csv`
  por las cuotas de tu casa de apuestas — sin esto el análisis de valor no es fiable.
- **Clima:** con conexión a internet el modelo consulta Open-Meteo
  automáticamente; sin conexión usa la climatología de julio. Para condiciones
  especiales (como la tormenta del 5 de julio en CDMX) usa `data/clima_override.csv`.
- **Forma:** ajusta la columna `forma_2026` de `data/ratings_equipos.csv` tras
  cada ronda (rango razonable: ±80 puntos).

## Estado del torneo (5 de julio de 2026)

- Octavos jugados: Marruecos 3-0 Canadá · Francia 1-0 Paraguay · **Brasil 1-2
  Noruega** (doblete de Haaland; Brasil eliminado).
- Hoy: **México vs Inglaterra** en el Azteca (retrasado por tormenta eléctrica).
- Cuartos ya definidos: Francia vs Marruecos (Boston, 9-jul) y Noruega vs
  ganador México/Inglaterra (Miami, 11-jul).

> ⚠️ **Aviso importante:** ningún modelo garantiza aciertos. Las probabilidades
> son estimaciones con error inherente y el fútbol de eliminación directa tiene
> una varianza enorme. Apuesta solo dinero que puedas permitirte perder, usa
> stakes fraccionados y trata esto como entretenimiento informado, no como una
> fuente de ingresos. Si el juego deja de ser un juego, pide ayuda
> (España: 900 200 225 · línea de Jugadores Anónimos).
