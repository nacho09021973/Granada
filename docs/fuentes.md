# Fuentes

Solo entra aquí lo que se ha consultado directamente y cuyos campos se han
comprobado uno a uno. Cada entrada indica **qué se verificó**, **qué no**, y
qué afirmación del proyecto sostiene: (A) matemática o (B) empírica, según la
distinción del README.

Verificación realizada el 2026-08-24; entrada 8 añadida el 2026-08-25. El material descartado y el informe del
que salió esta pista bibliográfica están en `investigacion-preliminar.md`,
marcado como no verificado.

---

## 1. Ferrer-Pérez-Blanco, Gámiz-Gordo y Reinoso-Gordo (2019)

**New Drawings of the Alhambra: Deformations of Muqarnas in the Pendentives of
the Sala de la Barca.** *Sustainability* 11(2), 316.
DOI [10.3390/su11020316](https://doi.org/10.3390/su11020316).

- Autores y afiliaciones: Ignacio Ferrer-Pérez-Blanco (Laboratory of Digital
  Culture for Architectural Projects, EPFL), Antonio Gámiz-Gordo (Expresión
  Gráfica Arquitectónica, Universidad de Sevilla), Juan Francisco
  Reinoso-Gordo (Expresión Gráfica Arquitectónica y en la Ingeniería,
  Universidad de Granada).
- Recibido 27-11-2018, aceptado 27-12-2018, publicado 09-01-2019.
- **Licencia CC BY 4.0** (leída en la página 15 del PDF). Reutilizable con
  atribución.
- **Verificado**: portada, abstract, afiliaciones, fechas, licencia, y el
  contenido de la página 2, leídos directamente del PDF.

### Por qué es la fuente más importante para este repositorio

La página 2 describe el sistema **occidental o andalusí** de mocárabes según
los dos manuscritos de carpintería del siglo XVII que cita — Fray Andrés de
San Miguel y Diego López de Arenas — y da los tres perfiles planos básicos:

- un rectángulo de proporción **5 a 7, «redondeada a 5·√2»**;
- un triángulo rectángulo isósceles de catetos 5 e hipotenusa 7 («también
  redondeada»);
- un triángulo isósceles con ángulo de 45° y lados mayores de 5.

Y, literalmente:

> «Theoretically, the layout of the muqarnas' inner angles are reduced to
> four: 45°, 67.5°, 90°, and 135°.»

Dos consecuencias directas, ambas de tipo (A):

1. **Los cuatro ángulos son múltiplos de 22.5° = 2π/16.** Un conjunto de
   direcciones cerrado bajo giros de 22.5° es exactamente el de las raíces
   16-ésimas de la unidad. Eso hace de **Z[ζ₁₆] el anillo natural del sistema
   andalusí**, y de la cuerda de 22.5° su longitud primitiva. El 67.5° = 3·22.5°
   es el que lo fija: sin él bastaría con orden 8.
2. **El oficio histórico usaba 7/5 = 1.4 como aproximación de √2 = 1.41421…**
   La fuente lo dice sin rodeos: «rounded to 5 root of 2». Ese redondeo es
   precisamente lo que el núcleo de Granada elimina — en Z[ζ₈] ⊂ Z[ζ₁₆], √2 no
   es un decimal sino el elemento ζ + ζ⁻¹, y su cuadrado es exactamente 2.

**Objeto de estudio**: las pechinas de la **Sala de la Barca** (Palacio de
Comares). **No** la Sala de las Dos Hermanas. Ver la nota de la sección 6.

---

## 2. Ferrer Pérez-Blanco, tesis doctoral (2023)

**Mocárabes de La Alhambra. Forma, dibujo y configuración arquitectónica.**
Universidad de Sevilla, 2023. Director: Antonio Gámiz Gordo. 491 páginas.

- **LEÍDA DIRECTAMENTE** el 2026-08-24. Descargada de idUS por su API DSpace
  (el acceso web devuelve 403 a las herramientas automáticas): item
  `e4283c2c-f94e-4f08-b551-870fa2a5091f`, bitstream de 24.4 MB, 491 páginas.
  Defendida el 31-01-2023, sobresaliente cum laude.
- Sus consecuencias para el modelo están en `docs/teselado.md`. Corrige varias
  cosas que este proyecto había dado por buenas.
- El resumen confirma la distinción entre la tradición **oriental**
  (al-Kāshī, matemático del siglo XV) y la **occidental** (López de Arenas,
  Fray Andrés de San Miguel), y documenta composiciones asimétricas.
- Handle `11441/143321` **confirmado**.
- Derechos: acceso abierto, pero las figuras son obra del autor. Se citan y se
  usan como referencia; no se redistribuye ninguna en este repositorio.

Sostiene (B), y es la referencia a leer antes de abordar los perfiles de celda.

---

## 3. Almagro Gorbea — plano AA-415_23 (RABASF)

**Casa Real de la Alhambra (Granada) — Sección y techo sala de las Dos
Hermanas.** Real Academia de Bellas Artes de San Fernando, serie *Arquitectura
de Al-Andalus*, inventario [AA-415_23](https://www.academiacolecciones.com/arquitectura/inventario.php?id=AA-415_23).

- **Verificado** campo a campo en la ficha de inventario: autor (Almagro
  Gorbea, Antonio; Barcelona, 1948), escala **1/25 (A0)**, formato
  planimetría vectorial, **PDF de 4.7 MB**, observaciones «Sección y planta
  del techo de la sala de las Dos Hermanas con ortoimagenes», procedencia
  «Fondo gráfico donado por el Académico D. Antonio Almagro Gorbea».
- **Verificado leyendo el PDF directamente** (4.7 MB, coincide con la ficha).
  Cajetín transcrito del propio plano: «ALHAMBRA. GRANADA. SALA DE LAS DOS
  HERMANAS. SECCION NORTE-SUR — A. Almagro / arq. RABASF **enero 2021**».
  Queda así confirmada la fecha, que la ficha de inventario no da.
- La lámina contiene dos vistas: la **ortoimagen cenital del techo** (4083 ×
  4054 px a 300 ppi) y la sección norte-sur, con escala gráfica de 0 a 10 m.
- La ficha **no menciona** geometría poligonal ni número de lados. El informe
  preliminar le atribuía cosas que no dice. La geometría se ha medido sobre la
  ortoimagen: ver la sección 7.

**Aviso de licencia**: es material de la RABASF. Se ha leído para verificar,
que es uso legítimo; **derivar geometría de él para un repositorio MIT es otra
cosa** y exige revisar sus condiciones de uso antes, no después.

---

## 4. APAG — plano P-000831

**Habitaciones altas de la Sala de las Dos Hermanas. Proyecto de reparación.**
Archivo del Patronato de la Alhambra y Generalife, Colección de Planos,
[handle 10514/4364](https://www.alhambra-patronato.es/ria/handle/10514/4364).

- **Verificado** campo a campo: delineante Manuel López Bueno; arquitecto
  conservador Leopoldo Torres Balbás; agosto de 1927, Granada; escala 1/50;
  papel cianotipo; 62 × 49 cm; nº de plano de archivo técnico 664; sección A-B.
- Coincide exactamente con la fila correspondiente de la tabla del informe
  preliminar. Es el único registro de esa tabla que se ha comprobado; **las
  otras nueve filas siguen sin verificar.**

---

## 5. Gámiz Gordo, Ferrer Pérez-Blanco y Reinoso Gordo (2023)

**A Deformed Muqarnas Dome at the Sala de los Reyes in the Alhambra: Graphic
Analysis of Architectural Heritage.** *Heritage* 6(12), 7400–7426.

- **Verificada la existencia** y los datos bibliográficos; depositado también
  en DigiBUG (UGR, handle 10481/91060).
- **Contenido NO leído**: MDPI devolvió HTTP 403. Según los resúmenes
  disponibles, dibuja digitalmente por primera vez cerca de dos mil piezas de
  esa cúpula y documenta deformaciones significativas mediante escáner láser 3D.
- Pendiente de lectura directa antes de usarse para nada.

---

## 6. Nota sobre las deformaciones: corrección de atribución

El informe preliminar presenta el hallazgo de deformaciones por escáner láser
dentro de su discusión sobre la Sala de las Dos Hermanas. **Eso no se
sostiene.** Los dos trabajos publicados que se han localizado son:

- las **pechinas de la Sala de la Barca**, Palacio de Comares (entrada 1);
- la **cúpula de la Sala de los Reyes**, Palacio de los Leones (entrada 5).

No se ha localizado ninguna medición publicada de deformaciones de la cúpula
de las Dos Hermanas.

Aun así, el hallazgo general sostiene la afirmación (B) del README con más
fuerza de la que se le había dado. Si en los elementos medidos los alarifes
deformaron la malla teórica y los asentamientos hicieron el resto, entonces
para cualquier cúpula histórica la afirmación (B) solo puede formularse como
*«ajusta dentro de una tolerancia medida»*, nunca como *«reproduce»*. La
geometría exacta es la del modelo, no la del monumento.

---

## 7. Orden de simetría de la cúpula, medido sobre la ortoimagen

Pregunta abierta hasta ahora: si la cúpula de las Dos Hermanas es de orden 8 o
de orden 16. Resuelta el 2026-08-24 midiendo sobre la ortoimagen cenital de
AA-415_23 (entrada 3).

**Descartado primero**: la página oficial del Patronato
([sala-de-dos-hermanas](https://www.alhambra-patronato.es/edificios-lugares/sala-de-dos-hermanas))
**no dice nada** del orden. Su única frase sobre la cúpula es que los mocárabes
«a partir de una estrella central, se desarrollan mediante el conocido teorema
de Pitágoras». El «hexadecágono» del informe preliminar no está respaldado ahí.
(De paso: esa alusión a Pitágoras encaja con el rectángulo 5 : 5√2 de la
entrada 1 — la diagonal del cuadrado es la relación que el oficio aproximaba
por 7/5.)

**Medido**, sobre la ortoimagen de 4083 × 4054 px:

- La planta es **cuadrada con las cuatro esquinas achaflanadas** por las
  trompas, lo que produce un **octógono**. Visible sin ambigüedad.
- El anillo exterior tiene **16 cupulines**, con separación angular **media de
  22.5°**, alternando ≈25° y ≈20°.
- Espectro angular de Fourier de la luminancia, por zonas radiales, con el
  centro afinado minimizando el armónico k=1:

  | zona | k=4 | k=8 | **k=16** | k=32 |
  |---|---|---|---|---|
  | estrella central | 1.6 % | 6.3 % | 6.0 % | 1.0 % |
  | cuerpo | 1.7 % | 12.1 % | 11.6 % | 3.2 % |
  | anillo exterior | 1.9 % | 4.0 % | **34.2 %** | 5.4 % |
  | toda la bóveda | 1.6 % | 7.8 % | **17.2 %** | 3.2 % |

**Conclusión, en dos partes que no deben mezclarse:**

1. **El andamiaje angular es de orden 16.** k=16 es el armónico dominante en
   el conjunto (17.2 %) y aplastante en el anillo de cupulines (34.2 %). La
   retícula de direcciones es la de múltiplos de 22.5° = 2π/16.
2. **La simetría rotacional exacta del ornamento es de orden 8.** Si fuese
   exactamente 16, los armónicos k=8 y k=24 tendrían que anularse, y no lo
   hacen (7.8 % y 5.4 %). Las 16 posiciones alternan entre dos tipos, cosa
   coherente con una base octogonal que lleva dos cupulines por lado.

Para Granada lo que importa es (1): **el anillo correcto es Z[ζ₁₆]**, porque es
la retícula angular la que fija el anillo en el que viven los vértices. Que el
grupo de simetría del ornamento sea C₈ ⊂ C₁₆ es una cuestión de qué decoración
se coloca sobre esa retícula, no de qué anillo hace falta para describirla.

Esto coincide de forma independiente con la entrada 1: el conjunto de ángulos
{45°, 67.5°, 90°, 135°} de López de Arenas genera exactamente la misma retícula
de 22.5°. Dos vías distintas — un tratado del siglo XVII y una medición
fotogramétrica del XXI — dan el mismo orden.

**Límites de esta medición, explícitos:**

- Es fotometría sobre una imagen ráster: mide luminancia, no geometría
  construida. La iluminación, los deterioros y los restos de policromía
  inyectan ruido. Los porcentajes no son precisos, solo comparables entre sí.
- Queda un k=1 residual de ~5–6 %: el centrado no es perfecto, y eso derrama
  energía hacia k=15 y k=17.
- No se ha analizado la simetría especular.
- **El PDF lleva además una capa vectorial que no se ha extraído.** Medir sobre
  ella daría geometría en vez de fotometría y sería mejor evidencia. Pendiente.
- El método es reproducible (desenrollado polar + FFT angular), pero el script
  usa Pillow y por eso **no entra en el paquete**: `granada/` mantiene cero
  dependencias.

---

## 8. Informe documental de altimetría (2026-08-25)

**Cotas Mocárabes Alhambra Dos Hermanas. Informe documental: altimetría y
restitución tridimensional de la cúpula de mocárabes de la Sala de las Dos
Hermanas.** Documento del proyecto, 12 páginas, redactado por el autor de este
repositorio. Fichero: `docs/Cotas Mocárabes Alhambra Dos Hermanas.pdf`.

Vaciado de repositorios institucionales —Dialnet, TESEO, Digibug, RiuNet,
oa.upm.es, APAG, RABASF e IAPH— en busca de cotas por pieza.

**Su conclusión principal es la que importa aquí**, y es una ausencia:

> «no existe en el dominio público ninguna tabla, despiece o listado
> topográfico que asocie de manera unívoca cada pieza o celda de la cúpula de
> las Dos Hermanas a una cota numérica, nivel, hilada o corona exacta.»

Es la primera confirmación **externa al propio trabajo** de que
`BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` no es un fallo de búsqueda nuestro.
Sostiene una afirmación de tipo (B), y por ahora la afirmación que sostiene es
la inexistencia de la fuente, no una cota.

- **Verificado directamente**: las tres remisiones a la tesis de Ferrer
  Pérez-Blanco son exactas, comprobadas contra el PDF —página impresa 185,
  «2.3.5. Altura de la pata»; 190, «2.3.6. Relación de proporciones en planta y
  alzado»; 316, «4.4. Mocárabes reglados. Arcos de mocárabes concéntricos»—.
  Leída la 190 entera: confirma la relación 7P / 7,5P / 8P ya recogida en
  `docs/teselado.md`, que es la altura de **una pieza**, no la cota de cada
  tesela.
- **Verificado sobre el propio plano**: AA-415_23 tiene capa vectorial
  (`/OCProperties`, `/OCGs`, AutoCAD 2010, A0) y dos ortoimágenes incrustadas,
  pero **no lleva cotas numéricas escritas**: 20 palabras de texto en todo el
  A0. Permite medir geometría contra la escala 1/25; no permite leer niveles.
  Y una sección es un corte: da un perfil, no puede firmar el paso de cada una
  de las 211 vecindades en planta.
- **Verificado en la web el 2026-08-25** (ver entrada 9 y el desglose de abajo):
  Saseta Velázquez (2016) existe y se ha leído entero; Roldán-Medina (2018)
  existe; Martínez Sevilla, *Revista PH* 106, existe **pero no contiene lo que
  se le atribuye**.
- **Sin verificar todavía**: APAG P-000159 y D-0353; Museo de la Alhambra,
  inventarios 006601 y 006091; MakerWorld 3150958.

### Desglose de la verificación de sus referencias

| referencia | existe | contenido atribuido |
|---|---|---|
| Ferrer, tesis, pp. 185 / 190 / 316 | **sí**, exactas | **correcto** |
| Saseta Velázquez (2016), Dialnet 6306440 | **sí**, pp. 135–144 | **correcto**, con un desliz aritmético |
| Roldán-Medina (2018), DOI 10.13140/RG.2.2.16056.80640 | **sí** | sin comprobar el interior |
| Martínez Sevilla, *Revista PH* 106, pp. 12–13 | **sí**, pp. 10–13 | **NO: el dato no está ahí** |
| AA-415_23, capa vectorial | **sí** | correcto, pero sin cotas escritas |

**El desliz aritmético**: el informe dice que «la altura mínima de una adaraja
es 7 + 1 = 8 unidades». Saseta dice literalmente que la altura mínima es
**7 + 1 + 7 = 15**, y que lo que vale **8 unidades es la pauta de elevación
entre un nivel y otro**. El 8 es el salto de nivel, no la altura de la pieza.
La conclusión que importa no cambia, pero el número decía otra cosa.

**La referencia que fallaba, y dónde estaba realmente el dato**: en el impreso
de *Revista PH* 106 (junio 2022), pp. 10–13, DOI
[10.33349/2022.106.5145](https://doi.org/10.33349/2022.106.5145), las páginas
12–13 llevan una simulación solar de la celosía del Patio del Yeso, una foto de
la exposición y la bibliografía. Ahí no está.

Está en la **versión web del mismo artículo**, publicada en el sitio del
proyecto el 28-06-2022 y firmada por Álvaro A. Martínez Sevilla (DaSCI), como
**pie de una figura**: ver la entrada 10. Mismo autor, mismo título, mismo año,
otra edición. La cita del informe estaba casi bien: fallaba el soporte, no la
atribución.

### Tensión con lo medido, que no hay que disimular

El informe recoge de Saseta que «el nivel no se mantiene, sino que asciende (o
desciende) de manera constante entre coronas». Leído como **un nivel por
medina**, eso es exactamente la clase de regla que la decisión 0006 refuta
sobre esta planta: R1 imposible por paridad, R2 con 67 de 107 ciclos rotos y
ciclo testigo. Las dos cosas solo se reconcilian si «constante» admite el salto
de **dos** niveles — que es justo lo que la tesis documenta como piezas A3 y
D3, y lo que el teorema del triángulo exige por su cuenta.

No se resuelve aquí. Se deja anotado para que quien lo lea no dé por buena la
regla simple sin pasar por 0006.

---

## 9. Saseta Velázquez (2016) — la pauta de elevación

**El juego de los mocárabes.** *Cuadernos de los Amigos de los Museos de
Osuna* 18 (2016), pp. 135–144. ISSN 1697-1019. Dialnet, artículo
[6306440](https://dialnet.unirioja.es/descarga/articulo/6306440.pdf). Acceso
abierto; leído directamente el 2026-08-25.

Localizado a partir del informe de la entrada 8, y **es la aportación más útil
de aquella lista**.

### Lo que confirma, y es una confirmación independiente

Siguiendo a Nuere, divide el lado menor de la adaraja en cinco partes y toma
siete unidades en vertical:

> «el arco mixtilíneo tiene, por tanto, siete unidades de altura y como el
> lomo, o sea, el solape vertical entre una y otra adaraja es de una unidad, la
> altura mínima que hay que darle a la adaraja será de 7 + 1 + 7 = 15, y **la
> pauta para la elevación entre un nivel y otro de adarajas es de 8 unidades**»

Ocho unidades de salto entre niveles. Es **el mismo 8P** que la tesis de Ferrer
sitúa como «nivel siguiente» en su plantilla de doble perfil (7P mayor, 7,5P
menor, 8P nivel siguiente), y que `docs/teselado.md` ya recogía. Dos autores
independientes, dos vías distintas, el mismo número. Sostiene una afirmación de
tipo (B) sobre el **tamaño** del salto.

Lo que **no** da, y hay que decirlo: el tamaño de un salto no es su signo. Sigue
sin haber nada que diga, para cada medina, si se sube, se descansa o se baja.

### Lo que corrobora de una decisión ya tomada

Saseta construyó un modelo de la cúpula de las Dos Hermanas partiendo del
dibujo de Jones y Goury, y se topó con lo mismo que nosotros:

> «lamentablemente el dibujo es esquemático, **no incluye las medinas**, con lo
> que al reproducirlo vemos que se necesitan demasiadas piezas fuera del
> sistema. Es necesario realizar una planta que incluya las medinas para que
> las adarajas no se salgan del canon»

Esto respalda por una vía independiente la decisión 0004, punto 2: usar solo la
mitad de Ferrer y **no** mezclar la mitad de Jones y Goury. No fue una
precaución nuestra; es un defecto conocido de esa lámina.

Su propio modelo tampoco resuelve las cotas: el autor dice que «el estado
actual del modelo **por ahora no es más que una aproximación**».

---

## 10. Martínez Sevilla — las 104 adarajas de estrella de Dos Hermanas

**Cuando el estudio matemático amplía la mirada interpretativa del patrimonio
cultural.** Álvaro A. Martínez Sevilla, Instituto de Investigación DaSCI.

Dos ediciones, y **solo una trae el dato**:

- **Impresa**: *Revista PH* 106, junio 2022, pp. 10–13, DOI
  [10.33349/2022.106.5145](https://doi.org/10.33349/2022.106.5145). Leída
  entera el 2026-08-25: **no menciona Dos Hermanas**.
- **Web**, [paseosmatematicos.fundaciondescubre.es](https://paseosmatematicos.fundaciondescubre.es/noticias/cuando-el-estudio-matematico-amplia-la-mirada-interpretativa-del-patrimonio-cultural/),
  28-06-2022. Contiene una figura cuyo pie dice:

> «Localización de las 104 adarajas de estrella en la cúpula de Dos Hermanas
> (Alhambra). Las estrellas son de 5 tipos distintos | fuente elaboración
> propia sobre ortofotografía en plano nadir. Proyecto PMAA»

Eso es lo que hay: **una figura con pie**, no una tabla ni un listado. Las 104
piezas están localizadas sobre ortofotografía cenital y clasificadas en 5
tipos, pero el dato está en forma de imagen y sin método publicado.

### El dato de los siete niveles, y por qué no se puede usar todavía

La cobertura de la exposición *Paseo Matemático al-Ándalus* (enero de 2022)
atribuye a Martínez un hallazgo adicional:

> «la cúpula de la sala de Dos Hermanas tiene **siete niveles** que evocan los
> siete niveles del Salón del Trono, lo que refuerza, mediante la matemática,
> la hipótesis de que Dos Hermanas iba a ser el trono de Mohammed V»

Es la primera cifra de niveles que aparece en toda la búsqueda, y por eso hay
que tratarla con cuidado:

- procede de **nota de prensa de una exposición**, no de una publicación con
  método; no se cita artículo, capítulo ni catálogo, y la búsqueda no ha
  encontrado ninguno;
- **no dice de qué cuenta se trata**: siete niveles de adarajas de estrella no
  es lo mismo que siete niveles del mocárabe completo. La sección medida en
  `docs/estratificacion.md` da **23 hiladas** con paso de ~20 cm, y las dos
  cifras solo son compatibles si cuentan cosas distintas;
- va **enlazada a una hipótesis simbólica** —los siete cielos, el trono de
  Mohammed V—. Un número que «evoca» otro número es justo el que más vigilancia
  merece antes de darlo por medido.

No entra como cota de nada. Entra como **afirmación de terceros, localizada y
fechada**, para que quien retome esto sepa que existe y de qué pie cojea.

### Licencia: leer sí, derivar no

*Revista PH* publica bajo **Creative Commons Reconocimiento-NoComercial-
SinObraDerivada 3.0**, comprobado en la ficha del artículo. La cláusula **ND**
es explícita: se puede citar y leer, **no se puede derivar geometría** de su
ortofotografía ni de la figura de las 104 adarajas para este repositorio. Es la
misma cautela que el plano AA-415_23, pero aquí la licencia lo dice con todas
las letras y no hay que ir a preguntar.

Si esa figura llegara a hacer falta como dato, el camino es pedir permiso al
autor, no recortarla.

---

## 11. Ferrer Pérez-Blanco — respuesta sobre niveles y sentido de ascenso

**Comunicación personal recibida el 2026-08-28**, en respuesta a preguntas
directas del proyecto sobre la cúpula de la Sala de las Dos Hermanas. Se
conserva el mensaje original fuera del repositorio. La captura adjunta está en
[`Foto de Ferrer.png`](Foto%20de%20Ferrer.png); se incorpora como evidencia de
la comunicación, no como material libre para reutilización.

Lo que Ferrer afirma de forma directa:

- participó hace años en un escaneado, pero ahora no tiene acceso a los
  ficheros; sabe por conocidos que se ha escaneado de nuevo en años recientes
  ante una intervención prevista en la zona Dos Hermanas-Lindaraja;
- las **ocho unidades entre niveles no están escritas en ningún manuscrito**:
  son una deducción de investigadores posteriores o de medidas empíricas;
- el sentido de ascenso de cada pieza y nivel debe ser coherente; lo más eficaz
  es deducirlo de fotografías y, en la lógica compositiva, las piezas vecinas
  tienen el mismo sentido.

Lo que ofrece expresamente **de memoria** y, por tanto, queda como pista:

- sus modelos teóricos con las proporciones de Fray Andrés de San Miguel y
  López de Arenas resultaban ambos más altos que el construido, aunque el de
  Fray Andrés se ajustaba mejor;
- un recuento rápido del alzado de Almagro le da **24 niveles**;
- Dos Hermanas tiene piezas especiales alrededor de una estrella irregular de
  cinco puntas y también, según recuerda, grupos de mocárabes de distinto
  tamaño.

La captura es un alzado rasterizado con líneas rojas cada diez niveles. No es
el DWG ni una nube de puntos y no permite identificar por sí sola el signo de
cada vecindad. El recuento rápido de 24 tampoco invalida las 23 hiladas de
`docs/estratificacion.md` ni los siete niveles citados en la entrada 10: antes
hay que establecer si los tres recuentos usan la misma definición de nivel y
los mismos límites de la cúpula.

Esta respuesta corrige una posible lectura excesiva de la entrada 9. Saseta y
la tesis de Ferrer documentan **8P como pauta usada en reconstrucciones
modernas**; el número no debe atribuirse por ello a los manuscritos de Fray
Andrés o López de Arenas. Para el software, 8P sigue siendo un parámetro de
hipótesis, no una constante histórica demostrada.

La página docente señalada por Ferrer,
[ignaciofpb.es/muqarnas](https://ignaciofpb.es/muqarnas), confirma que en el
ejercicio de 2023 se proporcionaron reglas simplificadas para componer una
planta coherente. Ferrer precisa en el correo que la cuarta imagen empleaba
piezas con flechas y líneas de nivel para comprobar esa coherencia. La página
no publica una regla pieza por pieza aplicable directamente a Dos Hermanas.

**Consecuencias operativas**:

- representar explícitamente el sentido de ascenso y comprobar la coherencia
  entre piezas vecinas;
- admitir perfiles, escalas y piezas excepcionales dentro de una composición;
- no cerrar el número de niveles hasta reproducir los criterios de conteo;
- localizar al responsable de los escaneados reciente y antiguo y solicitar
  acceso o, al menos, sus metadatos.

---

## Pendiente de verificar

- Recuento de piezas de la cúpula de las Dos Hermanas: circulan 5.416 piezas y
  «104 adarajas en forma de estrella» (IAPH / Paseos Matemáticos). Sin
  comprobar, y de tipo (B). La entrada 8 le pone localización precisa —
  Martínez Sevilla, *Revista PH* 106 (junio 2022), pp. 12–13, con las 104
  adarajas de estrella localizadas espacialmente y divididas en 5 tipos—.
  **Localizado el 2026-08-25**: no está en el impreso sino en la versión web del
  mismo artículo, como pie de figura. Ver la entrada 10, que incluye además el
  dato de los siete niveles y la restricción de licencia ND.
- La capa vectorial de AA-415_23, como comprobación de la sección 7.
- Las otras nueve filas de la tabla de planos del APAG.
- Owen Jones y Jules Goury, *Plans, Elevations, Sections and Details of the
  Alhambra* (1842–1845). Citada de segunda mano en las entradas 1 y 5, que la
  usan como referencia de contraste. Merece consulta directa.
- Enrique Nuere, análisis gráfico de las piezas componentes de los mocárabes,
  citado como precursor de los estudios CAD en la entrada 1.
- Los manuscritos del siglo XVII: Fray Andrés de San Miguel y Diego López de
  Arenas. Son la fuente primaria del sistema occidental y la raíz de la
  entrada 1.
- Autoría, fecha y condiciones de reutilización de la captura enviada por
  Ferrer; identificación y acceso a los escaneados de Dos Hermanas-Lindaraja.
