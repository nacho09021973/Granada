"""Blender: diferencia de las piezas del piloto con el prisma de la boca."""
from pathlib import Path
import bpy
import bmesh
import numpy as np

out = Path(__file__).resolve().parents[1] / "renders/previas"
piezas = np.load(out / "piezas_marco_00.npz")
borde = np.load(out / "piloto_asiento.npz")["v"]
base, techo = borde[:192:2], borde[1:192:2]
eje = techo[0] - base[0]
eje /= np.linalg.norm(eje)
# Proyección sobre el plano perpendicular al eje del pozo. Las tapas del
# cortador se sitúan fuera de todas las piezas.
anillo = base - np.outer(base @ eje, eje)
alturas = piezas["v"] @ eje
n = len(anillo)
verts = np.vstack([anillo + eje*(alturas.min()-1), anillo + eje*(alturas.max()+1)])
caras = [tuple(reversed(range(n))),tuple(range(n,2*n))]
caras.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))

def objeto(nombre, vertices, caras):
    m = bpy.data.meshes.new(nombre)
    m.from_pydata(vertices.tolist(), [], [tuple(f) for f in caras])
    bm = bmesh.new()
    bm.from_mesh(m)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-8)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if any(not edge.is_manifold for edge in bm.edges):
        raise ValueError(f"Malla abierta: {nombre}")
    bm.to_mesh(m)
    bm.free()
    obj = bpy.data.objects.new(nombre,m)
    bpy.context.collection.objects.link(obj)
    return obj

cortador = objeto("prisma",verts,caras)
vv,ff=[],[]
inicio=0
for j,cantidad in enumerate(piezas["longitudes"]):
    fin=inicio+cantidad
    fs=piezas["f"]
    fs=fs[(fs[:,0]>=inicio)&(fs[:,0]<fin)]-inicio
    pieza=objeto(str(j),piezas["v"][inicio:fin],fs)
    mod=pieza.modifiers.new("boca","BOOLEAN")
    mod.operation="DIFFERENCE"
    mod.solver="EXACT"
    mod.object=cortador
    evaluado=pieza.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluado.to_mesh()
    mesh.calc_loop_triangles()
    ff.extend(tuple(len(vv)+i for i in tri.vertices) for tri in mesh.loop_triangles)
    vv.extend(tuple(v.co) for v in mesh.vertices)
    evaluado.to_mesh_clear()
    inicio=fin
assert inicio==len(piezas["v"]) and ff
np.savez(out/"piezas_recortadas_00.npz",v=vv,f=ff,piezas=piezas["piezas"])
