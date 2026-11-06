"""Controles de la hilada A1/A2 de `granada.hilada`."""

import math

import pytest

from granada.hilada import PIEZAS_POR_VUELTA, colocar, hilada, radio_frente
from granada.piezas import R2, pieza


@pytest.mark.parametrize("s", [i / 20 * R2 for i in range(21)])
def test_a1_y_a2_casan_en_el_cateto_comun(s):
    """A1 centrada en x=0 y A2 con su vertice en x=R2 comparten el cateto
    (R2, 0)-(0, -R2). El fondo de las dos coincide a lo largo de el."""
    a1, a2 = pieza("A1"), pieza("A2")
    x, y = R2 - s, -s
    assert a1.fondo(x, y) == pytest.approx(a2.fondo(x - R2, y), abs=1e-12)


def test_la_vuelta_cierra_y_respeta_el_orden_8():
    assert PIEZAS_POR_VUELTA % 16 == 0
    assert radio_frente() == pytest.approx(PIEZAS_POR_VUELTA * R2 / (2 * math.pi))


def test_colocar_pone_el_frente_en_el_radio():
    (p,) = colocar([(0.0, 0.0, 0.0)], math.pi / 3, 5.0)
    assert math.hypot(p[0], p[1]) == pytest.approx(5.0)


def test_hilada_tiene_las_piezas_y_la_losa():
    nombres = [g[0] for g in hilada(16, subdivision=4)]
    assert sum(n.startswith("A1") for n in nombres) == 8
    assert sum(n.startswith("A2") for n in nombres) == 8
    assert nombres[-1] == "losa"
