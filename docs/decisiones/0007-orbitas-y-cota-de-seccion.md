# 0007 — Once órbitas, la sección de clase A, y hasta dónde llega

**Estado:** aceptada — 2026-08-25

## Contexto

La decisión 0006 cerró tres reglas de nivel y dejó el bloqueo intacto: hay 211
vecindades interiores y ninguna firmada. Antes de seguir buscando fuentes
convenía medir **cuánto trabajo hay realmente**, porque «211 saltos» exagera el
problema:

- Los 211 saltos no son grados de libertad. Quedan determinados por los niveles
  de las 105 caras, y mientras no haya una cota absoluta un nivel es libre. La
  cuenta cierra con los ciclos ya medidos: **211 − 107 = 104 = 105 − 1**.
- Si además la nivelación respeta la simetría medida de la cúpula —C8 exacta
  más espejo, es decir el diédrico de orden 16—, las incógnitas bajan al número
  de **órbitas de caras** bajo ese grupo.

Esa segunda reducción es una **hipótesis sobre la cúpula, no un dato**. Se
enuncia aquí para poder falsarla contra los mismos 107 ciclos el día que haya
un solo salto firmado; no se usa como aval de nada.

## Decisión de método

1. **El grupo es el diédrico de orden 16**, C8 medida sobre la ortoimagen
   (`fuentes.md`, sección 7) más el espejo. No se supone: se hereda de una
   medición anterior.
2. **El punto fijo es el centroide de área del octógono central**, no el
   `(0, 0)` del registro, que es una convención del recorte.
3. **El centroide es de área, no media de vértices.** La media de vértices se
   desplaza cuando la simplificación RDP deja un vértice de más en un lado del
   contorno; el centroide de área no. Comparar una cara con su copia simétrica
   —digitalizadas por separado, a veces con distinto número de vértices— exige
   el de área. Es la misma cautela que ya obligó a rehacer el emparejamiento de
   triángulos en la decisión 0006.
4. **El emparejamiento se audita solo, sin elegir tolerancia a ojo.** Un tamaño
   de órbita tiene que dividir al orden del grupo. Un emparejamiento roto
   incumple esa condición y se delata; por eso `orbitas_por_simetria` devuelve
   los tamaños tal cual en vez de forzarlos.
5. **Basta un representante por clase de conjugación de espejo.** D8 tiene ocho
   ejes, en dos clases: los que pasan por los **puntos medios de dos lados
   opuestos** del octógono central (0°, 45°, 90°, 135°) y los que pasan por dos
   **vértices** opuestos (22,5°, 67,5°, …). Una órbita es cerrada bajo el
   grupo, así que si algún eje de una clase corta alguna de sus caras, el
   representante también. Se llaman clase **A** (0°) y clase **B** (22,5°).
6. **Un corte tiene que ser resoluble.** Que una cara asome al otro lado del
   eje por centésimas de píxel no es un corte del dibujo: es ruido de la
   digitalización. `corta_al_eje` acepta un margen y el script exige **un píxel
   del dibujo** (13,8 mm) a los dos lados. Sin ese filtro se cuentan cortes que
   no existen — y de hecho se contaban: ver más abajo.

## Resultado: once órbitas

| órbita | tamaño | área media (m²) | radio medio (m) | figura | corta A | corta B |
|---:|---:|---:|---:|---|:--:|:--:|
| 10 | 1 | 1,1773 | 0,000 | octógono | sí | sí |
| 9 | 8 | 0,0616 | 0,679 | medio cuadrado | sí | *roce* |
| 8 | 8 | 0,2667 | 0,965 | — | *roce* | sí |
| 6 | 8 | 0,4967 | 1,320 | — | sí | *roce* |
| 7 | 16 | 0,0542 | 1,560 | — | no | *roce* |
| 4 | 8 | 0,2165 | 1,912 | — | sí | no |
| 5 | 16 | 0,0164 | 1,994 | cuadrado | **no** | **no** |
| 2 | 16 | 0,2175 | 2,027 | — | **no** | **no** |
| 3 | 8 | 0,3724 | 2,087 | — | no | sí |
| 0 | 8 | 0,8658 | 2,646 | — | sí | no |
| 1 | 8 | 0,8331 | 2,871 | — | no | sí |

