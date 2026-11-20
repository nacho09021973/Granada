"""Generar el cupulín 00 de sustitución con la venv, desde la raíz."""

import sys
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from importlib import import_module
gc = import_module("granada.cupula")
from granada.campo import campo, PASO_VERTICAL, PENDIENTE
from scripts.render_hilada_campo import EJE_CUPULIN_CAMPO, PROFUNDIDAD_CUPULIN


def main():
    c = campo(A=3, forma="raiz", borde="octogonal")
    h = RegularGridInterpolator((c.y, c.x), c.H)
    gc.EJE_CUPULIN_GRADOS = EJE_CUPULIN_CAMPO
    q = gc.cupulines_medidos()[0]
    profundidad = PROFUNDIDAD_CUPULIN * PASO_VERTICAL / np.hypot(1, PENDIENTE)

    def z(x, y):
        return h([[y, x]]).item()

    params = dict(profundidad=profundidad, cota=z)
    original, caras, _ = gc.cupulin_estrellado(q, **params)
    v, f, _ = gc.cupulin_estrellado(q, **params, asiento_intersectado=True)
    assert f == caras
    base = np.asarray(v)[:192:2]
    error = max(abs(base[:, 2] - h(base[:, [1, 0]]))) * gc.CATETO_M
    assert error < 1e-7
    np.savez(
        "renders/previas/piloto_asiento.npz",
        original=original,
        v=v,
        centro=base.mean(axis=0),
        error_m=error,
    )


if __name__ == "__main__":
    main()
