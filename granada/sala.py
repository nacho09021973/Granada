"""La sala bajo la cupula: muros del cuadrado, trompas y tambor.

Medidas (todas de la seccion de AA-415_23, docs/AA-415_23_seccion.jpg):
- alturas, ancho de la sala, del arco de entrada y de la ventana alta:
  datos/alzado_sala.json (scripts/leer_alzado_sala.py, lectura a ojo con
  margen de unos 10 cm);
- radio (apotema) del tambor: datos/estratificacion_medida.json
  (scripts/medir_estratificacion.py), media de sus tres umbrales.

Que es eleccion:
- las trompas se modelan como escalones (ESCALONES_TROMPA) que avanzan desde la esquina
  del cuadrado hasta el lado diagonal del octogono, con la cara inferior de
  cada escalon cubierta por una reticula de piramides (como las flores de la
  ortoimagen). La forma real de cada trompa de mocarabes no esta leida;
- los huecos (arco de entrada y ventana alta) son paneles oscuros delante del
  muro, no aberturas; la ornamentacion de muros y friso no se modela.

La disposicion general (cuadrado, trompas, tambor con ventanas) es la de la
seccion; Ferrer_5 (maqueta de Contreras) solo se uso para verla en planta,
no para medir.

Unidades del cateto (granada.cupula.CATETO_M), z = 0 en el arranque de la
cupula. Los lados del octogono miran a 0, 45, 90... grados.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from granada.cupula import CATETO_M, RADIO_BASE, _MEDIA_OCT

RAIZ = Path(__file__).resolve().parents[1]
ALZADO = RAIZ / "datos" / "alzado_sala.json"
ESTRATIFICACION = RAIZ / "datos" / "estratificacion_medida.json"

ESCALONES_TROMPA = 16
PASO_RETICULA_M = 0.21
"""Lado de las celdas de la reticula de las trompas: en la ortoimagen las
flores de las esquinas estan separadas unos 100 px (~0,21 m)."""
ALTO_PIRAMIDE = 0.45
NUDO_M = 0.04
CABALLETE_M = 0.018


def medidas() -> dict:
    a = json.loads(ALZADO.read_text(encoding="utf-8"))
    e = json.loads(ESTRATIFICACION.read_text(encoding="utf-8"))
    radio_tambor_m = float(np.mean([u["radio_tambor_m"] for u in e["umbrales"].values()]))
    n = {k: v["z_cateto"] for k, v in a["niveles"].items()}
    w = {k: v["cateto"] for k, v in a["anchos"].items()}
    return {
        "suelo": n["suelo"],
        "pie_trompas": n["pie_trompas"],
        "pie_friso": n["pie_friso_tambor"],
        "clave_arco": n["clave_arco_grande"],
        "luz_arco": w["arco_grande"],
        "remate_ventana": n["remate_ventana_alta"],
        "pie_ventana": n["pie_ventana_alta"],
        "luz_ventana": w["ventana_alta"],
        "medio_lado": w["sala"] / 2,
        "apotema_tambor": radio_tambor_m / CATETO_M,
    }


class _Malla:
    def __init__(self):
        self.V: list[tuple[float, float, float]] = []
        self.F: list[tuple[int, int, int]] = []
        self.C: list[str] = []
        self.S: list[float] = []

    def poligono(self, P, color="yeso", luz=0.95):
        """Abanico desde el primer vertice (P convexo, en orden)."""
        k = len(self.V)
        self.V.extend((float(x), float(y), float(z)) for x, y, z in P)
        for i in range(1, len(P) - 1):
            self.F.append((k, k + i, k + i + 1))
            self.C.append(color)
            self.S.append(luz)

    def grupo(self):
        return self.V, self.F, self.C, self.S


def _octogono(apotema: float) -> np.ndarray:
    a = np.radians(22.5 + 45 * np.arange(8))
    r = apotema / math.cos(math.pi / 8)
    return np.stack([r * np.cos(a), r * np.sin(a)], axis=1)


def tambor(m: dict):
    """Muro octogonal del tambor, del pie del friso al arranque."""
    out = _Malla()
    O = _octogono(m["apotema_tambor"])
    # Cada lado en 48 tramos: render_cycles.py interpola el radio del tambor
    # entre vertices para colocar las ventanas, y con solo las esquinas las
    # dejaba detras del muro.
    for p, q in zip(O, np.roll(O, -1, axis=0)):
        for i in range(48):
            a, b = p + (q - p) * i / 48, p + (q - p) * (i + 1) / 48
            out.poligono([(*a, m["pie_friso"]), (*b, m["pie_friso"]), (*b, 0.0), (*a, 0.0)])
    return out.grupo()


def cornisa(m: dict, radio_base: float = RADIO_BASE):
    """Corona horizontal en el arranque, entre el tambor y la cupula (mas
    estrecha). Grupo aparte: en la vista ortogonal se ve, el tambor no."""
    out = _Malla()
    O = _octogono(m["apotema_tambor"])
    I = _octogono(radio_base / _MEDIA_OCT)
    for (p, q), (pi, qi) in zip(zip(O, np.roll(O, -1, axis=0)), zip(I, np.roll(I, -1, axis=0))):
        out.poligono([(*p, 0.0), (*q, 0.0), (*qi, 0.0), (*pi, 0.0)], luz=1.0)
    return out.grupo()


def _recortar(P: list, a: float, b: float, c: float) -> list:
    """Sutherland-Hodgman: parte de P con a x + b y >= c."""
    def dentro(p):
        return a * p[0] + b * p[1] >= c - 1e-9

    fuera = []
    for p, q in zip(P, P[1:] + P[:1]):
        if dentro(p):
            fuera.append(p)
        if dentro(p) != dentro(q):
            u = (c - a * p[0] - b * p[1]) / (a * (q[0] - p[0]) + b * (q[1] - p[1]))
            fuera.append((p[0] + u * (q[0] - p[0]), p[1] + u * (q[1] - p[1])))
    return fuera


def _area(P) -> float:
    P = np.asarray(P)
    return 0.5 * float(np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1]))


def trompas(m: dict):
    """Cuatro trompas escalonadas. Devuelve (V, F, colores, sombras)."""
    out = _Malla()
    H = m["medio_lado"]
    D_tambor = m["apotema_tambor"] * (1 + math.tan(math.pi / 8))
    D_esquina = 2 * H
    n = ESCALONES_TROMPA
    dz = (m["pie_friso"] - m["pie_trompas"]) / n
    s = PASO_RETICULA_M / CATETO_M
    w = CABALLETE_M / CATETO_M
    rn = NUDO_M / CATETO_M
    celdas_lado = int(math.ceil((D_esquina - D_tambor) / s)) + 2
    for k in range(4):
        cg, sg = math.cos(k * math.pi / 2), math.sin(k * math.pi / 2)

        def girar(x, y):
            return x * cg - y * sg, x * sg + y * cg

        for i in range(n):
            D_lejos = D_esquina - i * (D_esquina - D_tambor) / n
            D_cerca = D_esquina - (i + 1) * (D_esquina - D_tambor) / n
            z = m["pie_trompas"] + i * dz
            # Cara inferior del escalon: banda D_cerca <= x + y <= D_lejos.
            for a in range(celdas_lado):
                for b in range(celdas_lado):
                    x1, y1 = H - a * s, H - b * s
                    P = [(x1 - s, y1 - s), (x1, y1 - s), (x1, y1), (x1 - s, y1)]
                    P = _recortar(P, 1.0, 1.0, D_cerca)
                    if len(P) >= 3:
                        P = _recortar(P, -1.0, -1.0, -D_lejos)
                    if len(P) < 3 or _area(P) < 0.05 * s * s:
                        continue
                    cx = sum(p[0] for p in P) / len(P)
                    cy = sum(p[1] for p in P) / len(P)
                    alto = ALTO_PIRAMIDE * math.sqrt(_area(P))
                    Q = [girar(*p) for p in P]
                    ap = girar(cx, cy)
                    base = len(out.V)
                    out.V.extend((x, y, z) for x, y in Q)
                    out.V.append((ap[0], ap[1], z + alto))
                    for j in range(len(Q)):
                        out.F.append((base + j, base + len(Q), base + (j + 1) % len(Q)))
                        out.C.append("yeso")
                        out.S.append(0.9)
                    for p, q in zip(Q, Q[1:] + Q[:1]):
                        # Solo las aristas de la reticula, paralelas a los muros:
                        # las del recorte diagonal pintaban rayas.
                        if min(abs(q[0] - p[0]), abs(q[1] - p[1])) < 1e-6:
                            _caballete(out, p, q, z - 0.03, w)
                    for p in Q:
                        _nudo(out, p, z - 0.04, rn)
            # Contrahuella: muro vertical en x + y = D_cerca, de z a z + dz,
            # entre los dos muros del cuadrado.
            t = D_cerca - H
            p, q = girar(H, t), girar(t, H)
            out.poligono([(*p, z), (*q, z), (*q, z + dz), (*p, z + dz)], luz=0.85)
    return out.grupo()


def _caballete(out: _Malla, p, q, z, w):
    d = np.subtract(q, p)
    largo = float(np.hypot(*d))
    if largo < 1e-9:
        return
    nrm = np.array([-d[1], d[0]]) / largo * w
    out.poligono([(*(np.add(p, nrm)), z), (*(np.add(q, nrm)), z), (*(np.subtract(q, nrm)), z), (*(np.subtract(p, nrm)), z)], luz=1.0)


def _nudo(out: _Malla, p, z, r, lobulos: int = 8, n: int = 24):
    base = len(out.V)
    out.V.append((p[0], p[1], z - 0.35 * r))
    for i in range(n):
        phi = 2 * math.pi * i / n
        rr = r * (0.78 + 0.22 * math.cos(lobulos * phi))
        out.V.append((p[0] + rr * math.cos(phi), p[1] + rr * math.sin(phi), z))
    for i in range(n):
        out.F.append((base, base + 1 + (i + 1) % n, base + 1 + i))
        out.C.append("yeso")
        out.S.append(1.0)


def _arco(cx: float, ancho: float, abajo: float, clave: float, n: int = 24):
    """Contorno de un hueco de medio punto (x, z) en el plano del muro."""
    r = ancho / 2
    arranque = clave - r
    P = [(cx - r, abajo), (cx + r, abajo)]
    for i in range(n + 1):
        t = math.pi * i / n
        P.append((cx + r * math.cos(t), arranque + r * math.sin(t)))
    return P


def muros(m: dict):
    """Cuatro muros del cuadrado, del suelo al pie del friso, con el arco de
    entrada y la ventana alta como paneles oscuros, y el suelo."""
    out = _Malla()
    H = m["medio_lado"]
    abajo, arriba = m["suelo"], m["pie_friso"]
    for k in range(4):
        cg, sg = math.cos(k * math.pi / 2), math.sin(k * math.pi / 2)

        def en_muro(u, z, dentro=0.0):
            # Muro en x = H (antes de girar); u a lo largo del muro.
            x, y = H - dentro, u
            return (x * cg - y * sg, x * sg + y * cg, z)

        out.poligono([en_muro(-H, abajo), en_muro(H, abajo), en_muro(H, arriba), en_muro(-H, arriba)], luz=0.9)
        for P in (
            _arco(0.0, m["luz_arco"], abajo, m["clave_arco"]),
            _arco(0.0, m["luz_ventana"], m["pie_ventana"], m["remate_ventana"]),
        ):
            # Abanico desde el centro del hueco (convexo).
            cx = sum(p[0] for p in P) / len(P)
            cz = sum(p[1] for p in P) / len(P)
            orden = sorted(P, key=lambda p: math.atan2(p[1] - cz, p[0] - cx))
            out.poligono([en_muro(cx, cz, 0.03)] + [en_muro(u, z, 0.03) for u, z in orden] + [en_muro(*orden[0], 0.03)],
                         color="hueco", luz=1.0)
    out.poligono([(H, H, abajo), (H, -H, abajo), (-H, -H, abajo), (-H, H, abajo)], luz=0.8)
    return out.grupo()


def sofito(m: dict):
    """Techo horizontal entre el tambor y el cuadrado, al pie del friso."""
    out = _Malla()
    H = m["medio_lado"]
    arriba = m["pie_friso"]
    # Sofito: cuadrado menos octogono del tambor, a la cota del pie del friso.
    # Cuatro rectangulos frente a los lados axiales y cuatro pentagonos en las
    # esquinas (tapados casi del todo por las trompas).
    A = m["apotema_tambor"]
    t = A * math.tan(math.pi / 8)
    zs = arriba + 0.02
    for k in range(4):
        cg, sg = math.cos(k * math.pi / 2), math.sin(k * math.pi / 2)

        def g(x, y):
            return (x * cg - y * sg, x * sg + y * cg, zs)

        out.poligono([g(A, -t), g(H, -t), g(H, t), g(A, t)], luz=0.9)
        out.poligono([g(A, t), g(H, t), g(H, H), g(t, H), g(t, A)], luz=0.9)
    return out.grupo()


def sala(radio_base: float = RADIO_BASE):
    """Grupos (nombre, V, F, colores, sombras) de la arquitectura."""
    m = medidas()
    return [
        ("tambor", *tambor(m)),
        ("sala_cornisa", *cornisa(m, radio_base)),
        ("sala_sofito", *sofito(m)),
        ("sala_trompas", *trompas(m)),
        ("sala_muros", *muros(m)),
    ]
