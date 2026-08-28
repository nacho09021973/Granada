"""Niveles topologicos de las teselas de mocarabes occidentales.

La planta propuesta por Ferrer Perez-Blanco no codifica la altura con una
unica cifra por poligono. Codifica, dentro de cada figura, el sentido y los
niveles de ascenso mediante una o varias flechas. Por tanto hay que separar:

* la familia y topologia de la pieza (A1, A2, A3, B4, C1, C2 o D3), que fija
  si la pieza salva uno o dos niveles;
* el nivel absoluto en el que se coloca cada instancia, que depende de las
  relaciones topologicas con sus vecinas.

Este modulo representa ambas cosas con enteros exactos. No intenta deducir
las relaciones de una ortoimagen ni completa componentes desconectados: si un
componente no tiene un nivel anclado, queda explicitamente sin resolver.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Iterable, Mapping

__all__ = [
    "AsignacionNivel",
    "InconsistenciaNiveles",
    "RelacionVecindad",
    "RestriccionNivel",
    "RestriccionSinFirmar",
    "ResultadoNiveles",
    "TopologiaAscenso",
    "TipoMocarabe",
    "admite_salto_unitario",
    "resolver_desde_vecindades",
    "resolver_niveles",
    "restricciones_firmadas",
]


class TopologiaAscenso(str, Enum):
    """Comportamiento generico de las flechas de ascendencia de una pieza.

    La clasificacion no determina la orientacion de una instancia concreta ni
    firma saltos con sus vecinas. Solo expresa la gramatica de los cuatro
    grupos mostrados por Ferrer en el ejercicio docente de 2023.
    """

    DIVERGENTE = "divergente"
    CONVERGENTE = "convergente"
    MIXTA = "mixta"
    NEUTRA = "neutra"


class TipoMocarabe(str, Enum):
    """Familia occidental de siete piezas documentada en la tesis.

    La letra identifica la figura plana de Jones y Goury y el numero su
    topologia. A3 y D3 son las dos piezas que salvan dos niveles; las demas
    salvan uno.
    """

    A1 = "A1"  # medio cuadrado
    A2 = "A2"  # atacia
    A3 = "A3"  # medio cuadrado de dos niveles
    B4 = "B4"  # conza
    C1 = "C1"  # media jaira
    C2 = "C2"  # dumbaque
    D3 = "D3"  # jaira de dos niveles

    @property
    def figura(self) -> str:
        return self.value[0]

    @property
    def topologia(self) -> int:
        return int(self.value[1:])

    @property
    def salto_niveles(self) -> int:
        return 2 if self in (TipoMocarabe.A3, TipoMocarabe.D3) else 1

    @property
    def topologia_ascenso(self) -> TopologiaAscenso:
        """Clase de ascendencia de la pieza antes de orientarla en la planta."""
        return {
            1: TopologiaAscenso.DIVERGENTE,
            2: TopologiaAscenso.CONVERGENTE,
            3: TopologiaAscenso.MIXTA,
            4: TopologiaAscenso.NEUTRA,
        }[self.topologia]


@dataclass(frozen=True, slots=True)
class AsignacionNivel:
    """Una pieza concreta colocada entre dos cotas topologicas."""

    tipo: TipoMocarabe
    nivel_base: int

    def __post_init__(self) -> None:
        if not isinstance(self.tipo, TipoMocarabe):
            raise TypeError("tipo debe ser TipoMocarabe")
        _validar_entero("nivel_base", self.nivel_base)
        if self.nivel_base < 0:
            raise ValueError("nivel_base no puede ser negativo")

    @property
    def nivel_cima(self) -> int:
        return self.nivel_base + self.tipo.salto_niveles

    @property
    def niveles_cubiertos(self) -> tuple[int, ...]:
        return tuple(range(self.nivel_base, self.nivel_cima))


@dataclass(frozen=True, slots=True)
class RestriccionNivel:
    """Relacion dirigida ``nivel(destino) = nivel(origen) + salto``.

    ``salto`` admite cero y valores negativos. Esto permite expresar tanto
    descansos como descensos sin convertir la direccion de una medina en una
    propiedad global de la arista compartida.
    """

    origen: str
    destino: str
    salto: int

    def __post_init__(self) -> None:
        if not isinstance(self.origen, str) or not self.origen:
            raise ValueError("origen debe ser un identificador no vacio")
        if not isinstance(self.destino, str) or not self.destino:
            raise ValueError("destino debe ser un identificador no vacio")
        if self.origen == self.destino:
            raise ValueError("una restriccion necesita dos nodos distintos")
        _validar_entero("salto", self.salto)


class InconsistenciaNiveles(ValueError):
    """Las restricciones o sus anclas exigen cotas incompatibles."""


class RestriccionSinFirmar(ValueError):
    """Se pidio propagar con vecindades cuyo salto aun no tiene evidencia."""


@dataclass(frozen=True, slots=True)
class RelacionVecindad:
    """Dos teselas que se tocan, con el salto de nivel declarado o pendiente.

    Que dos teselas compartan una medina no dice si entre ellas hay ascenso,
    descanso o descenso: ese signo se lee de las flechas de la planta
    propuesta, y la figura 128 de Dos Hermanas no las trae. Por eso ``salto``
    admite ``None`` y ese es su valor por defecto. Una relacion sin firmar se
    conserva como dato explicito y **no** se convierte en restriccion.
    """

    origen: str
    destino: str
    salto: int | None = None
    evidencia: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.origen, str) or not self.origen:
            raise ValueError("origen debe ser un identificador no vacio")
        if not isinstance(self.destino, str) or not self.destino:
            raise ValueError("destino debe ser un identificador no vacio")
        if self.origen == self.destino:
            raise ValueError("una vecindad necesita dos teselas distintas")
        if self.salto is not None:
            _validar_entero("salto", self.salto)
            if not self.evidencia:
                raise ValueError(
                    "un salto firmado necesita citar su evidencia; "
                    f"falta en {self.origen!r}->{self.destino!r}"
                )

    @property
    def esta_firmada(self) -> bool:
        return self.salto is not None

    def como_restriccion(self) -> RestriccionNivel:
        if self.salto is None:
            raise RestriccionSinFirmar(
                f"la vecindad {self.origen!r}->{self.destino!r} no tiene signo"
            )
        return RestriccionNivel(self.origen, self.destino, self.salto)


@dataclass(frozen=True, slots=True)
class ResultadoNiveles:
    """Solucion parcial y componentes que aun carecen de ancla.

    ``niveles`` solo contiene componentes con una cota absoluta anclada. Los
    componentes sin ancla se conservan aparte y no reciben un cero ficticio.
    """

    niveles: Mapping[str, int]
    componentes_sin_ancla: tuple[frozenset[str], ...]

    def __post_init__(self) -> None:
        niveles = dict(self.niveles)
        for nodo, nivel in niveles.items():
            if not isinstance(nodo, str) or not nodo:
                raise ValueError("todos los nodos deben tener identificador")
            _validar_entero(f"nivel de {nodo}", nivel)
        componentes = tuple(frozenset(c) for c in self.componentes_sin_ancla)
        if any(not c for c in componentes):
            raise ValueError("un componente sin ancla no puede estar vacio")
        vistos: set[str] = set()
        for componente in componentes:
            if vistos.intersection(componente):
                raise ValueError("los componentes sin ancla deben ser disjuntos")
            vistos.update(componente)
        sin_resolver = set().union(*componentes) if componentes else set()
        if sin_resolver.intersection(niveles):
            raise ValueError("un nodo no puede estar resuelto y sin ancla")
        object.__setattr__(self, "niveles", MappingProxyType(niveles))
        object.__setattr__(self, "componentes_sin_ancla", componentes)

    @property
    def esta_completo(self) -> bool:
        return not self.componentes_sin_ancla

    def exigir_completo(self) -> Mapping[str, int]:
        if not self.esta_completo:
            grupos = [sorted(c) for c in self.componentes_sin_ancla]
            raise ValueError(f"quedan componentes sin ancla: {grupos}")
        return self.niveles


def resolver_niveles(
    restricciones: Iterable[RestriccionNivel],
    anclas: Mapping[str, int] | None = None,
) -> ResultadoNiveles:
    """Propaga cotas enteras y falla si encuentra un ciclo contradictorio.

    Las restricciones determinan diferencias de nivel. Una o mas ``anclas``
    fijan la cota absoluta de sus componentes. Sin ancla solo existe una
    solucion salvo traslacion vertical, por lo que ese componente no se
    devuelve como resuelto.
    """

    lista = tuple(restricciones)
    if any(not isinstance(r, RestriccionNivel) for r in lista):
        raise TypeError("todas las restricciones deben ser RestriccionNivel")

    anclas_dict = dict(anclas or {})
    for nodo, nivel in anclas_dict.items():
        if not isinstance(nodo, str) or not nodo:
            raise ValueError("cada ancla necesita un identificador no vacio")
        _validar_entero(f"ancla de {nodo}", nivel)
        if nivel < 0:
            raise ValueError("las anclas no pueden ser negativas")

    adyacencia: dict[str, list[tuple[str, int]]] = defaultdict(list)
    nodos = set(anclas_dict)
    for r in lista:
        nodos.update((r.origen, r.destino))
        adyacencia[r.origen].append((r.destino, r.salto))
        adyacencia[r.destino].append((r.origen, -r.salto))

    resueltos: dict[str, int] = {}
    sin_ancla: list[frozenset[str]] = []
    visitados: set[str] = set()

    for raiz in sorted(nodos):
        if raiz in visitados:
            continue
        relativos = {raiz: 0}
        cola = deque([raiz])
        while cola:
            actual = cola.popleft()
            for vecino, salto in adyacencia[actual]:
                propuesto = relativos[actual] + salto
                if vecino in relativos:
                    if relativos[vecino] != propuesto:
                        raise InconsistenciaNiveles(
                            f"ciclo incompatible en {actual!r}->{vecino!r}: "
                            f"{relativos[vecino]} != {propuesto}"
                        )
                    continue
                relativos[vecino] = propuesto
                cola.append(vecino)

        componente = frozenset(relativos)
        visitados.update(componente)
        offsets = {
            anclas_dict[nodo] - relativo
            for nodo, relativo in relativos.items()
            if nodo in anclas_dict
        }
        if not offsets:
            sin_ancla.append(componente)
            continue
        if len(offsets) != 1:
            raise InconsistenciaNiveles(
                f"anclas incompatibles en el componente {sorted(componente)}"
            )
        offset = offsets.pop()
        absolutos = {nodo: relativo + offset for nodo, relativo in relativos.items()}
        if min(absolutos.values()) < 0:
            raise InconsistenciaNiveles(
                f"la propagacion produce niveles negativos en {sorted(componente)}"
            )
        resueltos.update(absolutos)

    sin_ancla.sort(key=lambda c: tuple(sorted(c)))
    return ResultadoNiveles(resueltos, tuple(sin_ancla))


def restricciones_firmadas(
    relaciones: Iterable[RelacionVecindad],
) -> tuple[RestriccionNivel, ...]:
    """Convierte vecindades en restricciones, o falla nombrando las que faltan.

    Es deliberadamente cerrado: mientras quede una vecindad sin firmar no hay
    conversion parcial, porque propagar con un subconjunto arbitrario daria una
    planta de niveles que parece resuelta sin serlo.
    """

    lista = tuple(relaciones)
    if any(not isinstance(r, RelacionVecindad) for r in lista):
        raise TypeError("todas las relaciones deben ser RelacionVecindad")
    sin_firmar = [(r.origen, r.destino) for r in lista if not r.esta_firmada]
    if sin_firmar:
        raise RestriccionSinFirmar(
            f"{len(sin_firmar)} vecindades sin signo de nivel, "
            f"empezando por {sin_firmar[:3]}"
        )
    return tuple(r.como_restriccion() for r in lista)


def admite_salto_unitario(
    relaciones: Iterable[RelacionVecindad],
) -> tuple[bool, tuple[str, ...]]:
    """Existe alguna nivelacion en la que toda vecindad salve un nivel exacto?

    Alrededor de cualquier ciclo los saltos suman cero. Si todos valieran mas
    o menos uno, la suma tendria la paridad del numero de pasos: un ciclo de
    longitud impar no puede cerrar. La respuesta es afirmativa si y solo si el
    grafo de vecindades es bipartito.

    Un ciclo impar es, por tanto, la prueba de que ahi hace falta un descanso
    o una pieza que salve dos niveles. La pregunta es estructural: mira quien
    toca con quien e **ignora** el salto que cada relacion lleve firmado.

    Devuelve ``(True, ())`` o ``(False, ciclo testigo)``.
    """

    lista = tuple(relaciones)
    if any(not isinstance(r, RelacionVecindad) for r in lista):
        raise TypeError("todas las relaciones deben ser RelacionVecindad")

    adyacencia: dict[str, list[str]] = defaultdict(list)
    for relacion in lista:
        adyacencia[relacion.origen].append(relacion.destino)
        adyacencia[relacion.destino].append(relacion.origen)

    color: dict[str, int] = {}
    padre: dict[str, str | None] = {}
    for raiz in sorted(adyacencia):
        if raiz in color:
            continue
        color[raiz] = 0
        padre[raiz] = None
        cola = deque([raiz])
        while cola:
            actual = cola.popleft()
            for vecino in adyacencia[actual]:
                if vecino not in color:
                    color[vecino] = 1 - color[actual]
                    padre[vecino] = actual
                    cola.append(vecino)
                elif color[vecino] == color[actual]:
                    return (False, _ciclo_entre(padre, actual, vecino))
    return (True, ())


def _ciclo_entre(
    padre: Mapping[str, str | None], uno: str, otro: str
) -> tuple[str, ...]:
    """Ciclo que cierran dos nodos del mismo color mas la arista que los une."""

    def hasta_la_raiz(nodo: str) -> list[str]:
        camino = []
        actual: str | None = nodo
        while actual is not None:
            camino.append(actual)
            actual = padre[actual]
        return camino

    rama_uno = hasta_la_raiz(uno)
    rama_otro = hasta_la_raiz(otro)
    en_rama_uno = set(rama_uno)
    for posicion, nodo in enumerate(rama_otro):
        if nodo in en_rama_uno:
            corte = rama_uno.index(nodo)
            return tuple(rama_uno[: corte + 1] + list(reversed(rama_otro[:posicion])))
    return tuple(rama_uno + rama_otro)


def resolver_desde_vecindades(
    relaciones: Iterable[RelacionVecindad],
    anclas: Mapping[str, int] | None = None,
) -> ResultadoNiveles:
    """Propaga niveles solo si todas las vecindades llevan salto firmado."""

    return resolver_niveles(restricciones_firmadas(relaciones), anclas)


def _validar_entero(nombre: str, valor: object) -> None:
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise TypeError(f"{nombre} debe ser un entero")
