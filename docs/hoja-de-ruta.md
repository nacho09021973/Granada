# Hoja de ruta si Ferrer no contesta

Escrita el 2026-08-29. Supuesto de partida: la respuesta a la petición de la
entrada 12 de `fuentes.md` **puede no llegar**, y aun así hay que seguir. A
partir de cierto punto eso obliga a decidir cosas que ninguna fuente decide.

Este documento existe para que esas decisiones se tomen **a la vista**, no por
acumulación de pequeños atajos.

---

## La regla, antes que los pasos

Una decisión nuestra no es lo mismo que un dato. Para que sigan sin confundirse,
toda elección sin fuente cumple las cuatro:

1. **Decisión escrita** en `docs/decisiones/`, con lo que se elige y lo que se
   descarta.
2. **`procedencia` en el artefacto**, cara a cara o pieza a pieza. Nunca un
   valor inventado dentro de un campo que en otras filas es medido.
3. **Interruptor en el código**: una bandera con nombre, y el comportamiento
   defendible por defecto. Si hay que enseñar la versión especulativa, se pide
   explícitamente.
4. **Condición de muerte**: qué evidencia concreta la tumbaría. Sin eso no es
   una hipótesis, es una preferencia.

Y una regla de higiene: **si Ferrer contesta más tarde, la capa inventada se
revisa entera**, no se conserva porque ya estaba.

## El umbral que no hay que cruzar sin renombrar el proyecto

Hoy el modelo tiene **105 piezas**, todas correspondientes a caras de una planta
publicada. El paso 3 de abajo las llevaría a unas 500, y **cuatro de cada cinco
no vendrían de ninguna fuente**.

Ese es el umbral. Cruzarlo no está prohibido, pero al cruzarlo el nombre honesto
deja de ser «reconstrucción aproximada de la cúpula de las Dos Hermanas» y pasa
a ser «cúpula compuesta en el sistema de las Dos Hermanas». Es un cambio de
afirmación, no de redacción: hay que tocar el README y decirlo.

## Plazo

Segundo aviso a Ferrer si no hay respuesta el **2026-09-19**. A partir de ahí se
activa el paso 1, que hasta entonces no merece la pena.

---

## Paso 1 — Leer los sentidos de ascenso sobre el vídeo

**Se desbloquea con su silencio.** Hoy no se hace porque trabajar sobre 15,6 s a
480×856 comprimidos es absurdo teniendo el original a una petición. Si el
original no llega, el vídeo deja de ser un desperdicio y pasa a ser lo que hay.

- **Qué falta**: el signo de cada una de las 227 vecindades. Hoy están inferidas
  por distancia de grafo (decisión 0007), que es topología, no observación.
- **Qué se hace**: extraer fotogramas a 2 fps, registrarlos contra el cuarto de
  planta, y anotar las orientaciones **legibles** con su fotograma, su región y
  el criterio de lectura.
- **No es invención**, es evidencia mala: se etiqueta «observado sobre una
  reconstrucción decimonónica que rellena lagunas por diseño, fotograma N»,
  nunca «observado sobre la cúpula». La entrada 13 de `fuentes.md` documenta que
  las maquetas de Contreras **no son copias exactas**: rellenan huecos a
  propósito para dar «una visión más completa».
- **Se propaga por rotación C8, no por espejo.** La simetría rotacional está
  medida por Fourier sobre la ortoimagen, independiente de la red, así que
  usarla no es circular. La especular la entrada 7 dice expresamente que **no se
  ha analizado**. Las órbitas están calculadas y controladas en
  `datos/orbitas_c8.json` (decisión 0012): **14 caras y 27 vecindades** cubren
  216 de las 227.
- **La propagación no multiplica el N.** Observadas 27 vecindades son 27, no
  216. Es la segunda mitad de la cautela 5, y esa sigue entera.
- **Lo sustituye**: la malla de Ferrer, que permitiría leerlas con geometría en
  vez de a ojo.

## Paso 2 — Asignar plantilla mayor o menor a cada cara — **hecho**

Decisión 0013, el 2026-08-29. **Bandas 0, 1 y 2 con el perfil menor** —88
caras—, **bandas 3, 4 y 5 con el mayor** —17—, y la frontera de módulo entre la
banda 2 y la 3.

- **Qué faltaba**: la tesis documenta dos perfiles y el paralelismo entre
  vecinas obliga a que existan fronteras donde se rompe (decisión 0010).
  Ninguna fuente dice cuáles.
- **Cómo se eligió**: seis criterios en orden, con lo documentado por delante
  de lo nuestro. El que más pesa es romper el paralelismo en las menos
  vecindades posibles, que es lo único que aquí viene de una observación de la
  fuente; el empate lo deshace dónde cambia la subdivisión angular de la planta
  —de 40 caras por banda a 8—, y la constancia de la junta, que es argumento
  nuestro, solo decide de qué lado va cada plantilla.
- **Una corrección a lo que decía aquí**: la alternancia banda ancha / banda
  estrecha que este documento proponía es justo la que **más** rompe el
  paralelismo —115 vecindades de 211— aunque sea la que mejor iguala las
  juntas. Queda en el catálogo de la decisión 0013 como rival descartado.
- **Es una hipótesis comprobable**: predice que la frontera de módulo cae entre
  las bandas 2 y 3. Si Ferrer la sitúa en otro sitio, se cae limpiamente.
