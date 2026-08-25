#!/usr/bin/env python3
"""Somete reglas candidatas de nivel a los ciclos del grafo de vecindades.

No asigna niveles: intenta refutarlos. Una regla propone un salto firmado para
cada vecindad; alrededor de cada ciclo los saltos tienen que sumar cero. Si no
suman, la regla es imposible sobre esta planta, y el ciclo que la rompe queda
como testigo con nombre y apellido.

Dos controles positivos acompanan a las reglas para que el test no sea vacuo:
una regla trivial y otra construida a proposito para ser consistente. Si esas
dos no pasaran, el que estaria mal seria el test.

El contorno exterior **no** entra en el dual: es un solo nodo artificial que
une las 16 caras del borde y crearia ciclos que no existen en la cupula.

Sin dependencias fuera de la biblioteca estandar y de ``granada``.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import defaultdict, deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from granada.niveles import (  # noqa: E402
    RelacionVecindad,
    admite_salto_unitario,
)

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA_CARAS = RAIZ / "datos" / "caras_red.json"
ENTRADA_RED = RAIZ / "datos" / "red_medinas.json"
SALIDA = RAIZ / "datos" / "reglas_de_nivel.json"

# Paso de hilada medido en la seccion meridiana, en metros, y radio del borde.
PASO_HILADA_M = 0.20
UMBRALES_PX = (0, 10, 15, 20, 25, 30, 40)


def cargar():
    crudo_caras = ENTRADA_CARAS.read_bytes()
    caras_json = json.loads(crudo_caras)
    red = json.loads(ENTRADA_RED.read_bytes())
    caras = {cara["id"]: cara for cara in caras_json["caras"]}
    longitudes = {
        (min(a, b), max(a, b)): longitud for a, b, longitud, _ in red["aristas"]
    }
    angulos = {(min(a, b), max(a, b)): angulo for a, b, _, angulo in red["aristas"]}
    px_por_metro = sum(red["registro"]["px_por_metro"]) / 2
    interiores = [
        vecindad
        for vecindad in caras_json["vecindades"]
        if "contorno" not in (vecindad["a"], vecindad["b"])
    ]
    return caras_json, caras, interiores, longitudes, angulos, px_por_metro


def longitud_compartida(vecindad, longitudes) -> float:
    return sum(
        longitudes[(min(a, b), max(a, b))] for a, b in vecindad["aristas"]
    )


def es_ortogonal(vecindad, angulos) -> bool:
    """La medina compartida sigue una direccion de lado, no una diagonal."""

    medidos = [angulos[(min(a, b), max(a, b))] for a, b in vecindad["aristas"]]
    ortogonales = sum(1 for a in medidos if min(a % 90, 90 - a % 90) < 22.5)
    return ortogonales * 2 >= len(medidos)


def hacia_el_centro(vecindad, caras) -> tuple[str, str]:
    a, b = vecindad["a"], vecindad["b"]
    if caras[a]["radio_m"] > caras[b]["radio_m"]:
        return (a, b)
    return (b, a)


def consistencia(firmadas: list[tuple[str, str, int]]) -> dict:
    """Cuenta ciclos fundamentales incumplidos y devuelve un testigo."""

    adyacencia: dict[str, list[tuple[str, int]]] = defaultdict(list)
    nodos: set[str] = set()
    for origen, destino, salto in firmadas:
        nodos |= {origen, destino}
        adyacencia[origen].append((destino, salto))
        adyacencia[destino].append((origen, -salto))

    cota: dict[str, int] = {}
    padre: dict[str, str | None] = {}
    arbol: set[tuple[str, str]] = set()
    for raiz in sorted(nodos):
        if raiz in cota:
            continue
        cota[raiz] = 0
        padre[raiz] = None
        cola = deque([raiz])
        while cola:
            actual = cola.popleft()
            for vecino, salto in adyacencia[actual]:
                if vecino not in cota:
                    cota[vecino] = cota[actual] + salto
                    padre[vecino] = actual
                    arbol.add((min(actual, vecino), max(actual, vecino)))
                    cola.append(vecino)

    violadas = [
        (origen, destino, salto, cota[destino] - cota[origen])
        for origen, destino, salto in firmadas
        if (min(origen, destino), max(origen, destino)) not in arbol
        and cota[destino] - cota[origen] != salto
    ]
    testigo: tuple[str, ...] = ()
    if violadas:
        origen, destino = violadas[0][0], violadas[0][1]
        rama = []
        actual: str | None = origen
        while actual is not None:
            rama.append(actual)
            actual = padre[actual]
        otra = []
        actual = destino
        while actual is not None:
            otra.append(actual)
            actual = padre[actual]
        comun = set(rama)
        for posicion, nodo in enumerate(otra):
            if nodo in comun:
                corte = rama.index(nodo)
                testigo = tuple(rama[: corte + 1] + list(reversed(otra[:posicion])))
                break
    return {
        "consistente": not violadas,
        "ciclos_fundamentales_violados": len(violadas),
        "testigo": list(testigo),
    }


def triangulos(vecindades) -> list[tuple[str, str, str]]:
    adyacencia: dict[str, set[str]] = defaultdict(set)
    for vecindad in vecindades:
        adyacencia[vecindad["a"]].add(vecindad["b"])
        adyacencia[vecindad["b"]].add(vecindad["a"])
    return [
        (uno, otro, tercero)
        for uno in sorted(adyacencia)
        for otro, tercero in itertools.combinations(sorted(adyacencia[uno]), 2)
        if tercero in adyacencia[otro] and uno < otro < tercero
    ]


def como_relaciones(vecindades) -> list[RelacionVecindad]:
    return [RelacionVecindad(v["a"], v["b"]) for v in vecindades]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    argumentos = parser.parse_args()

    caras_json, caras, interiores, longitudes, angulos, px_por_metro = cargar()
    radio_maximo = max(cara["radio_m"] for cara in caras.values())

    reglas = {
        "R1_toda_medina_salva_un_nivel": {
            "enunciado": "toda medina separa dos niveles consecutivos, en el "
            "sentido que sea",
            "tipo": "candidata",
            "firma": None,  # no fija sentido: es una pregunta de existencia
        },
        "R2_ascenso_hacia_el_centro": {
            "enunciado": "se sube un nivel al cruzar cada medina hacia el centro",
            "tipo": "candidata",
            "firma": lambda v: (*hacia_el_centro(v, caras), 1),
        },
        "R3_ortogonales_suben_diagonales_descansan": {
            "enunciado": "las medinas de lado suben un nivel hacia el centro y "
            "las diagonales son descansos",
            "tipo": "candidata",
            "firma": lambda v: (
                *hacia_el_centro(v, caras),
                1 if es_ortogonal(v, angulos) else 0,
            ),
        },
        "C1_todo_descanso": {
            "enunciado": "control positivo trivial: ninguna medina cambia de nivel",
            "tipo": "control",
            "firma": lambda v: (v["a"], v["b"], 0),
        },
        "C2_coronas_cuantizadas": {
            "enunciado": "control positivo no trivial: nivel = radio cuantizado al "
            "paso de hilada medido, 20 cm (modelo de coronas, rechazado en 0003 "
            "por contradecir el teselado)",
            "tipo": "control",
            "firma": lambda v: (
                v["a"],
                v["b"],
                _corona(caras[v["b"]], radio_maximo)
                - _corona(caras[v["a"]], radio_maximo),
            ),
        },
    }

    resultados = {}
    for nombre, regla in reglas.items():
        if regla["firma"] is None:
            posible, testigo = admite_salto_unitario(como_relaciones(interiores))
            resultados[nombre] = {
                "enunciado": regla["enunciado"],
                "tipo": regla["tipo"],
                "consistente": posible,
                "criterio": "el grafo de vecindades tiene que ser bipartito",
                "testigo": list(testigo),
            }
            continue
        firmadas = [regla["firma"](v) for v in interiores]
        salida = consistencia(firmadas)
        salida["enunciado"] = regla["enunciado"]
        salida["tipo"] = regla["tipo"]
        salida["saltos"] = {
            str(valor): sum(1 for _, _, s in firmadas if s == valor)
            for valor in sorted({s for _, _, s in firmadas})
        }
        resultados[nombre] = salida

    lista_triangulos = triangulos(interiores)
    barrido = []
    for umbral in UMBRALES_PX:
        conservadas = [
            v
            for v in interiores
            if longitud_compartida(v, longitudes) * px_por_metro >= umbral
        ]
        posible, _ = admite_salto_unitario(como_relaciones(conservadas))
        barrido.append(
            {
                "umbral_px": umbral,
                "vecindades": len(conservadas),
                "caras": len({c for v in conservadas for c in (v["a"], v["b"])}),
                "triangulos": len(triangulos(conservadas)),
                "admite_salto_unitario": posible,
                "ciclos_violados_por_R2": consistencia(
                    [(*hacia_el_centro(v, caras), 1) for v in conservadas]
                )["ciclos_fundamentales_violados"],
            }
        )

    compartidas = sorted(
        longitud_compartida(v, longitudes) * px_por_metro for v in interiores
    )
    en_triangulo = sorted(
        longitud_compartida(v, longitudes) * px_por_metro
        for v in interiores
        if any(
            {v["a"], v["b"]} <= set(triangulo) for triangulo in lista_triangulos
        )
    )

    documento = {
        "version": 1,
        "fuente": {
            "derivado_de": "datos/caras_red.json",
            "sha256_caras": hashlib.sha256(ENTRADA_CARAS.read_bytes()).hexdigest(),
        },
        "metodo": {
            "dual": "105 caras y 211 vecindades interiores; el contorno exterior "
            "queda fuera por ser un nodo artificial",
            "ciclos_independientes": len(interiores) - len(caras) + 1,
            "criterio": "alrededor de cada ciclo los saltos firmados suman cero",
            "paso_hilada_m": PASO_HILADA_M,
        },
        "reglas": resultados,
        "teorema_del_triangulo": {
            "enunciado": "tres teselas mutuamente vecinas no pueden salvar un "
            "nivel cada par: la suma de tres saltos de valor absoluto uno es "
            "impar y nunca cierra en cero. Al menos una de las tres medinas es "
            "un descanso o salva dos niveles.",
            "triangulos": len(lista_triangulos),
            "triangulos_robustos_30px": barrido[-2]["triangulos"],
            "lista": [list(t) for t in lista_triangulos],
        },
        "robustez": {
            "barrido_de_longitud_compartida": barrido,
            "longitud_compartida_px": {
                "minima": compartidas[0],
                "mediana": compartidas[len(compartidas) // 2],
                "maxima": compartidas[-1],
            },
            "longitud_compartida_en_triangulos_px": {
                "minima": en_triangulo[0],
                "mediana": en_triangulo[len(en_triangulo) // 2],
                "maxima": en_triangulo[-1],
            },
        },
        "estado": "BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS",
    }

    argumentos.salida.write_text(
        json.dumps(documento, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    for nombre, salida in resultados.items():
        veredicto = "consistente" if salida["consistente"] else "IMPOSIBLE"
        detalle = ""
        if not salida["consistente"] and "ciclos_fundamentales_violados" in salida:
            detalle = f" ({salida['ciclos_fundamentales_violados']} ciclos rotos)"
        print(f"{salida['tipo']:9s} {nombre:42s} {veredicto}{detalle}")
    print(
        f"triangulos del dual: {len(lista_triangulos)}, "
        f"robustos a 30 px: {barrido[-2]['triangulos']}"
    )
    print(f"escrito {argumentos.salida}")
    return 0


def _corona(cara, radio_maximo: float) -> int:
    return round((radio_maximo - cara["radio_m"]) / PASO_HILADA_M)


if __name__ == "__main__":
    raise SystemExit(main())
