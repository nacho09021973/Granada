# Próximos pasos

Estado a 2026-08-25. Documento de trabajo: se actualiza, no se conserva como
histórico. El registro de decisiones va en `docs/decisiones/`.

---

## Cierre de jornada — 2026-08-25

Hecha la tarea que quedaba señalada: **las caras de la red están
identificadas, medidas y clasificadas**, y cada vecindad lleva su salto
explícitamente sin firmar.

105 caras interiores (Euler `V − E + F = 2`, cero cruces, área de caras = área
de contorno = 30,690 m²). Clasifican **25**: 8 medios cuadrados y 1 octógono
regular confirmados, 16 cuadrados marcados al límite de resolución. Las otras
**80 quedan sin figura**, 51 de ellas ni siquiera convexas. Las **227
vecindades** llevan todas `"salto": null`. Suite en **588 tests superados** y
`git diff --check` limpio.

**Sigue sin propagarse nada.** El bloqueo ya no es la topología —está
completa— sino documental: falta la evidencia del signo de cada paso.

Estado de reanudación: `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS`.

---

## Dónde estamos

**Objetivo actual**: reconstruir la cúpula de mocárabes de la Sala de las Dos
Hermanas **como el día de su inauguración** — yeso blanco de obra nueva y
policromía original. Es una afirmación (B) del README: empírica, sobre un
estado perdido, y por tanto sujeta a evidencia.

### Lo que está hecho y se sostiene

| pieza | estado |
|---|---|
| Núcleo aritmético en Z[ζ_m] | **sólido**, cero dependencias |
| Perfiles de celda `cuna` y `rombo` | **correctos** — la tesis los confirma como figuras A, C y D |
| Estratificación medida de la sección | **válida** — 23 hiladas, paso ~20 cm, cono de 38° ± 0.6° |
| Orden de simetría | **medido** — retícula angular 16, simetría exacta C8, espejo → D8 |
| Paleta y policromía | **medida**, con verde sostenido y rojo descartado |
| Planta de la tesis registrada | **validada** — contraste +5.43 frente a +0.16 desplazada |
| Red de medinas completa | **323 nudos, 427 aristas, 1 componente**, 24 terminales de borde |
| Representación de niveles | **implementada** — siete tipos, A3/D3 a dos niveles, propagación fail-closed |
| Sombra como indicio | **validada solo en el extremo** — 15/16 cupulines más oscuros; no calibra niveles enteros |
| Caras del teselado | **105 caras**, Euler 2, cero cruces; 9 figuras confirmadas, 16 al límite, 80 sin figura |
| Vecindades entre teselas | **227**, todas con salto sin firmar y sin conversión parcial posible |
| Reglas de nivel candidatas | **tres refutadas** con testigo sobre la propuesta de Ferrer, no sobre la cúpula |
| Tamaño del salto de nivel | **8 unidades**, confirmado por dos fuentes independientes (Ferrer 8P y Saseta 2016) |
| Teorema del triángulo | **54 triángulos** (16 robustos = 8 pares espejo, N estricto 6): la planta exige descansos o piezas de dos niveles |
| Órbitas de caras bajo D8 | **11** órbitas (16·3 + 8·7 + 1), estables en 25 de 30 tolerancias; la sección norte-sur solo alcanza **5** con corte resoluble, y quedan **6** |
| Proyección de la sección sobre la planta | **casa en orden, residuo 9,5 mm**, con el eje B como control negativo (73 mm); las dos escalas concuerdan solo al 4 % |
| Simetría del dibujo de Ferrer | **exacta a 0,35 px**: no contiene la asimetría real de la cúpula, y eso refuerza la cautela 6 |

### Lo que hay que tirar

- `granada/celda.py`: la función **`trapecio`**. Me la inventé; no corresponde a
  ninguna figura del sistema occidental.
- `granada/estratificacion.py`: la **estratificación por coronas polares**
  completa. El modelo correcto es un teselado, no anillos concéntricos.
- `granada/adaraja.py`: el **perfil de cónica única**. La tesis documenta
  plantilla de **doble perfil** (mayor en quintos a 7P, menor en séptimos a
  7,5P, nivel siguiente a 8P) con perfiles **paralelos** entre piezas vecinas.
- Sus tests correspondientes.

