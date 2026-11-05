#!/usr/bin/env python3
"""Monta una hilada A1/A2 en anillo y la renderiza.

Salidas: `renders/hilada_a1a2.obj` y `renders/hilada_a1a2.png` (vista oblicua
desde abajo y vista en perspectiva desde dentro del anillo). Supuestos en `granada/hilada.py`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.hilada import PIEZAS_POR_VUELTA, hilada  # noqa: E402
from granada.piezas import escribir_obj  # noqa: E402
from granada.render3d import rasterizar  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--piezas", type=int, default=PIEZAS_POR_VUELTA)
    ap.add_argument("--lado", type=int, default=1000)
    ap.add_argument("--obj", type=Path, default=RAIZ / "renders" / "hilada_a1a2.obj")
    ap.add_argument("--png", type=Path, default=RAIZ / "renders" / "hilada_a1a2.png")
    args = ap.parse_args()

    grupos = hilada(args.piezas)
    escribir_obj(args.obj, grupos)
    V, F = [], []
    for _, Vg, Fg in grupos:
        base = len(V)
        V.extend(Vg)
        F.extend((a + base, b + base, c + base) for a, b, c in Fg)

    L = args.lado
    luces = [((-0.4, 0.5, -0.75), 0.7), ((0.5, -0.3, -0.6), 0.3)]
    oblicua, _ = rasterizar(V, F, L, L, azim=0.0, elev=-28.0, luces=luces)
    # Ojo de un visitante bajo la hilada, mirando al lado opuesto del anillo.
    ojo = ((0.0, -2.5, -4.0), (0.0, 6.5, 1.6), 75.0)
    cerca, _ = rasterizar(V, F, L, L, luces=luces, perspectiva=ojo)
    lienzo = Image.new("RGB", (2 * L, L))
    lienzo.paste(oblicua, (0, 0))
    lienzo.paste(cerca, (L, 0))
    lienzo.save(args.png)
    print(f"{args.piezas} piezas, {len(V)} vertices, {len(F)} triangulos -> {args.png.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
