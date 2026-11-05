# Fuentes

Solo entra aquí lo que se ha consultado directamente y cuyos campos se han
comprobado uno a uno. Cada entrada indica **qué se verificó**, **qué no**, y
qué afirmación del proyecto sostiene: (A) matemática o (B) empírica, según la
distinción del README.

Verificación realizada el 2026-08-24; entrada 8 añadida el 2026-08-25;
entradas 9 a 12 añadidas el 2026-08-25 y el 2026-08-26, y la entrada 3
ampliada el 2026-08-26 al leer el PDF entero. El material descartado y el informe del
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

### Qué hay dentro del PDF, leído entero el 2026-08-26

La ficha de inventario dice «planimetría vectorial» y este repositorio lo
arrastró como si hubiera un dibujo de líneas que extraer. **No lo hay.** El
flujo de contenido de la página entera son **1823 bytes**, y sus dos capas
opcionales (los `/OCG` que la entrada 8 detectó) se llaman:

- **`Orto`** — dos imágenes JPEG incrustadas, y nada más;
- **`Rotulo`** — la escala gráfica y los textos.

Todo el trazado vectorial de la lámina son los dos rectángulos que enmarcan
las imágenes y los once ticks de la escala. **Ni un trazo del despiece de
mocárabes.** La lámina es fotogrametría texturizada colocada en un A0, no
delineación: la silueta de 23 hiladas de `docs/estratificacion.md` es el perfil
de una ortofoto, no una línea dibujada por el autor.

Es un dato de método, no una pega al plano. Y tiene una consecuencia: **no
existe la «capa vectorial de AA-415_23» que figuraba como pendiente**. Queda
cerrada en negativo.

### La escala, fijada por el autor y no medida

Los once ticks de la capa `Rotulo` son vectores con coordenadas exactas: diez
intervalos de 945 unidades —uno de 944, redondeo del PDF—, **9449 unidades para
10 m**, o sea 944,9 u/m. Con la matriz global del flujo (`0.12 0 0 0.12 16 50
cm`):

> **113,388 pt/m = 40,0008 mm por metro real → escala 1/24,9995, desviación
> +0,0019 % del 1/25 nominal.**

La sección 7 tenía 0,01 % **midiendo** sobre el ráster a 150 ppi. Esto no es
una medición mejor: es el número que puso Almagro. Sostiene una afirmación de
tipo (B) sobre la escala, y es la más firme del repositorio.

### Las dos ortoimágenes, extraídas a resolución nativa

Extraídas del flujo sin recomprimir (`/DCTDecode` directo a fichero) el
2026-08-26:

| imagen | píxeles | en la lámina | ppi nativos | fichero local |
|---|---|---|---|---|
| orto cenital del techo | 4083 × 4054 | 345,7 × 343,2 mm | **300,00** | `docs/AA-415_23_orto_techo.jpg` |
| sección norte-sur | 6219 × 7809 | 526,5 × 661,1 mm | **300,02** | `docs/AA-415_23_seccion.jpg` |

Cruzadas con la escala anterior: **472,5 px por metro real**, es decir
**exactamente el doble** de los 236,2 px/m con los que se hicieron las
mediciones de la sección 7 y de `estratificacion.md`. **1 px = 2,12 mm
reales.** Cualquier medida que dependa de la resolución se puede rehacer al
doble de finura sobre estos ficheros, sin volver a rasterizar nada.

Los dos JPEG están **en `.gitignore`**, por lo mismo que el PDF: son el
contenido íntegro de la lámina, no una cita.

### Lo que sigue sin haber

Cota Z. Una ortofoto no la lleva, igual que no la lleva una sección. Extraer
mejor las imágenes no toca `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS`; solo
mejora la regla con la que se mide.

### Condiciones de uso: leídas, y dicen que sí

El campo **Derechos** de la ficha de inventario, literal:

> «La reproducción de esta imagen en alguna publicación deberá hacer constar
> con claridad su autoría, así como la referencia de la publicación en que
> hubiera sido previamente difundida por sus autores. Su uso comercial queda
> supeditado a la expresa autorización del autor. **Se autoriza su uso con
> fines de docencia e investigación.**»

**Dónde consta, que importa**: en la ficha de academiacolecciones.com, **no en
el PDF**. Comprobado el 2026-08-26 — la cadena «Derechos», «docencia» y
«comercial» no aparece ni en los bytes crudos del fichero, ni en ninguno de sus
flujos descomprimidos, ni en metadatos (`Custom Metadata: no`, `Metadata
Stream: no`). La condición es igual de válida; lo que no vale es citarla como
si viniera del fichero.

Consecuencias, una por cláusula:

