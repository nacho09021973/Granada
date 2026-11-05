#!/usr/bin/env python3
"""Modela los siete prismas de Jones y Goury y los renderiza en fila.

Salidas:
- `renders/piezas_alfabeto.obj`: las siete piezas, un grupo por tipo, en fila;
- `renders/piezas_alfabeto.png`: dos filas, vista frontal en tres cuartos
  (como el grabado) y vista desde abajo (como se ven en la cupula).

Se compara a ojo con la fig. 5 del articulo de Gamiz Gordo y Ferrer (pagina 15
del PDF). La geometria y sus supuestos estan en `granada/piezas.py`.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.piezas import TIPOS, NIVELES, escribir_obj, malla, pieza  # noqa: E402

SEPARACION = 2.1
YESO = np.array([238, 228, 210], dtype=float)
FONDO_ARRIBA = np.array([46, 42, 40], dtype=float)
FONDO_ABAJO = np.array([20, 19, 20], dtype=float)


def camara(azim: float, elev: float):
    """Base ortonormal de una camara que mira al origen desde (azim, elev)."""
    a, e = math.radians(azim), math.radians(elev)
    hacia = np.array([math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)])
    derecha = np.cross(hacia, np.array([0.0, 0.0, 1.0]))
    derecha /= np.linalg.norm(derecha)
    arriba = np.cross(derecha, hacia)
    return derecha, arriba, hacia


def rasterizar(V, F, W, H, azim, elev, luces):
    """Proyeccion ortografica con z-buffer y sombreado lambertiano por cara."""
    V = np.asarray(V, dtype=float)
    F = np.asarray(F, dtype=int)
    der, arr, hac = camara(azim, elev)
    sx, sy, prof = V @ der, V @ arr, V @ hac
    margen = 0.06
    xmin, xmax, ymin, ymax = sx.min(), sx.max(), sy.min(), sy.max()
    escala = min(W * (1 - 2 * margen) / (xmax - xmin), H * (1 - 2 * margen) / (ymax - ymin))
    px = (sx - (xmin + xmax) / 2) * escala + W / 2
    py = H / 2 - (sy - (ymin + ymax) / 2) * escala

    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    n = np.cross(b - a, c - a)
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    hacia_camara = n @ hac
    n[hacia_camara < 0] *= -1  # dos caras: sombrea la cara que mira a la camara
    luz = np.full(len(F), 0.32)
    for direccion, intensidad in luces:
        d = np.asarray(direccion, dtype=float)
        d /= np.linalg.norm(d)
        luz += intensidad * np.clip(n @ d, 0, None)
    color = np.clip(YESO[None, :] * luz[:, None], 0, 255)

    zbuf = np.full((H, W), -np.inf)
    img = np.zeros((H, W, 3))
    t = np.linspace(0, 1, H)[:, None, None]
    img[:] = FONDO_ARRIBA * (1 - t) + FONDO_ABAJO * t
    for k in range(len(F)):
        i0, i1, i2 = F[k]
        x0, y0, x1, y1, x2, y2 = px[i0], py[i0], px[i1], py[i1], px[i2], py[i2]
        bx0, bx1 = int(max(0, math.floor(min(x0, x1, x2)))), int(min(W - 1, math.ceil(max(x0, x1, x2))))
        by0, by1 = int(max(0, math.floor(min(y0, y1, y2)))), int(min(H - 1, math.ceil(max(y0, y1, y2))))
        if bx0 > bx1 or by0 > by1:
            continue
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-12:
            continue
        gx, gy = np.meshgrid(np.arange(bx0, bx1 + 1) + 0.5, np.arange(by0, by1 + 1) + 0.5)
        l0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / den
        l1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / den
        l2 = 1 - l0 - l1
        dentro = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if not dentro.any():
            continue
        z = l0 * prof[i0] + l1 * prof[i1] + l2 * prof[i2]
        sub = zbuf[by0 : by1 + 1, bx0 : bx1 + 1]
        gana = dentro & (z > sub)
        sub[gana] = z[gana]
        img[by0 : by1 + 1, bx0 : bx1 + 1][gana] = color[k]
    return Image.fromarray(img.astype(np.uint8)), (px, py)


def construir():
    grupos, Vt, Ft = [], [], []
    for k, tipo in enumerate(TIPOS):
        V, F = malla(pieza(tipo))
        dx = (k - (len(TIPOS) - 1) / 2) * SEPARACION
        V = [(x + dx, y, z) for x, y, z in V]
        grupos.append((tipo, V, F))
        base = len(Vt)
        Vt.extend(V)
        Ft.extend((a + base, b + base, c + base) for a, b, c in F)
    return grupos, Vt, Ft


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ancho", type=int, default=1800)
    ap.add_argument("--obj", type=Path, default=RAIZ / "renders" / "piezas_alfabeto.obj")
    ap.add_argument("--png", type=Path, default=RAIZ / "renders" / "piezas_alfabeto.png")
    args = ap.parse_args()

    grupos, V, F = construir()
    escribir_obj(args.obj, grupos)

    W = args.ancho
    H = W * 2 // 5
    luces = [((-0.6, 0.8, 0.5), 0.7), ((0.7, 0.5, -0.4), 0.3)]
    frontal, _ = rasterizar(V, F, W, H, azim=-18.0, elev=14.0, luces=luces)
    luces_abajo = [((-0.5, 0.6, -0.7), 0.7), ((0.6, 0.3, -0.6), 0.3)]
    abajo, _ = rasterizar(V, F, W, H, azim=-10.0, elev=-62.0, luces=luces_abajo)

    lienzo = Image.new("RGB", (W, 2 * H + 40), (20, 19, 20))
    lienzo.paste(frontal, (0, 0))
    lienzo.paste(abajo, (0, H + 40))
    dibujo = ImageDraw.Draw(lienzo)
    try:
        fuente = ImageFont.truetype("DejaVuSans.ttf", 26)
        pequena = ImageFont.truetype("DejaVuSans.ttf", 18)
    except OSError:
        fuente = pequena = ImageFont.load_default()
    for k, tipo in enumerate(TIPOS):
        cx = int(W * (0.06 + 0.88 * (k + 0.5) / len(TIPOS)))
        dibujo.text((cx, H + 8), tipo, fill=(230, 220, 200), font=fuente, anchor="mt")
        etiqueta = "2 niveles" if NIVELES[tipo] == 2 else "1 nivel"
        dibujo.text((cx, 2 * H + 30), etiqueta, fill=(150, 145, 135), font=pequena, anchor="mb")
    args.png.parent.mkdir(parents=True, exist_ok=True)
    lienzo.save(args.png)
    print(f"{len(V)} vertices, {len(F)} triangulos -> {args.obj.name}, {args.png.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