No borrar todavía: hasta que el sustituto funcione, el código muerto sirve de
referencia. Pero que quede marcado como muerto.

---

## Tarea del nivel de cada tesela: estado

Es lo que convierte una planta en cúpula, y es lo que falta.

**Dificultad conocida**: las piezas **A3 y D3 abarcan dos niveles** (medios
cuadrados y jairas «de dos niveles»). El nivel no es una función de la tesela;
es una función de la tesela *y* su topología.

Vías posibles, por orden de coste:

1. **Deducirlo de la sombra en la ortoimagen.** La profundidad de cada celda se
   correlaciona con su luminancia: las celdas hondas están en sombra. Con las
   16 copias simétricas agrupadas hay señal suficiente para intentarlo. Barato
   y usa datos que ya tengo.
2. **Deducirlo de la topología de la red.** Si las medinas separan niveles
   consecutivos, el nivel se propaga por el grafo desde el borde. La red está
   completa y las caras y vecindades ya están identificadas; lo que falta —y
   la topología por sí sola no da— es el signo/salto de cada paso.
3. **Leerlo de la tesis.** El capítulo 3 propone una representación de plantas
   con líneas de nivel y con puntos, precisamente para esto. Mirar
   `3.2.5 Plantas con líneas de nivel` y `3.3.2 Planta propuesta`.

### Hecho

- **Contadas las órbitas de caras** bajo el diédrico de orden 16
  (`granada/caras.py`, `orbitas_por_simetria`): **11 órbitas** de tamaños
  16·3, 8·7 y 1, suma 105, todos divisores de 16, y el once aguanta 25 de 30
  combinaciones de tolerancia —las 5 que fallan se delatan solas con un tamaño
  que no divide al grupo—. Es la cadena 211 saltos → 104 niveles → **11
  incógnitas si la nivelación respeta la simetría**, hipótesis falsable contra
  los mismos 107 ciclos, no un dato. La sección norte-sur de Almagro es de
  **clase A** por la planta de la sala. Con el filtro de resolución —un corte
  exige un píxel del dibujo a los dos lados, y los que caen miden 0,03–0,41 px
  frente a 17,6 px del más justo que queda— alcanza **5 órbitas** y 33 caras, y
  deja **6 sin cota**, 72 de las 105 caras. Las órbitas **2, 5 y 7**, que son
  las tres de 16 y suman 48 caras, **no las alcanza ningún eje de simetría**. Y
  las 11 caras que el eje de clase A toca son exactamente las 11 de la costura
  del espejo. Decisión 0007.
- **Proyectada la sección sobre el grafo, y casa.** Las 5 fronteras radiales del
  eje A —0,597, 0,844, 1,681, 2,151 y 3,295 m— se emparejan en orden con los 5
  complejos de escalón de la silueta, con residuo medio de **9,5 mm** (p =
  0,014 frente a radios al azar). El **control negativo pasa**: las fronteras
  del eje B contra los mismos escalones dan 73 mm y p = 0,23. Queda una cota
  absoluta por órbita alcanzada, pero **una banda no es un nivel**: las órbitas
  6 y 0 abarcan 6,5 y 8,1 hiladas, porque la red de medinas es más gruesa que
  las hiladas reales. El barrido de escala tiene el mínimo en ×1,04 y el valle
  plano de 1,00 a 1,06: las dos calibraciones concuerdan al 4 %, no mejor.
  Decisión 0007.
- **Medido cuánto depende la proyección de qué eje de la clase A sea.** Los
  cuatro —0°, 45°, 90° y 135°— dan las mismas 6 órbitas tocadas, las mismas 5
  resolubles y el mismo ajuste contra la sección: **9,5 – 10,6 mm**, frente a
  **72,6 – 73,7 mm** de los cuatro ejes de la clase B. La proyección y su
  control negativo son indiferentes a la orientación. La horquilla entre los
  cuatro ejes, de 2,6 a 9,6 mm por frontera, es del mismo orden que el residuo:
  es el suelo de lo que el dibujo da, y no hay nada que afinar por debajo del
  centímetro.
  Lo que sí cambia es cuánto se apoya en la mitad pegada: por el eje de 0°, que
  **es** la costura del espejo, las 11 caras son las 11 de la costura; por el de
  90° hay 5 digitalizadas del ráster, 5 reflejadas y sólo el octógono sobre la
  costura. Y la bóveda no puede decir cuál es: si es D8, nada de ella distingue
  el 0° del 90°. Decisión 0007.
