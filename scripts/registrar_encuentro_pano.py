"""Registra el intradós del OBJ en el fondo del paño 00, en metros.

Blender -b --python-exit-code 1 -P scripts/registrar_encuentro_pano.py
No modifica el OBJ ni el GLB. Conserva las muestras y hashes en datos/.
"""

import hashlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from hiladas_ventanas import FONDO_M, SUPERIOR, EJE_PX


def main():
    obj = ROOT / "renders/previas/cupula_campo_vigente_1400.obj"
    auditoria = json.loads((ROOT / "datos/auditoria_geometria_obj.json").read_text())
    assert hashlib.sha256(obj.read_bytes()).hexdigest() == auditoria["sha256_obj"]
    escala = auditoria["cateto_m"]
    alzado = json.loads((ROOT / "datos/alzado_sala.json").read_text())
    px_m = alzado["px_por_m"]
    origen = alzado["niveles"]["arranque_cupula"]["fila_px"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=str(obj), forward_axis="Y", up_axis="Z", use_split_groups=True)
    for o in bpy.context.selected_objects:
        o.matrix_world = Matrix.Scale(escala, 4) @ o.matrix_world
    bpy.context.view_layer.update()
    tambor = bpy.data.objects["tambor"]
    apa = max((tambor.matrix_world @ v.co).x for v in tambor.data.vertices)
    # Solo campo: excluir la chapa de la cornisa y los muros de presentación.
    vertices, caras = [], []
    for o in bpy.context.scene.objects:
        if o.name.startswith(("hilada", "cupulilla", "cupulin", "corona_arranque")):
            inicio = len(vertices)
            vertices.extend(o.matrix_world @ v.co for v in o.data.vertices)
            caras.extend(tuple(inicio + i for i in p.vertices) for p in o.data.polygons)
    arbol = BVHTree.FromPolygons(vertices, caras, all_triangles=True)
    filas = []
    for _, eje, fila in SUPERIOR:
        u = (eje - EJE_PX) / px_m
        x = apa - FONDO_M[-1]
        y = u * x / apa
        p, _, _, _ = arbol.ray_cast(Vector((x, y, -2)), Vector((0, 0, 1)), 8)
        z = (origen - fila) / px_m
        filas.append(dict(eje_px=eje, fila_px=fila, xy_m=[x, y],
                          cresta_seccion_m=z,
                          intrados_campo_m=float(p.z) if p else None,
                          margen_m=float(p.z) - z if p else None))
    resultado = dict(
        procedencia="Lecturas de 0036 y primer impacto vertical del OBJ auditado; no medición nueva",
        sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [obj, ROOT / "datos/alzado_sala.json", ROOT / "scripts/hiladas_ventanas.py",
                          Path(__file__)]},
        apotema_m=apa, fondo_m=FONDO_M[-1], muestras=filas,
    )
    salida = ROOT / "datos/registro_encuentro_pano.json"
    salida.write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + "\n")
    for f in filas:
        print(f)


if __name__ == "__main__":
    main()
