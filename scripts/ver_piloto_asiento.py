"""Blender -b -t 1 --python-exit-code 1 -P scripts/ver_piloto_asiento.py"""

from pathlib import Path
import json, sys
import numpy as np
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auditar_geometria_obj import cargar, OUT, tono, ROOT
from mathutils import Vector

arbol, grupos, indices, vertices, caras = cargar()
grupo = grupos.index("cupulin_00")
ids = np.unique(caras[indices == grupo])
piloto = np.load(OUT / "piloto_asiento.npz")
assert np.allclose(vertices[ids], piloto["original"], atol=0.000001, rtol=0)
vertices[ids] = piloto["v"]
nuevo = BVHTree.FromPolygons(vertices, caras, all_triangles=True)
centro = piloto["centro"]
res = {"residuo_base_m": float(piloto["error_m"])}
recortar = "--recortar" in sys.argv
reponer = "--reponer" in sys.argv or recortar
if reponer:
    piezas = np.load(OUT / ("piezas_recortadas_00.npz" if recortar else "piezas_marco_00.npz"))
    con_piezas = BVHTree.FromPolygons(
        np.concatenate([vertices, piezas["v"]]),
        np.concatenate([caras, piezas["f"] + len(vertices)]), all_triangles=True)
    res["piezas_repuestas"] = int(piezas["piezas"])
fotos = []
for vista, cam in [("ortogonal", None), ("visitante", np.array([0.0, -6.0, -14.0]))]:
    direccion = np.array([0.0, 0.0, 1.0]) if cam is None else centro - cam
    direccion /= np.linalg.norm(direccion)
    u = np.cross([0, 1, 0], direccion)
    u /= np.linalg.norm(u)
    v = np.cross(direccion, u)
    n = 180
    ys, xs = np.mgrid[:n, :n]
    puntos = (
        centro
        + 5.5 * ((xs[..., None] + 0.5) / n - 0.5) * u
        - 5.5 * ((ys[..., None] + 0.5) / n - 0.5) * v
    )
    fila = []
    variantes = [("vigente", arbol), ("candidato", nuevo)]
    if reponer:
        variantes = [("piloto", nuevo), ("recortadas" if recortar else "repone_enteras", con_piezas)]
    for nombre, tree in variantes:
        img = np.full((n, n, 3), [120, 20, 50], dtype=np.uint8)
        fallos = visibles = 0
        for i, j in np.ndindex(n, n):
            p = puntos[i, j]
            origen = p - 50 * direccion if cam is None else cam
            hit, normal, k, _ = tree.ray_cast(
                Vector(origen), Vector(p - origen).normalized()
            )
            if hit is None:
                fallos += 1
            else:
                gris = tono(normal)
                img[i, j] = gris
                if k < len(indices) and indices[k] == grupo:
                    visibles += 1
                    img[i, j] = [gris // 2, gris, gris]
        res[vista + "_" + nombre] = {
            "rayos": n * n,
            "sin_impacto": fallos,
            "cupulin_visible": visibles,
        }
        fila.append(img)
    fotos.append(np.concatenate(fila, axis=1))
img = np.concatenate(fotos)
nombre_salida = "piloto_marco_entero" if reponer else "piloto_asiento"
if recortar:
    nombre_salida = "piloto_marco_recortado"
(OUT / (nombre_salida + ".ppm")).write_bytes(b"P6\n360 360\n255\n" + img.tobytes())
(ROOT / "datos" / (nombre_salida + ".json")).write_text(json.dumps(res, indent=2) + "\n")
