# 0008 — El alfabeto de piezas se lee de la planta, salvo un par

**Estado:** aceptada — 2026-08-26

## Contexto

`docs/teselado.md` afirmaba, y sobre ello descansaba la forma del bloqueo:

> «La **topología** de la pieza —A1, A2, A3, B4, C1, C2, D3— no se lee de la
> planta: es lo que las flechas de la planta propuesta codifican, y la figura
> 128 no las trae.»

La primera mitad es correcta. La segunda es falsa, y esta decisión la corrige
con fuente literal. El documento que la desmiente es el artículo de **Gámiz
Gordo y Ferrer Pérez-Blanco, *VLC arquitectura* 6(2), 2019, pp. 57-87**,
aportado completo al repositorio como
`docs/2019VLCGAMIZ_FERRER_MUQARNASALHAMBRA.pdf` (31 páginas, imágenes
embebidas a 300 ppi). Entrada 13 de `fuentes.md`.

## El texto original de Jones y Goury, que es la fuente de todo

El artículo transcribe (p. 69-70) el texto que Jones y Goury imprimieron **en
la propia lámina X**, junto al dibujo de una pechina de la sala de la Barca:

> «They are composed of numerous prisms of plaster, united by their contiguous
> lateral surfaces, consisting of **seven different forms**, proceeding from
> **three primary figures on plan**: they are, the **right angled triangle (A)**,
> the **rectangle (B)**, and the **isosceles triangle (C)**. […] the vertical
> angle of the isosceles triangle (C) is **45º**. The figure (B) has **one
> form** in section; the figure (A) **three**; and figure (C) **three**; the
> third (**C3**) being a **rhomboid, formed by the double isosceles triangle**.
> The curves (x x x) of the several pieces are similar, **by which it will be
> seen that a piece may be combined with any one of the others by either of its
> sides**; thus rendering them susceptible of combinations as various as the
> melodies which may be produced from the seven notes of the musical scale.»

Tres cosas se leen de ahí y ninguna es interpretación:

1. La familia es de **siete**, y sale de **tres figuras en planta**: A triángulo
   rectángulo, B rectángulo, C triángulo isósceles de **45°**. Concuerda con la
   entrada 1 de `fuentes.md` (los tres perfiles de los manuscritos de
   carpintería) y con los cuatro ángulos múltiplos de 22,5° que fundan Z[ζ₁₆].
2. **C3 es el rombo**, «formed by the double isosceles triangle». Es la frase
   que resuelve la colisión de nomenclaturas (abajo).
3. La última afirmación —cualquier pieza con cualquier otra por cualquier
   lado— es **la que hay que desconfiar**. Ver «La tensión» al final.

## Qué contiene la figura 5 (p. 71)

«Prismas elementales de mocárabes y su agrupación. Detalle lámina X y dibujos
propios», imagen embebida de **1713 × 910 px a 300 ppi**. Cinco bloques; los
tres primeros son grabado de Jones y Goury (1842-45), **dominio público**:

1. Las tres figuras base en planta A, B, C.
2. Los **siete prismas** en volumen, cada uno con su perfil y su **patilla**.
3. Un **«PLAN»** de un sector de 18 celdas **con el tipo rotulado en cada una**
   y el **alzado del mismo conjunto con los mismos rótulos**.
4. El redibujo de los autores: el sector coloreado por tipo **con flechas**, y
   una leyenda de ocho tipos.
5. Un render del conjunto.

## Resultado 1 — el mapeo de nomenclaturas, sourced por los dos lados

El artículo (p. 70):

> «Jones y Goury las nombraron considerando tres formas en planta (A, B y C),
> más un número para diferenciar sus variantes **y sus secuencias**, hasta un
> total de siete piezas: **A1, A2, A3, B, C1, C2 y C3**. Por coherencia y
> claridad aquí se ha seguido dicha nomenclatura.»

La tesis (§2.5.2, p. 197):

> «Para Jones y Goury las figuras son tres; A, B y C, si bien **la C la duplica
> por simetría por su lado menor para obtener el rombo completo, que se designa
> aquí con la letra D**.»

