"""Barrido de A, forma y signo del campo (decision 0017, paso 4) para que se
lea la estrella de la red, como en Ferrer_5 y la ortoimagen.

Pedido del usuario el 2026-11-18: la cupula se ve muy distinta de Ferrer_5;
lo primero es que el dibujo grande (estrella central, brazos, celdas hondas)
se lea. Para cada combinacion dibuja, en planta vista desde abajo:

- el relieve de H sombreado con luz rasante (lo que el render ensena como
  profundidad), normalizado igual en todas las vistas;
- los frentes montables (colocacion suavizada, 2 filas por hilada);
- el total de piezas, frente a las 5416 de Jones y Goury (entrada 18 de
  docs/fuentes.md), y el desnivel de H sobre el cono.

Hoja de contacto con la ortoimagen y Ferrer_5 al lado, y JSON con las cifras.
Es diagnostico para elegir a ojo; no calibra nada por si solo.

Uso:
    .venv/bin/python scripts/barrer_estrella_campo.py [--A 1,2,3,4.5] \
        [--formas lineal,raiz] [--signos 1,-1]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.campo import PENDIENTE, RADIO_BASE, campo  # noqa: E402
from granada.hiladas_campo import admitido_suavizado, frente_suavizado, frentes, hilada_de  # noqa: E402

PANEL = 420
LUZ = np.array([-0.55, 0.45, 0.70])
"""Luz rasante para el sombreado (direccion hacia la luz). Eleccion."""


def sombreado(c) -> np.ndarray:
    """Relieve de H sin el cono, sombreado por la normal, visto desde abajo."""
    gy, gx = np.gradient(c.H, c.paso)
    n = np.stack([-gx, -gy, np.ones_like(gx)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    l = LUZ / np.linalg.norm(LUZ)
    s = np.clip(n @ l, 0, 1)
    X, Y = np.meshgrid(c.x, c.y)
    s[np.hypot(X, Y) > RADIO_BASE] = 0.15
    # Vista desde abajo: espejo en x.
    return s[::-1, ::-1]


def panel(c, filas: int, rotulo: str) -> tuple[Image.Image, dict]:
    s = sombreado(c)
    im = Image.fromarray((40 + 200 * s).astype(np.uint8)).convert("RGB").resize((PANEL, PANEL))
    dr = ImageDraw.Draw(im)
    escala = PANEL / (c.x[-1] - c.x[0])
    piezas = 0
    n = 0
    for f in frentes(c, filas_por_hilada=filas):
        if not admitido_suavizado(f):
            continue
        fs = frente_suavizado(f)
        piezas += hilada_de(fs).piezas
        n += 1
        P = [(PANEL / 2 - x * escala, PANEL / 2 - y * escala) for x, y in fs.puntos]
        dr.line(P, fill=(200, 60, 40) if hilada_de(fs).familia == "C" else (40, 90, 200), width=1)
    X, Y = np.meshgrid(c.x, c.y)
    cono = np.maximum(0.0, (RADIO_BASE - np.hypot(X, Y)) * PENDIENTE)
    desnivel = float(np.abs(c.H - cono).max())
    dr.rectangle((0, 0, PANEL, 30), fill=(20, 20, 20))
    dr.text((6, 3), rotulo, fill="white")
    dr.text((6, 16), f"{piezas} piezas ({piezas / 5416:.0%} de 5416), {n} frentes", fill="white")
    return im, {"piezas": piezas, "frentes": n, "desnivel_max_catetos": desnivel}


def referencia(ruta: Path, rotulo: str) -> Image.Image:
    im = Image.open(ruta).convert("RGB")
    lado = min(im.size)
    im = im.crop(((im.width - lado) // 2, (im.height - lado) // 2,
                  (im.width + lado) // 2, (im.height + lado) // 2)).resize((PANEL, PANEL))
    ImageDraw.Draw(im).rectangle((0, 0, PANEL, 16), fill=(20, 20, 20))
    ImageDraw.Draw(im).text((6, 3), rotulo, fill="white")
    return im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--A", default="1,2,3,4.5")
    ap.add_argument("--formas", default="lineal,raiz")
    ap.add_argument("--signos", default="1,-1")
    ap.add_argument("--filas-por-hilada", type=int, default=2)
    ap.add_argument("--png", type=Path, default=RAIZ / "renders" / "previas" / "barrido_estrella.png")
    ap.add_argument("--json", type=Path, default=RAIZ / "datos" / "barrido_estrella.json")
    a = ap.parse_args()
    valores = [float(v) for v in a.A.split(",")]
    combinaciones = [(f, int(s)) for f in a.formas.split(",") for s in a.signos.split(",")]
    paneles = [referencia(RAIZ / "docs" / "AA-415_23_orto_techo.jpg", "Ortoimagen AA-415_23 (2021)"),
               referencia(RAIZ / "docs" / "Ferrer_5.png", "Ferrer_5: maqueta de Contreras (XIX)")]
    paneles += [Image.new("RGB", (PANEL, PANEL), (30, 30, 30))] * (len(valores) - 2)
    resultados = []
    for forma, signo in combinaciones:
        for A in valores:
            c = campo(A=A, forma=forma, signo=signo)
            im, r = panel(c, a.filas_por_hilada, f"A={A} forma={forma} signo={signo:+d}")
            paneles.append(im)
            resultados.append({"A": A, "forma": forma, "signo": signo, **r})
            print(resultados[-1])
    columnas = len(valores)
    filas = (len(paneles) + columnas - 1) // columnas
    hoja = Image.new("RGB", (columnas * PANEL, filas * PANEL), (30, 30, 30))
    for k, im in enumerate(paneles):
        hoja.paste(im, ((k % columnas) * PANEL, (k // columnas) * PANEL))
    a.png.parent.mkdir(parents=True, exist_ok=True)
    hoja.save(a.png)
    fuentes = ["granada/campo.py", "granada/hiladas_campo.py", "scripts/barrer_estrella_campo.py",
               "datos/red_medinas.json", "datos/registro_red.json"]
    a.json.write_text(json.dumps({
        "procedencia": "Diagnostico para elegir A, forma y signo a ojo (2026-11-18); no calibra",
        "referencia_piezas": {"total": 5416, "fuente": "Jones y Goury, docs/fuentes.md entrada 18"},
        "filas_por_hilada": a.filas_por_hilada,
        "entorno": {"python": platform.python_version(), "numpy": np.__version__},
        "sha256": {p: hashlib.sha256((RAIZ / p).read_bytes()).hexdigest() for p in fuentes},
        "resultados": resultados,
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"-> {a.png}\n-> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
