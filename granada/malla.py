"""Levantado de la cupula: una celda por cara del teselado, y salida en OBJ.

Cada cara de la planta recibe un solido cerrado: la **plataforma** horizontal a
la cota de su banda y, colgando de ella, el **frente** de la adaraja con el
perfil de su plantilla. El resultado se exporta como malla triangular.

Que es medido y que es modelo
-----------------------------
- la planta de cada cara y su cota de banda vienen de `datos/`, ya calibradas
  contra la seccion medida (decision 0009);
- el **salto vertical** que abarca una cara es su extension radial por la
  pendiente medida del cono, `paso_vertical / paso_horizontal`;
- la **proporcion** entre el frente y ese salto es la documentada, 7/8 o 15/16
  (`granada.perfil`);
- la **curva** entre los extremos del perfil es la conica racional: eleccion de
  modelo declarada, no una medida.

Limite que hay que decir al presentarlo
---------------------------------------
La cara mediana de esta planta abarca **5,2 hiladas** de la seccion. Una cara no
es una adaraja: es una region que en la cupula real contiene varias. Este
levantado le da **una** celda, luego representa el escalonado de las bandas, no
el de las hiladas.
"""

from __future__ import annotations

import math
from fractions import Fraction

from granada.perfil import MAYOR, PlantillaPerfil


class Malla:
    """Malla triangular con grupos nombrados, exportable a OBJ."""

    __slots__ = ("vertices", "triangulos", "grupos")

    def __init__(self) -> None:
        self.vertices: list[tuple[float, float, float]] = []
        self.triangulos: list[tuple[int, int, int]] = []
        self.grupos: list[tuple[str, int]] = []

    def abrir_grupo(self, nombre: str) -> None:
        self.grupos.append((nombre, len(self.triangulos)))

    def anadir_vertice(self, x: float, y: float, z: float) -> int:
        self.vertices.append((x, y, z))
        return len(self.vertices) - 1

    def anadir_triangulo(self, a: int, b: int, c: int) -> None:
        if a == b or b == c or a == c:
            return
        self.triangulos.append((a, b, c))

    def a_obj(self, cabecera: str = "") -> str:
        lineas = [f"# {linea}" for linea in cabecera.splitlines() if cabecera]
        for x, y, z in self.vertices:
            lineas.append(f"v {x:.6f} {y:.6f} {z:.6f}")
        corte = {inicio: nombre for nombre, inicio in self.grupos}
        for indice, (a, b, c) in enumerate(self.triangulos):
            if indice in corte:
                lineas.append(f"o {corte[indice]}")
            lineas.append(f"f {a + 1} {b + 1} {c + 1}")
        return "\n".join(lineas) + "\n"


def _area_orientada(poligono: list[tuple[float, float]]) -> float:
    total = 0.0
    for (x0, y0), (x1, y1) in zip(poligono, poligono[1:] + poligono[:1]):
        total += x0 * y1 - x1 * y0
    return total / 2


def _densificar(
    poligono: list[tuple[float, float]], subdivision: int
) -> list[tuple[float, float]]:
    """Reparte puntos por cada lado para que la curva del perfil se vea."""
    if subdivision < 1:
        raise ValueError(f"subdivision debe ser >= 1, se recibio {subdivision}")
    denso = []
    for (x0, y0), (x1, y1) in zip(poligono, poligono[1:] + poligono[:1]):
        for paso in range(subdivision):
            t = paso / subdivision
            denso.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return denso


def _en_triangulo(
    p: tuple[float, float],
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
) -> bool:
    def lado(u, v, w):
        return (v[0] - u[0]) * (w[1] - u[1]) - (v[1] - u[1]) * (w[0] - u[0])

    d1, d2, d3 = lado(a, b, p), lado(b, c, p), lado(c, a, p)
    return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))


def triangular(poligono: list[tuple[float, float]]) -> list[tuple[int, int, int]]:
    """Triangula un poligono simple por recorte de orejas.

    El abanico desde el centroide no sirve aqui: 51 de las 105 caras de esta
    planta **no son convexas**, y el abanico les genera triangulos invertidos
    que aparecen como puas en el render.
    """
    indices = list(range(len(poligono)))
    if _area_orientada(poligono) < 0:
        indices.reverse()
    triangulos = []
    guarda = 0
    while len(indices) > 3 and guarda <= len(indices) * len(indices):
        guarda += 1
        for k in range(len(indices)):
            i, j, l = (
                indices[k - 1],
                indices[k],
                indices[(k + 1) % len(indices)],
            )
            a, b, c = poligono[i], poligono[j], poligono[l]
            if _area_orientada([a, b, c]) <= 0:
                continue
            if any(
                _en_triangulo(poligono[m], a, b, c)
                for m in indices
                if m not in (i, j, l)
            ):
                continue
            triangulos.append((i, j, l))
            indices.pop(k)
            guarda = 0
            break
        else:
            break
    for k in range(1, len(indices) - 1):
        triangulos.append((indices[0], indices[k], indices[k + 1]))
    return triangulos


