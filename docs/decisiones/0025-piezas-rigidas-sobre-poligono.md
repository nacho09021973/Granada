# 0025 — Piezas rígidas sobre polígono: rechazado

**Estado:** ensayo fallido, 2026-11-17. Opción `colocacion="rigida"`, que
se conserva para trazabilidad. El defecto sigue siendo `"rayo"`.

## Pregunta

0024 atribuyó el desorden visible de la zona media a piezas que se doblan
siguiendo frentes que giran 20–60° dentro de su ancho. El usuario eligió
probar piezas rígidas. ¿Se ordena la zona si cada pieza se coloca entera
sobre un lado del polígono inscrito en su frente?

## Método

En `granada/hiladas_campo.py`, `poligono_de` construye un lado por pieza.
Sus vértices están en s_i ± L/2 sobre el frente, con L el paso tangencial
estirado. La normal se orienta hacia donde baja H. El fondo se busca por
bisección sobre el spline de 0024, a lo largo de la normal, hasta tres fondos
nominales, y se recorta a 0,35–1,6 fondos como en rayo. `colocar_rigida`
aplica a la pieza una traslación, una rotación y una escala en y.

La medida está en `scripts/comparar_colocacion_flujo.py`, apartado
`rigida`, y en `datos/comparacion_colocacion_flujo.json`.

## Resultado

Render: `renders/previas/cupula_campo_rigida.png`. La zona media sale
**más** desordenada que con rayo o flujo. Las piezas ya no se doblan, pero
quedan orientadas casi al azar.

| Medida (A=2, B, 5540 lados) | Valor |
|---|---:|
| Lados que giran >45° respecto al siguiente | 721 |
| Mediana de giro entre lados, filas 19–23 y 31–37 | 31–60° |
| Mediana de giro entre lados, filas 3–9 y 39–45 | 4–22° |
| Fondos sin cruce de la cota dentro de 3 fondos | 407 (97 en la fila 1, borde H=0) |
| Fondos recortados, sin cruce incluido | 892 |

Test de control: en el cono, los lados son tangentes y el fondo es radial
e igual al paso horizontal.

## Lectura

Rayo, flujo y rígida fallan en las mismas filas. El problema no está en
cómo se coloca la pieza, sino en el frente: serpentea a una escala menor
que una pieza. Doblar la pieza la arruga; no doblarla la desorienta.

Quedan las opciones 2 y 3 de 0024:

- suavizar el frente a escala de pieza;
- cambiar el campo (A o suavizado), lo que afecta a la estrella.

La decisión es del usuario.

## Alcance

No se han contado intersecciones 3D ni piezas defectuosas. No se ha
validado fidelidad histórica.
