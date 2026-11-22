"""Alzado registrado del GLB y control de saliente frente a Foto de Ferrer.

Inspección geométrica local; las imágenes de terceros no se redistribuyen.
"""
import argparse
import gzip
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def leer(path):
    datos = gzip.decompress(path.read_bytes())
    n = struct.unpack_from("<I", datos, 12)[0]
    j = json.loads(datos[20:20 + n])

    def acceso(i):
        a = j["accessors"][i]
        vista = j["bufferViews"][a["bufferView"]]
        tipo = {5126: "<f4", 5125: "<u4", 5123: "<u2"}[a["componentType"]]
        columnas = {"VEC3": 3, "SCALAR": 1}[a["type"]]
        assert vista.get("byteStride", np.dtype(tipo).itemsize * columnas) == np.dtype(tipo).itemsize * columnas
        return np.frombuffer(datos, dtype=tipo, count=a["count"] * columnas,
                             offset=28 + n + vista.get("byteOffset", 0) + a.get("byteOffset", 0)).reshape(-1, columnas)

    mallas = {}
    for nodo in j["nodes"]:
        if "mesh" not in nodo:
            continue
        assert "children" not in nodo and "matrix" not in nodo
        assert nodo.get("rotation", [0, 0, 0, 1]) == [0, 0, 0, 1]
        vertices, caras = [], []
        for p in j["meshes"][nodo["mesh"]]["primitives"]:
            v = acceso(p["attributes"]["POSITION"]).astype(float)
            f = acceso(p["indices"]).reshape(-1, 3) + len(vertices)
            v = v * nodo.get("scale", [1, 1, 1]) + nodo.get("translation", [0, 0, 0])
            vertices.extend(v[:, [0, 2, 1]] * [1, -1, 1])
            caras.extend(f)
        mallas[nodo["name"]] = (np.array(vertices), np.array(caras))
    return mallas


def perfil_foto(foto, umbral=245):
    rgb = np.asarray(foto).astype(float)
    rojo = (rgb[:, :, 0] - rgb[:, :, 1] > 35) & (rgb[:, :, 0] - rgb[:, :, 2] > 35)
    tinta = (rgb.mean(axis=2) < umbral) & ~rojo
    superior = np.where(tinta.any(axis=0), tinta.argmax(axis=0), np.nan)
    return superior


def pintar(mallas, registro, tam):
    escala = registro["px_por_m"]
    x0, y0 = registro["origen_modelo_px"]
    triangulos, colores, profundidades = [], [], []
    luz = np.array([-.35, -.65, .68])
    luz /= np.linalg.norm(luz)
    for nombre, (v, f) in mallas.items():
        if nombre.startswith(("sala_muros", "sala_sofito", "sala_trompas")):
            continue
        t = v[f]
        # Hemicúpula posterior, como control de alzado. No se infieren de
        # aquí las correspondencias de cada pieza con la foto.
        t = t[(t[:, :, 1].mean(axis=1) >= 0) & (t[:, :, 2].max(axis=1) >= -.7)]
        if not len(t):
            continue
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
        brillo = .35 + .65 * abs(n @ luz)
        color = np.array([90, 155, 205] if nombre.startswith("cupulin_") else [210, 205, 193])
        colores.extend(np.uint8(brillo[:, None] * color))
        triangulos.extend(np.stack([x0 + escala * t[:, :, 0], y0 - escala * t[:, :, 2]], axis=-1))
        profundidades.extend(t[:, :, 1].mean(axis=1))
    im = Image.new("RGB", tam, "white")
    d = ImageDraw.Draw(im)
    for i in np.argsort(profundidades)[::-1]:
        d.polygon([tuple(p) for p in triangulos[i]], fill=tuple(colores[i]))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glb", type=Path, default=ROOT / "web/modelos/dos-hermanas.glb.gz")
    ap.add_argument("--nombre", default="antes")
    a = ap.parse_args()
    registro = json.loads((ROOT / "datos/registro_foto_ferrer.json").read_text())
    foto = Image.open(ROOT / "docs/Foto de Ferrer.png").convert("RGB")
    mallas = leer(a.glb)
    superior = perfil_foto(foto)
    escala = registro["px_por_m"]
    x0, y0 = registro["origen_modelo_px"]
    cupulines = []
    for nombre, (v, _) in mallas.items():
        if not nombre.startswith("cupulin_"):
            continue
        x = np.clip(np.rint(x0 + escala * v[:, 0]).astype(int), 0, foto.width - 1)
        limite = (y0 - superior[x]) / escala
        cupulines.append(dict(nombre=nombre, z_min_m=float(v[:, 2].min()), z_max_m=float(v[:, 2].max()),
                              exceso_max_sobre_silueta_m=float(np.nanmax(v[:, 2] - limite))))
    salida = ROOT / "renders/previas/0040_alzado"
    salida.mkdir(parents=True, exist_ok=True)
    im = pintar(mallas, registro, foto.size)
    im.save(salida / f"modelo_{a.nombre}.png")
    hoja = Image.new("RGB", (foto.width * 2, foto.height + 35), "#f3f0e8")
    hoja.paste(foto, (0, 35))
    hoja.paste(im, (foto.width, 35))
    d = ImageDraw.Draw(hoja)
    d.text((10, 10), "Foto de Ferrer · alzado", fill="black")
    d.text((foto.width + 10, 10), f"Modelo {a.nombre} · cupulines en azul · misma escala y origen", fill="black")
    hoja.save(salida / f"comparacion_{a.nombre}.png")
    informe = dict(glb=str(a.glb), sha256_glb_gzip=hashlib.sha256(a.glb.read_bytes()).hexdigest(),
                   sha256_script=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   registro=registro, cupulines=cupulines,
                   limite="La silueta limita el alzado proyectado, no determina la profundidad de un cupulín interior")
    (ROOT / f"datos/alzado_cupulines_{a.nombre}.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(cupulines, indent=2))


if __name__ == "__main__":
    main()
