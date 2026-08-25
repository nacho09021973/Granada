"""Caras del teselado: del grafo de medinas a las teselas y sus vecindades.

La red de medinas es un grafo plano dibujado. Sus **caras** son las regiones
que las medinas delimitan, es decir, las candidatas a tesela. Este modulo las
extrae con rotacion de semiaristas, las mide y las compara con las figuras
planas que la tesis documenta para el sistema occidental.

Tres cautelas gobiernan el diseno:

* Una cara es una region del dibujo, no una pieza. La figura plana (A, C, D,
  cuadrado, octogono) se lee de la planta; la **topologia** de la pieza
  (A1, A2, A3, B4, C1, C2, D3) no, y este modulo nunca la asigna.
* Solo se clasifica lo que ajusta dentro de una tolerancia declarada. Lo demas
  queda ``SIN_CLASIFICAR``: sin figura, no con una figura inventada.
* La vecindad entre dos caras es adyacencia, no diferencia de nivel. El signo
  del paso se representa aparte, en ``granada.niveles``, y sin firmar por
  defecto.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping, Sequence

__all__ = [
    "CONTORNO",
    "Cara",
    "FiguraPlana",
    "GrafoNoAdmisible",
    "PLANTILLAS",
    "Plantilla",
    "ResultadoCaras",
    "Vecindad",
    "ajuste_a_plantilla",
    "clasificar",
    "cruces_de_aristas",
    "extraer_caras",
    "tolerancia_por_resolucion",
]

#: Indice reservado para la cara exterior en una ``Vecindad``.
CONTORNO = -1


class GrafoNoAdmisible(ValueError):
    """El grafo no es un dibujo plano conexo del que extraer caras."""


class FiguraPlana(str, Enum):
    """Figuras planas documentadas para el teselado occidental.

    Las tres primeras son las figuras de Jones y Goury que la tesis identifica
    con angulos internos fijos; las dos ultimas son las figuras de la trama que
    la propuesta dibuja en esta cupula. ``SIN_CLASIFICAR`` no es una figura: es
    la ausencia de evidencia para asignar una.
    """

    MEDIO_CUADRADO = "medio_cuadrado"  # figura A, angulo opuesto 45 grados
    MEDIA_JAIRA = "media_jaira"  # figura C, triangulo de las jairas
    JAIRA = "jaira"  # figura D, rombo completo de 45/135
    CUADRADO = "cuadrado"
    OCTOGONO = "octogono"
    SIN_CLASIFICAR = "sin_clasificar"


@dataclass(frozen=True, slots=True)
class Plantilla:
    """Figura de referencia: angulos internos fijos y lados salvo escala.

    ``angulos[i]`` es el angulo interno en el vertice ``i`` y ``lados[i]`` la
    longitud del lado que va del vertice ``i`` al ``i + 1``. La escala es
    libre: el ajuste la estima y solo puntua la forma.
    """

    angulos: tuple[float, ...]
    lados: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.angulos) != len(self.lados):
            raise ValueError("angulos y lados deben tener la misma longitud")
        if len(self.angulos) < 3:
            raise ValueError("una plantilla necesita al menos tres vertices")
        if any(a <= 0 or a >= 360 for a in self.angulos):
            raise ValueError("angulos fuera de rango")
        if any(l <= 0 for l in self.lados):
            raise ValueError("los lados deben ser positivos")
        suma = sum(self.angulos)
        esperada = 180.0 * (len(self.angulos) - 2)
        if not math.isclose(suma, esperada, abs_tol=1e-9):
            raise ValueError(f"los angulos suman {suma}, no {esperada}")


_CUERDA_45 = 2 * math.sin(math.radians(22.5))  # raiz de 2 - raiz de 2

PLANTILLAS: Mapping[FiguraPlana, Plantilla] = {
    FiguraPlana.MEDIO_CUADRADO: Plantilla((90.0, 45.0, 45.0), (1.0, math.sqrt(2), 1.0)),
    FiguraPlana.MEDIA_JAIRA: Plantilla((45.0, 67.5, 67.5), (1.0, _CUERDA_45, 1.0)),
    FiguraPlana.JAIRA: Plantilla((45.0, 135.0, 45.0, 135.0), (1.0,) * 4),
    FiguraPlana.CUADRADO: Plantilla((90.0,) * 4, (1.0,) * 4),
    FiguraPlana.OCTOGONO: Plantilla((135.0,) * 8, (1.0,) * 8),
}


@dataclass(frozen=True, slots=True)
class Cara:
    """Una region cerrada del dibujo, medida y sin interpretar.

    ``vertices`` recorre la cara en sentido antihorario. ``angulos[i]`` es el
    angulo interno en ``vertices[i]``, en grados, y ``lados[i]`` la longitud
    del lado que sale de ese vertice.
    """

    vertices: tuple[int, ...]
    angulos: tuple[float, ...]
    lados: tuple[float, ...]
    area: float

    def __post_init__(self) -> None:
        if len(self.vertices) < 3:
            raise ValueError("una cara necesita al menos tres vertices")
        if not (len(self.vertices) == len(self.angulos) == len(self.lados)):
            raise ValueError("vertices, angulos y lados deben coincidir")
        if self.area <= 0:
            raise ValueError("una cara interior tiene area positiva")

    @property
    def numero_de_lados(self) -> int:
        return len(self.vertices)

    @property
    def lado_minimo(self) -> float:
        return min(self.lados)

    @property
    def perimetro(self) -> float:
        return math.fsum(self.lados)

    @property
    def es_convexa(self) -> bool:
        return all(angulo < 180.0 for angulo in self.angulos)


@dataclass(frozen=True, slots=True)
class Vecindad:
    """Dos caras que comparten al menos una arista de medina.

    ``cara_b`` vale ``CONTORNO`` cuando la vecina es el exterior. La vecindad
    dice que dos teselas se tocan; **no** dice si entre ellas hay ascenso,
    descanso o descenso.
    """

    cara_a: int
    cara_b: int
    aristas: tuple[tuple[int, int], ...]

    def __post_init__(self) -> None:
        if self.cara_a < 0:
            raise ValueError("cara_a debe ser una cara interior")
        if self.cara_b < CONTORNO or self.cara_a == self.cara_b:
            raise ValueError("cara_b debe ser otra cara interior o el contorno")
        if not self.aristas:
            raise ValueError("una vecindad comparte al menos una arista")

    @property
    def es_de_borde(self) -> bool:
        return self.cara_b == CONTORNO


@dataclass(frozen=True, slots=True)
class ResultadoCaras:
    """Caras interiores, contorno exterior y vecindades entre caras."""

    caras: tuple[Cara, ...]
    contorno: tuple[int, ...]
    area_contorno: float
    vecindades: tuple[Vecindad, ...]
    aristas_puente: tuple[tuple[int, int], ...]

    @property
    def numero_de_caras(self) -> int:
        return len(self.caras)

    @property
    def area_total(self) -> float:
        return math.fsum(cara.area for cara in self.caras)

    @property
    def vecindades_de_borde(self) -> tuple[Vecindad, ...]:
        return tuple(v for v in self.vecindades if v.es_de_borde)


def extraer_caras(
    nodos: Sequence[Sequence[float]],
    aristas: Iterable[Sequence[int]],
) -> ResultadoCaras:
    """Extrae las caras de un dibujo plano conexo por rotacion de semiaristas.

    Cada arista se recorre una vez en cada sentido. La semiarista siguiente es
    la primera en sentido horario alrededor del vertice de llegada, de modo que
    las caras interiores salen en sentido antihorario y el contorno exterior en
    sentido horario.

    Falla en vez de adivinar: exige indices validos, aristas sin repetir, grafo
    conexo y una unica cara exterior. Los cruces de aristas, que romperian la
    planaridad, se comprueban aparte con ``cruces_de_aristas``.
    """

    puntos = _validar_nodos(nodos)
    pares = _validar_aristas(aristas, len(puntos))

    vecinos: dict[int, list[int]] = {i: [] for i in range(len(puntos))}
    for a, b in pares:
        vecinos[a].append(b)
        vecinos[b].append(a)
    sueltos = [i for i, lista in vecinos.items() if not lista]
    if sueltos:
        raise GrafoNoAdmisible(f"nudos sin aristas: {sueltos[:5]}")
    if not _es_conexo(vecinos):
        raise GrafoNoAdmisible("el grafo tiene mas de una componente conexa")

    posicion: dict[int, dict[int, int]] = {}
    for centro, lista in vecinos.items():
        lista.sort(key=lambda otro: _rumbo(puntos[centro], puntos[otro]))
        posicion[centro] = {otro: i for i, otro in enumerate(lista)}

    ciclos = _recorrer_semiaristas(pares, vecinos, posicion)

    caras: list[Cara] = []
    contornos: list[tuple[tuple[int, ...], float]] = []
    cara_de_semiarista: dict[tuple[int, int], int] = {}
    for ciclo in ciclos:
        vertices = tuple(origen for origen, _ in ciclo)
        area = _area_orientada(puntos, vertices)
        if area <= 0:
            contornos.append((vertices, area))
            continue
        indice = len(caras)
        for semiarista in ciclo:
            cara_de_semiarista[semiarista] = indice
        caras.append(
            Cara(
                vertices=vertices,
                angulos=_angulos_internos(puntos, vertices),
                lados=_longitudes(puntos, vertices),
                area=area,
            )
        )

    if len(contornos) != 1:
        raise GrafoNoAdmisible(
            f"se esperaba una unica cara exterior, se hallaron {len(contornos)}"
        )
    contorno, area_contorno = contornos[0]
    for semiarista in zip(contorno, contorno[1:] + contorno[:1]):
        cara_de_semiarista[semiarista] = CONTORNO

    esperadas = len(pares) - len(puntos) + 2
    if len(ciclos) != esperadas:
        raise GrafoNoAdmisible(
            f"Euler no se cumple: {len(ciclos)} caras frente a {esperadas}; "
            "el dibujo no es plano tal como se da"
        )

    compartidas: dict[tuple[int, int], list[tuple[int, int]]] = {}
    puentes: list[tuple[int, int]] = []
    for a, b in pares:
        izquierda = cara_de_semiarista[(a, b)]
        derecha = cara_de_semiarista[(b, a)]
        if izquierda == derecha:
            puentes.append((a, b))
            continue
        clave = (min(izquierda, derecha), max(izquierda, derecha))
        compartidas.setdefault(clave, []).append((a, b))

    vecindades = tuple(
        Vecindad(cara_a=max(par), cara_b=min(par), aristas=tuple(sorted(lista)))
        for par, lista in sorted(compartidas.items())
    )
    return ResultadoCaras(
        caras=tuple(caras),
        contorno=contorno,
        area_contorno=abs(area_contorno),
        vecindades=vecindades,
        aristas_puente=tuple(sorted(puentes)),
    )


def ajuste_a_plantilla(cara: Cara, plantilla: Plantilla) -> tuple[float, float]:
    """Mejor ajuste de una cara a una plantilla salvo giro, reflexion y escala.

    Devuelve ``(desviacion angular maxima en grados, desviacion relativa
    maxima de lado)``. Si el numero de lados no coincide devuelve infinitos:
    una plantilla no cambia de numero de vertices.
    """

    n = cara.numero_de_lados
    if n != len(plantilla.angulos):
        return (math.inf, math.inf)

    mejor = (math.inf, math.inf)
    for angulos, lados in _variantes(cara.angulos, cara.lados):
        for giro in range(n):
            rotados_a = [angulos[(giro + i) % n] for i in range(n)]
            rotados_l = [lados[(giro + i) % n] for i in range(n)]
            desviacion_angular = max(
                abs(medido - patron)
                for medido, patron in zip(rotados_a, plantilla.angulos)
            )
            escala = math.fsum(
                medido / patron for medido, patron in zip(rotados_l, plantilla.lados)
            ) / n
            desviacion_lado = max(
                abs(medido - escala * patron)
                for medido, patron in zip(rotados_l, plantilla.lados)
            ) / escala
            if _peor((desviacion_angular, desviacion_lado)) < _peor(mejor):
                mejor = (desviacion_angular, desviacion_lado)
    return mejor


def clasificar(
    cara: Cara,
    tolerancia_grados: float,
    tolerancia_lado: float = 0.12,
) -> tuple[FiguraPlana, float, float]:
    """Asigna la figura documentada que ajuste dentro de las dos tolerancias.

    Devuelve ``(figura, desviacion angular, desviacion de lado)``. Si ninguna
    plantilla ajusta, la figura es ``SIN_CLASIFICAR`` y las desviaciones son
    las de la plantilla mas proxima, para poder auditar por que se rechazo.
    """

    if tolerancia_grados <= 0 or tolerancia_lado <= 0:
        raise ValueError("las tolerancias deben ser positivas")

    mejor = (FiguraPlana.SIN_CLASIFICAR, math.inf, math.inf)
    mejor_rechazada = (math.inf, math.inf)
    for figura, plantilla in PLANTILLAS.items():
        desviacion_angular, desviacion_lado = ajuste_a_plantilla(cara, plantilla)
        dentro = (
            desviacion_angular <= tolerancia_grados
            and desviacion_lado <= tolerancia_lado
        )
        normalizada = max(
            desviacion_angular / tolerancia_grados, desviacion_lado / tolerancia_lado
        )
        if dentro and normalizada < max(
            mejor[1] / tolerancia_grados, mejor[2] / tolerancia_lado
        ):
            mejor = (figura, desviacion_angular, desviacion_lado)
        if not dentro and _peor((desviacion_angular, desviacion_lado)) < _peor(
            mejor_rechazada
        ):
            mejor_rechazada = (desviacion_angular, desviacion_lado)

    if mejor[0] is FiguraPlana.SIN_CLASIFICAR:
        return (FiguraPlana.SIN_CLASIFICAR, *mejor_rechazada)
    return mejor


def tolerancia_por_resolucion(cara: Cara, resolucion: float) -> float:
    """Tolerancia angular que impone la resolucion del dibujo, en grados.

    Un vertice digitalizado con incertidumbre ``resolucion`` desplaza la
    direccion de cada uno de sus dos lados hasta ``resolucion / longitud``
    radianes. La cota se toma sobre el lado mas corto de la cara, que es el
    que mas angulo pierde. No es un parametro libre: sale de la tolerancia de
    simplificacion con la que se extrajo la red.
    """

    if resolucion <= 0:
        raise ValueError("la resolucion debe ser positiva")
    return math.degrees(2 * resolucion / cara.lado_minimo)


def cruces_de_aristas(
    nodos: Sequence[Sequence[float]],
    aristas: Iterable[Sequence[int]],
) -> tuple[tuple[tuple[int, int], tuple[int, int]], ...]:
    """Pares de aristas que se cortan sin compartir nudo.

    Un dibujo plano no tiene ninguno. Es el control que hay que pasar antes de
    llamar caras a las regiones que salen del recorrido.
    """

    puntos = _validar_nodos(nodos)
    pares = _validar_aristas(aristas, len(puntos))
    encontrados: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for i, (a, b) in enumerate(pares):
        for c, d in pares[i + 1 :]:
            if len({a, b, c, d}) < 4:
                continue
            if _se_cortan(puntos[a], puntos[b], puntos[c], puntos[d]):
                encontrados.append(((a, b), (c, d)))
    return tuple(encontrados)


def _validar_nodos(nodos: Sequence[Sequence[float]]) -> tuple[tuple[float, float], ...]:
    puntos: list[tuple[float, float]] = []
    for indice, nodo in enumerate(nodos):
        if len(nodo) != 2:
            raise ValueError(f"el nudo {indice} no tiene dos coordenadas")
        x, y = (float(nodo[0]), float(nodo[1]))
        if not (math.isfinite(x) and math.isfinite(y)):
            raise ValueError(f"el nudo {indice} no es finito")
        puntos.append((x, y))
    if len(puntos) < 3:
        raise GrafoNoAdmisible("hacen falta al menos tres nudos")
    if len(set(puntos)) != len(puntos):
        raise GrafoNoAdmisible("hay nudos repetidos en la misma posicion")
    return tuple(puntos)


def _validar_aristas(
    aristas: Iterable[Sequence[int]], total: int
) -> tuple[tuple[int, int], ...]:
    pares: list[tuple[int, int]] = []
    vistas: set[tuple[int, int]] = set()
    for arista in aristas:
        a, b = int(arista[0]), int(arista[1])
        if not (0 <= a < total and 0 <= b < total):
            raise ValueError(f"la arista {(a, b)} sale del rango de nudos")
        if a == b:
            raise GrafoNoAdmisible(f"el nudo {a} tiene un lazo")
        clave = (min(a, b), max(a, b))
        if clave in vistas:
            raise GrafoNoAdmisible(f"la arista {clave} esta repetida")
        vistas.add(clave)
        pares.append(clave)
    if not pares:
        raise GrafoNoAdmisible("no hay aristas")
    return tuple(pares)


def _es_conexo(vecinos: Mapping[int, Sequence[int]]) -> bool:
    inicio = next(iter(vecinos))
    vistos = {inicio}
    pila = [inicio]
    while pila:
        actual = pila.pop()
        for vecino in vecinos[actual]:
            if vecino not in vistos:
                vistos.add(vecino)
                pila.append(vecino)
    return len(vistos) == len(vecinos)


def _recorrer_semiaristas(
    pares: Sequence[tuple[int, int]],
    vecinos: Mapping[int, Sequence[int]],
    posicion: Mapping[int, Mapping[int, int]],
) -> list[list[tuple[int, int]]]:
    pendientes: set[tuple[int, int]] = set()
    for a, b in pares:
        pendientes.add((a, b))
        pendientes.add((b, a))

    ciclos: list[list[tuple[int, int]]] = []
    for inicio in sorted(pendientes):
        if inicio not in pendientes:
            continue
        ciclo: list[tuple[int, int]] = []
        actual = inicio
        while actual in pendientes:
            pendientes.discard(actual)
            ciclo.append(actual)
            origen, destino = actual
            lista = vecinos[destino]
            siguiente = lista[(posicion[destino][origen] - 1) % len(lista)]
            actual = (destino, siguiente)
        if actual != inicio:
            raise GrafoNoAdmisible("el recorrido de semiaristas no cierra")
        ciclos.append(ciclo)
    return ciclos


def _rumbo(origen: tuple[float, float], destino: tuple[float, float]) -> float:
    return math.atan2(destino[1] - origen[1], destino[0] - origen[0])


def _area_orientada(
    puntos: Sequence[tuple[float, float]], vertices: Sequence[int]
) -> float:
    total = math.fsum(
        puntos[u][0] * puntos[v][1] - puntos[v][0] * puntos[u][1]
        for u, v in zip(vertices, tuple(vertices[1:]) + (vertices[0],))
    )
    return total / 2


def _angulos_internos(
    puntos: Sequence[tuple[float, float]], vertices: Sequence[int]
) -> tuple[float, ...]:
    n = len(vertices)
    angulos = []
    for i, vertice in enumerate(vertices):
        anterior = vertices[(i - 1) % n]
        siguiente = vertices[(i + 1) % n]
        entrada = _rumbo(puntos[vertice], puntos[anterior])
        salida = _rumbo(puntos[vertice], puntos[siguiente])
        angulos.append(math.degrees((entrada - salida) % (2 * math.pi)))
    return tuple(angulos)


def _longitudes(
    puntos: Sequence[tuple[float, float]], vertices: Sequence[int]
) -> tuple[float, ...]:
    n = len(vertices)
    return tuple(
        math.dist(puntos[vertices[i]], puntos[vertices[(i + 1) % n]])
        for i in range(n)
    )


def _variantes(
    angulos: Sequence[float], lados: Sequence[float]
) -> tuple[tuple[tuple[float, ...], tuple[float, ...]], ...]:
    """La cara tal cual y su reflexion, con la correspondencia lado-vertice."""

    n = len(angulos)
    reflejados_a = tuple(angulos[(n - i) % n] for i in range(n))
    reflejados_l = tuple(lados[(n - 1 - i) % n] for i in range(n))
    return ((tuple(angulos), tuple(lados)), (reflejados_a, reflejados_l))


def _peor(desviaciones: tuple[float, float]) -> float:
    angular, lado = desviaciones
    return max(angular / 6.0, lado / 0.12)


def _se_cortan(
    p: tuple[float, float],
    q: tuple[float, float],
    r: tuple[float, float],
    s: tuple[float, float],
) -> bool:
    def cruz(
        o: tuple[float, float], a: tuple[float, float], b: tuple[float, float]
    ) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    d1, d2 = cruz(r, s, p), cruz(r, s, q)
    d3, d4 = cruz(p, q, r), cruz(p, q, s)
    return (d1 > 0) != (d2 > 0) and (d3 > 0) != (d4 > 0)
