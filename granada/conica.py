"""Conica racional en el plano meridiano: la primitiva de curva del proyecto.

Este modulo fue `adaraja.py` y modelaba la pieza con una **conica unica**. Ese
modelo esta refutado: la tesis documenta una plantilla de doble perfil y
paralelismo entre piezas vecinas, y quien la representa es `granada/perfil.py`
(decision 0010). Con el modelo se fueron `PuntoMalla`, `malla_adaraja` y su
embedding, que levantaban geometria a partir de el; el levantado vive ahora en
`granada/malla.py`.

Lo que queda es la curva, y por eso el modulo se llama como se llama:
`PerfilArco` es una conica racional **exacta en `Fraction`**, sin trigonometria
ni coma flotante. `plantilla.py` la usa como **interpolador declarado** entre los
puntos que la fuente si documenta. No afirma nada sobre la forma de una pieza:
es el interpolador, no el modelo.

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

__all__ = [
    "PerfilArco",
    "PESO_PARABOLA",
    "PESO_CIRCULO",
    "TIRO_CUENCO",
    "TIRO_RECTO",
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
