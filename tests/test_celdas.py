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
    assert abs(sum(r["piezas"] for r in resumen if not r["esquina"]) - 5416) / 5416 < 0.03


def test_las_esquinas_cubren_el_cuadrado(red):
    resumen, grupos = red
    from granada.celdas import PASO_ESQUINA_M, reticula_de_las_esquinas
    from granada.cupula import CATETO_M

    celdas, nudos, aristas = reticula_de_las_esquinas()
    # Cuatro triangulos de 43 unidades^2 en celdas de lado 0,21 m: unas 45 por esquina.
    lado = PASO_ESQUINA_M / CATETO_M
    assert 4 * 43.05 / lado**2 * 0.8 < len(celdas) < 4 * 43.05 / lado**2 * 1.2
    assert len([r for r in resumen if r["esquina"]]) == len(celdas)
    assert nudos and aristas
    assert sum(g[0].startswith("esquina_") for g in grupos) > 0


def test_las_cupulillas_de_los_cupulines_son_de_yeso():
    from granada.cupula import cupulin, cupulines_medidos

    _, _, C, _ = cupulin(cupulines_medidos()[0], 1.0, subdivision=2, colorear=lambda *a: "yeso")
    # Ni cupulilla ni marco de oro (cambio del 2026-11-07).
    assert "oro" not in C


def test_la_boca_del_cupulin_apunta_al_centro():
    from granada.cupula import PICO_CUPULIN, cupulines_medidos

    c = cupulines_medidos()[0]
    o, e1, e2, n = c.marco()
    # El eje e2 del marco apunta al centro de la cupula, y el pico va por e2.
    assert np.dot(e2[:2], -o[:2]) > 0.99 * np.linalg.norm(o[:2])
    dentro = o + 0.95 * PICO_CUPULIN * c.radio * e2
    fuera = o - 0.95 * PICO_CUPULIN * c.radio * e2
    assert c.contiene(dentro) and not c.contiene(fuera)


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


def test_hay_un_caballete_por_arista_y_una_roseta_por_nudo():
    from granada.celdas import RED, nudos_y_caballetes

    red = json.loads(RED.read_text(encoding="utf-8"))
    V, F, C, S = nudos_y_caballetes(esquinas=False)
    assert len(F) == 2 * len(red["aristas"]) + 48 * len(red["nodos"])
    assert set(C) == {"yeso"} and len(C) == len(F) == len(S)


def test_el_centro_lleva_roseta_y_triangulos_azules(red):
    from granada.celdas import caras_del_centro

    centro, azules = caras_del_centro()
    assert centro == "c042" and len(azules) == 8
    _, grupos = red
    nombres = {g[0] for g in grupos}
    assert f"{centro}_roseta" in nombres
    for g in grupos:
        if g[0].split("_")[0] in azules and g[0].endswith("cupulilla"):
            assert set(g[3]) == {"azul"}
