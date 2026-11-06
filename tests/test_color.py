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
    from granada.color import LIMPIEZA, MEDIDOS, PALETA_LIMPIA

    for nombre in LIMPIEZA:
        medido = [int(MEDIDOS[nombre][i:i + 2], 16) / 255 for i in (1, 3, 5)]
        limpio = [int(PALETA_LIMPIA[nombre][i:i + 2], 16) / 255 for i in (1, 3, 5)]
        h0 = colorsys.rgb_to_hsv(*medido)[0]
        h1 = colorsys.rgb_to_hsv(*limpio)[0]
        assert abs(h0 - h1) < 0.01, nombre


def test_la_paleta_por_defecto_es_la_de_la_fotografia():
    import json

    from granada.color import ACENTOS, PESOS_DISPERSO

    d = json.loads(ACENTOS.read_text(encoding="utf-8"))
    bandas = d["por_umbral"]["S>=0.20 V>=0.28"]["bandas"]
    assert PALETA["yeso"] == d["yeso"]["mediana_cuartil_claro"]
    assert PALETA["verde"] == bandas["verde"]["mediana"]
    assert PALETA["almagra"] == bandas["tierra"]["mediana"]
    assert PESOS_DISPERSO["azul"] == bandas["azul"]["peso"]


def test_paleta_es_hex_valido():
    for nombre in PALETA:
        assert all(0 <= c <= 255 for c in rgb(nombre))


def test_cupula_coloreada_tiene_un_color_por_triangulo():
    _, grupos = cupula(subdivision=2, color=True)
    for nombre, V, F, C, S in grupos:
        assert len(C) == len(F) == len(S), nombre
        assert set(C) <= set(PALETA), nombre
        assert all(0 < s <= 1 for s in S), nombre


def test_disperso_solo_pinta_fondos_y_respeta_c8():
    from granada.color import PESOS_DISPERSO, disperso

    por_sector = {0: 18}
    pintar = disperso(por_sector)
    assert pintar("A2", "tapa", 0, 5) == "yeso"
    assert pintar("A2", "pared", 0, 5) == "yeso"
    colores = [pintar("A2", "fondo", 0, i) for i in range(18 * 8)]
    assert set(colores) <= set(PESOS_DISPERSO) | {"yeso"}
    # Cada pieza y su homologa en los otros siete sectores llevan el mismo color.
    for i in range(18):
        assert len({colores[i + 18 * k] for k in range(8)}) == 1


def test_disperso_es_determinista_y_domina_el_yeso():
    from granada.color import PROBABILIDAD_DISPERSO, disperso

    pintar = disperso({h: 1000 for h in range(18)})
    muestra = [pintar("A2", "fondo", h, i) for h in range(18) for i in range(1000)]
    assert muestra == [pintar("A2", "fondo", h, i) for h in range(18) for i in range(1000)]
    pintadas = sum(c != "yeso" for c in muestra) / len(muestra)
    assert abs(pintadas - PROBABILIDAD_DISPERSO) < 0.02


def test_cupula_admite_los_dos_repartos():
    for reparto in ("disperso", "anillos"):
        _, grupos = cupula(subdivision=2, color=True, reparto=reparto)
        assert all(len(g[3]) == len(g[2]) for g in grupos)
    with pytest.raises(ValueError):
        cupula(subdivision=2, color=True, reparto="otro")
