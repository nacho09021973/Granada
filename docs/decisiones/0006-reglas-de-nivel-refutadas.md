# 0006 — Tres reglas de nivel refutadas, y lo que la refutación deja en pie

**Estado:** aceptada — 2026-08-25

## Contexto

Con las caras y las 227 vecindades ya identificadas (decisión 0005), el signo
de cada paso seguía sin evidencia. Antes de salir a buscar una fuente convenía
comprobar algo barato: **de las reglas que uno propondría de memoria, ¿cuáles
son siquiera posibles sobre esta planta?**

No se trata de asignar niveles. Se trata de intentar refutarlos. Alrededor de
cualquier ciclo del grafo de vecindades los saltos firmados tienen que sumar
cero; si una regla no lo cumple, es imposible, y el ciclo que la rompe queda
como testigo con nombre y apellido.

## Decisión de método

1. **El contorno exterior no entra en el dual.** Es un solo nodo artificial que
   uniría las 16 caras del borde y crearía ciclos que no existen en la cúpula.
   El dual real son **105 caras, 211 vecindades y 107 ciclos independientes**.
2. **Toda regla se juzga con dos controles positivos.** Uno trivial (todas las
   medinas son descansos) y uno no trivial y consistente por construcción (el
   modelo de coronas cuantizado al paso de hilada medido de 20 cm). Si esos dos
   no pasaran, el roto sería el test, no la planta.
3. **La pregunta de existencia va al núcleo.** `admite_salto_unitario` en
   `granada/niveles.py` responde si existe *alguna* nivelación en la que toda
   vecindad salve exactamente un nivel, y devuelve un ciclo impar como testigo
   cuando no.

## Resultado

| regla | veredicto |
|---|---|
| R1 · toda medina separa dos niveles consecutivos, en el sentido que sea | **imposible** |
| R2 · se sube un nivel al cruzar cada medina hacia el centro | **imposible**, 67 de 107 ciclos rotos |
| R3 · las medinas de lado suben, las diagonales descansan | **imposible**, 67 de 107 ciclos rotos |
| C1 · control: ninguna medina cambia de nivel | consistente |
| C2 · control: coronas cuantizadas al paso de 20 cm | consistente |

Los dos controles pasan, así que el test no rechaza por costumbre. C2 además
recuerda que **consistente no es correcto**: el modelo de coronas cierra todos
los ciclos y sigue estando rechazado desde la decisión 0003 por contradecir el
teselado documentado. La consistencia es una criba, no un aval.

## Lo que la refutación deja en pie: el teorema del triángulo

R1 no cae por casualidad. Cae porque el grafo de vecindades **no es bipartito**,
y eso tiene una lectura exacta:

> En tres teselas mutuamente vecinas, los tres saltos suman cero al recorrer el
> triángulo. Si los tres valieran ±1, la suma sería impar —±1 o ±3— y nunca
> cerraría. Por tanto **al menos una de las tres medinas es un descanso o salva
> dos niveles**.

La planta contiene **54 triángulos** de ese tipo. Y lo que la tesis documenta
por su cuenta, sin pasar por aquí, es exactamente esas dos figuras: los
**descansos** de la sección 3.2.5 y las piezas **A3 y D3**, que salvan dos
niveles.

Es un resultado positivo obtenido de pura topología, sin fotometría, sin radio
y sin suponer nada sobre la altura: **el dibujo de la planta exige por sí solo
piezas que no salvan un nivel exacto.** No dice cuáles, ni dónde, ni en qué
sentido.

## Control de robustez

Los triángulos se apoyan en las medinas cortas: su longitud compartida mediana
es de **20,7 px** frente a **31,4 px** del conjunto. Eso obliga a comprobar si
la refutación sobrevive al descartar las medinas más cortas, que son las que
peor resiste la digitalización.

| se descartan las vecindades de menos de | vecindades | triángulos | ¿admite salto unitario? | ciclos rotos por R2 |
|---:|---:|---:|:--:|---:|
| — | 211 | 54 | no | 67 |
| 10 px | 209 | 50 | no | 67 |
| 15 px | 204 | 44 | no | 62 |
| 20 px | 159 | 16 | no | 32 |
| 30 px | 112 | 16 | no | 18 |
| 40 px | 42 | 0 | sí | 0 |

Aguanta hasta 30 px, por encima de la mediana del propio dato. Los **16
triángulos** que sobreviven son el mismo motivo repetido en 16 posiciones
alrededor de la cúpula —caras de ≈0,21, ≈0,22 y ≈0,87 m²— con medinas
compartidas de 32 a 38 px.

La fila de 40 px **no apoya nada**: ahí solo quedan 42 de 211 vecindades, el
dual se deshace en trozos y el test pierde la potencia para refutar. Se incluye
para que se vea dónde deja de decir algo.

## Cuántas de las 16 instancias son independientes

