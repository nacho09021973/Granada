#!/usr/bin/env python3
"""Convierte la red de medinas en caras, las clasifica y deja el signo sin firmar.

Entrada: ``datos/red_medinas.json`` (version 2). Salida: ``datos/caras_red.json``.

El script no decide niveles. Produce tres cosas: las caras que las medinas
delimitan, la figura plana de aquellas que ajustan a una plantilla documentada
dentro de la tolerancia que impone la resolucion del dibujo, y la lista de
vecindades entre caras con ``salto: null`` en todas. Ese ``null`` es el dato:
la figura 128 no trae flechas ni cotas, asi que ningun paso esta firmado.

Sin dependencias fuera de la biblioteca estandar y de ``granada``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from granada.caras import (  # noqa: E402
    CONTORNO,
    FiguraPlana,
    PLANTILLAS,
    Plantilla,
    ajuste_a_plantilla,
    clasificar,
    cruces_de_aristas,
    extraer_caras,
    tolerancia_por_resolucion,
)

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "datos" / "red_medinas.json"
SALIDA = RAIZ / "datos" / "caras_red.json"

# Tolerancia de simplificacion con la que se extrajo la red, en pixeles de la
# figura 128. No es un parametro libre de esta fase: se hereda de la anterior.
RESOLUCION_PX = 2.0
TOLERANCIA_LADO = 0.12
BARRIDO_PX = (0.5, 1.0, 1.5, 2.0, 3.0)

# Una clasificacion solo se da por confirmada si la cara es bastante mayor que
# la resolucion del dibujo y si su plantilla ajusta claramente mejor que la
# mejor plantilla de control. Lo demas se etiqueta pero se marca al limite.
LADO_MINIMO_FIRME_PX = 5 * RESOLUCION_PX
MARGEN_FIRME = 2.0

# Control: figuras que no pertenecen al sistema occidental documentado. Dos de
# ellas comparten angulos o lados con las plantillas buenas, de modo que el
# control no se pasa por el mero numero de vertices.
PLANTILLAS_AJENAS = {
    "triangulo_equilatero": Plantilla((60.0,) * 3, (1.0,) * 3),
    "triangulo_isosceles_100": Plantilla(
        (100.0, 40.0, 40.0), (1.0, 2 * math.sin(math.radians(50)), 1.0)
    ),
    "rombo_de_60": Plantilla((60.0, 120.0, 60.0, 120.0), (1.0,) * 4),
    "rectangulo_1_a_1.4": Plantilla((90.0,) * 4, (1.0, 1.4, 1.0, 1.4)),
    "pentagono_regular": Plantilla((108.0,) * 5, (1.0,) * 5),
    "hexagono_regular": Plantilla((120.0,) * 6, (1.0,) * 6),
    "octogono_de_lados_alternos": Plantilla((135.0,) * 8, (1.0, 1.4) * 4),
}


def clasificar_todas(caras, resolucion_m, tolerancia_lado=TOLERANCIA_LADO):
    salida = []
    for cara in caras:
        tolerancia = tolerancia_por_resolucion(cara, resolucion_m)
        figura, desviacion_angular, desviacion_lado = clasificar(
            cara, tolerancia, tolerancia_lado
        )
        salida.append((figura, tolerancia, desviacion_angular, desviacion_lado))
    return salida


def mejor_ajena(cara, tolerancia, tolerancia_lado=TOLERANCIA_LADO):
    """Plantilla ajena mas proxima y si habria entrado con la misma tolerancia."""

    mejor = (None, math.inf, math.inf)
    for nombre, plantilla in PLANTILLAS_AJENAS.items():
        desviacion_angular, desviacion_lado = ajuste_a_plantilla(cara, plantilla)
        if not math.isfinite(desviacion_angular):
            continue
        peor = max(desviacion_angular / tolerancia, desviacion_lado / tolerancia_lado)
        if peor < max(mejor[1] / tolerancia, mejor[2] / tolerancia_lado):
            mejor = (nombre, desviacion_angular, desviacion_lado)
    entra = mejor[1] <= tolerancia and mejor[2] <= tolerancia_lado
    return mejor, entra


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=ENTRADA)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    argumentos = parser.parse_args()

    crudo = argumentos.entrada.read_bytes()
    red = json.loads(crudo)
    if red["version"] != 2:
        raise SystemExit(f"se esperaba red_medinas version 2, hay {red['version']}")

    nodos = [tuple(p) for p in red["nodos"]]
    aristas = [(a, b) for a, b, _, _ in red["aristas"]]
    px_por_metro = statistics.fmean(red["registro"]["px_por_metro"])
    resolucion_m = RESOLUCION_PX / px_por_metro

    cruces = cruces_de_aristas(nodos, aristas)
    if cruces:
        raise SystemExit(f"la red no es un dibujo plano: {len(cruces)} cruces")

    resultado = extraer_caras(nodos, aristas)

    # Orden estable e independiente del recorrido: por el menor nudo de la cara.
    orden = sorted(
        range(len(resultado.caras)), key=lambda i: sorted(resultado.caras[i].vertices)
    )
    nuevo_indice = {viejo: nuevo for nuevo, viejo in enumerate(orden)}
    caras = [resultado.caras[i] for i in orden]
    nombre = [f"c{i:03d}" for i in range(len(caras))]

    clasificacion = clasificar_todas(caras, resolucion_m)
    conteo = Counter(figura.value for figura, _, _, _ in clasificacion)

    filas = []
    ajenas_que_entran = 0
    for indice, (cara, (figura, tolerancia, dev_ang, dev_lado)) in enumerate(
        zip(caras, clasificacion)
    ):
        centro_x = statistics.fmean(nodos[v][0] for v in cara.vertices)
        centro_y = statistics.fmean(nodos[v][1] for v in cara.vertices)
        (nombre_ajena, ajena_ang, ajena_lado), entra = mejor_ajena(cara, tolerancia)
        ajenas_que_entran += int(entra)
        propia = max(dev_ang / tolerancia, dev_lado / TOLERANCIA_LADO)
        ajena = max(ajena_ang / tolerancia, ajena_lado / TOLERANCIA_LADO)
        margen = math.inf if propia == 0 else ajena / propia
        filas.append(
            {
                "id": nombre[indice],
                "vertices": list(cara.vertices),
                "lados": cara.numero_de_lados,
                "area_m2": cara.area,
                "perimetro_m": cara.perimetro,
                "lado_minimo_m": cara.lado_minimo,
                "lado_minimo_px": cara.lado_minimo * px_por_metro,
                "convexa": cara.es_convexa,
                "centroide_m": [centro_x, centro_y],
                "radio_m": math.hypot(centro_x, centro_y),
                "azimut_grados": math.degrees(math.atan2(centro_y, centro_x)) % 360,
                "figura": None
                if figura is FiguraPlana.SIN_CLASIFICAR
                else figura.value,
                "tolerancia_grados": tolerancia,
                "desviacion_angular_grados": dev_ang,
                "desviacion_lado_relativa": dev_lado,
                "plantilla_ajena_mas_proxima": nombre_ajena,
                "desviacion_ajena_angular_grados": ajena_ang,
                "desviacion_ajena_lado_relativa": ajena_lado,
                # Cuantas veces peor ajusta la plantilla ajena mas proxima.
                "margen_frente_a_ajena": None if math.isinf(margen) else margen,
                "firmeza": None
                if figura is FiguraPlana.SIN_CLASIFICAR
                else (
                    "confirmada"
                    if (
                        cara.lado_minimo * px_por_metro >= LADO_MINIMO_FIRME_PX
                        and margen >= MARGEN_FIRME
                    )
                    else "al_limite_de_resolucion"
                ),
            }
        )

    vecindades = []
    for vecindad in resultado.vecindades:
        cara_a = nombre[nuevo_indice[vecindad.cara_a]]
        if vecindad.es_de_borde:
            cara_b = "contorno"
        else:
            cara_b = nombre[nuevo_indice[vecindad.cara_b]]
        primero, segundo = sorted((cara_a, cara_b))
        vecindades.append(
            {
                "a": primero,
                "b": segundo,
                "aristas": [list(par) for par in vecindad.aristas],
                # Sin flechas ni cotas en la figura 128 no hay signo que poner.
                "salto": None,
                "evidencia": None,
            }
        )
    vecindades.sort(key=lambda fila: (fila["a"], fila["b"]))

    barrido = []
    for resolucion_px in BARRIDO_PX:
        conteo_barrido = Counter(
            figura.value
            for figura, _, _, _ in clasificar_todas(caras, resolucion_px / px_por_metro)
        )
        barrido.append(
            {
                "resolucion_px": resolucion_px,
                **{
                    clave: conteo_barrido.get(clave, 0)
                    for clave in (
                        "medio_cuadrado",
                        "media_jaira",
                        "jaira",
                        "cuadrado",
                        "octogono",
                        "sin_clasificar",
                    )
                },
            }
        )

    por_figura = {}
    for clave in sorted(conteo):
        if clave == "sin_clasificar":
            continue
        grupo = [fila for fila in filas if fila["figura"] == clave]
        por_figura[clave] = {
            "n": len(grupo),
            "lado_minimo_px": min(fila["lado_minimo_px"] for fila in grupo),
            "tolerancia_maxima_grados": max(
                fila["tolerancia_grados"] for fila in grupo
            ),
            "ajuste_angular_maximo_grados": max(
                fila["desviacion_angular_grados"] for fila in grupo
            ),
            "ajuste_lado_maximo_relativo": max(
                fila["desviacion_lado_relativa"] for fila in grupo
            ),
            "ajena_angular_minimo_grados": min(
                fila["desviacion_ajena_angular_grados"] for fila in grupo
            ),
            "ajena_lado_minimo_relativo": min(
                fila["desviacion_ajena_lado_relativa"] for fila in grupo
            ),
            "margen_minimo_frente_a_ajena": min(
                (
                    fila["margen_frente_a_ajena"]
                    for fila in grupo
                    if fila["margen_frente_a_ajena"] is not None
                ),
                default=None,
            ),
            "azimut_grados": sorted(fila["azimut_grados"] for fila in grupo),
        }

    sin_clasificar = [fila for fila in filas if fila["figura"] is None]
    documento = {
        "version": 1,
        "fuente": {
            "derivado_de": "datos/red_medinas.json",
            "version_red": red["version"],
            "sha256_red": hashlib.sha256(crudo).hexdigest(),
            "referencia": red["fuente"]["referencia"],
            "handle": red["fuente"]["handle"],
        },
        "metodo": {
            "extraccion": "rotacion de semiaristas sobre el dibujo plano",
            "resolucion_px": RESOLUCION_PX,
            "resolucion_m": resolucion_m,
            "tolerancia_angular": "2 * resolucion / lado mas corto de cada cara",
            "tolerancia_lado_relativa": TOLERANCIA_LADO,
            "plantillas": sorted(figura.value for figura in PLANTILLAS),
            "plantillas_de_control": sorted(PLANTILLAS_AJENAS),
            "lado_minimo_firme_px": LADO_MINIMO_FIRME_PX,
            "margen_firme": MARGEN_FIRME,
            "signo_de_nivel": "sin firmar: la figura 128 no trae flechas ni cotas",
        },
        "controles": {
            "nudos": len(nodos),
            "aristas": len(aristas),
            "caras_interiores": len(caras),
            "euler_v_menos_e_mas_f": len(nodos) - len(aristas) + len(caras) + 1,
            "cruces_de_aristas": len(cruces),
            "area_caras_m2": resultado.area_total,
            "area_contorno_m2": resultado.area_contorno,
            "clasificadas": len(caras) - conteo.get("sin_clasificar", 0),
            "sin_clasificar": conteo.get("sin_clasificar", 0),
            "sin_clasificar_no_convexas": sum(
                1 for fila in sin_clasificar if not fila["convexa"]
            ),
            "conteo_por_figura": {
                clave: conteo.get(clave, 0)
                for clave in sorted(figura.value for figura in PLANTILLAS)
            },
            "clasificadas_confirmadas": sum(
                1 for fila in filas if fila["firmeza"] == "confirmada"
            ),
            "clasificadas_al_limite": sum(
                1 for fila in filas if fila["firmeza"] == "al_limite_de_resolucion"
            ),
            "caras_que_admiten_plantilla_ajena": ajenas_que_entran,
            "barrido_de_resolucion": barrido,
            "por_figura": por_figura,
            "vecindades": len(vecindades),
            "vecindades_de_borde": sum(1 for v in vecindades if v["b"] == "contorno"),
            "vecindades_con_salto_firmado": sum(
                1 for v in vecindades if v["salto"] is not None
            ),
            "aristas_puente": len(resultado.aristas_puente),
        },
        "estado": "BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS",
        "caras": filas,
        "contorno": {
            "vertices": list(resultado.contorno),
            "area_m2": resultado.area_contorno,
            "aristas_puente": [list(par) for par in resultado.aristas_puente],
        },
        "vecindades": vecindades,
    }

    argumentos.salida.write_text(
        json.dumps(documento, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    controles = documento["controles"]
    print(
        f"caras: {controles['caras_interiores']}  "
        f"Euler: {controles['euler_v_menos_e_mas_f']}"
    )
    print(
        f"clasificadas: {controles['clasificadas']}  {controles['conteo_por_figura']}"
        f"  (confirmadas {controles['clasificadas_confirmadas']}, "
        f"al limite {controles['clasificadas_al_limite']})"
    )
    print(f"control de plantillas ajenas admitidas: {ajenas_que_entran}")
    print(
        f"vecindades: {controles['vecindades']} "
        f"({controles['vecindades_de_borde']} contra el contorno), "
        f"firmadas: {controles['vecindades_con_salto_firmado']}"
    )
    print(f"escrito {argumentos.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
