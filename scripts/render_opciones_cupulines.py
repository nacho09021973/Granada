#!/usr/bin/env python3
"""Compara dos acabados de los cupulines, en vista cenital desde el centro.

- A: cupulines con el mismo yeso que el resto (render por defecto).
- B: cupulines oscurecidos al `TONO_OSCURO` de su color, como se ven en la
  ortoimagen de AA-415_23. Es un tono puesto a mano, no sombra calculada.

Salida: `renders/opciones_cupulines.png`. Malla de `granada/cupula.py`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.cupula import cupula  # noqa: E402
from granada.render3d import rasterizar  # noqa: E402

TONO_OSCURO = 0.4
LUCES = [((0.55, 0.35, -0.75), 0.75), ((-0.6, -0.45, -0.65), 0.3)]
CENITAL = ((0.0, 0.0, -13.0), (0.0, 0.001, 10.0), 90.0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lado", type=int, default=1000)
    ap.add_argument("--png", type=Path, default=RAIZ / "renders" / "opciones_cupulines.png")
    args = ap.parse_args()

    _, grupos = cupula()
    V, F, tono = [], [], []
    for nombre, Vg, Fg in grupos:
        base = len(V)
        V.extend(Vg)
        F.extend((a + base, b + base, c + base) for a, b, c in Fg)
        tono.extend([TONO_OSCURO if nombre.startswith("cupulin_") else 1.0] * len(Fg))

    L = args.lado
    a, _ = rasterizar(V, F, L, L, luces=LUCES, perspectiva=CENITAL)
    b, _ = rasterizar(V, F, L, L, luces=LUCES, perspectiva=CENITAL, tono=tono)
    lienzo = Image.new("RGB", (2 * L, L + 50), (20, 19, 20))
    lienzo.paste(a, (0, 50))
    lienzo.paste(b, (L, 50))
    dibujo = ImageDraw.Draw(lienzo)
    try:
        fuente = ImageFont.truetype("DejaVuSans.ttf", 30)
    except OSError:
        fuente = ImageFont.load_default()
    color = (235, 225, 205)
    dibujo.text((L // 2, 25), "A · cupulines claros (actual)", fill=color, font=fuente, anchor="mm")
    dibujo.text((L + L // 2, 25), "B · cupulines oscuros (como en la foto)", fill=color, font=fuente, anchor="mm")
    lienzo.save(args.png)
    print(f"-> {args.png.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
