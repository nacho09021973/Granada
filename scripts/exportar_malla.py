#!/usr/bin/env python3
"""Exporta la cupula aproximada como malla OBJ.

Levanta una celda por cara del teselado sobre las cotas de banda calibradas
contra la seccion medida (decision 0009) y con la plantilla de doble perfil
documentada (decision 0010).

No es una restitucion historica verificada. Cada cara recibe **una** celda,
pero la cara mediana de esta planta abarca 5.2 hiladas de la seccion: lo que
sale reproduce el escalonado de las seis bandas, no el de las 23 hiladas.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.malla import cupula  # noqa: E402
from granada.perfil import MAYOR, MENOR, vecindades_no_paralelas  # noqa: E402

RED = RAIZ / "datos" / "red_medinas.json"
CARAS = RAIZ / "datos" / "caras_red.json"
NIVELES = RAIZ / "datos" / "niveles_aproximados.json"
SALIDA = RAIZ / "renders" / "cupula_aproximada.obj"
INFORME = RAIZ / "datos" / "malla_cupula.json"
PLANTILLAS = {"mayor": MAYOR, "menor": MENOR}


def _centroide(poligono: list[tuple[float, float]]) -> tuple[float, float]:
    return (
        sum(x for x, _ in poligono) / len(poligono),
        sum(y for _, y in poligono) / len(poligono),
    )


def preparar(nombre_plantilla: str) -> tuple[list[dict], dict]:
    nodos = json.loads(RED.read_text(encoding="utf-8"))["nodos"]
    caras_red = json.loads(CARAS.read_text(encoding="utf-8"))["caras"]
    niveles_dato = json.loads(NIVELES.read_text(encoding="utf-8"))
    niveles = {cara["id"]: cara for cara in niveles_dato["caras"]}
    pendiente = (
        niveles_dato["metodo"]["paso_vertical_hilada_m"]
        / niveles_dato["metodo"]["paso_horizontal_hilada_m"]
    )

    # Cota de la banda inmediatamente inferior a la de cada cara; la banda
    # exterior apoya en el arranque, a cota 0.
    cotas_banda = sorted({cara["altura_m"] for cara in niveles.values()})
    cota_de_debajo = {}
    for identificador, cara in niveles.items():
        indice = cotas_banda.index(cara["altura_m"])
        cota_de_debajo[identificador] = cotas_banda[indice - 1] if indice else 0.0

    caras = []
    for cara in caras_red:
        poligono = [tuple(nodos[indice]) for indice in cara["vertices"]]
        radios = [math.hypot(x, y) for x, y in poligono]
        extension = max(radios) - min(radios)
        # El salto disponible de una cara es lo que hay hasta la banda de debajo,
        # no su propio vuelo radial. Es lo que da sentido a la plantilla: el
        # frente ocupa 7/8 de ese salto y el octavo restante es la junta. Colgar
        # el vuelo radial dejaba huecos abiertos de hasta 0.39 m entre bandas.
        cota = niveles[cara["id"]]["altura_m"]
        caras.append(
            {
                "id": cara["id"],
                "poligono": poligono,
                "cota_m": cota,
                "salto_vertical_m": cota - cota_de_debajo[cara["id"]],
                "extension_radial_m": extension,
                "vuelo_radial_m": max(0.0, max(radios) - cara["radio_m"]),
                "hilada": niveles[cara["id"]]["hilada"],
            }
        )
    contexto = {
        "pendiente_cono": pendiente,
        "vecindades": json.loads(CARAS.read_text(encoding="utf-8"))["vecindades"],
        "plantilla": nombre_plantilla,
    }
    return caras, contexto


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    parser.add_argument("--informe", type=Path, default=INFORME)
    parser.add_argument("--plantilla", choices=sorted(PLANTILLAS), default="mayor")
    parser.add_argument("--subdivision", type=int, default=4)
    parser.add_argument(
        "--escala-profundidad",
        type=float,
        default=1.0,
        help="exageracion del frente; 1.0 conserva la proporcion documentada",
    )
    args = parser.parse_args()

    caras, contexto = preparar(args.plantilla)
    plantilla = PLANTILLAS[args.plantilla]
    asignacion = {cara["id"]: plantilla for cara in caras}
    rotas = vecindades_no_paralelas(asignacion, contexto["vecindades"])

    malla = cupula(
        caras,
        asignacion,
        subdivision=args.subdivision,
        escala_profundidad=args.escala_profundidad,
    )
    cabecera = (
        "Cupula de las Dos Hermanas: reconstruccion APROXIMADA, no verificada.\n"
        f"Plantilla {plantilla.nombre}, cima {plantilla.cima}P de 8P entre niveles.\n"
        "Cotas de banda calibradas contra la seccion medida (decision 0009).\n"
        "Una celda por cara; la cara mediana abarca 5.2 hiladas de la seccion.\n"
        "Generado por scripts/exportar_malla.py"
    )
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(malla.a_obj(cabecera), encoding="utf-8")

    cotas = [v[2] for v in malla.vertices]
    # Residuo de la plataforma de cada cara frente al cono medido en su radio.
    residuos = [
        cara["cota_m"] - (3.64 - math.hypot(*_centroide(cara["poligono"]))) / 0.782
        for cara in caras
    ]
    rms = math.sqrt(sum(r * r for r in residuos) / len(residuos))
    informe = {
        "version": 1,
        "estado": "APPROXIMATE_MESH_AVAILABLE",
        "advertencia": (
            "Malla aproximada. Una celda por cara del teselado, no una adaraja "
            "por pieza; no es una restitucion historica verificada."
        ),
        "fuente": {
            "caras_red": hashlib.sha256(CARAS.read_bytes()).hexdigest(),
            "niveles_aproximados": hashlib.sha256(NIVELES.read_bytes()).hexdigest(),
        },
        "modelo": {
            "plantilla": plantilla.nombre,
            "cima_en_unidades_P": str(plantilla.cima),
            "unidades_entre_niveles": 8,
            "fraccion_util": str(plantilla.fraccion_util),
            "division": plantilla.division,
            "curva": "conica racional interpolada; eleccion de modelo, no medida",
            "salto_vertical": "extension radial de la cara por la pendiente del cono",
            "pendiente_cono": contexto["pendiente_cono"],
            "subdivision_de_lado": args.subdivision,
            "escala_profundidad": args.escala_profundidad,
        },
        "controles": {
            "caras": len(caras),
            "vertices": len(malla.vertices),
            "triangulos": len(malla.triangulos),
            "grupos": len(malla.grupos),
            "cota_minima_m": min(cotas),
            "cota_maxima_m": max(cotas),
            "vecindades_no_paralelas": len(rotas),
            "residuo_rms_frente_al_cono_m": rms,
            "residuo_maximo_frente_al_cono_m": max(abs(r) for r in residuos),
            "hiladas_que_abarca_la_cara_mediana": sorted(
                cara["extension_radial_m"] for cara in caras
            )[len(caras) // 2]
            / (
                json.loads(NIVELES.read_text(encoding="utf-8"))["metodo"][
                    "paso_horizontal_hilada_m"
                ]
            ),
        },
    }
    args.informe.write_text(
        json.dumps(informe, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(
        f"{len(caras)} celdas, {len(malla.vertices)} vertices y "
        f"{len(malla.triangulos)} triangulos; cotas {min(cotas):.3f}-{max(cotas):.3f} m; "
        f"{len(rotas)} vecindades no paralelas; "
        f"residuo rms frente al cono {rms:.3f} m; escrito {args.salida}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
