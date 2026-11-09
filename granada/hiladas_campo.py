"""Piezas a lo largo de las curvas de nivel del campo (decision 0017, paso 3).

Cada curva de nivel cerrada de `granada.campo` a la cota z_j es el **frente**
de una hilada. Se reproduce la colocacion del modelo de anillos
(`granada.cupula.en_contorno` y `plan_de_hiladas`), generalizada a una curva
cualquiera:

- x local (a lo ancho) pasa a longitud de arco sobre la curva;
- y local (hacia el frente; la pieza queda en y <= 0) pasa a un desplazamiento
  hacia fuera, en la direccion de bajada del campo, -grad H / |grad H|. La
  profundidad local de la hilada es la distancia hasta la curva de la cota
  anterior, PASO_VERTICAL / |grad H|; la pieza se estira para llenarla. Con
  A = 0 sale PASO_VERTICAL / PENDIENTE, el paso horizontal medido, que es el
  fondo de la familia A: el modelo de anillos;
- z: la pieza cuelga con la pata una hilada por debajo de su frente,
  cota = z_j - PASO_VERTICAL, como en el modelo de anillos.

Se desplaza por el gradiente y no por la normal de la polilinea porque el
campo es mas suave que su curva: en las esquinas de la estrella la normal
salta y el gradiente no tanto. Aun asi, en las esquinas concavas las piezas
vecinas se solapan o se separan: es el riesgo declarado del paso 3.

Con filas_por_hilada=2 (opcion B, decision 0018), cada pieza se reduce a
media escala en las tres coordenadas y el paso entre frentes se divide por
dos. Se conserva el campo, su rejilla y su suavizado; las nuevas cotas son
supuestas. El recuento puede crecer aproximadamente por cuatro, no por dos.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import map_coordinates

from granada.campo import PASO_VERTICAL, Campo, cotas_de_hilada, curvas, es_cerrada
from granada.cupula import FAMILIAS, SECUENCIA, Hilada
from granada.piezas import etiquetas, malla, oclusion, pieza

PROFUNDIDAD_RELATIVA = (0.35, 1.6)
"""Limites de la profundidad local respecto al fondo de la familia. Donde el
campo es casi plano (|grad H| -> 0) la profundidad se dispararia; se recorta.
Eleccion."""


@dataclass(frozen=True)
class Frente:
    """Curva cerrada que hace de frente de una hilada."""

    indice: int
    """Fila j, a cota j * paso; no equivale necesariamente a hilada medida."""
    puntos: np.ndarray
    """Polilinea cerrada (n x 2), el ultimo punto repite el primero."""
    s: np.ndarray
    """Longitud acumulada en cada punto."""
    filas_por_hilada: int = 1
    """Subdivisiones elegidas de la hilada de referencia; 2 es la opcion B."""

    @property
    def escala(self) -> float:
        return 1 / self.filas_por_hilada

    @property
    def paso(self) -> float:
        return PASO_VERTICAL * self.escala

    @property
    def largo(self) -> float:
        return float(self.s[-1])

    @property
    def cota(self) -> float:
        """Cota de la pata: una hilada por debajo del frente."""
        return (self.indice - 1) * self.paso


def frente(indice: int, P: np.ndarray, filas_por_hilada: int = 1) -> Frente:
    if type(filas_por_hilada) is not int or filas_por_hilada < 1:
        raise ValueError("filas_por_hilada debe ser un entero positivo")
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
    return Frente(indice, P, s, filas_por_hilada)


PIEZAS_MINIMAS = 6
"""Un lazo con menos piezas no se monta: las piezas se deforman en pegotes
(comprobado el 2026-11-08). Se cerrara con una cupulilla (paso 4)."""


def frentes(c: Campo, minimo: int = PIEZAS_MINIMAS, filas_por_hilada: int = 1) -> list[Frente]:
    """Frentes cerrados del campo con sitio para `minimo` piezas, de abajo arriba."""
    fuera = []
    for j, z in enumerate(cotas_de_hilada(filas_por_hilada=filas_por_hilada), start=1):
        for P in curvas(c, z):
            if es_cerrada(P):
                f = frente(j, P, filas_por_hilada)
                if hilada_de(f).piezas >= minimo:
                    fuera.append(f)
    return fuera


def _gradiente(c: Campo):
    gy, gx = np.gradient(c.H, c.paso)

    def en(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        col = (x - c.x[0]) / c.paso
        fil = (y - c.y[0]) / c.paso
        return (map_coordinates(gx, [fil, col], order=1, mode="nearest"),
                map_coordinates(gy, [fil, col], order=1, mode="nearest"))

    return en


def colocar(V, f: Frente, gradiente, inicio: float, estiramiento: float, fondo: float):
    """Del marco local de la pieza al frente `f` (ver el docstring del modulo)."""
    P = np.asarray(V, dtype=float)
    s = np.mod(inicio + P[:, 0] * estiramiento, f.largo)
    x = np.interp(s, f.s, f.puntos[:, 0])
    y = np.interp(s, f.s, f.puntos[:, 1])
    gx, gy = gradiente(x, y)
    norma = np.maximum(np.hypot(gx, gy), 1e-9)
    profundidad = np.clip(f.paso / norma, PROFUNDIDAD_RELATIVA[0] * fondo, PROFUNDIDAD_RELATIVA[1] * fondo)
    t = -P[:, 1] / fondo * profundidad
    X = x - gx / norma * t
    Y = y - gy / norma * t
    return list(zip(X.tolist(), Y.tolist(), (P[:, 2] + f.cota).tolist()))


def hilada_de(f: Frente) -> Hilada:
    """Plan de la hilada: familia por la secuencia A, A, C del modelo de anillos
    y numero par de piezas para que alternen frente y vertice."""
    familia = SECUENCIA[(f.indice - 1) % len(SECUENCIA)]
    paso_t = FAMILIAS[familia].paso_tangencial * f.escala
    n = max(2, 2 * round(f.largo / (2 * paso_t)))
    return Hilada(f.indice - 1, familia, float("nan"), f.cota, f.paso, n, f.largo / (n * paso_t))


def montar(c: Campo, seleccion: list[Frente] | None = None, subdivision: int = 6,
           filas_por_hilada: int = 1):
    """Grupos (nombre, V, F, etiquetas, sombras), uno por frente."""
    gradiente = _gradiente(c)
    plantillas: dict = {}
    grupos = []
    for k, f in enumerate(frentes(c, filas_por_hilada=filas_por_hilada) if seleccion is None else seleccion):
        h = hilada_de(f)
        fam = FAMILIAS[h.familia]
        V, F, E, S = [], [], [], []
        for i, tipo in enumerate(h.tipos()):
            clave = (tipo, f.filas_por_hilada)
            if clave not in plantillas:
                pz = pieza(tipo, PASO_VERTICAL)
                Vm, Fm = malla(pz, subdivision)
                Em = etiquetas(pz, Vm, Fm)
                plantillas[clave] = (np.asarray(Vm) * f.escala, Fm, Em, oclusion(pz, Vm, Fm, Em))
            Vp, Fp, Ep, Sp = plantillas[clave]
            base = len(V)
            V.extend(colocar(Vp, f, gradiente, i * fam.paso_tangencial * f.escala * h.estiramiento, h.estiramiento, fam.fondo * f.escala))
            F.extend((a + base, b + base, cc + base) for a, b, cc in Fp)
            E.extend(Ep)
            S.extend(Sp)
        grupos.append((f"frente_{f.indice:02d}_{k:03d}_{h.familia}", V, F, E, S))
    return grupos


def resumen(c: Campo, filas_por_hilada: int = 1) -> list[dict]:
    """Por frente: hilada, largo, piezas y si es anillo o lazo."""
    fuera = []
    for f in frentes(c, filas_por_hilada=filas_por_hilada):
        h = hilada_de(f)
        rodea = bool(_contiene_origen(f.puntos))
        fuera.append({"hilada": f.indice, "fila": f.indice,
                      "hilada_de_referencia": f.indice / f.filas_por_hilada,
                      "cota_frente_catetos": f.indice * f.paso,
                      "procedencia": "cota de modelo; subdividida" if f.filas_por_hilada > 1 else "cota de modelo; paso de referencia",
                      "largo": f.largo, "piezas": h.piezas, "familia": h.familia,
                      "anillo": rodea, "estiramiento": h.estiramiento})
    return fuera


def _contiene_origen(P: np.ndarray) -> bool:
    x, y = P[:, 0], P[:, 1]
    cruza = (y[:-1] > 0) != (y[1:] > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        xc = x[:-1] + (0 - y[:-1]) * (x[1:] - x[:-1]) / (y[1:] - y[:-1])
    return bool(np.sum(cruza & (xc > 0)) % 2)


def piezas_totales(c: Campo, filas_por_hilada: int = 1) -> int:
    return sum(r["piezas"] for r in resumen(c, filas_por_hilada))

