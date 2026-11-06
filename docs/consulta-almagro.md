# Consulta a Antonio Almagro Gorbea

Redactada el 2026-08-25. **Enviada el 2026-08-26**, a dos destinatarios:
Antonio Almagro Gorbea e Ignacio Ferrer Pérez-Blanco. A la espera de respuesta.

Destinatario principal: Antonio Almagro Gorbea, autor de la lámina AA-415_23.
Profesor de Investigación emérito del CSIC (Escuela de Estudios Árabes,
Granada) y Académico de la RABASF.

Segundo destinatario: **Ignacio Ferrer Pérez-Blanco**, autor de la tesis de
2023 de la que sale la planta que usa este repositorio. No estaba previsto en
esta redacción, y conviene decir por qué es el interlocutor adecuado para dos
de las cuatro preguntas:

- **La pregunta 2 es suya antes que de nadie.** Pregunta por la sección 3.3.2 y
  la figura 128 de su propia tesis: por qué la representación con flechas de
  ascenso no está aplicada a Dos Hermanas. Nadie más puede contestar a eso.
- **Pone a prueba la conjetura de la entrada 14 de `fuentes.md`.** Ese informe
  supone que Ferrer omitió las flechas porque las deformaciones documentadas
  por UGR/US quiebran el salto ideal. Es una inferencia sin apoyo. Su respuesta la
  confirma o la tumba, y en cualquiera de los dos casos deja de ser conjetura.

La pregunta 1 —los datos de origen del levantamiento— sigue siendo de Almagro y
solo de Almagro.

Va a investigadores con obra propia sobre esto: la nota es corta, dice qué se
ha hecho ya para no pedirles lo que sus trabajos ya dan, y hace cuatro
preguntas que se pueden contestar con un sí, un no o un puntero.

El texto que sigue es el redactado para Almagro, y queda aquí como registro de
lo enviado. **A Ferrer se le envió una versión adaptada, cuyo texto no consta
en este repositorio.** Conviene pegarlo aquí abajo cuando se pueda: si
contesta, hay que poder saber qué se le preguntó exactamente y con qué
palabras, y no reconstruirlo de memoria meses después.

---

**Asunto:** AA-415_23 (Sala de las Dos Hermanas): niveles de las adarajas y
datos de origen del levantamiento

Estimado profesor Almagro Gorbea:

Le escribo por un trabajo de reconstrucción geométrica de la cúpula de mocárabes
de la Sala de las Dos Hermanas. Uso su lámina **AA-415_23** (RABASF, *Sección y
techo sala de las Dos Hermanas*, enero de 2021) como fuente de medida, y la
propuesta de planta de la tesis de Ignacio Ferrer Pérez-Blanco (2023) como
topología del teselado.

El trabajo está detenido en un punto muy concreto. De la planta se obtienen
**105 teselas y 211 vecindades entre ellas**, y de la bibliografía se obtiene el
tamaño del salto entre niveles —8 unidades, que Saseta Velázquez (2016) da
explícitamente y que coincide con el 8P de la plantilla de doble perfil de
Ferrer—. Lo que no aparece en ninguna fuente es el **signo**: si al cruzar cada
medina se asciende, se descansa o se desciende. Un vaciado de Dialnet, TESEO,
Digibug, RiuNet, el APAG, la RABASF y el IAPH no ha dado ninguna tabla pública
que asocie cada pieza con una cota.

De su lámina sí he podido medir bastante, y por eso no le pregunto por ello: la
escala gráfica da 236,2 px/m a 150 dpi, coincidente al 0,01 % con el 1/25
nominal; la sección da 23 hiladas con paso de unos 20 cm y un cono a 38° de la
vertical; y las fronteras radiales de la planta de Ferrer casan en orden con los
escalones de la silueta de su sección, con un residuo de un centímetro. Pero una
sección es un corte: da un perfil, no el nivel de cada pieza en planta.

Le agradecería mucho, si tiene un momento, cualquier indicación sobre estos
cuatro puntos:

1. **¿Conserva los datos de origen del levantamiento?** El PDF publicado lleva
   capas vectoriales (AutoCAD 2010) pero ninguna cota escrita: hay veinte
   palabras de texto en todo el A0. Si existe todavía el modelo, la nube de
   puntos o el bloque fotogramétrico, la cota de cada adaraja se leería
   directamente y el problema quedaría resuelto de raíz.

2. **¿Conoce alguna planta de esta cúpula con líneas de nivel o cotas por
   pieza?** —suya o de otro autor—. La sección 3.3.2 de la tesis de Ferrer
   propone una representación con flechas de ascenso, pero la figura 128, que
   es la de Dos Hermanas, no la lleva aplicada.

3. **Orientación de la lámina.** ¿Qué lado de la ortoimagen cenital del techo
   corresponde a la fachada principal? Y la sección norte-sur, ¿corta por el
   eje perpendicular a las paredes o por la diagonal de la sala? La cúpula es
   simétrica de orden ocho, así que la propia bóveda no permite deducirlo, y la
   ortoimagen está recortada en el arranque, sin llegar a los vanos del tambor.

4. **Condiciones de uso.** He leído el plano para verificar mediciones, que
   entiendo que es uso legítimo. Derivar geometría de él para publicarla en un
   repositorio de código abierto es otra cosa, y prefiero preguntar antes que
   después: ¿qué permiso haría falta, suyo o de la Academia?

Cualquiera de las cuatro respuestas, incluso si es que no, me ahorra semanas de
búsqueda. Quedo a su disposición para enviarle lo que llevo hecho, y por
supuesto la lámina quedará citada como fuente.

Con mi agradecimiento y un cordial saludo,

Ignacio

---

## Seguimiento

Enviada el 2026-08-26. Qué hacer con lo que vuelva:

- **Registrar la respuesta en `docs/fuentes.md` como entrada nueva, con fecha,
  sea cual sea.** Una negativa también es un dato, y es justamente el que
  sostiene que `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` no es un fallo de
  búsqueda nuestro. Si vienen dos respuestas, son dos entradas.
- La pregunta 1 es la única que puede desbloquear el proyecto de golpe. Las
  otras tres cierran cabos: la 2 es la vía documental, la 3 resuelve la
  orientación de la decisión 0007 de la rama `cotas-z-y-falsacion` (no fusionada) y la 4 hay que tenerla antes de derivar
  geometría, no después (cautela 4).
- Si a la 1 contesta que no conserva nada, el bloqueo pasa a ser definitivo por
  esa vía y hay que ir a la 2, o a las 104 adarajas del PMAA pidiendo permiso a
  Martínez Sevilla (entrada 10 de `fuentes.md`, licencia CC BY-NC-ND).
- Si Ferrer contesta a la 2, su respuesta decide además la conjetura de la
  entrada 14 —que omitió las flechas por las deformaciones—, que hoy no tiene
  ningún apoyo. Confirmada o tumbada, deja de ser conjetura.
- **Hasta que llegue algo, el estado del proyecto no se mueve.** Haber
  preguntado no es haber medido.
- **La pregunta 4 se ha afinado sola (2026-08-26).** Al leer el campo Derechos
  de la ficha se ve que el uso para investigación **ya está autorizado**, así
  que lo que hay que preguntarle no es «¿qué permiso haría falta?» sino algo
  mucho más concreto: **¿autoriza el uso comercial**, que su ficha se reserva,
  para que la geometría derivada pueda salir bajo MIT? Si contesta que no, la
  salida es separar licencias —código MIT, datos derivados CC BY-NC— y no hace
  falta molestarle más. La pregunta enviada sigue siendo válida; solo que ahora
  se sabe cuál de sus respuestas importa.
- **Hueco de registro pendiente**: falta el texto de la versión adaptada que
  fue a Ferrer. Sin él, una respuesta suya llegaría sin la pregunta al lado.
  Es lo único de este envío que no está documentado.

Nota de método que ya se aplicó al enviar: no se adjuntó el PDF de la lámina.
Es suyo.
