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

### Cómo debe representarse el nivel

Leídas directamente las secciones 3.2.5 (pp. 254–256 impresas) y 3.3.2
(pp. 269–272) de la tesis:

- las líneas de nivel son una representación **analítica**, posterior al
  diseño artesanal; los descansos introducen ramificaciones y bucles;
- una misma planta puede admitir variantes con niveles diferentes;
- la propuesta del autor usa, a escala media, **una o varias flechas dentro de
  cada figura** para codificar sentido, tipología y niveles de ascenso;
- una arista compartida no debe recibir necesariamente un único sentido
  global: la indicación pertenece a cada lado/pieza;
- el esquema identifica tipos, pero no pretende definir toda la geometría de
  cada mocárabe ni agotar las singularidades de la Alhambra.

Consecuencia de datos: la figura 128 específica de Dos Hermanas da la red de
medinas pero **no incluye las flechas ni las cotas** de la propuesta del
capítulo 3. No se pueden leer de ella los niveles absolutos.

Consecuencia de código: `granada/niveles.py` separa el tipo/topología de la
pieza de su nivel absoluto, propaga diferencias enteras y deja los componentes
sin ancla explícitamente sin resolver. A3 y D3 salvan dos niveles; las otras
cinco piezas, uno. Decisión completa en `docs/decisiones/0003-niveles-topologicos.md`.

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

1. Conseguir una planta con flechas o cotas de nivel de *esta* cúpula, o una
   fuente que permita firmar el salto de cada vecindad.
2. Retirar `trapecio` y la estratificación por coronas.
3. Rehacer el perfil como plantilla de doble perfil (7P / 7,5P, nivel a 8P).
4. Asignar nivel a cada tesela, contemplando que A3 y D3 abarcan dos. Las
   caras y sus 227 vecindades ya están (2026-08-25); falta el signo de cada
   paso.
5. Contrastar la planta levantada **superpuesta sobre la ortoimagen** antes
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

---

## Extracción de la red: nudos, aristas y módulo (2026-08-24)

La primera extracción, por transiciones locales del esqueleto, produjo **71
nudos y 48 aristas** repartidos en 24 componentes, con 11 nudos aislados. Sirvió
para auditar direcciones y módulos sobre un subconjunto, pero no para propagar
niveles.

La extracción completa sigue cada camino entre regiones de cruce y conserva
los giros reales con simplificación Ramer-Douglas-Peucker. Usa solo la mitad
superior de la figura 128 —la propuesta del autor— y genera la inferior por
reflexión D8; no mezcla el dibujo de Jones y Goury. El octógono punteado
editorial queda fuera.

Resultado actual en `datos/red_medinas.json`, en metros y con origen próximo al
centro de la cúpula: **323 nudos, 427 aristas, una componente conexa, 105 ciclos
independientes y 24 terminales de borde**. No aparecen fragmentos menores de 5
px y la topología es idéntica para umbrales de gris 170, 200 y 230. Se reproduce
con `scripts/completar_red_medinas.py`; decisión y techo de afirmación en
`docs/decisiones/0004-red-medinas-completa.md`.

### Advertencia sobre «ajustar a la retícula»

**Z[ζ₁₆] es denso en el plano.** No es una retícula discreta: cualquier punto
se aproxima tan bien como se quiera. «Redondear al punto de rejilla más
próximo» no significa nada aquí.

Lo comprobé empíricamente antes de seguir. Permitiendo coeficientes de hasta
40, los nudos ajustan con residuo de 0.6 mm… **y unos puntos aleatorios ajustan
igual de bien (1.16×)**. El test no discrimina nada. Por eso hay que acotar los
coeficientes, y por eso todo test aquí lleva su control.

### Lo que sí se sostiene: las cuatro direcciones

Primer intento, tomando como aristas *todos* los pares de nudos próximos:
resultado negativo, histograma casi plano. El fallo era mío: la mayoría de esos
pares no están unidos por ninguna medina.

La auditoría inicial, sobre las 48 aristas recuperadas entonces, comparó los
tramos **reales** con dos controles:

| | aristas reales | pares próximos | azar |
|---|---|---|---|
| desviación **mediana** al múltiplo de 45° | **1.23°** | 7.94° | 11.09° |
| dentro de 7° | **70.8 %** | 47.8 % | 30.3 % |

En la red completa, que además conserva los giros pequeños de las figuras
interiores, la desviación mediana es **2,20°** y el **77,3 %** de los 427
tramos queda a 5° o menos. Las cuatro direcciones de medina que enuncia la tesis
quedan **confirmadas sobre la medición**, no solo citadas.