Es decir: **A1…C3 es la nomenclatura original de Jones y Goury; la D es
renombre de Ferrer**. El mapeo:

| Jones y Goury / artículo | tesis | nombre de oficio |
|---|---|---|
| A1 | A1 | medios cuadrados |
| A2 | A2 | atacías |
| A3 | A3 | medios cuadrados de dos niveles |
| B | B4 | conzas |
| C1 | C1 | medias jairas |
| C2 | C2 | dumbaques |
| **C3** | **D3** | **jairas de dos niveles** |
| C4 | — | añadido de los autores; ver abajo |

**Se confirma solo, por un camino independiente de los nombres.** En la leyenda,
exactamente **dos** tipos llevan **dos flechas apiladas en línea**: A3 y C3. En
la tesis, exactamente **dos** piezas «salvan dos niveles»: A3 y D3. Y el
artículo lo dice en palabras (p. 70): «las piezas **A3 y C3, que ascienden dos
niveles**». Tres fuentes, las dos mismas piezas.

**C4 queda fuera, y con motivo declarado** (p. 70): «se han redibujado las
piezas A3 y C3, así como **la C4, que Jones y Goury no dibujaron,
asimilándola con la C1**». Es aportación de los autores y se comporta como C1
—un nivel—. No entra en el alfabeto hasta contrastarlo contra §2.5.4 de la
tesis («Piezas particulares, más allá del ABCD»).

## Resultado 2 — qué codifican las flechas, dicho por los autores

No hay que deducirlo (p. 70):

> «El nuevo dibujo aquí aportado de cada pieza incorpora un color distinto y
> **flechas indicando el sentido de ascenso del mocárabe**.»

Leyenda, leída a 5×:

| tipo | figura en planta | orientación | flechas |
|---|---|---|---|
| A1 | triángulo rectángulo | vértice arriba | 1, larga |
| A2 | triángulo rectángulo | **vértice abajo** | 2 **divergentes** |
| A3 | triángulo rectángulo | vértice arriba | **2 apiladas en vertical** |
| B | rectángulo | — | 1, larga |
| C1 | triángulo isósceles 45° | vértice arriba | 1, larga |
| C2 | triángulo isósceles 45° | **vértice abajo** | 1, larga |
| C3 | **rombo** | — | **2 apiladas en vertical** |
| C4 | cometa | vértice arriba | 2 divergentes |

Las dos formas de «dos flechas» **no significan lo mismo**, y confundirlas es
el error de lectura obvio:

- **apiladas en línea** (A3, C3) = la pieza **asciende dos niveles**;
- **divergentes** (A2, C4) = **un nivel**, con dos sentidos, uno por lado. Es
  la advertencia de §3.3.2 que ya estaba en `teselado.md`: «una arista
  compartida no debe recibir necesariamente un único sentido global».

## Resultado 3 — el par ambiguo es uno solo, y es el que importa

Cruzando la estructura (figuras A, B, C/D × topologías) con la orientación:

| figura | candidatos | ¿separa la orientación? |
|---|---|---|
| A | A1, A2, A3 | separa A2 (vértice abajo); **A1 y A3 quedan juntos** |
| B | B4 | único |
| C | C1, C2 | sí (arriba / abajo) |
| D — rombo | D3 | único |

> **De una planta que resuelva pieza a pieza, figura + orientación identifican
> el tipo de forma única salvo un par: A1 frente a A3.**

Y ese par es exactamente **un nivel frente a dos** dentro de la figura A. Todo
el problema de nivel, en lo que a legibilidad en planta se refiere, se reduce a
**un binario por celda de figura A**.

El artículo afirma además que ese binario **está dibujado** (p. 70):

> «**Jones y Goury detallaron con precisión las "patillas" de estos mocárabes,
> lo que permite identificar su tipo con exactitud.**»

### El grabado lo marca, y el control sale negativo

