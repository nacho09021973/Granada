"""El borde opcional se contrasta con el cono y con dominio e interior."""
import numpy as np
import pytest

from granada.campo import PASO_VERTICAL, campo
from granada.cupula import PENDIENTE, RADIO_BASE
from scripts.diagnosticar_arranque_campo import diagnosticar


def test_arranque_circular_del_cono_frente_a_formula_analitica():
    c = campo(A=0, borde="circular")
    X, Y = np.meshgrid(c.x, c.y)
    assert np.allclose(c.H, (RADIO_BASE-np.hypot(X, Y))*PENDIENTE)
    r = diagnosticar(c, muestras=33, capas=40)
    assert r["contornos_H0"] == r["frentes_primera_fila"] == 1
    assert r["error_radio_contorno_H0_max_m"] < c.paso*.01
    b = r["bandas"][0]
    assert b["aumentan_H"] == b["triangulos_invertidos"] == 0
    assert b["extremos_fuera_radio_tolerancia_1e_9"] == 0


def test_atenuacion_respeta_interior_y_cono_exterior():
    libre = campo(A=2)
    c = campo(A=2, borde="circular")
    X, Y = np.meshgrid(c.x, c.y)
    radio = np.hypot(X, Y)
    interior = radio <= RADIO_BASE-PASO_VERTICAL/PENDIENTE
    exterior = radio >= RADIO_BASE
    assert np.array_equal(c.H[interior], libre.H[interior])
    assert np.allclose(c.H[exterior], ((RADIO_BASE-radio)*PENDIENTE)[exterior])
    assert np.array_equal(campo(A=2, borde="libre").H, libre.H)


def test_borde_desconocido_falla():
    with pytest.raises(ValueError):
        campo(borde="otro")


def test_borde_octogonal_arranca_en_el_octogono_de_la_cornisa():
    import math
    from granada.campo import RADIO_BASE, curvas
    from granada.cupula import _MEDIA_OCT
    c = campo(A=0, borde="octogonal")
    (P,) = [Q for Q in curvas(c, 1e-6) if len(Q) > 100][:1]
    r = np.hypot(P[:, 0], P[:, 1])
    apotema = RADIO_BASE / _MEDIA_OCT
    # La curva H = 0 recorre el octogono: entre la apotema y el vertice.
    assert abs(r.min() - apotema) < 0.1
    assert abs(r.max() - apotema / math.cos(math.pi / 8)) < 0.1
    # Hacia la clave el campo vuelve al cono circular.
    X, Y = np.meshgrid(c.x, c.y)
    cerca = np.hypot(X, Y) < 2
    cono = (RADIO_BASE - np.hypot(X, Y)) * PENDIENTE
    assert np.abs(c.H[cerca] - cono[cerca]).max() < 0.1
