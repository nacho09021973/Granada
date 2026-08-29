"""Plantilla de doble perfil de la adaraja.

La tesis de Ferrer Perez-Blanco documenta que no hay un perfil unico, sino una
**plantilla de doble perfil**, y que las piezas vecinas mantienen sus perfiles
**paralelos** (`docs/teselado.md`):

- **perfil mayor**, dividido en quintos, punto mas alto a **7P**
- **perfil menor**, dividido en septimos, a **7,5P**
- **el nivel siguiente, a 8P**

Eso es lo documentado y aqui se respeta de forma exacta, en `Fraction`. Lo que
la fuente **no** da es la curva entre esos puntos ni que pieza usa cada
plantilla. La curva se interpola con la conica racional de `granada.adaraja`,
que es una **eleccion de modelo declarada**, no una medida; la asignacion queda
abierta y por defecto todas las caras usan el perfil mayor.

Sobre P
-------
P es la unidad de la propia plantilla, no el modulo de la planta: el nivel
siguiente esta a 8P, luego P vale un octavo del paso vertical entre hiladas.
De ahi que lo que importa geometricamente sea la **fraccion util** 7/8 o 15/16
del salto disponible, y no un valor absoluto en metros. Escalar por el numero
de hiladas que abarca una cara conserva esa fraccion.

Advertencia de alcance
----------------------
8P es pauta de reconstruccion moderna documentada por Saseta y usada por
Ferrer; **no consta en los manuscritos** (`docs/fuentes.md`, entrada 11). Es un
parametro, no una constante historica.
"""

from __future__ import annotations

from fractions import Fraction

from granada.conica import PerfilArco


UNIDADES_ENTRE_NIVELES = Fraction(8)
CIMA_MAYOR = Fraction(7)
CIMA_MENOR = Fraction(15, 2)
DIVISION_MAYOR = 5
DIVISION_MENOR = 7
MUESTRAS_INVERSION = 64


class PlantillaPerfil:
    """Uno de los dos perfiles documentados, con su division y su cima."""

    __slots__ = ("nombre", "division", "cima", "perfil", "_tabla")

    def __init__(
        self, nombre: str, division: int, cima: Fraction, perfil: PerfilArco
    ) -> None:
        if division < 1:
            raise ValueError(f"la division debe ser positiva: {division}")
        if not isinstance(cima, Fraction):
            raise TypeError("la cima debe ser Fraction exacta")
        if not 0 < cima < UNIDADES_ENTRE_NIVELES:
            raise ValueError(
                f"la cima debe quedar por debajo del nivel siguiente: {cima}"
            )
        self.nombre = nombre
        self.division = division
        self.cima = cima
        self.perfil = perfil
        self._tabla = perfil.muestrear(MUESTRAS_INVERSION)

    @property
    def fraccion_util(self) -> Fraction:
        """Parte del salto entre niveles que ocupa el frente de la pieza."""
        return self.cima / UNIDADES_ENTRE_NIVELES

    def estaciones(self) -> tuple[Fraction, ...]:
        """La division de la plantilla: quintos o septimos de su cima."""
        return tuple(
            self.cima * Fraction(i, self.division) for i in range(self.division + 1)
        )

    def altura_normalizada(self, u: Fraction) -> Fraction:
        """Altura del perfil en la coordenada radial u de la pieza.

        u vale 0 en el borde exterior, donde la pieza cuelga mas, y 1 en el
        interior, donde engancha con la hilada de encima. Se obtiene invirtiendo
        el radio de la conica sobre una tabla de `MUESTRAS_INVERSION` tramos:
        la conica es exacta, esta inversion es una interpolacion declarada.
        """
        if not isinstance(u, Fraction):
            raise TypeError(f"u debe ser Fraction, se recibio {type(u).__name__}")
        if not 0 <= u <= 1:
            raise ValueError(f"u fuera de [0, 1]: {u}")
        objetivo = 1 - u
        anterior = self._tabla[0]
        for actual in self._tabla[1:]:
            if actual[0] <= objetivo <= anterior[0]:
                tramo = anterior[0] - actual[0]
                if tramo == 0:
                    return anterior[1]
                peso = (anterior[0] - objetivo) / tramo
                return anterior[1] + peso * (actual[1] - anterior[1])
            anterior = actual
        return self._tabla[-1][1]

    def profundidad(self, salto_vertical: Fraction) -> Fraction:
        """Cuanto cuelga la pieza dado el salto vertical que tiene disponible.

        Conserva la proporcion documentada: el frente ocupa `cima/8` del salto y
        el resto queda como junta hasta el nivel siguiente.
        """
        return salto_vertical * self.fraccion_util

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PlantillaPerfil):
            return NotImplemented
        return (
            self.division == other.division
            and self.cima == other.cima
            and self.perfil == other.perfil
        )

    def __hash__(self) -> int:
        return hash((self.division, self.cima, self.perfil))

    def __repr__(self) -> str:
        return f"PlantillaPerfil({self.nombre!r}, division={self.division}, cima={self.cima})"


MAYOR = PlantillaPerfil("mayor", DIVISION_MAYOR, CIMA_MAYOR, PerfilArco())
MENOR = PlantillaPerfil("menor", DIVISION_MENOR, CIMA_MENOR, PerfilArco())


def paralelas(a: PlantillaPerfil, b: PlantillaPerfil) -> bool:
    """Dos piezas tienen perfiles paralelos si comparten plantilla.

    Perfiles paralelos son trasladados verticalmente uno del otro. Dos piezas
    con la misma plantilla lo son aunque esten en niveles distintos, porque solo
    las separa la traslacion. Dos piezas con plantillas distintas no lo son: ni
    la cima ni la division coinciden.
    """
    return a == b


def vecindades_no_paralelas(
    asignacion: dict[str, PlantillaPerfil],
    vecindades: list[dict],
) -> list[tuple[str, str]]:
    """Vecindades cuyas dos piezas rompen el paralelismo documentado.

    El contorno no es una pieza y no impone plantilla, asi que se omite.
    """
    rotas = []
    for vecindad in vecindades:
        a, b = vecindad["a"], vecindad["b"]
        if b == "contorno":
            continue
        if a not in asignacion or b not in asignacion:
            continue
        if not paralelas(asignacion[a], asignacion[b]):
            rotas.append((a, b))
    return rotas
