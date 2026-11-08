"""Recuento de piezas de la cupula por celdas para cada (cierre, escala).

ESCALA_CELDA se calibra para que el total de piezas de las 105 celdas sea el de
Jones y Goury, 5416 (docs/fuentes.md, entrada 18). CIERRE_CELDA decide cuando
una celda deja de recibir hiladas y se tapa con su cupulilla; bajarlo mete mas
hiladas y obliga a recalibrar la escala. Este script da la tabla con la que se
eligen los dos (granada/celdas.py).

Uso:
    .venv/bin/python scripts/calibrar_escala_celda.py \
        [--cierres 0.9,0.5,0.3] [--escalas 0.475,0.5,0.525,0.55]

Por cada par imprime: piezas, celdas sin hiladas y la fraccion media del radio
de la celda que ocupa la cupulilla de cierre.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from granada.celdas import MULTIPLO_CELDA, celdas_de_la_red
from granada.cupula import PlantaPoligono, plan_de_hiladas, radios_desde

OBJETIVO = 5416


def recuento(cierre: float, escala: float, celdas) -> tuple[int, int, float]:
    piezas = vacias = 0
    fracciones = []
    for c in celdas:
        if c.orbita == "esquina":
            continue
        cx, cy = c.centro
        cg, sg = math.cos(-c.giro), math.sin(-c.giro)
        P = np.asarray(c.poligono) - np.array([cx, cy])
        L = np.stack([P[:, 0] * cg - P[:, 1] * sg, P[:, 0] * sg + P[:, 1] * cg], axis=1) / escala
        rho = radios_desde(L, np.zeros(2))
        F0 = float(rho.mean())
        h = plan_de_hiladas(F0, planta=PlantaPoligono(tuple(rho.tolist()), F0, cierre), cierre=cierre, multiplo=MULTIPLO_CELDA)
        piezas += sum(x.piezas for x in h)
        vacias += not h
        fracciones.append((h[-1].radio_frente if h else F0) / F0)
    return piezas, vacias, float(np.mean(fracciones))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cierres", default="0.9,0.6,0.4,0.3")
    ap.add_argument("--escalas", default="0.475,0.5,0.525,0.55,0.575,0.6")
    a = ap.parse_args()
    celdas = celdas_de_la_red()
    print("cierre escala piezas desvio_% celdas_sin_hiladas fraccion_cierre")
    for cierre in map(float, a.cierres.split(",")):
        for escala in map(float, a.escalas.split(",")):
            n, v, f = recuento(cierre, escala, celdas)
            print(f"{cierre:.2f} {escala:.3f} {n:5d} {100 * (n - OBJETIVO) / OBJETIVO:+6.1f} {v:3d} {f:.2f}")


if __name__ == "__main__":
    main()
