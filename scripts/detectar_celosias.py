"""Bordes de las celosías del tambor en una fotografía (paso 1 de 2).

Detecta las celosías iluminadas, el canto inferior que les tapa el alféizar
y sus bordes laterales rectos. La foto, los umbrales y la identificación de
los vanos vienen de un fichero de lecturas `datos/lecturas_<clave>.json`.
Escribe una lámina de control en `renders/previas/0041_<clave>/` y los bordes
en `datos/bordes_celosias_<clave>.json`. El paso 2 es
`scripts/medir_nicho_fotos.py`.

Las manchas se etiquetan con los puntos de `datos/lecturas_trip82.json`.

Uso: OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/detectar_celosias.py --lecturas datos/lecturas_trip82.json
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]

UMBRAL_TEXTURA = 18
UMBRAL_ROJO = 170
VENTANA_TEXTURA = 15
CIERRE = 9
RECORTE_LADO = 0.15
BUSQUEDA_PX = 25
MARGEN_ALFEIZAR = 20
ALTURA_RECTA = 0.40


def mascara_celosia(rgb, umbral_textura=UMBRAL_TEXTURA, umbral_rojo=UMBRAL_ROJO):
    """Celosía: zona clara con mucha varianza local (calados), no la pared lisa."""
    gris = rgb.astype(float).mean(2)
    media = ndimage.uniform_filter(gris, VENTANA_TEXTURA)
    var = ndimage.uniform_filter(gris**2, VENTANA_TEXTURA) - media**2
    rojo = ndimage.uniform_filter(rgb[..., 0].astype(float), VENTANA_TEXTURA)
    m = (np.sqrt(np.maximum(var, 0)) > umbral_textura) & (rojo > umbral_rojo)
    m = ndimage.binary_closing(m, structure=np.ones((CIERRE, CIERRE)), iterations=2)
    m = ndimage.binary_fill_holes(m)
    return ndimage.binary_opening(m, structure=np.ones((7, 7)))


def ajustar_recta(pts, rechazo=2.5, vueltas=3):
    """Recta total por mínimos cuadrados con rechazo de atípicos (k·RMS)."""
    pts = np.asarray(pts, float)
    sel = np.ones(len(pts), bool)
    for _ in range(vueltas):
        m = pts[sel].mean(0)
        _, _, vt = np.linalg.svd(pts[sel] - m)
        res = (pts - m) @ vt[1]
        rms = np.sqrt(np.mean(res[sel] ** 2))
        nuevo = np.abs(res) <= max(rechazo * rms, 0.5)
        if (nuevo == sel).all():
            break
        sel = nuevo
    return m, vt[0], res[sel]


def bordes_mancha(m, pendiente, gris):
    """Borde inferior (canto del alféizar) y laterales rectos de una celosía.

    El pie se aproxima con la máscara y se afina, columna a columna, en el
    máximo salto de claro (arriba) a oscuro (abajo). Los lados se recorren por
    filas de imagen, por encima del alféizar y por debajo del arranque del
    arco, y se afinan en el máximo del gradiente horizontal.
    """
    gy, gx = np.gradient(gris)
    ys, xs = np.nonzero(m)
    t0 = np.array([1.0, pendiente]) / np.hypot(1.0, pendiente)
    n0 = np.array([t0[1], -t0[0]])
    m0 = np.array([xs.mean(), ys.mean()])
    P = np.stack([xs, ys], 1).astype(float) - m0
    u, v = P @ t0, P @ n0
    ub = np.round(u).astype(int)
    umin, umax = ub.min(), ub.max()
    aprox = []
    for k in range(int(umin + 0.25 * (umax - umin)), int(umax - 0.25 * (umax - umin))):
        sel = ub == k
        if sel.any():
            aprox.append(m0 + k * t0 + v[sel].min() * n0)
    ma, ta, _ = ajustar_recta(aprox)
    pend = ta[1] / ta[0]
    # Afinado del pie por columnas de imagen.
    x0, x1 = xs.min(), xs.max()
    inf = []
    for x in range(int(x0 + RECORTE_LADO * (x1 - x0)), int(x1 - RECORTE_LADO * (x1 - x0))):
        yc = ma[1] + (x - ma[0]) * pend
        ya, yb = int(yc - BUSQUEDA_PX), int(yc + BUSQUEDA_PX)
        if ya < 1 or yb >= gris.shape[0] - 1:
            continue
        perfil = gy[ya:yb, x]
        k = int(np.argmin(perfil))  # claro arriba, oscuro abajo: dI/dy negativo
        if 0 < k < len(perfil) - 1:
            a_, b_, c_ = perfil[k - 1 : k + 2]
            den = a_ - 2 * b_ + c_
            k = k + (0.5 * (a_ - c_) / den if den != 0 else 0)
        inf.append((x, ya + k))
    mi, ti, _ = ajustar_recta(inf)
    pend = ti[1] / ti[0]

    def sobre_alfeizar(x, y):
        return mi[1] + (x - mi[0]) * pend - y

    # Lados: por filas de imagen.
    altura = max(sobre_alfeizar(x, y) for x, y in zip(xs[:: 50], ys[:: 50]))
    izq, der = [], []
    for y in range(int(ys.min()), int(ys.max()) + 1):
        fila = xs[ys == y]
        if len(fila) < 5:
            continue
        for lado, xe, signo in (("izq", fila.min(), 1), ("der", fila.max(), -1)):
            h = sobre_alfeizar(xe, y)
            if not (MARGEN_ALFEIZAR < h < ALTURA_RECTA * altura):
                continue
            xa, xb = int(xe - 10), int(xe + 10)
            perfil = gx[y, xa:xb] * signo  # oscuro fuera, claro dentro
            k = int(np.argmax(perfil))
            (izq if lado == "izq" else der).append((xa + k, y))
    out = {}
    for nombre, pts in (("inferior", inf), ("izquierdo", izq), ("derecho", der)):
        if len(pts) < 10:
            out[nombre] = None
            continue
        mm, tt, rr = ajustar_recta(pts)
        out[nombre] = dict(
            punto=mm.tolist(),
            direccion=tt.tolist(),
            n=len(pts),
            n_usados=len(rr),
            rms_px=float(np.sqrt(np.mean(rr**2))),
            puntos=np.asarray(pts, float)[:: max(1, len(pts) // 40)].round(1).tolist(),
        )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lecturas", type=Path, required=True)
    args = ap.parse_args()
    LECTURAS = args.lecturas if args.lecturas.is_absolute() else ROOT / args.lecturas
    lect = json.loads(LECTURAS.read_text())
    clave = lect["clave"]
    SALIDA = ROOT / f"datos/bordes_celosias_{clave}.json"
    PREVIAS = ROOT / f"renders/previas/0041_{clave}"
    umbrales = dict(umbral_textura=UMBRAL_TEXTURA, umbral_rojo=UMBRAL_ROJO) | lect.get("umbrales", {})
    foto = ROOT / lect["foto"]
    if hashlib.sha1(foto.read_bytes()).hexdigest() != lect["sha1"]:
        raise SystemExit("La foto no coincide con la lectura")
    rgb = np.asarray(Image.open(foto).convert("RGB"))
    m = mascara_celosia(rgb, **umbrales)
    gris = ndimage.gaussian_filter(rgb.astype(float).mean(2), 1.5)
    etiquetas, n = ndimage.label(m)
    vanos = {}
    for nombre, info in lect["vanos"].items():
        x, y = info["dentro"]
        e = etiquetas[y, x]
        if e == 0:
            raise SystemExit(f"{nombre}: el punto {x},{y} no cae en ninguna mancha")
        mm = etiquetas == e
        vanos[nombre] = dict(info, area_px=int(mm.sum()), bordes=bordes_mancha(mm, lect["pendiente_alfeizar"][info["cara"]], gris))
        b = vanos[nombre]["bordes"]
        print(nombre, mm.sum(), {k: (v["n_usados"], v["n"], round(v["rms_px"], 2)) if v else None for k, v in b.items()})

    PREVIAS.mkdir(parents=True, exist_ok=True)
    im = Image.fromarray(rgb).convert("RGB")
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).bitmap((0, 0), Image.fromarray((m * 255).astype(np.uint8)), fill=(0, 120, 255, 110))
    im = Image.alpha_composite(im.convert("RGBA"), capa).convert("RGB")
    d = ImageDraw.Draw(im)
    color = dict(inferior=(255, 0, 0), izquierdo=(0, 255, 0), derecho=(255, 0, 255))
    for nombre, v in vanos.items():
        for lado, b in v["bordes"].items():
            if b is None:
                continue
            p, t = np.array(b["punto"]), np.array(b["direccion"])
            L = 400 if lado == "inferior" else 250
            d.line([tuple(p - L * t), tuple(p + L * t)], fill=color[lado], width=2)
        d.text(tuple(np.array(v["dentro"]) + 10), nombre, fill=(255, 255, 0))
    im.save(PREVIAS / "bordes.jpg", quality=90)
    SALIDA.write_text(
        json.dumps(
            dict(
                foto=lect["foto"],
                clave=clave,
                lecturas=str(LECTURAS.relative_to(ROOT)),
                sha256_script=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                sha256_lecturas=hashlib.sha256(LECTURAS.read_bytes()).hexdigest(),
                umbrales=umbrales,
                vanos=vanos,
            ),
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
