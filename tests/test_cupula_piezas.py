"""Controles del apilado de hiladas de `granada.cupula`."""

import math

import pytest

from granada.cupula import (
    FAMILIAS, PENDIENTE, RADIO_BASE, RADIO_CIERRE, cupula, doblar, plan_de_hiladas,
    planta_por_defecto,
)


@pytest.fixture(scope="module")
def plan():
    return plan_de_hiladas()


def test_pendiente_y_radio_vienen_del_dato():
    assert PENDIENTE == pytest.approx(0.20304347826086958 / 0.1582608695652174)
    assert RADIO_BASE == pytest.approx(3.64 / (0.1582608695652174 / (math.sqrt(2) / 2)))


def test_cada_hilada_entra_lo_que_fondea_la_siguiente(plan):
    """La trasera de la hilada k+1 cae en el frente de la k: tapa su banda."""
    assert plan[0].radio_frente + FAMILIAS[plan[0].familia].fondo == pytest.approx(RADIO_BASE)
    for a, b in zip(plan, plan[1:]):
        assert b.radio_frente + FAMILIAS[b.familia].fondo == pytest.approx(a.radio_frente)
        assert b.cota == pytest.approx(a.cota + a.paso)


def test_el_perfil_es_el_cono_medido(plan):
    for h in plan:
        assert h.paso / FAMILIAS[h.familia].fondo == pytest.approx(PENDIENTE)


def test_cada_vuelta_cierra_con_poco_estiramiento(plan):
    """Multiplo de 16 para el orden 8; en las hiladas pequenas el salto de 16
    piezas obliga a estirar hasta un 20 %."""
    planta = planta_por_defecto()
    for h in plan:
        assert h.piezas % 16 == 0
        f = FAMILIAS[h.familia]
        largo = planta.arco(h.radio_frente)[2]
        assert h.piezas * f.paso_tangencial * h.estiramiento == pytest.approx(largo)
        assert 0.8 < h.estiramiento < 1.2
    assert plan[-1].radio_frente >= RADIO_CIERRE


def test_la_planta_va_del_octogono_a_la_estrella():
    planta = planta_por_defecto()
    eje, diagonal_oct = 0.0, math.pi / 8
    base, cierre = planta.radio_base, planta.radio_cierre
    # arranque: octogono, lado plano a 0 grados y vertice a 22,5
    assert planta.forma(eje, base) < planta.forma(diagonal_oct, base)
    # cierre: estrella, punta a 0 y 45 grados, entrante a 22,5
    assert planta.forma(eje, cierre) > planta.forma(diagonal_oct, cierre)
    assert planta.forma(math.pi / 4, cierre) == pytest.approx(planta.forma(eje, cierre))
    assert planta.forma(eje, cierre) / planta.forma(diagonal_oct, cierre) == pytest.approx(
        math.sqrt(2) * math.cos(math.pi / 8))


def test_en_contorno_respeta_el_orden_8():
    planta = planta_por_defecto()
    F = 6.0
    a = planta.punto(0.3, F)
    b = planta.punto(0.3 + math.pi / 4, F)
    assert math.hypot(*a) == pytest.approx(math.hypot(*b))


def test_doblar_pone_el_frente_en_el_radio_y_la_trasera_detras():
    (f, t) = doblar([(0.3, 0.0, 0.0), (0.3, -0.5, 1.0)], 0.2, 7.0, 1.0, 2.0)
    assert math.hypot(f[0], f[1]) == pytest.approx(7.0)
    assert math.hypot(t[0], t[1]) == pytest.approx(7.5)
    assert t[2] == pytest.approx(3.0)


def test_cupula_reducida_monta_todas_las_hiladas():
    hiladas, grupos = cupula(subdivision=2, radio_base=6.0)
    nombres = [g[0] for g in grupos]
    assert len(nombres) == len(hiladas) + 2
    assert nombres[-2:] == ["cupulilla", "tambor"]