1. **«Se autoriza su uso con fines de docencia e investigación.»** Este trabajo
   es investigación. **Derivar geometría de la lámina está autorizado**, no
   solo leerla para verificar. Esto levanta la parte principal de la cautela 4,
   que llevaba desde el principio pidiendo revisar las condiciones «antes, no
   después». Revisadas: dicen que sí.
2. **«Su uso comercial queda supeditado a la expresa autorización del autor.»**
   Aquí está el único choque real, y no es con la derivación sino **con la
   licencia de salida**. Este repositorio es **MIT**, y MIT concede a cualquier
   tercero, de forma expresa, el derecho a usar, sublicenciar y vender. Publicar
   geometría derivada bajo MIT sería conceder en nombre de Almagro un permiso
   que él se reserva. Dos vías limpias:
   - **separar licencias** — el código sigue MIT, y los datos derivados de la
     lámina salen bajo una licencia sin uso comercial (CC BY-NC 4.0), con su
     aviso; es lo habitual en proyectos con datos de patrimonio;
   - **pedir la autorización expresa**, que es literalmente la pregunta 4 de la
     consulta enviada el 2026-08-26. Si contesta que sí, MIT deja de chocar.
3. **Atribución, y es doble**: «su autoría» **y** «la referencia de la
   publicación en que hubiera sido previamente difundida por sus autores». No
   basta con poner el nombre: hay que citar dónde se publicó antes. Para esta
   lámina, la ficha AA-415_23 de la RABASF, A. Almagro, enero de 2021.

**Lo que sigue sin cambiar**: los dos JPEG extraídos siguen en `.gitignore`. La
autorización cubre *usarlos* para investigar, que es lo que hacemos; *publicar*
la imagen en un repositorio de licencia comercial es el mismo punto 2 de arriba,
y no hace ninguna falta — lo que este proyecto necesita publicar es geometría
propia, no la ortofoto de Almagro. Mantenerlos fuera cuesta cero.

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
- ~~**El PDF lleva además una capa vectorial que no se ha extraído.** Medir
  sobre ella daría geometría en vez de fotometría y sería mejor evidencia.~~
  **Cerrado en negativo el 2026-08-26**: esa capa no existe. Las del PDF son la
  ortoimagen y el rótulo (entrada 3). No hay forma de cambiar fotometría por
  geometría en esta lámina: **es una ortofoto, y no hay más**.
- **Esta medición ya estaba a resolución nativa.** Los 4083 × 4054 px son los de
  la imagen incrustada, así que la extracción del 2026-08-26 no le añade nada.
  La que sí estaba a la mitad era la estratificación, rehecha ese día.
- **Reproducida de forma independiente el 2026-08-26, en lo cualitativo.** Una
  reimplementación desde cero sobre la ortoimagen extraída confirma las dos
  conclusiones: k=16 domina con claridad en la zona de los cupulines —hasta el
  31 % de la potencia— y **k=8 no se anula** (3,8 %), que es lo que impide leer
  la simetría del ornamento como orden 16.
- **Pero los porcentajes de la tabla no son reproducibles**, y es un defecto de
  esta sección, no de la medida. Faltan dos parámetros por documentar: la
  **normalización** —los valores solo salen del orden publicado si se normaliza
  la **potencia** `|F|²`, no el módulo— y los **radios exactos** de las cuatro
  zonas. Con zonas elegidas a ojo el 34,2 % del anillo exterior aparece en la
  banda que la reimplementación llama «cuerpo». Quien vuelva aquí debe fijar
  ambos antes de comparar cifra con cifra.
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
  A0. **Corregido el 2026-08-26**: hay capas `/OCG`, pero ninguna contiene
  dibujo vectorial. Son `Orto` (las dos imágenes) y `Rotulo` (escala y textos);
  el flujo entero son 1823 bytes. Y las 20 palabras están ahora transcritas una
  a una en la entrada 3. Lo que esta línea concluye no cambia; lo que hay
  detrás, sí. Permite medir geometría contra la escala 1/25; no permite leer niveles.
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

## 11. Informe de respuestas a la consulta de Almagro (2026-08-26)

**Resolución Analítica a las Cuestiones Estructurales, Geométricas y
Documentales sobre la Cúpula de Mocárabes de la Sala de las Dos Hermanas.**
Fichero: `docs/Respuestas a Preguntas de Almagro.md`, 141 líneas, 42
referencias. Redacción automática por herramienta de investigación asistida,
tomando como entrada el borrador `docs/consulta-almagro.md`.

**Lo primero, porque el nombre del fichero engaña**: esto **no** es una
respuesta de Antonio Almagro. Es un informe de terceros que contesta *a* las
cuatro preguntas que el borrador le dirige. La consulta real se envió el
**2026-08-26** —a Almagro y a Ignacio Ferrer— y sigue sin respuesta; cuando
llegue, entra como fuente aparte y con su fecha. Este informe no la anticipa ni
la sustituye.

