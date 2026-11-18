"""Tira comparativa: Ferrer_5 y una o varias vistas de la cupula, a la misma
altura y con rotulo. Solo compone imagenes; no mide nada.

Uso:
    .venv/bin/python scripts/comparar_con_ferrer.py SALIDA.png \
        "rotulo1=ruta1.png" "rotulo2=ruta2.png" [--alto 600]

Ferrer_5 (docs/Ferrer_5.png) va siempre la primera, recortada al octogono
del tambor (RECORTE_FERRER, a ojo) para que su escala se parezca a la de la
vista «cupula» de scripts/render_cycles.py.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[1]
FERRER = RAIZ / "docs" / "Ferrer_5.png"
RECORTE_FERRER = (130, 130, 730, 730)
"""(izq, arriba, der, abajo) en px de Ferrer_5: el octogono con su marco. A ojo."""
ROTULO_ALTO = 28


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("salida")
    ap.add_argument("vistas", nargs="+", help="rotulo=ruta.png")
    ap.add_argument("--alto", type=int, default=600)
    a = ap.parse_args()
    paneles = [("Ferrer_5 (maqueta, s. XIX)", Image.open(FERRER).convert("RGB").crop(RECORTE_FERRER))]
    for v in a.vistas:
        rotulo, ruta = v.split("=", 1)
        paneles.append((rotulo, Image.open(ruta).convert("RGB")))
    paneles = [(r, im.resize((round(im.width * a.alto / im.height), a.alto))) for r, im in paneles]
    ancho = sum(im.width for _, im in paneles)
    tira = Image.new("RGB", (ancho, a.alto + ROTULO_ALTO), "white")
    d = ImageDraw.Draw(tira)
    x = 0
    for rotulo, im in paneles:
        tira.paste(im, (x, ROTULO_ALTO))
        d.text((x + 8, 8), rotulo, fill="black")
        x += im.width
    tira.save(a.salida)
    print(f"-> {a.salida}")


if __name__ == "__main__":
    main()
