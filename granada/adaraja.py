"""OBSOLETO: perfil de conica unica, conservado solo como referencia.

La tesis documenta una plantilla de doble perfil y paralelismo entre piezas
vecinas. Este modulo no representa ese sistema y no debe alimentar un nuevo
render historico.

Alzado de la adaraja: el perfil concavo que cuelga de cada hilada.

La estratificacion da el esqueleto escalonado de la cupula. Lo que convierte
ese cono de escalones en mocarabes es el perfil vertical de cada celda: la
cara casi vertical arriba y el labio redondeado que vuela hacia fuera abajo.

Aqui se modela como una **conica racional** en el plano meridiano (radio,
altura). Racional quiere decir exacta: con puntos de control y peso en
`Fraction`, evaluar en un `t` racional da coordenadas racionales. Ni trigono-
metria ni coma flotante.

El perfil
---------
Normalizado al cuadrado unidad de la celda: el radio va de 0 (interior) a 1
(exterior) y la altura de 0 (abajo) a 1 (arriba).

    P0 = (1, 0)          exterior abajo: el labio
    P1 = (tiro, tiro)    control, sobre la diagonal
    P2 = (0, 1)          interior arriba: donde engancha con la hilada de encima

Curva de Bezier cuadratica racional de pesos 1, `peso`, 1:

    B(t) = [ (1-t)^2 P0 + 2t(1-t)*peso*P1 + t^2 P2 ]
           / [ (1-t)^2 + 2t(1-t)*peso + t^2 ]

Dos mandos, y solo dos:

- **tiro** en [0, 1] gobierna la profundidad. Con 0 el control cae en el
  origen y sale el cuenco hondo; con 1/2 el control cae sobre la cuerda y la
  curva degenera en el segmento recto (cono liso, sin mocarabes); con 1 el
  perfil se abomba hacia fuera.
- **peso** gobierna la forma de la conica. Con 1 es una parabola; por debajo,
  una elipse; por encima, una hiperbola.

Con tiro = 0 las tangentes salen perpendiculares: vertical en P2 y horizontal
en P0. Es justo lo que se ve en la seccion del plano.

Sobre el arco de circunferencia exacto
--------------------------------------
El cuarto de circunferencia exacto pide peso = sqrt(2)/2 = 0.70710678...,
que no es racional. `PESO_CIRCULO` usa 70/99, el convergente clasico de
sqrt(2), con un error relativo de 5.1e-5: a efectos de dibujo es una
circunferencia, pero la curva es en rigor una elipse.

Curiosidad que puede aprovecharse mas adelante: sqrt(2) SI vive en el
subanillo real de Z[zeta_16] y de Z[zeta_24] (es lambda^2 - 2 y lambda^3 -
3*lambda respectivamente), asi que para esos dos ordenes el arco circular
exacto seria representable sin salir del cuerpo del propio anillo. Para
m=20 no lo seria: alli no hay sqrt(2). No esta implementado.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from granada.celda import pasos_maximos
from granada.cyclotomic import CyclotomicInteger, CyclotomicRing, numeric_embedding_xy

__all__ = [
    "PerfilArco",
    "PuntoMalla",
    "PESO_PARABOLA",
    "PESO_CIRCULO",
    "TIRO_CUENCO",
    "TIRO_RECTO",
    "malla_adaraja",
]

PESO_PARABOLA = Fraction(1)
PESO_CIRCULO = Fraction(70, 99)  # ~ sqrt(2)/2, error relativo 5.1e-5

TIRO_CUENCO = Fraction(0)  # control en el origen: cuenco hondo
TIRO_RECTO = Fraction(1, 2)  # control sobre la cuerda: segmento recto


class PerfilArco:
    """Conica racional en el plano meridiano, normalizada a [0,1] x [0,1]."""

    __slots__ = ("tiro", "peso")

    def __init__(
        self, tiro: Fraction = TIRO_CUENCO, peso: Fraction = PESO_CIRCULO
    ) -> None:
        if not isinstance(tiro, Fraction) or not isinstance(peso, Fraction):
            raise TypeError("tiro y peso deben ser Fraction exactas")
        if not 0 <= tiro <= 1:
            raise ValueError(f"tiro fuera de [0, 1]: {tiro}")
        if peso <= 0:
            raise ValueError(f"el peso debe ser positivo, se recibio {peso}")
        self.tiro = tiro
        self.peso = peso

    def punto(self, t: Fraction) -> tuple[Fraction, Fraction]:
        """Punto del perfil en el parametro t. Exacto, racional.

        Devuelve (radio, altura) con radio 1 en el exterior y 0 en el eje,
        altura 0 abajo y 1 arriba.
        """
        if not isinstance(t, Fraction):
            raise TypeError(f"t debe ser Fraction, se recibio {type(t).__name__}")
        if not 0 <= t <= 1:
            raise ValueError(f"t fuera de [0, 1]: {t}")
        u = 1 - t
        b0 = u * u
        b1 = 2 * t * u * self.peso
        b2 = t * t
        den = b0 + b1 + b2
        # P0 = (1, 0), P1 = (tiro, tiro), P2 = (0, 1)
        radio = (b0 * 1 + b1 * self.tiro + b2 * 0) / den
        altura = (b0 * 0 + b1 * self.tiro + b2 * 1) / den
        return (radio, altura)

    def muestrear(self, n: int) -> tuple[tuple[Fraction, Fraction], ...]:
        """n+1 puntos del perfil, en parametros racionales equiespaciados."""
        if n < 1:
            raise ValueError(f"hacen falta muestras, se recibio n={n}")
        return tuple(self.punto(Fraction(i, n)) for i in range(n + 1))

    def es_recto(self) -> bool:
        """El control sobre la cuerda degenera la conica en un segmento."""
        return self.tiro == TIRO_RECTO

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PerfilArco):
            return NotImplemented
        return self.tiro == other.tiro and self.peso == other.peso

    def __hash__(self) -> int:
        return hash((self.tiro, self.peso))

    def __repr__(self) -> str:
        return f"PerfilArco(tiro={self.tiro}, peso={self.peso})"


class PuntoMalla:
    """Un vertice de la malla: planta en Q(zeta_m) y altura en Q.

    La planta se guarda como coeficientes racionales en la misma base que
    Z[zeta_m], porque interpolar dentro de una celda saca del anillo entero
    pero no del cuerpo. Todo sigue siendo exacto.
    """

    __slots__ = ("ring", "plano", "altura")

    def __init__(
        self,
        ring: CyclotomicRing,
        plano: Sequence[Fraction],
        altura: Fraction,
    ) -> None:
        if len(plano) != ring.degree:
            raise ValueError(
                f"se esperaban {ring.degree} coeficientes, se recibieron {len(plano)}"
            )
        for c in plano:
            if not isinstance(c, Fraction):
                raise TypeError("los coeficientes del plano deben ser Fraction")
        if not isinstance(altura, Fraction):
            raise TypeError("la altura debe ser Fraction")
        self.ring = ring
        self.plano = tuple(plano)
        self.altura = altura

    @classmethod
    def desde_entero(
        cls, elemento: CyclotomicInteger, altura: Fraction
    ) -> "PuntoMalla":
        return cls(
            elemento.ring, tuple(Fraction(c) for c in elemento.coeffs), altura
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PuntoMalla):
            return NotImplemented
        return (
            self.ring.m == other.ring.m
            and self.plano == other.plano
            and self.altura == other.altura
        )

    def __hash__(self) -> int:
        return hash((self.ring.m, self.plano, self.altura))

    def __repr__(self) -> str:
        return f"PuntoMalla(m={self.ring.m}, altura={self.altura})"


def malla_adaraja(
    ring: CyclotomicRing,
    radio_exterior: int,
    radio_interior: int,
    altura_base: Fraction,
    altura_cima: Fraction,
    pasos: int = 2,
    perfil: PerfilArco | None = None,
    n_perfil: int = 8,
    n_ancho: int = 4,
) -> tuple[tuple[PuntoMalla, ...], ...]:
    """Rejilla de vertices exactos de una adaraja.

    Devuelve n_perfil+1 filas de n_ancho+1 puntos. La fila i recorre el
    perfil de abajo arriba; dentro de cada fila, la columna j recorre el
    ancho angular de la celda, de zeta^0 a zeta^pasos.

    La seccion transversal es la cuerda entre los dos bordes de la celda, no
    el arco: la celda es un poligono en planta, asi que la cuerda es lo
    correcto y ademas mantiene todo racional.
    """
    if perfil is None:
        perfil = PerfilArco()
    if not 1 <= pasos <= pasos_maximos(ring):
        raise ValueError(
            f"pasos fuera de rango para m={ring.m}: "
            f"se esperaba 1..{pasos_maximos(ring)}, se recibio {pasos}"
        )
    if radio_exterior <= radio_interior or radio_interior < 0:
        raise ValueError(
            f"radios incoherentes: exterior {radio_exterior}, "
            f"interior {radio_interior}"
        )
    if not isinstance(altura_base, Fraction) or not isinstance(altura_cima, Fraction):
        raise TypeError("las alturas deben ser Fraction exactas")
    if altura_cima <= altura_base:
        raise ValueError("la cima debe quedar por encima de la base")
    if n_ancho < 1:
        raise ValueError(f"hacen falta divisiones a lo ancho, se recibio {n_ancho}")

    borde_a = ring.one
    borde_b = ring.zeta_power(pasos)
    espesor = radio_exterior - radio_interior
    canto = altura_cima - altura_base

    filas: list[tuple[PuntoMalla, ...]] = []
    for radio_norm, altura_norm in perfil.muestrear(n_perfil):
        radio = radio_interior + espesor * radio_norm
        altura = altura_base + canto * altura_norm
        fila: list[PuntoMalla] = []
        for j in range(n_ancho + 1):
            s = Fraction(j, n_ancho)
            coeffs = tuple(
                radio * ((1 - s) * Fraction(a) + s * Fraction(b))
                for a, b in zip(borde_a.coeffs, borde_b.coeffs)
            )
            fila.append(PuntoMalla(ring, coeffs, altura))
        filas.append(tuple(fila))
    return tuple(filas)


# ==========================================================================
# FRONTERA NUMERICA — ver el aviso equivalente en cyclotomic.py
# ==========================================================================


def numeric_embedding_punto(punto: PuntoMalla) -> tuple[float, float, float]:
    """Embedding numerico INEXACTO de un vertice de la malla en R^3.

    Solo para dibujar. Nunca para comparar ni decidir.
    """
    escala = 1
    for c in punto.plano:
        escala = escala * c.denominator // _mcd(escala, c.denominator)
    enteros = punto.ring.element([int(c * escala) for c in punto.plano])
    x, y = numeric_embedding_xy(enteros)
    return (x / escala, y / escala, float(punto.altura))


def _mcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a