### La circularidad, que es el defecto que lo define

Su **referencia 7 es `Borrador_Consulta_Antonio_Almagro.pdf`**: el documento de
este mismo repositorio. Es la fuente más citada del informe con diferencia —
**51 llamadas** de las que aparecen en el texto—, y sostiene precisamente las
afirmaciones que se le pedía verificar: las 105 teselas, las 211 vecindades, el
salto de 8 unidades, las 23 hiladas, el paso de 20 cm, la escala 1/25 y las
«veinte palabras de texto» del A0.

El informe cita la pregunta como si fuera la respuesta. **No aporta ninguna
corroboración externa de esos números**, y ninguna de sus frases marcadas con
un 7 puede contarse como confirmación independiente de nada de lo que ya
sostiene este repositorio. Anotado aquí explícitamente para que quien lo
retome no lo lea como aval.

### Verificación de sus referencias

| referencia | veredicto |
|---|---|
| 7, `Borrador_Consulta_Antonio_Almagro.pdf` | **es este repositorio**: circular, 51 llamadas |
| 5, `legadonazari.blogspot.com` | blog; sostiene el recuento de 5.416 piezas y la atribución a Jones |
| 9, «A Grammar of Muqarnas… by Jones and Goury 1834-1845» | **existe**, pero es un estudio moderno *sobre* esos dibujos, no obra de Jones |
| 9, reutilizada para Saseta (2016) | **numeración rota**: la misma llamada sirve a dos obras distintas |
| 19, 23, deformaciones (canal.ugr.es, Diario de Sevilla) | notas de prensa; correctas como tales, ver la sección 6 |
| 29, 30, Martínez Sevilla | coinciden con la entrada 10; nada nuevo |
| 37, 40, aviso legal y solicitud de imágenes RABASF | correctos, genéricos del sitio |
| 25, 26, 42 | **ruido**: *Machines of Loving Grace*, una guía docente de la URJC 2026-27 y un buscador de ayudas de la AEI |

**El error de atribución que hay que dejar fijado**: el informe abre diciendo
que Owen Jones y Jules Goury «publicaron en su *Grammar of Muqarnas* (1842) el
recuento de las piezas… cifrándolas en aproximadamente 5.416 unidades». Lo que
Jones y Goury publicaron en 1842–1845 es *Plans, Elevations, Sections and
Details of the Alhambra*. «A Grammar of Muqarnas» es el título de su propia
referencia 9, que por su subtítulo —*Drawings of the Alhambra by Jones and
Goury, 1834-1845*— es un estudio posterior **sobre** aquellos dibujos. El
informe ha convertido un análisis moderno en un libro decimonónico, y le ha
colgado una cifra que en realidad toma de un blog.

Eso deja el recuento de 5.416 piezas donde ya estaba: sin verificar, y ahora
además con una atribución falsa circulando. Ver la lista de pendientes.

### Lo aprovechable

**Orientación de la sala** — es lo único con contenido nuevo, y responde a la
mitad de la pregunta 3 del borrador. La Sala de las Dos Hermanas se abre en el
lado **septentrional** del Patio de los Leones; por tanto su portada, la
**fachada principal, es el paramento Sur**, y la progresión interior va hacia
el Norte: Sala de los Ajimeces y, al fondo, Mirador de Lindaraja. Es
topografía palatina bien establecida, pero el informe la apoya en un blog, una
web de turismo y una página de fotografía (referencias 1, 2, 4). **Correcta de
fondo, mal citada**: si va a sostener la orientación de la decisión 0007, hay
que recitarla contra fuente seria antes de usarla.

**Una pista concreta y buena**: su referencia 3 es la lámina **AA-415_20**,
*Sección Palacio de los Leones*, del propio Almagro y en el mismo fondo de la
RABASF que AA-415_23. Una sección del palacio entero sí puede fijar la
orientación de la sala sin depender de la consulta. Añadida a los pendientes.

**Encuadre legal** — distingue con claridad el uso de la lámina como testigo de
comprobación métrica (cita científica, legítimo) de su vectorización como
matriz generadora del modelo, que sería transformación y obra derivada y exige
licencia escrita. Coincide con la cautela 4 y con la entrada 10. No cambia
nada; lo confirma.

### Lo que presenta como hallazgo y es inferencia

Sostiene que Ferrer omite las flechas de nivel en Dos Hermanas **porque** las
deformaciones documentadas por UGR/US quiebran el salto ideal. La afirmación se
apoya en la referencia 7 —este repositorio— más una nota de prensa. Es una
hipótesis razonable y no hay nada que la respalde como causa: Ferrer no dice
por qué no la aplica. No entra como motivo; entra como conjetura de terceros.

