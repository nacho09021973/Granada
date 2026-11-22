# 0040 — Salientes y alzado de Foto de Ferrer.png

21 de noviembre de 2026. El usuario señala que los remates sobresalen más
en el modelo que en `docs/Foto de Ferrer.png` y pide contrastar y corregir
el alzado. Se incorpora una rebaja al GLB de la visita, conservando una
copia del control 0038 en `build/0040_original/modelos/`.

## Referencia y registro

Se inspecciona la captura indicada, no las fotografías de otras maquetas.
`scripts/registrar_foto_ferrer.py` la registra sobre la sección nativa
`docs/AA-415_23_seccion.jpg`: correlación normalizada en dos recortes
distintos. Ambos producen escala **0,2302621**, desplazamiento **(−51, 61) px**
y correlaciones 0,98978 y 0,98963. Los hashes, cajas y calibración vigente
quedan en `datos/registro_foto_ferrer.json`. La escala resultante es
108,796 px/m. No se estira por separado la altura o la anchura del modelo.

El alzado del modelo usa el origen vigente del proyecto, media cúpula
posterior seleccionada por centroide de triángulo y sombreado geométrico.
No es un registro de cada pieza ni una sección exacta de sólidos. El perfil
global no permite deducir por sí solo la profundidad de cada cupulín
interior. El modelo sigue siendo aproximado; la comparación no autoriza a
declarar que todos sus perfiles y encuentros coinciden con la fotografía.

## Dos salientes diferentes

El contraste distingue los 16 pozos (`cupulin_*`, azules en la lámina) de
los 65 casquetes de cierre (`cupulilla_*`, grises). Los dos habían recibido
alturas de presentación: cinco pasos en los pozos y altura relativa 2,0
en los cierres. Los comentarios originales explicaban esas elecciones por
el aspecto oscuro de las celdas. Una altura elegida para producir sombra
no es una medida geométrica de la obra.

### Corrección incorporada

- **64 casquetes**, dejando la clave `cupulilla_25` intacta. Se reconstruye
  una base armónica a partir de su contorno y se conserva el **45 % del
  exceso** sobre esa base. Equivale a recuperar un acabado de menor altura
  que el control 2,0; no es un factor medido en la fotografía. La rebaja
  máxima en un vértice es **23,59 cm**. Planta y vértices de borde quedan fijos.
- **16 pozos**. Se ensaya el techo correspondiente a dos pasos, limitado
  por la cota más alta de cada boca más una holgura. La transformación es
  monótona a lo largo del eje de 30° y deja fijos el marco y los primeros
  2 cm de pared junto al asiento. La reducción efectiva a lo largo del eje
  va de **8,82 a 34,67 cm**: no todos pueden bajar lo mismo sin rehacer la boca.
- Se conservan los triángulos y se recalculan las normales de las superficies
  modificadas. No cambian el paño de 0038 ni la altura de 4,67 m de la clave.

Son correcciones propuestas para reducir el exceso visible, no mediciones
de esas alturas a partir de la captura. El alzado aún enseña discrepancias,
especialmente en los pozos extremos y en las transiciones del campo.

### Alternativas no incorporadas

Se prueba bajar solo los techos, así como recalcular los 16 asientos por
intersección con el campo, a 30° y a 52°. Datos en
`datos/reduccion_saliente_cupulines.json`, `datos/cupulines_asiento_altura.json`
y `datos/cupulines_normal_cono.json`. Los asientos corregidos modifican sus
contornos espaciales y necesitarían rehacer los encuentros. No se sustituyen
globalmente por el mero hecho de disminuir el saliente. La modificación
incorporada conserva los asientos y los bordes que ya usa la visita.

## Verificación del archivo entregado

`scripts/corregir_alturas_alzado.py` vuelve a leer el GLB escrito y coteja
todos los grupos: mismos triángulos, grupos no modificados y error máximo
de serialización de **0,22 µm**. Las pruebas con un casquete sintético de
base inclinada contrastan el factor 1 (identidad), el factor 0 (base) y
la conservación de borde y planta. Otra prueba contrasta la boca fija del
pozo y su reducción de altura. **791 tests pasan**.

`scripts/comprobar_alturas_visita.py` importa por separado ambos GLB y usa
las mismas cámaras y destinos. Los resultados quedan en
`datos/comprobacion_alturas_visita.json`:

- Ventanas: mismos impactos luminosos en las tres vistas, **80/68** desde
  sala, **191/254** frontal y **263/127** lateral, sobre 759 rayos por vano.
  Se alcanzan las 16 y 17 piezas del paño en las tres posiciones.
- Cupulín piloto: **982 → 984** impactos desde sala y **979 → 984** desde
  la vista oblicua, sobre 4225 rayos. Este control se calcula sobre el GLB
  importado y no debe confundirse con las cifras del exportador antes de glTF.
- Cobertura del techo en disco de radio 3,35 m: **148/3096** rayos sin
  cubierta con rejilla 64 y **622/12644** con rejilla 128, iguales antes y
  después. No se afirma estanqueidad ni resolución de los huecos anteriores.

El encaje del paño de 0038 se repite sobre ambos GLB con
`scripts/comprobar_encaje_pano_glb.py --informe datos/0040_comprobacion_encaje.json`:
33 crestas, 0 cruces y 0 pares transversales en los dos, error máximo de
cotas 1,4·10⁻⁸ m. La rebaja no altera el paño.

El navegador pasa sala, selección, zoom, órbita, retorno y controles táctiles
emulados. Se inspeccionan las capturas de sala y cupulín. La página de
comparación también pasa carga de imágenes, deslizador y ancho móvil.

El GLB final tiene SHA-256
`dd3de2e2f3f6b5b406e01e1f75f7b015ea1d363d06638c53854df9d82306b197`.
La ficha adjunta incorpora la verificación nueva. La luz por vértice de
0038 se conserva y se rotula como anterior al ajuste; no se presenta como
iluminación física recalculada de la geometría nueva.

## Reproducción

El control es el GLB 0038, SHA-256 descomprimido `9830381458461aa24c66c148bca53fc4eba18ccf969c47de17c17eb1a428567c`.
Si falta la copia local, regenerar el control con `scripts/exportar_visita_web.py`
dirigiendo su salida a `build/0040_original/modelos`. El exportador del OBJ
genera el control; la visita actual requiere aplicar después esta corrección.
No aplicar repetidamente el factor al resultado ya corregido.

```bash
OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/registrar_foto_ferrer.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/alzado_ferrer_cupulines.py --glb build/0040_original/modelos/dos-hermanas.glb.gz --nombre antes
OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/reducir_saliente_cupulines.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/corregir_alturas_alzado.py
OPENBLAS_NUM_THREADS=1 ~/.local/opt/blender/blender -b --python-exit-code 1 -P scripts/comprobar_alturas_visita.py -- --antes build/0040_original/modelos/dos-hermanas.glb.gz --despues build/alzado-corregido/modelos/dos-hermanas.glb.gz
```

Repetir el paso de escritura después de la verificación adjunta los controles
a la ficha, sin cambiar el GLB. La copia verificada se incorpora a
`web/modelos/`. Las imágenes de comparación están en `web/estudio_alzado/` y
la [página de revisión](../../web/alzado-cupulines.html) enlaza la captura de
referencia sin redistribuir una copia nueva de la fotografía.
