"""Render fisico de la cupula por piezas con Blender Cycles.

Uso (Blender 4.2, sin ventana):

    ~/.local/opt/blender/blender -b -P scripts/render_cycles.py -- \
        [--muestras 128] [--lado 1400] [--vistas visitante,cenital]

Entrada: `renders/cupula_piezas.obj` y `.mtl`, que escribe
`scripts/render_cupula_piezas.py` (el .obj esta en .gitignore: regenerarlo
antes si cambio la malla). Salida: `renders/cupula_cycles_<vista>.png`, una
imagen por vista.

Que es dato y que es escena
---------------------------
La malla y sus colores son los del modelo (`granada/cupula.py`,
`granada/color.py`). Todo lo demas es escena, eleccion estetica y no dato:
- la sala bajo el tambor (muros que prolongan su contorno y suelo);
- 16 ventanas en el tambor, dos por lado del octogono, como en la sala real,
  pero con posicion y tamano a ojo; la luz entra solo por ellas;
- los materiales: grano del yeso, translucidez, rugosidad, oro metalico.
El escalon de sombra pintada de cada material del .mtl (`color_k`) se
descarta: aqui la sombra la calcula la luz.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

RAIZ = Path(__file__).resolve().parents[1]
OBJ = RAIZ / "renders" / "cupula_piezas.obj"

# Mismas camaras que el render rasterizado (scripts/render_cupula_piezas.py):
# (posicion, objetivo, campo horizontal en grados), en unidades del cateto.
VISTAS = {
    "visitante": ((0.0, -6.0, -14.0), (0.0, 4.0, 9.0), 80.0),
    "cenital": ((0.0, 0.0, -13.0), (0.0, 0.001, 10.0), 90.0),
}

SUELO = -24.0
"""Cota del suelo de la sala (el tambor baja hasta -6)."""

VENTANA_ANCHO = 1.7
VENTANA_ALTO = 3.2
VENTANA_CENTRO_Z = -3.6
VENTANA_SEPARACION = 2.6
"""Ventanas: medidas a ojo, en unidades del cateto (0,22 m)."""

LUZ_VENTANA_W = 300.0
"""Potencia de la luz de area tras cada ventana (W de Blender): luz de relleno."""

SOL_LADO = 5
"""Lado del octogono por cuyas ventanas entra el sol (0 = +x, sentido antihorario)."""
SOL_W = 9000.0
SOL_ELEVACION = 30.0
SOL_ABERTURA = 22.0
"""Haces de sol: focos en las ventanas de ese lado y la contigua, que suben
rasantes hacia el lado opuesto de la cupula; potencia, elevacion y abertura
en grados, a ojo."""
COLOR_SOL = (1.0, 0.80, 0.58)

COLOR_LUZ = (1.0, 0.93, 0.84)
"""Luz de dia calida, rebotada en el patio."""


def argumentos():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--muestras", type=int, default=128)
    ap.add_argument("--lado", type=int, default=1400)
    ap.add_argument("--vistas", default="visitante,cenital")
    ap.add_argument("--salida", type=Path, default=RAIZ / "renders")
    ap.add_argument("--sufijo", default="")
    return ap.parse_args(argv)


def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def colores_del_mtl(ruta: Path) -> dict[str, tuple[float, float, float]]:
    """Color base de cada familia: el escalon 0 (sin sombra) de `color_k`."""
    fuera, nombre = {}, None
    for linea in ruta.read_text().splitlines():
        partes = linea.split()
        if not partes:
            continue
        if partes[0] == "newmtl":
            nombre = partes[1]
        elif partes[0] == "Kd" and nombre and nombre.endswith("_0"):
            fuera[nombre[:-2]] = tuple(float(v) for v in partes[1:4])
    return fuera


def _srgb_a_lineal(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def material_yeso(nombre: str, color, rugosidad=0.85, grano=0.25, translucidez=0.04, variacion=0.06):
    """Yeso (o pigmento sobre yeso): grano en relieve y leve variacion de tono."""
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    lin = [_srgb_a_lineal(c) for c in color]
    # Variacion de tono: ruido grande que mezcla el color con uno algo mas oscuro.
    ruido = nt.nodes.new("ShaderNodeTexNoise")
    ruido.inputs["Scale"].default_value = 0.35
    ruido.inputs["Detail"].default_value = 4.0
    mezcla = nt.nodes.new("ShaderNodeMix")
    mezcla.data_type = "RGBA"
    mezcla.inputs["A"].default_value = (*lin, 1.0)
    mezcla.inputs["B"].default_value = (*[c * (1 - 3 * variacion) for c in lin], 1.0)
    rampa = nt.nodes.new("ShaderNodeMapRange")
    rampa.inputs["From Min"].default_value = 0.35
    rampa.inputs["From Max"].default_value = 0.75
    rampa.inputs["To Max"].default_value = 0.35
    nt.links.new(ruido.outputs["Fac"], rampa.inputs["Value"])
    nt.links.new(rampa.outputs["Result"], mezcla.inputs["Factor"])
    nt.links.new(mezcla.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rugosidad
    bsdf.inputs["Subsurface Weight"].default_value = translucidez
    bsdf.inputs["Subsurface Radius"].default_value = (0.08, 0.06, 0.04)
    # Grano: ruido fino en relieve.
    fino = nt.nodes.new("ShaderNodeTexNoise")
    fino.inputs["Scale"].default_value = 28.0
    fino.inputs["Detail"].default_value = 8.0
    fino.inputs["Roughness"].default_value = 0.65
    relieve = nt.nodes.new("ShaderNodeBump")
    relieve.inputs["Strength"].default_value = grano
    relieve.inputs["Distance"].default_value = 0.02
    nt.links.new(fino.outputs["Fac"], relieve.inputs["Height"])
    nt.links.new(relieve.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def material_oro(color):
    m = bpy.data.materials.new("oro")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    lin = [_srgb_a_lineal(c) for c in color]
    bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.32
    fino = nt.nodes.new("ShaderNodeTexNoise")
    fino.inputs["Scale"].default_value = 40.0
    fino.inputs["Detail"].default_value = 6.0
    relieve = nt.nodes.new("ShaderNodeBump")
    relieve.inputs["Strength"].default_value = 0.12
    relieve.inputs["Distance"].default_value = 0.01
    nt.links.new(fino.outputs["Fac"], relieve.inputs["Height"])
    nt.links.new(relieve.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def material_ventana():
    """Se ve blanca desde la camara; no ilumina (eso lo hacen las luces de area)."""
    m = bpy.data.materials.new("ventana")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    salida = nt.nodes.new("ShaderNodeOutputMaterial")
    emision = nt.nodes.new("ShaderNodeEmission")
    emision.inputs["Color"].default_value = (*COLOR_LUZ, 1.0)
    emision.inputs["Strength"].default_value = 12.0
    transparente = nt.nodes.new("ShaderNodeBsdfTransparent")
    camino = nt.nodes.new("ShaderNodeLightPath")
    mezcla = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(camino.outputs["Is Camera Ray"], mezcla.inputs["Fac"])
    nt.links.new(transparente.outputs["BSDF"], mezcla.inputs[1])
    nt.links.new(emision.outputs["Emission"], mezcla.inputs[2])
    nt.links.new(mezcla.outputs["Shader"], salida.inputs["Surface"])
    return m


def importar(colores):
    bpy.ops.wm.obj_import(filepath=str(OBJ), forward_axis="Y", up_axis="Z", use_split_groups=True)
    objetos = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    propios = {}
    for nombre, color in colores.items():
        if nombre == "oro":
            propios[nombre] = material_oro(color)
        elif nombre == "yeso":
            propios[nombre] = material_yeso(nombre, color)
        else:
            propios[nombre] = material_yeso(nombre, color, rugosidad=0.9, grano=0.18, translucidez=0.02, variacion=0.08)
    for o in objetos:
        for ranura in o.material_slots:
            if ranura.material is None:
                continue
            familia = ranura.material.name.split(".")[0].rsplit("_", 1)[0]
            if familia in propios:
                ranura.material = propios[familia]
        # Suaviza por angulo, como el rasterizador (aristas vivas > 35 grados).
    for o in objetos:
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    return objetos, propios


def contorno_del_tambor(objetos) -> np.ndarray:
    """Puntos (x, y) del borde inferior del tambor, ordenados por angulo."""
    tambor = next(o for o in objetos if o.name.startswith("tambor"))
    V = np.array([tuple(tambor.matrix_world @ v.co) for v in tambor.data.vertices])
    abajo = V[np.abs(V[:, 2] - V[:, 2].min()) < 1e-6][:, :2]
    ang = np.arctan2(abajo[:, 1], abajo[:, 0])
    orden = np.argsort(ang)
    return abajo[orden], V[:, 2].min()


def radio_en(contorno: np.ndarray, angulo: float) -> float:
    ang = np.arctan2(contorno[:, 1], contorno[:, 0])
    r = np.hypot(contorno[:, 0], contorno[:, 1])
    return float(np.interp(angulo, ang, r, period=2 * math.pi))


def sala(contorno: np.ndarray, cota_tambor: float, yeso_sala):
    """Muros bajo el tambor, siguiendo su contorno, y suelo."""
    n = len(contorno)
    verts = [(x, y, cota_tambor) for x, y in contorno] + [(x, y, SUELO) for x, y in contorno]
    caras = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    caras.append(tuple(range(2 * n - 1, n - 1, -1)))  # suelo
    malla = bpy.data.meshes.new("sala")
    malla.from_pydata(verts, [], caras)
    malla.update()
    obj = bpy.data.objects.new("sala", malla)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(yeso_sala)


def ventanas(contorno: np.ndarray, mat_ventana):
    """16 ventanas: dos por lado del octogono, en la cara interior del tambor."""
    for lado in range(8):
        normal_ang = math.radians(45 * lado)
        hacia_dentro = Vector((-math.cos(normal_ang), -math.sin(normal_ang), 0.0))
        tangente = Vector((-math.sin(normal_ang), math.cos(normal_ang), 0.0))
        r_lado = radio_en(contorno, normal_ang)
        for signo in (-1, 1):
            centro = -hacia_dentro * (r_lado - 0.03) + tangente * (signo * VENTANA_SEPARACION / 2)
            centro.z = VENTANA_CENTRO_Z
            # Panel visible.
            bpy.ops.mesh.primitive_plane_add(size=1.0, location=centro)
            panel = bpy.context.active_object
            panel.scale = (VENTANA_ANCHO, VENTANA_ALTO, 1.0)
            panel.rotation_mode = "QUATERNION"
            panel.rotation_quaternion = hacia_dentro.to_track_quat("Z", "Y")
            panel.data.materials.append(mat_ventana)
            # Luz de area un poco detras, mirando hacia dentro y algo hacia arriba.
            luz = bpy.data.lights.new(f"ventana_{lado}_{signo}", "AREA")
            luz.shape = "RECTANGLE"
            luz.size = VENTANA_ANCHO
            luz.size_y = VENTANA_ALTO
            luz.energy = LUZ_VENTANA_W
            luz.color = COLOR_LUZ
            luz.spread = math.radians(100)
            o = bpy.data.objects.new(luz.name, luz)
            bpy.context.collection.objects.link(o)
            o.location = centro - hacia_dentro * 0.05
            direccion = (hacia_dentro + Vector((0, 0, 0.35))).normalized()
            o.rotation_mode = "QUATERNION"
            o.rotation_quaternion = (-direccion).to_track_quat("Z", "Y")


def sol(contorno: np.ndarray):
    """Tres haces que entran por ventanas contiguas de `SOL_LADO`."""
    for k, (lado, signo) in enumerate(((SOL_LADO, -1), (SOL_LADO, 1), ((SOL_LADO + 1) % 8, -1))):
        normal_ang = math.radians(45 * lado)
        hacia_dentro = Vector((-math.cos(normal_ang), -math.sin(normal_ang), 0.0))
        tangente = Vector((-math.sin(normal_ang), math.cos(normal_ang), 0.0))
        centro = -hacia_dentro * (radio_en(contorno, normal_ang) - 0.3) + tangente * (signo * VENTANA_SEPARACION / 2)
        centro.z = VENTANA_CENTRO_Z
        foco = bpy.data.lights.new(f"sol_{k}", "SPOT")
        foco.energy = SOL_W
        foco.color = COLOR_SOL
        foco.spot_size = math.radians(SOL_ABERTURA)
        foco.spot_blend = 0.35
        foco.shadow_soft_size = 0.12
        o = bpy.data.objects.new(foco.name, foco)
        bpy.context.collection.objects.link(o)
        o.location = centro
        e = math.radians(SOL_ELEVACION)
        direccion = (hacia_dentro * math.cos(e) + Vector((0, 0, math.sin(e)))).normalized()
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = direccion.to_track_quat("-Z", "Y")


def camara(nombre: str, posicion, objetivo, fov: float):
    cam = bpy.data.cameras.new(nombre)
    cam.sensor_fit = "HORIZONTAL"
    cam.angle = math.radians(fov)
    cam.clip_start = 0.05
    cam.clip_end = 200.0
    o = bpy.data.objects.new(nombre, cam)
    bpy.context.collection.objects.link(o)
    o.location = posicion
    direccion = Vector(objetivo) - Vector(posicion)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = direccion.to_track_quat("-Z", "Y")
    return o


def ajustes(muestras: int, lado: int):
    esc = bpy.context.scene
    esc.render.engine = "CYCLES"
    esc.cycles.device = "CPU"
    esc.cycles.samples = muestras
    esc.cycles.use_denoising = True
    esc.cycles.denoiser = "OPENIMAGEDENOISE"
    esc.cycles.max_bounces = 8
    esc.cycles.diffuse_bounces = 6
    esc.cycles.glossy_bounces = 4
    esc.cycles.transparent_max_bounces = 4
    esc.cycles.sample_clamp_indirect = 8.0
    esc.render.resolution_x = lado
    esc.render.resolution_y = lado
    esc.render.resolution_percentage = 100
    esc.render.image_settings.file_format = "PNG"
    esc.view_settings.view_transform = "AgX"
    esc.view_settings.look = "AgX - Medium High Contrast"
    esc.view_settings.exposure = 0.0
    # Mundo negro: la sala esta cerrada y la luz entra por las ventanas.
    mundo = bpy.data.worlds.new("mundo")
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    esc.world = mundo


def main() -> int:
    args = argumentos()
    limpiar()
    colores = colores_del_mtl(OBJ.with_suffix(".mtl"))
    objetos, propios = importar(colores)
    contorno, cota = contorno_del_tambor(objetos)
    sala(contorno, cota, material_yeso("yeso_sala", colores["yeso"], grano=0.3, variacion=0.1))
    ventanas(contorno, material_ventana())
    sol(contorno)
    ajustes(args.muestras, args.lado)
    args.salida.mkdir(parents=True, exist_ok=True)
    for nombre in args.vistas.split(","):
        pos, obj, fov = VISTAS[nombre]
        bpy.context.scene.camera = camara(nombre, pos, obj, fov)
        ruta = args.salida / f"cupula_cycles_{nombre}{args.sufijo}.png"
        bpy.context.scene.render.filepath = str(ruta)
        bpy.ops.render.render(write_still=True)
        print(f"-> {ruta}")
    return 0


if __name__ == "__main__":
    main()
