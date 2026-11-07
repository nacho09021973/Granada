"""Une en una sola imagen los cuatro cuadrantes de un render hecho por partes.

render_cycles.py puede renderizar una parte del fotograma (--recorte). Para
16384 px se hace en cuatro cuadrantes de 8192 px, porque el fotograma entero,
con los pases del eliminador de ruido, puede pasar de 10 GB de memoria.

Uso:
    python3 scripts/unir_cuadrantes.py SALIDA.png SI.png SD.png II.png ID.png
(superior izquierdo, superior derecho, inferior izquierdo, inferior derecho)
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def main() -> int:
    if len(sys.argv) != 6:
        print(__doc__)
        return 2
    salida, *partes = (Path(p) for p in sys.argv[1:])
    imgs = [Image.open(p) for p in partes]
    w, h = imgs[0].size
    if any(im.size != (w, h) for im in imgs):
        raise SystemExit(f"cuadrantes de tamanos distintos: {[im.size for im in imgs]}")
    lienzo = Image.new(imgs[0].mode, (2 * w, 2 * h))
    for im, (x, y) in zip(imgs, ((0, 0), (w, 0), (0, h), (w, h))):
        lienzo.paste(im, (x, y))
    lienzo.save(salida)
    print(f"-> {salida} ({2 * w} x {2 * h})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
