# 0032 — Geometría visible de Dos Hermanas

Revisión local del 2026-11-19 sobre la malla de las previas a 1400 px. El resultado más visible es la organización del centro. El defecto técnico mejor localizado es el asiento de los cupulines.

## Qué se comparó

La [lámina de tres detalles](../../renders/previas/auditoria_geometria_detalles.png) enfrenta la ortoimagen de Antonio Almagro con una vista ortográfica inferior del OBJ. Cada columna abarca la misma región aproximada y el mismo ancho supuesto en ambas filas. Se usa el centro (2048, 2035) y la escala de planta de 472,2 px/m de la medición de cupulines. La correspondencia se establece por región, sin ajuste punto a punto ni identificación individual de las piezas. La lámina con los recortes de la RABASF queda en las previas locales.

Se inspeccionaron la planta y la sección en AA-415_23.pdf p. 1, sus dos imágenes nativas, la fotografía casi cenital de José Luis Filpo Cabana y la vista cúpula de Cycles. La ortoimagen permite comparar trazados en planta y la sección aporta escala vertical. La fotografía permite comprobar cómo se lee el volumen desde la sala. La figura 5 de Gámiz Gordo y Ferrer Pérez-Blanco (2019, PDF p. 15, p. impresa 71) documenta prismas y agrupaciones. La asignación de cada tipo a un punto particular de esta bóveda sigue abierta.

## Hallazgos por zona

1. **Clave y primer anillo.** La ortoimagen muestra un pequeño motivo central inscrito en un remate estrellado, rodeado de piezas con caras rectas y cambios de dirección. En el mismo ancho de 1,65 m del modelo domina una superficie circular continua. En el OBJ la primera superficie visible sobre el eje pertenece a `cupulilla_25`. Tiene la misma construcción que los cierres menores, con base armónica y un casquete cuyo alto depende de la distancia al borde. La altura máxima visible es 5,481 m sobre el arranque y coincide con el máximo de los vértices a menos de 0,1 mm. El objetivo del modelo es 4,67 m. La relectura de la sección a tres umbrales da 4,701, 4,908 y 4,910 m. Con esa definición de arranque el exceso es de unos **57–78 cm**. El intervalo expresa sensibilidad al umbral fotométrico. No es una tolerancia constructiva. Reducir la altura general de las 65 cupulillas afectaría también a los cierres de otras celdas y seguiría dejando un centro liso.

2. **Hiladas intermedias.** En la región examinada, la ortoimagen muestra caras planas y entrantes que cambian de dirección en encuentros angulares. En el relieve del modelo aparecen tiras largas que se curvan juntas y puntas muy estrechas entre ellas. El generador dispone de siete prismas, pero el montaje distribuye A1/A2/A3 y C1/C2 con la secuencia repetida A, A, C. Cada pareja de filas comparte familia y las piezas se adaptan al frente suavizado. Esto limita las agrupaciones que puede producir el algoritmo. La ortoimagen justifica ensayar encuentros rectos y oblicuos en esta zona. Por sí sola no identifica cada prisma ni determina su altura.

   Se recalcularon las bandas con A=3, raíz y borde octogonal. En los anillos seleccionados por el diagnóstico 0026, la peor mediana de giro por paso de pieza es 23,03° en la fila 34, por debajo de su criterio de 25°. Se cuentan 6.208 triángulos de banda con área en planta de signo invertido entre 3.261.056. Son elementos de la parametrización antes de montar las piezas. Su número carece de equivalencia directa con solapes entre sólidos. El criterio de giro puede cumplirse mientras el recorte sigue mostrando una agrupación distinta.

3. **Cupulines exteriores.** El OBJ contiene 16 grupos de cupulín. La ortoimagen permite reconocer el remate estrellado y el marco facetado alrededor del hueco. En el modelo se distingue una porción del pozo y una abertura negra junto a las hiladas. El ensamblaje descarta piezas enteras según su centroide y superpone un marco. Además, en `cupulin_estrellado` la base del pozo se eleva hasta H evaluado **antes** del desplazamiento lateral que introduce el eje a 30°. En los 96 puntos de cada una de las 16 bocas, la mediana de |z−H(x,y)| en coordenadas finales es **51,1 cm**, con extremos firmados de −22,2 y +110,4 cm. H es el campo del modelo. Estos valores miden una inconsistencia interna. La distancia real a cada sólido vecino requiere otro cálculo.

   Como contraste, al deshacer el desplazamiento lateral, la altura exportada coincide con la evaluación que usa el código dentro de 0,001 mm. Se ensayó intersectar cada generatriz con el campo en sus coordenadas finales. En el intervalo local de −3 a +7 catetos, muestreado cada 0,02, aparece un cambio de signo por punto. La bisección de esos intervalos deja un residuo vertical inferior a 0,001 mm en los 1.536 puntos. Es una comprobación numérica del borde. Queda por rehacer también el marco, la transición a las piezas y el recorte de las que atraviesan la boca.

