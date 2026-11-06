"""Controles del color de la cupula por piezas."""

from collections import Counter

import pytest

from granada.color import PALETA, colorear, rgb
from granada.cupula import cupula
from granada.piezas import TIPOS, etiquetas, malla, pieza


@pytest.mark.parametrize("tipo", TIPOS)
def test_etiquetas_cubren_la_malla_y_tapa_y_fondo_casan(tipo):
    p = pieza(tipo)
    V, F = malla(p, 6)
    e = Counter(etiquetas(p, V, F))
    # Tapa y fondo son la misma triangulacion de la planta a dos cotas.
    assert e["tapa"] == e["fondo"] > 0
    # Cada tramo del borde levanta una pared de dos triangulos.
    assert e["pared"] > 0 and e["pared"] % 2 == 0
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
