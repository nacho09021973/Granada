#!/usr/bin/env python3
"""Renderiza la nivelacion aproximada como planta hipsometrica auditable."""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
RED = RAIZ / "datos" / "red_medinas.json"
CARAS = RAIZ / "datos" / "caras_red.json"
NIVELES = RAIZ / "datos" / "niveles_aproximados.json"
SALIDA = RAIZ / "renders" / "niveles_aproximados.svg"

ANCHO = 1100
ALTO = 1100
CENTRO_X = 550
CENTRO_Y = 575
ESCALA = 128

PALETA = (
    "#d8ddd8",
    "#9ab7a5",
    "#65a6a6",
    "#4c82a6",
    "#6e6aa6",
    "#a05e8c",
    "#bf665e",
    "#d69a4a",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    args = parser.parse_args()

    red = json.loads(RED.read_text(encoding="utf-8"))
    caras = json.loads(CARAS.read_text(encoding="utf-8"))["caras"]
    niveles_dato = json.loads(NIVELES.read_text(encoding="utf-8"))
    niveles = {cara["id"]: cara for cara in niveles_dato["caras"]}
    nodos = red["nodos"]

    def proyectar(indice: int) -> tuple[float, float]:
        x, y = nodos[indice]
        return (CENTRO_X + x * ESCALA, CENTRO_Y + y * ESCALA)

    ordenadas = caras
    piezas = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ANCHO}" height="{ALTO}" '
        f'viewBox="0 0 {ANCHO} {ALTO}">',
        "<defs>",
        '<pattern id="incierto" width="8" height="8" patternUnits="userSpaceOnUse" '
        'patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="8" '
        'stroke="#ffffff" stroke-opacity="0.48" stroke-width="2"/></pattern>',
        '<filter id="sombra" x="-20%" y="-20%" width="140%" height="140%">'
        '<feDropShadow dx="0" dy="5" stdDeviation="8" flood-color="#18201f" '
        'flood-opacity="0.15"/></filter>',
        "</defs>",
        f'<rect width="{ANCHO}" height="{ALTO}" fill="#f4f3ef"/>',
        '<g filter="url(#sombra)">',
    ]

    for cara in ordenadas:
        info = niveles[cara["id"]]
        nivel = info["nivel"]
        color = PALETA[nivel]
        puntos = " ".join(
            f"{x:.1f},{y:.1f}" for x, y in (proyectar(v) for v in cara["vertices"])
        )
        titulo = escape(
            f"{cara['id']}: nivel {nivel}, intervalo "
            f"{info['intervalo_nivel'][0]}-{info['intervalo_nivel'][1]}"
        )
        piezas.append(
            f'<polygon points="{puntos}" fill="{color}" stroke="#263330" '
            f'stroke-width="1.05"><title>{titulo}</title></polygon>'
        )
        if not info["estable_7_8"]:
            piezas.append(
                f'<polygon points="{puntos}" fill="url(#incierto)" stroke="none"/>'
            )

    piezas.extend(
        [
            "</g>",
            '<g font-family="DejaVu Sans, sans-serif" fill="#1f2927">',
            '<text x="48" y="48" font-size="26" font-weight="700">'
            "Sala de las Dos Hermanas</text>",
            '<text x="48" y="76" font-size="16" fill="#4b5956">'
            "Planta hipsométrica aproximada · niveles 0–7</text>",
            '<text x="48" y="100" font-size="12" fill="#65716e">'
            "105 caras · 227 vecindades · saltos de 0, 1 o 2 niveles</text>",
            '<g transform="translate(48 1018)">',
        ]
    )
    for nivel, color in enumerate(PALETA):
        x = nivel * 54
        piezas.append(
            f'<rect x="{x}" y="0" width="46" height="14" fill="{color}"/>'
        )
        piezas.append(
            f'<text x="{x + 18}" y="34" font-size="12">{nivel}</text>'
        )
    piezas.extend(
        [
            '<rect x="500" y="0" width="32" height="18" fill="#6e6aa6"/>',
            '<rect x="500" y="0" width="32" height="18" fill="url(#incierto)"/>',
            '<text x="542" y="14" font-size="13">cambia en el escenario de 8 niveles</text>',
            "</g>",
            '<text x="48" y="1082" font-size="12" fill="#65716e">'
            "Modelo inferido para prototipado; no es una restitución histórica verificada.</text>",
            "</g></svg>",
        ]
    )
    args.salida.write_text("\n".join(piezas) + "\n", encoding="utf-8")
    print(f"escrito {args.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
