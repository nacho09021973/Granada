#!/usr/bin/env python3
"""Exporta cupulas comparativas exactas para el selector de trazado del visor.

La geometria se construye en Z[zeta_m]. Las coordenadas decimales solo son el
embedding numerico de esa geometria exacta para que Three.js pueda dibujarla.
Las cinco coronas y sus cotas son una composicion contemporanea declarada, no
una restitucion de un monumento.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.cyclotomic import (  # noqa: E402
    CyclotomicInteger,
    CyclotomicRing,
    numeric_embedding_xy,
)


SALIDA = RAIZ / "datos" / "ordenes_sinteticos.json"
ORDENES = (16, 20, 24)
PASOS_CELDA = 2
PASOS_ROTACION = 2
NUMERO_CORONAS = 5
# Perfil escalonado en unidades relativas. Cada corona ocupa el intervalo entre
# dos cotas consecutivas: es una decision expositiva, no una medida historica.
COTAS = (
    Fraction(11, 2),
    Fraction(19, 4),
    Fraction(15, 4),
    Fraction(5, 2),
    Fraction(5, 4),
    Fraction(0),
)

NOMBRES = {
    16: "Trazado de ocho sectores",
    20: "Trazado de diez sectores",
    24: "Trazado de doce sectores",
}


def fraccion(valor: Fraction) -> list[int]:
    return [valor.numerator, valor.denominator]


def vertices_de_celda(
    ring: CyclotomicRing, corona: int, sector: int
) -> tuple[CyclotomicInteger, ...]:
    """Sector de una corona regular, exacto en Z[zeta_m]."""
    if not 0 <= corona < NUMERO_CORONAS:
        raise ValueError(f"corona fuera de rango: {corona}")
    sectores = ring.m // PASOS_ROTACION
    if not 0 <= sector < sectores:
        raise ValueError(f"sector fuera de rango: {sector}")
    direccion_a = ring.zeta_power(PASOS_ROTACION * sector)
    direccion_b = ring.zeta_power(PASOS_ROTACION * (sector + 1))
    if corona == 0:
        return (ring.zero, direccion_a, direccion_b)
    radio_interior = corona
    radio_exterior = corona + 1
    return (
        radio_interior * direccion_a,
        radio_exterior * direccion_a,
        radio_exterior * direccion_b,
        radio_interior * direccion_b,
    )


def construir_orden(m: int) -> dict[str, object]:
    """Construye una cupula escalonada y conserva su planta exacta."""
    if m < 6 or m % PASOS_ROTACION:
        raise ValueError(
            f"el orden debe ser par y >= 6 para esta composicion; se recibio {m}"
        )
    ring = CyclotomicRing(m)
    sectores = m // PASOS_ROTACION
    filas = []
    for corona in range(NUMERO_CORONAS):
        superior = COTAS[corona]
        inferior = COTAS[corona + 1]
        for sector in range(sectores):
            vertices = vertices_de_celda(ring, corona, sector)
            filas.append(
                {
                    "id": f"m{m}-corona-{corona + 1:02d}-sector-{sector + 1:02d}",
                    "tipo": "cupulilla" if corona == 0 else "paño escalonado",
                    "corona": corona + 1,
                    "sector": sector + 1,
                    "cota_superior": fraccion(superior),
                    "cota_inferior": fraccion(inferior),
                    "vertices_exactos": [list(vertice.coeffs) for vertice in vertices],
                    "vertices_xy": [list(numeric_embedding_xy(vertice)) for vertice in vertices],
                }
            )
    return {
        "orden": m,
        "nombre": NOMBRES.get(m, f"Trazado de {sectores} sectores"),
        "rango_ciclotomico": ring.degree,
        "pasos_por_celda": PASOS_CELDA,
        "pasos_por_rotacion": PASOS_ROTACION,
        "angulo_celda_grados": 360 * PASOS_CELDA / m,
        "simetria_rotacional": sectores,
        "numero_sectores": sectores,
        "numero_coronas": NUMERO_CORONAS,
        "numero_celdas": len(filas),
        "perfil_cotas": [fraccion(cota) for cota in COTAS],
        "celdas": filas,
    }


def construir_documento(ordenes: tuple[int, ...] = ORDENES) -> dict[str, object]:
    if len(set(ordenes)) != len(ordenes):
        raise ValueError("los ordenes no pueden repetirse")
    return {
        "modelo": "cupulas-comparativas-escalonadas",
        "afirmacion": "A",
        "alcance": (
            "composicion contemporanea para comparar ritmos de trazado; "
            "no reproduce un monumento ni una tipologia historica concreta"
        ),
        "procedencia": {
            "planta": "generada exactamente en Z[zeta_m]",
            "coordenadas_exactas": "coeficientes enteros en la base ciclotomica",
            "vertices_xy": "embedding numerico, solo para visualizacion",
            "volumen": (
                "cinco coronas y perfil escalonado elegidos para comparacion "
                "visual; decision 0014, sin atribucion historica"
            ),
            "unidades": "relativas; no son metros ni cotas de obra",
        },
        "ordenes": [construir_orden(m) for m in ordenes],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    parser.add_argument("--ordenes", nargs="+", type=int, default=list(ORDENES))
    args = parser.parse_args()
    documento = construir_documento(tuple(args.ordenes))
    args.salida.write_text(
        json.dumps(documento, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"escrito {args.salida}: "
        f"{', '.join(str(fila['orden']) for fila in documento['ordenes'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