Tamaños `[16, 16, 16, 8, 8, 8, 8, 8, 8, 8, 1]`, suma **105**, todos divisores de
16. Las tres órbitas de 16 tienen estabilizador trivial: ninguna de sus caras
está centrada sobre un eje.

**La cadena de reducción, entera:**

| paso | incógnitas |
|---|---:|
| saltos entre caras | 211 |
| niveles de cara, quitados los 107 ciclos | 104 |
| órbitas, **si** la nivelación respeta D8 | **11** |
| lo que queda tras la sección de clase A que existe | **6** |

### Control de tolerancias

Emparejar copias digitalizadas por separado exige tolerancia, y una tolerancia
elegida a conveniencia es un parámetro libre disfrazado. Barrido de 6 × 5 = 30
combinaciones (área de 0,15 a 0,50; distancia de 6 a 15 cm):

- **25 combinaciones** dan tamaños admisibles, y las 25 dan **11 órbitas**.
- Las **5** que fallan son exactamente las de tolerancia de área 0,15, la más
  estrecha, y fallan de forma visible: dan 12 órbitas, una de ellas de un
  tamaño que no divide a 16. El criterio las descarta solo.

El once no depende de dónde se ponga la tolerancia dentro de la meseta.

## La clase de eje la fija la arquitectura, no la conveniencia

La única sección publicada de esta cúpula es la de Almagro Gorbea, y su cajetín
dice **«SECCION NORTE-SUR»**. El norte-sur es el eje propio de la sala —el que va
del Mirador de Lindaraja al Patio de los Leones—, y es perpendicular a dos de
sus paredes. En la planta registrada, 0° y 90° son dos de las cuatro direcciones
preferentes de la red (0°, 45°, 90° y 135°, con el 77 % de las aristas a menos
de 5° de alguna de ellas), y el octógono central tiene sus vértices a 22,1°,
66,6°, 111,8° …, de modo que sus **lados** miran a 0° y 90°: a las paredes.

No hace falta decidir aquí si el norte-sur del edificio cae en el 0° o en el 90°
del registro. Los dos están en la **clase A**, y dentro de una clase el recuento
de órbitas es el mismo. La sección de Almagro es de clase A por la planta de la
sala, no por cómo se orientó el recorte. Cuál de los cuatro ejes es sí importa
para otra cosa —para cuánto se apoya la lectura en la mitad pegada de la red— y
tiene sección propia más abajo.

Y la clase A es la peor de las dos:

| clase de eje | órbitas tocadas | de ellas, cortes resolubles | caras determinadas | órbitas restantes |
|---|---:|---:|---:|---:|
| A — por lados (0°), la que existe | 6 | **5** | **33** de 105 | **6** |
| B — por vértices (22,5°), la que no | 7 | 4 | 25 de 105 | 7 |

No se elige la clase que más resuelve. Se toma la que Almagro dibujó.

### El filtro de resolución quita un corte de cada clase, y no es un detalle

Sin margen, el eje A corta 6 órbitas y el B, 7. Con el margen de un píxel:

| eje | cara | margen a cada lado |
|---|---|---:|
| A | `c057`, `c058` (órbita 8) | **0,032 px** = 0,44 mm |
| B | `c069` (6), `c070` (7), `c055` (9) | 0,13 px |
| B | `c064` (9), `c043` (7), `c044` (6) | 0,31–0,41 px |

Frente a eso, el corte más justo de los que **sí** quedan mide **17,6 px**. No
hay zona gris: entre las dos poblaciones hay un factor de cuarenta. Los que caen
son tangencias del trazado, no cortes.

