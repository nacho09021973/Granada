"""Rasterizador minimo con z-buffer para mirar las mallas de piezas.

Proyeccion ortografica (orbita alrededor del conjunto) o en perspectiva (camara
puesta en un punto). Sombreado lambertiano por vertice, con normales suavizadas
solo entre caras que forman menos de `ANGULO_ARISTA` grados, de modo que las
superficies curvas salen continuas y las aristas vivas siguen vivas. Dos caras.
Solo numpy y Pillow.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image

YESO = np.array([238, 228, 210], dtype=float)
FONDO_ARRIBA = np.array([46, 42, 40], dtype=float)
FONDO_ABAJO = np.array([20, 19, 20], dtype=float)
AMBIENTE = 0.32
ANGULO_ARISTA = 35.0


def camara(azim: float, elev: float):
    """Base ortonormal de una camara que mira al origen desde (azim, elev)."""
    a, e = math.radians(azim), math.radians(elev)
    hacia = np.array([math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)])
    return _base(hacia)


def _base(hacia):
    """derecha, arriba, hacia; `hacia` apunta de la escena a la camara."""
    hacia = np.asarray(hacia, dtype=float)
    hacia = hacia / np.linalg.norm(hacia)
    eje = np.array([0.0, 0.0, 1.0])
    if abs(hacia @ eje) > 0.999:
        eje = np.array([0.0, 1.0, 0.0])
    derecha = np.cross(hacia, eje)
    derecha /= np.linalg.norm(derecha)
    arriba = np.cross(derecha, hacia)
    return derecha, arriba, hacia


def normales_suaves(V, F, angulo=ANGULO_ARISTA):
    """Normal por esquina de triangulo: media de las caras vecinas casi coplanarias."""
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    bruta = np.cross(b - a, c - a)  # longitud = 2 * area: pondera por area
    unidad = bruta / (np.linalg.norm(bruta, axis=1, keepdims=True) + 1e-12)
    umbral = math.cos(math.radians(angulo))
    esquinas = np.repeat(unidad[:, None, :], 3, axis=1).copy()
    vertice = F.reshape(-1)
    cara = np.repeat(np.arange(len(F)), 3)
    orden = np.argsort(vertice, kind="stable")
    vertice, cara = vertice[orden], cara[orden]
    cortes = np.flatnonzero(np.diff(vertice)) + 1
    for grupo in np.split(np.arange(len(vertice)), cortes):
        caras = cara[grupo]
        if len(caras) < 2:
            continue
        u = unidad[caras]
        cerca = (u @ u.T) > umbral
        suma = cerca.astype(float) @ bruta[caras]
        suma /= np.linalg.norm(suma, axis=1, keepdims=True) + 1e-12
        v = vertice[grupo[0]]
        for k, f in enumerate(caras):
            esquinas[f, list(F[f]).index(v)] = suma[k]
    return unidad, esquinas


def rasterizar(V, F, W, H, azim=0.0, elev=0.0, luces=(), perspectiva=None, suave=True):
    """Dibuja la malla y devuelve (imagen, (px, py)).

    Sin `perspectiva`: ortografica, encuadrando todo, vista desde (azim, elev).
    Con `perspectiva=(posicion, objetivo, fov_horizontal_grados)`: camara en
    `posicion` mirando a `objetivo`.
    """
    V = np.asarray(V, dtype=float)
    F = np.asarray(F, dtype=int)
    if perspectiva is None:
        der, arr, hac = camara(azim, elev)
        sx, sy, prof = V @ der, V @ arr, V @ hac
        margen = 0.06
        xmin, xmax, ymin, ymax = sx.min(), sx.max(), sy.min(), sy.max()
        escala = min(W * (1 - 2 * margen) / (xmax - xmin), H * (1 - 2 * margen) / (ymax - ymin))
        px = (sx - (xmin + xmax) / 2) * escala + W / 2
        py = H / 2 - (sy - (ymin + ymax) / 2) * escala
        visible = np.ones(len(F), dtype=bool)
        hacia_ojo = np.broadcast_to(hac, (len(F), 3))
    else:
        posicion, objetivo, fov = perspectiva
        posicion = np.asarray(posicion, dtype=float)
        der, arr, hac = _base(posicion - np.asarray(objetivo, dtype=float))
        d = V - posicion
        zc = -(d @ hac)  # distancia por delante de la camara
        focal = (W / 2) / math.tan(math.radians(fov) / 2)
        cerca = 1e-3
        zseg = np.maximum(zc, cerca)
        px = W / 2 + focal * (d @ der) / zseg
        py = H / 2 - focal * (d @ arr) / zseg
        prof = 1.0 / zseg  # 1/z interpola bien en pantalla; mayor = mas cerca
        visible = (zc[F] > cerca).all(axis=1)
        centro = V[F].mean(axis=1)
        hacia_ojo = posicion - centro

    unidad, esquinas = normales_suaves(V, F) if suave else (None, None)
    if not suave:
        a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
        unidad = np.cross(b - a, c - a)
        unidad /= np.linalg.norm(unidad, axis=1, keepdims=True) + 1e-12
        esquinas = np.repeat(unidad[:, None, :], 3, axis=1)
    girar = np.einsum("ij,ij->i", unidad, hacia_ojo) < 0
    esquinas = np.where(girar[:, None, None], -esquinas, esquinas)
    luz = np.full(esquinas.shape[:2], AMBIENTE)
    for direccion, intensidad in luces:
        dl = np.asarray(direccion, dtype=float)
        dl /= np.linalg.norm(dl)
        luz += intensidad * np.clip(esquinas @ dl, 0, None)
    color = np.clip(YESO[None, None, :] * luz[:, :, None], 0, 255)

    zbuf = np.full((H, W), -np.inf)
    img = np.zeros((H, W, 3))
    t = np.linspace(0, 1, H)[:, None, None]
    img[:] = FONDO_ARRIBA * (1 - t) + FONDO_ABAJO * t
    for k in np.flatnonzero(visible):
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
        if not gana.any():
            continue
        sub[gana] = z[gana]
        c0, c1, c2 = color[k]
        pix = l0[gana, None] * c0 + l1[gana, None] * c1 + l2[gana, None] * c2
        img[by0 : by1 + 1, bx0 : bx1 + 1][gana] = pix
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)), (px, py)
