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
  el arco de A2 y C2 se cierra por detras en nicho (ver `_arco`): el grabado
  da la vista frontal, y extruirla dejaba un tunel por el que asomaba la
  hilada de debajo;
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


EXPONENTE_CIERRE = 16
"""Cuanto se ciñe el arco a los catetos al cerrar el nicho. Con 16 el hueco
que queda en el borde trasero no pasa del 4,6 % de la altura del arco, y solo
junto a las patas."""


def _arco(media_anchura: float, paso: float, fondo: float | None = None) -> Callable[[float, float], float]:
    """Patas en los extremos x = +-W; el arco sube hacia el eje.

    Sin `fondo`, el arco se extruye en profundidad: un tunel abierto por
    detras. Con `fondo` (la profundidad del triangulo, vertice al frente en
    y = 0 y lado trasero en y = -fondo) el arco se cierra en nicho:
    z = arco(x) * g, con g = 1 sobre los catetos -donde la pieza casa con sus
    vecinas, que no cambian- y g -> 0 en el lado trasero, donde el fondo baja a
    la cota de la pata y empalma con la hilada de debajo. La cupula sube hacia
    el centro, asi que la celdilla tiene que bajar hacia atras, no abrirse.
    """
    alto = paso * FRACCION_UTIL

    def arco(x: float) -> float:
        return alto * curva(
            (media_anchura - abs(x) - MEDIA_PATA) / (media_anchura - MEDIA_PATA)
        )

    if fondo is None:
        return lambda x, y: arco(x)

    def z(x: float, y: float) -> float:
        t = min(1.0, max(0.0, -y / fondo))
        if t <= 0:
            return arco(x)
        q = min(1.0, abs(x) / (t * media_anchura))
        g = 1.0 - (1.0 - q ** EXPONENTE_CIERRE) * t * t
        return arco(x) * g

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
    eje: str = "x"
    """Coordenada que es constante a lo largo de las patas: "x" (patas en
    x = cte) o "y" (B, pata a lo largo del lado trasero). La rejilla va en
    columnas paralelas a las patas. Ver `_rejilla`."""


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
        return Pieza(tipo, a_vertice, 1, _arco(R2, paso, R2), h)
    if tipo == "A3":
        return Pieza(tipo, a_frente, 2, _nicho(_trompeta(R2, paso), 0.68 * R2, -0.45 * R2, False, paso), h)
    if tipo == "B":
        return Pieza(tipo, rect, 1, _curva_fondo_frente(-1.0, paso), h, eje="y")
    if tipo == "C1":
        return Pieza(tipo, c_frente, 1, _trompeta(S22, paso), h)
    if tipo == "C2":
        return Pieza(tipo, c_vertice, 1, _arco(S22, paso, C22), h)
    if tipo == "C3":
        return Pieza(tipo, rombo, 2, _nicho(_trompeta(C22, paso), 0.6 * C22, -S22, True, paso), h)
    raise ValueError(f"tipo desconocido: {tipo!r}; los siete son {TIPOS}")


# --------------------------------------------------------------------------
# Malla


FINURA = 600
"""Muestras con que se mide la variacion del fondo para repartir la rejilla."""


def _repartir(longitud, variacion, cortes: int) -> list[float]:
    """`cortes` + 1 posiciones en [0, 1] que reparten por igual la longitud
    de la curva (posicion, cota) en norma L1: mas densas donde el fondo cambia
    deprisa. `variacion[i]` es |dz| entre las muestras i e i + 1."""
    acumulado = [0.0]
    paso = longitud / (len(variacion))
    for dz in variacion:
        acumulado.append(acumulado[-1] + paso + dz)
    total = acumulado[-1]
    fuera, i = [], 0
    for k in range(cortes + 1):
        objetivo = total * k / cortes
        while i < len(variacion) - 1 and acumulado[i + 1] < objetivo:
            i += 1
        tramo = acumulado[i + 1] - acumulado[i]
        f = 0.0 if tramo <= 0 else (objetivo - acumulado[i]) / tramo
        fuera.append(min(1.0, (i + min(1.0, max(0.0, f))) / len(variacion)))
    fuera[0], fuera[-1] = 0.0, 1.0
    return fuera


