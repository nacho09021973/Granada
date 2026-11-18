# 0027 — Cierres, clave y cupulines del modelo por campo

**Estado:** propuesta, 2026-11-18. Pendiente de que el usuario vea el render
Cycles `renders/previas/cupula_cycles_{visitante,cenital}_campo_cupulines.png`.
Es el paso 4 de la 0017, más los cupulines que el usuario pidió ese día.

## Pregunta

El render aprobado el 2026-11-17 (0026) dejaba huecos negros: la clave, 16
huecos en el anillo exterior y 8 brazos de la estrella. Además, los 16
cupulines medidos no estaban en el modelo por campo. ¿Cómo se cierran sin
tocar la colocación?

## Qué se hizo

**Huecos por cobertura** (`granada/cierres_campo.py`). Un nudo de la rejilla
(1,3 cm) está cubierto si cae en la banda de algún frente montado, entre el
frente suavizado y su fondo. Lo que no cubre ninguna banda se abre con un
disco de 1,3 cm: lo que sobrevive es hueco y lo demás, rendija. Con A=2 y 2
filas por hilada salen 54 huecos (`datos/cierres_campo.json`):

- la clave, sobre la fila 45;
- el interior de los frentes más altos de cada celda, en r≈12–13;
- las medias lunas junto a ellos y los brazos de la estrella, en r≈3,8 y
  r≈5,3: bandas que no llegan a la curva anterior porque la profundidad se
  recorta a 1,6 fondos.

**Cupulilla de cierre.** Cada hueco recibe una cupulilla que sigue su
contorno, ensanchada 2,7 cm bajo las piezas vecinas. La base es la
interpolación armónica de H desde el borde. Una primera versión tomaba H del
punto de borde más cercano y dejaba escalones de hasta 13 cm en los huecos en
pendiente; lo detectó el test. Sobre la base sube un cuarto de círculo de
altura 0,9·dmax, como en `granada.cupula._cupulilla`.

**Lazos que colapsan al suavizar** (`admitido_suavizado`). `PIEZAS_MINIMAS`
se medía sobre la curva cruda, pero las piezas siguen la suavizada. El lazo
de la fila 24 en r=8,7 pasaba de 1,93 a 0,02 catetos y sus 6 piezas salían de
un punto. Ahora el mínimo se aplica a la curva suavizada, y el lazo que no
llega se deja a la cupulilla. Efecto: 6 de los 8 lazos de la fila 15 bajan a
4 piezas y también pasan a cupulilla. Los huecos tapados pasan de 60 a 54;
no se ha analizado qué huecos se funden o desaparecen.

**Cupulines** (`scripts/render_hilada_campo.py: cupulines_en_campo`). Son los
16 de `datos/cupulines.json`, construidos con `granada.cupula.cupulin`: se
quitan las piezas con el centroide en el marco y se añaden pocillo,
cupulita y marco. Hay dos cambios respecto al modelo de anillos, que sigue
igual:

- La boca y el marco se apoyan en H, no en el cono. Junto a la red, H se
  separa del cono hasta 1 cateto.
- `arranque="medio"`: la cupulita empieza a la cota media de la boca más la
  profundidad, no por encima de su punto más alto. Con eje vertical sobre el
  campo, el arranque alto dejaba un pozo de 7,5 catetos (~1,7 m) que desde
  abajo se leía como un prisma oscuro, con zonas negras alrededor. Con el
  medio baja a 5,7. En la vista ortogonal desde abajo la cupulita se ve
  entera y la boca, en gota, cae donde en la ortoimagen.

## Fuentes de la posición

Gámiz y Ferrer (2019), *VLC arquitectura* 6(2), junto a la fig. 10
(`docs/2019VLCGAMIZ_FERRER_MUQARNASALHAMBRA.pdf`, comprobado): la lámina X de
Jones y Goury tiene «16 pequeñas cúpulas sobre las ventanas laterales».
Encaja con la medida: la fase de 10,75° deja cada cupulín a ≈0,59 m del eje
de su cara, y la sección de Almagro da las ventanas a ≈0,57 m
[UNVERIFIED: medida por inspección en la investigación del 2026-11-18, sin
script]. Ninguna fuente localizada da la profundidad, las hiladas ni el
despiece de los cupulines (`reports/Cupulines y policromía de Dos Hermanas.md`).

## Lo que esto NO hace

- No es dato: cupulillas, clave, arranque y profundidad de los cupulines
  son elección de acabado.
- No arregla las rendijas. Solo se cuentan: 48 de al menos 7 cm² en planta,
  en las filas 13, 14, 17, 20, 23, 24, 34 y 37. La cobertura en planta no ve
  las rendijas entre piezas dentro de una banda.
- Las cupulillas de los 16 huecos exteriores quedan en sombra y se siguen
  leyendo como manchas oscuras, con luminancia 18/255 frente a 2 cuando
  estaban vacías. Queda para el color.
- El cupulín no reproduce las trompillas ni el arco mixtilíneo que describe
  Pavón Maldonado.

## Añadido el mismo día: cupulín estrellado

Visto de cerca en la ortoimagen, cada cupulín no es una cupulita de piezas:
es un pozo de paredes lisas con techo plano y una estrella de ocho puntas.
`granada.cupula.cupulin_estrellado` lo modela así: boca en gota, paredes
lisas hasta el techo (cota media de la boca + profundidad) y estrella {8/2}
de radio 0,8 rehundida 0,12 radios. Es el defecto de `render_hilada_campo.py`
(`--forma-cupulin piezas` vuelve a la cupulita). La profundidad y el
rehundido son supuestos. Render: `renders/previas/cupula_cycles_*_campo_estrellado.png`.

## Añadido el mismo día: corona de arranque y vista «cúpula»

La vista sala mostró rincones negros en las esquinas del octógono. La cornisa
de la sala (`granada/sala.py: cornisa`) llega a un octógono de apotema
`RADIO_BASE / _MEDIA_OCT`, pensado para el arranque octogonal del modelo de
anillos, mientras que el campo arranca en un círculo de radio `RADIO_BASE`.
`granada.cierres_campo.corona_arranque` tapa la corona que queda entre ambos
con un plano de yeso a z = −0,01, que entra 0,4 catetos bajo la primera fila.

`scripts/render_cycles.py` añade la vista «cupula»: desde el eje, 22 catetos
por debajo del arranque y con 82°, encuadra la cúpula entera con el tambor.
La cenital (13 catetos, 90°) recorta el anillo exterior.