### El módulo: no hay uno solo

Las cifras de este apartado proceden del subconjunto inicial de 48 aristas y
son provisionales hasta repetir el control de módulo sobre la red completa.

Las longitudes se agrupan con claridad (≈0.21, ≈0.33, ≈0.44, ≈0.76, ≈1.1 m),
pero **ningún módulo único las explica**: el mejor deja un residuo del 18–23 %
del propio módulo. Eso no es un fallo de la medición, es lo que la tesis ya
advierte para esta cúpula en concreto — el frente que pasa de 7P a 10P, y
«composiciones en las que hay mocárabes de distinto módulo».

### La razón entre direcciones

| | valor |
|---|---|
| mediana de aristas ortogonales (15) | 0.561 m |
| mediana de aristas diagonales (22) | 0.430 m |
| **razón diagonal / ortogonal** | **0.7679** |
| 2·sin(π/8) = √(2 − √2) | 0.7654 |

Coincide al 0.3 %. Es **el mismo elemento** que aparece en el primer test del
núcleo aritmético: la cuerda de 45°, cuyo cuadrado es exactamente 2 − √2, que
vive en Z[ζ₁₆] y no en Z[ζ₈], y que resultó ser la base de la cuña canónica
`cuna(R16, 2)`.

Precaución: es una razón entre medianas de 15 y 22 aristas trazadas de una
figura impresa. El acuerdo al 0.3 % es más preciso de lo que el método merece.
Lo defendible es que la razón vale ~0.77 y **no** 1 ni √2.

---

## Contraste de la sombra como indicio de nivel (2026-08-24)

Se probó primero el caso barato indicado en `PROXIMOS-PASOS.md`, pero contra un
extremo geométrico conocido en vez de asignar niveles por inspección: los 16
cupulines exteriores frente a 16 parches intermedios al mismo radio.

| medida | resultado |
|---|---:|
| cupulines más oscuros que su control | **15/16** |
| mediana control − cupulín (0–255) | **+16,99** |
| Wilcoxon pareado unilateral | **p = 3,05·10⁻⁵** |
| máximo del control de fase | a **1,24°** del eje documentado |
| percentil de la fase documentada | **90,6** |

La señal existe y confirma que la sombra puede servir como evidencia auxiliar.
No basta para asignar un nivel entero: al mover el radio de muestreo a 1350 px
el efecto baja a +7,36 y 12/16 pares (parches de 90 px), y siguen mezclándose
orientación, pigmento, suciedad e iluminación. Resultado exacto y sensibilidad
en `datos/contraste_sombra_niveles.json`; reproducción con
`scripts/analizar_sombra_niveles.py`.

**Terminal actual**: `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS`. La fotometría
ordena extremos, pero no calibra los 23 niveles. La red ya es conexa y expone
24 anclas candidatas en el borde; la figura 128 carece de flechas/cotas y el
grafo, por sí solo, no dice si cada paso asciende, descansa o desciende.


---

## Las caras de la red: teselas candidatas (2026-08-25)

La red de medinas es un grafo plano dibujado; sus **caras** son las regiones
que las medinas delimitan. Extraídas por rotación de semiaristas
(`granada/caras.py`, sin dependencias): **105 caras interiores**, Euler
`V − E + F = 2`, **cero cruces** de aristas en los 90 951 pares, y el área de
las caras iguala la del contorno, 30,690 m². El recuento coincide con los 105
ciclos independientes que ya daba la decisión 0004, como tenía que ser.

### Qué se puede leer de la planta y qué no

De una planta se lee la **figura** (medio cuadrado, media jaira, jaira,
cuadrado, octógono). La **topología** de la pieza —A1, A2, A3, B4, C1, C2,
D3— no se lee de la planta: es lo que las flechas de la planta propuesta
codifican, y la figura 128 no las trae. El módulo clasifica figuras y **nunca**
asigna un `TipoMocarabe`.

### Clasificación, con tolerancia heredada y no elegida

La tolerancia angular de cada cara es `2 · resolución / lado más corto`, con
la resolución de 2 px de la simplificación con la que se extrajo la red. No es
un mando que se pueda subir hasta que salga el resultado deseado.

| figura | caras | ajuste angular | margen frente a la mejor plantilla ajena |
|---|---:|---:|---:|
| medio cuadrado (A) | **8** | ≤ 2,35° | 3,9× |
| octógono regular (centro) | **1** | 0,76° | 6,5× |
| cuadrado | 16 | ≤ 8,89° | **1,16×** |
| sin clasificar | 80 | — | — |

