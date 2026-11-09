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


def test_dos_filas_conservan_cotas_y_anaden_solo_intermedias():
    original = np.asarray(cotas_de_hilada())
    doble = np.asarray(cotas_de_hilada(filas_por_hilada=2))
    assert len(doble) == 45
    assert np.allclose(doble[1::2], original)
    assert np.allclose(np.diff(doble), PASO_VERTICAL / 2)


@pytest.mark.parametrize("filas", [0, -1, 1.5, True])
def test_subdivision_invalida(filas):
    with pytest.raises(ValueError):
        cotas_de_hilada(filas_por_hilada=filas)


def test_opcion_b_sigue_el_cono_con_medio_paso(plano):
    from granada.cupula import FAMILIAS
    from granada.hiladas_campo import _gradiente, colocar, frentes, hilada_de

    g = _gradiente(plano)
    for f in frentes(plano, filas_por_hilada=2)[4:40:7]:
        h = hilada_de(f)
        fondo = FAMILIAS[h.familia].fondo / 2
        V = colocar([(0, -fondo, 0), (0, 0, 0)], f, g, 1.234, h.estiramiento, fondo)
        atras, delante = (np.hypot(v[0], v[1]) for v in V)
        assert h.paso == PASO_VERTICAL / 2
        assert abs(delante - (RADIO_BASE - f.indice * h.paso / PENDIENTE)) < 2 * plano.paso
        assert abs(atras - (RADIO_BASE - f.cota / PENDIENTE)) < 3 * plano.paso
        assert abs(h.piezas * FAMILIAS[h.familia].paso_tangencial - f.largo) <= FAMILIAS[h.familia].paso_tangencial


def test_malla_con_medio_fondo_y_altura_es_finita_y_respeta_su_paso(plano):
    from granada.hiladas_campo import frentes, montar

    f = frentes(plano, filas_por_hilada=2)[12]
    ((_, V, F, E, S),) = montar(plano, [f], subdivision=2)
    V = np.asarray(V)
    assert np.isfinite(V).all()
    assert min(min(t) for t in F) >= 0
    assert max(max(t) for t in F) < len(V)
    assert len(F) == len(E) == len(S)
    assert V[:, 2].min() >= f.cota - 1e-9
    assert V[:, 2].max() <= f.cota + 2 * f.paso + 1e-9


def test_dividir_una_hilada_conserva_familia_y_piezas_por_contorno(plano):
    from granada.hiladas_campo import frente, frentes, hilada_de

    for original in frentes(plano):
        h = hilada_de(original)
        for j in (2 * original.indice - 1, 2 * original.indice):
            dividida = hilada_de(frente(j, original.puntos, filas_por_hilada=2))
            assert dividida.familia == h.familia
            assert dividida.piezas == h.piezas
            assert dividida.estiramiento == h.estiramiento
            assert dividida.paso == h.paso / 2


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
