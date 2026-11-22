"""Exporta el OBJ de campo con Blender. Ejecutar con -b -P desde la raíz."""

import gzip
import argparse
import hashlib
import json
import math
import struct
import sys
import tempfile
from pathlib import Path

import bpy
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from render_cycles import colores_del_mtl, _srgb_a_lineal  # noqa: E402
from detalle_visita import (  # noqa: E402
    Superficie,
    clave,
    cupulin_piloto,
    tambor_con_vanos,
    luz_de_vanos,
)
from talla_cupulin import construir_frentes, medir_boca  # noqa: E402
from hiladas_ventanas import (  # noqa: E402
    construir_sector,
    medir_sector,
    pared_piloto,
    verificar_juntas_glb,
)

OBJ = ROOT / "renders/previas/cupula_campo_vigente_1400.obj"
SALIDA = ROOT / "web/modelos"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=SALIDA)
    ap.add_argument("--encaje", choices=("0036", "seccion", "silueta"), default="silueta")
    args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    salida = args.salida
    auditoria = json.loads((ROOT / "datos/auditoria_geometria_obj.json").read_text())
    sha = hashlib.sha256(OBJ.read_bytes()).hexdigest()
    if sha != auditoria["sha256_obj"]:
        raise ValueError("El OBJ no corresponde a la auditoría 0032")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(
        filepath=str(OBJ), forward_axis="Y", up_axis="Z", use_split_groups=True
    )
    objetos = list(bpy.context.selected_objects)
    mtl = OBJ.with_suffix(".mtl")
    paleta = {}
    colores = colores_del_mtl(mtl)
    # El tostado del OBJ representa sombra de maqueta. Con oclusión espacial,
    # reinterpretar ese fondo como yeso tostado, manteniendo su reparto.
    colores["tostado"] = (0.72, 0.64, 0.53)
    for familia, rgb in colores.items():
        material = bpy.data.materials.new(familia)
        material.diffuse_color = (*map(_srgb_a_lineal, rgb), 1)
        material.roughness = 0.38 if familia == "oro" else 0.88
        material.metallic = 0.65 if familia == "oro" else 0
        material.use_backface_culling = False
        paleta[familia] = material
    escala = auditoria["cateto_m"]
    for objeto in objetos:
        objeto.matrix_world = Matrix.Scale(escala, 4) @ objeto.matrix_world
        for slot in objeto.material_slots:
            familia = slot.material.name.rsplit("_", 1)[0]
            slot.material = paleta[familia]
    bpy.context.view_layer.update()
    sala = json.loads((ROOT / "datos/alzado_sala.json").read_text())
    borde = clave(bpy.data.objects["cupulilla_25"], paleta)
    centro = cupulin_piloto(bpy.data.objects["cupulin_00"], paleta, OBJ.parent, escala)
    def pared(forma, apotema, bajo, alzado):
        return pared_piloto(forma, apotema, bajo, alzado, encaje=args.encaje)
    boca = "escalonada" if args.encaje == "silueta" else "arco"
    apotema = tambor_con_vanos(bpy.data.objects["tambor"], paleta, sala, pared, boca=boca)
    bpy.context.view_layer.update()
    suelo = sala["niveles"]["suelo"]["z_m"]
    lectura = medir_boca(centro, suelo)
    registro = json.loads((ROOT / "datos/cupulines.json").read_text())["metodo"]
    frentes = Superficie()
    n_frentes = construir_frentes(frentes, registro)
    frentes.objeto("Frentes tallados junto al cupulín 00", paleta)
    bpy.context.view_layer.update()
    con_talla = medir_boca(centro, suelo)
    print("Incidencias sobre la boca antes y después", lectura, con_talla, flush=True)
    assert all(lectura[v] > 0 and con_talla[v] >= 0.95 * lectura[v] for v in lectura)
    antes_sector = medir_sector(apotema, suelo)
    sector = construir_sector(apotema, paleta, sala, encaje=args.encaje)
    bpy.context.view_layer.update()
    despues_sector = medir_sector(apotema, suelo)
    boca_final = medir_boca(centro, suelo)
    print("Sector 00", sector, antes_sector, despues_sector, boca_final, flush=True)
    for vista, control in despues_sector.items():
        for previo, actual in zip(
            antes_sector[vista]["cielo_por_ventana"], control["cielo_por_ventana"]
        ):
            if not previo or actual < 0.95 * previo:
                raise ValueError(f"La cornisa oculta la ventana desde {vista}")
        if min(control["piezas_visibles"]) < 2:
            raise ValueError(f"Las dos hiladas no son visibles desde {vista}")
    if boca_final != con_talla:
        raise ValueError("La cornisa altera la vista comprobada del cupulín")
    objetos = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in objetos:
        o.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    bpy.context.view_layer.update()
    print("Calculando visibilidad de los vanos…", flush=True)
    muestras = luz_de_vanos(objetos, apotema)
    salida.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporal:
        glb = Path(temporal) / "dos-hermanas.glb"
        bpy.ops.export_scene.gltf(
            filepath=str(glb),
            export_format="GLB",
            export_animations=False,
            export_texcoords=False,
            export_cameras=False,
            export_lights=False,
            export_vertex_color="ACTIVE",
        )
        datos = glb.read_bytes()
    longitud = struct.unpack_from("<I", datos, 12)[0]
    escena = json.loads(datos[20 : 20 + longitud])
    sector["encuentros_glb"] = verificar_juntas_glb(
        escena, datos, 28 + longitud, sector
    )
    assert all(
        "COLOR_0" in p["attributes"] for m in escena["meshes"] for p in m["primitives"]
    )
    triangulos = sum(
        escena["accessors"][p["indices"]]["count"] // 3
        for m in escena["meshes"]
        for p in m["primitives"]
    )
    caras_obj = sum(len(o.data.polygons) for o in objetos)
    if triangulos != caras_obj or len(escena["meshes"]) != len(objetos):
        raise ValueError(
            f"Exportación incompleta: {triangulos}/{caras_obj} triángulos, "
            f"{len(escena['meshes'])}/{len(objetos)} mallas"
        )
    destino = salida / "dos-hermanas.glb.gz"
    with (
        destino.open("wb") as f,
        gzip.GzipFile(filename="", mode="wb", fileobj=f, mtime=0) as g,
    ):
        g.write(datos)
    ficha = dict(
        obj=str(OBJ.relative_to(ROOT)),
        sha256_obj=sha,
        sha256_mtl=hashlib.sha256(mtl.read_bytes()).hexdigest(),
        sha256_glb=hashlib.sha256(datos).hexdigest(),
        blender=bpy.app.version_string,
        cateto_m=escala,
        suelo_m=sala["niveles"]["suelo"]["z_m"],
        mallas=len(objetos),
        triangulos=triangulos,
        bytes_gzip=destino.stat().st_size,
        borde_clave=borde,
        cota_max_clave_m=4.67,
        puntos_visibilidad=muestras,
        muestras_de_ventana=16,
        geometria_presentacion=[
            "clave",
            "cupulin_00",
            "frentes_locales",
            "tambor",
            "hiladas_del_pano_00",
        ],
        sector_00=dict(**sector, antes=antes_sector, despues=despues_sector),
        frentes_locales=n_frentes,
        comprobacion_boca={
            "rayos_por_vista": 65**2,
            "antes_de_los_frentes": lectura,
            "con_frentes": con_talla,
            "con_dos_hiladas": boca_final,
        },
        fuentes_piloto={
            p: hashlib.sha256((OBJ.parent / p).read_bytes()).hexdigest()
            for p in ("piloto_asiento.npz", "piezas_recortadas_00.npz")
        },
        sha256_generadores={
            p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
            for p in ("scripts/exportar_visita_web.py", "scripts/hiladas_ventanas.py",
                      "scripts/encajar_frentes_visita.py", "scripts/detalle_visita.py",
                      "scripts/talla_cupulin.py", "scripts/nicho_escalonado.py",
                      "datos/alzado_sala.json")
        },
    )
    (salida / "dos-hermanas.json").write_text(json.dumps(ficha, indent=2) + "\n")
    print(ficha)


if __name__ == "__main__":
    main()