Los 8 medios cuadrados rodean el octógono central y forman con él la estrella
de ocho puntas del centro. Sus azimuts son una **órbita C8 exacta** —0,4°,
45,7°, 90,5°… 315,0°— y la extracción solo impuso simetría de espejo, así que
esa periodicidad de 45° sale del dibujo, no del método.

Los 16 cuadrados quedan marcados `al_limite_de_resolucion`: su lado mide
8,1–9,5 px de la figura, del orden del grosor de cruce del propio esqueleto, y
su ventana de tolerancia llega a 28°. Están etiquetados, no confirmados.

### Las 80 caras sin figura

No son ruido: se agrupan por área en familias de 16, 24, 8, 8, 8 y 16 copias.
Dentro de una familia el número de lados varía —7, 8 o 9 en la de 0,85 m²—
porque cada copia se digitaliza con un vértice de más o de menos; el área no.
**51 de las 80 ni siquiera son convexas**, y las figuras del sistema
occidental lo son. Son regiones que la figura 128 no subdivide, exactamente lo
que ya se advertía arriba sobre la corona interior. Un teselado completo exige
una planta más fina, no una tolerancia más generosa.

En el dibujo se aprecian además, en los cruces de la banda intermedia, figuras
pequeñas y alargadas del tipo que la tesis llama **almendras** al describir los
nudos. Se deja anotado como observación; no se clasifica.

### Las vecindades, y por qué van sin firmar

Las caras comparten **227 vecindades**, 16 de ellas contra el contorno
exterior; las 24 aristas colgantes son los terminales de borde y no separan
dos caras. Cada vecindad se guarda con `"salto": null`.

Ese `null` es el dato, no un hueco por rellenar: que dos teselas compartan una
medina no dice si entre ellas hay ascenso, descanso o descenso.
`RelacionVecindad` exige citar evidencia para firmar un salto y
`restricciones_firmadas` falla mientras quede una sin firmar — no hay
propagación parcial que aparente una planta resuelta.

Dato: `datos/caras_red.json`. Mapa: `renders/caras_red.svg`. Decisión y techo
de afirmación: `docs/decisiones/0005-caras-y-vecindades.md`.


---

## Qué reglas de nivel son siquiera posibles (2026-08-25)

Con las caras ya identificadas se puede hacer algo barato antes de buscar
fuentes: coger las reglas que uno propondría de memoria e intentar
**refutarlas**. Alrededor de cualquier ciclo del grafo de vecindades los saltos
firmados tienen que sumar cero.

El dual honesto son **105 caras, 211 vecindades y 107 ciclos independientes**;
el contorno exterior queda fuera por ser un nodo artificial que uniría las 16
caras del borde.

| regla | veredicto |
|---|---|
| toda medina separa dos niveles consecutivos | **imposible** |
| se sube un nivel al cruzar hacia el centro | **imposible**, 67 ciclos rotos |
| las de lado suben, las diagonales descansan | **imposible**, 67 ciclos rotos |
| control: ninguna medina cambia de nivel | consistente |
| control: coronas cuantizadas al paso de 20 cm | consistente |

Los controles positivos pasan, de modo que el test no rechaza por costumbre. Y
el segundo recuerda que **consistente no es correcto**: el modelo de coronas
cierra todos los ciclos y sigue rechazado por contradecir el teselado.

### El teorema del triángulo

La primera regla no cae por casualidad, sino porque el grafo de vecindades no
es bipartito:

> En tres teselas mutuamente vecinas los tres saltos suman cero. Si los tres
> valieran ±1 la suma sería impar y nunca cerraría. Al menos una de las tres
> medinas es un **descanso** o **salva dos niveles**.

La planta tiene **54 triángulos** así, y 16 sobreviven al control más duro
—descartar toda medina compartida de menos de 30 px, por encima de la mediana
del dato—; son el mismo motivo repetido 16 veces alrededor de la cúpula.

Lo que la tesis documenta por su cuenta son exactamente esas dos cosas: los
descansos de la sección 3.2.5 y las piezas **A3 y D3**, que salvan dos niveles.
La topología de la planta digitalizada lo exige sin usar fotometría, ni radio,
ni ninguna suposición sobre la altura.

No firma ni un solo salto: `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` sigue.
Lo ganado es que tres atajos quedan cerrados con testigo y no por prudencia.

Dato: `datos/reglas_de_nivel.json`. Decisión: `docs/decisiones/0006-reglas-de-nivel-refutadas.md`.
