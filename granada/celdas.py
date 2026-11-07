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
- **La sala** (tambor, trompas y muros del cuadrado) sale de granada/sala.py,
  con las medidas de la seccion; las trompas son imitacion.

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
    _MEDIA_OCT,
    CATETO_M,
    PENDIENTE,
    PlantaPoligono,
    radios_desde,
    RADIO_BASE,
    _cupulilla,
    _montar,
    cupulin,
    cupulines_medidos,
    detector_de_marcos,
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
contar las de los cupulines ni las de las esquinas). Ver tests/test_celdas.py."""
MULTIPLO_CELDA = 4
CIERRE_CELDA = 0.9
"""Radio medio (en unidades de pieza) por debajo del cual una celda se cierra
con su cupulilla en vez de con otra hilada."""
MUESTRAS = 720


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


ALTO_PIRAMIDE = 0.45
"""Altura de la piramide de cada celda de esquina respecto a su lado."""
PASO_ESQUINA_M = 0.21
"""Lado de las celdas de la reticula de las esquinas. En la ortoimagen las
trompas son una reticula de flores pequenas en filas paralelas a los muros,
separadas unos 100 px (~0,21 m a 472 px/m)."""


def _recortar(P: list, a: float, t: float) -> list:
    """Sutherland-Hodgman: parte de P con x + y >= a + t."""
    def dentro(p):
        return p[0] + p[1] >= a + t - 1e-9

    fuera = []
    for p, q in zip(P, P[1:] + P[:1]):
        if dentro(p):
            fuera.append(p)
        if dentro(p) != dentro(q):
            u = (a + t - p[0] - p[1]) / ((q[0] - p[0]) + (q[1] - p[1]))
            fuera.append((p[0] + u * (q[0] - p[0]), p[1] + u * (q[1] - p[1])))
    return fuera


def reticula_de_las_esquinas(radio_base: float = RADIO_BASE):
    """Celdas, nudos y aristas de la reticula de las cuatro esquinas entre el
    octogono de arranque y el cuadrado que lo circunscribe (lados del octogono
    a 0, 45, 90... grados). Unidades del cateto, marco de la cupula."""
    a = radio_base / _MEDIA_OCT
    t = a * math.tan(math.pi / 8)
    s = PASO_ESQUINA_M / CATETO_M
    n = int(math.ceil((a - t) / s))
    celdas: list[Celda] = []
    nudos: list[tuple[float, float]] = []
    aristas: set[tuple[tuple[float, float], tuple[float, float]]] = set()
    for k in range(4):
        cg, sg = math.cos(k * math.pi / 2), math.sin(k * math.pi / 2)

        def girar(p):
            return (round(p[0] * cg - p[1] * sg, 6), round(p[0] * sg + p[1] * cg, 6))

        for i in range(n):
            for j in range(n):
                x1, y1 = a - i * s, a - j * s
                x0, y0 = x1 - s, y1 - s
                P = _recortar([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], a, t)
                if len(P) < 3:
                    continue
                Q = np.array([girar(p) for p in P])
                if _area(Q) < 0.15 * s * s:
                    continue
                if _area(Q) < 0:
                    Q = Q[::-1]
                centro = centro_del_nucleo(Q)
                celdas.append(Celda(f"esquina_{k}_{i:02d}_{j:02d}", (float(centro[0]), float(centro[1])),
                                    math.atan2(centro[1], centro[0]), tuple(map(tuple, Q.tolist())), "esquina"))
                for p, q in zip(Q.tolist(), np.roll(Q, -1, axis=0).tolist()):
                    aristas.add(tuple(sorted((tuple(p), tuple(q)))))
                for p in Q.tolist():
                    if (p[0] * cg + p[1] * sg) + (-p[0] * sg + p[1] * cg) > a + t + 1e-6:
                        nudos.append(tuple(p))
    return celdas, sorted(set(nudos)), sorted(aristas)


def celdas_de_las_esquinas(radio_base: float = RADIO_BASE) -> list[Celda]:
    return reticula_de_las_esquinas(radio_base)[0]


ALTURA_FONDO = 4.0
"""Altura, en unidades del cateto, del fondo de yeso sobre el cono."""
NUDO_M = 0.04
"""Radio de las rosetas en los nudos de la red. En la ortoimagen cada cruce de
la red lleva una roseta blanca en relieve de unos 40 px (~8 cm a 472 px/m)."""
CABALLETE_M = 0.018
"""Medio ancho del caballete de yeso sobre cada arista de la red: en la
ortoimagen las lineas de la red son aristas claras y finas."""


def _dentro_del_contorno(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Paridad de cruces contra el contorno de la red registrada."""
    caras = json.loads(CARAS.read_text(encoding="utf-8"))
    red = json.loads(RED.read_text(encoding="utf-8"))
    N = _transformar(np.array(red["nodos"], dtype=float), json.loads(REGISTRO.read_text(encoding="utf-8"))) / CATETO_M
    P = N[caras["contorno"]["vertices"]]
    dentro = np.zeros(len(x), dtype=bool)
    for (x1, y1), (x2, y2) in zip(P, np.roll(P, -1, axis=0)):
        cruza = (y1 > y) != (y2 > y)
        with np.errstate(divide="ignore", invalid="ignore"):
            xc = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
        dentro ^= cruza & (x < xc)
    return dentro


