"""Paleta de Ferrer_5 (maqueta de Contreras, siglo XIX) dentro de la cupula.

Pedido del usuario el 2026-11-18: que la cupula se parezca mas a Ferrer_5. El
contraste de la maqueta es de color: fondos de celda marron oscuro y caras
crema con acentos rojos. Este script mide esos tonos para no elegirlos a ojo.

Region: disco central de la imagen de radio RADIO_FRACCION del semilado (el
octogono de la cupula en Ferrer_5, sin tambor ni sala). Clases, por pixel:
- oscuro: luminancia por debajo del percentil 25;
- claro: luminancia por encima del percentil 75 y saturacion < 0,35;
- rojo: tono en [345, 20] grados, S >= 0,35, V >= 0,35;
- azul: tono en [190, 250] grados, S >= 0,15, V >= 0,30.
De cada clase se da la mediana RGB y su fraccion de pixeles.

Ferrer_5 es una foto de pantalla de una restitucion del XIX, no una medida
de la obra: los tonos describen la maqueta (docs/fuentes.md, entrada 12).

Uso: .venv/bin/python scripts/medir_paleta_ferrer.py
Salida: datos/paleta_ferrer.json
"""

from __future__ import annotations

import colorsys
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
FUENTE = RAIZ / "docs" / "Ferrer_5.png"
SALIDA = RAIZ / "datos" / "paleta_ferrer.json"
RADIO_FRACCION = 0.5
"""El octogono de la cupula ocupa ~0,55 del semilado de Ferrer_5; 0,5 deja
fuera el tambor. Medido a ojo sobre la imagen."""


def _hex(rgb) -> str:
    return "#{:02X}{:02X}{:02X}".format(*(int(round(c)) for c in rgb))


def main() -> int:
    im = np.asarray(Image.open(FUENTE).convert("RGB"), dtype=float)
    h, w, _ = im.shape
    Y, X = np.mgrid[0:h, 0:w]
    dentro = np.hypot(X - w / 2, Y - h / 2) < RADIO_FRACCION * min(h, w) / 2
    P = im[dentro]
    hsv = np.array([colorsys.rgb_to_hsv(*(p / 255)) for p in P])
    H, S, V = hsv[:, 0] * 360, hsv[:, 1], hsv[:, 2]
    L = P @ np.array([0.2126, 0.7152, 0.0722])
    p25, p75 = np.percentile(L, [25, 75])
    clases = {
        "oscuro": L < p25,
        "claro": (L > p75) & (S < 0.35),
        "rojo": ((H >= 345) | (H <= 20)) & (S >= 0.35) & (V >= 0.35),
        "azul": (H >= 190) & (H <= 250) & (S >= 0.15) & (V >= 0.30),
    }
    resultado = {}
    for nombre, m in clases.items():
        resultado[nombre] = {
            "mediana": _hex(np.median(P[m], axis=0)) if m.any() else None,
            "fraccion": float(m.mean()),
        }
        print(nombre, resultado[nombre])
    SALIDA.write_text(json.dumps({
        "fuente": {"ruta": str(FUENTE.relative_to(RAIZ)),
                   "sha256": hashlib.sha256(FUENTE.read_bytes()).hexdigest()},
        "region": {"radio_fraccion_semilado": RADIO_FRACCION},
        "naturaleza": "maqueta del XIX fotografiada en pantalla; describe la restitucion, no la obra",
        "clases": resultado,
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"-> {SALIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
