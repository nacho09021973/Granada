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


def test_domina_el_yeso_y_el_color_va_en_las_celdillas_arqueadas():
    assert colorear("A1", "pared", 3, 0) == "yeso"
    assert colorear("A2", "tapa", 3, 0) == "yeso"
    assert colorear("A1", "fondo", 3, 0) == "yeso"
    assert colorear("A3", "fondo", 3, 0) == "oro"
    assert {colorear("A2", "fondo", h, 0) for h in range(6)} == {"azul", "almagra", "verde", "yeso"}


def test_los_tonos_son_los_medidos():
    import colorsys
    from granada.color import LIMPIEZA, MEDIDOS

    for nombre in LIMPIEZA:
        medido = [int(MEDIDOS[nombre][i:i + 2], 16) / 255 for i in (1, 3, 5)]
        limpio = [c / 255 for c in rgb(nombre)]
        h0 = colorsys.rgb_to_hsv(*medido)[0]
        h1 = colorsys.rgb_to_hsv(*limpio)[0]
        assert abs(h0 - h1) < 0.01, nombre


def test_paleta_es_hex_valido():
    for nombre in PALETA:
        assert all(0 <= c <= 255 for c in rgb(nombre))


def test_cupula_coloreada_tiene_un_color_por_triangulo():
    _, grupos = cupula(subdivision=2, color=True)
    for nombre, V, F, C, S in grupos:
        assert len(C) == len(F) == len(S), nombre
        assert set(C) <= set(PALETA), nombre
        assert all(0 < s <= 1 for s in S), nombre
