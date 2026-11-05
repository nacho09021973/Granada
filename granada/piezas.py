"""Los siete prismas de mocarabe de Jones y Goury, como solidos 3D.

Fuente: lamina X de Jones y Goury (1842-45), reproducida en la fig. 5 de Gamiz
Gordo y Ferrer Perez-Blanco, *VLC arquitectura* 6(2), 2019, p. 71
(`docs/2019VLCGAMIZ_FERRER_MUQARNASALHAMBRA.pdf`, pagina 15 del PDF). Texto de
la lamina, transcrito en p. 69-70 del articulo: siete formas, de tres figuras
en planta -triangulo rectangulo A, rectangulo B, triangulo isosceles C de 45
grados-; B una forma, A tres, C tres; C3 es el rombo del isosceles doble.

Que es fuente y que es modelo
-----------------------------
Fuente:
- las tres figuras en planta y sus angulos (A medio cuadrado, C isosceles de
  45 grados, C3 rombo de dos C unidos por el lado menor);
- que A3 y C3 ascienden dos niveles y el resto uno (articulo, p. 70);
- la vista frontal de cada prisma en el grabado: trompeta con la pata en el eje
  (A1, A3, C1, C3), arco con las patas en las esquinas (A2, C2), curva de fondo
  a frente (B), nicho de medio punto (A3) y apuntado (C3) en el nivel superior;
- la curva: la plantilla mayor de `granada.perfil` (cima a 7P, nivel a 8P).

Modelo, declarado y no medido:
- el solido es la planta extruida en vertical y recortada por debajo con una
  superficie z = f(x, y). La silueta del grabado se extruye en profundidad, que
  es la lectura literal de una vista frontal; el oficio real no esta obligado a
  ello;
- el ancho de la pata, la altura del prisma (dos pasos de nivel), la anchura y
  profundidad del nicho y la forma exacta de su arco son parametros elegidos a
  ojo sobre el grabado;
- la doble curva de C3 (doble perfil) no se modela.

Ejes locales: x a lo ancho, y hacia el frente (el frente de la pieza esta en
y = 0 y la pieza queda en y <= 0), z hacia arriba con la pata en z = 0. La
unidad es el cateto del medio cuadrado A.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable

from granada.perfil import MAYOR, PlantillaPerfil

Punto2 = tuple[float, float]
Punto3 = tuple[float, float, float]

PASO_NIVEL = 1.6
"""Altura de un nivel en unidades del cateto. Elegida a ojo sobre el grabado:
la curva de A1 mide alli lo mismo que su hipotenusa."""

ALTURA_PRISMA = 2 * PASO_NIVEL
"""Todas las piezas miden lo mismo en el grabado; las de dos niveles usan la
parte alta para el nicho."""

MEDIA_PATA = 0.05
"""Medio ancho de la pata, en unidades del cateto. Parametro."""

SUBDIVISION = 40

BORDE_NICHO = 0.04
"""Ancho de la transicion entre el nicho y el resto del fondo. Evita un salto
vertical que la rejilla triangular no puede representar sin astillas."""

S22 = math.sin(math.radians(22.5))
C22 = math.cos(math.radians(22.5))
R2 = math.sqrt(2) / 2

TIPOS = ("A1", "A2", "A3", "B", "C1", "C2", "C3")
NIVELES = {"A1": 1, "A2": 1, "A3": 2, "B": 1, "C1": 1, "C2": 1, "C3": 2}


def _tabla_curva(plantilla: PlantillaPerfil, muestras: int = 64) -> list[float]:
    return [
        1.0 - float(plantilla.altura_normalizada(Fraction(muestras - i, muestras)))
        for i in range(muestras + 1)
    ]


_CURVA = _tabla_curva(MAYOR)
FRACCION_UTIL = float(MAYOR.fraccion_util)


def curva(t: float) -> float:
    """Curva x del grabado, normalizada: 0 en la pata, 1 en el arranque del prisma.

    Vertical junto a la pata y tendida arriba. Es 1 - h(1 - t) con h la
    plantilla mayor de `granada.perfil`, interpolada en 64 tramos.
    """
    t = min(1.0, max(0.0, t))
    pos = t * (len(_CURVA) - 1)
    i = min(int(pos), len(_CURVA) - 2)
    f = pos - i
    return _CURVA[i] + f * (_CURVA[i + 1] - _CURVA[i])


def _trompeta(media_anchura: float, paso: float) -> Callable[[float, float], float]:
    """Pata en el eje x = 0; la curva sube hacia los dos lados."""
    alto = paso * FRACCION_UTIL

    def z(x: float, y: float) -> float:
        return alto * curva((abs(x) - MEDIA_PATA) / (media_anchura - MEDIA_PATA))

    return z


def _arco(media_anchura: float, paso: float) -> Callable[[float, float], float]:
    """Patas en los extremos x = +-W; el arco sube hacia el eje."""
    alto = paso * FRACCION_UTIL

    def z(x: float, y: float) -> float:
        return alto * curva(
            (media_anchura - abs(x) - MEDIA_PATA) / (media_anchura - MEDIA_PATA)
        )

    return z


def _nicho(
    base: Callable[[float, float], float],
    media_luz: float,
    desde_y: float,
    apuntado: bool,
    paso: float,
) -> Callable[[float, float], float]:
    """Nicho del segundo nivel, abierto por debajo, en la parte delantera.

    El arco se dibuja en planta con la luz dada y se escala en vertical con
    paso / PASO_NIVEL, para que el nicho quepa en el prisma con cualquier paso.
    """
    arranque = paso * 1.25
    radio = 1.5 * media_luz
    k = paso / PASO_NIVEL

    def techo(x: float) -> float:
        r = abs(x)
        if apuntado:
            centro = radio - media_luz
            return arranque + k * math.sqrt(max(0.0, radio * radio - (r + centro) ** 2))
        return arranque + k * math.sqrt(max(0.0, media_luz * media_luz - r * r))

    def peso(d: float) -> float:
        """1 dentro del nicho, 0 fuera, con transicion lineal de ancho BORDE_NICHO."""
        return min(1.0, max(0.0, d / BORDE_NICHO))

    def z(x: float, y: float) -> float:
        abajo = base(x, y)
        w = min(peso(media_luz - abs(x)), peso(y - desde_y))
        if w <= 0:
            return abajo
        alto = techo(min(abs(x), media_luz - BORDE_NICHO))
        return max(abajo, abajo + w * (alto - abajo))

    return z


def _curva_fondo_frente(fondo: float, paso: float) -> Callable[[float, float], float]:
    """B: pata a lo largo del lado trasero; la curva sube hacia el frente."""
    alto = paso * FRACCION_UTIL

    def z(x: float, y: float) -> float:
        d = y - fondo
        return alto * curva((d - MEDIA_PATA) / (-fondo - MEDIA_PATA))

    return z


@dataclass(frozen=True)
class Pieza:
    tipo: str
    planta: tuple[Punto2, ...]
    """Poligono convexo en sentido antihorario."""
    niveles: int
    fondo: Callable[[float, float], float]
    """Cota de la cara inferior en cada punto de la planta."""
    altura: float = ALTURA_PRISMA


def pieza(tipo: str, paso: float = PASO_NIVEL) -> Pieza:
    """El prisma `tipo` con altura de nivel `paso` (el prisma mide 2 * paso)."""
    h = 2 * paso
    a_frente = ((-R2, 0.0), (0.0, -R2), (R2, 0.0))
    a_vertice = ((0.0, 0.0), (-R2, -R2), (R2, -R2))
    c_frente = ((-S22, 0.0), (0.0, -C22), (S22, 0.0))
    c_vertice = ((0.0, 0.0), (-S22, -C22), (S22, -C22))
    # Diagonal larga a lo ancho y vertice obtuso al frente, como en el grabado
    # (C3 es alli la pieza mas ancha) y en la leyenda de la fig. 5.
    rombo = ((0.0, 0.0), (-C22, -S22), (0.0, -2 * S22), (C22, -S22))
    rect = ((-R2, 0.0), (-R2, -1.0), (R2, -1.0), (R2, 0.0))
    if tipo == "A1":
        return Pieza(tipo, a_frente, 1, _trompeta(R2, paso), h)
    if tipo == "A2":
        return Pieza(tipo, a_vertice, 1, _arco(R2, paso), h)
    if tipo == "A3":
        return Pieza(tipo, a_frente, 2, _nicho(_trompeta(R2, paso), 0.68 * R2, -0.45 * R2, False, paso), h)
    if tipo == "B":
        return Pieza(tipo, rect, 1, _curva_fondo_frente(-1.0, paso), h)
    if tipo == "C1":
        return Pieza(tipo, c_frente, 1, _trompeta(S22, paso), h)
    if tipo == "C2":
        return Pieza(tipo, c_vertice, 1, _arco(S22, paso), h)
    if tipo == "C3":
        return Pieza(tipo, rombo, 2, _nicho(_trompeta(C22, paso), 0.6 * C22, -S22, True, paso), h)
    raise ValueError(f"tipo desconocido: {tipo!r}; los siete son {TIPOS}")


# --------------------------------------------------------------------------
# Malla


def _rejilla(a: Punto2, b: Punto2, c: Punto2, n: int):
    """Subdivide el triangulo abc en n*n triangulos; devuelve puntos y caras."""
    puntos: list[Punto2] = []
    indice: dict[tuple[int, int], int] = {}
    for i in range(n + 1):
        for j in range(n + 1 - i):
            u, v = i / n, j / n
            w = 1 - u - v
            indice[(i, j)] = len(puntos)
            puntos.append((w * a[0] + u * b[0] + v * c[0], w * a[1] + u * b[1] + v * c[1]))
    caras = []
    for i in range(n):
        for j in range(n - i):
            caras.append((indice[(i, j)], indice[(i + 1, j)], indice[(i, j + 1)]))
            if j < n - i - 1:
                caras.append((indice[(i + 1, j)], indice[(i + 1, j + 1)], indice[(i, j + 1)]))
    return puntos, caras


def malla(p: Pieza, n: int = SUBDIVISION) -> tuple[list[Punto3], list[tuple[int, int, int]]]:
    """Solido cerrado: tapa, fondo curvo y paredes. Normales hacia fuera."""
    V: list[Punto3] = []
    F: list[tuple[int, int, int]] = []
    planta = p.planta
    o = planta[0]
    for k in range(1, len(planta) - 1):
        puntos, caras = _rejilla(o, planta[k], planta[k + 1], n)
        base = len(V)
        for x, y in puntos:
            V.append((x, y, p.altura))
        for a, b, c in caras:
            F.append((base + a, base + b, base + c))
        base = len(V)
        for x, y in puntos:
            V.append((x, y, p.fondo(x, y)))
        for a, b, c in caras:
            F.append((base + a, base + c, base + b))
    m = len(planta)
    for k in range(m):
        a, b = planta[k], planta[(k + 1) % m]
        for s in range(n):
            t0, t1 = s / n, (s + 1) / n
            p0 = (a[0] + t0 * (b[0] - a[0]), a[1] + t0 * (b[1] - a[1]))
            p1 = (a[0] + t1 * (b[0] - a[0]), a[1] + t1 * (b[1] - a[1]))
            base = len(V)
            V.extend(
                [
                    (p0[0], p0[1], p.fondo(*p0)),
                    (p1[0], p1[1], p.fondo(*p1)),
                    (p1[0], p1[1], p.altura),
                    (p0[0], p0[1], p.altura),
                ]
            )
            F.append((base, base + 1, base + 2))
            F.append((base, base + 2, base + 3))
    return soldar(V, F)


def etiquetas(p: Pieza, V, F, tolerancia: float = 1e-9) -> list[str]:
    """Clasifica cada triangulo de `malla(p)`: 'pared', 'tapa' o 'fondo'.

    Pared: sus tres vertices estan sobre un mismo lado del poligono de planta.
    Tapa: los tres a la altura del prisma. Fondo: el resto, la cara curva.
    """
    lados = [(p.planta[k], p.planta[(k + 1) % len(p.planta)]) for k in range(len(p.planta))]

    def en_lado(v, a, b) -> bool:
        cruz = (b[0] - a[0]) * (v[1] - a[1]) - (b[1] - a[1]) * (v[0] - a[0])
        return abs(cruz) < tolerancia * 1e3

    fuera = []
    for tri in F:
        vs = [V[i] for i in tri]
        if any(all(en_lado(v, a, b) for v in vs) for a, b in lados):
            fuera.append("pared")
        elif all(abs(v[2] - p.altura) < tolerancia for v in vs):
            fuera.append("tapa")
        else:
            fuera.append("fondo")
    return fuera


SOMBRA_PARED = 0.6
SOMBRA_TAPA = 0.5


def oclusion(p: Pieza, V, F, etiqueta: list[str]) -> list[float]:
    """Factor de luz por triangulo (1 = sin sombra). Eleccion estetica.

    Imita la oclusion ambiental de una celdilla: en el fondo curvo, cuanto mas
    sube dentro de la pieza, menos luz le llega; las paredes quedan en
    penumbra, porque en la cupula montada son el fondo de las juntas entre
    hiladas, y las tapas casi no se ven.
    """
    paso = p.altura / 2
    fuera = []
    for tri, e in zip(F, etiqueta):
        if e == "pared":
            fuera.append(SOMBRA_PARED)
        elif e == "tapa":
            fuera.append(SOMBRA_TAPA)
        else:
            t = sum(V[i][2] for i in tri) / 3 / paso
            fuera.append(max(0.45, 1.0 - 0.32 * t))
    return fuera


def soldar(V, F, decimales: int = 9):
    """Funde vertices coincidentes y quita triangulos degenerados."""
    clave: dict[tuple[float, float, float], int] = {}
    nuevo: list[int] = []
    W: list[Punto3] = []
    for v in V:
        k = tuple(round(c, decimales) for c in v)
        if k not in clave:
            clave[k] = len(W)
            W.append(v)
        nuevo.append(clave[k])
    G = []
    for a, b, c in F:
        a, b, c = nuevo[a], nuevo[b], nuevo[c]
        if len({a, b, c}) == 3:
            G.append((a, b, c))
    return W, G


def escribir_obj(ruta, grupos, paleta: dict[str, str] | None = None) -> None:
    """Grupos (nombre, V, F) o (nombre, V, F, colores). Con `paleta` y colores
    por cara escribe ademas el .mtl al lado y un `usemtl` por cambio de color."""
    lineas = ["# Alfabeto de Jones y Goury, modelo declarado en granada/piezas.py"]
    if paleta:
        mtl = ruta.with_suffix(".mtl")
        lineas.append(f"mtllib {mtl.name}")
        bloques = []
        for nombre, h in paleta.items():
            r, g, b = (int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
            bloques.append(f"newmtl {nombre}\nKd {r:.4f} {g:.4f} {b:.4f}\n")
        mtl.write_text("\n".join(bloques), encoding="utf-8")
    desplazamiento = 1
    for grupo in grupos:
        nombre, V, F = grupo[:3]
        colores = grupo[3] if len(grupo) > 3 and paleta else None
        lineas.append(f"g {nombre}")
        lineas.extend(f"v {x:.6f} {y:.6f} {z:.6f}" for x, y, z in V)
        actual = None
        for k, (a, b, c) in enumerate(F):
            if colores is not None and colores[k] != actual:
                actual = colores[k]
                lineas.append(f"usemtl {actual}")
            lineas.append(f"f {a + desplazamiento} {b + desplazamiento} {c + desplazamiento}")
        desplazamiento += len(V)
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")
