# Policromía: qué sostiene la evidencia y qué no

Medido el 2026-08-24 sobre la ortoimagen cenital de AA-415_23.

Objetivo: reconstruir la cúpula **como el día de su inauguración**, no como está
hoy. Eso es una afirmación (B) del README — empírica, sobre un estado perdido —
así que aquí se separa con cuidado lo medido de lo supuesto.

## El multiplicador: 16 copias del mismo diseño

El grupo de simetría es D8: ocho rotaciones de 45° más espejo, orden 16. El
dominio fundamental es de **22.5°** y está fotografiado **dieciséis veces**.

El eje especular se localizó minimizando la diferencia con la imagen reflejada:
cae en **0°**, con un error 4.5 veces menor que la peor hipótesis posible.

Agrupar las 16 copias convierte una superficie deteriorada en una lectura mucho
mejor que la de cualquier punto concreto. Dato lateral: **el emborronamiento
residual del promedio es la deformación** — las copias no se solapan al píxel
porque la cúpula real no es exactamente simétrica, que es justo lo que
documentan los escaneos láser (`fuentes.md`, entradas 1 y 5).

## Los pigmentos: documentados

Del Patronato de la Alhambra, literalmente:

> «Como acabado decorativo esta la policromía realizada con pigmentos minerales
> que muestran los colores: azul, rojo, negro, verde. Junto con incorporaciones
> metálicas de oro y plata.»

Los análisis por microscopía de luz polarizada sobre fragmentos de yeserías de
la Alhambra identifican **lazurita** (lapislázuli), **bermellón** (cinabrio) y
**negro carbón**. El azul original era lapislázuli natural; el sintético
corresponde a las restauraciones de finales del XIX. El rojo, de minio (óxido
de plomo) o cinabrio.

**Lo que NO está establecido**: el reparto en esta cúpula concreta. Qué celda
era azul, cuál roja, dónde había oro. No se ha localizado ningún estudio
específico de la policromía de los mocárabes de las Dos Hermanas.

## Clasificación de los restos

Cada punto del dominio fundamental se clasifica por voto sobre sus 16 copias,
con vecindad de ±2 px para absorber el desajuste que introduce la deformación.
Umbral: al menos 2 copias coincidentes.

Dos colores se excluyeron **a priori** por indistinguibles:

- **El oro** cae en tono 40–60°, exactamente donde están la suciedad y el yeso
  envejecido.
- **El negro carbón** se confunde con la sombra de las cavidades.

Resultado sobre el dominio fundamental: yeso 68.0 %, rojo 16.1 %, verde 13.6 %,
azul 2.3 %.

## La prueba: periodicidad angular sin plegar

Un mapa plegado es simétrico por construcción y no prueba nada. La prueba se
hace sobre la imagen **sin plegar**: si una clase es pigmento del diseño, su
distribución angular tendrá energía concentrada en múltiplos de 8; si es
suciedad, se repartirá al azar.

| clase | energía en múltiplos de 8 | contra el azar (12.5 %) |
|---|---|---|
| **verde** | **28.6 %** | **2.3×** |
| yeso *(línea base)* | 19.5 % | 1.6× |
| azul | 17.3 % | 1.4× |
| rojo | 16.9 % | 1.35× |

**El verde se sostiene.** Sus armónicos dominantes son k=16, 8, 24, 32 y 40 —
todos múltiplos de 8. Eso no lo produce la suciedad.

**El rojo no se sostiene.** Queda *por debajo* de la línea base del propio yeso:
no es distinguible de la estructura general de la superficie. Era la clase más
extensa después del yeso y resulta ser la menos fiable. En el mapa aparecía en
regueros radiales siguiendo las aristas del relieve, que es precisamente donde
se acumulan los óxidos de hierro y la suciedad. **No se pinta.**

**El azul queda en duda.** Apenas por encima del azar, pero su distribución
espacial es visiblemente regular: un anillo de posiciones periódicas a radio
medio. Se pinta, marcado como evidencia débil.

## Estado

`renders/inauguracion_evidencia.png` — yeso blanco de obra nueva, verde y azul
solo donde la evidencia los sostiene. Es una **recoloración de la ortoimagen**,
usando su propio relieve como sombreado: todavía no una reconstrucción desde la
geometría.

Sale a manchas porque la supervivencia del pigmento es irregular. Limpiarlo
exige el teselado: una vez se sepa qué celda es cada mancha, la afirmación pasa
de «estos píxeles eran verdes» a «esta celda era verde, con N de 16 copias
conservando traza».

## TODO

- El teselado del dominio fundamental. Es el trabajo pendiente y el que
  convierte esto en una reconstrucción por celdas.
- El oro: si lo había en esta cúpula y dónde. Hay oro y plata documentados en
  yeserías nazaríes —letras doradas sobre fondo azul lapislázuli en el Mexuar,
  1362— pero nada específico de aquí.
- El rojo: descartado con **esta** imagen. Una fuente con análisis de pigmento
  in situ lo resolvería; la ortofotografía no.