Lo mismo con la ortogonalidad de la sección: el argumento es que la convención
de rotulación del CSIC y la RABASF «presupone sistemáticamente» un corte
perpendicular, citando la propia lámina. Es plausible y no es una fuente. La
pregunta 3 del borrador sigue mereciendo respuesta del autor.

### Qué sostiene, al final

Una sola cosa, y por vía negativa: coincide con la entrada 8 en que **no existe
tabla pública de cotas por pieza**. Como esa coincidencia se apoya en buena
parte en el propio borrador, vale menos que la de la entrada 8, que sí era
externa. `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` sigue en pie, y este
informe no lo mueve.

---

## 12. AA-415_23.dxf — vectorización automática, descartada (2026-08-26)

Fichero recibido el 2026-08-26, 13,5 MB, DXF R14. **Procedencia sin anotar**:
quien lo envió no consta en este repositorio, y no se inventa. Si vino de
Almagro o de Ferrer sería además la primera respuesta a la consulta del
2026-08-26 y tendría entrada propia; queda pendiente de aclarar.

**No es el fichero de origen del levantamiento.** Su propia cabecera lo dice:

> `SCAN2CAD Date : 08/26/26` · `SCAN2CAD DotsPerInch : 300`

Es una vectorización automática de un ráster, generada el mismo día en que
llegó. Lo comprobado sobre sus 1.048.533 pares código/valor:

- **141.492 coordenadas Z, todas 0.** Sin una sola excepción. No es que falten
  en algunas entidades: el dibujo es plano entero.
- **Una sola capa de dibujo**, `S2C_1` (Scan2CAD Layer 1), con 72.860
  entidades. Un levantamiento llevaría capas con nombre.
- **67.976 `LINE`, 2.281 `ARC`, 313 `CIRCLE`**: polilíneas rotas en segmentos
  sueltos, mediana de 10 px, el 3,3 % por debajo de 2 px. Firma de trazado
  automático.
- **`$INSUNITS = 0`**, sin unidades: las coordenadas son píxeles (5305 × 7499),
  no metros.
- **Un solo `MTEXT` en todo el fichero, y es `\U+002A`: un asterisco.** No
  sobrevivió una palabra del plano, ni la escala gráfica, que es justamente lo
  que permitiría calibrarlo.

**Resolución**: 5305 × 7499 px sobre un A0 son **160,2 ppi efectivos**, no los
300 que anuncia su cabecera —esa cifra es una etiqueta interna de la
herramienta—. En las unidades de este repositorio, 252,3 px/m frente a los
236,2 px/m ya medidos: **un 7 % más**, a cambio del error del trazado
automático.

### Por qué queda descartado del todo

No por la resolución, sino por lo que la entrada 3 estableció ese mismo día:
**la lámina no tiene dibujo de líneas**. Es fotogrametría texturizada. Un
vectorizador aplicado a una ortofoto no traza el despiece de mocárabes —no hay
tal trazo que seguir—, traza **contornos de mancha de la piedra y el yeso**.
Esos son los 68.000 segmentos cortos y los 313 círculos de 6 a 20 px: ruido de
textura con forma de geometría, que es la clase de dato más peligrosa que
puede entrar en este repositorio.

Lo correcto para cualquier medida es la vía de la entrada 3: las dos
ortoimágenes a 300 ppi nativos (472,5 px/m) con la escala exacta del autor.
Estrictamente mejor y sin intermediario algorítmico.

**Licencia**: un calco vectorial íntegro del plano es el ejemplo de manual de
«transformación» y obra derivada. Más expuesto que medir sobre el PDF, no
menos. Está en `.gitignore` por el mismo motivo que el PDF.

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
  **Aviso de la entrada 11**: circula además una atribución falsa de esa cifra,
  que se la cuelga a un supuesto *Grammar of Muqarnas* de Jones y Goury (1842).
  Ese libro no existe con ese título; ver la entrada 11. Quien verifique el
  recuento no debe partir de ahí.
- ~~La capa vectorial de AA-415_23, como comprobación de la sección 7.~~
  **Cerrado en negativo el 2026-08-26**: no existe. Las capas del PDF son la
  ortoimagen y el rótulo; no hay dibujo vectorial que comprobar. En su lugar
  salieron la escala exacta del autor y las dos imágenes a 300 ppi. Entrada 3.
- **AA-415_20, *Sección Palacio de los Leones*** (Almagro, RABASF, mismo fondo
  que AA-415_23). Puede fijar la orientación de la sala respecto al patio sin
  depender de la respuesta a la pregunta 3 del borrador. Pista de la entrada 11.