- **Comprobada la asimetría izquierda-derecha sobre la planta: no está.** A
  primera vista 10 de 10 órbitas tienen el radio medio mayor a la derecha
  (+0,23 % de mediana), pero eso lo produce un solo grado de libertad: el
  centro. Ajustándolo —queda a **3,1 mm, 0,22 px** del centroide del octógono—
  la señal se va: 4 de 10 y mediana −0,03 %. El área, invariante por traslación,
  nunca dio señal. La dispersión radial dentro de cada órbita es de **4,9 mm
  rms = 0,35 px**, por debajo del suelo de la digitalización. La figura 128 es
  simétrica hasta el límite de su propio dibujo, así que **no sirve para medir
  la deformación** — y su ausencia refuerza la cautela 6. La asimetría real sí
  se ve, pero en la ortoimagen: es el emborronamiento de `docs/policromia.md`.
  Decisión 0007.
- **Comprobada la cota de 1,082 m sobre AA-415_23: la intención era correcta y
  el número no.** La escala gráfica da 236,2 px/m a 150 dpi (2362 px / 10 m),
  confirmada por tercera vez; 233,8 px/m es un 1,0 % bajo y vale 11 mm sobre la
  propia cota. En metros, 1,082 m cae en un tramo liso y el escalón más próximo
  queda a 31–44 mm; el acuerdo de 13 mm solo aparece bajando el umbral a 1 px,
  donde hay un «escalón» cada 27 mm y acertar por 13 mm es lo esperable por
  azar. La proyección sí identifica el final de las dos primeras órbitas: el
  octógono acaba en **0,862 m** y los medios cuadrados en **1,113–1,122 m**, y
  es esa la cota que el plano sostiene. Decisión 0007.
- Identificadas las **caras** por rotación de semiaristas (`granada/caras.py`,
  sin dependencias): 105 caras, Euler `V − E + F = 2`, cero cruces en los
  90 951 pares de aristas y área de caras igual a la del contorno. Clasificadas
  solo contra las plantillas documentadas y con la tolerancia que impone la
  resolución del dibujo: 8 medios cuadrados y 1 octógono confirmados (órbita
  C8 exacta, margen 3,9× y 6,5× frente a las plantillas de control), 16
  cuadrados al límite de resolución y 80 caras sin figura. Decisión y controles
  en `docs/decisiones/0005-caras-y-vecindades.md`.
- Refutadas tres reglas de nivel candidatas sobre el dual de 105 caras, 211
  vecindades y 107 ciclos: «toda medina salva un nivel» es imposible porque el
  grafo no es bipartito; «se sube uno hacia el centro» rompe 67 ciclos;
  «ortogonales suben, diagonales descansan», otros 67. Los dos controles
  positivos pasan, así que el test no rechaza por costumbre. Aguanta descartar
  toda medina compartida de menos de 30 px. Decisión 0006.
- **Teorema del triángulo**: en tres teselas mutuamente vecinas los tres saltos
  no pueden valer ±1, porque una suma impar no cierra en cero. Hay 54
  triángulos, 16 de ellos robustos. La planta exige por sí sola descansos o
  piezas de dos niveles — justo lo que la tesis documenta como A3, D3 y
  descansos. Es topología pura: ni fotometría, ni radio, ni suposición de
  altura.
- Representadas las **227 vecindades** con `salto = None`. Firmar exige citar
  evidencia y `restricciones_firmadas` falla mientras quede una sin firmar: no
  hay propagación parcial que aparente una planta resuelta.
- Leídas directamente `3.2.5 Plantas con líneas de nivel` y `3.3.2 Planta
  propuesta`, incluidas las figuras 28–29. La planta propuesta codifica
  sentido, tipología y niveles de ascenso con **una o varias flechas dentro de
  cada figura**; una arista compartida no tiene por qué tener un sentido único.
- Implementado `granada/niveles.py`: separa tipo/topología, nivel absoluto y
  restricciones entre nodos. Detecta ciclos contradictorios y deja componentes
  sin ancla sin resolver. A3 y D3 salvan dos niveles.
