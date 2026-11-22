"""Comprueba cotas e intersecciones del paño en dos GLB, con Blender.

blender -b --python-exit-code 1 -P scripts/comprobar_encaje_pano_glb.py
Las intersecciones cuentan pares de triángulos, no defectos independientes.
"""

import gzip
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np
from mathutils import Vector, Matrix, Quaternion
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from hiladas_ventanas import INFERIOR, SUPERIOR, EJE_PX, FONDO_M


def leer(path):
    datos = gzip.decompress(path.read_bytes())
    n = struct.unpack_from("<I", datos, 12)[0]
    escena = json.loads(datos[20:20 + n])
    inicio = 28 + n

    def acceso(i):
        a = escena["accessors"][i]
        v = escena["bufferViews"][a["bufferView"]]
        dtype = {5126: "<f4", 5125: "<u4", 5123: "<u2"}[a["componentType"]]
        columnas = {"VEC3": 3, "SCALAR": 1}[a["type"]]
        assert v.get("byteStride", columnas * np.dtype(dtype).itemsize) == columnas * np.dtype(dtype).itemsize
        offset = inicio + v.get("byteOffset", 0) + a.get("byteOffset", 0)
        return np.frombuffer(datos, dtype=dtype, offset=offset,
                             count=a["count"] * columnas).reshape(-1, columnas)

    mallas = {}
    for nodo in escena["nodes"]:
        if "mesh" not in nodo:
            continue
        assert "children" not in nodo, "Revisar jerarquía de transformaciones"
        if "matrix" in nodo:
            transformacion = np.asarray(nodo["matrix"]).reshape(4, 4).T
        else:
            q = nodo.get("rotation", [0, 0, 0, 1])
            transformacion = np.asarray(Matrix.LocRotScale(
                Vector(nodo.get("translation", [0, 0, 0])),
                Quaternion((q[3], *q[:3])),
                Vector(nodo.get("scale", [1, 1, 1]))))
        vertices, caras = [], []
        for p in escena["meshes"][nodo["mesh"]]["primitives"]:
            v = acceso(p["attributes"]["POSITION"]).astype(float)
            v = v @ transformacion[:3, :3].T + transformacion[:3, 3]
            f = acceso(p["indices"]).reshape(-1, 3) + len(vertices)
            # GLB: Y vertical; Blender: Z vertical.
            vertices.extend(v[:, [0, 2, 1]] * [1, -1, 1])
            caras.extend(f)
        mallas[nodo["name"]] = (np.array(vertices), np.array(caras))
    return mallas, hashlib.sha256(datos).hexdigest()


def cruce(a, b):
    """Cruce transversal: excluye contactos de borde y caras coplanares."""
    for t, otro in ((a, b), (b, a)):
        normal = np.cross(otro[1] - otro[0], otro[2] - otro[0])
        norma = np.linalg.norm(normal)
        if norma < 1e-12:
            return False
        distancia = (t - otro[0]) @ (normal / norma)
        if distancia.min() >= -1e-6 or distancia.max() <= 1e-6:
            return False
    for t, otro in ((a, b), (b, a)):
        for p, q in zip(t, np.roll(t, -1, axis=0)):
            d = q - p
            if d @ d < 1e-14:
                continue
            hit = intersect_ray_tri(*map(Vector, otro), Vector(d), Vector(p), True)
            if hit is not None:
                fraccion = (np.asarray(hit) - p) @ d / (d @ d)
                if 1e-6 < fraccion < 1 - 1e-6:
                    return True
    return False