En el «PLAN», las **cinco** celdas rotuladas A3 llevan **un arco semicircular
dentro**, apoyado en su lado exterior. Ninguna de las **trece** restantes
(A1, B, A2 × 4, C1 × 2, C2 × 2, C3 × 2) lo lleva. Cinco de cinco, cero falsos
positivos. Dos cautelas, y la segunda es un resultado negativo real:

1. **Confusión con el borde.** En este sector las cinco A3 son además las únicas
   celdas que apoyan su base en el contorno exterior. La figura sola **no puede
   decidir** si el arco marca «A3» o «pieza de borde». Hace falta un sector con
   A3 en el interior.
2. **El arco no marca «dos niveles».** C3 asciende dos niveles y **no** lleva
   arco. La lectura genérica queda refutada dentro de la propia figura. Lo que
   el arco separa es A3 de A1 dentro de la figura A — que es justo lo que hace
   falta, pero es una afirmación más estrecha.

## Resultado 4 — una restricción de vecindad, de la tesis

§2.5.2, pieza A3 (p. 202), literal:

> «Esta tipología de mocárabe de dos niveles, tiene su pata del primer nivel
> con el grosor más pequeño… En su segundo nivel, entra en juego la
> correspondencia con su mocárabe vecino, que por tener el perfil menor en la
> pata, **ha de ser una pieza A2 o B**, siendo la primera la opción más común.»

Es una **restricción de compatibilidad entre vecinas**, no una cota. Convierte
parte del problema en satisfacción de restricciones sobre el teselado en vez de
firma de saltos uno a uno.

Y cierra otra vez con el paso de nivel, ahora cuantitativo:

> «…el perfil inferior, que en el caso de llegar a **7,5P** y teniendo niveles
> de **8P**, corresponde pues a **0,5P**.»

Cuarta aparición independiente del paso de 8 unidades. Y §2.5.2, D3: «se usan
los dos perfiles, el de menor grosor para el **primer nivel**, con topología
**divergente**, siendo el de mayor grosor empleado en el **segundo nivel**,
donde la topología **converge** de nuevo al punto más alto». Es el mecanismo
detrás de la doble flecha apilada.

## La tensión, y hay que dejarla escrita

Jones y Goury afirman en la lámina X que **«a piece may be combined with any
one of the others by either of its sides»**, porque «the curves of the several
pieces are similar». Si eso fuera cierto, la gramática **no restringiría nada**
y no habría nada que leer.

La tesis lo contradice, y explica por qué (§2.5.2, p. 197):

> «Con respecto al perfil, para Jones y Goury **carece de definición
> geométrica** y no tiene para ellos el doble perfil de la plantilla de los
> manuscritos de carpintería. […] se puede deducir, que **los simplificaron en
> el término curva, por motivos didácticos**.»

Y el propio artículo, sobre los mocárabes que Jones y Goury dibujaron
(p. 79): «muchos de sus mocárabes deformados **no obedecían al proceso de
agrupación formulado por ellos mismos**».

**Conclusión operativa: la libertad combinatoria de Jones y Goury es una
simplificación didáctica y no se usa como regla.** Lo que sí se usa es el
doble perfil con paralelismo entre vecinas, que sí restringe — y del que la
restricción A3 → vecino A2 o B es un caso documentado.

## Añadido el 2026-08-26 — §3.2.3 y §3.2.4 de la tesis

Al comprobar el fichero `docs/Lamina X.pdf` —que **no es la lámina**, sino un
extracto de la **página 250 de la tesis** hecho con PDF24; sus metadatos dan
`Title: (Ferrer Pérez-Blanco, Ignacio Tesis.pdf)` y sus imágenes están a 150 y
106 ppi— aparecieron dos secciones del capítulo 3 que no se habían leído. Las
dos son directamente del problema.

### La rotulación existe en un solo dibujo, y no es el de la cúpula

§3.2.3, p. 250, literal:

> «El carácter didáctico de este dibujo de Jones y Goury, lo demuestra el hecho
> de que **la pequeña pechina de ejemplo es el único plano en el que nombraron
> los mocárabes**.»

