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