def examinar(path):
    mallas, sha = leer(path)
    ficha = json.loads(path.with_name("dos-hermanas.json").read_text())
    apa = ficha["sector_00"]["apotema_m"]
    alzado = json.loads((ROOT / "datos/alzado_sala.json").read_text())
    errores = []
    for fila, tabla in enumerate((INFERIOR, SUPERIOR), 1):
        for k, (_, eje, y) in enumerate(tabla, 1):
            u = (eje - EJE_PX) / alzado["px_por_m"]
            x = apa - FONDO_M[fila - 1]
            z = (alzado["niveles"]["arranque_cupula"]["fila_px"] - y) / alzado["px_por_m"]
            objetivo = np.array([x, u * x / apa, z])
            v, _ = mallas[f"adaraja_00_{fila}_{k:02d}"]
            cerca = v[np.argmin(np.linalg.norm(v[:, :2] - objetivo[:2], axis=1))]
            errores.append(dict(fila=fila, pieza=k, error_z_m=float(cerca[2] - z),
                                error_xy_m=float(np.linalg.norm(cerca[:2] - objetivo[:2]))))
    campo = []
    for nombre, (v, f) in mallas.items():
        if nombre.startswith(("hilada_", "cupulin_", "cupulilla_", "corona_arranque", "Frentes", "Adarajas", "Apoyo")):
            campo.append((nombre, v, f, BVHTree.FromPolygons(v, f, all_triangles=True)))
    cruces = []
    for nombre, (v, f) in mallas.items():
        if not nombre.startswith("adaraja_00_"):
            continue
        arbol = BVHTree.FromPolygons(v, f, all_triangles=True)
        for otro, w, g, bvh in campo:
            pares = arbol.overlap(bvh)
            n = sum(cruce(v[f[i]], w[g[j]]) for i, j in pares)
            if n:
                cruces.append(dict(pieza=nombre, campo=otro, pares_transversales=n))
    apoyos = []
    for nombre, (v, f) in mallas.items():
        if nombre.startswith("Apoyo"):
            t = v[f]
            area_doble = np.linalg.norm(np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), axis=1)
            apoyos.append(dict(nombre=nombre, triangulos=len(f),
                                degenerados=int((area_doble <= 1e-12).sum())))
    return dict(archivo=str(path.relative_to(ROOT)), sha256_glb=sha,
                error_max_cotas_m=max(abs(e["error_z_m"]) for e in errores),
                crestas=errores, cruces=cruces, apoyos=apoyos,
                pares_transversales=sum(c["pares_transversales"] for c in cruces))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", type=Path, default=ROOT / "web/modelos/dos-hermanas.glb.gz")
    ap.add_argument("--despues", type=Path, default=ROOT / "build/encaje-seccion/modelos/dos-hermanas.glb.gz")
    ap.add_argument("--exigir", action="store_true", help="falla si el candidato altera cotas, cruza el campo o tiene apoyos degenerados")
    ap.add_argument("--informe", type=Path, default=ROOT / "datos/comprobacion_encaje_pano_glb.json")
    args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    a = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float)
    b = np.array([[.2, .2, -1], [.2, .2, 1], [.8, .2, 1]])
    assert cruce(a, b)
    assert not cruce(a, a + [0, 0, 1])
    assert not cruce(a, a)
    resultado = dict(
        metodo="Cotas exportadas y BVH con prueba de cruce transversal a 1 micra; excluye contactos coplanares y no prueba separación mínima",
        sha256_script=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        sha256_fuentes={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in (
            "scripts/hiladas_ventanas.py", "scripts/encajar_frentes_visita.py",
            "scripts/exportar_visita_web.py", "datos/alzado_sala.json")},
        variantes=[examinar(p.resolve()) for p in (args.antes, args.despues)],
    )
    args.informe.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False) + "\n")
    for v in resultado["variantes"]:
        print(v["archivo"], v["error_max_cotas_m"], v["pares_transversales"], flush=True)
    if args.exigir:
        candidato = resultado["variantes"][-1]
        assert candidato["error_max_cotas_m"] < 1e-6
        assert candidato["pares_transversales"] == 0
        assert all(p["degenerados"] == 0 for p in candidato["apoyos"])


if __name__ == "__main__":
    main()
