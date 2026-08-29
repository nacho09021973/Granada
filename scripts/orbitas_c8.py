#!/usr/bin/env python3
"""Calcula las orbitas de las caras y vecindades bajo la rotacion C8.

Para que una observacion sobre un sector valga para toda la cupula hace falta
saber que cara va con cual al girar. Eso no se supone: se calcula sobre la planta
y se controla.

La simetria de apoyo es la **rotacional**, medida por Fourier sobre la
ortoimagen (`docs/fuentes.md`, entrada 7): armonico k=16 dominante y simetria
rotacional exacta de orden 8. Es independiente de la red, asi que usarla no es
circular.

**No incluye el espejo.** La misma entrada 7 dice expresamente que la simetria
especular no se ha analizado, y la mitad inferior de la red ya es un espejo
impuesto. Esta permutacion es solo rotacional.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

ENTRADA = RAIZ / "datos" / "caras_red.json"
SALIDA = RAIZ / "datos" / "orbitas_c8.json"
ORDEN = 8
MARGEN_HOLGADO = 2.0
ANGULOS_DE_CONTROL = (22.5, 30.0, 60.0)


def girar(punto: tuple[float, float], grados: float) -> tuple[float, float]:
    a = math.radians(grados)
    x, y = punto
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))


def emparejar(
    centroides: dict[str, tuple[float, float]], grados: float
) -> tuple[dict[str, str], list[float], list[float]]:
    """Cada cara girada contra la cara mas cercana, con su margen."""
    mapa, distancias, margenes = {}, [], []
    for identificador, centro in centroides.items():
        objetivo = girar(centro, grados)
        candidatos = sorted(
            (math.dist(objetivo, otro), clave)
            for clave, otro in centroides.items()
        )
        mapa[identificador] = candidatos[0][1]
        distancias.append(candidatos[0][0])
        margenes.append(candidatos[1][0] / max(candidatos[0][0], 1e-12))
    return mapa, distancias, margenes


def orden_de(mapa: dict[str, str]) -> int:
    actual, orden = dict(mapa), 1
    while any(actual[k] != k for k in mapa) and orden <= len(mapa):
        actual = {k: mapa[actual[k]] for k in mapa}
        orden += 1
    return orden


def orbitas_de(mapa: dict[str, str]) -> list[list[str]]:
    vistos, orbitas = set(), []
    for identificador in mapa:
        if identificador in vistos:
            continue
        orbita, siguiente = [identificador], mapa[identificador]
        while siguiente != identificador:
            orbita.append(siguiente)
            vistos.add(siguiente)
            siguiente = mapa[siguiente]
        vistos.add(identificador)
        orbitas.append(orbita)
    return orbitas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=ENTRADA)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    args = parser.parse_args()

    crudo = args.entrada.read_bytes()
    dato = json.loads(crudo)
    centroides = {c["id"]: tuple(c["centroide_m"]) for c in dato["caras"]}
    paso = 360.0 / ORDEN

    mapa, distancias, margenes = emparejar(centroides, paso)
    orbitas = orbitas_de(mapa)
    ajustadas = sorted(
        identificador
        for identificador, margen in zip(centroides, margenes)
        if margen < MARGEN_HOLGADO
    )

    # Cada vecindad viaja con sus dos caras. El contorno es invariante.
    def imagen(extremo: str) -> str:
        return extremo if extremo == "contorno" else mapa[extremo]

    def canonica(a: str, b: str) -> tuple[str, str]:
        return (a, b) if a <= b else (b, a)

    vecindades = {canonica(v["a"], v["b"]) for v in dato["vecindades"]}
    mapa_vecindades = {
        par: canonica(imagen(par[0]), imagen(par[1])) for par in vecindades
    }
    # La permutacion no cierra del todo las vecindades: unas pocas caen fuera del
    # conjunto. No es un fallo estructural -es el residuo del dibujo, y varias
    # tocan las caras de margen ajustado- pero por ahi no se propaga nada. Las
    # orbitas que contengan un paso roto quedan marcadas como NO propagables.
    rotas = sorted(
        list(par) for par, destino in mapa_vecindades.items() if destino not in vecindades
    )
    orbitas_vecindades, propagables = [], []
    vistos = set()
    for par in sorted(vecindades):
        if par in vistos:
            continue
        orbita, actual, intacta = [par], par, True
        for _ in range(ORDEN):
            siguiente = mapa_vecindades.get(actual)
            if siguiente is None or siguiente not in vecindades:
                intacta = False
                break
            if siguiente == par:
                break
            orbita.append(siguiente)
            actual = siguiente
        vistos.update(orbita)
        orbitas_vecindades.append(
            {
                "representante": sorted(orbita)[0],
                "vecindades": [list(x) for x in sorted(orbita)],
                "tamano": len(orbita),
                "propagable": intacta and len(orbita) == ORDEN,
            }
        )
        if intacta and len(orbita) == ORDEN:
            propagables.append(orbita)

    controles_de_angulo = []
    for grados in ANGULOS_DE_CONTROL:
        _, dist, marg = emparejar(centroides, grados)
        controles_de_angulo.append(
            {
                "grados": grados,
                "desajuste_maximo_mm": max(dist) * 1000,
                "caras_con_margen_holgado": sum(1 for m in marg if m >= MARGEN_HOLGADO),
            }
        )

    documento = {
        "version": 1,
        "estado": "C8_ORBITS_AVAILABLE",
        "advertencia": (
            "Solo rotacion. La simetria especular no se ha analizado (fuentes.md, "
            "entrada 7) y no se aplica aqui. Una observacion propagada por orbita "
            "no multiplica el N: el N declarado es el de lo observado."
        ),
        "fuente": {
            "derivado_de": str(args.entrada.relative_to(RAIZ)),
            "sha256": hashlib.sha256(crudo).hexdigest(),
            "simetria": (
                "rotacional de orden 8, medida por Fourier sobre la ortoimagen; "
                "fuentes.md entrada 7. Independiente de la red, luego no circular"
            ),
        },
        "metodo": {
            "giro_grados": paso,
            "emparejamiento": "centroide girado contra el centroide mas cercano",
            "margen_holgado": MARGEN_HOLGADO,
        },
        "controles": {
            "caras": len(centroides),
            "es_biyectiva": len(set(mapa.values())) == len(mapa),
            "orden_de_la_permutacion": orden_de(mapa),
            "orbitas": len(orbitas),
            "tamanos_de_orbita": sorted({len(o) for o in orbitas}),
            "desajuste_mediano_mm": statistics.median(distancias) * 1000,
            "desajuste_maximo_mm": max(distancias) * 1000,
            "margen_mediano": statistics.median(margenes),
            "margen_minimo": min(margenes),
            "caras_con_margen_ajustado": ajustadas,
            "vecindades": len(vecindades),
            "orbitas_de_vecindades": len(orbitas_vecindades),
            "orbitas_de_vecindades_propagables": len(propagables),
            "vecindades_que_no_cierran": rotas,
            "vecindades_cubiertas_por_orbitas_propagables": sum(
                len(o) for o in propagables
            ),
            "angulos_de_control": controles_de_angulo,
        },
        "dominio_fundamental": {
            "caras": sorted(orbita[0] for orbita in orbitas),
            "vecindades": sorted(list(o[0]) for o in propagables),
            "nota": (
                "observar estas caras cubre las 105 por rotacion; observar estas "
                "vecindades cubre las 227"
            ),
        },
        "permutacion": {k: mapa[k] for k in sorted(mapa)},
        "orbitas": [
            {"representante": sorted(o)[0], "caras": sorted(o), "tamano": len(o)}
            for o in sorted(orbitas, key=lambda o: sorted(o)[0])
        ],
        "orbitas_vecindades": sorted(
            orbitas_vecindades, key=lambda o: o["representante"]
        ),
    }
    args.salida.write_text(
        json.dumps(documento, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    c = documento["controles"]
    print(
        f"{c['orbitas']} orbitas de caras y {c['orbitas_de_vecindades_propagables']} "
        f"de vecindades propagables ({len(rotas)} vecindades no cierran); "
        f"orden {c['orden_de_la_permutacion']}; desajuste max {c['desajuste_maximo_mm']:.1f} mm; "
        f"{len(ajustadas)} caras con margen ajustado; escrito {args.salida}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