La consecuencia es concreta: **la órbita 8 no la alcanza la sección
norte-sur**, aunque el criterio ingenuo diga que sí. Y la clase B pierde tres
órbitas de golpe.

## Las seis que quedan

Con el filtro de resolución, la sección de clase A determina las órbitas
**10, 9, 6, 4 y 0** —33 caras— y deja sin cota las **6** restantes:
**1, 2, 3, 5, 7 y 8**, que son **72 de las 105 caras**, el 69 %.

Y hay tres órbitas que **no alcanza ningún eje de simetría**, ni de clase A ni
de clase B: las **2, 5 y 7**. Son exactamente **las tres órbitas de 16**, 48
caras, el 46 % de la planta. Tiene sentido que sean esas: son las de
estabilizador trivial, las que no tienen ninguna copia sentada sobre un eje.

> **Ninguna sección diametral por un eje de simetría de esta cúpula corta una
> sola cara de las órbitas 2, 5 y 7.** Para ellas no hace falta otra sección:
> hace falta otra clase de evidencia.

## Qué eje de la clase A es, y por qué casi da igual

La clase A tiene cuatro ejes —0°, 45°, 90° y 135°— y hasta aquí se ha usado el
0° como representante. Para el recuento de órbitas eso es lícito por definición
de clase. Para decir **qué caras** corta la sección, no: son caras distintas.

Lo primero es medir cuánto depende el resultado del eje concreto:

| eje | caras tocadas | órbitas | resolubles | fronteras radiales (m) | residuo contra la sección |
|---:|---:|---:|---:|---|---:|
| 0° | 11 | 6 | 5 · {0,4,6,9,10} | 0,5965 · 0,8438 · 1,6813 · 2,1508 · 3,2951 | **9,5 mm** |
| 45° | 11 | 6 | 5 · {0,4,6,9,10} | 0,5966 · 0,8455 · 1,6891 · 2,1563 · 3,2880 | 9,9 mm |
| 90° | 11 | 6 | 5 · {0,4,6,9,10} | 0,5938 · 0,8464 · 1,6795 · 2,1578 · 3,2926 | 9,9 mm |
| 135° | 11 | 6 | 5 · {0,4,6,9,10} | 0,5975 · 0,8455 · 1,6817 · 2,1563 · 3,2878 | 10,6 mm |

Las mismas órbitas, las mismas cinco resolubles y el mismo ajuste contra la
sección: **9,5 – 10,6 mm** para los cuatro. Y los cuatro ejes de la clase B dan
**72,6 – 73,7 mm**: el control negativo tampoco depende del representante.
**Nada de lo que sigue depende de qué eje de la clase A sea el norte-sur.**

Lo que sí conviene no maquillar es la horquilla entre los cuatro: de **2,6 a
9,6 mm** según la frontera. Es del mismo orden que el residuo del ajuste, o sea
que la propia indeterminación del eje pone tanto ruido como el ajuste tiene. Ahí
está el suelo de lo que este dibujo puede dar, y por eso no hay nada que afinar
por debajo del centímetro.

### Lo que sí depende: cuánto se apoya en la mitad pegada

La red se digitalizó solo en su mitad superior; la inferior es reflexión sobre
`y = 273,5 px` (decisión 0004, punto 2). Esa costura cae en `y = 0,0067 m`, a
0,5 mm del centro del grupo: **la costura es el eje de 0°**. De ahí que el eje
elegido cambie por completo el reparto entre lo digitalizado y lo impuesto:

| si la sección va por… | caras digitalizadas | reflejadas | sobre la costura |
|---|---:|---:|---:|
| **0°** (la costura) | 0 | 0 | **las 11** |
| **90°** (perpendicular) | 5 | 5 | 1 (el octógono) |