- Contrastada la sombra sobre los 16 cupulines conocidos: 15/16 son más oscuros
  que controles al mismo radio, diferencia mediana +16,99, p=3,05·10⁻⁵. La
  señal existe, pero la sensibilidad radial y los confundidores impiden una
  función brillo → nivel.
- Completada la red desde la mitad superior de la figura 128 —la propuesta de
  la tesis— y reflexión D8, sin mezclar la mitad inferior de Jones y Goury:
  323 nudos, 427 aristas, una componente, 105 ciclos y 24 terminales de borde.
  El resultado es idéntico para umbrales 170–230. Procedimiento y techo de
  afirmación en `docs/decisiones/0004-red-medinas-completa.md`.

### Bloqueo documental de las restricciones

La figura 128 específica de Dos Hermanas **no contiene las flechas ni cotas**
de la representación propuesta. La red ya es conexa, pero conectividad no
equivale a una diferencia de nivel: falta identificar las caras y codificar en
cada paso si hay ascenso, descanso o descenso.

`BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS`

No asignar niveles por brillo, radio ni distancia de grafo. Las teselas ya
están identificadas y sus 227 vecindades listadas: lo único que falta es el
signo de cada paso. Solo cuando esté firmado se comprobará si una propagación
anclada en los 24 terminales de borde es consistente.

**Atajos ya cerrados por escrito** (decisión 0006): un nivel por medina, el
ascenso hacia el centro y el reparto ortogonal/diagonal son imposibles sobre
esta planta, con ciclo testigo cada uno. No volver a proponerlos.

**Confirmación externa del bloqueo (2026-08-25).** El informe documental de la
entrada 8 de `docs/fuentes.md` vació Dialnet, TESEO, Digibug, RiuNet, APAG,
RABASF e IAPH y concluye que **no existe en el dominio público ninguna tabla
que asocie cada pieza a una cota**. El bloqueo no es un fallo de búsqueda.

**El tamaño del salto ya está, el signo no.** Saseta Velázquez (2016) da «la
pauta para la elevación entre un nivel y otro de adarajas es de 8 unidades»,
que coincide con el 8P de la plantilla de doble perfil de Ferrer. Dos fuentes
independientes, el mismo número. Pero el tamaño de un salto no es su signo.

**La regla de medir se ha afinado (2026-08-26).** Del PDF de AA-415_23 han
salido dos cosas que afectan a todo lo ya medido, ninguna de ellas una cota:

- **Escala exacta, del autor y no medida.** Los once ticks de la escala gráfica
  son vectores: 9449 unidades para 10 m, que con la matriz global del flujo dan
  **40,0008 mm por metro real → 1/24,9995, +0,0019 %**. La sección 7 tenía
  0,01 % midiendo sobre ráster.
- **Doble de resolución.** Las dos ortoimágenes, extraídas a resolución nativa,
  están a **300 ppi = 472,5 px/m**, exactamente el doble de los 236,2 px/m con
  los que se hicieron la sección 7 y `estratificacion.md`. 1 px = 2,12 mm
  reales. Ficheros en `docs/`, ignorados por git.

Nada de esto mueve el bloqueo: una ortofoto no tiene cota Z, igual que no la
tiene una sección.

**Mediciones rehechas el 2026-08-26, y el resultado es que no cambia nada.**
Todos los valores de `docs/estratificacion.md` caen dentro del error de los
anteriores: paso de hilada 19,8 ± 0,1 cm, pendiente 0,789 ± 0,015, ángulo del
cono 38,3° ± 0,6°. El único movimiento es el número de hiladas, de «~23» a
**24 ± 1**, y no por precisión sino porque la última hilada es genuinamente
ambigua: entre umbral 240 y 245 el final del cono se desplaza una hilada
entera.

Lo que hay que retener para la próxima vez: **el error no ha bajado**. Sigue en
± 0,015 con el píxel a 2,1 mm igual que con el píxel a 4,2 mm, porque el
residuo del ajuste es de 9,3 cm rms —cuarenta veces el píxel—. El límite no era
la resolución, sino que el perfil es escalonado y la cúpula está deformada.
Pedir más resolución para estrechar esa barra no funciona.

De paso quedan dos cosas que no había: la medición vive ahora en
`scripts/medir_estratificacion.py` en vez de haber sido ad hoc, y la
incertidumbre por umbral se cuantifica corriendo con tres.

