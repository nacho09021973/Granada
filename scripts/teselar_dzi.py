#!/usr/bin/env python3
"""Corta una imagen grande en teselas Deep Zoom (DZI) para el visor web.

Uso:

    python3 scripts/teselar_dzi.py renders/cupula_cycles_cenital_8k.png \
        web/zoom/cupula_cenital

Escribe `<destino>.dzi` (descriptor XML) y `<destino>_files/<nivel>/<col>_<fila>.jpg`,
el formato que lee OpenSeadragon: el nivel mas alto es la imagen entera y
cada nivel inferior la mitad de lado, hasta 1 x 1 pixel. Solo Pillow.
"""

from __future__ import annotations

import argparse
import math
import shutil
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # imagenes propias de varios cientos de megapixeles


def teselar(origen: Path, destino: Path, tesela: int = 254, solape: int = 1, calidad: int = 90) -> int:
    imagen = Image.open(origen).convert("RGB")
    ancho, alto = imagen.size
    niveles = math.ceil(math.log2(max(ancho, alto))) + 1
    carpeta = destino.parent / f"{destino.name}_files"
    if carpeta.exists():
        shutil.rmtree(carpeta)
    total = 0
    actual = imagen
    for nivel in range(niveles - 1, -1, -1):
        escala = 2 ** (niveles - 1 - nivel)
        w, h = max(1, math.ceil(ancho / escala)), max(1, math.ceil(alto / escala))
        if actual.size != (w, h):
            actual = actual.resize((w, h), Image.LANCZOS)
        dir_nivel = carpeta / str(nivel)
        dir_nivel.mkdir(parents=True)
        for col in range(math.ceil(w / tesela)):
            for fila in range(math.ceil(h / tesela)):
                x0 = max(0, col * tesela - solape)
                y0 = max(0, fila * tesela - solape)
                x1 = min(w, (col + 1) * tesela + solape)
                y1 = min(h, (fila + 1) * tesela + solape)
                actual.crop((x0, y0, x1, y1)).save(dir_nivel / f"{col}_{fila}.jpg", quality=calidad, optimize=True)
                total += 1
    destino.with_suffix(".dzi").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<Image xmlns="http://schemas.microsoft.com/deepzoom/2008" TileSize="{tesela}" '
        f'Overlap="{solape}" Format="jpg">\n'
        f'  <Size Width="{ancho}" Height="{alto}"/>\n'
        "</Image>\n",
        encoding="utf-8",
    )
    return total


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("origen", type=Path)
    ap.add_argument("destino", type=Path, help="ruta sin extension: se crean <destino>.dzi y <destino>_files/")
    ap.add_argument("--calidad", type=int, default=90)
    args = ap.parse_args()
    args.destino.parent.mkdir(parents=True, exist_ok=True)
    n = teselar(args.origen, args.destino, calidad=args.calidad)
    peso = sum(f.stat().st_size for f in (args.destino.parent / f"{args.destino.name}_files").rglob("*.jpg"))
    print(f"{n} teselas, {peso / 1e6:.1f} MB -> {args.destino.with_suffix('.dzi')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