def _cota_cono(x, y, radio_base: float):
    return np.maximum(0.0, (radio_base - np.hypot(x, y)) * PENDIENTE)


def nudos_y_caballetes(radio_base: float = RADIO_BASE, esquinas: bool = True):
    """(V, F, colores, sombras): caballetes sobre las aristas y rosetas en los
    nudos de la red registrada, justo por delante (debajo) de las piezas."""
    red = json.loads(RED.read_text(encoding="utf-8"))
    N = _transformar(np.array(red["nodos"], dtype=float), json.loads(REGISTRO.read_text(encoding="utf-8"))) / CATETO_M
    segmentos = [(N[int(a)], N[int(b)]) for a, b, *_ in red["aristas"]]
    puntos = [tuple(p) for p in N]
    if esquinas:
        _, nudos_e, aristas_e = reticula_de_las_esquinas(radio_base)
        segmentos += [(np.array(p), np.array(q)) for p, q in aristas_e]
        puntos += nudos_e
    V: list[tuple[float, float, float]] = []
    F: list[tuple[int, int, int]] = []
    C: list[str] = []
    S: list[float] = []
    w = CABALLETE_M / CATETO_M
    for pa, pb in segmentos:
        d = pb - pa
        largo = float(np.hypot(*d))
        if largo < 1e-9:
            continue
        nrm = np.array([-d[1], d[0]]) / largo * w
        q = [pa + nrm, pb + nrm, pb - nrm, pa - nrm]
        k = len(V)
        for x, y in q:
            V.append((float(x), float(y), float(_cota_cono(x, y, radio_base)) - 0.04))
        F.extend([(k, k + 2, k + 1), (k, k + 3, k + 2)])
        C.extend(["yeso"] * 2)
        S.extend([1.0] * 2)
    r = NUDO_M / CATETO_M
    lobulos, n = 8, 48
    for x0, y0 in puntos:
        z0 = float(_cota_cono(x0, y0, radio_base)) - 0.05
        k = len(V)
        V.append((float(x0), float(y0), z0 - 0.35 * r))
        for i in range(n):
            phi = 2 * math.pi * i / n
            rr = r * (0.78 + 0.22 * math.cos(lobulos * phi))
            V.append((float(x0 + rr * math.cos(phi)), float(y0 + rr * math.sin(phi)), z0))
        for i in range(n):
            F.append((k, k + 1 + (i + 1) % n, k + 1 + i))
        C.extend(["yeso"] * n)
        S.extend([1.0] * n)
    return V, F, C, S


ROSETA_M = 0.15
"""Radio de la roseta del centro. En la ortoimagen el centro de la estrella
lleva una roseta de unos 16 lobulos con el corazon pardo, de ~140 px (~0,3 m)
de diametro."""


def caras_del_centro() -> tuple[str, set[str]]:
    """La cara central (octogono) y los ocho medios cuadrados que la rodean,
    que en la ortoimagen estan pintados de azul (color de la foto, eleccion)."""
    caras = json.loads(CARAS.read_text(encoding="utf-8"))["caras"]
    centro = min(caras, key=lambda f: math.hypot(*f["centroide_m"]))["id"]
    azules = {f["id"] for f in caras if f.get("figura") == "medio_cuadrado" and math.hypot(*f["centroide_m"]) < 0.8}
    return centro, azules