Por el eje de 0°, las once caras cuya cota podría leerse son exactamente las
once que cruzan la costura, es decir aquellas cuyo contorno en planta está medio
impuesto por reflexión. Por el de 90°, cinco caras —`c000`, `c009`, `c016`,
`c037` y el octógono `c042`— salen del ráster tal cual, y las otras cinco son
sus reflejos; sólo el octógono pisa la costura. La segunda situación es
claramente mejor.

### Y la cúpula no puede decir cuál es

Es una consecuencia incómoda de la propia simetría: si la bóveda es D8, **nada
de la bóveda distingue el 0° del 90°**. Sólo lo distingue algo de fuera de ella
—los vanos de la sala, las ventanas del tambor, la fachada—, y la ortoimagen de
AA-415_23 está recortada en el arranque: no llega a mostrarlos.

Por indicación del autor del repositorio, en la lámina de Almagro y en la
fotografía de `docs/` **la parte alta de la imagen corresponde a la fachada
principal**, de modo que el norte-sur del edificio es el eje **vertical** del
registro, el de 90°, y la sección **no** corre por la costura. Queda anotado
como lo que es: información aportada, no medida aquí ni citada todavía a una
fuente. Se registra porque mejora el techo de la proyección, no porque haga
falta para ella.

## La asimetría izquierda-derecha no está en el dibujo de Ferrer

Se apuntó también que el lado derecho de la cúpula es en realidad algo mayor que
el izquierdo. Es comprobable sobre la planta, y con una ventaja: el espejo
impuesto es horizontal, así que una asimetría **izquierda-derecha** no la habría
metido la construcción del dato.

A primera vista aparece: **10 de 10 órbitas** tienen radio medio mayor a la
derecha que a la izquierda, con una mediana de **+0,23 %**. Un signo consistente
diez veces parece decisivo.

No lo es, y el control lo dice: diez órbitas no son diez observaciones
independientes, porque **un centro mal puesto produce exactamente ese patrón**.
Ajustando el centro que minimiza la dispersión radial dentro de cada órbita, el
óptimo está desplazado **3,1 mm (0,22 px)** respecto del centroide del octógono,
y con él la asimetría desaparece: pasa a **4 de 10** órbitas con la derecha
mayor y mediana **−0,03 %**. El área, que es invariante por traslación y por
tanto inmune a este confundidor, ya no daba señal desde el principio: 6 de 10.

La dispersión radial que queda dentro de cada órbita es de **4,9 mm rms**, o sea
**0,35 px** — por debajo del propio suelo de la digitalización, que arrastra una
simplificación RDP de 2 px.

**Conclusión, y va en la dirección incómoda:** la figura 128 es simétrica hasta
el límite de su propia digitalización. No contiene la asimetría de la cúpula
real, así que no puede usarse para medirla — y su ausencia **refuerza** la
cautela 6 en vez de levantarla: es lo que se espera de un sector replicado en
CAD, no de un levantamiento de una bóveda deformada. La asimetría real sí está
documentada, pero en la otra fuente: `docs/policromia.md` la ve como
emborronamiento al promediar las 16 copias de la ortoimagen.

## Proyección de la sección sobre el grafo

Hasta aquí todo es planta. La pregunta siguiente es si la sección de Almagro se
puede casar con ella pieza a pieza, y la respuesta es **sí, en orden y con un
residuo de 9,5 mm**, con un control negativo que pasa.

### Por qué la pregunta está bien planteada, y solo para la clase A

Una sección dibujada como ortoimagen muestra la silueta del conjunto, no solo
lo que toca el plano de corte. Da igual: a una altura dada, el punto más lejano
del eje **en la dirección del corte** lo alcanza el propio plano de corte
cuando ese plano es el de la apotema, porque el lado del octógono es
perpendicular a él y todo el lado está a esa distancia. La clase A es la de la
apotema. La identificación es lícita **por la misma razón por la que la clase A
es la peor**: la sección que existe es la que corta por los lados.

