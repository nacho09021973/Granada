"""Corrige salientes del GLB preservando topología y bordes de los cierres.

Rebaja el exceso de los casquetes sobre una base armónica de su propio borde.
Los pozos usan la transformación monótona de reducir_saliente_cupulines.
No es una medición de cada profundidad a partir de un alzado.
"""
import argparse
import gzip
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from alzado_ferrer_cupulines import leer, pintar
from PIL import Image, ImageDraw


def rebajar_casquete(v, f, factor):
    xy, inversa = np.unique(np.round(v[:, :2], 6), axis=0, return_inverse=True)
    z = np.full(len(xy), -np.inf)
    np.maximum.at(z, inversa, v[:, 2])
    # Rejilla cartesiana de cupulilla(): solo vecinos horizontales/verticales.
    t = v[f]
    lados = np.concatenate([t[:, 1, :2] - t[:, 0, :2], t[:, 2, :2] - t[:, 1, :2], t[:, 0, :2] - t[:, 2, :2]])
    dist = np.abs(lados).ravel()
    paso = float(np.median(dist[dist > .001]))
    ij = np.rint((xy - xy.min(axis=0)) / paso).astype(int)
    assert np.max(abs((xy - xy.min(axis=0)) - ij * paso)) < 3e-5
    indice = {tuple(p): i for i, p in enumerate(ij)}
    vecinos = [[indice.get(tuple(p + d)) for d in ((1, 0), (-1, 0), (0, 1), (0, -1))] for p in ij]
    borde = np.array([any(j is None for j in js) for js in vecinos])
    interior = np.flatnonzero(~borde)
    mapa = {int(i): k for k, i in enumerate(interior)}
    A = lil_matrix((len(interior), len(interior)))
    b = np.zeros(len(interior))
    for k, i in enumerate(interior):
        A[k, k] = 4
        for j in vecinos[i]:
            if borde[j]:
                b[k] += z[j]
            else:
                A[k, mapa[j]] = -1
    base = z.copy()
    if len(interior):
        base[interior] = spsolve(A.tocsr(), b)
    # Un casquete no se eleva donde el residuo sea negativo por discretización.
    nueva_z = z - (1 - factor) * np.maximum(z - base, 0)
    nueva_z[borde] = z[borde]
    p = v.copy()
    p[:, 2] += (nueva_z - z)[inversa]
    assert np.max(abs(p[inversa >= 0, :2] - v[:, :2])) == 0
    assert np.max(abs(p[borde[inversa], 2] - v[borde[inversa], 2])) < 1e-12
    return p, dict(vertices_borde=int(borde.sum()), paso_m=paso,
                   rebaja_max_m=float(np.max(v[:, 2] - p[:, 2])),
                   z_max_antes_m=float(v[:, 2].max()), z_max_despues_m=float(p[:, 2].max()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", type=Path, default=ROOT / "build/0040_original/modelos/dos-hermanas.glb.gz")
    ap.add_argument("--salida", type=Path, default=ROOT / "build/alzado-corregido/modelos")
    ap.add_argument("--factor-casquetes", type=float, default=.45)
    # Rutas de registro: por defecto las de 0040, para no alterar su reproducción.
    ap.add_argument("--informe", type=Path, default=ROOT / "datos/correccion_alturas_alzado.json")
    ap.add_argument("--verificacion", type=Path, default=ROOT / "datos/comprobacion_alturas_visita.json")
    ap.add_argument("--sin-laminas", action="store_true", help="no reescribe las láminas de 0040")
    a = ap.parse_args()
    a.informe, a.verificacion = (q if q.is_absolute() else ROOT / q for q in (a.informe, a.verificacion))
    assert 0 <= a.factor_casquetes <= 1
    mallas = leer(a.entrada)
    pozos = np.load(ROOT / "renders/previas/0040_alzado/cupulines_reducidos.npz")
    cambios, controles = {}, []
    for nombre, (v, f) in mallas.items():
        if nombre.startswith("cupulilla_") and nombre != "cupulilla_25":
            p, d = rebajar_casquete(v, f, a.factor_casquetes)
            cambios[nombre] = p
            controles.append(dict(nombre=nombre, **d))
        elif nombre.startswith("cupulin_"):
            p = pozos[nombre]
            assert p.shape == v.shape
            cambios[nombre] = p
    original = gzip.decompress(a.entrada.read_bytes())
    n = struct.unpack_from("<I", original, 12)[0]
    j = json.loads(original[20:20 + n])
    binario = bytearray(original[28 + n:])

    def escribir_acceso(i, valores):
        acceso = j["accessors"][i]
        vista = j["bufferViews"][acceso["bufferView"]]
        assert acceso["componentType"] == 5126
        offset = vista.get("byteOffset", 0) + acceso.get("byteOffset", 0)
        assert vista.get("byteStride", 12) == 12
        datos = np.asarray(valores, dtype="<f4")
        binario[offset:offset + datos.nbytes] = datos.tobytes()
        if "min" in acceso:
            acceso["min"], acceso["max"] = datos.min(axis=0).tolist(), datos.max(axis=0).tolist()

    for nodo in j["nodes"]:
        nombre = nodo.get("name")
        if nombre not in cambios:
            continue
        nuevo = cambios[nombre]
        offset = 0
        escala, traslado = np.array(nodo.get("scale", [1, 1, 1])), np.array(nodo.get("translation", [0, 0, 0]))
        for prim in j["meshes"][nodo["mesh"]]["primitives"]:
            i = prim["attributes"]["POSITION"]
            cantidad = j["accessors"][i]["count"]
            p = nuevo[offset:offset + cantidad]
            local = (p[:, [0, 2, 1]] * [1, 1, -1] - traslado) / escala
            escribir_acceso(i, local)
            # Normales por posición, para no conservar el sombreado del bulto viejo.
            v, f = mallas[nombre]
            seleccion = f[(f.min(axis=1) >= offset) & (f.max(axis=1) < offset + cantidad)] - offset
            normales = np.zeros_like(local)
            tri = local[seleccion]
            bruta = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
            for k in range(3):
                np.add.at(normales, seleccion[:, k], bruta)
            normales /= np.maximum(np.linalg.norm(normales, axis=1, keepdims=True), 1e-12)
            if "NORMAL" in prim["attributes"]:
                escribir_acceso(prim["attributes"]["NORMAL"], normales)
            offset += cantidad
    texto = json.dumps(j, separators=(",", ":")).encode()
    texto += b" " * ((-len(texto)) % 4)
    nuevo_glb = struct.pack("<III", 0x46546C67, 2, 28 + len(texto) + len(binario))
    nuevo_glb += struct.pack("<I4s", len(texto), b"JSON") + texto
    nuevo_glb += struct.pack("<I4s", len(binario), b"BIN\0") + bytes(binario)
    a.salida.mkdir(parents=True, exist_ok=True)
    archivo = a.salida / "dos-hermanas.glb.gz"
    archivo.write_bytes(gzip.compress(nuevo_glb, mtime=0))
    ficha = json.loads(a.entrada.with_name("dos-hermanas.json").read_text())
    ficha["sha256_glb"] = hashlib.sha256(nuevo_glb).hexdigest()
    ficha["bytes_gzip"] = archivo.stat().st_size
    ficha["ajuste_alzado"] = dict(factor_casquetes=a.factor_casquetes, pozos="reduccion_saliente_cupulines.json",
                                 sha256_script=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    verificacion = a.verificacion
    if verificacion.exists():
        control = json.loads(verificacion.read_text())
        if control["despues"]["sha256_glb"] == ficha["sha256_glb"]:
            ficha["controles_antes_del_ajuste"] = ficha.pop("comprobacion_boca", {})
            ficha["comprobacion_boca"] = dict(rayos_por_vista=4225,
                metodo="GLB importado; mismas cámaras y destinos antes/después",
                antes=control["antes"]["boca"], despues=control["despues"]["boca"])
            ficha["verificacion_alturas"] = dict(
                archivo=str(verificacion.relative_to(ROOT)),
                sha256=hashlib.sha256(verificacion.read_bytes()).hexdigest(),
                cobertura=control["despues"]["cobertura"], sector=control["despues"]["sector"])
    ficha["iluminacion_vertices"] = "Conservada del control 0038; no recalculada tras el ajuste geométrico"
    (a.salida / "dos-hermanas.json").write_text(json.dumps(ficha, indent=2) + "\n")
    releido = leer(archivo)
    errores = []
    for nombre, (v, f) in mallas.items():
        p, ff = releido[nombre]
        assert np.array_equal(f, ff)
        esperado = cambios.get(nombre, v)
        error = float(np.max(np.linalg.norm(esperado - p, axis=1)))
        assert error < 1e-6
        errores.append(error)
    registro = json.loads((ROOT / "datos/registro_foto_ferrer.json").read_text())
    foto = Image.open(ROOT / "docs/Foto de Ferrer.png").convert("RGB")
    if not a.sin_laminas:
        imagen = pintar(releido, registro, foto.size)
        imagen.save(ROOT / "renders/previas/0040_alzado/modelo_corregido.png")
        revision = ROOT / "web/estudio_alzado"
        revision.mkdir(parents=True, exist_ok=True)
        imagen.save(revision / "despues.png")
        Image.open(ROOT / "renders/previas/0040_alzado/modelo_antes.png").save(revision / "antes.png")
    informe = dict(casquetes=controles, pozos_corregidos=16, error_relectura_max_m=max(errores),
                   sha256_entrada=hashlib.sha256(a.entrada.read_bytes()).hexdigest(),
                   sha256_salida=hashlib.sha256(archivo.read_bytes()).hexdigest(),
                   fuente_foto=registro, topologia="Inalterada; mismos triángulos y coordenadas XY de los casquetes",
                   controles_previos=ficha.get("comprobacion_boca"),
                   limite="Los controles de visibilidad previos no se revalidan por copiar la ficha; comprobar el candidato")
    a.informe.write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n")
    print(dict(casquetes=len(controles), pozos=16, error=max(errores), salida=str(archivo)))


if __name__ == "__main__":
    main()