La red se digitalizó solo en su mitad superior; la inferior se generó por
reflexión sobre `y = 273,5 px` (decisión 0004, punto 2). La réplica impuesta
por construcción es por tanto **de orden 2**, no de orden 16: la simetría de
orden 16 nunca entró en el dato, así que la repetición del motivo no es
construida. Cuánta de ella es observación independiente es otra cuestión, y
hay que contarla.

Reflejando el centroide de cada triángulo sobre el eje y buscando el más
próximo, el emparejamiento resulta ser una **involución perfecta**: 16 de 16
emparejados, **8 pares**, ninguno auto-simétrico, desajuste máximo 3,91 px.

### Por qué 6 arriba y 7 abajo no es una asimetría

El reparto crudo de los centroides respecto del eje es 6 triángulos
enteramente arriba, 7 enteramente abajo y 3 a caballo. Un lector que espere
que el espejo dé tantos arriba como abajo verá ahí una asimetría. No la hay, y
la cuenta cierra exacta:

- los **6 pares interiores** aportan 6 arriba y 6 abajo;
- los **4 triángulos de costura** aportan los 3 «a caballo» más un cuarto cuyo
  centroide cae al lado de abajo del umbral por poco.

6 + 6 + 4 = 16, y 6 + 1 = 7 abajo. La aparente asimetría es un centroide de
costura clasificado por un umbral, no una propiedad del dibujo.

### Dos números, y el estricto es seis

Clasificando cada cara por los **vértices** de su polígono, no por su
centroide, los 16 triángulos se reparten así:

| clase | triángulos |
|---|---:|
| interior, con las tres caras digitalizadas del ráster | **6** |
| interior, con las tres caras reflejadas | 6 |
| de costura, con caras que cruzan el eje | 4 |

Los cuatro de costura contienen **dos caras que cruzan el eje** cada uno
—`c047` y `c053` en un par, `c050` y `c054` en el otro—. Una cara que cruza el
eje tiene parte de su contorno generada por reflexión, y la vecindad que cierra
el triángulo es producto del pegado. Su existencia depende de que el pegado sea
correcto, que es justamente la hipótesis que la red no puede avalar sin
circularidad.

Por tanto:

- **N = 6**, instancias del interior con las tres caras digitalizadas del
  ráster. Es el número que descarta el artefacto de esqueletizado **sin
  condicionantes**, y el que se fija.
- **N = 8** solo si se acepta el pegado como dado. Los dos pares de costura
  **corroboran, no observan**.

Seis instancias independientes bastan de sobra: el ruido de digitalización no
se alinea a 45°. La refutación de R1, R2 y R3 no depende del número en ningún
caso — se sostiene sobre la topología del dibujo entero.

### Nota sobre el desajuste del emparejamiento

Hasta 3,91 px no indica asimetría del dibujo. Los centroides del dato son
**medias de vértices**, y tres de cada seis caras emparejadas tienen distinto
número de vértices —9 contra 8, 4 contra 5— por la simplificación RDP. El
centroide de vértices no es invariante bajo remuestreo del contorno; el de área
sí. Las áreas de las caras emparejadas concuerdan a 0,6–58 cm² sobre
2 100–8 600 cm², menos del 3 % de la menor.

## Techo de afirmación

Lo refutado son **esas tres reglas sobre esta planta digitalizada**, no
cualquier regla ni la cúpula real. Que R2 sea imposible no dice que el nivel no
crezca hacia el centro en promedio: dice que no lo hace de un nivel por medina.

Y el techo está un nivel más arriba de lo estadístico, donde ya lo puso la
decisión 0004: **los 323 nudos no son la cúpula, son el dibujo de Ferrer.** Si
el autor trazó su propuesta replicando un sector en CAD —que es lo habitual—,
las 16 apariciones del motivo son **una sola decisión del dibujante**, y
ninguna manipulación del ráster puede distinguir ese caso del de 16
observaciones. Las ocho instancias independientes descartan el artefacto de
*digitalización*; no descartan la réplica en *origen*.

Eso no invalida la refutación: el argumento de paridad se sostiene sobre la
topología del dibujo, y el dibujo es la fuente declarada. Pero fija dónde
acaba. **R2 queda refutada sobre la propuesta publicada de Ferrer
Pérez-Blanco, no sobre la cúpula de la Sala de las Dos Hermanas.** Es la misma
frase que ya lleva la decisión 0004, y la refutación hereda esa y no otra más
fuerte.

El teorema del triángulo es una implicación, no una medición: *si* la planta
digitalizada refleja las adyacencias reales, *entonces* hay descansos o piezas
de dos niveles. Depende de que la figura 128 y su digitalización acierten con
quién toca con quién.

Y sobre todo: nada de esto firma un solo salto.
`BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` continúa. Lo que se ha ganado es que
tres atajos quedan cerrados por escrito y con testigo, en vez de quedar
cerrados por prudencia.

## Reproducción

- `scripts/probar_reglas_de_nivel.py` → `datos/reglas_de_nivel.json`
- Núcleo: `granada/niveles.py`, función `admite_salto_unitario`
- Pruebas: `tests/test_reglas_de_nivel.py` y las nuevas de `tests/test_niveles.py`
