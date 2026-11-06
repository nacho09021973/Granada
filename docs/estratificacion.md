# Estratificación medida sobre la sección de AA-415_23

La lámina de Almagro trae dos vistas: la ortoimagen cenital del techo, usada
para el orden de simetría (`fuentes.md`, sección 7), y la **sección norte-sur**.
De esta última sale todo lo de aquí.

**Medido el 2026-08-24 y rehecho el 2026-08-26** al doble de resolución. El
script es `scripts/medir_estratificacion.py` y los números crudos quedan en
`datos/estratificacion_medida.json`; la primera vez la medición fue ad hoc y no
se conservó código, que era el defecto más serio de esta página.

## Calibración

**Ya no se calibra midiendo.** La escala gráfica de la lámina son vectores con
coordenadas exactas dentro del PDF: 9449 unidades de flujo para 10 m, con la
matriz global `0.12`. De ahí 113,388 pt/m, y como la ortoimagen de la sección
ocupa 1492,44 pt con 6219 px:

> **472,488 px por metro real — 1 px = 2,116 mm.**

Es el número que puso el autor, no una lectura nuestra sobre el ráster. La
escala implícita sale 1/24,9995, a **+0,0019 %** del 1/25 nominal. Ver la
entrada 3 de `fuentes.md`.

El 2026-08-24 se midió sobre un render de la página A0 a 150 ppi, calibrado
leyendo la escala gráfica en la propia imagen: 236,1 px/m. **Exactamente la
mitad.**

## Resultados

| magnitud | 2026-08-24 (236 px/m) | **2026-08-26 (472 px/m)** |
|---|---|---|
| altura de la cúpula de mocárabes | 4,67 m | **4,8 ± 0,1 m** |
| radio en el arranque | 3,64 m | **3,7 ± 0,1 m** |
| radio del tambor | 3,87 m | **3,865 ± 0,003 m** |
| paso de hilada | ~20 cm | **19,8 ± 0,1 cm** |
| número de hiladas | ~23 | **24 ± 1** |
| pendiente dr/dh | 0,782 ± 0,016 | **0,789 ± 0,015** |
| ángulo del cono respecto a la vertical | 38,0° ± 0,6° | **38,3° ± 0,6°** |

Debajo de la cúpula el radio se estabiliza: ahí acaba el mocárabe y empieza el
tambor de las ventanas, de radio constante.

## Lo que hay que sacar de esta tabla

**No ha cambiado nada.** Todos los valores nuevos caen dentro del error de los
viejos. Duplicar la resolución ha confirmado la medición anterior sin
corregirla.

**Y el error tampoco baja.** La pendiente sigue con ± 0,015 frente al ± 0,016
de antes, aunque el píxel valga ahora 2,1 mm en vez de 4,2. El motivo es que el
límite nunca fue la resolución: el residuo del ajuste es de **9,3 cm rms**,
cuarenta veces el píxel. Lo que ensancha la barra es que el perfil es
escalonado y que la cúpula real está deformada, y eso no se arregla mirando más
de cerca. Conviene recordarlo antes de pedir más resolución para otra cosa.

Los dos únicos cambios que merecen mención son **la altura y el número de
hiladas**, y son la misma cosa: dónde acaba el cono depende del umbral. Entre
umbral 240 y 245 el final se mueve 98 px = 21 cm, que es **una hilada entera**.
De ahí el 24 ± 1: la última hilada es genuinamente ambigua sobre esta imagen,
no un problema de precisión. El «~23» anterior estaba dentro de esa ambigüedad.

## Cómo se mide

**Calibración**: constante derivada del PDF, arriba. No se lee de la imagen.

**Silueta**: umbral contra el fondo blanco, tomando el píxel con tinta más a la
izquierda y más a la derecha de cada fila. Se corre con **tres umbrales** (240,
245, 250) y la dispersión entre ellos es la incertidumbre sistemática que va en
la tabla. Es la fuente de error dominante y antes no se cuantificaba.

**Fin del cono**: primera fila a partir de la cual el radio ya no supera su
máximo previo en más de un píxel durante **hilada y media** seguidas. No se
elige a ojo. La ventana tiene que ser mayor que un paso de hilada: con media
hilada el detector se para en la primera huella y da 1,4 m de cúpula.

**Paso de hilada, por dos vías**:

1. **Autocorrelación** del perfil vertical de luminancia en una franja central
   de 60 cm, quitada antes la tendencia lenta. Máximo en 93–94 px = **19,7–19,9
   cm**, con r ≈ +0,60. Es el método robusto: da lo mismo con los tres umbrales
   y coincide con el 19,9 cm de la medición anterior.
2. **Escalones de la silueta**, contados **por lado**. El radio es
   (derecho − izquierdo)/2 y los dos bordes no escalonan a la vez, porque la
   sección real no es simétrica al milímetro; cada hilada aparece entonces como
   dos medios escalones en el radio. A 236 px/m eso se disimulaba, a 472 px/m
   ya no: contarlos sobre el radio combinado da 28 escalones y hunde el paso a
   14,7 cm. Por lado salen 27–29 escalones, y siguen siendo más que las hiladas
   —la textura de la ortofoto genera falsos positivos—, así que **este método se
   registra pero no se usa**. El paso bueno es el de la autocorrelación.

**Pendiente**: mínimos cuadrados de radio(h) sobre el tramo cónico. El error
está **inflado a propósito**: los residuos de un perfil escalonado están
fuertemente correlacionados, así que el error nominal de un ajuste con miles de
filas es ficticio y se reescala al número de hiladas independientes. Sin ese
reescalado saldría ± 0,003, que sería mentira.

## Lo que no es

Se probó si la pendiente correspondía a alguna constante del sistema:

| candidato | valor | desviación (2026-08-26) |
|---|---|---|
| 1/√2 | 0,7071 | **+11,6 %, a 5,5 σ — descartado** |
| 4/5 | 0,8000 | −1,4 %, a 0,7 σ |

**1/√2 sigue descartado**, y con más holgura que antes. El 4/5 sigue cayendo
dentro del error, y **sigue sin autorizar nada**: podría ser la intención de
diseño o podría ser coincidencia a este nivel de precisión. Que la medida más
fina lo confirme no lo convierte en un hallazgo — con ± 0,015 hay sitio para
muchas fracciones bonitas. No se privilegia ningún valor: la razón se expone
como parámetro con la medida por defecto.

## El modelo que se deduce

3,7 m de radio entre 24 hiladas dan **15,5 cm por hilada**, contra los 15,6 cm
de paso horizontal medido. Siguen coincidiendo. El modelo no cambia:

> Cada hilada avanza **exactamente una unidad de planta** hacia el eje y sube
> **razón** unidades, con razón = 1/0,789 = 1,267.

Con lo cual el radio de cada hilada es un **entero** en unidades de planta, y la
planta entera sigue viviendo en Z[ζ_m] sin salirse. La unidad de planta vale
unos 15,5 cm.

Implementado en `granada/estratificacion.py`, hoy marcado obsoleto por otra
razón —la planta correcta es un teselado con niveles topológicos, no anillos
concéntricos—. Su razón por defecto, 1,279, sigue dentro del error de la nueva
medida y no se toca.

## Advertencia

Esto es fotometría sobre una ortofoto, igual que la medición del orden de
simetría. La silueta depende de un umbral, el perfil es escalonado y la propia
cúpula tiene deformaciones documentadas. Las cifras valen para construir un
modelo verosímil, **no** para afirmar cómo la trazó nadie en el siglo XIV.

El script usa Pillow y numpy, y por eso vive en `scripts/` y no en `granada/`:
el paquete mantiene cero dependencias.
