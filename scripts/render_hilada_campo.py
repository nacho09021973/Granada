"""Monta unas pocas hiladas del modelo por campo de alturas y las renderiza.

Decision 0017, paso 3: comprobar a ojo como se colocan las piezas a lo largo
de una curva de nivel cualquiera (esquinas concavas, lazos) antes de montar la
cupula entera. Rasterizador propio (granada/render3d.py), en yeso.

Uso:
    .venv/bin/python scripts/render_hilada_campo.py [--A 2] [--hiladas 6,10] \
        [--png renders/previas/hilada_campo.png]

Salida: dos vistas en un PNG, cenital desde abajo a la izquierda y oblicua a
la derecha, y el recuento de frentes y piezas por hilada.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.campo import campo  # noqa: E402
from granada.hiladas_campo import frentes, hilada_de, montar  # noqa: E402
from granada.render3d import rasterizar  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--A", type=float, default=2.0)
    ap.add_argument("--forma", default="lineal")
    ap.add_argument("--signo", type=int, default=1)
    ap.add_argument("--hiladas", default="6,10", help="indices j, o 'todas'")
    ap.add_argument("--lado", type=int, default=1000)
    ap.add_argument("--png", type=Path, default=RAIZ / "renders" / "previas" / "hilada_campo.png")
    a = ap.parse_args()

    c = campo(A=a.A, forma=a.forma, signo=a.signo)
    todos = frentes(c)
    if a.hiladas == "todas":
        sel = todos
    else:
        quiero = {int(j) for j in a.hiladas.split(",")}
        sel = [f for f in todos if f.indice in quiero]
    for j in sorted({f.indice for f in sel}):
        fs = [f for f in sel if f.indice == j]
        print(f"hilada {j:2d}: {len(fs):3d} frentes, {sum(hilada_de(f).piezas for f in fs):5d} piezas")
    grupos = montar(c, sel)
    V, F = [], []
    for _, Vg, Fg, *_ in grupos:
        base = len(V)
        V.extend(Vg)
        F.extend((p + base, q + base, r + base) for p, q, r in Fg)

    luces = [((0.55, 0.35, -0.75), 0.75), ((-0.6, -0.45, -0.65), 0.3)]
    L = a.lado
    abajo, _ = rasterizar(V, F, L, L, supermuestreo=2, luces=luces, perspectiva=((0.0, 0.0, -13.0), (0.0, 0.001, 10.0), 90.0))
    oblicua, _ = rasterizar(V, F, L, L, supermuestreo=2, luces=luces, perspectiva=((0.0, -9.0, -9.0), (0.0, 2.0, 4.0), 70.0))
    lienzo = Image.new("RGB", (2 * L, L))
    lienzo.paste(abajo, (0, 0))
    lienzo.paste(oblicua, (L, 0))
    a.png.parent.mkdir(parents=True, exist_ok=True)
    lienzo.save(a.png)
    print(f"{len(F)} triangulos -> {a.png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
