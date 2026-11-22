# 0041 — Profundidad del nicho de los vanos medida en dos fotografías

22 de noviembre de 2026. Continúa el pendiente de 0038: contrastar el paño
sobre las ventanas con una vista oblicua registrada de la obra. El usuario
pide buscar fuentes; se registran fotografías de Wikimedia Commons y se
intenta medir sobre ellas. No se modifica el modelo.

## Fuentes revisadas

- **Jones y Goury, láminas XIX y XX** (entrada 17 de `docs/fuentes.md`): la
  XIX no muestra la cúpula; la XX es un alzado frontal del ajimez del piso
  alto, no del tambor. Descartadas.
- **Vídeo de la maqueta de Contreras** (entrada 12): 480 × 856 px y vanos
  rectangulares sin repisa. Sirve solo como contraste cualitativo de la
  maqueta; no se usa.
- **Seis fotografías de Commons** (entrada 20), registradas con
  `scripts/registrar_fotos_tambor.py`. Se usan dos:
  `Granada_trip82.jpg` (Tibor Kovacs, CC BY 2.0; clave `trip82`) y
  `Alhambra_of_Granada_(8139873808).jpg` (Olivier Bruchez, CC BY-SA 2.0;
  clave `bruchez`).

No se encontró ningún modelo 3D, escaneo o levantamiento publicado de esta
sala en la búsqueda del 2026-11-22.

## Lo que muestran las fotos

Cada vano del tambor está en un nicho: marco exterior con remate escalonado
de mocárabes, paredes laterales, anillo en arco y celosía al fondo. En el
modelo la celosía está a 9 cm del plano del muro
(`scripts/hiladas_ventanas.py`, contorno con fondo 0,09) y no hay remate de
nicho. En las caras oblicuas la diferencia se ve sin medir:
`renders/previas/0041_*/cara_C_foto_modelo.jpg`.

## Método

1. `scripts/detectar_celosias.py` detecta en cada foto las celosías
   iluminadas (textura y brillo), el canto del alféizar que les tapa el pie
   y sus lados rectos. Identificación de vanos, umbrales y bordes excluidos,
   con su motivo, en `datos/lecturas_<clave>.json`; bordes en
   `datos/bordes_celosias_<clave>.json`.
2. `scripts/medir_nicho_fotos.py trip82 bruchez` ajusta a la vez una cámara
   por foto (focal, orientación, posición) y un nicho común: eje ±a, semiancho
   h de la celosía, profundidad d de la celosía tras el plano del muro y
   semiancho hn de la boca. Escala: apotema del modelo, 3,8657 m. Para cada
   lado decide si se ve la celosía o el canto de la jamba. Resultado en
   `datos/medida_nicho_fotos.json`.
3. `scripts/superponer_camaras_fotos.py` (Blender) renderiza el GLB vigente
   con cada cámara ajustada y lo funde con la foto.

Supuestos no contrastados con las fotos: cámara estenopeica con punto
principal centrado y sin distorsión; canto del alféizar en el plano del muro
y a la misma cota en las tres caras; seis nichos iguales y simétricos; jambas
planas. El borde visible puede ser en parte el anillo en arco y no la
celosía: el modelo de nicho no lo distingue.

## Resultado

| magnitud | ajuste conjunto | intervalo en 8 variantes | modelo |
|---|---|---|---|
| d, celosía tras el muro | 0,30 m | 0,20–0,34 m | 0,09 m |
| h, semiancho de la celosía | 0,29 m | 0,286–0,308 m | 0,265 m |
| a, eje del vano | 0,557 m | 0,549–0,570 m | 0,59 m |
| hn, semiancho de la boca | 0,32 m | 0,30–0,44 m | — |

Variantes: cada foto sola (`trip82` 0,31 m; `bruchez` 0,20 m) y las seis que
quitan una cara de una foto. La σ formal (±0,8 cm en d) no representa la
incertidumbre: se toma el intervalo entre variantes. RMS 7,7 px sobre 1504
puntos, por encima del ruido de detección (1–2 px en la mayoría de bordes);
los mayores desvíos están en los lados de la cara A de `trip82` (±11 px).

**Lectura:** la celosía real está a unos 20–34 cm del plano del muro, no a
9 cm, bajo los supuestos anteriores. El ancho y el eje del vano difieren del
modelo en magnitudes comparables al residuo y no se dan por medidos. El
derrame (hn − h) no se resuelve.

## Comprobaciones

- **Segunda vía, superposición:** con las cámaras ajustadas, los vanos, las
  aristas del octógono y los alféizares del GLB caen sobre los de ambas
  fotos (`renders/previas/0041_*/superposicion.jpg`). El render recorta lo
  que está a menos de 3 m porque las cámaras quedan tras el muro de la sala
  del modelo, que no tiene hueco de puerta.
- **Altura de la cámara** (no impuesta; cota del alféizar de
  `datos/alzado_sala.json`): 1,37 m (`bruchez`) y 2,03 m (`trip82`) sobre el
  suelo. La primera es una altura de mano normal; la segunda, alta.
- **Posición:** ambas cámaras en x ≈ −4,4 y −5,0 m, fuera del cuadrado de la
  sala, compatibles con fotos tomadas desde el arco de entrada.

## Intentos descartados

Con una sola foto (`trip82`), d variaba entre 0,07 y 0,40 m según la cara
quitada. Añadir distorsión radial no redujo el residuo (7,6 → 7,1 px) y llevó
la cámara bajo el suelo. Se conserva la opción `--distorsion` en
`scripts/medir_nicho_fotos.py`, desactivada por defecto.

## Alcance

No se contrasta el vuelo de 32,05 cm de las hiladas (0038): este método mide
el nicho, no los mocárabes de encima. No se modifica el GLB. Ahondar el
nicho del modelo a unos 0,30 m queda como propuesta para decidir; exigiría
rehacer el paño 00 y los otros siete, y el remate escalonado del nicho que
muestran las fotos tampoco existe en el modelo.

## Reproducción

```bash
.venv/bin/python scripts/registrar_fotos_tambor.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/detectar_celosias.py --lecturas datos/lecturas_trip82.json
OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/detectar_celosias.py --lecturas datos/lecturas_bruchez.json
OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/medir_nicho_fotos.py trip82 bruchez
~/.local/opt/blender/blender -b --python-exit-code 1 -P scripts/superponer_camaras_fotos.py
```

El ajuste conjunto con variantes tarda varios minutos. Las
láminas de `renders/previas/0041_*/` no se versionan.
