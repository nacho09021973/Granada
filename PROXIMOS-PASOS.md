# Próximos pasos

Estado a 2026-08-24. Documento de trabajo: se actualiza, no se conserva como
histórico. El registro de decisiones va en `docs/decisiones/`.

---

## Dónde estamos

**Objetivo actual**: reconstruir la cúpula de mocárabes de la Sala de las Dos
Hermanas **como el día de su inauguración** — yeso blanco de obra nueva y
policromía original. Es una afirmación (B) del README: empírica, sobre un
estado perdido, y por tanto sujeta a evidencia.

### Lo que está hecho y se sostiene

| pieza | estado |
|---|---|
| Núcleo aritmético en Z[ζ_m] | **sólido**, 509 tests, cero dependencias |
| Perfiles de celda `cuna` y `rombo` | **correctos** — la tesis los confirma como figuras A, C y D |
| Estratificación medida de la sección | **válida** — 23 hiladas, paso ~20 cm, cono de 38° ± 0.6° |
| Orden de simetría | **medido** — retícula angular 16, simetría exacta C8, espejo → D8 |
| Paleta y policromía | **medida**, con verde sostenido y rojo descartado |
| Planta de la tesis registrada | **validada** — contraste +5.43 frente a +0.16 desplazada |
| Red de medinas extraída | **71 nudos, 48 aristas**, direcciones confirmadas a 1.23° |

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

## Siguiente tarea: el nivel de cada tesela

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
   consecutivos, el nivel se propaga por el grafo desde el borde. Requiere que
   la red extraída esté completa, y hoy tiene 48 aristas de las que debería
   tener.
3. **Leerlo de la tesis.** El capítulo 3 propone una representación de plantas
   con líneas de nivel y con puntos, precisamente para esto. Mirar
   `3.2.5 Plantas con líneas de nivel` y `3.3.2 Planta propuesta`.

**Empezar por (3)**, que es leer, y luego (1) para contrastar.

---

## Después

- **Completar la red.** 48 aristas para 71 nudos es poco: el trazado se pierde
  en los cruces densos de la corona interior. Mejorar el seguimiento del
  esqueleto o bajar el umbral de binarizado.
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