QUIEBRO = 2.0
"""Salto de pendiente del fondo (cota por unidad de cateto) a partir del cual
un cambio de pendiente se trata como arista y recibe su linea de rejilla. Las
patas saltan de 0 a mas de 15; los tramos de la curva tabulada, menos de 1."""


def _quiebros(perfiles: list[list[float]], paso: float, minimo: int = 1) -> list[int]:
    """Indices de muestra donde el fondo se quiebra en `minimo` perfiles.

    `perfiles`: incrementos de cota con signo entre muestras separadas `paso`.
    Un quiebro es un maximo local del salto de pendiente que supera `QUIEBRO`.
    Con `minimo` > 1 solo cuentan los que aparecen en la misma muestra (+-2) en
    varios perfiles: aristas paralelas a las columnas, como las patas; uno
    oblicuo cambia de sitio de perfil a perfil y lo recogen las filas.
    """
    marcas: list[set[int]] = []
    for dz in perfiles:
        salto = [0.0] + [abs(dz[i] - dz[i - 1]) / paso for i in range(1, len(dz))]
        aqui = set()
        for i in range(1, len(salto) - 1):
            if salto[i] >= QUIEBRO and salto[i] >= salto[i - 1] and salto[i] >= salto[i + 1]:
                aqui.add(i)
        marcas.append(aqui)
    fuera = set()
    for aqui in marcas:
        for i in aqui:
            if sum(any(abs(i - j) <= 2 for j in otro) for otro in marcas) >= minimo:
                fuera.add(i)
    elegidos, ultimo = [], None
    for i in sorted(fuera):
        if ultimo is None or i - ultimo > 2:
            elegidos.append(i)
        ultimo = i
    return elegidos


