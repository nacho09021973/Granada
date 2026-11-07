"""Cupula por piezas montada sobre la red de medinas.

Que es dato y que es eleccion
-----------------------------
- **La red** (datos/red_medinas.json, datos/caras_red.json): la planta de la
  figura 128 de la tesis de Ferrer, 105 caras. Su mitad inferior se genero por
  reflexion (completar_red_medinas.py): el espejo esta impuesto en la planta.
- **Su registro** en el marco de la cupula (datos/registro_red.json,
  scripts/registrar_red_cupulines.py): escala y giro que meten cada cupulin en
  una celda. La escala concuerda con el radio de arranque medido; el signo del
  giro no esta resuelto.
- **El relleno de cada celda es eleccion.** Ninguna fuente dice que pieza va en
  cada sitio (decision 0016). Cada cara se rellena como una cupulita: hiladas
  de piezas del alfabeto de Jones y Goury que se cierran hacia el punto mas
  alejado de sus bordes, como los cupulines de granada/cupula.py.
- **La altura** es la del cono medido (PENDIENTE, RADIO_BASE): cada celda se
  posa sobre el cono y sus hiladas suben desde el.

Cada cara es estrellada respecto a ese punto (comprobado: las 105 tienen
nucleo), asi que su contorno se describe como r(phi) desde el y las hiladas
interiores son copias homoteticas del contorno.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from granada.cupula import (
    CATETO_M,
    MARCO_CUPULIN,
    PENDIENTE,
    RADIO_BASE,
    _cupulilla,
    _montar,
    _tambor_friso,
    cupulin,
    cupulines_medidos,
    plan_de_hiladas,
    planta_por_defecto,
)

RAIZ = Path(__file__).resolve().parents[1]
RED = RAIZ / "datos" / "red_medinas.json"
CARAS = RAIZ / "datos" / "caras_red.json"
REGISTRO = RAIZ / "datos" / "registro_red.json"
ORBITAS = RAIZ / "datos" / "orbitas_c8.json"

ESCALA_CELDA = 0.475
"""Tamano de las piezas de las celdas respecto a las de la cupula por anillos.
Eleccion calibrada por recuento: Jones y Goury cuentan 5416 piezas en la
cupula (docs/fuentes.md, entrada 18). Con el registro de
datos/registro_red.json: 0,47 da 5604, 0,475 da 5392 y 0,48 da 5296 (sin
contar las de los cupulines). Ver tests/test_celdas.py."""
MULTIPLO_CELDA = 4
CIERRE_CELDA = 0.9
"""Radio medio (en unidades de pieza) por debajo del cual una celda se cierra
con su cupulilla en vez de con otra hilada."""
MUESTRAS = 720


@dataclass(frozen=True)
class PlantaPoligono:
    """Contorno de una cara como r(phi) desde un punto de su nucleo.

    Misma interfaz que granada.cupula.Planta (forma, punto, arco), con las
    hiladas interiores homoteticas: r = F * rho(phi) / radio_base.
    """

    rho: tuple[float, ...]
    radio_base: float
    radio_cierre: float
    estrella: bool = False

    def forma(self, phi, F):
        phi = np.mod(np.asarray(phi, dtype=float), 2 * math.pi)
        tabla = np.asarray(self.rho)
        malla = np.linspace(0, 2 * math.pi, len(tabla), endpoint=False)
        return np.interp(phi, malla, tabla, period=2 * math.pi) / self.radio_base

    def punto(self, phi, F):
        r = np.asarray(F) * self.forma(phi, F)
        return r * np.cos(phi), r * np.sin(phi)

    def arco(self, F):
        phi = np.linspace(0, 2 * math.pi, MUESTRAS + 1)
        x, y = self.punto(phi, np.full_like(phi, F))
        s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
        return s, phi, float(s[-1])


def _area(P: np.ndarray) -> float:
    return 0.5 * float(np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]))


def centro_del_nucleo(P: np.ndarray, rejilla: int = 48, rondas: int = 3) -> np.ndarray:
    """Punto del nucleo mas alejado de las rectas de los lados (P en sentido antihorario)."""
    A, B = P, np.roll(P, -1, axis=0)
    d = B - A
    nrm = np.stack([-d[:, 1], d[:, 0]], axis=1)
    nrm /= np.linalg.norm(nrm, axis=1)[:, None]
    lo, hi = P.min(axis=0), P.max(axis=0)
    mejor = P.mean(axis=0)
    for _ in range(rondas):
        g = np.stack(np.meshgrid(np.linspace(lo[0], hi[0], rejilla), np.linspace(lo[1], hi[1], rejilla)), -1).reshape(-1, 2)
        s = ((g[:, None, :] - A[None]) * nrm[None]).sum(-1).min(axis=1)
        mejor = g[int(np.argmax(s))]
        paso = (hi - lo) / rejilla
        lo, hi = mejor - 2 * paso, mejor + 2 * paso
    return mejor


def radios_desde(P: np.ndarray, c: np.ndarray, n: int = MUESTRAS) -> np.ndarray:
    """r(phi) del contorno P visto desde c, en n angulos (cara estrellada en c)."""
    phi = np.linspace(0, 2 * math.pi, n, endpoint=False)
    u = np.stack([np.cos(phi), np.sin(phi)], axis=1)
    A, B = P - c, np.roll(P, -1, axis=0) - c
    D = B - A
    r = np.full(n, np.inf)
    for a, dd in zip(A, D):
        den = u[:, 0] * dd[1] - u[:, 1] * dd[0]
        ok = np.abs(den) > 1e-12
        t = np.where(ok, (a[0] * dd[1] - a[1] * dd[0]) / np.where(ok, den, 1), np.inf)
        s = np.where(ok, (a[0] * u[:, 1] - a[1] * u[:, 0]) / np.where(ok, den, 1), -1)
        valido = ok & (t > 1e-9) & (s >= -1e-9) & (s <= 1 + 1e-9)
        r = np.where(valido & (t < r), t, r)
    return r


@dataclass(frozen=True)
class Celda:
    id: str
    centro: tuple[float, float]
    """Centro del nucleo, en unidades del cateto, marco de la cupula."""
    giro: float
    """Angulo del centro: el marco local de la celda mira hacia fuera."""
    poligono: tuple[tuple[float, float], ...]
    """Contorno en unidades del cateto, marco de la cupula, antihorario."""
    orbita: str


def _transformar(P: np.ndarray, registro: dict) -> np.ndarray:
    Q = P.copy()
    if registro["espejo_y"]:
        Q[:, 1] = -Q[:, 1]
    a = math.radians(registro["giro_grados"])
    c, s = math.cos(a), math.sin(a)
    return registro["escala"] * Q @ np.array([[c, s], [-s, c]])


def celdas_de_la_red() -> list[Celda]:
    nodos = np.array(json.loads(RED.read_text(encoding="utf-8"))["nodos"], dtype=float)
    caras = json.loads(CARAS.read_text(encoding="utf-8"))["caras"]
    registro = json.loads(REGISTRO.read_text(encoding="utf-8"))
    orbitas = {}
    for o in json.loads(ORBITAS.read_text(encoding="utf-8"))["orbitas"]:
        for c in o["caras"]:
            orbitas[c] = o["representante"]
    N = _transformar(nodos, registro) / CATETO_M
    fuera = []
    for f in caras:
        P = N[f["vertices"]]
        if _area(P) < 0:
            P = P[::-1]
        c = centro_del_nucleo(P)
        fuera.append(Celda(f["id"], (float(c[0]), float(c[1])), math.atan2(c[1], c[0]),
                           tuple(map(tuple, P.tolist())), orbitas.get(f["id"], f["id"])))
    return fuera


def _colocar(local, celda: Celda, e: float, radio_base: float) -> list[tuple[float, float, float]]:
    """Del marco local escalado de la celda al de la cupula, posado en el cono."""
    L = np.asarray(local, dtype=float)
    cg, sg = math.cos(celda.giro), math.sin(celda.giro)
    x = celda.centro[0] + e * (L[:, 0] * cg - L[:, 1] * sg)
    y = celda.centro[1] + e * (L[:, 0] * sg + L[:, 1] * cg)
    base = np.maximum(0.0, (radio_base - np.hypot(x, y)) * PENDIENTE)
    return list(zip(x.tolist(), y.tolist(), (base + e * L[:, 2]).tolist()))


def cupula_red(subdivision: int = 6, color: bool = False, radio_base: float = RADIO_BASE, con_cupulines: bool = True):
    """Grupos como granada.cupula.cupula: (nombre, V, F[, colores, sombras]).

    Devuelve tambien un resumen por celda (hiladas y piezas)."""
    from granada.color import _celdilla, colorear_cupulin_disperso

    e = ESCALA_CELDA
    huecos = cupulines_medidos() if con_cupulines else []
    marcos = [(c.marco(radio_base), c.radio * MARCO_CUPULIN) for c in huecos]

    def en_hueco_mundo(V) -> bool:
        P = np.asarray(V, dtype=float).mean(axis=0)
        for (o, e1, e2, n), r in marcos:
            d = P - o
            if math.hypot(d @ e1, d @ e2) < r and -4.0 < d @ n < 7.0:
                return True
        return False

    plantillas: dict = {}
    grupos = []
    resumen = []
    for celda in celdas_de_la_red():
        cx, cy = celda.centro
        cg, sg = math.cos(-celda.giro), math.sin(-celda.giro)
        P = np.asarray(celda.poligono) - np.array([cx, cy])
        local = np.stack([P[:, 0] * cg - P[:, 1] * sg, P[:, 0] * sg + P[:, 1] * cg], axis=1) / e
        rho = radios_desde(local, np.zeros(2))
        F0 = float(rho.mean())
        planta = PlantaPoligono(tuple(rho.tolist()), F0, CIERRE_CELDA)
        hiladas = plan_de_hiladas(F0, planta=planta, cierre=CIERRE_CELDA, multiplo=MULTIPLO_CELDA)

        def descartar(V, celda=celda):
            return en_hueco_mundo(_colocar(V, celda, e, radio_base))

        def pintar(tipo, etiqueta, hilada, indice, celda=celda):
            return _celdilla(tipo, etiqueta, hilada, indice, f"celda_{celda.orbita}")

        locales, _ = _montar(planta, hiladas, subdivision, plantillas, descartar if huecos else None, pintar if color else None)
        if hiladas:
            u = hiladas[-1]
            Vc, Fc = _cupulilla(planta, u.radio_frente, u.cota, u.paso, n=48, m=6)
        else:
            Vc, Fc = _cupulilla(planta, F0, -0.5, 0.5, n=48, m=6)
        if not (huecos and descartar(Vc)):
            locales.append(("cupulilla", Vc, Fc, ["yeso"] * len(Fc), [0.9] * len(Fc)) if color else ("cupulilla", Vc, Fc))
        for g in locales:
            nombre, Vg, Fg = g[:3]
            if not Fg:
                continue
            V = _colocar(Vg, celda, e, radio_base)
            grupos.append((f"{celda.id}_{nombre}", V, Fg, *g[3:]))
        resumen.append({"cara": celda.id, "orbita": celda.orbita, "radio_medio": F0 * e, "hiladas": len(hiladas),
                        "piezas": sum(h.piezas for h in hiladas)})

    if huecos:
        prof = 2 * plan_de_hiladas(radio_base, planta=planta_por_defecto(radio_base, True))[0].paso * math.cos(math.atan(PENDIENTE))
        mini: dict = {}
        for k, c in enumerate(huecos):
            grupos.append((f"cupulin_{k:02d}", *cupulin(c, prof, plantillas=mini, radio_base=radio_base,
                                                         colorear=colorear_cupulin_disperso if color else None)))
    if color:
        grupos.append(("tambor", *_tambor_friso(planta_por_defecto(radio_base, True), radio_base, 0.0)))
    return resumen, grupos
