# Próximos pasos

Estado a 2026-08-28. Documento de trabajo: se actualiza, no se conserva como
histórico. El registro de decisiones va en `docs/decisiones/`.

---

## Actualización — respuesta de Ferrer, 2026-08-28

La comunicación personal registrada en `docs/fuentes.md`, entrada 11, no
levanta `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` como afirmación histórica:
la captura permite contrastar el número global de niveles, pero no firma
ninguna de las 227 vecindades de la planta. La decisión 0007 sí habilita una
salida paralela `APPROXIMATE_LEVELS_AVAILABLE` para continuar el modelo 3D con
una hipótesis radial explícita y reemplazable.

Sí identifica la vía documental correcta. Ferrer indica que el sentido de
ascenso debe deducirse de fotografías y que las piezas vecinas han de mantener
un sentido coherente. El siguiente trabajo ya no es buscar una regla radial
universal, sino reunir fotografías oblicuas de resolución suficiente,
registrarlas contra la planta y anotar orientaciones observables con su
procedencia. La coherencia entre vecinas será una validación de esas
observaciones, no una fuente para inventar las que falten.

Su recuento rápido de **24 niveles** sobre el alzado de Almagro es compatible,
dentro de la incertidumbre del método, con las **~23 hiladas** medidas en
`docs/estratificacion.md`. No se fusionan aún ambas cifras: primero hay que
igualar la definición de nivel y los límites de la cuenta.

Ferrer aclara además que las **ocho unidades entre niveles no constan en los
manuscritos**. El 8P queda como pauta de reconstrucción moderna documentada por
Saseta y usada en los modelos de Ferrer, no como regla histórica transmitida
por Fray Andrés de San Miguel o López de Arenas.

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

**La propagación histórica sigue bloqueada.** El bloqueo ya no es la topología
—está completa— sino documental: falta la evidencia del signo de cada paso.
Desde la decisión 0007 existe además una nivelación aproximada separada, apta
para prototipos y explícitamente no verificada.

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
| Tamaño del salto de nivel | **8 unidades**, pauta moderna documentada por Saseta y usada por Ferrer; no consta en los manuscritos |
| Teorema del triángulo | **54 triángulos** (16 robustos = 8 pares espejo, N estricto 6): la planta exige descansos o piezas de dos niveles |
| Nivelación aproximada | **disponible** — 105 caras, 227 saltos, niveles 0–7 y sensibilidad 7/8 explícita |

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

No presentar niveles por brillo, radio o distancia de grafo como datos
observados. Las teselas ya están identificadas y sus 227 vecindades listadas:
lo único que falta para la versión histórica es el signo de cada paso. La
decisión 0007 autoriza la distancia de grafo únicamente como hipótesis de
trabajo separada en `datos/niveles_aproximados.json`.

**Atajos ya cerrados por escrito** (decisión 0006): un nivel por medina, el
ascenso hacia el centro y el reparto ortogonal/diagonal son imposibles sobre
esta planta, con ciclo testigo cada uno. No volver a proponerlos.

**Confirmación externa del bloqueo (2026-08-25).** El informe documental de la
entrada 8 de `docs/fuentes.md` vació Dialnet, TESEO, Digibug, RiuNet, APAG,
RABASF e IAPH y concluye que **no existe en el dominio público ninguna tabla
que asocie cada pieza a una cota**. El bloqueo no es un fallo de búsqueda.

**El tamaño del salto ya está como hipótesis moderna, el signo no.** Saseta
Velázquez (2016) da «la pauta para la elevación entre un nivel y otro de
adarajas es de 8 unidades», que coincide con el 8P usado en la plantilla de
doble perfil de Ferrer. Ferrer aclara en su respuesta del 2026-08-28 que ese
número no está escrito en los manuscritos: procede de deducciones posteriores
o medidas empíricas. Por tanto, 8P es un parámetro documentado de
reconstrucción, no una constante histórica demostrada. Y el tamaño de un salto
no es su signo.

**Dónde puede salir el signo**, por orden de coste:

1. **Fotografías oblicuas de alta resolución**, registradas contra la planta.
   Ferrer confirma que el sentido se deduce eficazmente de fotografías y que
   las piezas vecinas han de ser coherentes. Cada orientación anotada deberá
   conservar imagen, región y criterio de lectura; la coherencia solo valida,
   no rellena observaciones ausentes.
2. Una planta de Dos Hermanas —de la tesis o de otro autor— que traiga flechas
   o cotas. Es lo que la sección 3.3.2 propone y la figura 128 no aplica. La
   cuarta imagen del ejercicio docente de Ferrer de 2023 muestra el método de
   flechas y líneas de nivel, pero no aporta la solución de Dos Hermanas.
3. La sección medida: `docs/estratificacion.md` da 23 hiladas y paso ~20 cm.
   Una cara cuyo radio y cota se puedan casar con una hilada firmaría su ancla,
   no sus vecindades. Cuidado: es la propagación por coronas por otro camino.
4. La capa vectorial de AA-415_23. Comprobado que existe —AutoCAD 2010, A0,
   con `/OCProperties` y `/OCGs`— pero el plano **no lleva cotas escritas**: 20
   palabras de texto en todo el A0. Da un perfil medible contra la escala 1/25,
   no niveles por tesela; y una sección no puede firmar 211 vecindades en
   planta.
5. **Las 104 adarajas de estrella del PMAA — localizadas** (entrada 10 de
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
- **Levantar y renderizar.** Ya puede hacerse un prototipo con
  `datos/niveles_aproximados.json`, rotulado como aproximado y mostrando la
  sensibilidad 7/8. La versión histórica seguirá esperando validación sobre
  fotografías. **No presentar el prototipo como reconstrucción verificada.**
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
4. **Derechos.** Las figuras de la tesis son obra de su autor y **no se
   redistribuyen** aquí; se citan y se usan como referencia para construir
   geometría propia. El plano AA-415_23 es material de la RABASF: leerlo para
   verificar es legítimo, derivar geometría para un repo MIT exige revisar sus
   condiciones **antes**.
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
7. **La cúpula real está deformada.** Los escaneos láser lo documentan en otras
   salas, y aquí se nota en el emborronamiento al promediar las 16 copias.
   Cualquier afirmación (B) es «ajusta dentro de una tolerancia», nunca
   «reproduce».