### El perfil de la planta a lo largo del eje

Recorriendo el eje A desde el centro, las medinas lo cruzan a estos radios
(`fronteras_en_el_eje_m` en el dato), y las bandas entre ellos son las cinco
órbitas resolubles, en orden:

| banda | órbita | de (m) | a (m) |
|---|---:|---:|---:|
| 1 | 10 · octógono | 0,000 | 0,5965 |
| 2 | 9 · medio cuadrado | 0,5965 | 0,8438 |
| 3 | 6 | 0,8438 | 1,6813 |
| 4 | 4 | 1,6813 | 2,1508 |
| 5 | 0 | 2,1508 | 3,2951 |

La órbita 8 no aparece: su banda mediría 0,8 mm.

### Los escalones de la sección

Medidos sobre `docs/AA-415_23.pdf` a 150 dpi con la calibración de abajo,
tomando el píxel con tinta más externo de cada fila **en cada borde por
separado**, y agrupando en complejos los sub-escalones consecutivos:

| complejo | profundidad bajo el ápice | radio antes | radio después |
|---:|---|---:|---:|
| 1 | 0,862 m | 0,555 | 0,737 |
| 2 | 1,113 – 1,122 m | 0,876 | 0,980 |
| 3 | 2,468 – 2,506 m | 1,685 | 1,933 |
| 4 | 2,710 – 2,769 m | 2,013 | 2,269 |
| 5 | 4,445 – 4,484 m | 3,307 | 3,711 |

Cinco fronteras en planta, cinco complejos en la sección, y el orden es el
mismo. El emparejamiento no se elige: lo fuerza la monotonía del radio.

### Residuos y controles

Residuo de cada frontera al intervalo del escalón que le toca —cero si cae
dentro—: **0, 33, 4, 0, 11 mm**. Media **9,5 mm**.

Tres controles, porque un acuerdo sin control no dice nada:

| control | residuo medio | veredicto |
|---|---:|---|
| fronteras del eje **A** contra los escalones | **9,5 mm** | p = 0,014 |
| fronteras del eje **B** contra los mismos escalones | 73 mm | p = 0,23 — **no ajusta** |
| 5 radios uniformes al azar (2·10⁵ muestras) | — | la referencia de los dos p |

**El control negativo es el que da valor al positivo.** El eje B es un eje real
de la misma cúpula, con fronteras del mismo orden de magnitud, y sus radios
—0,646, 1,471, 2,348, 3,370— **no** casan con los escalones de esta sección. Si
casaran, el ajuste del eje A no significaría nada.

**Barrido de escala**, que es el sistemático que importa, porque planta y
sección se calibraron por caminos distintos:

| escala aplicada a las fronteras | ×0,96 | ×0,98 | **×1,00** | ×1,02 | ×1,04 | ×1,06 | ×1,10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| residuo medio (mm) | 56 | 33 | **9,5** | 3 | 0 | 2 | 19 |

El mínimo no está en 1,00 sino en **1,04**, y el valle es plano entre 1,00 y
1,06. Traducción honesta: las dos escalas concuerdan **al 4 %**, no mejor. Sirve
para identificar qué órbita produce cada escalón; **no** sirve para afinar el
registro de la planta, y decir «coinciden» sin este barrido sería vender
precisión que no hay.

### Lo que la proyección entrega

| órbita | banda en planta (m) | banda en la sección (m bajo el ápice) | hiladas de 20,8 cm |
|---:|---|---|---:|
| 10 · octógono | 0,000 – 0,596 | 0,000 – 0,862 | ~4,1 |
| 9 · medio cuadrado | 0,596 – 0,844 | 0,862 – 1,113 | ~1,2 |
| 6 | 0,844 – 1,681 | 1,122 – 2,468 | ~6,5 |
| 4 | 1,681 – 2,151 | 2,506 – 2,710 | ~1,0 |
| 0 | 2,151 – 3,295 | 2,769 – 4,445 | ~8,1 |

