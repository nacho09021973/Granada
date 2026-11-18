"""Cierres del modelo por campo de alturas (decision 0017, paso 3 de la
decision; paso 4 de PROXIMOS-PASOS del 2026-11-17).

Que se tapa. Los huecos se buscan por cobertura en planta, no por lazos: un
punto de la cupula esta cubierto si cae en la banda de algun frente montado
(entre el frente suavizado y su fondo, `banda_suavizada`). Lo que queda sin
cubrir es de tres clases, todas con el mismo remedio:

- el interior de los frentes mas altos de cada celda, por encima de los
  cuales no se monta nada (lazos de menos de PIEZAS_MINIMAS piezas o ninguna
  curva mas: los 16 huecos del anillo exterior y uno suelto);
- la clave, por encima del ultimo frente (solo hay cotas hasta la hilada 23);
- las zonas que ninguna banda alcanza porque la profundidad se recorta a
  PROFUNDIDAD_RELATIVA (los brazos de la estrella junto a la clave).

Las rendijas finas entre bandas se separan de los huecos por apertura
morfologica de radio RADIO_RENDIJA y solo se cuentan: arreglarlas queda fuera.

Como se tapa. Cada hueco recibe una cupulilla que sigue su contorno, sea el
que sea: base = interpolacion armonica de H desde el borde (vale H en el
borde y no salta en los huecos en pendiente); sobre ella sube como un cuarto
de circulo en la distancia al borde d, con altura
ALTURA_RELATIVA * dmax, como la cupulilla del modelo de anillos
(`granada.cupula._cupulilla`, alto 0,9 radio). El borde se ensancha
SOLAPE para que la cupulilla quede metida bajo las piezas vecinas.

Todo esto es eleccion de acabado, no dato: no hay medida de como cierra la
obra real cada celda ni la clave.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import binary_dilation, binary_opening, distance_transform_edt, label
from PIL import Image, ImageDraw

from granada.campo import Campo
from granada.cupula import RADIO_BASE
from granada.hiladas_campo import (PIEZAS_MINIMAS, SIGMA_FRENTE, Frente, _gradiente, banda_suavizada,
                                   frente_suavizado, frentes, hilada_de)

PASO_REJILLA = 2
"""Submuestreo de la rejilla del campo para la cobertura y la malla de las
cupulillas: 2 celdas de 0,03 catetos, ~1,3 cm."""

RADIO_RENDIJA = 0.06
"""Radio (catetos, ~1,3 cm) de la apertura que separa rendijas de huecos:
lo que no contiene un disco de este radio es rendija. Eleccion."""

AREA_MINIMA = 0.02
"""Area minima (catetos^2, ~10 cm^2) de un hueco tras la apertura. Eleccion."""

SOLAPE = 0.12
"""Ensanche del borde de la cupulilla bajo las piezas vecinas (catetos, ~2,7 cm)."""

ALTURA_RELATIVA = 0.9
"""Altura de la cupulilla respecto a la distancia maxima al borde, como en
granada.cupula._cupulilla."""

MARGEN_ARRANQUE = 0.5
"""Se ignora la corona r > RADIO_BASE - MARGEN_ARRANQUE: alli la banda de la
primera fila llega al arranque y lo que asoma es el tambor, no la cupula."""


@dataclass(frozen=True)
class Rejilla:
    x: np.ndarray
    y: np.ndarray
    H: np.ndarray

    @property
    def paso(self) -> float:
        return float(self.x[1] - self.x[0])


def rejilla(c: Campo, paso: int = PASO_REJILLA) -> Rejilla:
    return Rejilla(c.x[::paso], c.y[::paso], c.H[::paso, ::paso])


def _mascara(g: Rejilla, P: np.ndarray) -> np.ndarray:
    """Relleno del poligono P sobre la rejilla (barrido de PIL)."""
    fil = (P[:, 1] - g.y[0]) / g.paso
    col = (P[:, 0] - g.x[0]) / g.paso
    lienzo = Image.new("1", (g.H.shape[1], g.H.shape[0]), 0)
    ImageDraw.Draw(lienzo).polygon(list(zip(col.tolist(), fil.tolist())), fill=1)
    return np.asarray(lienzo, dtype=bool)


def bandas(c: Campo, seleccion: list[Frente] | None = None, filas_por_hilada: int = 2,
           sigma: float = SIGMA_FRENTE):
    """(frente suavizado, banda) de cada frente, como en montar(colocacion='suavizada')."""
    gradiente = _gradiente(c)
    fs = frentes(c, filas_por_hilada=filas_por_hilada) if seleccion is None else seleccion
    fuera = []
    for f in fs:
        fsu = frente_suavizado(f, sigma)
        if hilada_de(fsu).piezas < PIEZAS_MINIMAS:
            continue  # montar() tampoco lo monta: queda para el cierre
        fuera.append((fsu, banda_suavizada(c, fsu, sigma, gradiente)))
    return fuera


def cobertura(g: Rejilla, pares) -> np.ndarray:
    """Nudos de la rejilla que caen en alguna banda (frente XOR fondo).

    La banda de un frente cerrado es la corona entre la curva del frente y la
    de su fondo; se rellenan las dos y se toma la diferencia simetrica.
    """
    m = np.zeros(g.H.shape, dtype=bool)
    for f, b in pares:
        m |= _mascara(g, b.xy[0]) ^ _mascara(g, b.xy[-1])
    return m


@dataclass(frozen=True)
class Huecos:
    rejilla: Rejilla
    etiquetas: np.ndarray
    """0 fuera de huecos; 1..n cada hueco."""
    rendijas: np.ndarray
    """Mascara de lo descubierto que no llega a hueco."""

    @property
    def n(self) -> int:
        return int(self.etiquetas.max())


def huecos(c: Campo, pares, paso: int = PASO_REJILLA) -> Huecos:
    g = rejilla(c, paso)
    X, Y = np.meshgrid(g.x, g.y)
    dentro = np.hypot(X, Y) < RADIO_BASE - MARGEN_ARRANQUE
    libre = dentro & ~cobertura(g, pares)
    r = max(1, int(round(RADIO_RENDIJA / g.paso)))
    disco = np.hypot(*np.mgrid[-r:r + 1, -r:r + 1]) <= r
    grandes = binary_opening(libre, structure=disco)
    et, n = label(grandes)
    area = np.bincount(et.ravel(), minlength=n + 1) * g.paso ** 2
    validas = np.flatnonzero(area >= AREA_MINIMA)
    validas = validas[validas > 0]
    nuevas = np.zeros(n + 1, dtype=int)
    nuevas[validas] = np.arange(1, len(validas) + 1)
    et = nuevas[et]
    return Huecos(g, et, libre & (et == 0))


def resumen_huecos(h: Huecos) -> list[dict]:
    g = h.rejilla
    X, Y = np.meshgrid(g.x, g.y)
    fuera = []
    for k in range(1, h.n + 1):
        m = h.etiquetas == k
        cx, cy = float(X[m].mean()), float(Y[m].mean())
        fuera.append({"hueco": k, "area_catetos2": float(m.sum() * g.paso ** 2),
                      "centro": [cx, cy], "radio": float(np.hypot(cx, cy)),
                      "angulo_grados": float(np.degrees(np.arctan2(cy, cx))),
                      "H_min": float(g.H[m].min()), "H_max": float(g.H[m].max())})
    return fuera


NUDOS_RENDIJA = 4
"""Una rendija se cuenta si tiene al menos estos nudos (~7 cm^2). Las menores
son sobre todo la junta rasterizada entre dos bandas que se tocan."""


def rendijas_por_fila(h: Huecos, paso_fila: float, minimo: int = NUDOS_RENDIJA) -> dict[int, int]:
    """Componentes de rendija de al menos `minimo` nudos, por fila
    j = ceil(H / paso_fila) en su nudo mas bajo."""
    et, n = label(h.rendijas, structure=np.ones((3, 3)))
    tam = np.bincount(et.ravel(), minlength=n + 1)
    fuera: dict[int, int] = {}
    for k in np.flatnonzero(tam >= minimo):
        if k == 0:
            continue
        j = int(np.ceil(h.rejilla.H[et == k].min() / paso_fila))
        fuera[j] = fuera.get(j, 0) + 1
    return dict(sorted(fuera.items()))


def base_armonica(H: np.ndarray, dentro: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """Interpolacion armonica (Laplace, 4 vecinos) de H desde los nudos de fuera.

    Vale H en el borde y es suave dentro: un hueco en pendiente no hereda el
    salto entre el lado alto y el bajo que daria tomar el borde mas cercano.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve
    filas, cols = np.nonzero(dentro)
    n = len(filas)
    fi, co, va = [np.arange(n)], [np.arange(n)], [np.full(n, 4.0)]
    b = np.zeros(n)
    for df, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        f2 = np.clip(filas + df, 0, H.shape[0] - 1)
        c2 = np.clip(cols + dc, 0, H.shape[1] - 1)
        vecino = idx[f2, c2]
        ok = vecino >= 0
        fi.append(np.flatnonzero(ok))
        co.append(vecino[ok])
        va.append(np.full(ok.sum(), -1.0))
        b[~ok] += H[f2[~ok], c2[~ok]]
    A = coo_matrix((np.concatenate(va), (np.concatenate(fi), np.concatenate(co))), shape=(n, n)).tocsr()
    z = H.copy()
    z[filas, cols] = spsolve(A, b)
    return z