- **Coste si es falsa**: bajo. Mueve la profundidad de la pieza entre 7/8 y
  15/16 del salto, un 7,1 %, y no toca ninguna cota ni la topología.
- **El interruptor**: `--plantilla por-banda` es el defecto y `--plantilla
  mayor` reproduce el modelo de la decisión 0010. Que el defecto sea el
  repartido es una lectura discutible de la regla 3, argumentada en la 0013.

## Paso 3 — Bajar de banda a hilada

**Es la invención grande, y va detrás de una bandera.**

- **Qué falta**: la cara mediana abarca 5,2 hiladas. La figura 128 no subdivide
  las 80 caras sin figura, así que no hay planta más fina de esta cúpula.
- **Qué haríamos**: subdividir cada cara radialmente en tantos escalones como
  hiladas abarca, al paso horizontal medido.
- **Roza lo refutado.** Subdividir por radio dentro de una cara es la
  estratificación por coronas a pequeña escala. La salvaguarda es que ocurre
  **dentro** de una cara: no reasigna vecindades ni toca el orden topológico
  entre caras, que es lo que la decisión 0006 refutó. Aun así, no se puede
  presentar como pieza real.
- **Coste si es falso**: alto, y del tipo peor. El relieve se vería mucho mejor
  y eso hace que parezca más preciso de lo que es.
- **Cómo se entrega**: dos salidas, nunca una. `cupula_bandas.obj`, defendible y
  por defecto, y `cupula_subdividida.obj`, ilustrativa y rotulada como tal. Y
  antes de activarla por defecto, cruzar el umbral de arriba con su cambio de
  nombre.

## Paso 4 — Policromía — **base hecha**

Aquí hay menos que inventar de lo que parece, porque **el objetivo ya lo
decide**: «como el día de su inauguración, yeso blanco de obra nueva y
policromía original».

- **Modo por defecto: yeso blanco — hecho.** No exige asignar ni un color, es
  literalmente lo que dice el objetivo, y es la mitad de la afirmación que sí
  está sostenida. El visor separa este acabado de la capa analítica por niveles
  y rotula cualquier tono del usuario como visualización sin atribución
  histórica.
- **Capa opcional A, paleta medida**: `docs/policromia.md` sostiene el verde y
  descarta el rojo sobre la ortoimagen del plano. Aplicarla exige decidir qué
  color va en qué pieza, y eso no lo dice nadie: iría por tipo de pieza, con
  `procedencia` en cada una.
- **Capa opcional B, lectura de Contreras**: su maqueta trae rojo y dorado en
  posiciones repetidas. Es una lectura del siglo XIX, fechada y atribuible —
  hipótesis, nunca medida, y jamás mezclada con la capa A.
- **El oro y el negro no entran.** Sin fuente de pigmento in situ el oro es
  indistinguible de la suciedad, y el negro de la sombra.

## Paso 5 — Terminar la página interactiva — **hecho**

**Cero invención, y es el destino acordado.** Están la cúpula girable, la ficha
por cara, los controles de acabado y color y el selector de orden. El selector
no deforma la malla histórica: abre una vista sintética propia para los órdenes
16, 20 y 24, alimentada por `datos/ordenes_sinteticos.json`. La interfaz los
presenta como familias de 8, 10 y 12 sectores, con vista general y desde abajo,
procedencia y límites escritos para una audiencia histórica. Cada celda
conserva sus coeficientes exactos en Z[ζₘ]; las coordenadas decimales se
declaran como embedding numérico exclusivo para visualización.

## Paso 6 — La afirmación (A), que nunca dependió de nadie — **en curso**

El generador sintético de orden arbitrario es **matemático**: se sostiene o se
refuta con una demostración, no con una fuente. Ninguna de las esperas de este
documento le afecta. Si la vía histórica se cierra del todo, esta sigue abierta
y es donde el proyecto puede crecer sin deberle nada a nadie. La primera
composición completa ya está: tres cúpulas comparativas de cinco coronas y 8,
10 o 12 sectores. Su volumen es una decisión contemporánea explícita (0014), no
una reconstrucción. El siguiente trabajo es sustituir esa regla expositiva por
una regla tipológica cuando exista una composición histórica documentada que
el proyecto decida modelar.

---

## Lo que no se inventa, pase lo que pase

- **No firmar vecindades por coherencia entre vecinas.** Ferrer fue explícito:
  la coherencia **valida** observaciones, no rellena las que faltan.
- **No usar la simetría impuesta como evidencia.** Ni la mitad espejada de la
  red, ni el montaje cuádruple de `Ferrer_5`.
- **No reabrir los tres atajos refutados** de la decisión 0006. Cada uno tiene
  su ciclo testigo.
- **No presentar nada de esto como observado sobre la cúpula.** Lo que se
  observe será sobre una maqueta del siglo XIX o sobre un dibujo.
- **No derivar geometría publicable** del material de Ferrer sin su permiso
  expreso, con el repositorio en MIT.

## Si contesta

Se revisa la capa inventada entera antes de seguir, empezando por lo que su
respuesta toque directamente: el paralelismo (paso 2), los sentidos de ascenso
(paso 1) y las condiciones de uso de su modelo. Lo que sobreviva, sobrevive con
su decisión reescrita; lo que no, se retira como se retiró el código de la
decisión 0011.