Es una cota absoluta para cada una de las cinco órbitas que la sección alcanza,
obtenida sin fotometría, sin suponer coronas y sin firmar ningún salto.

### Y lo que no entrega: una banda no es un nivel

Las órbitas 6 y 0 ocupan **6,5 y 8,1 hiladas** de la sección. No pueden ser un
nivel cada una. La razón ya estaba escrita en `docs/teselado.md`: la red de
medinas es la red principal, y **el techo real tiene subdivisiones más finas que
las que dibuja la red**. Una cara de la planta puede contener varias hiladas de
adarajas.

De modo que la proyección da la cota de la banda, no el nivel de la pieza, y
tampoco el signo de ninguna de las 211 vecindades. El bloqueo sigue donde
estaba.

## La cota de 1,082 m

Se propuso la cota **1,082 m** medida desde el ápice hacia abajo como final de
las dos primeras órbitas y como cota de control de las superiores. Se ha
comprobado sobre el propio plano. **La intención era correcta y el número no.**

### Calibración

`docs/AA-415_23.pdf`, página A0 (2384 × 3370 pt), renderizada a 150 dpi en gris
→ 4967 × 7021 px. Es el mismo render con el que se midió `estratificacion.md`.
La escala gráfica está en la banda de pie: línea horizontal en `y = 6559`, de
`x = 1075` a `x = 3437`, con once marcas de metro. Longitud **2362 px para 10 m
→ 236,2 px/m**, y el espaciado entre marcas es de 236,2 px. El valor teórico
para escala 1/25 a 150 dpi es 236,22 px/m: coinciden al 0,01 %, y coinciden con
los 2361 px ya medidos en `estratificacion.md`.

El ápice es la primera fila con tinta de la vista inferior, `y = 2539`,
invariante para umbrales de gris de 128 a 250.

### Lo que sale

El factor **233,8 px/m** no corresponde a este plano a 150 dpi: es un 1,0 %
bajo. Y un px/m no es una propiedad del plano sino del render —a 1/25, px/m =
1,5748 × dpi—, así que la cifra no significa nada sin decir a qué resolución se
midió. A 148,5 dpi sí saldrían 233,8; a 150 dpi salen 236,2. El desajuste vale
**11 mm sobre 1,082 m**. Los 253 px, leídos con la escala gráfica del propio
plano, valen **1,071 m**.

Y en metros, sin depender ya de la calibración, **el dibujo no tiene nada en
1,082 m**: esa cota cae en el tramo liso entre los complejos 1 y 2, donde el
radio crece de 0,737 a 0,876 m sin quiebro. El escalón más próximo está a
**31–44 mm** según el umbral de detección — nunca a 13 mm.

**El control que invalida el 1,2 %.** Bajando el umbral a 1 px aparecen once
«escalones» entre 0,95 y 1,25 m: uno cada 27 mm. Con esa criba, la distancia
esperada de *cualquier* cota al escalón más próximo es de unos 7 mm, y
efectivamente hay uno a 7 mm de 1,082 m. Acertar por 13 mm es lo que da el azar.
El «1,2 % de precisión» mide la resolución de la criba, no el acuerdo con el
plano.

### El número que el plano sí sostiene

La proyección identifica los dos primeros complejos:

- **0,862 m** es el final de la órbita **10**, el octógono central (frontera en
  planta a 0,596 m).
- **1,113 – 1,122 m** es el final de la órbita **9**, los medios cuadrados
  (frontera en planta a 0,844 m).

Así que «el final de las dos primeras órbitas» **existe** y es medible: está en
**1,113 – 1,122 m** bajo el ápice, no en 1,082. La cota propuesta se queda
3–4 cm corta. Lo que se acepta como cota de control es la medida, con su
intervalo y con la identificación que la sostiene.

