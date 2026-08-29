#!/usr/bin/env python3
"""Infiere una nivelacion radial aproximada para la planta de Dos Hermanas.

Este script no convierte la inferencia en evidencia historica. Produce un
artefacto operativo separado de ``caras_red.json`` con dos escenarios: las 23
hiladas medidas sobre la seccion de Almagro y los 24 niveles contados de forma
rapida por Ferrer. Los saltos cierran por construccion porque se derivan de una
cota absoluta por cara.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from collections import Counter, defaultdict, deque
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "datos" / "caras_red.json"
SALIDA = RAIZ / "datos" / "niveles_aproximados.json"

RADIO_BASE_M = 3.64
ALTURA_TOTAL_M = 4.67
HILADAS_SECCION = 23
HILADAS_FERRER = 24
NIVELES_TOPOLOGICOS = 7
NIVELES_SENSIBILIDAD = 8
PASO_HORIZONTAL_M = RADIO_BASE_M / HILADAS_SECCION
PASO_VERTICAL_M = ALTURA_TOTAL_M / HILADAS_SECCION


def distancias_desde_borde(dato: dict) -> dict[str, int]:
    """Numero minimo de vecindades desde cada cara hasta el contorno."""
    adyacencia: dict[str, set[str]] = defaultdict(set)
    borde = set()
    for vecindad in dato["vecindades"]:
        a, b = vecindad["a"], vecindad["b"]
        if b == "contorno":
            borde.add(a)
        else:
            adyacencia[a].add(b)
            adyacencia[b].add(a)
    distancias = {cara: 0 for cara in borde}
    cola = deque(sorted(borde))
    while cola:
        actual = cola.popleft()
        for vecina in sorted(adyacencia[actual]):
            if vecina not in distancias:
                distancias[vecina] = distancias[actual] + 1
                cola.append(vecina)
    return distancias


def nivel_por_capa(capa: int, capa_maxima: int, niveles: int) -> int:
    return round(capa * niveles / capa_maxima)


def hilada_continua(radio_m: float) -> float:
    """Hilada de la seccion medida que corresponde a un radio en planta.

    Usa el paso horizontal medido sobre la seccion de Almagro. No es una regla
    de nivel: solo situa una banda ya formada por la topologia contra una
    seccion medida de forma independiente.
    """
    return (RADIO_BASE_M - radio_m) / PASO_HORIZONTAL_M


def calibrar_bandas(radios_por_banda: dict[int, list[float]]) -> dict[int, dict]:
    """Situa cada banda topologica en una hilada entera de la seccion."""
    bandas = {}
    for banda in sorted(radios_por_banda):
        hiladas = sorted(hilada_continua(r) for r in radios_por_banda[banda])
        cuartil = lambda p: hiladas[min(len(hiladas) - 1, int(p * (len(hiladas) - 1)))]
        mediana = statistics.median(hiladas)
        entera = max(0, min(HILADAS_SECCION, round(mediana)))
        bandas[banda] = {
            "banda": banda,
            "caras": len(hiladas),
            "radio_mediano_m": statistics.median(radios_por_banda[banda]),
            "hilada_mediana": mediana,
            "hilada": entera,
            "iqr_hiladas": cuartil(0.75) - cuartil(0.25),
            "altura_m": entera * PASO_VERTICAL_M,
        }
    return bandas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=ENTRADA)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    args = parser.parse_args()

    crudo = args.entrada.read_bytes()
    dato = json.loads(crudo)
    distancias = distancias_desde_borde(dato)
    capa_maxima = max(distancias.values())
    radios_por_banda: dict[int, list[float]] = defaultdict(list)
    for cara in dato["caras"]:
        radios_por_banda[distancias[cara["id"]]].append(cara["radio_m"])
    bandas = calibrar_bandas(radios_por_banda)

    caras = {}
    for cara in dato["caras"]:
        capa = distancias[cara["id"]]
        n7 = nivel_por_capa(capa, capa_maxima, NIVELES_TOPOLOGICOS)
        n8 = nivel_por_capa(capa, capa_maxima, NIVELES_SENSIBILIDAD)
        altura_conica = min(
            ALTURA_TOTAL_M, max(0.0, (RADIO_BASE_M - cara["radio_m"]) / 0.782)
        )
        caras[cara["id"]] = {
            "id": cara["id"],
            "radio_m": cara["radio_m"],
            "capa_desde_borde": capa,
            "nivel": n7,
            "nivel_8": n8,
            "intervalo_nivel": [min(n7, n8), max(n7, n8)],
            "estable_7_8": n7 == n8,
            "altura_conica_m": altura_conica,
            "hilada": bandas[capa]["hilada"],
            "altura_m": bandas[capa]["altura_m"],
            "iqr_hiladas_de_su_banda": bandas[capa]["iqr_hiladas"],
        }

    vecindades = []
    for vecindad in dato["vecindades"]:
        a, b = vecindad["a"], vecindad["b"]
        nivel_a = caras[a]["nivel"]
        nivel_b = 0 if b == "contorno" else caras[b]["nivel"]
        nivel_a8 = caras[a]["nivel_8"]
        nivel_b8 = 0 if b == "contorno" else caras[b]["nivel_8"]
        salto = nivel_b - nivel_a
        salto8 = nivel_b8 - nivel_a8
        hilada_a = caras[a]["hilada"]
        hilada_b = bandas[0]["hilada"] if b == "contorno" else caras[b]["hilada"]
        vecindades.append(
            {
                "a": a,
                "b": b,
                "salto": salto,
                "salto_8": salto8,
                "intervalo_salto": [min(salto, salto8), max(salto, salto8)],
                "estable_7_8": salto == salto8,
                "salto_hiladas": hilada_b - hilada_a,
                "procedencia": "diferencia de capas topologicas escaladas; no observado",
            }
        )

    conteo_niveles = Counter(cara["nivel"] for cara in caras.values())
    conteo_saltos = Counter(v["salto"] for v in vecindades)
    documento = {
        "version": 1,
        "estado": "APPROXIMATE_LEVELS_AVAILABLE",
        "advertencia": (
            "Reconstruccion operativa inferida, no nivelacion historica verificada. "
            "No sustituye las restricciones firmadas de datos/caras_red.json."
        ),
        "fuente": {
            "derivado_de": str(args.entrada.relative_to(RAIZ)),
            "sha256": hashlib.sha256(crudo).hexdigest(),
            "seccion_almagro": "23 hiladas, radio 3.64 m, altura 4.67 m",
            "comunicacion_ferrer_2026_08_28": "recuento rapido de 24 niveles",
            "martinez_sevilla_divulgacion": "siete niveles, sin metodo publicado",
        },
        "metodo": {
            "modelo": "capas minimas del dual desde el borde, escaladas a N niveles",
            "radio_base_m": RADIO_BASE_M,
            "altura_total_m": ALTURA_TOTAL_M,
            "hiladas_seccion": HILADAS_SECCION,
            "hiladas_recuento_ferrer": HILADAS_FERRER,
            "capas_del_grafo": capa_maxima,
            "niveles_topologicos_operativos": NIVELES_TOPOLOGICOS,
            "niveles_topologicos_sensibilidad": NIVELES_SENSIBILIDAD,
            "paso_horizontal_hilada_m": PASO_HORIZONTAL_M,
            "paso_vertical_hilada_m": PASO_VERTICAL_M,
            "cierre_de_ciclos": "garantizado al derivar cada salto de cotas absolutas",
        },
        "calibracion_altura": {
            "problema": (
                "el nivel topologico no da altura: repartir 4.67 m entre 7 niveles "
                "uniformes desfasaba hasta 1.51 m frente a la seccion medida"
            ),
            "modelo": (
                "la topologia agrupa las caras en bandas; la seccion medida situa "
                "cada banda en una hilada entera por el radio mediano de sus caras"
            ),
            "no_es_la_estratificacion_refutada": (
                "no asigna saltos por radio vecindad a vecindad, que es lo refutado "
                "en la decision 0006: asigna cotas absolutas de banda, de las que los "
                "saltos se derivan y por tanto cierran todos los ciclos"
            ),
            "supuesto": (
                "la envolvente es de revolucion, medida como cono de 38 grados sobre "
                "la seccion; las celdas cuelgan por debajo de esa envolvente"
            ),
            "bandas": [bandas[k] for k in sorted(bandas)],
        },
        "controles": {
            "caras": len(caras),
            "vecindades": len(vecindades),
            "caras_estables_7_8": sum(c["estable_7_8"] for c in caras.values()),
            "vecindades_estables_7_8": sum(v["estable_7_8"] for v in vecindades),
            "nivel_minimo": min(c["nivel"] for c in caras.values()),
            "nivel_maximo": max(c["nivel"] for c in caras.values()),
            "conteo_por_nivel": {str(k): conteo_niveles[k] for k in sorted(conteo_niveles)},
            "conteo_por_salto": {str(k): conteo_saltos[k] for k in sorted(conteo_saltos)},
            "hiladas_de_las_bandas": [bandas[k]["hilada"] for k in sorted(bandas)],
            "bandas_ordenadas_como_las_hiladas": all(
                bandas[a]["hilada"] < bandas[b]["hilada"]
                for a, b in zip(sorted(bandas), sorted(bandas)[1:])
            ),
            "altura_de_la_banda_mas_alta_m": bandas[max(bandas)]["altura_m"],
            "desfase_cima_frente_a_seccion_m": (
                bandas[max(bandas)]["altura_m"] - ALTURA_TOTAL_M
            ),
            "iqr_maximo_de_banda_hiladas": max(b["iqr_hiladas"] for b in bandas.values()),
        },
        "caras": [caras[k] for k in sorted(caras)],
        "vecindades": vecindades,
    }
    args.salida.write_text(
        json.dumps(documento, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(
        f"{len(caras)} caras y {len(vecindades)} vecindades; "
        f"{documento['controles']['caras_estables_7_8']} caras estables; "
        f"escrito {args.salida}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
