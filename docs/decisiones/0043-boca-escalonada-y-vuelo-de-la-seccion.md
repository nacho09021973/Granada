# 0043 — Boca escalonada de los vanos y perfil del paño 00 según la sección

22 de noviembre de 2026. Quedaban dos pendientes de 0042: el remate
escalonado de cada nicho y el contraste del vuelo de 32,05 cm de las hiladas
(0038). El usuario elige rehacer los dos (opción A): medir el remate, poner
la boca escalonada en los dieciséis vanos y ajustar el perfil del paño 00 a
la sección.

## Vuelo: silueta lateral de la sección

`scripts/medir_vuelo_seccion.py` mide la silueta de los bordes de
`docs/AA-415_23_seccion.jpg`, dos lados y tres umbrales. En esos bordes la
ortofoto muestra de canto las caras laterales del tambor. El control de
escala da apotemas de 3,856 y 3,873 m, frente a 3,866 m en el modelo. Resultado en
`datos/vuelo_seccion.json`:

- el plano del muro termina a **−0,154 m** del arranque (de −0,136 a −0,169);
- entre ese punto y +0,05/+0,09 m la silueta vuela de 4 a 25 cm;
- después hay un salto horizontal hasta 0,52 m (lado izquierdo) y 0,58 m (lado derecho).

`scripts/silueta_glb_seccion.py` extrae la misma silueta del GLB. Renderiza
en ortográfica, con el mismo corte, y recorta el modelo en el plano del muro,
porque la sección no muestra nada más allá. En el GLB de 0042 el muro llegaba
a +0,20 m y el salto, a +0,38 m. Quitar las caras oblicuas
(`--solo-pano`) no cambia el perfil.

Los 32,05 cm no son visibles en la silueta: son el borde interior oculto tras
las adarajas, y la silueta solo da lo más cercano al muro. Lo que sí se contrasta es la
cota a la que el paño se separa del muro.

## Remate: medida

Las lecturas a ojo están en `datos/lecturas_remate_trip82.json`: dos vanos de
la cara B de `Granada_trip82.jpg`, ±8 px. `scripts/medir_remate_fotos.py` las
retroproyecta al plano del muro con la cámara de 0041 y toma como eje el
centro del merlón. Resultado en `datos/remate_nichos.json`:

| tramo | |s| exterior (m) | z foto (m) | z sección frontal (m) |
|---|---|---|---|
| merlón | 0,043 | +0,171 | +0,186 |
| hombro | 0,174 | +0,057 | +0,064 |
| entrante | 0,261 | −0,147 | −0,138 |
| pináculo | 0,347 | +0,031 | +0,002 |
| esquina (marco) | 0,464 | −0,148 | −0,148 |

Las cotas coinciden en los dos vanos con ±1–2 cm, y los límites de los tramos con ±0,5 cm.
Semiancho de la boca: 0,404 m (de 0,36 a 0,47); semiancho del marco: 0,464 m.

**Segunda vía.** La vista frontal de la sección es una ortofoto y da la cota
real del contorno del vano del paño 00, sin depender de la cámara. Esas
lecturas están en el mismo JSON. La ortofoto suaviza los escalones en
lóbulos, pero sus puntos altos y bajos caen a 0–3 cm de la foto y en las
mismas posiciones laterales. Por eso el remate se modela plano, en el plano
del muro.

**Descartado:**
- **Foto de Bruchez:** no tiene resolución para leer el remate.
- **Triangular con las dos cámaras:** su separación (unos 0,7 m) no basta.
  Los contornos de prueba desplazados en profundidad casi no se separan en la imagen.
- **Resolver cota y vuelo contra la silueta lateral:** daba el merlón a +0,025 m, lo que
  contradice la vista frontal.

**Comprobación cualitativa.** El contorno proyectado
(`renders/previas/0043/remate_*.jpg`) encaja en la cara B de `trip82`. En las
caras A y C, y en la foto de Bruchez, los cantos verticales caen bien pero los
escalones quedan de 30 a 60 px altos. Las cámaras de 0041 se ajustaron con
alféizares y lados verticales, que no fijan la escala vertical por encima del
alféizar. Las cotas de esta decisión se apoyan en la sección frontal, no en
esas caras.

## Cambio en el modelo

- **`scripts/nicho_escalonado.py`** (nuevo): contorno escalonado y marco.
  - Banda de 0,06 m con la moldura de 0035 escalada.
  - Nicho escalonado hasta 0,30 m, con muro de fondo y celosía en arco de
    0,29 m de semiancho.
  - El ápice de la celosía queda a −0,205 m para que quepa bajo la boca. No
    está medido directamente [UNVERIFIED].
  - Los anillos se obtienen desplazando el contorno. El merlón y el pináculo,
    que se quedan sin anchura, se reducen a un diente plano.
- **Paño 00, encaje `silueta`** en `scripts/hiladas_ventanas.py`:
  - Las dos órdenes bajan **0,213 m**: el máximo de la junta fuera de los
    marcos (+0,059 m) menos el final de muro de la sección (−0,154 m).
  - Sobre cada vano, la junta del primer orden es el contorno del marco, y el
    muro comparte sus vértices con las adarajas.
  - Los encajes `seccion` y `0036` se conservan.
- **Paños 1 a 7** (`tambor_con_vanos`, `boca="escalonada"`): mismo nicho. El
  remate se recorta 1,2 cm bajo el canto del muro (z = 0), porque allí no hay
  adarajas encima. El merlón, el hombro y el pináculo quedan a −0,012 m.
