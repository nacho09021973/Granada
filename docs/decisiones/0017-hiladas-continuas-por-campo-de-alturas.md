# 0017 — Hiladas continuas: curvas de nivel de un campo de alturas sobre la red

**Estado:** propuesta — 2026-11-08. En construcción; ningún render la usa aún.

## Problema

El modelo por celdas (`granada/celdas.py`) rellena cada una de las 105 caras de
la red de medinas como una cupulita propia, con hiladas concéntricas que se
cierran hacia su centro, y posa las celdas sobre el cono medido. Ninguna hilada
cruza de una celda a otra. El resultado se lee como 105 abanicos radiales
sueltos.

La cúpula real no es así. La sección de AA-415_23 mide **24 ± 1 hiladas**
horizontales (`docs/estratificacion.md`), y la foto de Commons (entrada 19 de
`docs/fuentes.md`) y las maquetas de Ferrer (entrada 12) muestran filas de
celdas con frente en arco que vuelan sobre la de abajo. El modelo de anillos
(`granada/cupula.py`) sí tiene hiladas continuas, pero su planta es una
estrella genérica, no la red medida.

Lo que no tenemos, y no vamos a tener, es la cota de cada tramo de la red: el
bloqueo `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` sigue vigente sobre el dato
histórico. Ninguna fuente publicada da una medición por puntos.

## Decisión

Las hiladas se definen como **curvas de nivel de un campo de alturas** sobre la
planta, cortadas a las cotas de hilada medidas:

    H(x, y) = cono(r) + A · f(d(x, y))

- `cono(r)` es el cono medido: `(RADIO_BASE − r) · PENDIENTE`, con las
  constantes de `granada/cupula.py`;
- `d` es la distancia al punto más cercano de una arista de la red registrada
  (`datos/red_medinas.json` con `datos/registro_red.json`), y vale 0 sobre el
  contorno de la red, de modo que fuera de ella el campo es el cono;
- `f` y `A` son elección.

Se sigue la propuesta del usuario del 2026-11-08: las cotas **se suponen**
siguiendo un orden lógico, y se declaran como tal.

Los dos extremos del parámetro son los dos modelos que ya existen:

- con `A = 0` las curvas son anillos concéntricos: el modelo de anillos;
- con `A` grande cada cara cierra en su propia cupulita: el modelo por celdas.

Entre ambos, las hiladas bajas dan la vuelta entera, se quiebran en estrella
al seguir la red y, cerca de la cima de cada cara, se parten en lazos que
cierran solos.

## Qué es dato y qué es elección

| | valor | naturaleza |
|---|---|---|
| radio de arranque, pendiente, paso vertical de hilada | `granada/cupula.py` (`datos/niveles_aproximados.json`) | medido sobre la sección |
| planta de la red y su registro | `datos/red_medinas.json`, `datos/registro_red.json` | figura 128 de la tesis; la mitad inferior por reflexión |
| alfabeto de piezas | `granada/piezas.py` | Jones y Goury, decisión 0016 |
| total de piezas | 5416 | Jones y Goury, entrada 18 |
| forma de `f`, amplitud `A`, signo (aristas como valles o crestas) | por calibrar | **elección** |

Las constantes de `granada/cupula.py` son las del 2026-08-28 (23 hiladas,
paso vertical 0,203 m, radio 3,64 m); `estratificacion.md` las rehízo el
2026-08-26 en 24 ± 1, 0,198 m y 3,7 m. Se usan las del modelo para no mezclar
dos calibraciones; la diferencia queda como sensibilidad conocida.

## Pasos y controles

1. **Campo y curvas** (`granada/campo.py`). Control: con `A = 0`, una sola
   curva cerrada por cota, circular, de radio `RADIO_BASE − z / PENDIENTE`.
2. **Piezas a lo largo de una polilínea cerrada cualquiera.** Hoy
   `en_contorno` exige una planta estrellada desde el centro. Riesgo técnico
   principal: solapes y huecos en las esquinas cóncavas.
3. **Cierres.** Un lazo sin sitio para una pieza se tapa con una cupulilla de
   tamaño de pieza. Los 16 cupulines del anillo exterior se conservan.
4. **Calibrar `A`** contra el total de 5416 piezas, la ortoimagen
   (`scripts/contrastar_ortoimagen.py`) y la foto de Commons, probando los dos
   signos.
5. **Validar el alzado** cortando la malla en sección y contando hiladas
   frente a las medidas, y con una vista oblicua comparable a `Ferrer_4`.

## Lo que esto NO hace

- No firma ningún salto: las cotas salen del campo, que es una hipótesis.
- No dice que la red sea una curva de nivel de nada en la obra real.
- No sustituye al modelo por celdas hasta que pase los controles del paso 5.
