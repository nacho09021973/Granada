"""Campo de alturas sobre la planta y sus curvas de nivel (decision 0017).

    H(x, y) = cono(r) + signo * A * f(d(x, y))

- cono(r): el cono medido, (RADIO_BASE - r) * PENDIENTE, sin bajar de 0;
- d: distancia a la arista mas cercana de la red registrada; 0 sobre el
  contorno de la red, y fuera de el el termino se anula, asi que fuera de la
  red el campo es el cono;
- f, A y el signo son eleccion, no dato.

Las hiladas del modelo son las curvas de nivel de H a las cotas de hilada
medidas (PASO_VERTICAL). Con A = 0 son anillos concentricos.

Unidades: el cateto de la pieza A (CATETO_M), como el resto del modelo.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

import numpy as np
from scipy.ndimage import distance_transform_edt
from skimage.measure import find_contours, points_in_poly

from granada.celdas import CARAS, RED, REGISTRO, _transformar
from granada.cupula import _M, CATETO_M, PENDIENTE, RADIO_BASE

PASO_VERTICAL = _M["paso_vertical_hilada_m"] / CATETO_M
"""Paso vertical de hilada medido en la seccion, en unidades del cateto."""
HILADAS = int(_M["hiladas_seccion"])

RESOLUCION = 0.03
"""Lado de la celda de la rejilla del campo, en unidades del cateto (~7 mm)."""


def _nodos() -> np.ndarray:
    red = json.loads(RED.read_text(encoding="utf-8"))
    registro = json.loads(REGISTRO.read_text(encoding="utf-8"))
    return _transformar(np.array(red["nodos"], dtype=float), registro) / CATETO_M


def aristas_de_la_red() -> list[tuple[np.ndarray, np.ndarray]]:
    """Aristas de la red registrada, en unidades del cateto."""
    N = _nodos()
    red = json.loads(RED.read_text(encoding="utf-8"))
    return [(N[int(a)], N[int(b)]) for a, b, *_ in red["aristas"]]


def contorno_de_la_red() -> np.ndarray:
    """Poligono del contorno exterior de la red, en unidades del cateto."""
    caras = json.loads(CARAS.read_text(encoding="utf-8"))
    return _nodos()[caras["contorno"]["vertices"]]


FORMAS = {
    "lineal": lambda d: d,
    "raiz": np.sqrt,
}
"""Formas de f. Eleccion: lineal da celdas en piramide, raiz en cupula."""


@dataclass(frozen=True)
class Campo:
    x: np.ndarray
    """Abscisas de las columnas de la rejilla."""
    y: np.ndarray
    """Ordenadas de las filas de la rejilla."""
    H: np.ndarray
    """H[fila, columna], en unidades del cateto."""
    A: float
    forma: str
    signo: int

    @property
    def paso(self) -> float:
        return float(self.x[1] - self.x[0])


def distancia_a_la_red(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Distancia de cada nudo de la rejilla a la arista mas cercana, por
    transformada de distancia sobre las aristas rasterizadas."""
    paso = float(x[1] - x[0])
    marca = np.zeros((len(y), len(x)), dtype=bool)
    for p, q in aristas_de_la_red():
        n = max(2, int(math.ceil(float(np.hypot(*(q - p))) / (paso / 2))) + 1)
        t = np.linspace(0.0, 1.0, n)
        px = p[0] + t * (q[0] - p[0])
        py = p[1] + t * (q[1] - p[1])
        col = np.clip(np.rint((px - x[0]) / paso).astype(int), 0, len(x) - 1)
        fil = np.clip(np.rint((py - y[0]) / paso).astype(int), 0, len(y) - 1)
        marca[fil, col] = True
    return distance_transform_edt(~marca) * paso


def campo(A: float = 0.0, forma: str = "lineal", signo: int = 1, resolucion: float = RESOLUCION) -> Campo:
    """El campo H sobre una rejilla que cubre el circulo de arranque."""
    if signo not in (1, -1):
        raise ValueError("signo ha de ser 1 o -1")
    if forma not in FORMAS:
        raise ValueError(f"forma desconocida: {forma!r}; hay {sorted(FORMAS)}")
    lado = RADIO_BASE * 1.02
    x = np.arange(-lado, lado + resolucion / 2, resolucion)
    y = x.copy()
    X, Y = np.meshgrid(x, y)
    H = np.maximum(0.0, (RADIO_BASE - np.hypot(X, Y)) * PENDIENTE)
    if A:
        d = distancia_a_la_red(x, y)
        dentro = points_in_poly(np.column_stack([X.ravel(), Y.ravel()]), contorno_de_la_red()).reshape(X.shape)
        H = H + np.where(dentro, signo * A * FORMAS[forma](d), 0.0)
    return Campo(x, y, H, A, forma, signo)


def cotas_de_hilada(hiladas: int = HILADAS) -> list[float]:
    """Cotas de las juntas entre hiladas: k * PASO_VERTICAL, k = 1 .. hiladas - 1.
    Se dejan fuera el arranque (z = 0, donde el cono se aplana) y la clave."""
    return [k * PASO_VERTICAL for k in range(1, hiladas)]


LAZO_MINIMO = 2
"""Extension minima de una curva, en celdas de rejilla. Las menores son ruido
de la distancia rasterizada: a escala de una celda la transformada de
distancia puede variar mas de una unidad por unidad y fabricar maximos locales
de 0,01-0,03 cateto que no existen con la distancia exacta (comprobado el
2026-11-08 con A = 0,9 * PENDIENTE, ver tests/test_campo.py)."""


def curvas(c: Campo, z: float) -> list[np.ndarray]:
    """Curvas de nivel de H a la cota z, como polilineas (n x 2) en unidades del
    cateto. Las cerradas repiten el primer punto al final. Se descartan las de
    extension menor que LAZO_MINIMO celdas."""
    fuera = []
    for cont in find_contours(c.H, z):
        fil, col = cont[:, 0], cont[:, 1]
        P = np.column_stack([c.x[0] + col * c.paso, c.y[0] + fil * c.paso])
        if np.ptp(P, axis=0).max() >= LAZO_MINIMO * c.paso:
            fuera.append(P)
    return fuera


def es_cerrada(P: np.ndarray, tolerancia: float = 1e-9) -> bool:
    return bool(np.hypot(*(P[0] - P[-1])) <= tolerancia)
