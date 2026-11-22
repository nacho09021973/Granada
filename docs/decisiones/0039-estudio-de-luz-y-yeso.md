# 0039 — Estudio de luz y yeso en un encuadre

21 de noviembre de 2026. El usuario pide dejar atrás el aspecto de videojuego
después de cerrar el encaje del paño. Se prepara una comparación local del
encuadre de **Hiladas**, antes de extender un acabado a toda la visita.

## Resultado y límite

La [comparación local](../../web/estudio-yeseria.html) permite deslizar entre
la visita actual y un render de Cycles. Se inspeccionan las dos imágenes a
igual tamaño. El estudio produce sombras proyectadas y rebotes; el relieve
y los encuentros se leen de otra manera. **No se considera alcanzado el
hiperrealismo ni se promueve este acabado a toda la visita.** Las formas
repetidas, los macizos lisos y las aberturas de la malla siguen siendo visibles.

La visita conserva su GLB y sus materiales. El estudio aceptado para la
comparación también conserva las 181 mallas y 1.086.004 triángulos de 0038;
no mueve vértices. El microbisel es una perturbación de normales del shader,
no una corrección geométrica de siluetas ni de encuentros.

## Luz y materiales propuestos

Se importa el GLB detallado de 0038, no el OBJ de campo anterior. Se retira
la modulación por vértice usada como aproximación de luz en la web. El
albedo se obtiene del factor de material del GLB: leer solo el valor por
defecto del socket del importador producía blanco y se corrigió antes del
estudio definitivo.

El yeso y el crema reciben tonos de presentación nuevos; los otros factores
de color se conservan. Se añaden variación fina de tono, rugosidad 0,90,
relieve de superficie submilimétrico y microbisel de normales de 0,6 mm.
El ruido se evalúa en posición global, en metros. Son parámetros de acabado,
no análisis de pigmentos ni medidas del yeso histórico.

La luz de relleno sale de los fondos luminosos de los vanos y una luz de
área se sitúa en el interior de una ventana del propio paño para dar luz
rasante. Potencias, radiancia, exposición y balance de color son propuestos.
No representan una fecha, una orientación solar o una medición fotométrica.
La foto local `renders/previas/foto_commons_detalle.jpg`, localizada por la
entrada 19 de `docs/fuentes.md`, se inspecciona como referencia visual de
concavidades, caras planas y densidad del detalle. No se registra como una
fotografía del mismo encuadre ni se usa para medir sus colores.

## Comprobación

- Render final con RTX 5060/CUDA, Blender 4.5.15 LTS: 1800 × 1480 px,
  192 muestras, 2 min 22,77 s registrados por Blender.
- Se verifica el hash del GLB de entrada y su recuento de mallas y caras.
  El GLB original conserva el SHA-256
  `9830381458461aa24c66c148bca53fc4eba18ccf969c47de17c17eb1a428567c`.
- La cámara se contrasta por dos vías: la proyección de Blender y una
  perspectiva calculada por productos escalares con el contrato de
  `verHiladas` en Three.js. Cuatro puntos coinciden con error máximo de
  1,45 × 10⁻⁷ de la imagen. Registro en
  `datos/comprobacion_camara_estudio.json`.
- El recorte usa las mismas fracciones de viewport que el control web de
  0038. La comparación conjunta reduce ambos lados a 580 × 380 px. El
  estudio individual conserva 1160 × 760 px. La diferencia de resolución
  de origen y de motor de render impide atribuir toda diferencia visible
  a un único material o parámetro.
- La prueba de navegador comprueba carga de imágenes, cambio efectivo del
  encuadre al mover el deslizador, ancho móvil y ausencia de errores de página.
  No es una prueba de realismo. Se inspecciona también la lámina conjunta.

`datos/estudio_acabado_yeseria.json` conserva parámetros y hashes de fuentes,
generadores, control e imágenes. La escena `.blend` y el render completo
están en `renders/previas/0039_cycles/`; se regeneran con el script permanente.

## Ensayo adicional descartado

Se ensayaron un trasdós plano y tres macizos con talla vegetal usando
`--completar-macizos` (64 muestras, luz principal de 5 W, salida local
`renders/previas/0039_talla/`). El generador comprueba un muestreo del apoyo
en la pared. La inspección mostró hojas demasiado esquemáticas, sin el
detalle de la referencia; no se incorporan al GLB ni a la imagen principal
de comparación. El código de esa prueba se conserva como opción de ensayo,
desactivada por defecto, para mantener su procedencia. No constituye una
restitución documentada de la talla.

## Reproducción

Desde la raíz del repositorio, con Blender y las fuentes locales disponibles:

```bash
LD_LIBRARY_PATH=/usr/lib/wsl/lib OPENBLAS_NUM_THREADS=1 ~/.local/opt/blender/blender -b -t 4 --python-exit-code 1 -P scripts/render_estudio_yeseria.py -- --ancho 1800 --muestras 192 --salida renders/previas/0039_cycles --blend
OPENBLAS_NUM_THREADS=1 ~/.local/opt/blender/blender -b renders/previas/0039_cycles/estudio.blend --python-exit-code 1 -P scripts/comprobar_camara_estudio.py
.venv/bin/python scripts/preparar_comparacion_yeseria.py
NODE_PATH=build/comprobacion-web/node_modules CHROME_PATH=/home/adnac/.cache/ms-playwright/chromium-1187/chrome-linux/chrome node scripts/comprobar_estudio_yeseria.cjs
```

La revisión humana de este encuadre decide si interesa el acabado. Para
reducir la apariencia de modelo sigue haciendo falta geometría más fiel
del mismo tramo, especialmente talla, transiciones y soporte de las piezas.