La medición del orden de simetría (sección 7 de `fuentes.md`) **no se ha
rehecho porque ya estaba a resolución nativa**. Sí se ha reproducido desde cero:
sus dos conclusiones se sostienen, pero sus porcentajes no son reproducibles
mientras no documente su normalización y los radios de sus zonas. Anotado allí.

Y descarta el DXF que llegó ese día (entrada 12): es una vectorización
automática, todas sus Z valen 0, y al aplicarse sobre una ortofoto no traza el
despiece sino contornos de mancha del yeso.

**Consulta enviada el 2026-08-26.** `docs/consulta-almagro.md` salió a
**Antonio Almagro Gorbea**, y una versión adaptada a **Ignacio Ferrer
Pérez-Blanco** —cuyo texto todavía no está en el repositorio—. Cuatro
preguntas: los datos de origen del levantamiento, la existencia de una planta
con cotas, la orientación de la lámina y las condiciones de uso. La 1 es la
única que puede desbloquear esto de golpe; la 2 es de Ferrer antes que de
nadie, porque pregunta por la figura 128 de su propia tesis. Sin respuesta
todavía. Cuando llegue —incluso si es una negativa— entra en `fuentes.md` como
entrada nueva y con fecha.

Mientras tanto, **el estado no cambia**: una consulta enviada no es un dato, y
`BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` sigue vigente.

**El verificador ya está montado (2026-08-26).** `granada/falsacion.py` y
`scripts/verificar_saltos_firmados.py` esperan al primer salto firmado. Hoy,
sin datos, dicen `SIN_SALTOS_FIRMADOS` y 11 órbitas libres; con un dato dan la
respuesta en el acto. Lo que salió al construirlo:

- Las **211 vecindades colapsan en 16 clases** bajo la hipótesis de simetría, y
  **un solo salto firmado determina su clase entera** —de 4 a 16 vecindades—.
- El cociente deja **6 ciclos de cierre**: seis ecuaciones que unos saltos
  firmados tienen que satisfacer, y seis maneras de refutar la hipótesis.
- **Diez saltos bien elegidos** fijan la nivelación entera salvo la cota
  absoluta. Comprobado en `tests/test_falsacion.py`.
- De regalo, un defecto de los datos: la clase de órbitas **2–7 tiene 15
  vecindades y debería tener 16**. Faltan `c078`–`c068`, a azimuts contiguos.
  No refuta nada; acusa a la digitalización. Registrado en la decisión 0007 y
  **no corregido a mano**.

Así que la petición a quien pueda contestar es mucho más pequeña de lo que
parecía: **un salto firmado sirve para empezar y diez lo cierran**, en vez de
5.416 cotas o 211 signos.

**Dónde puede salir el signo**, por orden de coste:

1. Una planta de Dos Hermanas —de la tesis o de otro autor— que traiga flechas
   o cotas. Es lo que la sección 3.3.2 propone y la figura 128 no aplica.
2. La sección medida: `docs/estratificacion.md` da 23 hiladas y paso ~20 cm.
   Una cara cuyo radio y cota se puedan casar con una hilada firmaría su ancla,
   no sus vecindades. Cuidado: es la propagación por coronas por otro camino.
3. ~~La capa vectorial de AA-415_23.~~ **No existe** (leído el PDF entero el
   2026-08-26, entrada 3 de `fuentes.md`): sus capas son `Orto` —dos JPEG— y
   `Rotulo` —escala y textos—, y el flujo de la página son 1823 bytes. La
   lámina es fotogrametría texturizada, no delineación. Lo que se comprobó que
   existe —AutoCAD 2010, A0, `/OCProperties`, `/OCGs`— es eso, no un dibujo de
   líneas. El plano tampoco **lleva cotas escritas**: 20
   palabras de texto en todo el A0. Da un perfil medible contra la escala 1/25,
   no niveles por tesela; y una sección no puede firmar 211 vecindades en
   planta. Acotado además por la decisión 0007: la sección que existe es de
   clase A, alcanza 5 de las 11 órbitas con corte resoluble, y las 11 caras que
   toca son las 11 de la costura del espejo. Lo que sí da, y está medido, es una
   cota absoluta por órbita alcanzada — pero una banda de la sección abarca
   hasta 8 hiladas, así que no es un nivel.
