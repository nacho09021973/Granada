# Estratificación medida sobre la sección de AA-415_23

La lámina de Almagro trae dos vistas: la ortoimagen cenital del techo, ya usada
para el orden de simetría (`fuentes.md`, sección 7), y la **sección norte-sur**.
De esta última sale todo lo de aquí. Medido el 2026-08-24.

## Calibración

Página A0 (2384 × 3370 pt), renderizada a 150 dpi → 4967 × 7021 px.

La escala gráfica del plano (0–10 m) mide 2361 px, es decir **236.1 px/m**. El
valor teórico para escala 1/25 a 150 dpi es 236.22 px/m. Coinciden al 0.05 %,
así que la calibración está confirmada por dos vías.

## Resultados

| magnitud | valor |
|---|---|
| altura de la cúpula de mocárabes | **4.67 m** |
| radio en el arranque | **3.64 m** |
| paso de hilada | **~20 cm** |
| número de hiladas | **~23** |
| pendiente dr/dh | **0.782 ± 0.016** |
| ángulo del cono respecto a la vertical | **38.0° ± 0.6°** |
| paso horizontal por hilada | **15.6 cm** |

Debajo de los 4.67 m el radio se estabiliza en 3.87 m: ahí acaba la cúpula y
empieza el tambor de las ventanas, de radio constante.

## Cómo se midió

**Paso de hilada, por dos métodos independientes que concuerdan:**

1. Autocorrelación del perfil vertical de luminancia en una franja central de
   280 px, quitada antes la tendencia lenta. Máximo en 47 px = **19.9 cm**, con
   r = +0.725, y su armónico en 95 px = 40.2 cm.
2. Detección directa de los escalones del radio en la silueta: 21 escalones
   entre h = 0.30 m y h = 4.46 m, paso medio **20.8 cm**.

**Silueta:** umbral contra el fondo blanco puro, tomando el píxel con tinta más
a la izquierda y más a la derecha de cada fila. La banda en blanco entre las dos
vistas (y = 2352–2540) fija el ápice.

**Pendiente:** ajuste por mínimos cuadrados de radio(h) sobre el tramo cónico
(0.25 m < h < 4.6 m). Da `radio = 0.7832·h − 0.014`, con residuo de 9.2 cm rms,
compatible con un perfil escalonado de 20 cm. La ordenada en el origen es
prácticamente nula: el cono converge en el ápice, sin desplazamiento.

El error de la pendiente está **inflado a propósito**. Los residuos de un perfil
escalonado están fuertemente correlacionados, así que el error nominal de un
ajuste con miles de filas es ficticio; se ha reescalado al número de hiladas
independientes (23). De ahí el ± 0.016.

## Lo que no es

Se probó si la pendiente correspondía a alguna constante del sistema:

| candidato | valor | desviación |
|---|---|---|
| 1/√2 | 0.7071 | **+10.8 %, a 4.7 σ — descartado** |
| 4/5 | 0.8000 | −2.1 %, a 1.1 σ |

**1/√2 queda descartado.** Lo había apuntado como hipótesis antes de ajustar
bien la recta, y los datos dicen que no. El 4/5 cae dentro del error, pero nada
autoriza a afirmar que sea la intención de diseño: podría serlo o podría ser
coincidencia a ese nivel de precisión. **No se privilegia ningún valor bonito**;
la razón se expone como parámetro con la medida por defecto.

## El modelo que se deduce

3.64 m de radio entre 23 hiladas dan **15.8 cm por hilada**, y el paso
horizontal medido es 15.6 cm. Coinciden. Eso da un modelo limpio:

> Cada hilada avanza **exactamente una unidad de planta** hacia el eje y sube
> **razón** unidades, con razón = 1/0.782 = 1.279.

Con lo cual el radio de cada hilada es un **entero** en unidades de planta, y la
planta entera sigue viviendo en Z[ζ_m] sin salirse. La unidad de planta vale
unos 15.7 cm.

Implementado en `granada/estratificacion.py`. La vertical se lleva en
`fractions.Fraction`: exacta y racional, sin coma flotante. Un punto en 3D es un
par (elemento de Z[ζ_m], Fraction).

Comprobación en `tests/test_estratificacion.py`: con u = 0.157 m el modelo da
radio 3.61 m y altura 4.62 m, contra los 3.64 y 4.67 medidos. Menos del 1 % de
diferencia.

## Advertencia

Esto es fotometría sobre una imagen ráster, igual que la medición del orden de
simetría. La silueta depende de un umbral, el perfil es escalonado y la propia
cúpula tiene deformaciones documentadas. Las cifras valen para construir un
modelo verosímil, **no** para afirmar cómo la trazó nadie en el siglo XIV.

El script usa Pillow y por eso no entra en `granada/`: el paquete mantiene cero
dependencias.
