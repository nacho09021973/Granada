#!/usr/bin/env python3
"""Contrasta la cupula por piezas con la ortoimagen cenital de AA-415_23.

Pone el render cenital del modelo a la escala, centro y orientacion de la
ortoimagen y mide lo mismo en las dos con el mismo codigo:

1. **Espectro angular por zonas**: desenrollado polar y FFT angular, el metodo
   de la entrada 7 de `docs/fuentes.md`. Fraccion de potencia en k = 1, 4, 8,
   16, 32 sobre la potencia total de k >= 1. Aplicado a la ortoimagen es ademas
   un control contra la tabla de `fuentes.md` (alli en otra normalizacion y con
   zonas no documentadas: se comparan los ordenes, no las cifras).
2. **Correlacion polar con giro**: correlacion de Pearson entre las dos
   imagenes desenrolladas, por zona, girando el modelo de 0 a 45 grados. Si la
   colocacion angular del modelo es buena, el maximo cae en 0 (o en multiplos
   de 45) y los giros de control dan menos. Se calcula en crudo y con las dos
   imagenes suavizadas (gaussiana de `SUAVIZADO_M`), para medir solo la
   estructura grande: la textura fina del modelo no se parece a la real.

Salidas: `renders/contraste_ortoimagen.png` (ortoimagen | modelo | mezcla) y
`datos/contraste_ortoimagen.json`.

Supuestos, heredados y no elegidos aqui: escala 472,2 px/m y centro (2048, 2035)
de `scripts/medir_cupulines.py`; eje y de la imagen hacia abajo igual al eje y
del modelo. Las zonas radiales son eleccion de este script.

Derechos: la ortoimagen es de la RABASF (entrada 3 de `fuentes.md`); el panel
que la reproduce sigue el precedente de `renders/planta_sobre_orto.png`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, map_coordinates

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.cupula import CATETO_M, cupula  # noqa: E402
from granada.render3d import rasterizar  # noqa: E402

ORTO = RAIZ / "docs" / "AA-415_23_orto_techo.jpg"
CENTRO_PX = (2048, 2035)
PX_POR_M = 2 * 236.1
REDUCCION = 2
ZONAS_M = {"estrella_central": (0.2, 0.9), "cuerpo": (0.9, 2.7), "anillo_exterior": (2.7, 3.5)}
ARMONICOS = (1, 4, 8, 16, 32)
MUESTRAS_ANGULO = 1440
SUAVIZADO_M = 0.15
TONO_CONTROL = 0.4
# Luz vertical desde abajo: simetrica, para que el contraste no mida la
# direccion de la luz (las luces laterales del render meten k=1 y rompen
# la equivalencia entre giros de 0 y 45 grados).
LUCES = [((0.0, 0.0, -1.0), 1.0)]


def polar(lum, centro, r0, r1, giro_muestras: int = 0):
    """Matriz (radios, angulos) de luminancia por interpolacion bilineal."""
    cx, cy = centro
    r = np.arange(r0, r1)[:, None]
    a = 2 * np.pi * np.arange(MUESTRAS_ANGULO)[None, :] / MUESTRAS_ANGULO
    x = cx + r * np.cos(a)
    y = cy + r * np.sin(a)
    m = map_coordinates(lum, [y.ravel(), x.ravel()], order=1).reshape(x.shape)
    return np.roll(m, giro_muestras, axis=1) if giro_muestras else m


def espectro(m):
    c = np.fft.rfft(m - m.mean(axis=1, keepdims=True), axis=1)
    p = (np.abs(c) ** 2).sum(axis=0)
    total = p[1:].sum()
    return {f"k{k}": float(p[k] / total) for k in ARMONICOS}


def correlacion(a, b):
    a = (a - a.mean()) / a.std()
    b = (b - b.mean()) / b.std()
    return float((a * b).mean())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--png", type=Path, default=RAIZ / "renders" / "contraste_ortoimagen.png")
    ap.add_argument("--informe", type=Path, default=RAIZ / "datos" / "contraste_ortoimagen.json")
    args = ap.parse_args()
    if not ORTO.exists():
        print(f"falta {ORTO.relative_to(RAIZ)}", file=sys.stderr)
        return 1

    orto_img = Image.open(ORTO).convert("L")
    W, H = orto_img.size[0] // REDUCCION, orto_img.size[1] // REDUCCION
    orto = np.asarray(orto_img.resize((W, H), Image.LANCZOS), dtype=float)
    centro = (CENTRO_PX[0] / REDUCCION, CENTRO_PX[1] / REDUCCION)
    px_m = PX_POR_M / REDUCCION

    _, grupos = cupula()
    V, F, tono = [], [], []
    for nombre, Vg, Fg in grupos:
        base = len(V)
        tono.extend([TONO_CONTROL if nombre.startswith("cupulin_") else 1.0] * len(Fg))
        # y del modelo = y de la imagen (hacia abajo): se invierte para que
        # la proyeccion, que pone y hacia arriba, lo deje en su sitio.
        V.extend((x, -y, z) for x, y, z in Vg)
        F.extend((a + base, b + base, c + base) for a, b, c in Fg)
    render, _ = rasterizar(
        V, F, W, H, azim=0.0, elev=-90.0, luces=LUCES,
        encuadre=(centro[0], centro[1], px_m * CATETO_M),
    )
    modelo = np.asarray(render.convert("L"), dtype=float)
    # Control, no acabado elegido: los mismos cupulines oscurecidos. Sirve para
    # ver si la anticorrelacion del anillo exterior se debe a que en el modelo
    # son claros y en la foto oscuros.
    control, _ = rasterizar(
        V, F, W, H, azim=0.0, elev=-90.0, luces=LUCES, tono=tono,
        encuadre=(centro[0], centro[1], px_m * CATETO_M),
    )
    modelo_c = np.asarray(control.convert("L"), dtype=float)

    sigma = SUAVIZADO_M * px_m
    orto_s, modelo_s = gaussian_filter(orto, sigma), gaussian_filter(modelo, sigma)
    modelo_cs = gaussian_filter(modelo_c, sigma)
    giros = np.arange(0, 45.01, 0.5)

    def barrido(a, b):
        c = np.array([correlacion(a, np.roll(b, int(round(g / 360 * MUESTRAS_ANGULO)), axis=1)) for g in giros])
        return {
            "sin_giro": float(c[0]),
            "maxima": float(c.max()),
            "giro_del_maximo_grados": float(giros[int(c.argmax())]),
            "media_con_giro": float(c[1:].mean()),
            "por_giro": {f"{g:g}": round(float(v), 4) for g, v in zip(giros, c)},
        }

    zonas = {}
    for nombre, (m0, m1) in ZONAS_M.items():
        r0, r1 = int(m0 * px_m), int(m1 * px_m)
        po, pm = polar(orto, centro, r0, r1), polar(modelo, centro, r0, r1)
        zonas[nombre] = {
            "radios_m": [m0, m1],
            "espectro_ortoimagen": espectro(po),
            "espectro_modelo": espectro(pm),
            "correlacion_cruda": barrido(po, pm),
            "correlacion_suavizada": barrido(polar(orto_s, centro, r0, r1), polar(modelo_s, centro, r0, r1)),
            "control_cupulines_oscuros": {
                "espectro_modelo": espectro(polar(modelo_c, centro, r0, r1)),
                "correlacion_suavizada": barrido(polar(orto_s, centro, r0, r1), polar(modelo_cs, centro, r0, r1)),
            },
        }

    # Panel: ortoimagen | modelo | mezcla (ortoimagen en rojo, modelo en verde-azul).
    lado = 900
    def recorte(a):
        r = int(3.7 * px_m)
        cx, cy = int(centro[0]), int(centro[1])
        im = Image.fromarray(a[max(0, cy - r):cy + r, max(0, cx - r):cx + r].astype(np.uint8))
        return im.resize((lado, lado), Image.LANCZOS)
    io, im_ = recorte(orto), recorte(modelo)
    mezcla = Image.merge("RGB", (io, im_, im_))
    lienzo = Image.new("RGB", (3 * lado, lado + 50), (20, 19, 20))
    for k, panel in enumerate((io.convert("RGB"), im_.convert("RGB"), mezcla)):
        lienzo.paste(panel, (k * lado, 50))
    d = ImageDraw.Draw(lienzo)
    try:
        f = ImageFont.truetype("DejaVuSans.ttf", 26)
    except OSError:
        f = ImageFont.load_default()
    for k, t in enumerate(("Ortoimagen AA-415_23 (RABASF)", "Modelo por piezas", "Mezcla: rojo = foto, cian = modelo")):
        d.text((k * lado + lado // 2, 25), t, fill=(235, 225, 205), font=f, anchor="mm")
    lienzo.save(args.png)

    informe = {
        "version": 1,
        "fuente": {"ruta": str(ORTO.relative_to(RAIZ)), "sha256": hashlib.sha256(ORTO.read_bytes()).hexdigest()},
        "metodo": {
            "script": "scripts/contrastar_ortoimagen.py",
            "centro_px": list(CENTRO_PX),
            "px_por_m_supuesto": PX_POR_M,
            "reduccion": REDUCCION,
            "muestras_angulares": MUESTRAS_ANGULO,
            "espectro": "fraccion de potencia sobre k>=1",
            "suavizado_m": SUAVIZADO_M,
        },
        "zonas": zonas,
    }
    args.informe.write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for n, z in zonas.items():
        print(n)
        print("  orto  ", {k: round(v * 100, 1) for k, v in z["espectro_ortoimagen"].items()})
        print("  modelo", {k: round(v * 100, 1) for k, v in z["espectro_modelo"].items()})
        z["control"] = z["control_cupulines_oscuros"]["correlacion_suavizada"]
        for clase in ("correlacion_cruda", "correlacion_suavizada", "control"):
            c = z.pop(clase) if clase == "control" else z[clase]
            print(f"  {clase}: sin giro {c['sin_giro']:.3f}  max {c['maxima']:.3f} "
                  f"en {c['giro_del_maximo_grados']} grados  media con giro {c['media_con_giro']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
