# 0026 — Frentes suavizados a escala de pieza

**Estado:** aceptada por el usuario, 2026-11-17, tras ver el render Cycles.
`colocacion="suavizada"` con `SIGMA_FRENTE` = 1,0 pasa a ser el defecto de
`montar` y de `scripts/render_hilada_campo.py`. Rayo, flujo y rígida se
conservan como opciones. No sustituye la malla del visor.

## Pregunta

0024 y 0025 mostraron que el desorden de la zona media viene del frente:
serpentea a una escala menor que la pieza. El usuario eligió suavizar el
frente a escala de pieza (opción 2 de 0024). ¿Qué σ ordena las filas con
el menor desvío respecto a la curva de nivel real?

**Criterio fijado antes del barrido:** en los anillos de las filas 13–24
y 30–37, la mediana del giro por paso tangencial debe quedar por debajo de
25° en todos los frentes. Es el nivel de las filas ordenadas. Entre los
σ que lo cumplan, se elige el de menor desvío.

## Método

`granada/hiladas_campo.py`:

- `suavizar_curva`: gaussiana a lo largo del arco, periódica en curvas
  cerradas y compensada: G·Q + (G·Q − G·G·Q). La gaussiana sola encoge un
  anillo σ²/2R, 0,1 catetos en R=5; lo detectó el test del cono. La
  compensación deja ese error en O(σ⁴).
- `frente_suavizado`: el número de piezas se recalcula con la nueva
  longitud.
- `banda_suavizada`: normal del frente suavizado, con un sentido por frente
  (el que baja H en la mayoría de muestras). El fondo es el primer corte con
  las curvas de la cota anterior, suavizadas con el mismo σ, hasta tres
  fondos. Sin corte se usa el fondo de rayo. Se recorta a 0,35–1,6 fondos.

`scripts/barrer_suavizado_frentes.py` → `datos/barrido_suavizado_frentes.json`.

## Resultado (A=2, B, borde libre, 63 frentes)

| σ (catetos / cm) | giro máx. de las medianas, filas desordenadas | desvío máx. de la curva real | inversiones de banda | piezas |
|---:|---:|---:|---:|---:|
| 0 | 60,6° | 0 | 48 947 | 5538 |
| 0,35 / 7,8 | 51,8° | 2,3 cm | 24 723 | 5414 |
| 0,7 / 15,7 | 38,6° | 5,7 cm | 8 816 | 5196 |
| **1,0 / 22,4** | **23,9°** ✓ | **8,1 cm** | **2 540** | **5018** |

Solo σ=1,0 cumple el criterio, con poco margen (23,9° frente a 25°).
La mediana en las filas desordenadas baja de 33° a 8,8°, como las
ordenadas (9,1°).

Render: `renders/previas/cupula_campo_suavizada_s1.0.png`. Las filas de
arquillos se leen continuas en casi toda la cúpula. Quedan zonas ásperas
en la oblicua: arriba a la derecha, alrededor de la estrella de la clave
y en los lazos pequeños.

## Costes declarados

- Las hiladas se apartan hasta 8 cm de la curva de nivel del campo. En esas
  filas se pierde el dibujo fino de las celdas de la red.
- Bajan las piezas de 5538 a 5018 (−9 %): los frentes lisos son más cortos.
  El recuento sigue sin validar el total histórico.
- 3148 de 89 240 fondos no cortan la curva anterior y usan el de rayo;
  9694 quedan recortados.
- La fila 1 llega hasta r = 16,55 catetos, unos 6 cm fuera del radio base.
  Es el problema de borde H=0 ya registrado (0020, 0021).

## Alcance

No se han contado intersecciones 3D ni piezas defectuosas. No se ha
validado fidelidad histórica. Los cierres, la clave y los cupulines
siguen pendientes.

## Artefactos

```bash
/tmp/granada-venv/bin/python scripts/barrer_suavizado_frentes.py
/tmp/granada-venv/bin/python scripts/render_hilada_campo.py --A 2 --hiladas todas \
    --colocacion suavizada --sigma 1.0 --png renders/previas/cupula_campo_suavizada_s1.0.png
/tmp/granada-venv/bin/python -m pytest -q
```

Tests: `tests/test_colocacion_flujo.py`. Comprueban la eliminación de ondas
cortas sin encoger el círculo y que, en el cono, la banda suavizada coincide
con el paso horizontal.
