"""Colocacion por flujo (0024): en el cono coincide con el rayo; con A=2 llega a la cota."""
import numpy as np
import pytest

from granada.campo import PENDIENTE, RADIO_BASE, campo
from granada.cupula import FAMILIAS
from granada.hiladas_campo import (banda_de_flujo, colocar_en_banda, frentes, hilada_de,
                                   interpolador_suave, montar)


@pytest.fixture(scope="module")
def cono():
    return campo(A=0)


def test_en_el_cono_el_flujo_es_radial_y_llena_la_banda(cono):
    suave = interpolador_suave(cono)
    for f in frentes(cono, filas_por_hilada=2)[4:40:9]:
        b = banda_de_flujo(cono, f, suave)
        r = np.hypot(b.xy[..., 0], b.xy[..., 1])
        esperado = RADIO_BASE - (f.indice - b.q) * f.paso / PENDIENTE
        assert np.abs(r - esperado[:, None]).max() < 2 * cono.paso
        assert np.abs(b.error_cota).max() < 1e-3 * f.paso
        # Radial: el angulo no cambia del frente al fondo.
        a0 = np.arctan2(b.xy[0, :, 1], b.xy[0, :, 0])
        a1 = np.arctan2(b.xy[-1, :, 1], b.xy[-1, :, 0])
        assert np.abs(np.angle(np.exp(1j * (a1 - a0)))).max() < 1e-3


def test_colocar_en_banda_lleva_frente_y_fondo_a_sus_curvas(cono):
    f = frentes(cono, filas_por_hilada=2)[10]
    h = hilada_de(f)
    fondo = FAMILIAS[h.familia].fondo * f.escala
    b = banda_de_flujo(cono, f)
    V = colocar_en_banda([(0, -fondo, 0), (0, 0, 0)], f, b, 1.234, h.estiramiento, fondo)
    atras, delante = (np.hypot(v[0], v[1]) for v in V)
    assert abs(delante - (RADIO_BASE - f.indice * f.paso / PENDIENTE)) < 2 * cono.paso
    assert abs(atras - (RADIO_BASE - f.cota / PENDIENTE)) < 2 * cono.paso
    assert V[0][2] == pytest.approx(f.cota)


def test_montar_flujo_es_finito_y_rechaza_metodo_desconocido(cono):
    f = frentes(cono, filas_por_hilada=2)[12]
    ((_, V, F, E, S),) = montar(cono, [f], subdivision=2, colocacion="flujo")
    assert np.isfinite(np.asarray(V)).all() and len(F) == len(E) == len(S)
    with pytest.raises(ValueError):
        montar(cono, [f], colocacion="otra")


def test_rigida_en_el_cono_pone_lados_tangentes_y_fondo_radial(cono):
    from granada.hiladas_campo import poligono_de
    f = frentes(cono, filas_por_hilada=2)[10]
    pg = poligono_de(cono, f)
    radial = pg.centros / np.linalg.norm(pg.centros, axis=1)[:, None]
    assert np.abs(np.sum(pg.tangentes * radial, axis=1)).max() < 1e-2
    assert np.sum(pg.normales * radial, axis=1).min() > .99
    esperado = f.paso / PENDIENTE
    assert np.abs(pg.fondo_libre - esperado).max() < 2 * cono.paso
    ((_, V, F, E, S),) = montar(cono, [f], subdivision=2, colocacion="rigida")
    assert np.isfinite(np.asarray(V)).all() and len(F) == len(E) == len(S)


def test_suavizar_curva_quita_ondas_cortas_y_conserva_circulo():
    from granada.hiladas_campo import suavizar_curva
    t = np.linspace(0, 2 * np.pi, 2001)
    circulo = np.column_stack([10 * np.cos(t), 10 * np.sin(t)])
    onda = circulo * (1 + .02 * np.sin(60 * t))[:, None]
    liso = suavizar_curva(onda, 1.0)
    r = np.hypot(*liso.T)
    assert np.allclose(liso[0], liso[-1])
    assert np.ptp(r) < .05 * np.ptp(np.hypot(*onda.T))
    assert abs(r.mean() - 10) < .1
    assert np.abs(np.hypot(*suavizar_curva(circulo, 0).T) - 10).max() < 1e-2


def test_suavizada_en_el_cono_llena_la_banda(cono):
    from granada.hiladas_campo import banda_suavizada, frente_suavizado
    for f0 in frentes(cono, filas_por_hilada=2)[4:40:9]:
        f = frente_suavizado(f0, 1.0)
        b = banda_suavizada(cono, f, 1.0)
        r = np.hypot(b.xy[..., 0], b.xy[..., 1])
        esperado = RADIO_BASE - (f.indice - b.q) * f.paso / PENDIENTE
        assert np.abs(r - esperado[:, None]).max() < 3 * cono.paso
    ((_, V, F, E, S),) = montar(cono, [f0], subdivision=2, colocacion="suavizada", sigma=1.0)
    assert np.isfinite(np.asarray(V)).all() and len(F) == len(E) == len(S)
