"""Blender en CPU. Detalle del marco, desde el visitante, antes y después."""
from pathlib import Path
import sys, math, json
import numpy as np
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from auditar_geometria_obj import cargar, OUT
from render_cycles import camara, VISTAS

bpy.ops.wm.read_factory_settings(use_empty=True)
_,grupos,indices,V,F=cargar()
piloto=np.load(OUT/"piloto_asiento.npz")
ids=np.unique(F[indices==grupos.index("cupulin_00")])
assert np.allclose(V[ids],piloto["original"],atol=1e-6,rtol=0)
V[ids]=piloto["v"]
centro=Vector(piloto["centro"])
def malla(nombre,v,f):
    usados,local=np.unique(f,return_inverse=True)
    mesh=bpy.data.meshes.new(nombre)
    mesh.from_pydata(v[usados].tolist(),[],local.reshape(-1,3).tolist())
    obj=bpy.data.objects.new(nombre,mesh)
    bpy.context.collection.objects.link(obj)
    return obj
# Retener el entorno para las sombras y la silueta.
cerca=np.linalg.norm(V-np.array(centro),axis=1)<12
malla("Entorno",V,F[cerca[F].any(axis=1)])
p=np.load(OUT/"piezas_recortadas_00.npz")
extra=malla("Bordes conservados",p["v"],p["f"])
s=bpy.context.scene
s.render.engine="CYCLES"
s.cycles.samples=8
s.cycles.use_denoising=True
s.render.resolution_x=s.render.resolution_y=640
s.render.resolution_percentage=100
s.world=bpy.data.worlds.new("Ambiente")
s.world.color=(0.19,0.19,0.19)
pos,obj,fov=VISTAS["visitante"]
general=camara("visitante",pos,obj,fov)
bpy.context.view_layer.update()
xy=world_to_camera_view(s,general,centro)
(OUT/"marco_localizacion.json").write_text(json.dumps([xy.x,1-xy.y]))
s.camera=camara("detalle",pos,centro,math.degrees(2*math.atan(2.4/(centro-Vector(pos)).length)))
for lugar,potencia,tamano in [((-5,-6,-6),1800,5),((4,2,-8),460,5)]:
    luz=bpy.data.lights.new("Luz","AREA")
    luz.energy=potencia
    luz.shape="DISK"
    luz.size=tamano
    o=bpy.data.objects.new("Luz",luz)
    bpy.context.collection.objects.link(o)
    o.location=centro+Vector(lugar)
    o.rotation_euler=(centro-o.location).to_track_quat("-Z","Y").to_euler()
for nombre in ["antes","despues"]:
    extra.hide_render=nombre=="antes"
    s.render.filepath=str(OUT/f"marco_yeso_{nombre}.png")
    bpy.ops.render.render(write_still=True)
