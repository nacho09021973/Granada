"""Renderiza el GLB de la visita con las cámaras ajustadas y lo funde con cada foto.

Segunda vía para las cámaras de `datos/medida_nicho_fotos.json`
(`scripts/medir_nicho_fotos.py`): si el octógono, los alféizares y los vanos
del modelo caen sobre los de la foto, la cámara es coherente con la geometría
conocida. No comprueba la profundidad del nicho: el modelo tiene el nicho
de 9 cm, y justo ahí se espera la diferencia.

Sistema del ajuste: z = 0 en el canto del alféizar, cara B con normal +x.
En el modelo el alféizar está a `pie_ventanas_tambor` de `datos/alzado_sala.json`
y la cara +x es la del paño 00. Cámara del ajuste con ejes x derecha, y abajo,
z adelante; Blender mira por -Z local con Y arriba.

Salida: `renders/previas/0041_<clave>/superposicion.jpg` (foto | modelo |
fundido) y `modelo.png`. Solo se ajusta la distorsión si el ajuste la tiene;
la superposición la ignora (k1 = 0 en el ajuste principal).

Uso: ~/.local/opt/blender/blender -b --python-exit-code 1 -P scripts/superponer_camaras_fotos.py [-- --glb RUTA --sufijo _0042]
"""

import argparse
import gzip
import sys
import json
import tempfile
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[1]
MEDIDA = ROOT / "datos/medida_nicho_fotos.json"
GLB = ROOT / "web/modelos/dos-hermanas.glb.gz"
ESCALA = 0.5
RECORTE_CERCANO = 3.0


def cargar_modelo(origen=GLB):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with tempfile.TemporaryDirectory() as temporal:
        glb = Path(temporal) / "entrada.glb"
        glb.write_bytes(gzip.decompress(origen.read_bytes()))
        bpy.ops.import_scene.gltf(filepath=str(glb))


def leer_png(ruta):
    img = bpy.data.images.load(str(ruta))
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1, :, :3]
    bpy.data.images.remove(img)
    return px


def guardar(px, ruta):
    h, w, _ = px.shape
    img = bpy.data.images.new("salida", w, h)
    img.pixels = np.concatenate([px[::-1], np.ones((h, w, 1), np.float32)], 2).ravel()
    img.filepath_raw = str(ruta)
    img.file_format = "JPEG"
    img.save()
    bpy.data.images.remove(img)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glb", type=Path, default=GLB)
    ap.add_argument("--sufijo", default="", help="se añade a los nombres de las láminas")
    args = ap.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])
    origen = args.glb if args.glb.is_absolute() else ROOT / args.glb
    medida = json.loads(MEDIDA.read_text())
    z_alfeizar = json.loads((ROOT / "datos/alzado_sala.json").read_text())["niveles"]["pie_ventanas_tambor"]["z_m"]
    cargar_modelo(origen)
    escena = bpy.context.scene
    escena.render.engine = "BLENDER_WORKBENCH"
    escena.display.shading.light = "STUDIO"
    escena.display.shading.color_type = "MATERIAL"
    escena.display.shading.show_cavity = True
    escena.display.shading.show_backface_culling = False
    escena.render.film_transparent = False
    datos_cam = bpy.data.cameras.new("ajuste")
    camara = bpy.data.objects.new("ajuste", datos_cam)
    escena.collection.objects.link(camara)
    escena.camera = camara
    for clave, cam in medida["principal"]["camaras"].items():
        bordes = json.loads((ROOT / f"datos/bordes_celosias_{clave}.json").read_text())
        foto = ROOT / bordes["foto"]
        ancho, alto = cam["imagen_px"]
        R = np.array(cam["rotacion"])  # mundo -> cámara (x der, y abajo, z adelante)
        C = np.array(cam["posicion_m"]) + [0, 0, z_alfeizar]
        giro = R.T @ np.diag([1.0, -1.0, -1.0])  # cámara Blender -> mundo
        m = np.eye(4)
        m[:3, :3] = giro
        m[:3, 3] = C
        camara.matrix_world = Matrix(m.tolist())
        datos_cam.sensor_fit = "HORIZONTAL"
        datos_cam.sensor_width = 36.0
        datos_cam.lens = cam["focal_px"] * 36.0 / ancho
        # Las cámaras del ajuste quedan tras el muro de la sala del modelo, que no
        # tiene hueco de puerta. El tambor está a más de 8 m: se recorta lo que
        # queda a menos de RECORTE_CERCANO para ver a través del muro.
        datos_cam.clip_start = RECORTE_CERCANO
        datos_cam.clip_end = 100
        escena.render.resolution_x = int(ancho * ESCALA)
        escena.render.resolution_y = int(alto * ESCALA)
        escena.render.resolution_percentage = 100
        salida = ROOT / f"renders/previas/0041_{clave}"
        salida.mkdir(parents=True, exist_ok=True)
        escena.render.filepath = str(salida / f"modelo{args.sufijo}.png")
        bpy.ops.render.render(write_still=True)
        modelo = leer_png(salida / f"modelo{args.sufijo}.png")
        h, w, _ = modelo.shape
        img = bpy.data.images.load(str(foto))
        img.scale(w, h)
        fot = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, img.channels)[::-1, :, :3]
        bpy.data.images.remove(img)
        fundido = 0.5 * fot + 0.5 * modelo
        guardar(np.concatenate([fot, modelo, fundido], 1), salida / f"superposicion{args.sufijo}.jpg")
        print(clave, "->", salida / f"superposicion{args.sufijo}.jpg", flush=True)


if __name__ == "__main__":
    main()
