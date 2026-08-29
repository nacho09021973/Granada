"""Perfiles de celda en planta, con vertices exactos en Z[zeta_m].

Una celda de mocarabe se proyecta en planta sobre un poligono cuyos vertices
viven en Z[zeta_m]. Este modulo construye esos poligonos y las agrupaciones
por rotacion, todo con aritmetica entera exacta: ningun float interviene, y
el cierre de un anillo de celdas es una igualdad de enteros, no una
tolerancia.

Parametrizacion por pasos, no por angulos
-----------------------------------------
El sistema occidental descrito por Lopez de Arenas y Fray Andres de San
Miguel reduce los angulos interiores a 45, 67.5, 90 y 135 grados. Todos son
multiplos de 22.5 = 2*pi/16 (ver docs/fuentes.md, entrada 1).

Aqui NO se codifican esos angulos, sino el numero de pasos de reticula que
los generan. El triangulo canonico del tratado no es "de 45 grados": es "de
2 pasos", que a m=16 son 45 grados, a m=20 son 36 y a m=24 son 30. Asi las
celdas se deforman solas al cambiar el orden de simetria, y ningun angulo
degenera al transponer el sistema a otros ordenes.

Ordenes elegidos para el proyecto: 16, 20 y 24. Los tres tienen phi(m)=8 y
subanillo real de rango 4, luego son igual de ricos, pero cada uno vive en
un mundo cuadratico distinto -- sqrt(2), sqrt(5) y sqrt(2) con sqrt(3)
respectivamente -- asi que sus proporciones son genuinamente diferentes y no
una escala de la misma figura.

Un paso vale 2*pi/m. Los pasos utiles van de 1 a m//2 - 1: con m//2 pasos el
apice seria de 180 grados y el poligono degeneraria en un segmento.
"""

from __future__ import annotations

from typing import Sequence

from granada.cyclotomic import (
    CyclotomicInteger,
    CyclotomicRing,
    RealCyclotomicInteger,
    numeric_embedding_xy,
)

__all__ = [
    "Celda",
    "cuna",
    "rombo",
    "anillo",
    "pasos_maximos",
]


def pasos_maximos(ring: CyclotomicRing) -> int:
    """Mayor numero de pasos que da un apice no degenerado."""
    return ring.m // 2 - 1


class Celda:
    """Un poligono cerrado con vertices exactos en Z[zeta_m].

    Los vertices se guardan en orden; el cierre del poligono es implicito
    (el ultimo enlaza con el primero). Inmutable.
    """

    __slots__ = ("ring", "vertices", "nombre")

    def __init__(
        self,
        ring: CyclotomicRing,
        vertices: Sequence[CyclotomicInteger],
        nombre: str = "",
    ) -> None:
        if len(vertices) < 3:
            raise ValueError(f"un poligono necesita 3 vertices o mas, hay {len(vertices)}")
        for v in vertices:
            if v.ring.m != ring.m:
                raise ValueError("hay vertices de otro anillo")
        self.ring = ring
        self.vertices = tuple(vertices)
        self.nombre = nombre

    # -- transformaciones exactas -------------------------------------------

    def rotate(self, k: int = 1) -> "Celda":
        """Gira la celda k pasos alrededor del origen. Exacto."""
        return Celda(
            self.ring, tuple(v.rotate(k) for v in self.vertices), self.nombre
        )

    def conjugate(self) -> "Celda":
        """Refleja la celda respecto del eje real. Exacto."""
        return Celda(
            self.ring, tuple(v.conjugate() for v in self.vertices), self.nombre
        )

    def translate(self, desplazamiento: CyclotomicInteger) -> "Celda":
        """Traslada la celda. Exacto."""
        return Celda(
            self.ring,
            tuple(v + desplazamiento for v in self.vertices),
            self.nombre,
        )

    # -- metrica exacta -----------------------------------------------------

    def lados_al_cuadrado(self) -> tuple[RealCyclotomicInteger, ...]:
        """Longitud al cuadrado de cada lado, en el subanillo real.

        Exactas: no son aproximaciones de longitudes, son elementos de
        Z[2*cos(2*pi/m)].
        """
        n = len(self.vertices)
        return tuple(
            (self.vertices[(i + 1) % n] - self.vertices[i]).norm_squared()
            for i in range(n)
        )

    def es_equilatera(self) -> bool:
        lados = self.lados_al_cuadrado()
        return all(l == lados[0] for l in lados)

    # -- protocolo ----------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Celda):
            return NotImplemented
        return self.ring.m == other.ring.m and self.vertices == other.vertices

    def __hash__(self) -> int:
        return hash((self.ring.m, self.vertices))

    def __len__(self) -> int:
        return len(self.vertices)

    def __repr__(self) -> str:
        etiqueta = f" {self.nombre!r}" if self.nombre else ""
        return f"Celda(m={self.ring.m},{etiqueta} {len(self.vertices)} vertices)"