De modo que **el dibujo de la cúpula de Dos Hermanas no lleva rótulos de tipo**.
Los tiene el sector de 18 celdas y nada más. Esta decisión nunca supuso lo
contrario —el resultado 3 se apoya en figura, orientación y patilla, no en
rótulos—, pero cierra por escrito la salida más cómoda y hay que no volver a
proponerla.

### Por qué el tipo no puede dar el nivel: los ángulos son fijos

§3.2.3, p. 249, y es un enunciado de sistema, no una observación:

> «Mientras que en el sistema oriental el mismo tipo de figura puede tener
> ángulos distintos según esté en un nivel u en otro, en el sistema occidental
> **los ángulos son fijos en la familia de figuras planas, por lo que la pieza
> del mismo tipo del nivel más alto y el más bajo son exactamente la misma**.»

Dos consecuencias, y tiran en direcciones opuestas:

1. **A favor del modelo.** El alfabeto es independiente del nivel: un juego
   finito de prototipos basta, y la separación que hace `granada/niveles.py`
   entre tipo/topología y nivel absoluto no es una comodidad de programación
   sino una propiedad del sistema occidental.
2. **En contra de cualquier atajo.** Como la pieza del nivel más alto y la del
   más bajo **son exactamente la misma**, ninguna medida de su forma en planta
   puede dar su cota. Lo intrínseco al tipo es cuántos niveles **asciende**
   (uno, o dos en A3 y C3), nunca en cuál está. Es el enunciado limpio de por
   qué `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` es lo que es.

### El mecanismo detrás de las patillas: la pata marca el sentido

§3.2.4 «Plantas con puntos», pp. 251-252, describe la notación de los artesanos
magrebíes que recoge Paccard:

- pieza de **una sola pata**: un **círculo negro en la esquina donde está la
  pata**;
- pieza de **varias patas**: **puntos rojos** en cada esquina con pata, dos o
  tres;
- la pieza rectangular **no lleva puntos si su perfil es continuo**, y dos si
  tiene patas;
- el color es inconsistente entre plantas y **no** codifica el tipo.

Y la frase que importa:

> «gracias al punteado de las vecinas **se puede extraer el sentido de los
> mocárabes**»

Es el mismo dato que Jones y Goury dibujan: **dónde está la pata**. Una notación
lo marca con un punto en la esquina, la otra lo dibuja como patilla. Por eso
«detallaron con precisión las patillas […] lo que permite identificar su tipo
con exactitud» — la posición de la pata es a la vez tipo y sentido. Los dos
sistemas de notación codifican la misma magnitud por caminos distintos, lo cual
es la mejor corroboración disponible de que esa magnitud es la que gobierna.

Corolario que cierra una tentación: **el color no sirve**. §3.2.3 dice que las
piezas coloreadas «pueden ascender o descender» y que lo que marcan es su
vecindad con los **sinos**; §3.2.4 añade que algunas piezas del mismo color
«tienen sentido contrario, lo que demuestra que no son la misma pieza». Vale
para `docs/policromia.md`: la policromía **no** es una vía al nivel.

De paso, un dato geométrico que corrobora el análisis de sombra: los sinos
«representan **concavidades** en la composición». Es la razón documental de que
15 de 16 cupulines salieran más oscuros.

### Tercera nomenclatura, la marroquí

§3.2.4 da los nombres de Paccard y amplían la tabla del resultado 1:

| Jones y Goury | tesis | marroquí (Paccard) |
|---|---|---|
| A3 | A3 | **Chiira** |
| C3 | D3 | **Charbiyia Chiira** |

Con una advertencia del propio texto: en los dibujos de artesanos que Paccard
reproduce **no hay correspondencia con la A3**, y los triángulos de tres puntos
que podrían serlo «corresponden con errores de dibujo». Concuerda con que la
tesis llame a la A3 «curiosamente uno de las menos empleadas». **A3 es rara**, y
eso es relevante para el binario A1/A3: la prior no es 50-50.

## Lo que esto NO hace

