"""Controles del color de la cupula por piezas."""

from collections import Counter

import pytest

from granada.color import PALETA, colorear, rgb
from granada.cupula import cupula
from granada.piezas import TIPOS, etiquetas, malla, pieza


@pytest.mark.parametrize("tipo", TIPOS)
def test_etiquetas_cubren_la_malla_con_n2_de_tapa_y_de_fondo(tipo):
    p = pieza(tipo)
    n = 6
    V, F = malla(p, n)
    e = Counter(etiquetas(p, V, F))
    triangulos_planta = len(p.planta) - 2
    assert e["tapa"] == e["fondo"] == triangulos_planta * n * n
    assert e["pared"] == len(p.planta) * n * 2
    assert sum(e.values()) == len(F)


def test_las_paredes_y_tapas_son_yeso_y_los_fondos_pigmento():
    assert colorear("A1", "pared", 3, 0) == "yeso"
    assert colorear("A2", "tapa", 3, 0) == "yeso"
    assert colorear("A3", "fondo", 3, 0) == "oro"
    assert {colorear(t, "fondo", h, 0) for t in ("A1", "A2", "C1") for h in range(3)} == {"azul", "rojo", "verde"}


def test_paleta_es_hex_valido():
    for nombre in PALETA:
        assert all(0 <= c <= 255 for c in rgb(nombre))


def test_cupula_coloreada_tiene_un_color_por_triangulo():
    _, grupos = cupula(subdivision=2, color=True)
    for nombre, V, F, C in grupos:
        assert len(C) == len(F), nombre
        assert set(C) <= set(PALETA), nombre
