"""Controles del campo de alturas de la decision 0017 (granada/campo.py)."""

import numpy as np
import pytest

from granada.campo import PASO_VERTICAL, campo, contorno_de_la_red, cotas_de_hilada, curvas, es_cerrada
from granada.cupula import PENDIENTE, RADIO_BASE


@pytest.fixture(scope="module")
def plano():
    return campo(A=0.0)


def test_con_a_cero_cada_cota_da_un_solo_anillo_circular(plano):
    """Paso 1 de la decision 0017: con A = 0 se recupera el modelo de anillos."""
    for z in cotas_de_hilada():
        cs = curvas(plano, z)
        assert len(cs) == 1, f"cota {z:.3f}: {len(cs)} curvas"
        (P,) = cs
        assert es_cerrada(P)
        r = np.hypot(P[:, 0], P[:, 1])
        esperado = RADIO_BASE - z / PENDIENTE
        assert np.max(np.abs(r - esperado)) < 2 * plano.paso


def test_las_cotas_son_las_hiladas_medidas():
    z = cotas_de_hilada()
    assert len(z) == 22
    assert np.allclose(np.diff(z), PASO_VERTICAL)
    assert z[-1] < RADIO_BASE * PENDIENTE


def test_fuera_de_la_red_el_campo_es_el_cono(plano):
    c = campo(A=1.0)
    X, Y = np.meshgrid(c.x, c.y)
    r = np.hypot(X, Y)
    radio_red = np.hypot(*contorno_de_la_red().T).max()
    lejos = r > radio_red + 2 * c.paso
    assert np.allclose(c.H[lejos], plano.H[lejos])


def test_por_debajo_de_la_pendiente_no_hay_lazos():
    """|grad d| <= 1, asi que con A < PENDIENTE el termino de la red nunca le
    gana al cono: no hay maximos locales y cada cota da un solo anillo."""
    c = campo(A=0.9 * PENDIENTE)
    assert all(len(curvas(c, z)) == 1 for z in cotas_de_hilada())


def test_por_encima_de_la_pendiente_las_hiladas_se_parten_en_lazos():
    c = campo(A=2.0)
    lazos = [len(curvas(c, z)) for z in cotas_de_hilada()]
    assert lazos[0] == 1
    assert max(lazos) > 8
    assert all(es_cerrada(P) for z in cotas_de_hilada() for P in curvas(c, z))


def test_con_a_cero_la_pieza_llena_la_banda_hasta_la_hilada_anterior(plano):
    """Paso 3: con A = 0 el fondo de cada pieza cae sobre la curva de la cota
    anterior (radio RADIO_BASE - (j - 1) * paso horizontal), como en el modelo
    de anillos."""
    from granada.cupula import FAMILIAS
    from granada.hiladas_campo import _gradiente, colocar, frentes, hilada_de

    g = _gradiente(plano)
    for f in frentes(plano)[2:20:5]:
        h = hilada_de(f)
        fondo = FAMILIAS[h.familia].fondo
        V = colocar([(0.0, -fondo, 0.0), (0.0, 0.0, 0.0)], f, g, 1.234, h.estiramiento, fondo)
        r_atras, r_frente = (float(np.hypot(v[0], v[1])) for v in V)
        assert abs(r_frente - (RADIO_BASE - f.indice * PASO_VERTICAL / PENDIENTE)) < 2 * plano.paso
        assert abs(r_atras - (RADIO_BASE - (f.indice - 1) * PASO_VERTICAL / PENDIENTE)) < 3 * plano.paso


def test_con_a_cero_el_numero_de_piezas_es_el_del_modelo_de_anillos(plano):
    from granada.hiladas_campo import resumen

    filas = resumen(plano)
    assert len(filas) == 22 and all(r["anillo"] for r in filas)
    # Redondear a un numero par de piezas estira como mucho una pieza entre n.
    assert all(abs(r["estiramiento"] - 1) <= 1 / r["piezas"] for r in filas)
