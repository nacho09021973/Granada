"""Controles analiticos del descenso y deteccion de subida entre extremos."""
import numpy as np
import pytest
from scipy.ndimage import map_coordinates

from granada.campo import Campo
from scripts.ensayar_transporte_interior import descender, subida_segmento, valor_gradiente


def test_derivada_bilineal_coincide_con_polinomio_y_diferencias_centradas():
    x = np.linspace(-2, 2, 21)
    X, Y = np.meshgrid(x, x)
    c = Campo(x, x, 2+3*X-2*Y+X*Y, 0, "sintetico", 1)
    p = np.array([.37, -.23])
    h, g = valor_gradiente(c, p)
    assert h == pytest.approx(2+3*p[0]-2*p[1]+p[0]*p[1])
    assert g == pytest.approx([3+p[1], -2+p[0]])
    assert h == pytest.approx(map_coordinates(c.H, [[(p[1]-x[0])/c.paso], [(p[0]-x[0])/c.paso]], order=1)[0])
    for d in range(2):
        delta = np.eye(2)[d]*1e-6
        assert g[d] == pytest.approx((valor_gradiente(c, p+delta)[0]-valor_gradiente(c, p-delta)[0])/2e-6)


def test_detecta_subida_oculta_entre_extremos_iguales():
    x = np.array([0., 1.])
    # H=x(1-y), sobre la diagonal H=t(1-t): extremos cero, cima 1/4.
    c = Campo(x, x, np.array([[0., 1.], [0., 0.]]), 0, "sintetico", 1)
    assert subida_segmento(c, np.array([0., 0.]), np.array([1., 1.])) == pytest.approx(1)


def test_llega_en_plano_y_declara_cota_inexistente():
    x = np.linspace(-2, 2, 81)
    X, Y = np.meshgrid(x, x)
    c = Campo(x, x, X, 0, "sintetico", 1)
    r = descender(c, [.7, .13], 0, 1)
    assert r["alcanza_cota"] and r["H_decrece"]
    assert r["recorrido_m"] > 0
    plano = Campo(x, x, np.ones_like(X), 0, "sintetico", 1)
    r = descender(plano, [0., 0.], 0, 1)
    assert not r["alcanza_cota"] and r["parada"] == "gradiente_pequeno"
    with pytest.raises(ValueError):
        valor_gradiente(c, [3., 0.])
