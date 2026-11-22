"""Estudio Cycles del paño web, con cámara equivalente y procedencia.

LD_LIBRARY_PATH=/usr/lib/wsl/lib blender -b -P scripts/render_estudio_yeseria.py -- --muestras 128
No modifica el archivo GLB. Las adiciones opcionales, luz y acabado son
propuestas de presentación: no se infieren pigmentos ni cotas de la fotografía.
"""

import argparse
import gzip
import hashlib
import json
import math
import struct
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from render_cycles import dispositivo, ajustes


def completar_macizos(apa, paleta):
    """Talla vegetal propuesta sobre los macizos lisos; no calca un original."""
    from detalle_visita import Superficie
    from talla_cupulin import tallar_ataurique
    from mathutils.bvhtree import BVHTree
    tambor = bpy.data.objects["tambor"]
    v = [tambor.matrix_world @ p.co for p in tambor.data.vertices]
    f = [tuple(p.vertices) for p in tambor.data.polygons]
    arbol = BVHTree.FromPolygons(v, f, all_triangles=True)
    resultado = []
    for k, (a, b) in enumerate(((-1.40, -0.90), (-0.29, 0.29), (0.90, 1.40))):
        forma = Superficie()
        apoyos = 0
        for inferior in (-1.22, -0.91, -0.60):
            # Comprobar una rejilla del asiento; ni las ventanas ni las adarajas
            # pueden servir de fondo de estas nuevas superficies de presentación.
            for i in range(5):
                for j in range(5):
                    y, z = a + (b - a) * i / 4, inferior + 0.28 * j / 4
                    hit, _, _, _ = arbol.ray_cast(Vector((apa - 0.05, y, z)), Vector((1, 0, 0)), 0.10)
                    assert hit is not None and abs(hit.x - apa) < 1e-5, "Talla sin apoyo en el macizo"
                    apoyos += 1

            def punto(u, v, h):
                return (apa - h, a + (b - a) * u, inferior + 0.28 * v)

            tallar_ataurique(forma, punto)
        obj = forma.objeto(f"Estudio de talla en macizo {k}", paleta)
        for pol in obj.data.polygons:
            pol.use_smooth = True
        resultado.append(dict(nombre=obj.name, triangulos=len(obj.data.polygons),
                              apoyos_comprobados=apoyos, altura_relieve_max_m=0.0064))
    # Trasdós plano por fuera del paño. Es un soporte escénico propuesto,
    # no el levantamiento de una cubierta histórica.
    forma = Superficie()
    ids = forma.puntos([(apa + 0.04, y, z) for y, z in ((-1.65, -0.02), (1.65, -0.02),
                                                       (1.65, 1.05), (-1.65, 1.05))])
    forma.cara(ids, "yeso")
    obj = forma.objeto("Trasdós propuesto del paño", paleta)
    resultado.append(dict(nombre=obj.name, triangulos=2, x_m=apa + 0.04,
                          limites_y_m=[-1.65, 1.65], limites_z_m=[-0.02, 1.05]))
    return resultado


def srgb(x):
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4