4. **Cobertura de la bóveda.** Se lanzaron rayos verticales desde debajo de los triángulos del OBJ en un disco de 3,35 m de radio. De 199.848 rayos, 10.170 atraviesan la bóveda sin impacto, **5,09 %**, unos **1,79 m²** de proyección horizontal. Al duplicar el paso de muestreo se obtienen 1,80 m². Un cálculo baricéntrico independiente coincide en los 226 rayos de control, incluidos once sin impacto. Aquí se incluyen las piezas, la clave, los cierres y los 16 pozos con techo. La cifra se refiere a la proyección del OBJ previo a los modificadores de Blender. Una franja oscura en una foto también puede ser sombra, y una cámara oblicua ve otras aberturas. El conteo por bandas de 0031 respondía a otra pregunta.

## Orden de corrección

- **Cupulín piloto.** Corregir el asiento a lo largo del eje, conformar el anillo exterior y comprobar los rayos perdidos y la superficie realmente visible en un entorno que abarque toda la boca. Comparar también desde la cámara visitante. Si la cobertura mejora a costa de ocultar el pozo con piezas enteras, hay que revisar el corte.
- **Clave propia.** Diseñar el remate a partir de los quiebros visibles en la ortoimagen y contrastar su perfil con la sección. Documentar qué alturas intermedias se eligen. El ensayo debe recuperar el dibujo central y respetar la altura general con el mismo origen vertical.
- **Un sector de las hiladas.** Reconstruir un grupo reconocible de caras y encuentros, con sus dos filas vecinas. Comprobar direcciones, concavidades, cobertura y lectura en perspectiva. Extender el método al resto tras ver qué elementos se repiten realmente.
- **Encuentro con el tambor.** En la fotografía los vanos están enmarcados por molduras y planos con relieve. Las grandes superficies lisas que los rodean en el render también influyen en la percepción de escala. Conviene revisar una ventana y su cornisa cuando esté fijado el arranque de las hiladas.

## Reproducción y alcance

Desde la raíz del repositorio, con el OBJ de las previas presente:

```bash
nice -n 15 taskset -c 0 ~/.local/opt/blender/blender -b -t 1 --python-exit-code 1 -P scripts/auditar_geometria_obj.py
OPENBLAS_NUM_THREADS=1 nice -n 15 taskset -c 0 .venv/bin/python scripts/contrastar_geometria_campo.py
```

Las dos salidas numéricas son [auditoría de la malla](../../datos/auditoria_geometria_obj.json) y [contraste con el campo y la sección](../../datos/contraste_geometria_campo.json). Incluyen el hash del OBJ y los resultados por radio, frente o cupulín. El relieve usa iluminación fija de normales geométricas de triángulo. La faceta individual se ve más marcada que con el sombreado suave de Cycles. Los rayos y los cortes de esta auditoría se refieren a la malla exportada. La reconstrucción histórica completa sigue requiriendo correspondencias y cotas locales.

### Piloto ejecutado en cupulin_00

Se recalcularon base y dos bordes del marco a lo largo de sus generatrices a 30°. Solo se sustituyeron los vértices de este grupo. Antes de sustituirlos se contrastó la geometría original regenerada con los vértices del OBJ. Sobre un encuadre fijo de 5,5 catetos y 180 × 180 rayos, en ortogonal los rayos sin impacto bajan de 5567 a 4700 y los impactos visibles en el grupo suben de 3419 a 4605. Desde la posición visitante, apuntando al mismo detalle, bajan de 594 a 47 y suben de 6302 a 7291, respectivamente. El recorte incluye el entorno exterior de la boca y excluye la sala. El total de rayos sin impacto no equivale al área de una junta. El ensayo conserva el descarte original de piezas enteras y el desplazamiento local del marco de −0,03 catetos.

Reconstrucción de ambas vistas y de la lámina local:

```bash
OPENBLAS_NUM_THREADS=1 nice -n 15 taskset -c 0 .venv/bin/python scripts/piloto_asiento_cupulin.py
nice -n 15 taskset -c 0 ~/.local/opt/blender/blender -b -t 1 --python-exit-code 1 -P scripts/ver_piloto_asiento.py
.venv/bin/python -c 'from PIL import Image; Image.open("renders/previas/piloto_asiento.ppm").save("renders/previas/piloto_asiento.png")'
```

Izquierda, vigente. Derecha, piloto. Arriba, ortogonal. Abajo, visitante. El turquesa identifica el cupulín completo incluido su marco y el granate, rayos sin impacto en la bóveda. Resultados en `datos/piloto_asiento.json`. El asiento intersectado queda como opción de ensayo.

### Contraste del descarte por centroide en el cupulín 00

