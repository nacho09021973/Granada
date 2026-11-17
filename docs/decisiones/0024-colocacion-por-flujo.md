# 0024 — Colocación por flujo: arregla la banda, no el desorden visible

**Estado:** ensayo, 2026-11-17. Opción `colocacion="flujo"`; el defecto
sigue siendo `"rayo"`. No cambia el campo ni el visor.

## Pregunta

Punto 2 de la hoja de ruta: la zona media e interior sale desordenada.
0019 vio inversiones de banda y fondos que no llegan a la cota anterior. 0023
atribuyó las paradas del flujo a la bilineal, sin encierro geométrico. ¿Seguir
las líneas de máxima pendiente sobre un interpolador suave ordena la zona?

## Método

`granada/hiladas_campo.py`:

- `interpolador_suave`: spline cúbico de H (`RectBivariateSpline`, s=0),
  con gradiente continuo y sin valles en las aristas de celda.
- `banda_de_flujo`: desde muestras del frente separadas un paso de rejilla,
  integra dX/dh = −grad/|grad|² con RK4. Hay 16 niveles de H entre el
  frente y la cota anterior y 4 subpasos por nivel. Tras cada nivel, Newton
  sobre el gradiente devuelve el punto a su nivel. El paso espacial se limita
  a una celda.
- `colocar_en_banda`: (arco, profundidad) de cada vértice → tabla, por
  interpolación bilineal. Sustituye al desplazamiento recto con fondo
  recortado (0,35–1,6 fondos). La pieza llena la banda real.

`scripts/comparar_colocacion_flujo.py` → `datos/comparacion_colocacion_flujo.json`.
A=2, B y borde libre, con los 63 frentes.

## Resultado

| | rayo | flujo |
|---|---:|---:|
| Triángulos de banda invertidos | 27 390 / 2 069 560 (1,3 %) | 2 556 / 3 310 176 (0,08 %) |
| Frentes con alguna inversión | 24 | 22 |
| Error de cota en el fondo, típico | 0,1–3,7 pasos | ~1,5e-3 pasos |

Con flujo, las inversiones que quedan se concentran en las filas 1, 15, 17,
18 y 24. Son frentes cuya banda cambia de topología, de anillo a lazos, o
están junto al borde H=0 de la fila 1. Allí las líneas de flujo divergen:
la razón de anchos fondo/frente llega a 84 y la profundidad a 2,8 fondos.
En siete lazos de la fila 18 el fondo no llega a su cota (0,04–0,30 pasos),
por el tope de paso donde |grad| es casi cero.

El error de ~1e-3 pasos es la diferencia entre el spline y la bilineal con
la que se mide, no un fallo de llegada.

Test de control: en el cono (A=0), el flujo es radial y llena la banda.

## Lectura: el desorden visible viene de otra causa

El render completo (`renders/previas/cupula_campo_flujo.png`) apenas cambia
frente al de rayo. Se suaviza el anillo dentado a un tercio del radio, pero
la zona media sigue arrugada.

Se midió el giro del frente a lo largo de un paso tangencial de pieza:

- Filas 13–24 y 30–37: mediana de 20–60°, percentil 95 de 70–145°.
- Filas 2–8 y 38–45: mediana < 25°, percentil 95 < 50° (salvo los
  entrantes de los cupulines).

Las filas con más giro son las desordenadas en la imagen. Cada pieza se
dobla siguiendo una curva que gira hasta ~100° dentro de su propio ancho.
Esto es geometría del frente, igual con rayo y con flujo. Coincide con la
nota previa de la hoja de ruta: las celdas de la red son menores que la
pieza.

La relación entre giro y desorden visual es una correlación observada, no
una medida del render.

## Alcance

No se han contado intersecciones 3D entre sólidos ni piezas defectuosas.
No se ha validado fidelidad histórica. Los cierres y la clave siguen
pendientes. La elección entre rayo y flujo, y el tratamiento del giro, son
del usuario.

## Artefactos

```bash
/tmp/granada-venv/bin/python scripts/comparar_colocacion_flujo.py
/tmp/granada-venv/bin/python scripts/render_hilada_campo.py --A 2 --hiladas todas \
    --colocacion flujo --png renders/previas/cupula_campo_flujo.png
/tmp/granada-venv/bin/python -m pytest -q
```

Tests: `tests/test_colocacion_flujo.py`.