def pieza(
    malla: Malla,
    poligono: list[tuple[float, float]],
    cota_m: float,
    salto_vertical_m: float,
    plantilla: PlantillaPerfil = MAYOR,
    subdivision: int = 4,
    escala_profundidad: float = 1.0,
) -> None:
    """Anade a la malla el solido de una cara: plataforma y frente colgando.

    Se llama `pieza` y no `celda` para no chocar con el modulo `granada.celda`,
    que es la celda de la PLANTA. Esto es el solido levantado de una de ellas.
    """
    if len(poligono) < 3:
        raise ValueError(f"una cara necesita 3 vertices o mas: {len(poligono)}")
    if salto_vertical_m < 0:
        raise ValueError(f"el salto vertical no puede ser negativo: {salto_vertical_m}")
    if _area_orientada(poligono) < 0:
        poligono = list(reversed(poligono))

    borde = _densificar(poligono, subdivision)
    radios = [math.hypot(x, y) for x, y in borde]
    r_min, r_max = min(radios), max(radios)
    profundidad = (
        float(plantilla.profundidad(Fraction(salto_vertical_m).limit_denominator(10**9)))
        * escala_profundidad
    )

    def coordenada_radial(radio: float) -> Fraction:
        if r_max == r_min:
            return Fraction(1)
        bruto = (r_max - radio) / (r_max - r_min)
        return Fraction(min(1.0, max(0.0, bruto))).limit_denominator(10**6)

    def cota_inferior(radio: float) -> float:
        altura = float(plantilla.altura_normalizada(coordenada_radial(radio)))
        return cota_m - profundidad * (1 - altura)

    arriba = [malla.anadir_vertice(x, y, cota_m) for x, y in borde]
    abajo = [
        malla.anadir_vertice(x, y, cota_inferior(radio))
        for (x, y), radio in zip(borde, radios)
    ]

    for i, j, k in triangular(borde):
        malla.anadir_triangulo(arriba[i], arriba[j], arriba[k])
        malla.anadir_triangulo(abajo[k], abajo[j], abajo[i])

    n = len(borde)
    for i in range(n):
        j = (i + 1) % n
        malla.anadir_triangulo(arriba[i], abajo[i], abajo[j])
        malla.anadir_triangulo(arriba[i], abajo[j], arriba[j])


def contiene_el_eje(poligono: list[tuple[float, float]]) -> bool:
    """El eje de la cupula cae dentro de la cara, que es entonces la de cierre."""
    dentro = False
    for (ax, ay), (bx, by) in zip(poligono, poligono[1:] + poligono[:1]):
        if (ay > 0) != (by > 0) and 0 < (bx - ax) * (0 - ay) / (by - ay) + ax:
            dentro = not dentro
    return dentro


def corona(
    malla: Malla,
    poligono: list[tuple[float, float]],
    cota_apice_m: float,
    cota_borde_m: float,
    plantilla: PlantillaPerfil = MAYOR,
    subdivision: int = 4,
    anillos: int = 6,
) -> None:
    """Anade la pieza de cierre: una cupulilla, no una plataforma plana.

    La cara que contiene el eje no puede tratarse como las demas. Su centroide
    esta en el eje, asi que la cota de banda la lleva entera al apice y remata la
    cupula con una tapa plana. En realidad su borde apoya en la banda de debajo y
    sube al apice describiendo una cupulilla: el cono medido continuado hasta el
    eje.

    Se construye como las demas celdas -tapa arriba, superficie curva debajo- solo
    que aqui la superficie es de revolucion sobre el mismo perfil de la plantilla.
    """
    if anillos < 2:
        raise ValueError(f"hacen falta al menos dos anillos, se recibio {anillos}")
    if cota_apice_m < cota_borde_m:
        raise ValueError("el apice no puede quedar por debajo del borde")
    if _area_orientada(poligono) < 0:
        poligono = list(reversed(poligono))

    borde = _densificar(poligono, subdivision)
    salto = cota_apice_m - cota_borde_m

    tapa = [malla.anadir_vertice(x, y, cota_apice_m) for x, y in borde]
    for i, j, k in triangular(borde):
        malla.anadir_triangulo(tapa[i], tapa[j], tapa[k])

    capas = []
    for indice in range(anillos):
        avance = Fraction(indice, anillos)
        encogido = 1 - float(avance)
        cota = cota_borde_m + salto * float(plantilla.altura_normalizada(avance))
        capas.append(
            [malla.anadir_vertice(x * encogido, y * encogido, cota) for x, y in borde]
        )
    apice = malla.anadir_vertice(0.0, 0.0, cota_apice_m)

    n = len(borde)
    for interior, exterior in zip(capas[1:], capas):
        for i in range(n):
            j = (i + 1) % n
            malla.anadir_triangulo(exterior[j], exterior[i], interior[i])
            malla.anadir_triangulo(exterior[j], interior[i], interior[j])
    for i in range(n):
        malla.anadir_triangulo(capas[-1][(i + 1) % n], capas[-1][i], apice)
        malla.anadir_triangulo(tapa[i], tapa[(i + 1) % n], capas[0][i])
        malla.anadir_triangulo(tapa[(i + 1) % n], capas[0][(i + 1) % n], capas[0][i])


def cupula(
    caras: list[dict],
    plantillas: dict[str, PlantillaPerfil] | None = None,
    subdivision: int = 4,
    escala_profundidad: float = 1.0,
) -> Malla:
    """Levanta las celdas de todas las caras.

    Cada cara del argumento lleva ``id``, ``poligono`` en metros, ``cota_m`` y
    ``salto_vertical_m``. La cara que contiene el eje se cierra como cupulilla.
    """
    malla = Malla()
    for cara in caras:
        malla.abrir_grupo(f"cara_{cara['id']}")
        plantilla = (plantillas or {}).get(cara["id"], MAYOR)
        if contiene_el_eje(cara["poligono"]):
            corona(
                malla,
                cara["poligono"],
                cara["cota_m"],
                cara["cota_m"] - cara["salto_vertical_m"],
                plantilla,
                subdivision,
            )
        else:
            pieza(
                malla,
                cara["poligono"],
                cara["cota_m"],
                cara["salto_vertical_m"],
                plantilla,
                subdivision,
                escala_profundidad,
            )
    return malla