def cupulilla(g: Rejilla, m: np.ndarray, solape: float = SOLAPE):
    """Malla (V, F) de la cupulilla sobre la mascara `m` (ver docstring del modulo)."""
    r = max(1, int(round(solape / g.paso)))
    disco = np.hypot(*np.mgrid[-r:r + 1, -r:r + 1]) <= r
    ancho = binary_dilation(m, structure=disco)
    d = distance_transform_edt(ancho)
    idx = -np.ones(m.shape, dtype=int)
    filas, cols = np.nonzero(ancho)
    idx[filas, cols] = np.arange(len(filas))
    borde = base_armonica(g.H, ancho, idx)
    # El nudo de borde (a un nudo de fuera) queda a d = 0, en la base.
    d = np.maximum(d - 1, 0) * g.paso
    dmax = float(d.max())
    alto = ALTURA_RELATIVA * dmax
    t = np.clip(d / max(dmax, 1e-9), 0, 1)
    z = borde + alto * np.sqrt(t * (2 - t))
    V = list(zip(g.x[cols].tolist(), g.y[filas].tolist(), z[filas, cols].tolist()))
    a = idx[:-1, :-1]
    b = idx[:-1, 1:]
    cc = idx[1:, 1:]
    dd = idx[1:, :-1]
    F = []
    for p, q, s in ((a, b, cc), (a, cc, dd)):
        ok = (p >= 0) & (q >= 0) & (s >= 0)
        F.extend(zip(p[ok].tolist(), q[ok].tolist(), s[ok].tolist()))
    return V, F


