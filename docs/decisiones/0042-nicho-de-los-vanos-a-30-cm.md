# 0042 — Nicho de los vanos del tambor a 30 cm

22 de noviembre de 2026. El usuario decide ahondar el nicho de los dieciséis
vanos según la medida de 0041. El remate escalonado de mocárabes sobre cada
nicho, que muestran las fotografías, queda para otro paso.

## Cambio

`PROFUNDIDAD_NICHO_M = 0.30` en `scripts/hiladas_ventanas.py`: valor del
ajuste conjunto de 0041, dentro del intervalo medido de 0,20–0,34 m. Antes
0,09 m, sin medida. Lo usan los dos generadores de vanos:

- **Paños 1 a 7** (`scripts/detalle_visita.py`, `tambor_con_vanos`): retranqueo
  de -0,09/-0,12 a -0,27/-0,30 m; tracería de la celosía de -0,085 a -0,265 m;
  panel luminoso de -0,19 a -0,37 m.
- **Paño 00** (`scripts/hiladas_ventanas.py`, `pared_piloto`): último anillo
  del nicho y celosía de 0,09 a 0,30 m; fondo luminoso de 0,17 a 0,38 m.

Las distancias entre esos elementos se conservan. No cambian los anchos ni el
eje de los vanos (0041 no los resolvió), las hiladas del paño 00, el campo,
los cupulines ni los cierres. Se conserva el ajuste de alturas de 0040.

## Regeneración

El control sale del exportador y la visita aplica después la corrección 0040,
como indica esa decisión. Para no sobrescribir los registros de 0040,
`scripts/corregir_alturas_alzado.py` acepta ahora `--informe`,
`--verificacion` y `--sin-laminas`, y `scripts/comprobar_alturas_visita.py`
acepta `--informe`; sus valores por defecto siguen siendo los de 0040. En
una primera ejecución sin esas opciones se sobrescribieron
`datos/correccion_alturas_alzado.json` y `web/estudio_alzado/despues.png`; se
restauraron desde git antes de seguir.

```bash
OPENBLAS_NUM_THREADS=1 ~/.local/opt/blender/blender -b -t 2 --python-exit-code 1 -P scripts/exportar_visita_web.py -- --salida build/0042_original/modelos
OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/corregir_alturas_alzado.py --entrada build/0042_original/modelos/dos-hermanas.glb.gz --salida build/0042/modelos --informe datos/correccion_alturas_0042.json --verificacion datos/comprobacion_visita_0042.json --sin-laminas
OPENBLAS_NUM_THREADS=1 ~/.local/opt/blender/blender -b --python-exit-code 1 -P scripts/comprobar_alturas_visita.py -- --antes <GLB 0040> --despues build/0042/modelos/dos-hermanas.glb.gz --informe datos/comprobacion_visita_0042.json --vanos-cambiados
# repetir la corrección para adjuntar la verificación a la ficha (no cambia el GLB)
OPENBLAS_NUM_THREADS=1 ~/.local/opt/blender/blender -b --python-exit-code 1 -P scripts/comprobar_encaje_pano_glb.py -- --antes <GLB 0040> --despues build/0042/modelos/dos-hermanas.glb.gz --informe datos/comprobacion_encaje_0042.json --exigir
~/.local/opt/blender/blender -b --python-exit-code 1 -P scripts/superponer_camaras_fotos.py -- --glb build/0042/modelos/dos-hermanas.glb.gz --sufijo _0042
```

`<GLB 0040>` es `web/modelos/dos-hermanas.glb.gz` del commit 4845a8f
(SHA-256 descomprimido `dd3de2e2…`). Control 0042 sin corregir:
`363413c6…`. GLB de la visita: `5fa3b2b300d39632c1cc318ca1de857ca9adfbf2f7234efa250b6a769a8ce55c`.

## Comprobaciones

- **Exportador:** mismos 1 086 004 triángulos, mismas juntas del paño 00
  (31 juntas, 1370 vértices compartidos) y misma visibilidad de la boca del
  cupulín que el control 0040.
- **Visita, GLB importado** (`datos/comprobacion_visita_0042.json`): boca del
  cupulín 984/984 en las dos vistas; cobertura del techo 148/3096 y 622/12644
  sin cubrir, igual que antes; las 16 y 17 piezas del paño visibles desde las
  tres vistas.
- **Luz que llega a los vanos del paño 00** (rayos sobre 759 por vano):

  | vista | 0040 | 0042 |
  |---|---|---|
  | sala | 80 / 68 | 38 / 29 |
  | frontal | 191 / 254 | 138 / 281 |
  | lateral | 263 / 127 | 191 / 15 |

  Es el efecto buscado: un nicho tres veces más hondo tapa más vano en las
  vistas oblicuas. El criterio de 0040 («cada vano ≥ 95 % del anterior»)
  falla por eso; se añade la opción explícita `--vanos-cambiados`, que solo
  para este control exige que cada vano siga visible (> 0 rayos) y deja
  anotado el criterio en el informe. El mínimo es 15/759 (vano 2, vista
  lateral).
- **Encaje del paño 00** (`datos/comprobacion_encaje_0042.json`, `--exigir`):
  33 crestas, 0 cruces, 0 pares transversales, error de cotas 1,4·10⁻⁸ m,
  igual que en 0040.
- **Navegador** (`scripts/comprobar_visita_web.cjs`): sala, selección, zoom,
  órbita, retorno y controles táctiles. Capturas en `renders/previas/0042_visita/`.
- **Contraste con las fotos de 0041:** con las mismas cámaras, la cara C del
  modelo enseña ahora pared lateral del nicho en el mismo lado y con anchura
  parecida a la de la foto (`renders/previas/0041_*/cara_C_foto_0040_0042.jpg`).
  Sigue faltando el remate escalonado y el marco exterior del nicho.
- 791 tests pasan.

## Límites

La profundidad es la del ajuste conjunto de 0041, con su intervalo de
±7 cm y sus supuestos. Las jambas siguen perpendiculares al muro: el
derrame no se resolvió. La luz por vértice se calcula en el exportador antes
de la corrección 0040, con muestras situadas 10 cm por delante del plano
del muro, que el nicho no altera; la ficha conserva la etiqueta heredada
«Conservada del control 0038». El vuelo de 32,05 cm de las hiladas sigue sin
contrastar.
