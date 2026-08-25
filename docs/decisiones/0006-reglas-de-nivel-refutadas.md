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

## Techo de afirmación

Lo refutado son **esas tres reglas sobre esta planta digitalizada**, no
cualquier regla ni la cúpula real. Que R2 sea imposible no dice que el nivel no
crezca hacia el centro en promedio: dice que no lo hace de un nivel por medina.

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
