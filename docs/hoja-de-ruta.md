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

## Paso 2 — Asignar plantilla mayor o menor a cada cara

- **Qué falta**: la tesis documenta dos perfiles y el paralelismo entre vecinas
  obliga a que existan fronteras donde se rompe (decisión 0010). Ninguna fuente
  dice cuáles.
- **Qué decidimos**: una plantilla por banda, cambiando en las fronteras de
  banda. Tiene apoyo en los propios datos: las bandas 0, 1 y 3 abarcan 5–7
  hiladas y las bandas 2 y 4 abarcan 1,3–1,5. Hay un cambio de escala real ahí,
  y es el candidato natural a frontera de módulo.
- **Es una hipótesis comprobable**: predice que las fronteras de módulo
  coinciden con las de banda. Si Ferrer dice que están en otro sitio, se cae
  limpiamente.
- **Coste si es falsa**: bajo. Mueve la profundidad de la pieza entre 7/8 y
  15/16 del salto, un 6 %.
- **Hacerlo antes que el paso 3**: es barato, y si el 3 nunca llega, el modelo
  se queda con los dos perfiles usados, que es más fiel que con uno.

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

## Paso 4 — Policromía

Aquí hay menos que inventar de lo que parece, porque **el objetivo ya lo
decide**: «como el día de su inauguración, yeso blanco de obra nueva y
policromía original».

- **Modo por defecto: yeso blanco.** No exige asignar ni un color, es
  literalmente lo que dice el objetivo, y es la mitad de la afirmación que sí
  está sostenida.
- **Capa opcional A, paleta medida**: `docs/paleta.md` sostiene el verde y
  descarta el rojo sobre la ortoimagen del plano. Aplicarla exige decidir qué
  color va en qué pieza, y eso no lo dice nadie: iría por tipo de pieza, con
  `procedencia` en cada una.
- **Capa opcional B, lectura de Contreras**: su maqueta trae rojo y dorado en
  posiciones repetidas. Es una lectura del siglo XIX, fechada y atribuible —
  hipótesis, nunca medida, y jamás mezclada con la capa A.
- **El oro y el negro no entran.** Sin fuente de pigmento in situ el oro es
  indistinguible de la suciedad, y el negro de la sombra.

## Paso 5 — Terminar la página interactiva

**Cero invención, y es el destino acordado.** Falta el selector de orden y los
controles de color; la cúpula girable y la ficha por cara ya están. Si todo lo
demás se atasca, esto se puede terminar igual.

## Paso 6 — La afirmación (A), que nunca dependió de nadie

El generador sintético de orden arbitrario es **matemático**: se sostiene o se
refuta con una demostración, no con una fuente. Ninguna de las esperas de este
documento le afecta. Si la vía histórica se cierra del todo, esta sigue abierta
y es donde el proyecto puede crecer sin deberle nada a nadie.

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