- **No firma ningún salto de la cúpula.**
  `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` sigue vigente. Lo que cae es la
  *razón* por la que se creía irresoluble desde una planta.
- **No se aplica a las 105 caras.** El alfabeto es de **piezas**, y la lámina X
  tiene **5416**. La red de medinas es más gruesa que el despiece real —decisión
  0007: «una cara de la planta puede contener varias hiladas de adarajas»—. Una
  cara de `caras_red.json` **no es** un mocárabe, y asignarle un tipo del
  alfabeto sería un error de escala.
- **No dice que el dibujo de la cúpula traiga estas marcas.** El sector de la
  fig. 5 es la muestra de gramática, de 18 celdas. Que el dibujo de Dos
  Hermanas, con 5416 piezas en una lámina, resuelva figura, orientación y arco
  es una **pregunta empírica abierta**.
- **No fija el signo del sentido de ascenso.** «Sentido de ascenso» está dicho;
  qué lado de la arista sube en cada caso hay que leerlo pieza a pieza.

## Consecuencia para la redigitalización

Cambia el criterio con el que se juzga un escaneo de la lámina X. La pregunta
ya no es «¿trae sección corregistrada?» sino:

> **¿resuelve pieza a pieza, con orientación legible, y separa A1 de A3?**

Y hay una medida de partida. La **figura 10** del artículo es lámina X **pura**
—la sección IMAGE SOURCES la da como «Jones and Goury […] Plate X», sin dibujos
de los autores—, embebida a **827 × 1566 px**: el octógono ocupa ~790 px, o sea
**~110 px/m** frente a los **72,5 px/m** de los que salió `red_medinas.json`.
Ya es **1,5×** sin salir del repositorio, y el doble de la reproducción de la
tesis. Sigue lejos de 5416 piezas —a esa escala una pieza son ~10 px—, pero
basta para dos comprobaciones que hoy no se pueden hacer con nada más:

1. **Comparar redes de medinas cara a cara.** En la fig. 10 la mitad inferior
   del octógono muestra la retícula principal en polígonos grandes y la
   superior el despiece fino. Si eso es convención del dibujo y no defecto de
   impresión, la mitad inferior es directamente comparable con
   `red_medinas.json` — y esa comparación es el arbitraje entre las dos plantas
   que la decisión anterior dejó planteado.
2. **Contar hiladas contra Almagro.** La sección de la fig. 10 es una
   sección-alzado con las hiladas separadas. Contarlas y contrastarlas con las
   **24 ± 1** de `estratificacion.md`, medidas sobre AA-415_23, es un control
   cruzado entre dos documentos independientes.

## Reproducción

- Fuente: `docs/2019VLCGAMIZ_FERRER_MUQARNASALHAMBRA.pdf`, 31 pp.
  Fig. 5 en la página 15 del PDF (p. 71 del artículo), imagen de 1713 × 910 a
  300 ppi. Fig. 10 en la página 24 (p. 80), imagen de 827 × 1566 a 300 ppi.
  Fig. 9 en la página 21 (pechina de la Barca, lámina X). `pdfimages -list`.
- Recortes de la fig. 5, en coordenadas de esa imagen: «PLAN»
  `(880,30)-(1370,330)`; alzado `(1350,20)-(1713,410)`; prismas grabados
  `(20,230)-(850,470)`; leyenda `(30,735)-(860,900)`.
- Contrastes en la tesis: §2.5.2 p. 197 (figuras y perfiles), p. 202 (A3),
  p. 211 (D3), índice pp. 198-211 para la lista de siete.
- **Derechos.** La sección IMAGE SOURCES del artículo atribuye cada figura. La
  **10 y la 11 son Jones y Goury sin añadido**: grabado de 1842-45, **dominio
  público**. La 5 y la 9 son «Detail of plate X **and authors' own drawings**»:
  mixtas. La licencia de *VLC arquitectura* **no consta en el PDF** y sigue sin
  comprobar; mientras tanto aquí se cita y se describe, no se reproduce.
