#!/usr/bin/env python3
"""Mide el tamano real del problema de niveles bajo la simetria de la cupula.

Los 211 saltos entre caras no son grados de libertad: quedan determinados por
los 105 niveles de las caras, y como solo importa la altura relativa mientras
no haya una medida absoluta, un nivel es libre. La cuenta cuadra con los ciclos
ya medidos: 211 vecindades - 107 ciclos independientes = 104 = 105 - 1.

Si ademas la nivelacion respeta la simetria D8 medida en la cupula --hipotesis,
no dato-- las incognitas bajan al numero de **orbitas de caras** bajo ese grupo.
Este script las cuenta, y cuenta cuantas de ellas atraviesa una seccion por
cada una de las dos clases de eje de espejo del grupo.

Sin dependencias fuera de la biblioteca estandar y de ``granada``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections.abc import Sequence
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from granada.caras import (  # noqa: E402
    Cara,
    centroide,
    corta_al_eje,
    margen_al_eje,
    orbitas_por_simetria,
)

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA_CARAS = RAIZ / "datos" / "caras_red.json"
ENTRADA_RED = RAIZ / "datos" / "red_medinas.json"
SALIDA = RAIZ / "datos" / "orbitas_caras.json"

ORDEN = 8  # C8 medida; con espejo, grupo diedrico de orden 16
# Las dos clases de conjugacion de reflexiones de D8. Dentro de una clase la
# respuesta es la misma, asi que basta un representante de cada una.
CLASES_DE_EJE = {"A": 0.0, "B": 22.5}
# Los cuatro ejes de cada clase. El recuento tiene que salir igual para los
# cuatro; si no, el representante estaria diciendo algo del eje y no de la
# clase. Ademas hace falta saberlo porque cual de ellos es el norte-sur del
# edificio no se lee de la boveda: si es D8, nada de ella lo distingue.
EJES_DE_LA_CLASE = {clave: [angulo + 45.0 * k for k in range(4)]
                    for clave, angulo in CLASES_DE_EJE.items()}

# Cada copia se digitaliza por separado, asi que emparejarlas exige tolerancia.
# No se elige a ojo: el criterio es que todo tamano de orbita divida al orden
# del grupo, cosa que un emparejamiento roto incumple. Hay meseta amplia.
TOLERANCIA_DISTANCIA_M = 0.10
TOLERANCIA_AREA = 0.30
BARRIDO_AREA = (0.15, 0.20, 0.25, 0.30, 0.40, 0.50)
BARRIDO_DISTANCIA_M = (0.06, 0.08, 0.10, 0.12, 0.15)

# Un mismo cruce del eje aparece dos veces si pasa cerca de un nudo.
AGRUPADO_DE_FRONTERAS_M = 0.03


def fronteras_en_el_eje(
    red: dict, centro: Sequence[float], angulo_grados: float
) -> list[float]:
    """Radios a los que una medina cruza la recta del eje, agrupados.

    Es el perfil de la planta a lo largo de la seccion: la lista de radios en
    los que, recorriendo el eje desde el centro, se pasa de una cara a otra.
    Se agrupan los cruces separados por menos de la tolerancia porque un mismo
    corte aparece dos veces cuando el eje pasa por un nudo.
    """

    puntos = red["nodos"]
    radianes = math.radians(angulo_grados)
    coseno, seno = math.cos(radianes), math.sin(radianes)
    cruces = []
    for arista in red["aristas"]:
        x0 = puntos[arista[0]][0] - centro[0]
        y0 = puntos[arista[0]][1] - centro[1]
        x1 = puntos[arista[1]][0] - centro[0]
        y1 = puntos[arista[1]][1] - centro[1]
        u0 = -x0 * seno + y0 * coseno
        u1 = -x1 * seno + y1 * coseno
        if (u0 <= 0 < u1) or (u1 <= 0 < u0):
            t = -u0 / (u1 - u0)
            cruces.append(
                abs((x0 + t * (x1 - x0)) * coseno + (y0 + t * (y1 - y0)) * seno)
            )
    cruces.sort()
    grupos: list[list[float]] = []
    for radio in cruces:
        if grupos and radio - grupos[-1][-1] < AGRUPADO_DE_FRONTERAS_M:
            grupos[-1].append(radio)
        else:
            grupos.append([radio])
    return [math.fsum(g) / len(g) for g in grupos]


def asimetria_izquierda_derecha(
    caras: Sequence[Cara],
    puntos: Sequence[Sequence[float]],
    centro: Sequence[float],
    orbitas: Sequence[Sequence[int]],
) -> dict:
    """Es un lado de la cupula mayor que el otro, en el dibujo?

    El espejo impuesto de la red es horizontal, asi que una asimetria
    izquierda-derecha no la habria metido la construccion del dato. Pero hay un
    confundidor de un solo grado de libertad que la imita entera: **el centro
    mal puesto**. Por eso se mide dos veces, con el centroide del octogono y
    con el centro que minimiza la dispersion radial dentro de cada orbita.
    """

    centros = [centroide(cara, puntos) for cara in caras]

    def dispersion(punto: tuple[float, float]) -> float:
        restos = []
        for orbita in orbitas:
            if len(orbita) < 2:
                continue
            radios = [math.dist(centros[i], punto) for i in orbita]
            media = math.fsum(radios) / len(radios)
            restos.extend((r - media) ** 2 for r in radios)
        return math.sqrt(math.fsum(restos) / len(restos))

    def reparto(punto: tuple[float, float]) -> tuple[int, int, float]:
        diferencias = []
        for orbita in orbitas:
            if len(orbita) < 2:
                continue
            izquierda = [
                math.dist(centros[i], punto)
                for i in orbita
                if centros[i][0] < punto[0]
            ]
            derecha = [
                math.dist(centros[i], punto)
                for i in orbita
                if centros[i][0] > punto[0]
            ]
            if not izquierda or not derecha:
                continue
            media_i = math.fsum(izquierda) / len(izquierda)
            media_d = math.fsum(derecha) / len(derecha)
            diferencias.append((media_d - media_i) / media_i)
        diferencias.sort()
        mediana = diferencias[len(diferencias) // 2]
        return sum(1 for v in diferencias if v > 0), len(diferencias), mediana

    mejor = (dispersion(tuple(centro)), centro[0], centro[1])
    paso = 0.02
    for _ in range(60):
        for x in (mejor[1] - paso, mejor[1], mejor[1] + paso):
            for y in (mejor[2] - paso, mejor[2], mejor[2] + paso):
                valor = dispersion((x, y))
                if valor < mejor[0]:
                    mejor = (valor, x, y)
        paso *= 0.7
    ajustado = (mejor[1], mejor[2])

    con_octogono = reparto(tuple(centro))
    con_ajustado = reparto(ajustado)
    return {
        "confundidor": (
            "un centro desplazado imita una asimetria izquierda-derecha "
            "completa; diez orbitas con el mismo signo son un grado de "
            "libertad, no diez observaciones"
        ),
        "centro_ajustado_m": list(ajustado),
        "desplazamiento_del_centro_m": math.dist(ajustado, tuple(centro)),
        "dispersion_radial_rms_m": {
            "centro_del_octogono": dispersion(tuple(centro)),
            "centro_ajustado": mejor[0],
        },
        "orbitas_con_derecha_mayor": {
            "centro_del_octogono": list(con_octogono[:2]),
            "centro_ajustado": list(con_ajustado[:2]),
        },
        "mediana_relativa_derecha_menos_izquierda": {
            "centro_del_octogono": con_octogono[2],
            "centro_ajustado": con_ajustado[2],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    argumentos = parser.parse_args()

    crudo = ENTRADA_CARAS.read_bytes()
    dato = json.loads(crudo)
    red = json.loads(ENTRADA_RED.read_bytes())
    puntos = red["nodos"]
    # Un pixel del dibujo, en metros. Es el suelo de resolucion: por debajo de
    # el, que una cara asome al otro lado del eje no es un dato.
    resolucion = 1.0 / (sum(red["registro"]["px_por_metro"]) / 2)

    caras = [
        Cara(
            vertices=tuple(fila["vertices"]),
            angulos=(1.0,) * fila["lados"],  # no intervienen aqui
            lados=(1.0,) * fila["lados"],
            area=fila["area_m2"],
        )
        for fila in dato["caras"]
    ]
    nombres = [fila["id"] for fila in dato["caras"]]

    # El centro del grupo es el punto fijo: el centroide de area del octogono
    # central. No se toma el (0, 0) del registro, que es una convencion.
    central = next(
        i for i, fila in enumerate(dato["caras"]) if fila["figura"] == "octogono"
    )
    centro = centroide(caras[central], puntos)

    orbitas = orbitas_por_simetria(
        caras,
        puntos,
        centro,
        ORDEN,
        tolerancia=TOLERANCIA_DISTANCIA_M,
        tolerancia_area=TOLERANCIA_AREA,
    )
    tamanos = sorted((len(o) for o in orbitas), reverse=True)
    rotas = [len(o) for o in orbitas if (2 * ORDEN) % len(o) != 0]

    filas = []
    for indice, orbita in enumerate(orbitas):
        centros = [centroide(caras[i], puntos) for i in orbita]
        radios = [math.hypot(x - centro[0], y - centro[1]) for x, y in centros]
        azimuts = sorted(
            math.degrees(math.atan2(y - centro[1], x - centro[0])) % 360
            for x, y in centros
        )
        cortes = {
            clave: [
                nombres[i]
                for i in orbita
                if corta_al_eje(caras[i], puntos, centro, angulo)
            ]
            for clave, angulo in CLASES_DE_EJE.items()
        }
        resolubles = {
            clave: [
                nombres[i]
                for i in orbita
                if corta_al_eje(caras[i], puntos, centro, angulo, resolucion)
            ]
            for clave, angulo in CLASES_DE_EJE.items()
        }
        margenes = {
            clave: {
                nombres[i]: margen_al_eje(caras[i], puntos, centro, angulo)
                for i in orbita
                if corta_al_eje(caras[i], puntos, centro, angulo)
            }
            for clave, angulo in CLASES_DE_EJE.items()
        }
        filas.append(
            {
                "orbita": indice,
                "tamano": len(orbita),
                "caras": [nombres[i] for i in orbita],
                "area_media_m2": math.fsum(caras[i].area for i in orbita) / len(orbita),
                "radio_medio_m": math.fsum(radios) / len(radios),
                "azimuts_grados": azimuts,
                "figuras": sorted({dato["caras"][i]["figura"] for i in orbita}, key=str),
                "cortada_por_eje": {k: bool(v) for k, v in cortes.items()},
                "cortada_de_forma_resoluble": {
                    k: bool(v) for k, v in resolubles.items()
                },
                "caras_sobre_el_eje": cortes,
                "margen_al_eje_m": margenes,
            }
        )

    cobertura = {
        clave: {
            "orbitas_cortadas": sum(1 for f in filas if f["cortada_por_eje"][clave]),
            "caras_cortadas": sum(len(f["caras_sobre_el_eje"][clave]) for f in filas),
            "orbitas_sin_cortar": [
                f["orbita"] for f in filas if not f["cortada_por_eje"][clave]
            ],
            "orbitas_cortadas_resolubles": sum(
                1 for f in filas if f["cortada_de_forma_resoluble"][clave]
            ),
            "caras_determinadas_resolubles": sum(
                f["tamano"] for f in filas if f["cortada_de_forma_resoluble"][clave]
            ),
            "orbitas_sin_cortar_resolubles": [
                f["orbita"]
                for f in filas
                if not f["cortada_de_forma_resoluble"][clave]
            ],
        }
        for clave in CLASES_DE_EJE
    }

    fronteras = {
        clave: fronteras_en_el_eje(red, centro, angulo)
        for clave, angulo in CLASES_DE_EJE.items()
    }

    invariancia = {
        clave: [
            {
                "eje_grados": angulo,
                "caras_tocadas": sum(
                    1
                    for c in caras
                    if corta_al_eje(c, puntos, centro, angulo)
                ),
                "orbitas_resolubles": sorted(
                    indice
                    for indice, orbita in enumerate(orbitas)
                    if any(
                        corta_al_eje(caras[i], puntos, centro, angulo, resolucion)
                        for i in orbita
                    )
                ),
                "fronteras_m": fronteras_en_el_eje(red, centro, angulo),
            }
            for angulo in angulos
        ]
        for clave, angulos in EJES_DE_LA_CLASE.items()
    }

    asimetria = asimetria_izquierda_derecha(caras, puntos, centro, orbitas)

    barrido = []
    for area in BARRIDO_AREA:
        for distancia in BARRIDO_DISTANCIA_M:
            tamanos_barrido = sorted(
                (
                    len(o)
                    for o in orbitas_por_simetria(
                        caras, puntos, centro, ORDEN,
                        tolerancia=distancia, tolerancia_area=area,
                    )
                ),
                reverse=True,
            )
            barrido.append(
                {
                    "tolerancia_area": area,
                    "tolerancia_distancia_m": distancia,
                    "orbitas": len(tamanos_barrido),
                    "todos_dividen_al_grupo": all(
                        (2 * ORDEN) % n == 0 for n in tamanos_barrido
                    ),
                }
            )

    vecindades = sum(
        1 for v in dato["vecindades"] if "contorno" not in (v["a"], v["b"])
    )
    documento = {
        "version": 1,
        "fuente": {
            "derivado_de": "datos/caras_red.json",
            "sha256_caras": hashlib.sha256(crudo).hexdigest(),
        },
        "metodo": {
            "grupo": f"diedrico de orden {2 * ORDEN} (C{ORDEN} medida mas espejo)",
            "centro": "centroide de area del octogono central",
            "centro_m": list(centro),
            "centroide": "de area, no media de vertices",
            "clases_de_eje_grados": CLASES_DE_EJE,
            "tolerancia_distancia_m": TOLERANCIA_DISTANCIA_M,
            "tolerancia_area": TOLERANCIA_AREA,
            "resolucion_m": resolucion,
            "corte_resoluble": (
                "la cara tiene que sobresalir mas de un pixel del dibujo a los "
                "dos lados del eje; por debajo de eso el cruce es ruido de la "
                "digitalizacion, no un corte"
            ),
            "hipotesis": (
                "que la nivelacion respete la simetria de la cupula. Es una "
                "hipotesis falsable contra los mismos 107 ciclos, no un dato."
            ),
        },
        "controles": {
            "caras": len(caras),
            "vecindades_interiores": vecindades,
            "ciclos_independientes": vecindades - len(caras) + 1,
            "niveles_independientes_sin_simetria": len(caras) - 1,
            "orbitas": len(orbitas),
            "tamanos_de_orbita": tamanos,
            "suma_de_tamanos": sum(tamanos),
            "tamanos_que_no_dividen_al_grupo": rotas,
            "cobertura_por_clase_de_eje": cobertura,
            "fronteras_en_el_eje_m": fronteras,
            "invariancia_dentro_de_la_clase": invariancia,
            "asimetria_izquierda_derecha": asimetria,
            "barrido_de_tolerancias": barrido,
        },
        "estado": "BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS",
        "orbitas": filas,
    }
    argumentos.salida.write_text(
        json.dumps(documento, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"orbitas: {len(orbitas)}  tamanos {tamanos}")
    if rotas:
        print(f"  AVISO: tamanos que no dividen al grupo: {rotas}")
    for clave, datos in cobertura.items():
        print(
            f"  eje clase {clave}: corta {datos['orbitas_cortadas']} de "
            f"{len(orbitas)} orbitas y {datos['caras_cortadas']} caras; "
            f"resolubles {datos['orbitas_cortadas_resolubles']} orbitas y "
            f"{datos['caras_determinadas_resolubles']} caras"
        )
        print(f"    fronteras en el eje (m): "
              f"{[round(v, 4) for v in fronteras[clave]]}")
    print(
        f"  asimetria izq/der: {asimetria['orbitas_con_derecha_mayor']['centro_del_octogono'][0]}"
        f"/{asimetria['orbitas_con_derecha_mayor']['centro_del_octogono'][1]} orbitas con el"
        f" centro del octogono -> "
        f"{asimetria['orbitas_con_derecha_mayor']['centro_ajustado'][0]}"
        f"/{asimetria['orbitas_con_derecha_mayor']['centro_ajustado'][1]} con el centro ajustado"
        f" ({1000 * asimetria['desplazamiento_del_centro_m']:.1f} mm)"
    )
    print(f"escrito {argumentos.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
