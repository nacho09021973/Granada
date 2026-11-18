# 0030 — Paleta «ferrer» y luz en penumbra

**Estado:** aceptada por el usuario, 2026-11-18 («sí, sigue»), sobre la
propuesta de acercar el aspecto a Ferrer_5. Sustituye a la variante C de la
0028 como defecto. La C se conserva como `--variante yeso`.

## Por qué

Con la geometría ya corregida (0029), la cúpula seguía «muy diferente a
Ferrer_5». La luz no lo explicaba (`renders/previas/comparativa_luz.png`). El
contraste de la maqueta es de color: fondos de celda marrón oscuro, caras
crema, y el rojo y el azul solo como acentos.

## Qué se hizo

- `scripts/medir_paleta_ferrer.py` → `datos/paleta_ferrer.json`: medianas de
  las clases oscuro, claro, rojo y azul dentro de la cúpula de Ferrer_5. En la
  imagen, el rojo ocupa el 5 % de los píxeles y el azul el 0,3 %.
- `granada.color`: tonos tostado, crema, bermejo y pizarra. El tono y la
  saturación son los medidos; el valor se fija en `VALOR_FERRER`, porque la
  foto es de pantalla y está en penumbra.
- Reparto `ferrer()`:
  - fondos de la familia C en tostado: una fila de cada tres, que marca
    anillos;
  - fondos de la familia A en crema, con 2 acentos bermejos y 1 pizarra cada
    24 celdas;
  - paredes en crema;
  - cupulines con el pozo tostado, techo pizarra y estrella de oro;
  - cupulillas de cierre en tostado; clave de oro.
- Primera prueba descartada: con todos los fondos en tostado, la cúpula
  entera sale marrón, porque el fondo cóncavo es casi toda la superficie que
  se ve desde abajo (`renders/previas/comparativa_paleta_ferrer.png`).
- `render_cycles.py --luz penumbra` pasa a ser el defecto: sin los haces de
  sol y con la luz del suelo a 0,25.

## Fuerza

Ferrer_5 es una restitución del siglo XIX fotografiada en pantalla, no una
medida de la obra. Esto es parecido estético a la maqueta. Los pigmentos
medidos por analogía (0028) ya no gobiernan la paleta por defecto.

## Lo que queda distinto de Ferrer_5

- En la maqueta, lo oscuro dibuja una estrella radial de ocho brazos; aquí,
  anillos concéntricos por familia.
- Los cupulines se leen como pétalos alargados, no como huecos redondos.

## Prueba «ferrer_red» (2026-11-18, pendiente del usuario)

Al ampliar Ferrer_5, las rectas del centro a las esquinas cruzan los
mocárabes sin desviarse: se toman por juntas de la maqueta o de la foto, no
por pintura (supuesto). Lo oscuro de la maqueta son manchas en el centro hondo
de cada celda de la red.

- `granada.color.ferrer_red`: fondo en tostado cuando el centroide de la pieza
  está a ≥ `UMBRAL_RED` (0,55) de la distancia máxima a la red dentro de su
  celda; el resto como «ferrer». `montar` pasa el centroide a los repartos
  con `con_posicion`.
- `render_hilada_campo.py --variante ferrer_red`. No es el defecto.
- Comparación: `scripts/comparar_con_ferrer.py` →
  `renders/previas/comparativa_ferrer_red.png` (no versionada).
- Resultado: desaparecen los anillos; el oscuro queda por celdas y en cuñas
  entre cupulines. Las manchas salen como trazos finos, menos masa oscura que
  en la maqueta.
- Más masa oscura (`--umbral-red`, `--umbral-pared-red`;
  `renders/previas/comparativa_ferrer_red_masa.png`): con umbral 0,40 el
  oscuro gana bastante; añadir paredes oscuras desde 0,70 apenas cambia la
  vista desde abajo. Las manchas siguen saliendo como trazos, no como
  masas.

## Defecto «ferrer_red» con umbral 0,40 y prueba de forma de cupulines (2026-11-18)

El usuario pidió pasar a los cupulines con la propuesta de dejar (a) como
defecto: `--variante ferrer_red` y `UMBRAL_RED = 0.40` son ahora el defecto.

Cupulines alargados («pétalos»):
- La profundidad del pozo no es la causa: con 5, 2 y 1 pasos
  (`--profundidad-cupulin`, `renders/previas/comparativa_profundidad_cupulin.png`)
  el contorno apenas cambia.
- La causa es el prisma vertical (eje a 0°) que corta la superficie a 52°: el
  agujero en la superficie mide ~3,14 / cos 52° ≈ 5,1 por 2,46 catetos, más el
  pico de 1,55, y la cámara central lo ve casi de frente.
- `--eje-cupulin` y `--pico-cupulin` (`renders/previas/comparativa_forma_cupulin.png`):
  sin pico apenas cambia; con eje a 30° la boca sale casi redonda y se ve el
  techo azul con la estrella; con eje a 52° y sin pico salen huecos redondos
  oscuros, sin estrella visible, y en la ortogonal serían elipses de razón
  ~0,62 (nota de `EJE_CUPULIN_GRADOS`).
- Elegido por el usuario: eje a 30° (`EJE_CUPULIN_CAMPO` en
  `render_hilada_campo.py`); el modelo de anillos sigue con 0°.
