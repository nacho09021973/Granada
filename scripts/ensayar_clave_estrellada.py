"""Piloto local de clave, con Blender; no altera el OBJ de entrada.

blender -b -t 2 --python-exit-code 1 -P scripts/ensayar_clave_estrellada.py
Las cotas y el radio de la estrella son elecciones de ensayo.
"""
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from auditar_geometria_obj import cargar, OBJ, OUT, metro
from render_cycles import camara, VISTAS


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _, grupos, indices, v, f = cargar()
    seleccion = indices == grupos.index("cupulilla_25")
    ids = np.unique(f[seleccion])
    caras = np.searchsorted(ids, f[seleccion])
    original = v[ids].copy()
    aristas = Counter(tuple(sorted((int(a), int(b)))) for tri in caras
                      for a, b in zip(tri, np.roll(tri, -1)))
    borde = np.unique([ab for ab, n in aristas.items() if n == 1])
    xy = original[:, :2] * metro
    distancias = np.sqrt(((xy[:, None] - xy[borde][None]) ** 2).sum(axis=2))
    distancia = distancias.min(axis=1)
    cota_borde = original[borde[distancias.argmin(axis=1)], 2]*metro
    # Radio de una estrella poligonal de 16 vértices: ocho puntas.
    phi = np.mod(np.arctan2(xy[:, 1], xy[:, 0]), 2 * math.pi)
    sector = np.floor(phi / (math.pi / 8)).astype(int)
    a = sector * math.pi / 8
    b = a + math.pi / 8
    ra = np.where(sector % 2 == 0, 0.38, 0.29)
    rb = np.where(sector % 2 == 0, 0.29, 0.38)
    ax, ay, bx, by = ra*np.cos(a), ra*np.sin(a), rb*np.cos(b), rb*np.sin(b)
    radio = (ax*by-ay*bx) / (np.cos(phi)*(by-ay)-np.sin(phi)*(bx-ax))
    t = np.linalg.norm(xy, axis=1) / radio
    # Meseta central, dos quiebros y pendiente exterior. No son cotas medidas.
    perfil = np.interp(t, [0, .22, .30, .48, .57, .80, 1., 1.65],
                          [4.67, 4.67, 4.61, 4.61, 4.54, 4.54, 4.46, 4.40])
    peso = np.clip(distancia / .10, 0, 1)
    nuevo = original.copy()
    nuevo[:, 2] = (cota_borde*(1-peso) + perfil*peso)/metro
    nuevo[borde] = original[borde]
    assert np.array_equal(nuevo[borde], original[borde])
    assert np.array_equal(nuevo[:, :2], original[:, :2])
    print("Cotas borde y candidato:", original[borde, 2].max()*metro, nuevo[:, 2].max()*metro, flush=True)
    assert nuevo[:, 2].max()*metro <= 4.670001
    # Misma triangulación y planta: la cobertura vertical de este grupo es idéntica.
    np.savez(OUT / "clave_estrellada_piloto.npz", original=original, v=nuevo, f=caras, borde=borde)
    candidato = v.copy()
    candidato[ids] = nuevo
    centro = Vector((0, 0, 4.55/metro))
    pos, _, _ = VISTAS["visitante"]
    detalle = camara("Detalle", pos, centro, math.degrees(2*math.atan(3.5/(centro-Vector(pos)).length)))
    general = camara("Visitante", *VISTAS["visitante"])
    resultados = {}
    # Rayos desde la cámara, mismo encuadre, sin sala ni modificadores.
    direccion = (centro-Vector(pos)).normalized()
    derecha = direccion.cross(Vector((0, 0, 1))).normalized()
    arriba = derecha.cross(direccion).normalized()
    for nombre, puntos in [("actual", v), ("candidato", candidato)]:
        tree = BVHTree.FromPolygons(puntos, f, all_triangles=True)
        fallos = clave = 0
        for x in np.linspace(-3.5, 3.5, 100):
            for y in np.linspace(-3.5, 3.5, 100):
                rayo = (centro+float(x)*derecha+float(y)*arriba-Vector(pos)).normalized()
                hit, _, cara, _ = tree.ray_cast(Vector(pos), rayo)
                fallos += hit is None
                clave += hit is not None and bool(seleccion[cara])
        resultados[nombre] = dict(rayos=10000, sin_impacto=fallos, impactos_clave=clave)
    aceptable = resultados["candidato"]["sin_impacto"] <= resultados["actual"]["sin_impacto"]
    escena = bpy.context.scene
    escena.render.engine = "CYCLES"
    escena.cycles.samples = 16
    escena.cycles.use_denoising = True
    escena.render.resolution_x = escena.render.resolution_y = 560
    escena.view_settings.view_transform = "AgX"
    escena.world = bpy.data.worlds.new("Ambiente")
    escena.world.color = (.12, .12, .12)
    for lugar, potencia in [((-8, -10, -10), 1800), ((8, 3, -8), 600)]:
        luz = bpy.data.lights.new("Panel", "AREA")
        luz.energy, luz.size = potencia, 5
        o = bpy.data.objects.new("Panel", luz)
        bpy.context.collection.objects.link(o)
        o.location = lugar
        o.rotation_euler = (centro-o.location).to_track_quat("-Z", "Y").to_euler()
    material = bpy.data.materials.new("Yeso neutro de diagnóstico")
    material.diffuse_color = (.72, .69, .63, 1)
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (.72, .69, .63, 1)
    bsdf.inputs["Roughness"].default_value = .85
    mesh = bpy.data.meshes.new("Cupula")
    mesh.from_pydata(v.tolist(), [], f.tolist())
    objeto = bpy.data.objects.new("Cupula", mesh)
    bpy.context.collection.objects.link(objeto)
    objeto.data.materials.append(material)
    for variante, puntos in [("actual", v), ("candidato", candidato)]:
        mesh.vertices.foreach_set("co", puntos.ravel())
        mesh.update()
        for nombre, cam in [("detalle", detalle), ("visitante", general)]:
            escena.camera = cam
            escena.render.filepath = str(OUT / f"clave_{nombre}_{variante}.png")
            bpy.ops.render.render(write_still=True)
    salida = dict(sha256_obj=hashlib.sha256(OBJ.read_bytes()).hexdigest(),
                  script="scripts/ensayar_clave_estrellada.py", blender=bpy.app.version_string,
                  objetivo_m=4.67, maximo_candidato_m=float(nuevo[:, 2].max()*metro),
                  vertices_borde_conservados=len(borde), cobertura_vertical="idéntica por planta y caras conservadas",
                  visitante=resultados, cumple_no_aumentar_rayos_perdidos=aceptable,
                  alcance="Piloto supuesto; falta comparación con sección y validación visual. Sin promoción.")
    (ROOT / "datos/piloto_clave_estrellada.json").write_text(json.dumps(salida, indent=2, ensure_ascii=False)+"\n")


if __name__ == "__main__":
    main()
