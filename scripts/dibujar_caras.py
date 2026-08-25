#!/usr/bin/env python3
"""Dibuja las caras de la red y su clasificacion en un SVG auditable.

Sirve para mirar la planta antes de levantar nada: donde estan las caras que
ajustan a una figura documentada, cuales quedan sin clasificar y cuales no son
ni convexas. No usa la ortoimagen ni ninguna dependencia externa.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA_RED = RAIZ / "datos" / "red_medinas.json"
ENTRADA_CARAS = RAIZ / "datos" / "caras_red.json"
SALIDA = RAIZ / "renders" / "caras_red.svg"

LADO_PX = 900
MARGEN_PX = 30

COLOR = {
    "medio_cuadrado": "#c65a2e",
    "media_jaira": "#d8a13a",
    "jaira": "#7a9a4e",
    "cuadrado": "#3f7ea6",
    "octogono": "#6a4c93",
}
COLOR_SIN_FIGURA = "#e8e2d6"
COLOR_NO_CONVEXA = "#d6cec0"
COLOR_MEDINA = "#3a3632"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=SALIDA)
    argumentos = parser.parse_args()

    red = json.loads(ENTRADA_RED.read_text(encoding="utf-8"))
    caras = json.loads(ENTRADA_CARAS.read_text(encoding="utf-8"))
    nodos = red["nodos"]

    extremo = max(max(abs(x), abs(y)) for x, y in nodos)
    escala = (LADO_PX / 2 - MARGEN_PX) / extremo

    def punto(indice: int) -> tuple[float, float]:
        x, y = nodos[indice]
        return (LADO_PX / 2 + x * escala, LADO_PX / 2 + y * escala)

    piezas = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{LADO_PX}" '
        f'height="{LADO_PX}" viewBox="0 0 {LADO_PX} {LADO_PX}">',
        f'<rect width="{LADO_PX}" height="{LADO_PX}" fill="#fbf8f2"/>',
        "<g>",
    ]
    for cara in caras["caras"]:
        if cara["figura"] is None:
            relleno = COLOR_SIN_FIGURA if cara["convexa"] else COLOR_NO_CONVEXA
            opacidad = "1"
        else:
            relleno = COLOR[cara["figura"]]
            opacidad = "1" if cara["firmeza"] == "confirmada" else "0.45"
        puntos = " ".join(
            f"{x:.2f},{y:.2f}" for x, y in (punto(v) for v in cara["vertices"])
        )
        piezas.append(
            f'<polygon points="{puntos}" fill="{relleno}" fill-opacity="{opacidad}" '
            f'stroke="none"><title>{cara["id"]}: '
            f'{cara["figura"] or "sin clasificar"}, {cara["lados"]} lados, '
            f'{cara["area_m2"]:.4f} m2</title></polygon>'
        )
    piezas.append("</g><g>")
    for a, b, _, _ in red["aristas"]:
        (x1, y1), (x2, y2) = punto(a), punto(b)
        piezas.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{COLOR_MEDINA}" stroke-width="1.1"/>'
        )
    piezas.append("</g><g>")
    for indice in red["nodos_borde"]:
        x, y = punto(indice)
        piezas.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.2" fill="none" '
            f'stroke="{COLOR_MEDINA}" stroke-width="1.2"/>'
        )
    piezas.append("</g>")

    leyenda = [
        ("medio cuadrado (figura A), 8 confirmadas", COLOR["medio_cuadrado"], "1"),
        ("octogono central, 1 confirmada", COLOR["octogono"], "1"),
        ("cuadrado, 16 al limite de resolucion", COLOR["cuadrado"], "0.45"),
        ("sin clasificar, convexa", COLOR_SIN_FIGURA, "1"),
        ("sin clasificar, no convexa", COLOR_NO_CONVEXA, "1"),
        ("terminal de borde (ancla candidata)", "none", "1"),
    ]
    piezas.append(
        '<g font-family="DejaVu Sans, sans-serif" font-size="12" fill="#3a3632">'
    )
    for fila, (texto, color, opacidad) in enumerate(leyenda):
        y = MARGEN_PX / 2 + 16 * fila
        if color == "none":
            piezas.append(
                f'<circle cx="{MARGEN_PX / 2 + 6}" cy="{y + 5}" r="3.2" fill="none" '
                f'stroke="{COLOR_MEDINA}" stroke-width="1.2"/>'
            )
        else:
            piezas.append(
                f'<rect x="{MARGEN_PX / 2}" y="{y}" width="12" height="10" '
                f'fill="{color}" fill-opacity="{opacidad}"/>'
            )
        piezas.append(f'<text x="{MARGEN_PX / 2 + 18}" y="{y + 9}">{texto}</text>')
    piezas.append("</g></svg>")

    argumentos.salida.write_text("\n".join(piezas) + "\n", encoding="utf-8")
    print(f"escrito {argumentos.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
