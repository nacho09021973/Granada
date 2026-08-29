# 0012 — Propagar observaciones por rotación C8, no por espejo

**Estado:** aceptada — 2026-08-29

## Problema

El vídeo de Ferrer (`fuentes.md`, entrada 12) muestra **un cuarto** del modelo.
Si una observación hecha ahí no puede extenderse, el trabajo de leer sentidos de
ascenso cubriría a lo sumo una cuarta parte de la cúpula, y el paso 1 de
`docs/hoja-de-ruta.md` valdría poco.

La hoja de ruta decía que extenderlo *«sería usar como evidencia la simetría que
nosotros impusimos — la cautela 5»*. **Eso era demasiado estricto y confundía dos
cosas.** Al revisarlo contra la entrada 7 de `fuentes.md`:

| operación | respaldo |
|---|---|
| **rotación** de 45° | **medida**: armónico k=16 dominante (17,2 % en el conjunto, 34,2 % en el anillo de cupulines) y simetría rotacional exacta de orden 8, por Fourier sobre la ortoimagen |
| **espejo** | la entrada 7 dice literalmente **«No se ha analizado la simetría especular»**. Y la mitad inferior de la red ya es un espejo impuesto |

La medición de la rotación es **independiente de la red**: se hizo sobre la
ortoimagen. Usarla no es circular. Lo que sí sería circular es usar la red
espejada como evidencia de que hay espejo — que es lo que prohíbe la cautela 5, y
sigue prohibido.

## Decisión

Las observaciones se propagan **solo por rotación C8**. El espejo no se aplica.
`scripts/orbitas_c8.py` calcula el emparejamiento y `datos/orbitas_c8.json` lo
publica con sus controles.

**La segunda mitad de la cautela 5 sigue entera**: propagar no multiplica el N.
Observadas 27 vecindades son 27, nunca 216.

## Lo que sale

- La rotación de 45° empareja caras con caras: es **biyectiva** y de orden
  **exactamente 8**.
- **14 órbitas de caras**: 13 de tamaño 8 más el octógono central `c042`, que la
  rotación deja fijo. 13 × 8 + 1 = 105.
- **27 órbitas de vecindades propagables**, que cubren **216 de las 227**.
- **Dominio fundamental: 14 caras y 27 vecindades.** Eso es lo mínimo que hay que
  observar para cubrir la cúpula. El trabajo del paso 1 pasa de 227 lecturas a
  27.

## Controles

- **Desajuste** al emparejar: mediana 13,3 mm, máximo 101,5 mm.
- **Margen** frente al segundo candidato: mediana 13,9×, mínimo 1,35×. Seis caras
  quedan por debajo de 2× —`c003`, `c010`, `c011`, `c048`, `c078`, `c096`— y van
  nombradas una a una en el artefacto.
- **Ángulos de control.** Si 45° no fuera especial, cualquier giro emparejaría
  igual de bien. No lo hace:

  | giro | desajuste máximo | caras con margen ≥ 2× |
  |---:|---:|---:|
  | **45°** | **101,5 mm** | **99 de 105** |
  | 22,5° | 340,2 mm | 29 |
  | 30° | 540,8 mm | 49 |
  | 60° | 540,8 mm | 51 |

  El control de 22,5° importa aparte: es el ángulo de la retícula C16, y falla.
  Coherente con la entrada 7, que separa el andamiaje angular de orden 16 de la
  simetría exacta del ornamento, que es de orden 8.

## Las cinco vecindades que no cierran

De las 227, **cinco** tienen su imagen fuera del conjunto: `c025–c029`,
`c027–c030`, `c067–c078`, `c069–c079` y `c087–c096`. Dos de ellas tocan una de
las seis caras de margen ajustado.

Es un 2,2 %: residuo del dibujo, no fallo estructural. **Pero por ahí no se
propaga nada.** Las órbitas que contienen un paso roto quedan marcadas
`"propagable": false` y fuera del dominio fundamental. Once vecindades se quedan
sin cubrir, y así se declara.

## Límites

- Esto empareja caras de **la planta**, que ya es D8 por construcción. No
  demuestra nada sobre la cúpula real, que además está deformada (cautela 7).
- **La maqueta de Contreras no es una copia exacta** (entrada 13): su taller
  rellenaba lagunas para dar una imagen más completa. Si rellenaba hacia lo
  regular, su modelo será **más simétrico que la fábrica**, así que propagar
  sobre él es seguro pero poco informativo. Buscarle asimetrías, inútil.
- El espejo sigue **sin medir**. Está pendiente correr el mismo análisis de
  Fourier para la simetría especular sobre la ortoimagen; hasta entonces, D8 no
  se usa para propagar nada.

Reproducción:

```bash
python3 scripts/orbitas_c8.py
```