# --------------------------------------------------------------------------
# Perfiles canonicos
# --------------------------------------------------------------------------


def cuna(ring: CyclotomicRing, pasos: int = 2) -> Celda:
    """Triangulo isosceles con apice en el origen y lados de longitud 1.

    Vertices: 0, 1, zeta^pasos. El apice abarca `pasos` pasos de reticula.

    Es el perfil canonico del sistema occidental. Con m=16 y 2 pasos, el
    apice mide 45 grados, los angulos de la base 67.5, y la base al cuadrado
    vale exactamente 2 - sqrt(2): el triangulo que Lopez de Arenas describe
    como "isosceles con angulo de 45 grados y lados mayores de 5".
    """
    if not 1 <= pasos <= pasos_maximos(ring):
        raise ValueError(
            f"pasos fuera de rango para m={ring.m}: "
            f"se esperaba 1..{pasos_maximos(ring)}, se recibio {pasos}"
        )
    return Celda(
        ring,
        (ring.zero, ring.one, ring.zeta_power(pasos)),
        f"cuna-{pasos}",
    )


def rombo(ring: CyclotomicRing, pasos: int = 2) -> Celda:
    """Rombo de lado 1 con un vertice en el origen.

    Vertices: 0, 1, 1 + zeta^pasos, zeta^pasos. Los cuatro lados miden
    exactamente 1. Con m=16 y 4 pasos es el cuadrado unidad.
    """
    if not 1 <= pasos <= pasos_maximos(ring):
        raise ValueError(
            f"pasos fuera de rango para m={ring.m}: "
            f"se esperaba 1..{pasos_maximos(ring)}, se recibio {pasos}"
        )
    z = ring.zeta_power(pasos)
    return Celda(ring, (ring.zero, ring.one, ring.one + z, z), f"rombo-{pasos}")


# --------------------------------------------------------------------------
# Agrupacion en anillo
# --------------------------------------------------------------------------


def anillo(celda: Celda, pasos: int) -> tuple[Celda, ...]:
    """Replica una celda alrededor del origen girandola de `pasos` en `pasos`.

    Devuelve m // pasos copias. Exige que `pasos` divida a m: si no, el
    anillo no cerraria y la ultima celda no encajaria con la primera.

    El cierre es exacto por construccion, no por tolerancia: girar el anillo
    completo `pasos` pasos lo deja invariante como conjunto, y girar una
    celda m // pasos veces la devuelve a si misma con los mismos
    coeficientes enteros.
    """
    m = celda.ring.m
    if pasos < 1:
        raise ValueError(f"pasos debe ser >= 1, se recibio {pasos}")
    if m % pasos != 0:
        raise ValueError(
            f"el anillo no cierra: {pasos} pasos no dividen a m={m}. "
            f"Divisores validos: {[d for d in range(1, m + 1) if m % d == 0]}"
        )
    n = m // pasos
    return tuple(celda.rotate(pasos * i) for i in range(n))


# ==========================================================================
# FRONTERA NUMERICA — ver el aviso equivalente en cyclotomic.py
# ==========================================================================


def numeric_embedding_celda(celda: Celda) -> tuple[tuple[float, float], ...]:
    """Embedding numerico INEXACTO de los vertices de una celda en R^2.

    Solo para dibujar. Nunca para comparar ni decidir.
    """
    return tuple(numeric_embedding_xy(v) for v in celda.vertices)