def _roseta(z: float, e: float, lobulos: int = 16, n: int = 96):
    """Roseta de `lobulos` lobulos en el marco local escalado de una celda,
    abombada hacia abajo, con el corazon pardo. Devuelve (V, F, colores, sombras)."""
    r = ROSETA_M / CATETO_M / e
    V = [(0.0, 0.0, z - 0.25 * r)]
    F, C = [], []
    anillos = (0.35, 1.0)
    for j, f in enumerate(anillos):
        for i in range(n):
            phi = 2 * math.pi * i / n
            rr = r * f * ((0.8 + 0.2 * math.cos(lobulos * phi)) if j else 1.0)
            V.append((rr * math.cos(phi), rr * math.sin(phi), z - 0.25 * r * (1 - f)))
    for i in range(n):
        F.append((0, 1 + (i + 1) % n, 1 + i))
        C.append("almagra")
    for i in range(n):
        a, b = 1 + i, 1 + (i + 1) % n
        F.extend([(a, b, b + n), (a, b + n, a + n)])
        C.extend(["yeso", "yeso"])
    return V, F, C, [1.0] * len(F)


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
    en_marco = detector_de_marcos(huecos, radio_base)

    def en_hueco_mundo(V) -> bool:
        return en_marco(np.asarray(V, dtype=float).mean(axis=0))

    plantillas: dict = {}
    grupos = []
    resumen = []
    centro, azules = caras_del_centro()
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

        if celda.id in azules:
            def pintar(tipo, etiqueta, hilada, indice):
                return "azul" if etiqueta == "fondo" else "yeso"

        locales, _ = _montar(planta, hiladas, subdivision, plantillas, descartar if huecos else None, pintar if color else None)
        if hiladas:
            u = hiladas[-1]
            Vc, Fc = _cupulilla(planta, u.radio_frente, u.cota, u.paso, n=48, m=6)
            clave = u.cota + u.paso * 0.875 + 0.9 * u.radio_frente
        else:
            Vc, Fc = _cupulilla(planta, F0, -0.5, 0.5, n=48, m=6)
            clave = -0.5 + 0.5 * 0.875 + 0.9 * F0
        tono = "azul" if celda.id in azules else "yeso"
        if not (huecos and descartar(Vc)):
            locales.append(("cupulilla", Vc, Fc, [tono] * len(Fc), [0.9] * len(Fc)) if color else ("cupulilla", Vc, Fc))
        if celda.id == centro:
            locales.append(("roseta", *_roseta(clave - 0.05 / e, e)) if color else ("roseta", *_roseta(clave - 0.05 / e, e)[:2]))
        for g in locales:
            nombre, Vg, Fg = g[:3]
            if not Fg:
                continue
            V = _colocar(Vg, celda, e, radio_base)
            grupos.append((f"{celda.id}_{nombre}", V, Fg, *g[3:]))
        resumen.append({"cara": celda.id, "orbita": celda.orbita, "radio_medio": F0 * e, "hiladas": len(hiladas),
                        "piezas": sum(h.piezas for h in hiladas), "esquina": celda.orbita == "esquina"})

    if huecos:
        prof = 2 * plan_de_hiladas(radio_base, planta=planta_por_defecto(radio_base, True))[0].paso * math.cos(math.atan(PENDIENTE))
        mini: dict = {}
        for k, c in enumerate(huecos):
            grupos.append((f"cupulin_{k:02d}", *cupulin(c, prof, plantillas=mini, radio_base=radio_base,
                                                         colorear=colorear_cupulin_disperso if color else None)))
    Vn, Fn, Cn, Sn = nudos_y_caballetes(radio_base, esquinas=False)
    grupos.append(("red_nudos", Vn, Fn, Cn, Sn) if color else ("red_nudos", Vn, Fn))
    # Fondo plano de yeso por encima de la clave: solo se ve por los huecos que
    # dejan las celdas, los marcos y las esquinas (si no, se ve el vacio).
    # Sigue el cono: ALTURA_FONDO por encima dentro de la red (detras de las
    # celdas; un plano alto quedaba tan lejos de la luz que se veia negro) y a
    # ras del cono fuera de ella, donde no hay celdas que lo tapen. Sin fondo
    # en los marcos de los cupulines, que suben mas que el.
    a = radio_base / _MEDIA_OCT
    # Se quita el fondo que toca la boca (cualquier vertice dentro), no el del
    # marco: el marco, mas ancho que una celda de la rejilla, queda por delante
    # y tapa los dientes. Quitarlo en todo el marco dejaba dientes negros fuera;
    # quitarlo solo por el centroide dejaba dientes grises dentro.
    en_boca = detector_de_marcos(huecos, radio_base, escala=1.0)
    m = 192
    xs = np.linspace(-a, a, m + 1)
    t_oct = a * math.tan(math.pi / 8)
    # Cada triangulo toma la altura de la zona de su centroide, con vertices
    # propios: si compartieran vertices entre zonas, los de la frontera
    # quedarian inclinados y se verian como una linea oscura en escalera.
    centros_x, centros_y, tris = [], [], []
    for j in range(m):
        for i in range(m):
            p00 = (xs[i], xs[j])
            p10 = (xs[i + 1], xs[j])
            p01 = (xs[i], xs[j + 1])
            p11 = (xs[i + 1], xs[j + 1])
            for tri in ((p00, p11, p10), (p00, p01, p11)):
                tris.append(tri)
                centros_x.append(sum(p[0] for p in tri) / 3)
                centros_y.append(sum(p[1] for p in tri) / 3)
    cx = np.array(centros_x)
    cy = np.array(centros_y)
    a_ras = (np.abs(cx) + np.abs(cy) <= a + t_oct) & ~_dentro_del_contorno(cx, cy)
    Vf, Ff = [], []
    for tri, ras, x0, y0 in zip(tris, a_ras, cx, cy):
        alto = 0.01 if ras else ALTURA_FONDO
        P = [(float(x), float(y), float(_cota_cono(x, y, radio_base)) + alto) for x, y in tri]
        if huecos and any(en_boca(np.array(v)) for v in P):
            continue
        k = len(Vf)
        Vf.extend(P)
        Ff.append((k, k + 1, k + 2))
    grupos.append(("fondo", Vf, Ff, ["yeso"] * len(Ff), [0.9] * len(Ff)) if color else ("fondo", Vf, Ff))
    # La sala: tambor medido, trompas y muros del cuadrado (granada/sala.py).
    # Sustituye a la reticula plana de las esquinas a la cota del arranque.
    from granada.sala import sala

    for nombre, V, F, C, S in sala(radio_base):
        grupos.append((nombre, V, F, C, S) if color else (nombre, V, F))
    return resumen, grupos