def _rejilla(p: Pieza, n: int):
    """Triangulacion de la planta que sigue al fondo; devuelve puntos y caras.

    Con la rejilla en abanico desde un vertice, la linea de la pata -donde el
    fondo sube casi en vertical- cruzaba los triangulos en oblicuo y se dibujaba
    en diente de sierra. Aqui la planta se corta en columnas paralelas a las
    patas (`p.eje`): `n` repartidas por la variacion del fondo, una en cada
    vertice para que las cuerdas sean rectas y una en cada quiebro paralelo a
    ellas. Cada cuerda lleva max(2, n // 2) filas con el mismo criterio mas una
    en cada quiebro suyo (el borde del nicho, por ejemplo). Dos columnas
    vecinas se cosen en cremallera por la coordenada a lo largo de la cuerda,
    de modo que un quiebro recto une puntos a la misma altura. Caras en sentido
    antihorario en planta.
    """
    if p.eje == "x":
        a_local = lambda x, y: (x, y)  # noqa: E731
    elif p.eje == "y":
        a_local = lambda x, y: (y, x)  # noqa: E731
    else:
        raise ValueError(f"eje debe ser 'x' o 'y', se recibio {p.eje!r}")
    poligono = [a_local(x, y) for x, y in p.planta]
    z = lambda s, t: p.fondo(*a_local(s, t))  # noqa: E731  (a_local es su propia inversa)
    s0, s1 = min(q[0] for q in poligono), max(q[0] for q in poligono)
    lados = list(zip(poligono, poligono[1:] + poligono[:1]))

    def cuerda(s: float) -> tuple[float, float]:
        ts = []
        for (xa, ya), (xb, yb) in lados:
            if xa == xb:
                if abs(s - xa) < 1e-12:
                    ts += [ya, yb]
                continue
            f = (s - xa) / (xb - xa)
            if -1e-12 <= f <= 1 + 1e-12:
                ts.append(ya + f * (yb - ya))
        return min(ts), max(ts)

    def incrementos(xs, linea):
        zs = [linea(x) for x in xs]
        return [b - a for a, b in zip(zs, zs[1:])]

    # Columnas: variacion del fondo a lo largo de s en cinco lineas de la cuerda.
    ss = [s0 + (s1 - s0) * i / FINURA for i in range(FINURA + 1)]
    perfiles = []
    for u in (0.1, 0.3, 0.5, 0.7, 0.9):
        def linea(s, u=u):
            t0, t1 = cuerda(s)
            return z(s, t0 + u * (t1 - t0))
        perfiles.append(incrementos(ss, linea))
    # La mayor de las cinco: una subida que solo ocupa parte de la cuerda (el
    # nicho) cuenta entera.
    mayor = [max(abs(d) for d in col) for col in zip(*perfiles)]
    columnas = {round(s0 + (s1 - s0) * f, 12) for f in _repartir(s1 - s0, mayor, n)}
    columnas |= {round(q[0], 12) for q in poligono}
    columnas |= {round(ss[i], 12) for i in _quiebros(perfiles, (s1 - s0) / FINURA, minimo=3)}
    columnas = sorted(columnas)

    # Filas de quiebro: aristas rectas a lo largo de s (el borde del nicho),
    # las que salen a la misma t en tres de cinco columnas.
    t_min, t_max = min(q[1] for q in poligono), max(q[1] for q in poligono)
    tt = [t_min + (t_max - t_min) * i / FINURA for i in range(FINURA + 1)]
    perfiles_t = [incrementos(tt, lambda t, s=s0 + (s1 - s0) * f: z(s, t)) for f in (0.1, 0.3, 0.5, 0.7, 0.9)]
    filas_quiebro = [tt[i] for i in _quiebros(perfiles_t, (t_max - t_min) / FINURA, minimo=3)]

    filas = max(2, n // 2)
    puntos: list[Punto2] = []
    # Cada columna: lista de (t, indice, ancla); ancla = numero de la fila de
    # quiebro que pasa por ese punto, o None.
    rejilla: list[list[tuple[float, int, int | None]]] = []
    for s in columnas:
        t0, t1 = cuerda(s)
        if t1 - t0 < 1e-12:
            marcas = {round(t0, 12): None}
        else:
            ts = [t0 + (t1 - t0) * i / FINURA for i in range(FINURA + 1)]
            dz = incrementos(ts, lambda t, s=s: z(s, t))
            marcas = {round(t0 + u * (t1 - t0), 12): None for u in _repartir(t1 - t0, [abs(d) for d in dz], filas)}
            for k, t in enumerate(filas_quiebro):
                if t0 + 1e-9 < t < t1 - 1e-9:
                    # Sustituye al punto repartido mas cercano si esta muy cerca.
                    cerca = min(marcas, key=lambda m: abs(m - t))
                    if abs(cerca - t) < 0.25 * (t1 - t0) / filas and cerca not in (round(t0, 12), round(t1, 12)):
                        del marcas[cerca]
                    marcas[round(t, 12)] = k
        fila = []
        for t in sorted(marcas):
            fila.append((t, len(puntos), marcas[t]))
            puntos.append(a_local(s, t))
        rejilla.append(fila)

    def area(a, b, c):
        (xa, ya), (xb, yb), (xc, yc) = puntos[a], puntos[b], puntos[c]
        return (xb - xa) * (yc - ya) - (yb - ya) * (xc - xa)

    def desvio(a, c):
        (xa, ya), (xc, yc) = puntos[a], puntos[c]
        return abs((p.fondo(xa, ya) + p.fondo(xc, yc)) / 2 - p.fondo((xa + xc) / 2, (ya + yc) / 2))

    caras = []

    def anadir(t):
        ar = area(*t)
        if abs(ar) > 1e-14:
            caras.append(t if ar > 0 else (t[0], t[2], t[1]))

    def coser(izq, der):
        """Cose dos tramos de columna por su posicion relativa en el tramo."""
        def relativa(tramo):
            a, b = tramo[0][0], tramo[-1][0]
            return [0.0 if b - a < 1e-12 else (t - a) / (b - a) for t, _, _ in tramo]
        ui, ud = relativa(izq), relativa(der)
        i = j = 0
        while i < len(izq) - 1 or j < len(der) - 1:
            if j == len(der) - 1:
                paso = "i"
            elif i == len(izq) - 1:
                paso = "d"
            elif abs(ui[i + 1] - ud[j + 1]) < 1e-9:
                paso = "ambos"
            else:
                paso = "i" if ui[i + 1] < ud[j + 1] else "d"
            if paso == "ambos":
                a, b, c, d = izq[i][1], der[j][1], der[j + 1][1], izq[i + 1][1]
                if desvio(a, c) <= desvio(b, d):
                    anadir((a, b, c)); anadir((a, c, d))  # noqa: E702
                else:
                    anadir((a, b, d)); anadir((b, c, d))  # noqa: E702
                i += 1
                j += 1
            elif paso == "i":
                anadir((izq[i][1], der[j][1], izq[i + 1][1]))
                i += 1
            else:
                anadir((izq[i][1], der[j][1], der[j + 1][1]))
                j += 1

    for izq, der in zip(rejilla, rejilla[1:]):
        comunes = sorted({m for _, _, m in izq if m is not None} & {m for _, _, m in der if m is not None})
        cortes_i = [0] + [next(k for k, e in enumerate(izq) if e[2] == m) for m in comunes] + [len(izq) - 1]
        cortes_d = [0] + [next(k for k, e in enumerate(der) if e[2] == m) for m in comunes] + [len(der) - 1]
        for (a, b), (c, d) in zip(zip(cortes_i, cortes_i[1:]), zip(cortes_d, cortes_d[1:])):
            coser(izq[a : b + 1], der[c : d + 1])
    return puntos, caras


def malla(p: Pieza, n: int = SUBDIVISION) -> tuple[list[Punto3], list[tuple[int, int, int]]]:
    """Solido cerrado: tapa, fondo curvo y paredes. Normales hacia fuera."""
    puntos, caras = _rejilla(p, n)
    # Funde los puntos repetidos (las cuerdas de longitud cero en los vertices).
    clave: dict[tuple[float, float], int] = {}
    nuevo = []
    unicos: list[Punto2] = []
    for x, y in puntos:
        k = (round(x, 9), round(y, 9))
        if k not in clave:
            clave[k] = len(unicos)
            unicos.append((x, y))
        nuevo.append(clave[k])
    caras = [(nuevo[a], nuevo[b], nuevo[c]) for a, b, c in caras]
    caras = [t for t in caras if len(set(t)) == 3]
    m = len(unicos)
    V: list[Punto3] = [(x, y, p.altura) for x, y in unicos] + [(x, y, p.fondo(x, y)) for x, y in unicos]
    F: list[tuple[int, int, int]] = []
    for a, b, c in caras:
        F.append((a, b, c))
        F.append((m + a, m + c, m + b))
    # Paredes sobre las aristas del borde, que solo usa un triangulo; en el
    # sentido de ese triangulo (antihorario) la pared mira hacia fuera.
    usos: dict[tuple[int, int], int] = {}
    for a, b, c in caras:
        for u, v in ((a, b), (b, c), (c, a)):
            usos[(u, v)] = usos.get((u, v), 0) + 1
    for (u, v) in usos:
        if (v, u) not in usos:
            F.append((m + u, m + v, v))
            F.append((m + u, v, u))
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


SOMBRA_PARED = 0.9
"""Las caras verticales que asoman entre hiladas se leen como filetes de yeso
claro, como en los mocarabes reales; en penumbra salian grises."""
SOMBRA_TAPA = 0.85


def oclusion(p: Pieza, V, F, etiqueta: list[str]) -> list[float]:
    """Factor de luz por triangulo (1 = sin sombra). Eleccion estetica.

    Imita la oclusion ambiental de una celdilla: en el fondo curvo, cuanto mas
    sube dentro de la pieza, menos luz le llega; las paredes quedan
    casi a plena luz, porque entre hiladas se leen como filetes de yeso.
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
