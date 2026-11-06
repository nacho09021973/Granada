#!/usr/bin/env python3
"""Mide fase, radio y tamano de los 16 cupulines sobre la ortoimagen cenital.

Fuente: `docs/AA-415_23_orto_techo.jpg`, la ortoimagen de la lamina AA-415_23
(4083 x 4054 px). No se versiona por derechos (`.gitignore`); este script la
necesita en local. Salida: `datos/cupulines.json`.

Metodo
------
1. Fase: se barre la fase de 0 a 22,5 grados y, para cada una, la mediana de
   luminancia en 16 discos repartidos cada 22,5 grados, sobre una corona de
   radios 1300-1700 px. La fase de los cupulines es la mas oscura.
2. Radio: perfil radial de esa mediana en la fase hallada; el cupulin esta en
   el minimo.
3. Diametro: anchura del perfil por debajo del punto medio entre el minimo y
   el nivel de los controles (fase + 11,25 grados) al mismo radio.

Escala, que es un supuesto
--------------------------
`docs/estratificacion.md` calibra la seccion de la misma lamina en 236,1 px/m
renderizada a 150 dpi. La ortoimagen esta incrustada a 300 ppi; si la planta
esta a la misma escala 1/25 que la seccion, son 472,2 px/m. Lo corroboran el
ancho de la imagen (8,65 m) y que el radio de arranque medido en la seccion,
3,64 m, cae dentro del marco del octogono. No esta comprobado con una cota de
la propia planta.

El centro es el del analisis de sombra, (2048, 2035).
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
ORTO = RAIZ / "docs" / "AA-415_23_orto_techo.jpg"
SALIDA = RAIZ / "datos" / "cupulines.json"
CENTRO = (2048, 2035)
PX_POR_M = 2 * 236.1
PARCHE = 30
COPIAS = 16


def mediana_anillo(lum, radio, fase_grados):
    cx, cy = CENTRO
    v = []
    for k in range(COPIAS):
        a = math.radians(fase_grados + k * 360 / COPIAS)
        x, y = int(round(cx + radio * math.cos(a))), int(round(cy + radio * math.sin(a)))
        v.append(float(np.median(lum[y - PARCHE : y + PARCHE, x - PARCHE : x + PARCHE])))
    return float(np.median(v))


def main() -> int:
    if not ORTO.exists():
        print(f"falta {ORTO.relative_to(RAIZ)}", file=sys.stderr)
        return 1
    lum = np.asarray(Image.open(ORTO).convert("L"), dtype=float)

    fases = np.arange(0, 22.5, 0.25)
    corona = range(1300, 1701, 25)
    oscuridad = [np.mean([mediana_anillo(lum, r, f) for r in corona]) for f in fases]
    fase = float(fases[int(np.argmin(oscuridad))])

    radios = np.arange(1100, 1851, 10)
    perfil = np.array([mediana_anillo(lum, r, fase) for r in radios])
    control = np.array([mediana_anillo(lum, r, fase + 180 / COPIAS) for r in radios])
    i = int(np.argmin(perfil))
    umbral = (perfil[i] + control[i]) / 2
    j0 = i
    while j0 > 0 and perfil[j0 - 1] < umbral:
        j0 -= 1
    j1 = i
    while j1 < len(perfil) - 1 and perfil[j1 + 1] < umbral:
        j1 += 1
    radio_px = float((radios[j0] + radios[j1]) / 2)
    diametro_px = float(radios[j1] - radios[j0] + 10)

    resultado = {
        "version": 1,
        "fuente": {
            "ruta": str(ORTO.relative_to(RAIZ)),
            "sha256": hashlib.sha256(ORTO.read_bytes()).hexdigest(),
            "imagen_px": list(lum.shape[::-1]),
        },
        "metodo": {
            "script": "scripts/medir_cupulines.py",
            "centro_px": list(CENTRO),
            "parche_px": PARCHE,
            "px_por_m_supuesto": PX_POR_M,
            "escala": "supuesta: 1/25 como la seccion de la misma lamina, ver docstring",
        },
        "resultado": {
            "copias": COPIAS,
            "fase_grados": fase,
            "radio_px": radio_px,
            "diametro_px": diametro_px,
            "radio_m": radio_px / PX_POR_M,
            "diametro_m": diametro_px / PX_POR_M,
            "luminancia_minimo": float(perfil[i]),
            "luminancia_control_mismo_radio": float(control[i]),
        },
        "perfil": {
            "radios_px": radios.tolist(),
            "cupulines": perfil.round(2).tolist(),
            "controles": control.round(2).tolist(),
        },
        "aviso": (
            "La fase hallada no coincide con la fase 0 que usa scripts/analizar_sombra_niveles.py; "
            "sin resolver si es otra orientacion de la imagen o un error de aquel analisis."
        ),
    }
    SALIDA.write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(resultado["resultado"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
