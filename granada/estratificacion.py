"""OBSOLETO: estratificacion por coronas polares, conservada como referencia.

La planta correcta es un teselado con niveles topologicos, no una sucesion de
anillos concentricos. Este modulo no debe alimentar un nuevo render historico.

Estratificacion de la cupula: las hiladas, su radio y su altura.

La planta vive en Z[zeta_m] y es exacta. La vertical es una dimension aparte
y aqui se lleva en `fractions.Fraction`: aritmetica racional exacta, no coma
flotante. Un punto en 3D es por tanto un par (elemento de Z[zeta_m], Fraction)
y sigue sin haber redondeo en ningun sitio.

Modelo
------
La cupula es un cono escalonado de N hiladas. La hilada k (k=0 en la base)
ocupa el anillo entre los radios N-k y N-k-1, medidos en unidades de planta,
y se apoya a la altura k*razon.

`razon` es la altura de una hilada dividida por el paso horizontal, ambos en
unidades de planta. Es lo unico que gobierna la silueta: con razon grande la
cupula es esbelta, con razon pequena es achatada.

Procedencia del valor por defecto
---------------------------------
Medido sobre la seccion norte-sur del plano AA-415_23 de Almagro, calibrada
con su escala grafica a 236.2 px/m (ver docs/estratificacion.md):

    pendiente dr/dh = 0.782 +/- 0.016   ->   razon = 1/0.782 = 1.279

Es una medida, no una constante del sistema: se expone como parametro. Se
probo si la pendiente valia 1/sqrt(2) = 0.707 y queda a 4.7 sigma, descartado.
El valor 4/5 = 0.800 cae a 1.1 sigma, pero nada autoriza a afirmar que sea la
intencion de diseno, asi que no se privilegia.
"""

from __future__ import annotations

from fractions import Fraction

from granada.celda import Celda, trapecio
from granada.cyclotomic import CyclotomicRing, numeric_embedding_xy

__all__ = [
    "Estratificacion",
    "RAZON_MEDIDA",
    "HILADAS_MEDIDAS",
]

# Altura de hilada / paso horizontal, medida sobre AA-415_23.
RAZON_MEDIDA = Fraction(1000, 782)

# Numero de hiladas contado sobre la misma seccion.
HILADAS_MEDIDAS = 23


class Estratificacion:
    """Las hiladas de una cupula de orden m.

    La hilada k va del radio `radio_exterior(k)` al `radio_interior(k)`, ambos
    enteros en unidades de planta, y se asienta a la altura `altura(k)`.
    """

    __slots__ = ("ring", "hiladas", "razon", "pasos")

    def __init__(
        self,
        ring: CyclotomicRing,
        hiladas: int = HILADAS_MEDIDAS,
        razon: Fraction = RAZON_MEDIDA,
        pasos: int = 2,
    ) -> None:
        if hiladas < 1:
            raise ValueError(f"hacen falta hiladas, se recibio {hiladas}")
        if not isinstance(razon, Fraction):
            raise TypeError(
                f"la razon debe ser una Fraction exacta, se recibio {type(razon).__name__}"
            )
        if razon <= 0:
            raise ValueError(f"la razon debe ser positiva, se recibio {razon}")
        if ring.m % pasos != 0:
            raise ValueError(
                f"el anillo no cerraria: {pasos} pasos no dividen a m={ring.m}"
            )
        self.ring = ring
        self.hiladas = hiladas
        self.razon = razon
        self.pasos = pasos

    # -- geometria de cada hilada -------------------------------------------

    def radio_exterior(self, k: int) -> int:
        """Radio exterior de la hilada k, en unidades de planta. Entero."""
        self._comprobar(k)
        return self.hiladas - k

    def radio_interior(self, k: int) -> int:
        """Radio interior de la hilada k. Entero; vale 0 en la ultima."""
        self._comprobar(k)
        return self.hiladas - k - 1

    def altura(self, k: int) -> Fraction:
        """Altura de la base de la hilada k. Exacta, racional."""
        self._comprobar(k)
        return self.razon * k

    def altura_total(self) -> Fraction:
        """Altura del apice sobre la base. Exacta."""
        return self.razon * self.hiladas

    def radio_base(self) -> int:
        """Radio de la cupula en su arranque, en unidades de planta."""
        return self.hiladas

    def celdas(self, k: int) -> tuple[Celda, ...]:
        """El anillo completo de celdas de la hilada k, en planta.

        Son m // pasos trapecios anulares. El cierre es exacto.
        """
        self._comprobar(k)
        base = trapecio(
            self.ring, self.radio_exterior(k), self.radio_interior(k), self.pasos
        )
        n = self.ring.m // self.pasos
        return tuple(base.rotate(self.pasos * i) for i in range(n))

    def celdas_por_hilada(self) -> int:
        return self.ring.m // self.pasos

    def total_celdas(self) -> int:
        return self.hiladas * self.celdas_por_hilada()

    # -- utilidades ---------------------------------------------------------

    def _comprobar(self, k: int) -> None:
        if not 0 <= k < self.hiladas:
            raise IndexError(
                f"hilada fuera de rango: se esperaba 0..{self.hiladas - 1}, "
                f"se recibio {k}"
            )

    def __len__(self) -> int:
        return self.hiladas

    def __repr__(self) -> str:
        return (
            f"Estratificacion(m={self.ring.m}, hiladas={self.hiladas}, "
            f"razon={self.razon}, celdas={self.total_celdas()})"
        )


# ==========================================================================
# FRONTERA NUMERICA — ver el aviso equivalente en cyclotomic.py
# ==========================================================================


def numeric_embedding_hilada(
    estrato: Estratificacion, k: int
) -> tuple[tuple[tuple[float, float, float], ...], ...]:
    """Embedding numerico INEXACTO de una hilada en R^3.

    Devuelve, por cada celda, la tupla de sus vertices como (x, y, z). La cara
    superior de la hilada k esta a la altura de la hilada k+1, asi que aqui
    solo se da la cota de arranque; el alzado de la adaraja es otro asunto.

    Solo para dibujar. Nunca para comparar ni decidir.
    """
    z = float(estrato.altura(k))
    salida = []
    for celda in estrato.celdas(k):
        salida.append(
            tuple(
                (xy[0], xy[1], z)
                for xy in (numeric_embedding_xy(v) for v in celda.vertices)
            )
        )
    return tuple(salida)