- La orientación Sur = fachada principal de Dos Hermanas, contra fuente
  académica. La entrada 11 la da por buena apoyándose en blogs y en una web de
  turismo; el dato parece correcto y la cita no sirve.
- Las otras nueve filas de la tabla de planos del APAG.
- Owen Jones y Jules Goury, *Plans, Elevations, Sections and Details of the
  Alhambra* (1842–1845). Citada de segunda mano en las entradas 1 y 5, que la
  usan como referencia de contraste. Merece consulta directa.
- Enrique Nuere, análisis gráfico de las piezas componentes de los mocárabes,
  citado como precursor de los estudios CAD en la entrada 1.
- Los manuscritos del siglo XVII: Fray Andrés de San Miguel y Diego López de
  Arenas. Son la fuente primaria del sistema occidental y la raíz de la
  entrada 1.

---

## 13. Gámiz Gordo y Ferrer Pérez-Blanco (2019) — la gramática de Jones y Goury

**Una gramática de mocárabes: Dibujos de la Alhambra de Jones y Goury
(1834-1845)** / *A Grammar of Muqarnas*. *VLC arquitectura* 6(2), octubre 2019,
pp. 57-87. ISSN 2341-3050.
DOI [10.4995/vlc.2019.10947](https://doi.org/10.4995/vlc.2019.10947).

- Autores: **Antonio Gámiz Gordo** (ETS de Arquitectura de Sevilla) e **Ignacio
  Ferrer Pérez-Blanco** (École Polytechnique Fédérale de Lausanne).
- Recibido 10-11-2018, aceptado 09-10-2019.
- **LEÍDO DIRECTAMENTE** el 2026-08-26 en
  `docs/2019VLCGAMIZ_FERRER_MUQARNASALHAMBRA.pdf`, 31 páginas. Antes se disponía
  sólo de la página 15 y de la reproducción del artículo al final de la tesis.
- **Verificado**: portada, autores, afiliaciones, fechas, DOI, la sección
  IMAGE SOURCES y las páginas 69-71 palabra a palabra.
- **Licencia: NO CONSTA en el PDF.** No hay mención de Creative Commons ni de
  condiciones de reutilización en ninguna de las 31 páginas. Pendiente de
  comprobar en la web de la revista. Mientras tanto **se cita y se describe, no
  se reproduce**.

### Por qué importa

Es la fuente que **refuta** la afirmación de `docs/teselado.md` de que la
topología de la pieza no se puede leer de una planta. Decisión completa en
`docs/decisiones/0008-alfabeto-de-piezas.md`. Lo esencial:

1. **El texto original de Jones y Goury, impreso en la lámina X**, transcrito en
   las pp. 69-70: siete formas de tres figuras en planta —triángulo rectángulo
   (A), rectángulo (B), triángulo isósceles de **45°** (C)—, con **C3** definido
   como «a rhomboid, formed by the double isosceles triangle».
2. **La nomenclatura A1, A2, A3, B, C1, C2, C3 es de Jones y Goury**, no de los
   autores (p. 70). La **D** de la tesis es renombre de Ferrer para el rombo
   (tesis §2.5.2, p. 197). De ahí **C3 = D3**, jairas de dos niveles.
3. **«Las piezas A3 y C3, que ascienden dos niveles»** (p. 70), dicho en
   palabras. Coincide con las dos únicas piezas de la leyenda con doble flecha
   apilada, y con las dos únicas «de dos niveles» de la tesis.
4. **«Flechas indicando el sentido de ascenso del mocárabe»** (p. 70): la
   semántica de la notación, declarada por los autores.
5. **«Jones y Goury detallaron con precisión las "patillas" de estos mocárabes,
   lo que permite identificar su tipo con exactitud»** (p. 70). Es la frase que
   cambia el problema.
6. **C4 es añadido de los autores**, «que Jones y Goury no dibujaron,
   asimilándola con la C1» (p. 70). No entra en el alfabeto de siete.

### Lo que hay que desconfiar, y está dicho aquí

Jones y Goury afirman en la lámina X que «**a piece may be combined with any one
of the others by either of its sides**». La tesis explica que eso es una
**simplificación didáctica**: para ellos el perfil «carece de definición
geométrica» y no tienen el doble perfil de los manuscritos de carpintería
(§2.5.2, p. 197). Y este mismo artículo dice (p. 79) que muchos de los mocárabes
deformados que dibujaron «no obedecían al proceso de agrupación formulado por
ellos mismos». **No se usa como regla combinatoria.**

### Resoluciones útiles, medidas con `pdfimages -list`

| figura | pág. PDF | imagen | qué es | derechos |
|---|---:|---|---|---|
| 5 | 15 | 1713 × 910 @ 300 ppi | prismas, PLAN rotulado, alzado, leyenda | mixta |
| 9 | 21 | 1723 × 1040 @ 300 ppi | pechina de la Barca, lámina X + foto y dibujos propios | mixta |
| **10** | **24** | **827 × 1566 @ 300 ppi** | **Dos Hermanas: planta y sección, lámina X** [^lamx] | **Jones y Goury solo** |
| 11 | 25 | 1713 × 839 @ 300 ppi | lámina XV, sección del patio de los Leones | Jones y Goury solo |

[^lamx]: Precisado el 2026-08-27 (entrada 14): no está en la hoja grabada de la
    lámina X sino en su **hoja de texto**, la página 98 del tomo I, grabada en
    madera bajo las dos columnas. Sigue siendo lámina X y sigue siendo dominio
    público; cambia dónde hay que ir a buscarla.

La figura 10 da el octógono en ~790 px, es decir **~110 px/m**, frente a los
**72,5 px/m** de los que se digitalizó `red_medinas.json`: **1,5× mejor**, y el
doble que la reproducción dentro de la tesis. Es lámina X pura según IMAGE
SOURCES, o sea **grabado de 1842-45 en dominio público**.

**Lo que NO sostiene**: nada sobre la cúpula de Dos Hermanas pieza a pieza. El
sector rotulado de la fig. 5 tiene 18 celdas y es la muestra de gramática; el
dibujo de la cúpula tiene 5416 piezas y a 110 px/m una pieza son ~10 px. Que la
lámina resuelva figura, orientación y la marca A1/A3 en la cúpula **está sin
comprobar**.

---

## 14. Jones y Goury (1842-45) — el escaneo del Getty, y por qué no sirve

**Plans, elevations, sections, and details of the Alhambra.** Owen Jones y
Jules Goury. Escaneo del **Getty Research Institute** vía Internet Archive,
identificador **`gri_33125012280661`**
(<https://archive.org/details/gri_33125012280661>). Aportado el 2026-08-26 como
`docs/gri_33125012280661.pdf`, 356 páginas, 9,0 MB. Es el **tomo I**;
el tomo II es otro ítem y va en la entrada 15.

- **Obra en dominio público**: Goury murió en 1834, Jones en 1874.
- **VERIFICADO directamente** el 2026-08-26.

### Lo que sí aporta: el texto tipográfico de la lámina X

Páginas **97-98** del PDF, bilingüe inglés/francés, completo. Es la fuente
primaria del pasaje que el artículo de *VLC arquitectura* cita en traducción
(entrada 13), y trae dos datos que aquel no recoge:

> «**Nearly five thousand pieces** enter into the construction of the ceiling of
> the Hall of the Two Sisters; and although they are simply of plaster,
> **strengthened here and there with pieces of reed**, no part of the palace is,
> in the present day, in a more perfect state of preservation.»
> / «Près de **cinq mille morceaux** entrent dans la construction du plafond de
> la Salle des Deux Sœurs, et quoique ce ne soit que du plâtre, **renforcé avec
> des roseaux**…»

Dos consecuencias para el repositorio:

1. **El 5416 no es de Jones y Goury.** Ellos dicen «cerca de cinco mil». El
   **5416 es el recuento de Gámiz Gordo y Ferrer** (entrada 13). Citar cada
   número a quien es.
2. **Yeso reforzado con cañas**, dicho por quienes lo vieron en 1834-37, y con
   una nota sobre su estado de conservación entonces. Relevante para el objetivo
   (B) de reconstruir el material, no sólo la geometría.

### Lo que NO aporta: geometría. El derivado está comprimido con MRC

**No usar este PDF para medir nada.** Cada página son tres capas:

| capa | tamaño | qué es |
|---|---|---|
| miniatura | 684 × 1000 @ 100 ppi | descarte |
| fondo JPX | 2053 × 3000 @ 300 ppi | **6,4 KB** para una lámina entera |
| «smask» JBIG2 | 2053 × 3000, 1 bpc | **máscara de segmentación**, 87 % negra |

Seis kilobytes de JPEG2000 para 2053 × 3000 es compresión catastrófica: el color
queda como manchas sin contorno. Y la capa bilevel **no es una capa de línea**,
es la máscara que decide qué píxel viene del fondo; extraída y mirada, convierte
el grabado fino en borrones. Comprobado sobre la lámina X a resolución nativa:
los perfiles escalonados aparecen como fragmentos de color flotando **sin
ninguna línea que los una**, y el rótulo «Section on th…» sobrevive sólo porque
es tipografía.

Ningún trabajo de este repositorio se puede hacer sobre eso: el método mide con
márgenes de **un píxel del dibujo** y afirma cosas a **0,35 px** (cautela 7,
decisión 0007).

### Y su lámina X grabada no lleva el dibujo que hace falta

La **página 101** es la lámina X de este ejemplar —lo confirma la página 103,
cuyo texto dice «a portion of the arch, **shewn in Plate X.**»— y muestra la
**pechina de la sala de la Barca en color**, con su planta en cuadrante. Es la
figura 9 del artículo.

**No están en esa hoja** ni la fila de prismas con el «PLAN» rotulado (figura 5
del artículo) ni la planta y sección de Dos Hermanas (figura 10).

### Resuelto el 2026-08-27: no están en la lámina, están en su texto

No hay estado distinto ni hoja incompleta. Los dibujos de mocárabes de la
lámina X **no se imprimieron en la lámina**: son grabados de madera intercalados
en sus **hojas de texto**, las páginas 97 y 98 del propio PDF, que la entrada ya
tenía localizadas y había leído solo como texto.

- La **página 98** lleva, bajo las dos columnas, la **sección** de la cúpula de
  Dos Hermanas y debajo su **planta octogonal**. Puesta al lado de la imagen
  embebida de la figura 10 del artículo (827 × 1566), es **el mismo grabado**.
- La **página 97** lleva, bajo el texto, las **figuras primarias A, B y C en
  planta** con los rótulos (a a, a b, a c) que el texto cita, y el romboide C3.
  El MRC las ha dejado en un puñado de puntos sueltos: se sabe que están por su
  posición y por el texto, no porque se vean.

Y el propio texto de la lámina lo decía, en la frase inmediatamente anterior al
pasaje de los cinco mil trozos:

> «The conical ceilings of the Halls of Justice, Abencerrages, and Two Sisters,
> **of which we here give the plan and section**, as well as the columns and
> arches of a similar construction…»

O sea que la atribución del artículo —«detalle lámina X»— **es correcta**. Lo
que estaba mal era buscar el dibujo en la hoja grabada.

### Qué habría que conseguir en su lugar — comprobado el 2026-08-27

Consultada la ficha del ítem, **la hipótesis del `_jp2.zip` no se sostiene**.
Los derivados `_jp2.zip` de Internet Archive están normalizados a **3000 px de
alto**, sea cual sea la hoja —comprobado sobre las 220 páginas del tomo II, que
varían de ancho y no de alto—. Es un derivado de tamaño fijo, no el máster. La
etiqueta EXIF de 300 ppi que traen dentro es el valor por defecto que escribe
Capture One y no dice nada del original.

Medido sobre el octógono de la página 98, que es la prueba que importa:

| origen | octógono | equivalente |
|---|---:|---|
| figura 10 del artículo (entrada 13), 827 × 1566 @ 300 ppi | **771 px** | ~110 px/m |
| lo que daría el `_jp2.zip` del tomo I | **668 px** | ~95 px/m |

(La entrada 13 daba el octógono de la figura 10 en «~790 px»; remedido con
umbral sobre la imagen embebida salen **771**. No cambia el ~110 px/m.)

El `_jp2.zip` **sale un 13 % peor** que lo que ya hay en el repositorio. Su
única ventaja sería no llevar MRC, y la figura 10 del artículo tampoco lo lleva.
**No aporta nada medible: no hace falta descargarlo.**

Lo que sí queda identificado es el fichero que habría que conseguir:
`gri_33125012280661_images.zip`, **2,9 GB**, el paquete de imágenes de cámara
sin normalizar (Phase One IQ180, capturado el 2019-03-06). A ~8 MB por página
son mucho mayores que los 3000 px del derivado; **cuánto mayores está sin
comprobar**, y de eso depende todo.

Antes de bajar 2,9 GB conviene tener presente la escala real del grabado. En el
papel ese octógono mide **~14,6 cm**, y una de las 5416 piezas cae en **~1,8 mm
de papel** —de ahí los ~10 px por pieza que ya anotaba la entrada 13—. Para
leerlo pieza a pieza no hace falta un escaneo mejor de las 356 hojas: hace falta
un escaneo alto de **una sola hoja**, la 98 del tomo I.

El listón está medido y es concreto: la figura 10 de la entrada 13 ya da
**~110 px/m** sobre el octógono de Dos Hermanas. Un escaneo sólo aporta si
supera eso **con trazo continuo**, y la prueba de aceptación es la de la
decisión 0008: **¿resuelve pieza a pieza, con orientación legible, y separa A1
de A3?**

---

## 15. Jones y Goury, tomo II — el `_jp2.zip` aportado el 2026-08-27

**Details and ornaments from the Alhambra**, que es el título propio del
**tomo II** de la obra de la entrada 14. Escaneo del **Getty Research
Institute** vía Internet Archive, identificador **`gri_33125008608388`**
(<https://archive.org/details/gri_33125008608388>). Aportado como
`docs/gri_33125008608388_jp2.zip`: **220 imágenes JP2**, 29,7 MB.

- **Obra en dominio público** y el ítem viene marcado `NOT_IN_COPYRIGHT`.
- **VERIFICADO directamente** el 2026-08-27: abiertas las 220 páginas.
- Hoja de **58 cm** de alto (catálogo del Getty), que el derivado normaliza a
  3000 px de imagen y ~2620 px de papel: **~4500 px/m de papel**.

### Es el tomo que no lleva la cúpula

Leída entera la **«LIST OF PLATES»** de la página 12, las **50 láminas I–L** de
este tomo son ornamento: paneles, frisos, capiteles, zócalos, mosaicos. **No hay
ni una planta ni una sección.** Su lámina X son «sunk lines on the walls, House
of the Commandant» y no tiene nada que ver con la lámina X del tomo I.

**La prueba de aceptación de la decisión 0008 no llega a plantearse**: no hay
aquí dibujo de la cúpula de Dos Hermanas que resuelva o deje de resolver pieza a
pieza. Ese dibujo está en el tomo I, página 98 (entrada 14).

Correspondencia útil, comprobada en los dos sentidos contra los rótulos de las
propias láminas: **página = 16 + 4·(lámina − 1)**. La lista de la página 12
remite además a «vide plate N, vol. i» en una docena de entradas, así que sirve
de índice cruzado hacia el tomo I.

### Lo que sí aporta, y no es poco: mocárabes en color

El tomo es cromolitografía, y trae mocárabes **de la propia sala de las Dos
Hermanas**, con su policromía, a escalas grandes declaradas en la hoja:

| lámina | pág. | n.º | escala | qué es |
|---|---:|---:|---|---|
| **XXXIX** | **168** | 63 | **⅔ del natural** | cornisa de mocárabes en el arranque del arco de la Ventana, **sala de las Dos Hermanas**: alzado **y planta** |
| XXIV | 108 | 36 | ¾ del natural | ménsulas del pórtico del patio de los Leones, con fleco de mocárabes |

A ⅔ del natural sobre 4500 px/m de papel, la lámina XXXIX resuelve el elemento
real a **~3000 px/m**: un tercio de milímetro por píxel, unas **27 veces** la
figura 10 del artículo. Es, con diferencia, el dibujo de mocárabes de mayor
resolución que hay en el repositorio.

Y trae la correspondencia **planta ↔ alzado** del mismo elemento, coloreada
celda a celda, que es justo la relación que `docs/teselado.md` intenta levantar
por otros medios. Con la cautela de que es una cornisa, no la cúpula.

### La cautela que hay que ponerle al color

Jones **restituye**. Sus cromolitografías son una reconstrucción del color
original, no un registro del estado en que lo encontró, y él mismo lo dejó
dicho: la lámina 38 del **tomo I** se titula «Estado actual de los colores /
Actual state of the colours», y existe precisamente porque las demás no lo son.

Es la distinción A/B del README, hecha por un dibujante hacia 1845. Así que:

- **No es medida.** `docs/policromia.md` mide sobre la ortoimagen de 2021 y
  descarta el rojo porque su periodicidad angular no supera la línea base del
  propio yeso. La lámina XXXIX no puede refutar eso ni confirmarlo.
- **Sí es la primera fuente que reparte color celda a celda** en mocárabes de
  esta sala, que es exactamente lo que `policromia.md` declara no tener.
- Y da **oro de fondo**, que `policromia.md` había excluido *a priori* por
  indistinguible del yeso envejecido y de la suciedad.

Queda como hipótesis contrastable, no como dato. Y con ella queda una tarea
concreta: la **lámina 38 del tomo I**, que al ser «estado actual» sí es
registro, y permitiría medir cuánto se separa la restitución de Jones de lo que
tenía delante.

### Calidad del derivado, medida

- **21,4 KB por megapíxel** de media sobre las 220 páginas, frente a los
  **1,04 KB/MP** de la capa de fondo del PDF del tomo I (entrada 14): **veinte
  veces** más información por píxel, y sin máscara bilevel que trocee el trazo.
- Comprobado a 1:1 sobre la lámina XXXIX: trazo continuo, colores planos
  separados limpiamente, sin los borrones del MRC. **Aquí sí se puede medir.**

Lo cual acota bien el problema del tomo I: el defecto de aquel PDF **es el MRC,
no el escáner**. Un `_jp2.zip` del tomo I tendría esta misma calidad de trazo
—y, como mide la entrada 14, menos resolución que la figura 10 del artículo.

El fichero **no se versiona**: excluido en `.gitignore` por tamaño y por ser
fuente de consulta, no dato. Los derechos no son el motivo.
