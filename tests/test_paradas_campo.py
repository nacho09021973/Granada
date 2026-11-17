"""Controles independientes del diagnostico discreto de escape."""
from itertools import combinations

import numpy as np
from scipy.ndimage import label

from scripts.diagnosticar_paradas_campo import barrera_minimax


def test_barrera_con_cuenca_y_camino_testigo():
    H = np.array([[0., 5., 5.], [5., 2., 4.], [5., 3., 3.]])
    b = barrera_minimax(H, (1, 1), 0)
    assert b["altura_escape"] == 5
    assert b["barrera_desde_nodo"] == 3
    camino = b["camino_nodos"]
    assert camino[0] == [1, 1] and H[tuple(camino[-1])] == 0
    assert max(H[tuple(p)] for p in camino) == b["altura_escape"]
    assert all(abs(p[0]-q[0])+abs(p[1]-q[1]) == 1 for p, q in zip(camino, camino[1:]))


def test_minimax_coincide_con_conectividad_de_subniveles():
    # Segunda via: etiquetar subniveles, sin usar el algoritmo de caminos.
    for posiciones in combinations(range(9), 3):
        H = np.full((3, 3), 4.)
        H.ravel()[list(posiciones)] = [0., 1., 2.]
        inicio = (1, 1)
        esperado = None
        for z in np.unique(H):
            L, _ = label(H <= z)
            if L[inicio] and np.any((L == L[inicio]) & (H <= 0)):
                esperado = z
                break
        assert barrera_minimax(H, inicio, 0)["altura_escape"] == esperado


def test_cota_inexistente_y_bajada_sin_barrera():
    assert barrera_minimax(np.ones((2, 2)), (0, 0), 0) is None
    b = barrera_minimax(np.array([[2., 1., 0.]]), (0, 0), 0)
    assert b["barrera_desde_nodo"] == 0
