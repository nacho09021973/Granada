"""La rebaja debe conservar contorno, planta y límite sin corrección."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from corregir_alturas_alzado import rebajar_casquete
from reducir_saliente_cupulines import transformar


def parche():
    v = np.array([(x * .1, y * .1, 2 + .03 * x - .05 * y) for y in range(3) for x in range(3)])
    v[4, 2] += 1
    f = np.array([(i, i + 1, i + 4) for i in (0, 1, 3, 4)] + [(i, i + 4, i + 3) for i in (0, 1, 3, 4)])
    return v, f


def test_baja_el_bulto_sobre_la_base_inclinada_sin_mover_su_borde():
    v, f = parche()
    p, _ = rebajar_casquete(v, f, .45)
    assert np.array_equal(v[:, :2], p[:, :2])
    assert np.array_equal(v[np.arange(9) != 4], p[np.arange(9) != 4])
    assert p[4, 2] == pytest.approx(2 + .03 - .05 + .45)


def test_factor_uno_es_la_geometria_original_y_cero_es_la_base():
    v, f = parche()
    p, _ = rebajar_casquete(v, f, 1)
    assert np.array_equal(p, v)
    p, _ = rebajar_casquete(v, f, 0)
    assert p[4, 2] == pytest.approx(2 + .03 - .05)


def test_el_pozo_se_acorta_sin_mover_boca_y_marco():
    eje = np.array([.5, 0, np.sqrt(.75)])
    e1 = np.array([0, 1, 0])
    e2 = np.cross(eje, e1)
    phi = np.arange(16) * 2 * np.pi / 16
    base = .25 * (np.cos(phi)[:, None] * e1 + np.sin(phi)[:, None] * e2)
    v = np.vstack([base, base + .6 * eje])
    p, d = transformar(v, base, eje, .3)
    assert np.allclose(p[:16], base)
    assert np.allclose(p[16:], base + .3 * eje)
    assert d["reduccion_eje_m"] == pytest.approx(.3)
