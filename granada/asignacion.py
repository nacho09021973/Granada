"""Que plantilla usa cada cara: la asignacion, que ninguna fuente da.

La tesis documenta **dos** perfiles -mayor y menor- y observa que las piezas
vecinas mantienen los suyos **paralelos**. La decision 0010 saco de ahi una
consecuencia incomoda: el grafo dual de esta planta es conexo, luego exigir
paralelismo en las 227 vecindades obligaria a una sola plantilla y la segunda
sobraria. Como la fuente documenta dos, el paralelismo tiene que romperse en
alguna frontera de modulo. **Ninguna fuente dice cual.**

Este modulo no descubre esa frontera: la **elige**. Los criterios estan
escritos, van en un orden fijo -primero lo documentado, al final lo nuestro- y
el catalogo entero queda disponible para que la eleccion se lea al lado de sus
rivales. Es la decision 0013.

La junta, en unidades P
-----------------------
Entre el fondo de una banda y la plataforma de la de abajo queda la **junta**.
Una banda que abarca ``h`` hiladas tiene ``8h`` unidades P de salto, el frente
ocupa ``cima * h`` y la junta es ``h * (8 - cima)``: ``h`` P con la mayor,
``h/2`` P con la menor. Exacta en ``Fraction``, sin metros de por medio.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping, Sequence

from granada.perfil import (
    MAYOR,
    MENOR,
    UNIDADES_ENTRE_NIVELES,
    PlantillaPerfil,
    vecindades_no_paralelas,
)

CRITERIOS = (
    "1. Se usan las dos plantillas: la tesis documenta dos, y el residuo del "
    "18-23 % del mejor modulo unico dice que esta cupula no tiene uno solo.",
    "2. Los dos grupos de bandas son contiguos: un grupo de modulo es una "
    "region seguida de la cupula, no bandas sueltas.",
    "3. Ningun grupo se queda con una sola cara: la pieza de cierre va aparte "
    "desde la decision 0010 y aislarla no es una frontera de modulo.",
    "4. Se rompe el paralelismo en las menos vecindades posibles. Es el unico "
    "de estos criterios que viene de una observacion de la fuente, asi que va "
    "por delante de los nuestros.",
    "5. Entre empates, la frontera cae donde mas cambia la subdivision angular "
    "de la planta -las caras por banda-, que es donde se veria un cambio de "
    "modulo.",
    "6. Entre empates, la junta queda lo mas constante posible entre bandas. "
    "Es un argumento fisico nuestro, no una fuente: va el ultimo.",
)


def junta_en_P(
    salto_en_hiladas: Fraction | int, plantilla: PlantillaPerfil
) -> Fraction:
    """Lo que queda entre el fondo de una banda y la plataforma de la inferior."""
    salto = Fraction(salto_en_hiladas)
    if salto < 0:
        raise ValueError(f"el salto no puede ser negativo: {salto}")
    return salto * (UNIDADES_ENTRE_NIVELES - plantilla.cima)


@dataclass(frozen=True)
class Asignacion:
    """Dos grupos contiguos de bandas, cada uno con su plantilla.

    ``frontera`` es la primera banda del grupo de arriba. Con ``frontera == 0``
    o ``frontera >= bandas`` la asignacion es uniforme y no hay frontera.
    """

    abajo: PlantillaPerfil
    arriba: PlantillaPerfil
    frontera: int

    def __post_init__(self) -> None:
        if self.frontera < 0:
            raise ValueError(f"la frontera no puede ser negativa: {self.frontera}")

    @classmethod
    def uniforme(cls, plantilla: PlantillaPerfil) -> "Asignacion":
        return cls(plantilla, plantilla, 0)

    @property
    def uniformizada(self) -> bool:
        return self.abajo == self.arriba

    def plantilla_de_banda(self, banda: int) -> PlantillaPerfil:
        return self.abajo if banda < self.frontera else self.arriba

    def por_cara(self, bandas: Mapping[str, int]) -> dict[str, PlantillaPerfil]:
        return {
            identificador: self.plantilla_de_banda(banda)
            for identificador, banda in bandas.items()
        }

    @property
    def etiqueta(self) -> str:
        if self.uniformizada:
            return f"uniforme-{self.abajo.nombre}"
        return f"{self.abajo.nombre}|{self.arriba.nombre}@{self.frontera}"


@dataclass(frozen=True)
class Candidato:
    """Una asignacion con todos sus controles ya medidos."""

    asignacion: Asignacion
    juntas_P: tuple[Fraction, ...]
    rotas: tuple[tuple[str, str], ...]
    caras_por_grupo: tuple[int, int]
    cambio_de_subdivision: Fraction

    @property
    def dispersion_de_junta(self) -> Fraction:
        return max(self.juntas_P) / min(self.juntas_P)

    @property
    def degenerado(self) -> bool:
        return min(self.caras_por_grupo) == 1

    def a_dict(self) -> dict:
        return {
            "etiqueta": self.asignacion.etiqueta,
            "abajo": self.asignacion.abajo.nombre,
            "arriba": self.asignacion.arriba.nombre,
            "frontera": self.asignacion.frontera,
            "juntas_P": [str(j) for j in self.juntas_P],
            "dispersion_de_junta": str(self.dispersion_de_junta),
            "vecindades_no_paralelas": len(self.rotas),
            "caras_por_grupo": list(self.caras_por_grupo),
            "cambio_de_subdivision": str(self.cambio_de_subdivision),
            "degenerado": self.degenerado,
        }


def _caras_por_banda(bandas: Mapping[str, int], total: int) -> list[int]:
    cuenta = [0] * total
    for banda in bandas.values():
        cuenta[banda] += 1
    return cuenta


def _cambio_de_subdivision(caras_por_banda: Sequence[int], frontera: int) -> Fraction:
    """Cuanto cambia el numero de caras por banda al cruzar la frontera."""
    if not 0 < frontera < len(caras_por_banda):
        return Fraction(1)
    debajo, encima = caras_por_banda[frontera - 1], caras_por_banda[frontera]
    return Fraction(max(debajo, encima), min(debajo, encima))


def evaluar(
    asignacion: Asignacion,
    bandas: Mapping[str, int],
    saltos_en_hiladas: Sequence[int],
    vecindades: list[dict],
) -> Candidato:
    """Mide una asignacion: juntas, paralelismos rotos y tamaño de los grupos."""
    if len(saltos_en_hiladas) == 0:
        raise ValueError("hace falta al menos una banda")
    cuenta = _caras_por_banda(bandas, len(saltos_en_hiladas))
    corte = min(max(asignacion.frontera, 0), len(cuenta))
    grupos = (sum(cuenta[:corte]), sum(cuenta[corte:]))
    return Candidato(
        asignacion=asignacion,
        juntas_P=tuple(
            junta_en_P(salto, asignacion.plantilla_de_banda(banda))
            for banda, salto in enumerate(saltos_en_hiladas)
        ),
        rotas=tuple(vecindades_no_paralelas(asignacion.por_cara(bandas), vecindades)),
        caras_por_grupo=grupos,
        cambio_de_subdivision=_cambio_de_subdivision(cuenta, corte),
    )


def catalogo(
    bandas: Mapping[str, int],
    saltos_en_hiladas: Sequence[int],
    vecindades: list[dict],
    plantillas: Sequence[PlantillaPerfil] = (MAYOR, MENOR),
) -> list[Candidato]:
    """Todas las asignaciones de dos grupos contiguos, uniformes incluidas.

    Es el catalogo entero: la elegida se publica al lado de sus rivales para
    que se vea que la frontera se decide, no se mide.
    """
    candidatas = [Asignacion.uniforme(plantilla) for plantilla in plantillas]
    for frontera in range(1, len(saltos_en_hiladas)):
        for abajo in plantillas:
            for arriba in plantillas:
                if abajo != arriba:
                    candidatas.append(Asignacion(abajo, arriba, frontera))
    return [
        evaluar(asignacion, bandas, saltos_en_hiladas, vecindades)
        for asignacion in candidatas
    ]


def elegir(
    bandas: Mapping[str, int],
    saltos_en_hiladas: Sequence[int],
    vecindades: list[dict],
    plantillas: Sequence[PlantillaPerfil] = (MAYOR, MENOR),
) -> Candidato:
    """Aplica `CRITERIOS` en su orden y devuelve la asignacion elegida.

    Los criterios 1 a 3 filtran; el 4, el 5 y el 6 ordenan. Si el filtro deja
    el catalogo vacio -por ejemplo con una sola plantilla- se devuelve la
    uniforme, que es lo defendible cuando no hay donde elegir.
    """
    todas = catalogo(bandas, saltos_en_hiladas, vecindades, plantillas)
    viables = [
        candidato
        for candidato in todas
        if not candidato.asignacion.uniformizada and not candidato.degenerado
    ]
    if not viables:
        return evaluar(
            Asignacion.uniforme(plantillas[0]), bandas, saltos_en_hiladas, vecindades
        )
    return min(
        viables,
        key=lambda candidato: (
            len(candidato.rotas),
            -candidato.cambio_de_subdivision,
            candidato.dispersion_de_junta,
        ),
    )


def procedencia(cara: str, asignacion: Asignacion, banda: int) -> str:
    """Que hay detras de la plantilla de esta cara. Se escribe en el artefacto.

    La plantilla en si esta documentada; **cual** le toca a esta cara, no.
    """
    if asignacion.uniformizada:
        return (
            f"plantilla {asignacion.abajo.nombre} documentada (tesis); asignada a "
            f"{cara} por defecto uniforme, sin evidencia de que le toque esa"
        )
    plantilla = asignacion.plantilla_de_banda(banda)
    return (
        f"plantilla {plantilla.nombre} documentada (tesis); asignada a {cara} por "
        f"estar en la banda {banda}, con la frontera de modulo DECIDIDA en "
        f"{asignacion.frontera - 1}|{asignacion.frontera} (decision 0013), no medida"
    )
