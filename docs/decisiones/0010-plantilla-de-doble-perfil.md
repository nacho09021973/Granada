# 0010 — Plantilla de doble perfil y malla exportable

**Estado:** aceptada — 2026-08-29

## Decisión

Se sustituye el modelo de perfil único por la **plantilla de doble perfil** que
documenta la tesis, y se levanta la cúpula como malla triangular exportable.

`granada/plantilla.py` codifica lo documentado, exacto en `Fraction`:

| | división | cima | fracción útil del salto |
|---|---:|---:|---:|
| perfil **mayor** | quintos | 7P | 7/8 |
| perfil **menor** | séptimos | 7,5P | 15/16 |
| nivel siguiente | — | 8P | — |

`granada/malla.py` da a cada una de las 105 caras un sólido cerrado:
plataforma horizontal a la cota de su banda y, colgando de ella, el frente con
el perfil de su plantilla. `scripts/exportar_malla.py` escribe
`renders/cupula_aproximada.obj` y el informe `datos/malla_cupula.json`.

## Qué es medido y qué es elección de modelo

Se separan explícitamente porque tienen distinto valor probatorio:

- **medido**: la planta de cada cara; su cota de banda, calibrada contra la
  sección (decisión 0009); y el **vuelo** de cada cara, que es lo que el cono
  medido desciende del radio de su centroide a su borde exterior;
- **documentado**: la proporción 7/8 o 15/16 entre el frente y el salto
  disponible, y el paralelismo entre piezas vecinas;
- **elección de modelo, declarada**: la **curva** entre los extremos del
  perfil. Se interpola con la cónica racional de `granada/adaraja.py`, que es
  exacta en `Fraction` pero no es una medida de nada. Se conserva esa primitiva
  precisamente porque no impone forma: es el interpolador, no el modelo;
- **parámetro, no constante histórica**: 8P. Ferrer aclaró que no consta en los
  manuscritos (`docs/fuentes.md`, entrada 11).

## El paralelismo, aplicado a esta planta, fuerza plantilla única

La tesis observa que las piezas vecinas mantienen sus perfiles **paralelos**.
Perfiles paralelos son trasladados verticalmente uno de otro, luego dos piezas
vecinas han de compartir plantilla: mayor y menor no son paralelas, ni en cima
ni en división.

El grafo dual de esta planta es **conexo** — la BFS de la decisión 0007 alcanza
las 105 caras desde el borde. Por tanto, **exigir paralelismo en las 227
vecindades obliga a que toda la cúpula use una sola plantilla**, y la segunda
sobra. Como la tesis documenta dos, la conclusión es que el paralelismo no
puede valer en todas las vecindades a la vez: hay fronteras donde se rompe.

Es coherente con lo que la propia tesis advierte de *esta* cúpula: un frente
que pasa de **7P a 10P** en el grupo siguiente, con «mocárabes de distinto
módulo». Esas fronteras de módulo son las candidatas naturales a romper el
paralelismo, pero **ninguna fuente dice cuáles son**.

En consecuencia: todas las caras usan el perfil **mayor**, y el validador
`vecindades_no_paralelas` da 0 vecindades rotas de forma **trivial**. Queda
escrito que es trivial para que nadie lo lea como una validación. La plantilla
menor está implementada y probada, pero no se asigna a ninguna cara porque no
hay evidencia para hacerlo.

## Dos defectos que solo vio el render

Los controles numéricos —rango de cotas, residuo frente al cono, recuento de
grupos— daban por buena una malla que tenía dos fallos. Los destapó mirarla,
que es literalmente la cautela 2 de `PROXIMOS-PASOS.md`. Por eso el
rasterizador queda en el repositorio como `scripts/render_malla.py`: el control
visual tiene que ser reproducible, no un vistazo de una vez.

**1. Huecos abiertos entre bandas.** El primer levantado colgaba cada celda su
propio *vuelo* radial, que no llega a la banda de abajo: quedaban agujeros de
entre 0,078 y **0,390 m** entre todas las bandas consecutivas. Ninguno alteraba
el rango de cotas ni el residuo. La corrección es además más fiel a la
plantilla: la celda cuelga **7/8 del salto real hasta la banda inferior**, y el
octavo restante es la junta —de 0,051 a 0,152 m—, que es justo lo que significa
«cima a 7P, nivel siguiente a 8P».

**2. Púas por triangular en abanico.** El fondo y la plataforma se triangulaban
como abanico desde el centroide, y **51 de las 105 caras no son convexas**: el
abanico les genera triángulos invertidos que salían como púas. Sustituido por
**recorte de orejas** (`granada.malla.triangular`), con control de que la suma
de las áreas troceadas es el área del polígono y de que ningún triángulo se
sale de una cara cóncava de prueba.

## Controles

- La celda cuelga **exactamente** 7/8 —o 15/16— del salto disponible: igualdad
  de racionales, no tolerancia.
- El perfil engancha en 1 en el borde interior y cuelga en 0 en el exterior, y
  es **monótono** en todo su recorrido: un perfil que subiera y bajara no sería
  una adaraja.
- Ninguna cima alcanza 8P: entre la cima y el nivel siguiente queda la junta.
  Construir una plantilla con cima 8P falla.
- La malla cubre las **105 caras** en 105 grupos, 6.064 vértices y 11.708
  triángulos, con cotas entre **0,152 m y 4,670 m** y radio máximo 3,47 m.
- Entre el fondo de una banda y la plataforma de la inferior queda solo la
  junta, un octavo del salto: nunca un agujero abierto.
- Ajuste al cono medido: residuo **rms 0,234 m** y máximo 0,71 m sobre una
  cúpula de 4,67 m — un 5 % rms.

## Límites

- **Una celda por cara, y una cara no es una adaraja.** La cara mediana de esta
  planta abarca **5,2 hiladas** de la sección. El levantado reproduce el
  escalonado de las **seis bandas**, no el de las 23 hiladas. Para bajar a
  hilada haría falta subdividir las 80 caras sin figura, que la figura 128 no
  subdivide.
- **El residuo máximo está en el borde exterior**: la banda 0 tiene su cota en
  la hilada 6 y su celda no baja hasta el arranque. La planta no llega al
  arranque de la cúpula.
- **El octógono central se lleva la cota del ápice** porque su centroide está
  en el eje, aunque su borde esté en la hilada 19. Es la pieza donde la
  aproximación de banda cuesta más: en la cúpula real es una cupulilla, no una
  plataforma.
- La curva del perfil no está medida. Cambiarla cambia el aspecto sin que
  ninguna fuente lo arbitre.

## Lo que sigue viéndose mal, y es sabido

El **octógono central** remata la cúpula como una tapa plana de 1,28 m a 4,67 m
—un tambor, no una cupulilla—. Es el límite de banda llevado al extremo: su
centroide está en el eje aunque su borde esté en la hilada 19. Y el conjunto lee
como **seis bandejas**, no como una cúpula, porque seis bandas es lo que da esta
planta.

Reproducción:

```bash
python3 scripts/exportar_malla.py
python3 scripts/render_malla.py
```