- **Exportador:** encaje `silueta` por defecto, y `nicho_escalonado.py` entre
  los generadores con hash.
- **`scripts/comprobar_encaje_pano_glb.py`:** la cota esperada de cada cresta
  es la junta del encaje anotado en la ficha del modelo. Con el GLB de 0042 da
  el mismo resultado.

No cambian:
- la cornisa ni su borde interior (0,3205 m);
- el campo de mocárabes, los cupulines ni los cierres;
- el eje de los vanos (±0,59 m) ni la profundidad del nicho (0,30 m).

## Comprobaciones

- **Exportador:** 31 juntas laterales con 17 vértices como mínimo; 1402
  vértices compartidos entre órdenes y 1402 con la pared. 181 mallas y
  1 092 992 triángulos, frente a 1 086 004 antes. Boca del cupulín 883/928.
- **Visita** (`datos/comprobacion_visita_0043.json`):
  - boca del cupulín 984/984;
  - cobertura 148/3096 y 622/12644, igual que antes;
  - las 16 y 17 piezas del paño, visibles desde las tres vistas.
- **Luz que llega a los vanos**, rayos sobre 759 (criterio `--vanos-cambiados` de 0042):

  | vista | 0042 | 0043 |
  |---|---|---|
  | sala | 38 / 29 | 15 / 13 |
  | frontal | 138 / 281 | 155 / 266 |
  | lateral | 191 / 15 | 192 / 39 |

- **Encaje** (`datos/comprobacion_encaje_0043.json`, `--exigir`): 0 pares
  transversales; error de las 33 crestas 9,7·10⁻⁹ m respecto al encaje `silueta`.
- **Silueta del GLB 0043** (`datos/vuelo_modelo_silueta_0043.json`): el muro
  llega a +0,17 m y el salto, a +0,26 m. Ahí entra el marco del vano, que el
  modelo pone en el plano del muro hasta el merlón. Entre los vanos el paño
  deja el muro a −0,15 m por construcción.
- **Navegador:** sala, selección, zoom, órbita, retorno y controles táctiles.
  Capturas en `renders/previas/0043_visita/`.
- 796 tests pasan, 5 nuevos en `tests/test_nicho_escalonado.py`. Contrastan
  los escalones con el JSON y la sección frontal, recalculan el descenso desde
  la silueta, comprueban las juntas y que la celosía cabe bajo la boca.

## Discrepancias abiertas

- **Silueta lateral y remate.** La silueta no muestra nada en el plano del muro
  por encima de −0,15 m. Si el corte incluye el vano de la cara lateral, la
  parte alta del remate debería volar hacia dentro entre 4 y 25 cm, y por
  encima de +0,09 m más de 0,5 m. La vista frontal no da sitio a ese vuelo, a
  menos que la escala vertical de la cámara lo compense. Con las fuentes
  actuales no se resuelve. El remate queda plano.
- **Salto del campo.** En la sección está a +0,05/+0,09 m y llega a
  0,52–0,58 m. En el modelo, el borde de la cornisa queda a 0,32 m en z = 0 y
  el campo sale a unos 0,36–0,45 m. Corregirlo exige tocar la cornisa y el
  campo.
- **Omisiones y supuestos:**
  - no se modela el pinjante que remata el merlón en las fotos;
  - la moldura del marco es propuesta;
  - en los paños 1–7 el remate queda recortado.

## Reproducción

```bash
.venv/bin/python scripts/medir_vuelo_seccion.py --modelo datos/vuelo_modelo_silueta_0042.json --modelo datos/vuelo_modelo_silueta_0043.json
.venv/bin/python scripts/medir_remate_fotos.py
OPENBLAS_NUM_THREADS=1 ~/.local/opt/blender/blender -b -t 4 --python-exit-code 1 -P scripts/exportar_visita_web.py -- --salida build/0043_original/modelos
OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/corregir_alturas_alzado.py --entrada build/0043_original/modelos/dos-hermanas.glb.gz --salida build/0043/modelos --informe datos/correccion_alturas_0043.json --verificacion datos/comprobacion_visita_0043.json --sin-laminas
OPENBLAS_NUM_THREADS=1 ~/.local/opt/blender/blender -b --python-exit-code 1 -P scripts/comprobar_alturas_visita.py -- --antes <GLB 0042> --despues build/0043/modelos/dos-hermanas.glb.gz --informe datos/comprobacion_visita_0043.json --vanos-cambiados
# repetir la corrección para adjuntar la verificación a la ficha (no cambia el GLB)
OPENBLAS_NUM_THREADS=1 ~/.local/opt/blender/blender -b --python-exit-code 1 -P scripts/comprobar_encaje_pano_glb.py -- --antes <GLB 0042> --despues build/0043/modelos/dos-hermanas.glb.gz --informe datos/comprobacion_encaje_0043.json --exigir
~/.local/opt/blender/blender -b --python-exit-code 1 -P scripts/silueta_glb_seccion.py -- --glb <GLB> --salida datos/vuelo_modelo_silueta_<v>.json --sufijo _<v> [--solo-pano]
~/.local/opt/blender/blender -b --python-exit-code 1 -P scripts/superponer_camaras_fotos.py -- --glb build/0043/modelos/dos-hermanas.glb.gz --sufijo _0043
```

`<GLB 0042>` es `web/modelos/dos-hermanas.glb.gz` del commit 152cf09
(SHA-256 descomprimido `5fa3b2b3…`). Control 0043 sin corregir: `bb648b44…`.
GLB de la visita: `13dc0cdc5940724f7d867ee8b492992b594466c1dd550d3167c88b618c8221d0`.
