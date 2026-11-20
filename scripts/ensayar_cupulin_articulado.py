"""Piloto local. Blender -b -t 2 --python-exit-code 1 -P scripts/ensayar_cupulin_articulado.py"""
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auditar_geometria_obj import cargar, OUT
from render_cycles import camara, VISTAS


def malla(nombre, puntos, caras):
    mesh = bpy.data.meshes.new(nombre)
    mesh.from_pydata(np.asarray(puntos).tolist(), [], np.asarray(caras).tolist())
    obj = bpy.data.objects.new(nombre, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def transicion(piloto):
    # Boca intersectada con el campo. Se reutiliza el perímetro exterior
    # del marco de la prueba anterior y se construye hacia dentro.
    n = 96
    base, techo = piloto[:2*n:2], piloto[1:2*n:2]
    eje = techo[0]-base[0]
    eje /= np.linalg.norm(eje)
    exterior = piloto[-2*n+1::2]
    centro = (base[0]+base[n//2])/2
    radial = base-centro
    radial -= np.outer(radial@eje,eje)
    altura = (base-centro)@eje
    phi = np.arange(n)*2*math.pi/n
    avance = np.mean((techo-base)@eje)
    # Dos registros de nichos. Cada uno tiene arranques, concavidad y
    # remate; el segundo alterna apoyos respecto del primero.
    anillos = [exterior, base]
    for fila,(r1,r2,z1,z2) in enumerate([(0.98,0.80,0.,0.30),(0.80,0.63,0.30,0.62)]):
        fase = ((np.arange(n)+fila*6)%12)/12
        arco = np.sqrt(np.maximum(0,1-(2*fase-1)**2))
        for t in (0.18,0.42,0.70,1.):
            radio = r1+(r2-r1)*t + 0.10*np.sin(math.pi*t)*arco
            z = (1-(z1+(z2-z1)*t))*altura + avance*(z1+(z2-z1)*t)
            z += 0.23*np.sin(math.pi*t)*arco
            anillos.append(centro+radial*radio[:,None]+np.outer(z,eje))
    # Casquete facetado y estrella de dos cuadrados en el techo.
    direc = radial/np.linalg.norm(radial,axis=1)[:,None]
    r = np.median(np.linalg.norm(radial,axis=1))
    ang = np.mod(phi,math.pi/4)
    estrella = 0.45*r*math.cos(math.pi/4)/np.cos(math.pi/4-np.minimum(ang, math.pi/4-ang))
    for escala, z in [(1.,0.81),(0.91,0.90),(0.42,0.99)]:
        anillos.append(centro+direc*(estrella*escala)[:,None]+avance*z*eje)
    pts = np.vstack([*anillos,centro+avance*1.02*eje])
    faces = []
    for k in range(len(anillos)-1):
        for i in range(n):
            a,b=k*n+i,k*n+(i+1)%n
            faces.extend([(a,b,b+n),(a,b+n,a+n)])
    last=(len(anillos)-1)*n
    faces.extend((last+i,last+(i+1)%n,len(pts)-1) for i in range(n))
    return malla("Dos registros y estrella",pts,faces)


bpy.ops.wm.read_factory_settings(use_empty=True)
_,grupos,indices,V,F=cargar()
p=np.load(OUT/"piloto_asiento.npz")
m=indices==grupos.index("cupulin_00")
ids=np.unique(F[m])
assert np.allclose(V[ids],p["original"],atol=1e-6,rtol=0)

viejo=malla("Piloto de referencia",p["v"],np.searchsorted(ids,F[m]))
recortes=np.load(OUT/"piezas_recortadas_00.npz")
from corona_piloto import dos_filas
todas_v=np.vstack([V,recortes["v"]])
todas_f=np.vstack([F[~m],recortes["f"]+len(V)])
corona, sustituidas, sel=dos_filas(todas_v,todas_f,p["v"])
malla("Hiladas fuera del piloto",todas_v,todas_f[~sel])
vecinas=malla("Hiladas originales del entorno",todas_v,todas_f[sel])
nuevas=malla("Hiladas recortadas del entorno",*sustituidas)
cinturon=malla("Dos filas de encuentro",*corona)
nuevo=transicion(p["v"])
s=bpy.context.scene
s.render.engine="CYCLES"
s.cycles.samples=12
s.cycles.use_denoising=True
s.render.resolution_percentage=100
s.world=bpy.data.worlds.new("Ambiente")
s.world.color=(0.10,0.10,0.10)
centro=Vector(p["centro"])
pos,obj,fov=VISTAS["visitante"]
general=camara("visitante",pos,obj,fov)
detalle=camara("Detalle",pos,centro,math.degrees(2*math.atan(2.65/(centro-Vector(pos)).length)))
orto=camara("Planta",centro-Vector((0,0,20)),centro,20)
orto.data.type="ORTHO"
orto.data.ortho_scale=5.6
orto.rotation_euler=(math.pi,0,0)
orto.rotation_mode="XYZ"
# XY como en la ortoimagen: arriba = +Y, derecha = +X exige
# reflexión horizontal al observar desde abajo (en la lámina).
for delta,power,size in [((-8,-6,-8),1500,4),((6,3,-7),380,5)]:
    luz=bpy.data.lights.new("Luz","AREA")
    luz.energy=power
    luz.shape="DISK"
    luz.size=size
    o=bpy.data.objects.new("Luz",luz)
    bpy.context.collection.objects.link(o)
    o.location=centro+Vector(delta)
    o.rotation_euler=(centro-o.location).to_track_quat("-Z","Y").to_euler()
for nombre,cam,lado in [("planta",orto,600),("detalle",detalle,620),("visitante",general,850)]:
    s.camera=cam
    s.render.resolution_x=s.render.resolution_y=lado
    for variante in ["actual","candidato"]:
        viejo.hide_render=variante=="candidato"
        nuevo.hide_render=variante=="actual"
        vecinas.hide_render=viejo.hide_render
        nuevas.hide_render=cinturon.hide_render=nuevo.hide_render
        s.render.filepath=str(OUT/f"articulado_{nombre}_{variante}.png")
        bpy.ops.render.render(write_still=True)
