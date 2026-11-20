"""Audita el OBJ de las tres previas. Ejecutar con el Python de Blender.

Desde la raíz: blender -b -t 1 --python-exit-code 1 -P scripts/auditar_geometria_obj.py
La vista ortográfica y los rayos usan solo la cúpula, antes de modificadores.
"""

import hashlib
import json
import math
from pathlib import Path

import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "renders/previas"
OBJ = OUT / "cupula_campo_vigente_1400.obj"
metodo = json.loads((ROOT / "datos/niveles_aproximados.json").read_text())["metodo"]
# R2 en granada/piezas.py es sqrt(2)/2.
from sys import path

path.insert(0, str(ROOT))
# No importar scipy desde el Python de Blender. Verificar la escala en el otro script.
from granada.piezas import R2

metro = metodo["paso_horizontal_hilada_m"] / R2


def cargar():
    vertices, caras, grupos, indices = [], [], [], []
    grupo = None
    with OBJ.open() as fuente:
        for line in fuente:
            if line.startswith("g "):
                grupo = line.split()[1]
                if grupo == "tambor":
                    break
                if not grupo.startswith(("hilada_", "cupulin_", "cupulilla_")):
                    raise ValueError(grupo)
                grupos.append(grupo)
            elif line.startswith("v "):
                vertices.append(tuple(map(float, line.split()[1:])))
            elif line.startswith("f "):
                caras.append(tuple(int(p) - 1 for p in line.split()[1:]))
                indices.append(len(grupos) - 1)
    arbol = BVHTree.FromPolygons(vertices, caras, all_triangles=True)
    return arbol, grupos, np.array(indices), np.array(vertices), np.asarray(caras)


def tono(normal):
    k = 1 if normal.z <= 0 else -1
    luz = k * (0.48 * normal.x + 0.36 * normal.y - 0.8 * normal.z)
    return round(75 + 165 * max(0, min(1, luz)))


def main():
    arbol, grupos, indices, vertices, caras = cargar()
    n, ancho = 640, 8.5
    xy = ((np.arange(n) + 0.5) / n - 0.5) * ancho / metro
    dx = xy[1] - xy[0]
    gris = np.empty((n, n), dtype=np.uint8)
    categorias = sorted({g.split("_")[0] for g in grupos})
    lut = [categorias.index(g.split("_")[0]) for g in grupos]
    zona = np.full((n, n), -1)
    cotas = np.full((n, n), np.nan)
    for fila, y in enumerate(xy[::-1]):
        for col, x in enumerate(xy):
            p, normal, cara, _ = arbol.ray_cast((x, y, -2), (0, 0, 1))
            if p is None:
                gris[fila, col] = 15
                continue
            zona[fila, col] = lut[indices[cara]]
            cotas[fila, col] = p.z * metro
            # Orientar la normal hacia el observador; una sola luz oblicua fija.
            gris[fila, col] = tono(normal)
    (OUT / "auditoria_relieve.pgm").write_bytes(
        f"P5\n{n} {n}\n255\n".encode() + gris.tobytes()
    )
    regiones = {
        "clave": (0, 0, 1.65),
        "hiladas": (1.65, 0, 1.65),
        "cupulin": (3.13, 0.59, 1.25),
    }
    for nombre, (cx, cy, lado) in regiones.items():
        pixel = (np.arange(316) + 0.5) / 316 - 0.5
        detalle = np.full((316, 316), 15, np.uint8)
        for i, y in enumerate((cy - pixel * lado) / metro):
            for j, x in enumerate((cx + pixel * lado) / metro):
                p, normal, _, _ = arbol.ray_cast((x, y, -2), (0, 0, 1))
                if p is not None:
                    detalle[i, j] = tono(normal)
        (OUT / f"auditoria_detalle_{nombre}.pgm").write_bytes(
            b"P5\n316 316\n255\n" + detalle.tobytes()
        )
    X, Y = np.meshgrid(xy, xy[::-1])
    # Disco interior para que el tambor y el exterior no cuenten como abiertos.
    interior = np.hypot(X, Y) * metro < 3.35
    huecos = {}
    for paso in (1, 2):
        sub = interior[::paso, ::paso]
        fallos = zona[::paso, ::paso][sub] == -1
        huecos[str(paso)] = {
            "rayos": int(sub.sum()),
            "sin_impacto": int(fallos.sum()),
            "area_m2": float(fallos.sum() * (dx * metro * paso) ** 2),
        }
    # Contraste independiente sobre una submuestra: proyección baricéntrica
    # de los triángulos y primera z interpolada, sin consultar el árbol.
    tri = vertices[caras]
    lo, hi = tri.min(axis=1), tri.max(axis=1)
    control = {"rayos": 0, "sin_impacto": 0, "error_max_m": 0.0}
    for i in range(12, n, 31):
        for j in range(15, n, 29):
            if not interior[i, j]:
                continue
            x, y = X[i, j], Y[i, j]
            sub = tri[
                (lo[:, 0] <= x) & (hi[:, 0] >= x) & (lo[:, 1] <= y) & (hi[:, 1] >= y)
            ]
            a, b, c = sub.transpose(1, 0, 2)
            u, v = b - a, c - a
            det = u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]
            with np.errstate(divide="ignore", invalid="ignore"):
                t = ((x - a[:, 0]) * v[:, 1] - (y - a[:, 1]) * v[:, 0]) / det
                w = (u[:, 0] * (y - a[:, 1]) - u[:, 1] * (x - a[:, 0])) / det
                dentro = (t >= 0) & (w >= 0) & (t + w <= 1)
            assert bool(dentro.any()) == bool(np.isfinite(cotas[i, j]))
            control["rayos"] += 1
            if dentro.any():
                z = (
                    a[dentro, 2] + t[dentro] * u[dentro, 2] + w[dentro] * v[dentro, 2]
                ).min() * metro
                control["error_max_m"] = max(
                    control["error_max_m"], abs(float(z - cotas[i, j]))
                )
            else:
                control["sin_impacto"] += 1
    cortes = []
    for r in np.arange(0, 3.51, 0.1):
        fila = {"radio_m": round(float(r), 2)}
        for ang in (0, 22.5, 45, 90, 180, 270):
            a = math.radians(ang)
            p, _, cara, _ = arbol.ray_cast(
                (r * math.cos(a) / metro, r * math.sin(a) / metro, -2), (0, 0, 1)
            )
            fila[str(ang)] = (
                None if p is None else [round(p.z * metro, 4), grupos[indices[cara]]]
            )
        cortes.append(fila)
    res = {
        "obj": OBJ.name,
        "sha256_obj": hashlib.sha256(OBJ.read_bytes()).hexdigest(),
        "blender": bpy.app.version_string,
        "cateto_m": metro,
        "ancho_vista_m": ancho,
        "regiones_m": regiones,
        "lado_px": n,
        "radio_auditado_m": 3.35,
        "cobertura": huecos,
        "control_baricentrico": control,
        "grupos_por_tipo": {
            c: sum(g.startswith(c + "_") for g in grupos) for c in categorias
        },
        "maximo_vertices_m": float(vertices[:, 2].max() * metro),
        "maximo_visible_ortogonal_m": float(np.nanmax(cotas)),
        "cortes_radiales": cortes,
    }
    (ROOT / "datos/auditoria_geometria_obj.json").write_text(
        json.dumps(res, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