## Lo que no se hace

- **Firmar ningún salto.** Once órbitas es una cuenta de incógnitas y cinco
  bandas son cotas absolutas; ninguna de las dos cosas es el signo de una
  medina. `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` sigue.
- **Dar la hipótesis de simetría por buena.** Que la nivelación respete D8 es
  plausible y es falsable —contra los 107 ciclos, en cuanto haya un salto
  firmado—, pero hoy no está comprobada. Si es falsa, las incógnitas vuelven a
  ser 104, no 11.
- **Convertir una banda en un nivel.** Las órbitas 6 y 0 abarcan 6,5 y 8,1
  hiladas.
- **Asignar nivel por el radio medio de la órbita.** La tabla los ordena por
  radio porque es legible, no porque el orden signifique algo. Órbitas 5 y 2
  están a 1,994 y 2,027 m: dos centésimas no deciden un nivel.
- **Usar el ajuste de la proyección para reafinar el registro de la planta.** El
  valle de escala es plano del 1,00 al 1,06.
- **Elegir la clase de eje B porque parecía resolver una órbita más.** Ni existe
  esa sección, ni resolvía más: con el filtro de resolución alcanza cuatro.
- **Usar 1,082 m como cota de control.** No la sostiene el plano.

## Techo de afirmación

El mismo de las decisiones 0004 y 0006, y ni un escalón más arriba: las 105
caras son **el dibujo de Ferrer Pérez-Blanco**, no la cúpula. Si el autor
replicó un sector en CAD, las once órbitas son la estructura de su réplica y no
un hallazgo sobre el monumento.

La proyección sí añade algo nuevo en esa dirección, y conviene medir cuánto: el
perfil de la planta de Ferrer casa, en orden y a 9,5 mm, con la silueta medida
del levantamiento de Almagro, que es **otra fuente y sí es un levantamiento**,
mientras que el eje B de la misma planta no casa. Eso es una **corroboración
cruzada entre dos documentos independientes** de que las fronteras radiales de
la propuesta están donde el monumento las tiene, al 4 % de escala. No convierte
la propuesta en reconstrucción: no dice nada de las adyacencias en planta, que
es donde vive el problema del signo, ni de las tres órbitas que ninguna sección
alcanza.

Y en el otro platillo, la medida de la asimetría lo empeora: la figura 128 es
simétrica a 0,35 px, que es lo propio de un sector replicado en CAD y no de un
levantamiento de una bóveda que los escaneos documentan deformada. La
corroboración cruzada dice que **los radios de la propuesta están donde el
monumento los tiene**; no dice que la propuesta sea un levantamiento.

Y la reducción de 104 a 11 sigue siendo condicional: **si** la nivelación
respeta la simetría medida, **entonces** hay 11 incógnitas. La implicación es lo
que se acepta aquí; el antecedente sigue sin comprobar.

## Reproducción

- `scripts/orbitas_de_caras.py` → `datos/orbitas_caras.json`, que incluye las
  órbitas, los márgenes al eje de cada corte, las fronteras radiales de cada
  clase de eje, el recuento para los cuatro ejes de cada clase y la medida de
  asimetría izquierda-derecha con su centro ajustado.
- Núcleo: `granada/caras.py`, funciones `centroide`, `margen_al_eje`,
  `corta_al_eje` y `orbitas_por_simetria`
- Pruebas: `tests/test_orbitas_caras.py` y las nuevas de `tests/test_caras.py`
- La medición de la sección se hizo sobre `docs/AA-415_23.pdf`, que **no está en
  el repositorio** por licencia (RABASF). El procedimiento —150 dpi, escala
  gráfica en `y = 6559`, ápice en `y = 2539`, umbral 200, silueta por el píxel
  con tinta más externo de cada fila, escalones desde 6 px— basta para repetirla
  con el PDF descargado del inventario AA-415_23.
