"""Cierres del campo: el cono solo deja abierta la clave; con A=2 se tapan
los huecos de los lazos, la estrella y la clave; la cupulilla arranca en H."""
import numpy as np
import pytest
from skimage.measure import points_in_poly

from granada.campo import PENDIENTE, RADIO_BASE, campo
from granada.hiladas_campo import frentes
from granada.cierres_campo import bandas, cierres, cobertura, cupulilla, huecos, rejilla, resumen_huecos


@pytest.fixture(scope="module")
def cono():
    c = campo(A=0)
    return c, bandas(c)


@pytest.fixture(scope="module")
def red():
    c = campo(A=2.0)
    return c, bandas(c)


def test_en_el_cono_solo_queda_la_clave(cono):
    c, pares = cono
    h = huecos(c, pares)
    assert h.n == 1
    (r,) = resumen_huecos(h)
    assert r["radio"] < 0.1
    # Por encima del ultimo frente: la cota mas baja del hueco es la de esa fila.
    assert r["H_min"] >= pares[-1][0].indice * pares[-1][0].paso - 0.1


def test_con_a2_se_tapan_lazos_estrella_y_clave(red):
    c, pares = red
    grupos, h = cierres(c, pares)
    rs = resumen_huecos(h)
    assert len(grupos) == h.n
    radios = np.array([r["radio"] for r in rs])
    # La clave, centrada; los brazos de la estrella (r < 6), de 8 en 8.
    assert (radios < 0.1).sum() == 1
    assert ((radios > 3) & (radios < 6)).sum() % 8 == 0
    assert ((radios > 3) & (radios < 6)).sum() >= 8
    # Encima de cada frente sin hijo en la fila siguiente no se monta nada:
    # su punto mas alto ha de caer en un hueco tapado.
    g = h.rejilla
    X, Y = np.meshgrid(g.x, g.y)
    pts = np.column_stack([X.ravel(), Y.ravel()])
    techos = 0
    crudos = frentes(c, filas_por_hilada=2)  # sin suavizar: el suavizado colapsa los lazos pequenos
    cubierto = cobertura(g, pares).ravel()
    for f in crudos:
        hijos = [q for q in crudos if q.indice == f.indice + 1 and points_in_poly(q.puntos[:1], f.puntos)[0]]
        if hijos:
            continue
        dentro = points_in_poly(pts, f.puntos).reshape(X.shape)
        k = np.argmax(np.where(dentro, g.H, -np.inf))
        assert cubierto[k] or h.etiquetas.ravel()[k] > 0, f.indice
        techos += 1
    assert techos >= 17


def test_la_cupulilla_arranca_en_h_y_sube():
    c = campo(A=0)
    g = rejilla(c)
    X, Y = np.meshgrid(g.x, g.y)
    m = np.hypot(X - 5, Y) < 1.0
    V, F = cupulilla(g, m)
    V = np.asarray(V)
    assert len(F) > 0
    H = (RADIO_BASE - np.hypot(V[:, 0], V[:, 1])) * PENDIENTE
    d = np.hypot(V[:, 0] - 5, V[:, 1])
    borde = d > d.max() - 0.5 * g.paso
    # Anillo exterior a la cota del campo; la cumbre, ~0,9 dmax sobre el plano
    # del borde (en el cono la base armonica es ese plano: H es lineal en el
    # entorno salvo la curvatura del cono).
    assert np.abs(V[borde, 2] - H[borde]).max() < 0.05
    # Cumbre sobre la media del borde (valor de la base armonica en el centro).
    centro = np.argmin(d)
    from granada.cierres_campo import ALTURA_RELATIVA
    assert 0.85 * ALTURA_RELATIVA * d.max() < V[centro, 2] - H[borde].mean() < 1.1 * ALTURA_RELATIVA * d.max()


def test_el_lazo_que_colapsa_al_suavizar_no_se_monta(red):
    from granada.hiladas_campo import admitido_suavizado, hilada_de
    c, pares = red
    lazos = [f for f in frentes(c, filas_por_hilada=2) if f.indice == 24 and f.largo < 3]
    assert len(lazos) == 1 and hilada_de(lazos[0]).piezas >= 6
    assert not admitido_suavizado(lazos[0])
    assert not any(f.indice == 24 and np.hypot(*f.puntos.mean(axis=0) - (0, -8.73)) < 0.5 for f, _ in pares)


def test_corona_de_arranque_cubre_del_circulo_al_octogono_de_la_cornisa():
    from granada.cierres_campo import SOLAPE_ARRANQUE, corona_arranque
    from granada.cupula import _MEDIA_OCT
    V, F = corona_arranque(n=64)
    V = np.asarray(V)
    r = np.hypot(V[:, 0], V[:, 1])
    assert len(F) == 128
    assert np.allclose(r[:64], RADIO_BASE - SOLAPE_ARRANQUE)
    apotema = RADIO_BASE / _MEDIA_OCT
    assert apotema - 1e-9 <= r[64:].min() and r[64:].max() <= apotema / np.cos(np.pi / 8) + 1e-9