def cierres(c: Campo, pares, paso: int = PASO_REJILLA):
    """Grupos (nombre, V, F) de las cupulillas y el objeto Huecos."""
    h = huecos(c, pares, paso)
    grupos = []
    for k in range(1, h.n + 1):
        V, F = cupulilla(h.rejilla, h.etiquetas == k)
        grupos.append((f"cupulilla_{k:02d}", V, F))
    return grupos, h


SOLAPE_ARRANQUE = 0.4
"""Cuanto entra la corona de arranque bajo la primera fila (catetos, ~9 cm)."""


def corona_arranque(radio_base: float = RADIO_BASE, n: int = 384, z: float = -0.01):
    """Corona plana en el arranque, del circulo de la cupula por campo al
    octogono interior de la cornisa de la sala (granada.sala.cornisa).

    La cornisa se hizo para el modelo de anillos, que arranca en un octogono
    de apotema radio_base / _MEDIA_OCT; el campo arranca en un circulo de
    radio radio_base, y entre ambos quedaba una corona vacia, mas ancha en los
    vertices (rincones negros en la vista sala, 2026-11-18). Va un pelo por
    debajo de z = 0 para no coincidir con las patas de la primera fila.
    Eleccion de acabado, no medida."""
    from granada.cupula import _MEDIA_OCT, _octogono
    phi = 2 * np.pi * np.arange(n) / n
    r_in = radio_base - SOLAPE_ARRANQUE
    r_out = radio_base / _MEDIA_OCT * _octogono(phi)
    V = [(float(r * np.cos(p)), float(r * np.sin(p)), z) for p, r in zip(phi, np.full(n, r_in))]
    V += [(float(r * np.cos(p)), float(r * np.sin(p)), z) for p, r in zip(phi, r_out)]
    F = []
    for i in range(n):
        j = (i + 1) % n
        F.append((i, j, n + j))
        F.append((i, n + j, n + i))
    return V, F
