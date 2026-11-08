"""Colores de la ortoimagen de AA-415_23: yeso y acentos, con varios umbrales.

docs/paleta.md (2026-08-24) separo el pigmento con saturacion >= 0,20 y dio
58 % de tierra. A ojo, los acentos de la foto son verdes, azules y granates.
Hipotesis a comprobar: la banda tierra es sobre todo suciedad de baja
saturacion. Si lo es, su peso debe caer al subir el umbral de saturacion.

Mismo recorte que paleta.md (20-80 % del lado). Para cada umbral de
saturacion da el peso de cada banda de tono y su color mediano (RGB), y el
color mediano del yeso (S < 0,12) en su cuartil claro, que es el yeso con luz.

Uso:  python3 scripts/medir_acentos_ortoimagen.py [--entrada img] [--salida json] [--nota texto]
Entrada: docs/AA-415_23_orto_techo.jpg (excluida por derechos; copia en Drive).
Salida: datos/acentos_ortoimagen.json

Con --entrada se mide otra imagen con el mismo metodo; el 2026-11-08 se
midio asi la foto de Commons (docs/fuentes.md, entrada 19) como segunda
fuente, en datos/acentos_foto_commons.json.
"""

from __future__ import annotations

import argparse
import colorsys
import json
import statistics
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
ORTO = RAIZ / "docs" / "AA-415_23_orto_techo.jpg"
SALIDA = RAIZ / "datos" / "acentos_ortoimagen.json"

BANDAS = {
    # nombre: (H minimo, H maximo) en grados
    "granate": (330, 360 + 15),
    "tierra": (15, 38),
    "ocre": (38, 65),
    "verde": (65, 175),
    "azul": (175, 260),
}
UMBRALES_S = (0.20, 0.30, 0.40)
UMBRALES_V = (0.28, 0.45)
"""V >= 0,28 es el de paleta.md; V >= 0,45 deja fuera los huecos en sombra."""


def banda(h_grados: float) -> str | None:
    for nombre, (a, b) in BANDAS.items():
        if a <= h_grados < b or a <= h_grados + 360 < b:
            return nombre
    return None


def mediana_rgb(px: list[tuple[int, int, int]]) -> str:
    r, g, b = (round(statistics.median(c[i] for c in px)) for i in range(3))
    return f"#{r:02X}{g:02X}{b:02X}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", type=Path, default=ORTO)
    ap.add_argument("--salida", type=Path, default=SALIDA)
    ap.add_argument("--nota", default="color del estado de 2021 bajo la luz del levantamiento; no es el color original")
    a = ap.parse_args()
    im = Image.open(a.entrada).convert("RGB")
    w, h = im.size
    im = im.crop((int(0.2 * w), int(0.2 * h), int(0.8 * w), int(0.8 * h))).resize((1400, 1400), Image.LANCZOS)
    pixeles = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata())
    hsv = [colorsys.rgb_to_hsv(r / 255, g / 255, b / 255) for r, g, b in pixeles]

    yeso = [(p, v) for p, (_, s, v) in zip(pixeles, hsv) if s < 0.12]
    yeso.sort(key=lambda t: t[1])
    claro = [p for p, _ in yeso[3 * len(yeso) // 4:]]

    por_umbral = {}
    for s_min in UMBRALES_S:
        for v_min in UMBRALES_V:
            grupos: dict[str, list] = {n: [] for n in BANDAS}
            for p, (hh, s, v) in zip(pixeles, hsv):
                if s >= s_min and v >= v_min:
                    n = banda(hh * 360)
                    if n:
                        grupos[n].append(p)
            total = sum(len(g) for g in grupos.values())
            por_umbral[f"S>={s_min:.2f} V>={v_min:.2f}"] = {
                "fraccion_de_pixeles": round(total / len(pixeles), 4),
                "bandas": {
                    n: {"peso": round(len(g) / total, 4) if total else 0.0, "mediana": mediana_rgb(g) if g else None}
                    for n, g in grupos.items()
                },
            }

    salida = {
        "fuente": f"{a.entrada.resolve().relative_to(RAIZ)}, recorte 20-80 %, 1400 px",
        "yeso": {"fraccion_de_pixeles": round(len(yeso) / len(pixeles), 4), "mediana_cuartil_claro": mediana_rgb(claro)},
        "por_umbral": por_umbral,
        "nota": a.nota,
    }
    a.salida.write_text(json.dumps(salida, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(salida, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