def yeso(material, color, microbisel):
    """Albedo sin luz pintada; relieve de acabado submilimétrico en metros."""
    material.use_nodes = True
    nt = material.node_tree
    nt.nodes.clear()
    salida = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = (*color[:3], 1)
    p.inputs["Roughness"].default_value = 0.90
    p.inputs["Specular IOR Level"].default_value = 0.35
    p.inputs["IOR"].default_value = 1.46
    p.inputs["Subsurface Weight"].default_value = 0.025
    p.inputs["Subsurface Radius"].default_value = (0.003, 0.002, 0.001)
    if material.name.startswith("oro"):
        p.inputs["Metallic"].default_value = 0.72
        p.inputs["Roughness"].default_value = 0.34
        p.inputs["Subsurface Weight"].default_value = 0
    coord = nt.nodes.new("ShaderNodeNewGeometry")
    llana = nt.nodes.new("ShaderNodeTexNoise")
    llana.inputs["Scale"].default_value = 65
    llana.inputs["Detail"].default_value = 3
    nt.links.new(coord.outputs["Position"], llana.inputs["Vector"])
    grano = nt.nodes.new("ShaderNodeTexNoise")
    grano.inputs["Scale"].default_value = 1600
    grano.inputs["Detail"].default_value = 2
    nt.links.new(coord.outputs["Position"], grano.inputs["Vector"])
    variacion = nt.nodes.new("ShaderNodeMixRGB")
    variacion.blend_type = "MULTIPLY"
    variacion.inputs[0].default_value = 0.12
    variacion.inputs[1].default_value = (*color[:3], 1)
    nt.links.new(llana.outputs["Fac"], variacion.inputs[2])
    nt.links.new(variacion.outputs[0], p.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Distance"].default_value = 0.00025
    bump.inputs["Strength"].default_value = 0.45
    nt.links.new(grano.outputs["Fac"], bump.inputs["Height"])
    if microbisel > 0:
        bevel = nt.nodes.new("ShaderNodeBevel")
        bevel.inputs["Radius"].default_value = microbisel
        bevel.samples = 4
        nt.links.new(bevel.outputs["Normal"], bump.inputs["Normal"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    nt.links.new(p.outputs[0], salida.inputs["Surface"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--muestras", type=int, default=128)
    ap.add_argument("--ancho", type=int, default=1800)
    ap.add_argument("--exposicion", type=float, default=0.5)
    ap.add_argument("--ventanas", type=float, default=4.0, help="radiancia propuesta, no calibrada")
    ap.add_argument("--principal", type=float, default=20.0, help="W de Blender; luz propuesta")
    ap.add_argument("--luz", choices=("opuesta", "rasante"), default="rasante")
    ap.add_argument("--microbisel", type=float, default=0.0006, help="normal de arista, metros; no mueve vértices")
    ap.add_argument("--salida", type=Path, default=ROOT / "renders/previas/0039_cycles")
    ap.add_argument("--dispositivo", default="cuda", choices=("cpu", "cuda", "optix"))
    ap.add_argument("--blend", action="store_true")
    ap.add_argument("--completar-macizos", action="store_true", help="talla y trasdós locales propuestos; no cambia el GLB")
    args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    fuentes = ["web/modelos/dos-hermanas.glb.gz", "web/modelos/dos-hermanas.json",
               "scripts/render_estudio_yeseria.py", "scripts/render_cycles.py",
               "web/visita.js", "renders/previas/foto_commons_detalle.jpg",
               "scripts/talla_cupulin.py", "scripts/detalle_visita.py"]
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in fuentes}
    archivo = ROOT / fuentes[0]
    datos = gzip.decompress(archivo.read_bytes())
    longitud = struct.unpack_from("<I", datos, 12)[0]
    gltf = json.loads(datos[20:20 + longitud])
    paleta = {m["name"]: m.get("pbrMetallicRoughness", {}).get("baseColorFactor", [1, 1, 1, 1])
              for m in gltf["materials"]}
    ficha = json.loads((ROOT / fuentes[1]).read_text())
    assert hashlib.sha256(datos).hexdigest() == ficha["sha256_glb"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with tempfile.TemporaryDirectory() as temporal:
        glb = Path(temporal) / "entrada.glb"
        glb.write_bytes(datos)
        bpy.ops.import_scene.gltf(filepath=str(glb))
    objetos = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    triangulos = sum(len(o.data.polygons) for o in objetos)
    assert len(objetos) == ficha["mallas"]
    assert triangulos == ficha["triangulos"]
    apa = ficha["sector_00"]["apotema_m"]
    adiciones = completar_macizos(apa, {m.name: m for m in bpy.data.materials}) if args.completar_macizos else []
    materiales = list(bpy.data.materials)
    for m in materiales:
        p = m.node_tree.nodes.get("Principled BSDF")
        if p is None:
            continue
        # El importador conecta el factor de albedo mediante nodos. El valor
        # por defecto de Base Color puede ser blanco: leer el factor del GLB.
        color = tuple(paleta[m.name])
        if "Luz de patio" in m.name:
            nt = m.node_tree
            nt.nodes.clear()
            emitir = nt.nodes.new("ShaderNodeEmission")
            emitir.inputs["Color"].default_value = (1, 0.96, 0.90, 1)
            emitir.inputs["Strength"].default_value = args.ventanas
            salida = nt.nodes.new("ShaderNodeOutputMaterial")
            nt.links.new(emitir.outputs[0], salida.inputs["Surface"])
        else:
            if m.name == "yeso":
                color = tuple(map(srgb, (0.87, 0.85, 0.79))) + (1,)
            elif m.name == "crema":
                color = tuple(map(srgb, (0.82, 0.79, 0.71))) + (1,)
            yeso(m, color, args.microbisel)
    ajustes(args.muestras, args.ancho)
    escena = bpy.context.scene
    escena.render.resolution_y = round(args.ancho * 740 / 900)
    escena.view_settings.look = "AgX - Medium High Contrast"
    escena.view_settings.exposure = args.exposicion
    escena.cycles.adaptive_threshold = 0.015
    escena.cycles.seed = 3901
    dispositivo(args.dispositivo)
    objetivo = Vector((apa - 0.16, 0.30, -0.26))
    cam = bpy.data.cameras.new("Misma cámara que Hiladas")
    cam.sensor_fit = "VERTICAL"
    cam.lens = cam.sensor_height / (2 * math.tan(math.radians(46) / 2))
    cam.clip_start = 0.005
    cam.clip_end = 60
    camara = bpy.data.objects.new("Cámara del estudio", cam)
    bpy.context.collection.objects.link(camara)
    camara.location = (1.75, 0.48, -1.38)
    camara.rotation_euler = (objetivo - camara.location).to_track_quat("-Z", "Y").to_euler()
    escena.camera = camara
    # Luz desde el interior de un vano. El reparto no se atribuye a
    # una hora ni a una orientación solar histórica.
    luz = bpy.data.lights.new("Luz de ventana opuesta", "AREA")
    luz.energy = args.principal
    luz.shape = "RECTANGLE"
    luz.size, luz.size_y = 0.46, 0.90
    luz.color = (1, 0.96, 0.90)
    lampara = bpy.data.objects.new(luz.name, luz)
    bpy.context.collection.objects.link(lampara)
    lampara.location = ((-apa + 0.19) if args.luz == "opuesta" else (apa - 0.19), -0.59, -0.79)
    lampara.rotation_euler = (objetivo - lampara.location).to_track_quat("-Z", "Y").to_euler()
    salida = args.salida.resolve()
    salida.mkdir(parents=True, exist_ok=True)
    escena.render.filepath = str(salida / "pano_completo.png")
    if args.blend:
        bpy.ops.wm.save_as_mainfile(filepath=str(salida / "estudio.blend"))
    bpy.ops.render.render(write_still=True)
    informe = dict(
        naturaleza="Estudio visual: iluminación y acabado propuestos, sin nueva medición histórica",
        sha256=hashes, sha256_glb=ficha["sha256_glb"], blender=bpy.app.version_string,
        parametros={k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
        camara=dict(posicion=list(camara.location), objetivo=list(objetivo), fov_vertical=46,
                    viewport_referencia=[900, 740], recorte_referencia=[160, 140, 580, 380]),
        mallas=len(objetos), triangulos=triangulos,
        geometria="Base GLB sin mover vértices; adiciones locales indicadas por separado; microbisel de normales",
        adiciones=adiciones,
        imagen_sha256=hashlib.sha256((salida / "pano_completo.png").read_bytes()).hexdigest(),
    )
    (salida / "procedencia.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(informe, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
