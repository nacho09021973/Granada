"""Controles de la cupula por piezas sobre la red de medinas (granada/celdas.py)."""

import json
import math

import numpy as np
import pytest

from granada.celdas import (
    REGISTRO,
    PlantaPoligono,
    celdas_de_la_red,
    centro_del_nucleo,
    cupula_red,
    radios_desde,
)


@pytest.fixture(scope="module")
def red():
    return cupula_red(subdivision=2, color=True)


def test_hay_una_celda_por_cara_y_todas_son_estrelladas_en_su_centro():
    celdas = celdas_de_la_red()
    assert len(celdas) == 105
    for c in celdas:
        P = np.asarray(c.poligono)
        r = radios_desde(P, np.asarray(c.centro))
        assert np.isfinite(r).all() and (r > 0).all(), c.id


def test_la_planta_de_celda_reproduce_el_contorno():
    P = np.array([(0.0, 0.0), (4.0, 0.0), (4.0, 2.0), (2.0, 3.0), (0.0, 2.0)])
    c = centro_del_nucleo(P)
    rho = radios_desde(P, c)
    pl = PlantaPoligono(tuple(rho.tolist()), float(rho.mean()), 0.5)
    phi = np.linspace(0, 2 * math.pi, 50, endpoint=False)
    x, y = pl.punto(phi, np.full_like(phi, pl.radio_base))
    # Cada punto del contorno de la planta esta sobre un lado del poligono.
    for px, py in zip(x + c[0], y + c[1]):
        d = min(
            abs((b[0] - a[0]) * (a[1] - py) - (a[0] - px) * (b[1] - a[1])) / math.dist(a, b)
            for a, b in zip(P, np.roll(P, -1, axis=0))
        )
        assert d < 0.02


def test_el_recuento_de_piezas_es_el_de_jones_y_goury(red):
    resumen, _ = red
    assert abs(sum(r["piezas"] for r in resumen) - 5416) / 5416 < 0.03


def test_un_color_por_triangulo(red):
    _, grupos = red
    for g in grupos:
        assert len(g[3]) == len(g[2]) == len(g[4]), g[0]


def test_registro_deja_los_cupulines_en_los_entrantes():
    r = json.loads(REGISTRO.read_text(encoding="utf-8"))
    assert r["giro_grados"] == 0.0
    c = r["comprobacion_cupulines"]
    assert c["fuera_de_la_red"] == c["dentro_del_octogono"] == c["de"] == 16
    assert abs(c["fase_de_los_entrantes_grados"] - c["fase_de_los_cupulines_grados"]) < 1.0
