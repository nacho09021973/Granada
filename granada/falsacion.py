"""Que se puede concluir del primer salto de nivel que llegue firmado.

El bloqueo `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` no se levanta con las
cotas de las 5.416 piezas ni con los signos de las 211 vecindades. La cadena de
reduccion de la decision 0007 deja **once orbitas** bajo la hipotesis de que la
nivelacion respeta el diedrico de orden 16, y esa hipotesis es lo primero que
hay que poner a prueba, no dar por bueno.

Este modulo prepara ese examen para que el dia que llegue un dato la respuesta
sea inmediata. No inventa ningun salto: sin datos de entrada devuelve un
informe que dice exactamente eso.

La palanca, y por que un solo dato vale tanto
---------------------------------------------
Si la nivelacion respeta el grupo, dos caras de la misma orbita estan a la
misma cota. Entonces cada vecindad entre caras solo depende del **par de
orbitas** que conecta, y las 211 vecindades interiores colapsan a **16 clases**:
el grafo cociente sobre las once orbitas. Cada clase agrupa entre 4 y 16
vecindades que la hipotesis obliga a llevar **el mismo salto**.

De ahi las dos consecuencias que este modulo calcula:

* **Un salto firmado determina su clase entera**, de 4 a 16 vecindades de golpe.
* **Dos saltos de la misma clase que no coincidan refutan la hipotesis**, sin
  necesidad de propagar nada.

Y como el cociente tiene 16 aristas para 11 nodos y es conexo, le sobran
**6 ciclos independientes**: seis ecuaciones de cierre que un conjunto de saltos
firmados tiene que satisfacer. Son seis oportunidades mas de refutar.

Lo que este modulo NO hace
--------------------------
No usa la seccion de Almagro como ancla. La decision 0007 midio que una banda de
esa seccion abarca hasta ocho hiladas: da una cota **acotada**, no un nivel, y
meterla aqui como si fuera exacta seria fabricar precision.

Tampoco supone que la hipotesis sea cierta. Su unico proposito es dejar dicho de
antemano que observacion la mataria.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence

from granada.niveles import (
    InconsistenciaNiveles,
    RelacionVecindad,
    RestriccionNivel,
    resolver_niveles,
)

__all__ = [
    "ContradiccionDeClase",
    "InformeFalsacion",
    "Cociente",
    "cociente_de_orbitas",
    "examinar",
]

CONSISTENTE = "CONSISTENTE_CON_LA_SIMETRIA"
REFUTADA = "SIMETRIA_REFUTADA"
SIN_DATOS = "SIN_SALTOS_FIRMADOS"


def _clase(orbita_a: int, orbita_b: int) -> tuple[int, int]:
    """Identificador de la clase de vecindad: el par de orbitas, sin orden."""
    return (orbita_a, orbita_b) if orbita_a <= orbita_b else (orbita_b, orbita_a)


@dataclass(frozen=True, slots=True)
class Cociente:
    """El grafo de orbitas, con las vecindades que colapsan en cada arista."""

    de_orbita: Mapping[str, int]
    clases: Mapping[tuple[int, int], tuple[tuple[str, str], ...]]

    @property
    def n_orbitas(self) -> int:
        return len(set(self.de_orbita.values()))

    @property
    def n_aristas(self) -> int:
        return len(self.clases)

    @property
    def n_vecindades(self) -> int:
        return sum(len(v) for v in self.clases.values())

    @property
    def ciclos_independientes(self) -> int:
        """Aristas - nodos + componentes. Cada uno es una ecuacion de cierre."""
        padre = {o: o for o in set(self.de_orbita.values())}

        def raiz(x: int) -> int:
            while padre[x] != x:
                padre[x] = padre[padre[x]]
                x = padre[x]
            return x

        for i, j in self.clases:
            padre[raiz(i)] = raiz(j)
        componentes = len({raiz(o) for o in padre})
        return self.n_aristas - self.n_orbitas + componentes

    def clases_con_tamano_anomalo(self, orden_del_grupo: int = 16) -> tuple[tuple[int, int], ...]:
        """Clases cuyo tamano no divide al orden del grupo: se delatan solas.

        Es el mismo control que la decision 0007 aplica a los tamanos de orbita.
        Si la nivelacion respeta el grupo, una clase de vecindad es una orbita de
        pares y su cardinal tiene que dividir al orden. Un tamano que no divide
        no refuta la simetria: acusa a los **datos**, casi siempre una arista que
        la digitalizacion no cerro.
        """
        return tuple(
            clase
            for clase, vs in sorted(self.clases.items())
            if orden_del_grupo % len(vs)
        )

    def caras_sin_pareja(self, clase: tuple[int, int]) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """En una clase incompleta, que caras de cada orbita se quedaron sueltas."""
        grado: dict[str, int] = defaultdict(int)
        for a, b in self.clases.get(clase, ()):
            grado[a] += 1
            grado[b] += 1
        izq = tuple(
            sorted(c for c, o in self.de_orbita.items() if o == clase[0] and not grado[c])
        )
        der = tuple(
            sorted(c for c, o in self.de_orbita.items() if o == clase[1] and not grado[c])
        )
        return izq, der

    def clase_de(self, cara_a: str, cara_b: str) -> tuple[int, int]:
        for cara in (cara_a, cara_b):
            if cara not in self.de_orbita:
                raise KeyError(f"la cara {cara!r} no esta en ninguna orbita")
        return _clase(self.de_orbita[cara_a], self.de_orbita[cara_b])


@dataclass(frozen=True, slots=True)
class ContradiccionDeClase:
    """Dos saltos firmados que la simetria obligaba a ser iguales, y no lo son."""

    clase: tuple[int, int]
    primero: tuple[str, str, int]
    segundo: tuple[str, str, int]

    def __str__(self) -> str:
        a1, b1, s1 = self.primero
        a2, b2, s2 = self.segundo
        return (
            f"clase {self.clase}: {a1}->{b1} da {s1:+d} pero {a2}->{b2} da {s2:+d}"
        )


@dataclass(frozen=True, slots=True)
class InformeFalsacion:
    """Que dicen los saltos firmados que hay hasta ahora."""

    veredicto: str
    saltos_por_clase: Mapping[tuple[int, int], int]
    contradicciones: tuple[ContradiccionDeClase, ...]
    ciclo_roto: str
    orbitas_libres: int
    vecindades_determinadas: int
    componentes: tuple[frozenset[int], ...] = field(default=())

    @property
    def esta_refutada(self) -> bool:
        return self.veredicto == REFUTADA

    def resumen(self) -> str:
        lineas = [f"veredicto: {self.veredicto}"]
        if self.contradicciones:
            lineas.append("contradicciones dentro de una clase:")
            lineas.extend(f"  {c}" for c in self.contradicciones)
        if self.ciclo_roto:
            lineas.append(f"ciclo de cierre roto: {self.ciclo_roto}")
        lineas.append(
            f"clases firmadas: {len(self.saltos_por_clase)}"
            f"  ->  {self.vecindades_determinadas} de las 211 vecindades determinadas"
        )
        lineas.append(f"orbitas aun libres: {self.orbitas_libres}")
        return "\n".join(lineas)


def cociente_de_orbitas(
    vecindades: Iterable[Mapping[str, object]],
    orbitas: Iterable[Mapping[str, object]],
) -> Cociente:
    """Colapsa las vecindades de cara en clases por el par de orbitas.

    Las vecindades que tocan el contorno se descartan: el contorno no es una
    cara y no tiene orbita. Quedan las 211 interiores.
    """

    de_orbita: dict[str, int] = {}
    for o in orbitas:
        indice = int(o["orbita"])  # type: ignore[index]
        for cara in o["caras"]:  # type: ignore[index]
            de_orbita[str(cara)] = indice

    clases: dict[tuple[int, int], list[tuple[str, str]]] = defaultdict(list)
    for v in vecindades:
        a, b = str(v["a"]), str(v["b"])
        if a not in de_orbita or b not in de_orbita:
            continue
        clases[_clase(de_orbita[a], de_orbita[b])].append((a, b))

    return Cociente(
        de_orbita=dict(de_orbita),
        clases={k: tuple(v) for k, v in sorted(clases.items())},
    )


def _orientar(cociente: Cociente, a: str, b: str, salto: int) -> tuple[int, int, int]:
    """Lleva el salto al sentido canonico de la clase: de la orbita menor a la mayor."""
    oa, ob = cociente.de_orbita[a], cociente.de_orbita[b]
    return (oa, ob, salto) if oa <= ob else (ob, oa, -salto)


def examinar(
    saltos: Sequence[RelacionVecindad],
    cociente: Cociente,
) -> InformeFalsacion:
    """Somete la hipotesis de simetria a los saltos firmados que haya.

    Devuelve un informe aunque no haya ninguno: en ese caso dice cuantas
    orbitas siguen libres, que son todas.
    """

    firmados = [s for s in saltos if s.esta_firmada]
    for s in firmados:
        cociente.clase_de(s.origen, s.destino)  # valida que las caras existen

    por_clase: dict[tuple[int, int], tuple[str, str, int]] = {}
    contradicciones: list[ContradiccionDeClase] = []
    for s in firmados:
        oa, ob, salto = _orientar(cociente, s.origen, s.destino, int(s.salto or 0))
        clase = (oa, ob)
        if clase in por_clase:
            *_, previo = por_clase[clase]
            if previo != salto:
                a0, b0, _ = por_clase[clase]
                contradicciones.append(
                    ContradiccionDeClase(
                        clase=clase,
                        primero=(a0, b0, previo),
                        segundo=(s.origen, s.destino, salto),
                    )
                )
            continue
        por_clase[clase] = (s.origen, s.destino, salto)

    saltos_por_clase = {c: v[2] for c, v in por_clase.items()}

    # Ecuaciones de cierre: se delega en la maquinaria ya probada de niveles.
    ciclo_roto = ""
    restricciones = [
        RestriccionNivel(f"o{i:02d}", f"o{j:02d}", salto)
        for (i, j), salto in sorted(saltos_por_clase.items())
    ]
    try:
        resultado = resolver_niveles(restricciones)
    except InconsistenciaNiveles as exc:
        ciclo_roto = str(exc)
        libres = cociente.n_orbitas
        componentes: tuple[frozenset[int], ...] = ()
    else:
        # Sin anclas todo componente queda "sin ancla": lo que interesa es cuantos.
        tocadas = {int(n[1:]) for c in resultado.componentes_sin_ancla for n in c}
        sueltas = cociente.n_orbitas - len(tocadas)
        componentes = tuple(
            frozenset(int(n[1:]) for n in c) for c in resultado.componentes_sin_ancla
        )
        libres = len(componentes) + sueltas

    determinadas = sum(len(cociente.clases.get(c, ())) for c in saltos_por_clase)

    if contradicciones or ciclo_roto:
        veredicto = REFUTADA
    elif not firmados:
        veredicto = SIN_DATOS
    else:
        veredicto = CONSISTENTE

    return InformeFalsacion(
        veredicto=veredicto,
        saltos_por_clase=saltos_por_clase,
        contradicciones=tuple(contradicciones),
        ciclo_roto=ciclo_roto,
        orbitas_libres=libres,
        vecindades_determinadas=determinadas,
        componentes=componentes,
    )
