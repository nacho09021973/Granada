# 0029 — A=3 raíz por el total de piezas, y celdas hondas

**Estado:** aceptada por el usuario, 2026-11-18 («sí a ambas»).

## Contexto

El usuario veía la cúpula «muy diferente a Ferrer_5». El orden acordado fue:
primero que se lea el dibujo grande, después el borde octogonal y, al final,
la luz y el color.

## A, forma y signo (paso 4 de la 0017)

`scripts/barrer_estrella_campo.py` barre A ∈ {1, 2, 3, 4,5}, forma ∈
{lineal, raíz} y signo ∈ {+1, −1}. La salida está en
`renders/previas/barrido_estrella.png` y `datos/barrido_estrella.json`.

- El signo +1 hace de cada celda una bolsa hacia arriba, como los huecos de
  Ferrer_5. El −1 forma crestas.
- raíz, +1, A=3 da 5326 piezas, el 98 % de las 5416 de Jones y Goury. A=2
  lineal, el valor anterior, daba el 92 %.
- **Defecto nuevo** en `render_hilada_campo.py`: `--A 3 --forma raiz`.
- Resultado negativo: en un render en yeso, A=2 lineal y A=3 raíz se ven casi
  iguales (`renders/previas/comparativa_A_yeso.png`). Las bolsas del campo
  son hondonadas suaves cubiertas de piezas; desde abajo miran a la cámara y
  no hacen sombra. El campo no explica la diferencia con Ferrer_5.

## Celdas hondas

Los huecos oscuros de Ferrer_5 coinciden con dos elementos del modelo: los 16
cupulines y los 16 frentes más altos de cada celda, tapados con cupulilla.

- `cierres_campo.ALTURA_RELATIVA`: 0,9 → 2,0. Las cupulillas pasan a ser
  pozos y el anillo interior de 16 y la clave se leen oscuros
  (`renders/previas/comparativa_celdas_hondas.png`).
- `render_hilada_campo.PROFUNDIDAD_CUPULIN`: 2 → 5 pasos. Los cupulines
  siguen leyéndose claros, porque las ventanas de debajo iluminan sus
  paredes. Queda pendiente para el paso de la luz.

Las dos alturas son elección, no medida.

## Borde octogonal

`campo(borde="octogonal")`, el nuevo defecto de `render_hilada_campo.py`: el
cono se mide con una norma octogonal en el arranque que pasa a circular hacia
la clave. Es `rho = r · (_MEDIA_OCT / oct(φ))^w`, con `w = (r / RADIO_BASE)²`.
La curva H = 0 cae en el octógono interior de la cornisa y la trama llena las
esquinas del tambor (`renders/previas/comparativa_borde_octogonal.png`). Ya no
hace falta la corona de arranque, que queda solo para el borde libre. La forma
de la transición es elección.
