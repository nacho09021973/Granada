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

**Dónde puede salir el signo**, por orden de coste:

1. Una planta de Dos Hermanas —de la tesis o de otro autor— que traiga flechas
   o cotas. Es lo que la sección 3.3.2 propone y la figura 128 no aplica.
2. La sección medida: `docs/estratificacion.md` da 23 hiladas y paso ~20 cm.
   Una cara cuyo radio y cota se puedan casar con una hilada firmaría su ancla,
   no sus vecindades. Cuidado: es la propagación por coronas por otro camino.
3. La capa vectorial de AA-415_23, aún sin extraer, si distingue cotas.

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

- **El oro.** Documentado en yeserías nazaríes —letras doradas sobre fondo azul
  lapislázuli en el Mexuar, 1362— pero **nada específico de esta cúpula**. Su
  tono (40–60°) es indistinguible de la suciedad en la ortoimagen. Haría falta
  una fuente con análisis de pigmento in situ.
- **El rojo.** Descartado con *esta* imagen: su periodicidad angular queda por
  debajo de la línea base del propio yeso. Que el bermellón formaba parte de la
  paleta nazarí está documentado; que estuviera *aquí*, y dónde, no.
- **El negro carbón.** Indistinguible de la sombra de las cavidades.
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
5. **La cúpula real está deformada.** Los escaneos láser lo documentan en otras
   salas, y aquí se nota en el emborronamiento al promediar las 16 copias.
   Cualquier afirmación (B) es «ajusta dentro de una tolerancia», nunca
   «reproduce».
