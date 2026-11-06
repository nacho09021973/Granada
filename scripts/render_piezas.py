#!/usr/bin/env python3
"""Modela los siete prismas de Jones y Goury y los renderiza en fila.

Salidas:
- `renders/piezas_alfabeto.obj`: las siete piezas, un grupo por tipo, en fila;
- `renders/piezas_alfabeto.png`: dos filas, vista frontal en tres cuartos
  (como el grabado) y vista desde abajo (como se ven en la cupula).

Se compara a ojo con la fig. 5 del articulo de Gamiz Gordo y Ferrer (pagina 15
del PDF). La geometria y sus supuestos estan en `granada/piezas.py`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.piezas import TIPOS, NIVELES, escribir_obj, malla, pieza  # noqa: E402
from granada.render3d import rasterizar  # noqa: E402

SEPARACION = 2.1


def construir():
    grupos, Vt, Ft = [], [], []
    for k, tipo in enumerate(TIPOS):
        V, F = malla(pieza(tipo))
        dx = (k - (len(TIPOS) - 1) / 2) * SEPARACION
        V = [(x + dx, y, z) for x, y, z in V]
        grupos.append((tipo, V, F))
        base = len(Vt)
        Vt.extend(V)
        Ft.extend((a + base, b + base, c + base) for a, b, c in F)
    return grupos, Vt, Ft


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ancho", type=int, default=1800)
    ap.add_argument("--obj", type=Path, default=RAIZ / "renders" / "piezas_alfabeto.obj")
    ap.add_argument("--png", type=Path, default=RAIZ / "renders" / "piezas_alfabeto.png")
    args = ap.parse_args()

    grupos, V, F = construir()
    escribir_obj(args.obj, grupos)

    W = args.ancho
    H = W * 2 // 5
    luces = [((-0.6, 0.8, 0.5), 0.7), ((0.7, 0.5, -0.4), 0.3)]
    frontal, _ = rasterizar(V, F, W, H, azim=-18.0, elev=14.0, luces=luces)
    luces_abajo = [((-0.5, 0.6, -0.7), 0.7), ((0.6, 0.3, -0.6), 0.3)]
    abajo, _ = rasterizar(V, F, W, H, azim=-10.0, elev=-62.0, luces=luces_abajo)

    lienzo = Image.new("RGB", (W, 2 * H + 40), (20, 19, 20))
    lienzo.paste(frontal, (0, 0))
    lienzo.paste(abajo, (0, H + 40))
    dibujo = ImageDraw.Draw(lienzo)
    try:
        fuente = ImageFont.truetype("DejaVuSans.ttf", 26)
        pequena = ImageFont.truetype("DejaVuSans.ttf", 18)
    except OSError:
        fuente = pequena = ImageFont.load_default()
    for k, tipo in enumerate(TIPOS):
        cx = int(W * (0.06 + 0.88 * (k + 0.5) / len(TIPOS)))
        dibujo.text((cx, H + 8), tipo, fill=(230, 220, 200), font=fuente, anchor="mt")
        etiqueta = "2 niveles" if NIVELES[tipo] == 2 else "1 nivel"
        dibujo.text((cx, 2 * H + 30), etiqueta, fill=(150, 145, 135), font=pequena, anchor="mb")
    args.png.parent.mkdir(parents=True, exist_ok=True)
    lienzo.save(args.png)
    print(f"{len(V)} vertices, {len(F)} triangulos -> {args.obj.name}, {args.png.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