4. **Las 104 adarajas de estrella del PMAA — localizadas** (entrada 10 de
   `fuentes.md`). No están en el impreso de *Revista PH* 106 sino en la versión
   web del mismo artículo, como **pie de una figura**: 104 piezas sobre
   ortofotografía cenital, en 5 tipos. Es imagen, no tabla, y sin método
   publicado. Y *Revista PH* va con licencia **CC BY-NC-ND**: se puede citar,
   **no derivar geometría**. Si hiciera falta como dato, se pide permiso al
   autor.

---

## Después

- **Completar la red — hecho.** El seguimiento de esqueleto conserva los giros
  y elimina el contorno punteado: 323 nudos y 427 aristas en una componente.
- **Identificar caras y restricciones — hecho.** 105 caras, 25 clasificadas
  (9 confirmadas), 227 vecindades con el salto explícitamente sin firmar.
  Ninguna cara recibe `TipoMocarabe`: de la planta se lee la figura, no la
  topología.
- **Firmar los saltos — siguiente tarea.** Es documental, no de código: hace
  falta una fuente que diga, para cada paso, si asciende, descansa o
  desciende.
- **Módulos mixtos.** Confirmado que esta cúpula no tiene módulo único
  (residuo del 18–23 % con el mejor módulo). El modelo tiene que admitir
  piezas de distinto módulo, no forzar uno.
- **Doble perfil.** Rehacer `adaraja.py` con las dos plantillas y la regla de
  paralelismo entre vecinas.
- **Levantar y renderizar.** Solo cuando la planta con niveles esté validada
  sobre la ortoimagen. **No repetir el error de renderizar sin validar la
  planta.**
- **Página interactiva.** Es el destino acordado: cúpula girable, selector de
  orden y controles de color. Queda para el final.

---

## TODO abiertos, sin inventar

- **Los «siete niveles» de Martínez Sevilla.** La prensa de la exposición del
  PMAA le atribuye el hallazgo de que la cúpula tiene siete niveles, que
  evocarían los del Salón del Trono. No hay publicación con método detrás, no
  se dice si cuenta niveles de adarajas de estrella o del mocárabe completo, y
  la sección medida da 23 hiladas. Queda anotado en la entrada 10 como
  afirmación de terceros, fechada y localizada; **no se usa como cota**.
- **El oro.** Documentado en yeserías nazaríes —letras doradas sobre fondo azul
  lapislázuli en el Mexuar, 1362— pero **nada específico de esta cúpula**. Su
  tono (40–60°) es indistinguible de la suciedad en la ortoimagen. Haría falta
  una fuente con análisis de pigmento in situ.
- **El rojo.** Descartado con *esta* imagen: su periodicidad angular queda por
  debajo de la línea base del propio yeso. Que el bermellón formaba parte de la
  paleta nazarí está documentado; que estuviera *aquí*, y dónde, no.
- **El negro carbón.** Indistinguible de la sombra de las cavidades.
- **Referencias del informe de altimetría, verificación parcial hecha**
  (2026-08-25). Comprobadas: la tesis de Ferrer, Saseta Velázquez 2016 —leída
  entera, ahora entrada 9—, Roldán-Medina 2018 y *Revista PH* 106, que existe
  pero **no contiene lo que se le atribuía**. Quedan las signaturas P-000159 y
  D-0353 del APAG, los inventarios 006601 y 006091 del Museo y MakerWorld
  3150958.
- **Las 80 caras sin figura.** Se agrupan por área en familias de 16, 24, 8, 8,
  8 y 16 copias, así que son regiones reales del dibujo, no ruido. La figura
  128 no las subdivide; una planta más fina de esta cúpula las resolvería.
- **Las nueve filas restantes** de la tabla de planos del APAG en
  `docs/investigacion-preliminar.md`, sin verificar.
- **La capa vectorial** de AA-415_23, sin extraer. Daría geometría en vez de
  fotometría para la medición del orden de simetría.
