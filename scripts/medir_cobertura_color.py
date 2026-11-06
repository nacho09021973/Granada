"""Cobertura de pigmento: modelo coloreado frente a la ortoimagen de AA-415_23.

Aplica a las dos imagenes el filtro de docs/paleta.md: recorte al 20-80 % del
lado, HSV, y cuenta como pigmento los pixeles con saturacion >= 0,20 y valor
>= 0,28. Del modelo se usa la vista cenital del rasterizador de
`granada.render3d`, con la luz del render de color de
scripts/render_cupula_piezas.py.

No es una medida de fidelidad: la foto es el estado de 2021, con el color casi
perdido. Sirve para calibrar `PROBABILIDAD_DISPERSO` de granada/color.py, que
es eleccion estetica.

Uso:  python3 scripts/medir_cobertura_color.py [--reparto disperso|anillos]
Salida: datos/cobertura_color_<reparto>.json
"""

from __future__ import annotations

import argparse
import colorsys
import json
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.color import rgb  # noqa: E402
from granada.cupula import cupula  # noqa: E402
from granada.render3d import rasterizar  # noqa: E402

ORTO = RAIZ / "docs" / "AA-415_23_orto_techo.jpg"
S_MIN, V_MIN = 0.20, 0.28


def fraccion_pigmento(im: Image.Image, lado: int = 700) -> float:
    w, h = im.size
    recorte = im.convert("RGB").crop((int(0.2 * w), int(0.2 * h), int(0.8 * w), int(0.8 * h)))
    recorte = recorte.resize((lado, lado), Image.LANCZOS)
    n = 0
    datos = recorte.get_flattened_data() if hasattr(recorte, "get_flattened_data") else recorte.getdata()
    for r, g, b in datos:
        _, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        n += s >= S_MIN and v >= V_MIN
    return n / (lado * lado)


def cenital(reparto: str, lado: int, subdivision: int) -> Image.Image:
    _, grupos = cupula(subdivision, color=True, reparto=reparto)
    V, F, colores, sombras = [], [], [], []
    for _, Vg, Fg, Cg, Sg in grupos:
        base = len(V)
        V.extend(Vg)
        F.extend((a + base, b + base, c + base) for a, b, c in Fg)
        colores.extend(rgb(c) for c in Cg)
        sombras.extend(Sg)
    luces = [((0.55, 0.35, -0.75), 0.75), ((-0.6, -0.45, -0.65), 0.3)]
    vista = ((0.0, 0.0, -13.0), (0.0, 0.001, 10.0), 90.0)
    im, _ = rasterizar(V, F, lado, lado, supermuestreo=2, luces=luces, perspectiva=vista,
                       colores=colores, tono=sombras, ambiente=0.6)
    return im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reparto", default="disperso", choices=("disperso", "anillos"))
    ap.add_argument("--lado", type=int, default=900)
    ap.add_argument("--subdivision", type=int, default=6)
    args = ap.parse_args()

    modelo = fraccion_pigmento(cenital(args.reparto, args.lado, args.subdivision))
    foto = fraccion_pigmento(Image.open(ORTO)) if ORTO.exists() else None
    salida = {
        "reparto": args.reparto,
        "filtro": {"recorte": "20-80 %", "saturacion_min": S_MIN, "valor_min": V_MIN},
        "fraccion_pigmento_modelo": round(modelo, 4),
        "fraccion_pigmento_ortoimagen": None if foto is None else round(foto, 4),
        "nota": "calibracion estetica; la foto es el estado de 2021, no el original",
    }
    destino = RAIZ / "datos" / f"cobertura_color_{args.reparto}.json"
    destino.write_text(json.dumps(salida, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(salida, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
