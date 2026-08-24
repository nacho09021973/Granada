# El teselado: lo que dice la tesis

Fuente leída directamente el 2026-08-24: **Ferrer Pérez-Blanco, Ignacio (2023),
*Mocárabes de La Alhambra. Forma, dibujo y configuración arquitectónica*,
tesis doctoral, Universidad de Sevilla, director Antonio Gámiz Gordo, 491 pp.**
Defendida el 31-01-2023, sobresaliente cum laude. Acceso abierto en idUS,
handle `11441/143321`.

Nota de derechos: la tesis es de acceso abierto, pero **sus figuras son obra
del autor**. Aquí se citan y se usan como referencia para construir geometría
propia; **no se redistribuye ninguna imagen suya en este repositorio**.

---

## Lo que corrige de lo que yo tenía

**1. La plantilla de López de Arenas que se cita habitualmente no es suya.**

> «una reinterpretación de la plantilla de López de Arenas, que difiere de la
> que hoy se le suele asociar, **que este nunca dibujó**, y corresponde mejor a
> las proporciones de los mocárabes de la Alhambra»

Procede del dibujo de Mariátegui en las notas de la tercera edición de 1867,
interpretando el texto. Distintos investigadores usan hoy plantillas distintas
atribuidas al mismo autor. Y Nuere constata que López de Arenas «en múltiples
ocasiones no era claro en sus explicaciones, o simple y llanamente cometió
errores».

Consecuencia para `docs/fuentes.md` entrada 1: los tres perfiles planos que
tomé de allí son la versión simplificada y heredada, no la fuente primaria.

**2. Es Fray Andrés de San Miguel, no López de Arenas**, quien «corresponde
mejor a los mocárabes de la Alhambra».

**3. La familia de piezas es mucho más amplia** que las tres figuras, y
«diferente de aquellas deducidas de los manuscritos».

---

## El sistema, tal como lo expone la tesis

### Teselado, no coronas

> «los mocárabes occidentales se rigen por un **teselado de figuras planas**,
> las cuales tienen **ángulos fijos internos**»

Frente al sistema oriental (al-Kāshī), de trama radial, donde «la misma
tipología de pieza tiene en planta varios ángulos».

### Cuatro direcciones

> «hay **cuatro direcciones principales para las medinas**, las dos principales
> de los lados y las dos a 45° de las anteriores»

Retícula cuadrada más diagonales. Los nudos pueden tomar figuras más complejas,
como almendras.

### Las figuras planas y sus ángulos

- **medio cuadrado**: ángulo opuesto **45°**
- **triángulo de las jairas**: ángulo opuesto **67,5°**
- **C siempre en figura de rombo**; D es C duplicada por simetría por su lado
  menor, dando el rombo completo

Correspondencia con lo que ya está programado en `granada/celda.py` desde la
Fase 2a, que resulta ser correcto:

| tesis | código | comprobación |
|---|---|---|
| A, medio cuadrado | `cuna(R16, 4)` | ápice 90°, catetos 1, hipotenusa² = 2 |
| C, media jaira | `cuna(R16, 2)` | ápice 45°, base 67,5°, base² = 2 − √2 |
| D, jaira (rombo completo) | `rombo(R16, 2)` | rombo de 45°/135°, lados 1 |

Las piezas estaban bien desde el principio. Lo que estaba mal era el montaje:
`trapecio` y la corona polar, que me inventé y que hay que retirar.

### La familia de siete

Clasificación de Jones y Goury, que la tesis considera «la más coherente, así
como científica»: figuras A, B, C, D × topologías 1–4, dando siete mocárabes.

| pieza | nombre de oficio |
|---|---|
| A1 | medios cuadrados |
| A2 | atacias |
| A3 | medios cuadrados de dos niveles |
| B4 | conzas |
| C1 | medias jairas |
| C2 | dumbaques |
| D3 | jairas de dos niveles |

Hay además topologías 6 y 7 —«jairas ahorcadas y transversales»—, combinaciones
de la topología 1.

**Dato que rompe mi modelo por completo: A3 y D3 abarcan DOS niveles.** No todas
las celdas viven en una sola hilada.

### Los perfiles: son dos, y van en paralelo

No hay un perfil único. Hay **plantilla de doble perfil**, y cada pieza usa uno
u otro como principal:

- **perfil mayor**, dividido en quintos, punto más alto a **7P**
- **perfil menor**, dividido en séptimos, a **7,5P**
- **el nivel siguiente, a 8P**

Los perfiles de piezas vecinas se mantienen **paralelos** — un rasgo que la
tesis observa en la Alhambra y que Jones y Goury simplificaron al término
«curva».

Consecuencia para `granada/adaraja.py`: la cónica racional de un solo mando de
profundidad no es el modelo correcto. Hacen falta dos perfiles, y la elección
de cuál usa cada pieza.

