# 0038 — Encaje del paño 00 con la sección

21 de noviembre de 2026. Continúa el diagnóstico 0037. El alcance es el
desfase vertical del piloto y su encuentro local; el acabado hiperrealista
queda para un trabajo posterior.

## Cambio geométrico

El modo `seccion` de `scripts/hiladas_ventanas.py` convierte directamente las
filas de píxel con el origen y la escala de `datos/alzado_sala.json`. Elimina
el desplazamiento de −35,548 cm y el límite artificial de −1,3 cm del
segundo orden. Las 33 crestas conservan las cotas de las lecturas de 0036.
Se mantiene la separación mínima propuesta entre los órdenes. La versión
anterior se puede reproducir con `--encaje 0036`.

El primer ensayo conservaba el fondo de 25,1 cm. Al levantar las crestas,
la cornisa restante ocultaba parte del segundo orden y aparecían cruces
con la primera fila del campo. El fondo se lleva al borde interior de la
cornisa del modelo: **32,05 cm**. Se recortan en esa huella la primera fila
y los frentes tallados que la invadían. El canto recortado vuelve a la cota
de la cornisa mediante un apoyo vertical que reutiliza sus vértices.
No se estira ni se levanta el resto del campo.

La profundidad de 32,05 cm es un **encaje geométrico propuesto** con la
cornisa existente, no una medida histórica de fondo. El perfil posterior,
los macizos, el dibujo de las celosías y la talla siguen propuestos. La
transferencia de la sección al paño +X sigue siendo la hipótesis de 0036.
La cúspide exterior del nicho no es el borde luminoso del vano: eliminar el
desfase de las crestas no valida la abertura como una medición histórica.
Falta una vista oblicua registrada del mismo tramo para contrastar fondos
y apoyos antes de repetir el paño.

## Comprobaciones y procedencia

`tests/test_perfil_pano.py` comprueba las 33 crestas mediante una segunda
formulación desde el suelo, la separación de los órdenes, el control 0036
y el rechazo de un encaje desconocido. La tolerancia de 0,5 mm del contraste
desde el suelo absorbe el redondeo del JSON; no expresa la incertidumbre de
la lectura manual de la fotografía. La suite completa tiene 788 tests.

`scripts/comprobar_encaje_pano_glb.py` lee las coordenadas del GLB final,
incluidas las transformaciones de nodo, y comprueba las crestas exportadas.
Contrasta cada pieza del paño con las hiladas, cupulines, cierres, frentes
tallados y apoyos. Usa BVH y una prueba de cruce transversal entre triángulos
a 1 µm, con controles de cruce, separación y coplanaridad. El recuento es de
pares de triángulos, no de defectos independientes. Excluye contactos
coplanares y no certifica distancia mínima, estanqueidad de toda la cúpula
ni ausencia global de auto-intersecciones.

Los resultados y hashes quedan en `datos/comprobacion_encaje_pano_glb.json`.
La ficha del modelo conserva también los hashes de los generadores y las
comprobaciones de rayos y juntas. El muestreo previo del intradós queda en
`datos/registro_encuentro_pano.json`, generado por
`scripts/registrar_encuentro_pano.py` sobre el OBJ auditado. No debe
interpretarse como un muestreo del GLB corregido.

Resultado final del GLB incorporado a `web/modelos/`:

- Error numérico máximo de las 33 cotas exportadas menor de 1 µm. Esto
  verifica la conversión, no la precisión histórica de las lecturas.
- Cruces transversales del paño con las superficies vecinas examinadas:
  **150 pares en el control, 0 en el candidato**. Los 972 triángulos de los
  apoyos finales tienen área no nula con el umbral del comprobador.
- Los 31 encuentros laterales conservan al menos 17 vértices compartidos;
  hay 1370 posiciones compartidas entre órdenes y 1369 con la pared.
- Desde sala, frontal y lateral se alcanzan las 16 y las 17 piezas. Los
  impactos luminosos de los vanos se conservan antes y después de montar
  el paño: 80/68, 191/254 y 263/127 respectivamente, sobre 759 rayos por vano
  y vista. No son los mismos vanos del control 0036 desplazado.
- La boca del cupulín mantiene 883 y 928 impactos en los dos controles de
  4225 rayos. No se amplía ese resultado a todas las vistas posibles.

El GLB descomprimido final tiene SHA-256
`9830381458461aa24c66c148bca53fc4eba18ccf969c47de17c17eb1a428567c`;
el gzip ocupa 16.709.741 bytes y contiene 181 mallas y 1.086.004 triángulos.

## Reproducción

La copia de control se obtiene de `2e83eb1`, sin regenerar ni cambiar su
iluminación. Las imágenes de la sección y las comparaciones con ellas son
solo locales, conforme a las exclusiones del repositorio.

```bash
mkdir -p build/0036_original/modelos
git show 2e83eb1:web/modelos/dos-hermanas.glb.gz > build/0036_original/modelos/dos-hermanas.glb.gz
git show 2e83eb1:web/modelos/dos-hermanas.json > build/0036_original/modelos/dos-hermanas.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ~/.local/opt/blender/blender -b -t 4 --python-exit-code 1 -P scripts/exportar_visita_web.py -- --salida build/encaje-seccion/modelos
OPENBLAS_NUM_THREADS=1 ~/.local/opt/blender/blender -b --python-exit-code 1 -P scripts/comprobar_encaje_pano_glb.py -- --antes build/0036_original/modelos/dos-hermanas.glb.gz --exigir
```

El exportador usa el encaje `seccion` por defecto y permite dirigir la salida
a una carpeta de ensayo. La prueba en navegador usa la misma cámara y gestos
que el control; no cambia materiales ni iluminación para favorecer el candidato.

La prueba final de navegador pasa: sala, selección, zoom, órbita, retorno y
controles táctiles emulados. Se inspeccionan las capturas del giro y la
[comparación local con la versión anterior](../../renders/previas/0038_comparacion_web.png).
El ajuste no resuelve el aspecto de videojuego: las superficies repetidas,
la interpretación de las tallas y el acabado quedan para la fase visual.

Con el servidor local en marcha:

```bash
NODE_PATH=build/comprobacion-web/node_modules CHROME_PATH=/home/adnac/.cache/ms-playwright/chromium-1187/chrome-linux/chrome node scripts/comprobar_visita_web.cjs http://127.0.0.1:8765/web/visita.html#hiladas renders/previas/0038_final
.venv/bin/python scripts/comparar_visita_web.py --hiladas renders/previas/2026-11-21_web renders/previas/0038_final renders/previas/0038_comparacion_web.png
```
