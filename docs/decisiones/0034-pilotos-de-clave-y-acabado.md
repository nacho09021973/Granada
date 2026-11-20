# 0034 — Pilotos de clave central y acabado de obra nueva

2026-11-20. Ensayos locales; sin promoción de la clave al generador.

## Preguntas y límites previos

Continuación de 0033: sustituir solo la superficie central, conservar el
perímetro y comprobar altura, cobertura y lectura desde el visitante.
Se descarta la promoción si abre juntas, excede 4,67 m o no recupera una
lectura de encuentros compatible con la referencia. Cumplir las dos primeras
condiciones no basta para la tercera.

El usuario señala que las imágenes parecen un videojuego. Se contrasta
también un acabado de obra nueva con igual geometría, luz y cámara. No se
usa ese acabado para validar la reconstrucción ni se denomina hiperrealista
la salida de este ensayo.

## Clave ejecutada

`scripts/ensayar_clave_estrellada.py` sustituye las alturas de los 4.853
vértices de `cupulilla_25`, manteniendo sus coordenadas en planta y sus
triángulos. Conserva exactamente los 266 vértices del perímetro. La estrella
tiene ocho puntas, radios alternos de 0,38 y 0,29 m, cotas elegidas entre
4,40 y 4,67 m y una transición de 10 cm al borde existente. Estos valores
son supuestos del ensayo, no mediciones. El perfil original no se conserva
en el interior: hacerlo arrastraba parte de su exceso de altura.

Máximo del candidato: 4,670000 m. La cobertura vertical del grupo se conserva
por identidad de planta y triangulación. En 10.000 rayos desde el visitante,
apuntados al detalle con encuadre fijo, quedan 38 sin impacto en ambas
versiones; los impactos en la clave pasan de 2.978 a 3.295. Son muestreos de
la bóveda aislada antes de modificadores, no certifican ausencia de juntas
desde cualquier cámara ni de intersecciones entre sólidos.

**Evaluación visual: no se promueve.** El detalle renderizado muestra el
motivo estrellado con bordes escalonados por la rejilla. El encuentro exterior
sigue dominado por un anillo circular. En el recorte de la ortoimagen de
AA-415_23 p. 1 usado en 0032 se observan agrupaciones angulares alrededor
del centro que este ensayo no reproduce. La sección fotográfica extraída
del mismo plano se inspeccionó, pero no se midieron nuevas cotas locales:
solo se respeta la calibración de altura de 0033. La fidelidad de su perfil
local queda abierta. No se da por cerrada la clave.

## Acabado y aspecto artificial

La inspección del render `cupula_cycles_cupula_ferrer.png` frente a la
ortoimagen y la sección muestra bandas de piezas curvadas juntas, bocas
extensas y muros del tambor con muy poco relieve. La referencia contiene
agrupaciones angulares y ornamentación de escala mucho menor. Esta
comparación visual no asigna un porcentaje de culpa a cada componente.

El código de `render_cycles.py` añade alabeo nominal de 0,05 catetos
(unos 11 mm), bisel de 0,02 catetos y pérdida de pigmento con intensidad
0,55. El yeso usa un nodo Bump con Distance=0,2 catetos. Este último es un
parámetro de sombreado, no un desplazamiento geométrico de 4,5 cm.

Se añade la opción `--acabado obra-nueva`: omite los modificadores de
alabeo y bisel, el desgaste y la suciedad de los materiales de yeso/pigmento,
y reduce Distance del Bump a 0,001 catetos. Conserva los colores, el oro,
la rugosidad y la luz existentes. No es una calibración material del yeso.
El defecto sigue siendo `actual`; no se sustituye una opción por otra
basándose solo en que su nombre encaje con el objetivo del proyecto.

Las dos variantes de acabado se renderizan sobre el OBJ vigente, sin la
clave candidata, a 560 px y 16 muestras. Las parejas de clave usan yeso
neutro, igual luz y cámara. Son comparaciones de diagnóstico, no imágenes
finales de alta resolución.

**Resultado de la comparación de acabado:** en la vista completa a 560 px,
quitar el envejecimiento y reducir el microrelieve cambia poco la impresión
general. Persisten las bocas oscuras, las bandas continuas y la simplicidad
del tambor. En estas condiciones, el acabado por sí solo no resuelve la
objeción visual del usuario. No se extrapola este juicio a detalles que
esta resolución no permite apreciar. Ambas ejecuciones de Cycles y las
cuatro vistas de la clave terminaron correctamente con Blender 4.5.15 LTS;
`git diff --check` pasó.

## Reproducción y procedencia

Desde la raíz, con el OBJ vigente y su MTL presentes:

```bash
nice -n 15 ~/.local/opt/blender/blender -b -t 2 --python-exit-code 1 -P scripts/ensayar_clave_estrellada.py
nice -n 15 ~/.local/opt/blender/blender -b -t 2 --python-exit-code 1 -P scripts/render_cycles.py -- --obj renders/previas/cupula_campo_vigente_1400.obj --lado 560 --muestras 16 --vistas cupula --salida renders/previas --sufijo _acabado_actual --acabado actual
nice -n 15 ~/.local/opt/blender/blender -b -t 2 --python-exit-code 1 -P scripts/render_cycles.py -- --obj renders/previas/cupula_campo_vigente_1400.obj --lado 560 --muestras 16 --vistas cupula --salida renders/previas --sufijo _acabado_obra_nueva --acabado obra-nueva
.venv/bin/python scripts/laminas_clave_y_acabado.py
```

Datos: `datos/piloto_clave_estrellada.json` y
`datos/procedencia_clave_y_acabado.json`. El segundo registra hashes del
OBJ, MTL, fuentes y scripts. Geometría local: `renders/previas/clave_estrellada_piloto.npz`.
Láminas: `clave_comparacion_detalle.png`, `clave_comparacion_visitante.png`
y `comparacion_acabado.png`, en `renders/previas/`.

El siguiente trabajo geométrico requiere una malla con aristas alineadas
con los quiebros y piezas reconocibles de la referencia; deformar otra vez
la rejilla del cierre no resuelve ese requisito. Quedan pendientes la clave
definitiva, el sector de hiladas y el relieve del tambor del plan 0032.