- **La fotografía de la cúpula** aportada el 2026-08-25
  (`docs/Cúpula_de_la_sala_de_las_Dos_Hermanas_(Alhambra,_Granada).jpg`, 3964 ×
  2973). **Origen y licencia sin registrar**: está excluida en `.gitignore`
  hasta que consten en `fuentes.md`. Como geometría no sirve —es perspectiva,
  desde un punto desconocido, sobre una superficie no plana—. Para policromía
  podría servir como **segunda imagen independiente** de la misma superficie,
  que es lo que hoy falta, pero antes hay que neutralizar su dominante cálida:
  el 98 % de sus píxeles saturados caen en naranja y ocre, que es el yeso bajo
  esa luz, no pigmento. Lo que sí muestra, y la ortoimagen de AA-415_23 no, son
  **los vanos del tambor**: es la única vía a la vista para orientar la lámina
  respecto del edificio sin depender de una indicación externa.
- **La orientación de la lámina respecto del edificio**, sin fuente. Se ha
  anotado como información del autor que la parte alta de la imagen es la
  fachada principal, de donde el norte-sur sería el eje de 90°. Falta una
  fuente citable: una planta de la sala orientada, o el pie de la propia lámina.
- **Heritage 6(12) 388** (cúpula de la Sala de los Reyes): existencia
  verificada, contenido sin leer — MDPI devuelve 403.

---

## Cautelas que no hay que perder

1. **Z[ζ₁₆] es denso en el plano.** No es una retícula. Cualquier test de
   «ajuste a la retícula» sin acotar coeficientes es vacío: comprobado que con
   coeficientes de hasta 40 unos puntos aleatorios ajustan igual de bien que
   los reales. **Todo test lleva control.**
2. **Validar la planta antes de renderizar.** El primer render salió feo por
   modelar una superficie de revolución corrugada en vez de un teselado, y se
   descubrió tarde porque nunca se comparó la planta contra la ortoimagen.
3. **La razón diagonal/ortogonal medida (0.7679 contra √(2−√2) = 0.7654)** es
   más precisa de lo que el método merece. Defendible: vale ~0.77, no 1 ni √2.
4. **Derechos — revisado el 2026-08-26, y en buena parte resuelto.** Las
   figuras de la tesis son obra de su autor y **no se redistribuyen** aquí; se
   citan y se usan como referencia para construir geometría propia. Para el
   plano AA-415_23 la condición ya está leída (entrada 3 de `fuentes.md`):
   **«Se autoriza su uso con fines de docencia e investigación»**. Este trabajo
   lo es, así que **derivar geometría de la lámina está autorizado** y deja de
   ser el paso que había que revisar antes de darlo.
   Lo que la autorización **no** cubre es la licencia del repositorio: el mismo
   texto reserva el uso comercial a autorización expresa del autor, y **MIT
   concede uso comercial a cualquiera**. No es la derivación lo que choca, es
   la licencia de salida. Ver la entrada 3 para las dos vías: separar la
   licencia de los datos derivados, o la respuesta de Almagro a la pregunta 4
   de la consulta. Y la atribución es obligatoria y doble: autoría **y**
   referencia de la publicación previa.
5. **El espejo de la red se impuso, no se midió.** La mitad inferior de
   `datos/red_medinas.json` es reflexión de la superior. De ahí dos reglas: la
   red **nunca** sirve como evidencia de la simetría especular —sería
   circular—, y al contar instancias hay que clasificarlas **por vértices**
   antes de dar un N: una cara que cruza el eje depende del pegado. Los 16
   triángulos robustos son 8 pares, y solo **6** tienen las tres caras
   digitalizadas: N estricto = 6. De las 8 caras de medio cuadrado, 3. De los
   16 cuadrados, 8. El octógono central, ninguna.
6. **Lo refutado lo es sobre el dibujo de Ferrer, no sobre la cúpula.** Si el
   autor replicó un sector en CAD, las 16 apariciones son una decisión del
   dibujante y ningún tratamiento del ráster lo distingue. La refutación de las
   tres reglas hereda el techo de la decisión 0004, no uno más fuerte.
7. **Todo predicado geométrico lleva margen.** «¿Cruza esta cara el eje?» sin
   margen contestó que sí para una cara que asoma **0,032 px**, y con eso la
   sección parecía alcanzar una órbita más de las que alcanza. El margen no se
   elige: es un píxel del dibujo. La comprobación de que no parte una nube
   continua es que las dos poblaciones quedan a un factor de cuarenta.
8. **La cúpula real está deformada.** Los escaneos láser lo documentan en otras
   salas, y aquí se nota en el emborronamiento al promediar las 16 copias.
   Cualquier afirmación (B) es «ajusta dentro de una tolerancia», nunca
   «reproduce».