### La pendiente: mi medición encaja

> «los diferentes perfiles vistos de López de Arenas y Fray Andrés comportan
> diferentes pendientes que **se mueven en torno a los 60°**»

Pero la pendiente **global** de un conjunto no es la de una pieza suelta. Sale
de combinar tres posiciones en planta:

- ángulo principal a 90° respecto de la pared: el perfil está en verdadera
  magnitud;
- a 45°: pendiente mayor respecto de la sección ortogonal;
- una tercera posición en la que **la pendiente se anula**, subiendo y bajando
  los perfiles mutuamente.

> «obtenemos la base para combinarlas entre ellas y obtener **distintas
> pendientes globales**»

Lo medido en `docs/estratificacion.md` —52° sobre la horizontal, o 38° sobre la
vertical— es por tanto el compuesto, no el perfil suelto. **No hay
contradicción**: los 60° son de la pieza, mis 52° del conjunto, y la diferencia
la explican los niveles que anulan pendiente.

---

## La cúpula de las Dos Hermanas en concreto

> «Una de las **más complejas** y de la que hay diferentes dibujos, de distintos
> autores, es la sala de las Dos Hermanas. Jones y Goury dibujaron en la mitad
> inferior de su planta, una trama de lo que en principio, podría ser la medina
> de esta cúpula. **Diferentes autores han presentado distintas plantas**, por
> lo que se muestra aquí una propuesta propia»

La figura 128 (p. 229 impresa, 236 del PDF) monta las dos mitades del octógono:
arriba la propuesta de la tesis, abajo el dibujo de Jones y Goury (1842-45).

El teselado que se ve: **octógonos grandes** y **cuadrados** en la zona
exterior, con subdivisión progresivamente más fina hacia el centro, y pequeños
cuadrados y rombos en la corona interior. Contorno octogonal, coherente con lo
medido sobre la ortoimagen.

**Aviso importante sobre el módulo**: esta cúpula rompe el principio de
correspondencia uno a uno entre mocárabes a ambos lados de una medina. La tesis
documenta un frente que pasa de proporción **7P a 10P** en el grupo siguiente,
«lo que puede resultar en composiciones en las que hay **mocárabes de distinto
módulo**». Un modelo de celda uniforme no puede reproducirla.

Y una advertencia general del propio autor sobre sus principios de agrupación:

> «Estos puntos [...] no deben tomarse como reglas fijas. Forman [...] un marco
> de uso genérico, que **los artesanos incumplirán a voluntad** en casos
> precisos.»

---

## Qué queda por hacer

1. Digitalizar la planta de la figura 128 y ajustarla a la retícula de Z[ζ₁₆].
   La geometría resultante será propia; la fuente se cita.
2. Retirar `trapecio` y la estratificación por coronas.
3. Rehacer el perfil como plantilla de doble perfil (7P / 7,5P, nivel a 8P).
4. Asignar nivel a cada tesela, contemplando que A3 y D3 abarcan dos.
5. Contrastar la planta reconstruida **superpuesta sobre la ortoimagen** antes
   de levantar nada en 3D.

---

## Digitalización y registro sobre la ortoimagen (2026-08-24)

La planta de la figura 128 (mitad superior, la propuesta propia de la tesis) se
extrajo del PDF a 600 ppi y se registró sobre la ortoimagen de AA-415_23.

**Parámetros del registro**: centro de la ortoimagen (2048, 2035), escala
1.969 px de orto por px de figura, eje de espejo de la figura en y = 1350.
La mitad inferior se genera reflejando la superior, que es lícito porque la
cúpula tiene simetría especular D8 (medida en `docs/policromia.md`).

**Cómo se ajustó, y por qué no es a ojo.** Se maximiza el **contraste local**
bajo las líneas de la red: los caballetes de yeso que separan celdas son
máximos locales de brillo, así que un registro correcto debe colocar las líneas
encima de ellos. Puntuar por brillo a secas no vale — se engaña acercando la
red al centro, que es más claro.

| configuración | contraste medio |
|---|---|
| **óptimo** | **+5.43** |
| desplazado 60 px | +0.16 |
| escala un 8 % mayor | −0.40 |

El ajuste solo puntúa en la posición correcta, y se desploma a cero en cuanto
se mueve. No es casualidad ni es apreciación visual.

**La confirmación más clara**: los **16 cupulines** de la cúpula caen cada uno
**dentro de una celda octogonal** de la red. No se impuso; sale del registro.

Resultado en `renders/planta_sobre_orto.png`.

**Lo que la red no es**: es la *medina*, la red principal, no el contorno de
cada celda. En la corona interior el techo real tiene subdivisiones más finas
que las que dibuja la red. Eso es esperable y no es un fallo del ajuste.
