"""Curvas de nivel del campo de alturas de la decision 0017, para varios A.

Para cada (A, forma, signo) imprime cuantas curvas salen en cada cota de hilada
(1 = anillo continuo; mas = la hilada se parte en lazos que cierran solos) y
dibuja las curvas sobre la red registrada en un PNG.

Uso:
    .venv/bin/python scripts/curvas_de_nivel.py [--A 0,1,1.5,2,3] \
        [--forma lineal] [--signo 1] [--salida renders/previas]

Salida: <salida>/curvas_<forma>_s<signo>_A<A>.png, una por valor de A.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.campo import aristas_de_la_red, campo, cotas_de_hilada, curvas, es_cerrada  # noqa: E402
from granada.cupula import RADIO_BASE  # noqa: E402

LADO = 1400


def dibujar(c, por_cota, ruta: Path) -> None:
    im = Image.new("RGB", (LADO, LADO), (250, 248, 242))
    dr = ImageDraw.Draw(im)
    escala = LADO / (2.05 * RADIO_BASE)

    def px(P):
        return [(LADO / 2 + x * escala, LADO / 2 - y * escala) for x, y in P]

    for p, q in aristas_de_la_red():
        dr.line(px([p, q]), fill=(190, 190, 190), width=1)
    n = len(por_cota)
    for k, cs in enumerate(por_cota):
        t = k / max(1, n - 1)
        color = (int(40 + 180 * t), int(80 * (1 - t)), int(200 * (1 - t)))
        for P in cs:
            dr.line(px(P), fill=color, width=2)
    dr.text((12, 12), f"A = {c.A}  forma = {c.forma}  signo = {c.signo:+d}", fill=(0, 0, 0))
    im.save(ruta)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--A", default="0,1,1.5,2,3")
    ap.add_argument("--forma", default="lineal")
    ap.add_argument("--signo", type=int, default=1)
    ap.add_argument("--salida", type=Path, default=RAIZ / "renders" / "previas")
    a = ap.parse_args()
    a.salida.mkdir(parents=True, exist_ok=True)
    cotas = cotas_de_hilada()
    print("A      curvas por cota (hilada 1 .. 22)                    abiertas")
    for A in map(float, a.A.split(",")):
        c = campo(A=A, forma=a.forma, signo=a.signo)
        por_cota = [curvas(c, z) for z in cotas]
        abiertas = sum(not es_cerrada(P) for cs in por_cota for P in cs)
        print(f"{A:<6g} {' '.join(f'{len(cs):2d}' for cs in por_cota)}   {abiertas}")
        dibujar(c, por_cota, a.salida / f"curvas_{a.forma}_s{a.signo:+d}_A{A:g}.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
