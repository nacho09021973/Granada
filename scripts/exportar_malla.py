#!/usr/bin/env python3
"""Exporta la cupula aproximada como malla OBJ.

Levanta una celda por cara del teselado sobre las cotas de banda calibradas
contra la seccion medida (decision 0009) y con la plantilla de doble perfil
documentada (decision 0010), repartida entre las bandas por la frontera de
modulo que **decide** la decision 0013.

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

from granada.asignacion import (  # noqa: E402
    CRITERIOS,
    Asignacion,
    catalogo,
    elegir,
    evaluar,
    junta_en_P,
    procedencia,
)
from granada.malla import contiene_el_eje, cupula  # noqa: E402
from granada.perfil import MAYOR, MENOR, vecindades_no_paralelas  # noqa: E402

RED = RAIZ / "datos" / "red_medinas.json"
CARAS = RAIZ / "datos" / "caras_red.json"
NIVELES = RAIZ / "datos" / "niveles_aproximados.json"
SALIDA = RAIZ / "renders" / "cupula_aproximada.obj"
INFORME = RAIZ / "datos" / "malla_cupula.json"
PLANTILLAS = {"mayor": MAYOR, "menor": MENOR}
POR_BANDA = "por-banda"


def _centroide(poligono: list[tuple[float, float]]) -> tuple[float, float]:
    return (
        sum(x for x, _ in poligono) / len(poligono),
        sum(y for _, y in poligono) / len(poligono),
    )


def preparar() -> tuple[list[dict], dict]:
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

    # El salto de cada banda en hiladas enteras: la calibracion de la decision
    # 0009 le da a cada banda una hilada de la seccion, asi que la resta es
    # exacta y la junta puede escribirse en unidades P sin pasar por metros.
    hiladas_banda = sorted({cara["hilada"] for cara in niveles.values()})
    saltos_en_hiladas = [
        hilada - (hiladas_banda[indice - 1] if indice else 0)
        for indice, hilada in enumerate(hiladas_banda)
    ]

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
                "banda": niveles[cara["id"]]["capa_desde_borde"],
            }
        )
    contexto = {
        "pendiente_cono": pendiente,
        "vecindades": json.loads(CARAS.read_text(encoding="utf-8"))["vecindades"],
        "saltos_en_hiladas": saltos_en_hiladas,
        "paso_vertical_hilada_m": niveles_dato["metodo"]["paso_vertical_hilada_m"],
    }
    return caras, contexto


def asignacion_pedida(nombre: str, caras: list[dict], contexto: dict):
    """La asignacion que pide la linea de ordenes, ya medida.

    `por-banda` es la de la decision 0013: se elige con los criterios escritos
    en `granada.asignacion`. Las uniformes se conservan porque son el modelo de
    la decision 0010 y hay que poder compararse con el.
    """
    bandas = {cara["id"]: cara["banda"] for cara in caras}
    if nombre == POR_BANDA:
        return elegir(bandas, contexto["saltos_en_hiladas"], contexto["vecindades"])
    return evaluar(
        Asignacion.uniforme(PLANTILLAS[nombre]),
        bandas,
        contexto["saltos_en_hiladas"],
        contexto["vecindades"],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    parser.add_argument("--informe", type=Path, default=INFORME)
    parser.add_argument(
        "--plantilla",
        choices=[POR_BANDA, *sorted(PLANTILLAS)],
        default=POR_BANDA,
        help=(
            "por-banda reparte las dos plantillas documentadas por la frontera "
            "decidida en la decision 0013; mayor y menor levantan la cupula "
            "entera con una sola, que es el modelo de la decision 0010"
        ),
    )
    parser.add_argument("--subdivision", type=int, default=4)
    parser.add_argument(
        "--escala-profundidad",
        type=float,
        default=1.0,
        help="exageracion del frente; 1.0 conserva la proporcion documentada",
    )
    args = parser.parse_args()

    caras, contexto = preparar()
    candidato = asignacion_pedida(args.plantilla, caras, contexto)
    asignacion = candidato.asignacion
    bandas = {cara["id"]: cara["banda"] for cara in caras}
    reparto = asignacion.por_cara(bandas)
    rotas = vecindades_no_paralelas(reparto, contexto["vecindades"])
    en_la_frontera = [
        (a, b)
        for a, b in rotas
        if min(bandas[a], bandas[b]) == asignacion.frontera - 1
        and max(bandas[a], bandas[b]) == asignacion.frontera
    ]

    malla = cupula(
        caras,
        reparto,
        subdivision=args.subdivision,
        escala_profundidad=args.escala_profundidad,
    )
    if asignacion.uniformizada:
        linea_asignacion = (
            f"Plantilla unica {asignacion.abajo.nombre}, "
            f"cima {asignacion.abajo.cima}P de 8P entre niveles."
        )
    else:
        linea_asignacion = (
            f"Plantillas {asignacion.abajo.nombre} en las bandas 0-"
            f"{asignacion.frontera - 1} y {asignacion.arriba.nombre} en las "
            f"{asignacion.frontera}-{len(contexto['saltos_en_hiladas']) - 1}. "
            "La frontera se DECIDE (decision 0013), no consta en ninguna fuente."
        )
    cabecera = (
        "Cupula de las Dos Hermanas: reconstruccion APROXIMADA, no verificada.\n"
        f"{linea_asignacion}\n"
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
    paso_vertical = contexto["paso_vertical_hilada_m"]
    unidad_P = paso_vertical / 8
    filas = []
    for cara in sorted(caras, key=lambda c: c["id"]):
        plantilla = reparto[cara["id"]]
        junta = junta_en_P(contexto["saltos_en_hiladas"][cara["banda"]], plantilla)
        # La pieza de cierre no deja junta: su borde APOYA en la banda de abajo
        # (decision 0010), y de su plantilla solo usa la curva de la superficie
        # de revolucion. Escribirle una junta seria inventarla.
        cierre = contiene_el_eje(cara["poligono"])
        filas.append(
            {
                "id": cara["id"],
                "banda": cara["banda"],
                "hilada": cara["hilada"],
                "plantilla": plantilla.nombre,
                "pieza_de_cierre": cierre,
                "junta_P": None if cierre else str(junta),
                "junta_m": None if cierre else float(junta) * unidad_P,
                "procedencia": (
                    procedencia(cara["id"], asignacion, cara["banda"])
                    + (
                        "; cupulilla apoyada en la banda de abajo, sin junta "
                        "(decision 0010)"
                        if cierre
                        else ""
                    )
                ),
            }
        )
    reparto_por_plantilla = {
        nombre: sum(1 for fila in filas if fila["plantilla"] == nombre)
        for nombre in sorted(PLANTILLAS)
    }
    ordenado = sorted(
        catalogo(bandas, contexto["saltos_en_hiladas"], contexto["vecindades"]),
        key=lambda c: (len(c.rotas), -c.cambio_de_subdivision, c.dispersion_de_junta),
    )
    informe = {
        "version": 2,
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
            "asignacion": {
                **candidato.a_dict(),
                "procedencia": (
                    "DECIDIDA, no medida: las dos plantillas estan documentadas, "
                    "el reparto entre bandas no lo dice ninguna fuente"
                ),
                "criterios": list(CRITERIOS),
                "caras_por_plantilla": reparto_por_plantilla,
                "alternativas": [otro.a_dict() for otro in ordenado],
            },
            "plantillas": {
                nombre: {
                    "cima_en_unidades_P": str(plantilla.cima),
                    "fraccion_util": str(plantilla.fraccion_util),
                    "division": plantilla.division,
                }
                for nombre, plantilla in sorted(PLANTILLAS.items())
            },
            "unidades_entre_niveles": 8,
            "curva": "conica racional interpolada; eleccion de modelo, no medida",
            "salto_vertical": "extension radial de la cara por la pendiente del cono",
            "pendiente_cono": contexto["pendiente_cono"],
            "saltos_de_banda_en_hiladas": contexto["saltos_en_hiladas"],
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
            "vecindades_no_paralelas_fuera_de_la_frontera": len(rotas)
            - len(en_la_frontera),
            "junta_minima_P": str(min(candidato.juntas_P)),
            "junta_maxima_P": str(max(candidato.juntas_P)),
            "junta_minima_m": float(min(candidato.juntas_P)) * unidad_P,
            "junta_de_la_pieza_de_cierre": (
                "no aplica: la cupulilla apoya en la banda de abajo (decision 0010)"
            ),
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
        "caras": filas,
    }
    args.informe.write_text(
        json.dumps(informe, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(
        f"{len(caras)} celdas, {len(malla.vertices)} vertices y "
        f"{len(malla.triangulos)} triangulos; "
        f"cotas {min(cotas):.3f}-{max(cotas):.3f} m; "
        f"asignacion {asignacion.etiqueta} ({reparto_por_plantilla['menor']} menor "
        f"/ {reparto_por_plantilla['mayor']} mayor); "
        f"{len(rotas)} vecindades no paralelas, {len(en_la_frontera)} en la frontera; "
        f"residuo rms frente al cono {rms:.3f} m; escrito {args.salida}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
