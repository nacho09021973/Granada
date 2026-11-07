"""Borra las costuras de un render unido por cuadrantes con dos franjas.

unir_cuadrantes.py junta cuatro cuadrantes que el eliminador de ruido ha
limpiado por separado; en la cruz donde se tocan queda una linea tenue. Este
script pega encima dos franjas renderizadas de una sola pieza que cruzan esas
costuras (una vertical a toda altura y otra horizontal a todo ancho, centradas
en la mitad del lado), fundidas con un degradado lineal para que tampoco se
vean los bordes de las franjas.

Las franjas se renderizan con render_cycles.py --recorte; para 16384 px y
franjas de 512 px:
    vertical:   --recorte 0.484375,0,0.515625,1
    horizontal: --recorte 0,0.484375,1,0.515625

Uso:
    python3 scripts/coser_franjas.py ENTRADA.png VERTICAL.png HORIZONTAL.png SALIDA.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

PLENO = 96  # px a cada lado de la costura donde manda la franja entera
FUNDIDO = 224  # px a cada lado donde el peso de la franja llega a 0


def pesos(n: int) -> np.ndarray:
    """Peso de la franja a lo ancho (n px, costura en el centro)."""
    d = np.abs(np.arange(n) + 0.5 - n / 2)
    return np.clip((FUNDIDO - d) / (FUNDIDO - PLENO), 0.0, 1.0)


def main() -> int:
    if len(sys.argv) != 5:
        print(__doc__)
        return 2
    entrada, vertical, horizontal, salida = (Path(p) for p in sys.argv[1:])
    base = Image.open(entrada)
    modo = base.mode
    img = np.asarray(base, dtype=np.float32)
    del base
    alto, ancho = img.shape[:2]

    v = np.asarray(Image.open(vertical).convert(modo), dtype=np.float32)
    if v.shape[0] != alto:
        raise SystemExit(f"franja vertical de alto {v.shape[0]}, la imagen tiene {alto}")
    nv = v.shape[1]
    x0 = ancho // 2 - nv // 2
    w = pesos(nv)[None, :, None]
    img[:, x0:x0 + nv] = img[:, x0:x0 + nv] * (1 - w) + v * w
    del v

    h = np.asarray(Image.open(horizontal).convert(modo), dtype=np.float32)
    if h.shape[1] != ancho:
        raise SystemExit(f"franja horizontal de ancho {h.shape[1]}, la imagen tiene {ancho}")
    nh = h.shape[0]
    y0 = alto // 2 - nh // 2
    w = pesos(nh)[:, None, None]
    # En el cruce la franja horizontal tiene su propio fondo sin costura
    # vertical, asi que puede ir encima de la vertical sin reintroducirla.
    img[y0:y0 + nh] = img[y0:y0 + nh] * (1 - w) + h * w
    del h

    Image.fromarray(np.clip(img + 0.5, 0, 255).astype(np.uint8), modo).save(salida)
    print(f"-> {salida} ({ancho} x {alto}), franjas de {nv} y {nh} px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
