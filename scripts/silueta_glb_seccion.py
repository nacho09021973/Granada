"""Silueta del GLB cortado como la sección AA-415_23, para comparar el vuelo.

La sección es una ortofoto del modelo fotogramétrico cortado por el centro
de la sala; en sus bordes, las caras del tambor paralelas a la vista salen de
canto (`scripts/medir_vuelo_seccion.py`). Aquí se renderiza el GLB en
ortográfica, sin luz y en negro sobre blanco, mirando a lo largo de +y desde
el plano y = 0 (solo se ve lo que queda en y > 0). Así el paño 00 (+x), el
único con hiladas, sale de canto en el borde derecho, igual que una cara
lateral en la sección. Escala, 472,488 px/m, y origen vertical (z = 0 en el
arranque) son los de `datos/alzado_sala.json`.

El perfil se extrae con `silueta` de `scripts/medir_estratificacion.py`
(copiada aquí: Blender no trae PIL) y los mismos umbrales.

La sección no muestra nada más allá del plano del muro lateral, ni siquiera
los nichos de sus vanos (silueta recta en la banda de las ventanas,
desviación de 8–10 px): se interpreta como un recorte de la ortofoto en ese
plano. Para comparar igual, se corta el GLB en x = apotema + RECORTE y se
descarta lo de fuera (nichos, fondos luminosos, envolvente exterior).

Diferencia conocida: en el modelo solo el paño 00 tiene hiladas y vanos a
0,30 m; las caras oblicuas contiguas, que también entran en la envolvente
cerca de la esquina, no las tienen.

Uso: ~/.local/opt/blender/blender -b --python-exit-code 1 -P scripts/silueta_glb_seccion.py -- [--glb RUTA] [--salida datos/vuelo_modelo_silueta.json] [--sufijo _0042]
"""

import argparse
import gzip
import hashlib
import json
import sys
import tempfile
from math import cos, pi, sin
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[1]
APOTEMA = 3.8657066822052  # web/modelos/dos-hermanas.json
UMBRALES = (240, 245, 250)  # scripts/medir_estratificacion.py
X0, X1, Z0, Z1 = 0.5, 4.5, -1.6, 1.0
VENTANA = 0.6
RECORTE = 0.003


def silueta(gris, umbral):
    tinta = gris < umbral
    izq = np.full(gris.shape[0], np.nan)
    der = np.full(gris.shape[0], np.nan)
    for y in range(gris.shape[0]):
        col = np.nonzero(tinta[y])[0]
        if col.size:
            izq[y], der[y] = col[0], col[-1]
    return izq, der


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glb", type=Path, default=Path("web/modelos/dos-hermanas.glb.gz"))
    ap.add_argument("--salida", type=Path, default=Path("datos/vuelo_modelo_silueta.json"))
    ap.add_argument("--sufijo", default="")
    ap.add_argument("--solo-pano", action="store_true", help="descarta lo que queda fuera del sector del paño 00 (|ángulo| > 22,5°)")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])
    origen = a.glb if a.glb.is_absolute() else ROOT / a.glb
    salida = a.salida if a.salida.is_absolute() else ROOT / a.salida
    alzado = json.loads((ROOT / "datos/alzado_sala.json").read_text())
    escala = alzado["px_por_m"]
    bruto = gzip.decompress(origen.read_bytes())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with tempfile.TemporaryDirectory() as t:
        p = Path(t) / "m.glb"
        p.write_bytes(bruto)
        bpy.ops.import_scene.gltf(filepath=str(p))
    escena = bpy.context.scene
    for obj in [o for o in escena.objects if o.type == "MESH"]:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.transform(obj.matrix_world)
        bmesh.ops.bisect_plane(
            bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
            plane_co=(APOTEMA + RECORTE, 0, 0), plane_no=(1, 0, 0), clear_outer=True,
        )
        if a.solo_pano:
            bmesh.ops.bisect_plane(
                bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                plane_co=(0, 0, 0), plane_no=(-sin(pi / 8), cos(pi / 8), 0), clear_outer=True,
            )
        bm.to_mesh(obj.data)
        bm.free()
        obj.matrix_world = Matrix.Identity(4)
    escena.render.engine = "BLENDER_WORKBENCH"
    escena.display.shading.light = "FLAT"
    escena.display.shading.color_type = "SINGLE"
    escena.display.shading.single_color = (0, 0, 0)
    escena.display.shading.background_type = "VIEWPORT"
    escena.display.shading.background_color = (1, 1, 1)
    escena.display.shading.show_backface_culling = False
    escena.view_settings.view_transform = "Standard"
    escena.render.film_transparent = False
    if escena.world is None:
        escena.world = bpy.data.worlds.new("fondo")
    escena.world.color = (1, 1, 1)
    datos = bpy.data.cameras.new("corte")
    datos.type = "ORTHO"
    ancho, alto = round((X1 - X0) * escala), round((Z1 - Z0) * escala)
    datos.ortho_scale = (X1 - X0)
    datos.sensor_fit = "HORIZONTAL"
    datos.clip_start = 0.0005
    datos.clip_end = 20
    cam = bpy.data.objects.new("corte", datos)
    escena.collection.objects.link(cam)
    # Ejes de la cámara: x local = +x, y local = +z, mira por -z local = +y.
    m = np.eye(4)
    m[:3, :3] = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)
    m[:3, 3] = ((X0 + X1) / 2, 0.0, (Z0 + Z1) / 2)
    cam.matrix_world = Matrix(m.tolist())
    escena.camera = cam
    escena.render.resolution_x, escena.render.resolution_y = ancho, alto
    escena.render.resolution_percentage = 100
    previa = ROOT / f"renders/previas/0043/silueta_glb{a.sufijo}.png"
    previa.parent.mkdir(parents=True, exist_ok=True)
    escena.render.filepath = str(previa)
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(str(previa))
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1, :, :3]
    gris = (px.mean(2) * 255).round()
    fila_z = lambda z: int(round((Z1 - z) * escala))
    columna_x = lambda x: (x - X0) * escala
    xmuro = columna_x(APOTEMA)
    f0 = fila_z(0.0)
    filas = np.arange(fila_z(VENTANA), fila_z(-VENTANA) + 1)
    res = dict(
        glb=str(origen.relative_to(ROOT)) if origen.is_relative_to(ROOT) else str(origen),
        sha256_glb_descomprimido=hashlib.sha256(bruto).hexdigest(),
        px_por_m=escala,
        apotema_m=APOTEMA,
        solo_pano=a.solo_pano,
        perfiles={},
        resumen={},
    )
    for u in UMBRALES:
        _, der = silueta(gris, u)
        vuelo = (xmuro - der[filas]) / escala
        zs = (f0 - filas) / escala
        res["perfiles"][str(u)] = [[round(float(z), 4), None if np.isnan(v) else round(float(v), 4)] for z, v in zip(zs[::4], vuelo[::4])]
        i0 = int(np.where(filas == f0)[0][0])
        res["resumen"][str(u)] = dict(
            vuelo_en_arranque_m=round(float(vuelo[i0]), 4),
            vuelo_a_10cm_sobre_arranque_m=round(float(vuelo[i0 - int(0.10 * escala)]), 4),
            vuelo_a_20cm_sobre_arranque_m=round(float(vuelo[i0 - int(0.20 * escala)]), 4),
            muro_mediana_m=round(float(np.nanmedian((xmuro - der[fila_z(-0.25):fila_z(-1.346)]) / escala)), 4),
        )
        print(u, res["resumen"][str(u)], flush=True)
    salida.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(salida, previa)


if __name__ == "__main__":
    main()