Se regeneraron las 36 piezas que elimina el marco piloto y se repusieron enteras como control, manteniendo fijas las demás superficies. Desde el visitante cierran los 47 rayos abiertos del recorte, pero los impactos visibles en el grupo del cupulín bajan de 7291 a 1963. En ortogonal cierran solo 227 de 4700 rayos abiertos y la visibilidad del grupo baja de 4605 a 1952. Rechazada la reposición entera. El dato ortogonal impide atribuir todas las aberturas del entorno al descarte de estas piezas. Para la siguiente prueba, recortar las piezas en el perímetro de la boca y comprobar cobertura y visibilidad con estas mismas cámaras.

```bash
OPENBLAS_NUM_THREADS=1 nice -n 15 taskset -c 0 .venv/bin/python scripts/recuperar_piezas_marco.py
nice -n 15 taskset -c 0 ~/.local/opt/blender/blender -b -t 1 --python-exit-code 1 -P scripts/ver_piloto_asiento.py -- --reponer
.venv/bin/python -c 'from PIL import Image; Image.open("renders/previas/piloto_marco_entero.ppm").save("renders/previas/piloto_marco_entero.png")'
```

### Piloto con piezas recortadas

A las 36 piezas del control anterior se les resta individualmente el prisma definido por los 96 vértices de la boca y su eje inclinado. Se eligió el contorno interior del marco. En cada vista se lanzan los mismos 32.400 rayos. En visitante quedan 0 sin impacto (47 antes) y 6934 impactos en el grupo del cupulín (7291 antes, 1963 reponiendo piezas enteras). En ortogonal quedan 4473 sin impacto (4700 antes) y 4087 en el cupulín (4605 antes, 1952 con piezas enteras). El corte conserva la mejora de cobertura de las piezas enteras en ambas vistas y recupera gran parte de la visibilidad perdida. Los 4473 rayos ortogonales restantes incluyen el entorno del marco. El ensayo se limita al grupo 00 del OBJ previo a los modificadores.

Desde la raíz, tras generar el asiento piloto:
```bash
OPENBLAS_NUM_THREADS=1 nice -n 15 taskset -c 0 .venv/bin/python scripts/recuperar_piezas_marco.py
nice -n 15 taskset -c 0 ~/.local/opt/blender/blender -b -t 1 --python-exit-code 1 -P scripts/recortar_marco_piloto.py
nice -n 15 taskset -c 0 ~/.local/opt/blender/blender -b -t 1 --python-exit-code 1 -P scripts/ver_piloto_asiento.py -- --recortar
.venv/bin/python -c 'from PIL import Image; Image.open("renders/previas/piloto_marco_recortado.ppm").save("renders/previas/piloto_marco_recortado.png")'
```

### Ensayo del cupulín y dos filas locales

Hipótesis previa: los cambios de dirección en la entrada al pozo y el relieve de la estrella deben poder leerse desde el visitante. Si el cambio requiere una ampliación para resultar convincente, el ensayo termina en el cupulín 00.

La lectura de AA-415_23 p. 1 muestra caras planas casi rectangulares a la derecha de la boca, un extremo apuntado a la izquierda y apoyos oblicuos entre ambos. La lámina de lectura marca cuatro aristas a mano. Se tomó como base el piloto de asiento corregido con piezas recortadas. Se ensayaron dos filas escalonadas locales que sustituyen la superficie de las hiladas en una corona alrededor de la boca, dos registros alternos en el interior y una estrella con profundidad. El límite exterior toma su altura por intersección con los triángulos vecinos en 96 direcciones. Los apoyos perdidos en ese muestreo usan la cota del marco. La anchura, los ocho sectores repetidos, las concavidades y las alturas intermedias son elecciones del ensayo. El corte de la corona se usa para visualización superficial y no certifica sólidos cerrados.

Las parejas muestran la misma cámara, geometría vecina y luz en yeso. La planta se presenta orientada para comparar la punta de la boca con la ortoimagen. La perspectiva desde el visitante se muestra ampliada y también en el encuadre completo, con la bóveda aislada de la sala. La referencia conserva su iluminación fotográfica. Reproducción desde la raíz con los archivos del piloto recortado:

```bash
nice -n 15 taskset -c 0,1 ~/.local/opt/blender/blender -b -t 2 --python-exit-code 1 -P scripts/ensayar_cupulin_articulado.py
.venv/bin/python scripts/laminas_cupulin_articulado.py
```

Láminas locales: `renders/previas/articulado_comparacion.png`, `articulado_par_detalle.png`, `articulado_par_visitante.png` y `articulado_lectura.png`. El candidato introduce más escalones, pero la repetición de coronas conserva el aspecto de marco continuo. En el exterior aparecen empalmes angulosos, y las caras rectangulares grandes de la referencia siguen sin leerse. Se conserva como ensayo local.
