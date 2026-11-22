"""Candidato: asiento intersectado de los 16 cupulines y altura acotada.

Se mantiene el eje de 30° y la planta local; no se usa la luz para decidir altura.
"""
import hashlib
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import map_coordinates

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import granada.cupula as gc
from granada.campo import campo, PASO_VERTICAL
from granada.cupula import CATETO_M, PENDIENTE
from alzado_ferrer_cupulines import leer, pintar, perfil_foto
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eje", type=float, default=30)
    ap.add_argument("--pasos", type=float, default=2.5)
    ap.add_argument("--nombre", default="asiento_altura")
    a = ap.parse_args()
    gc.EJE_CUPULIN_GRADOS = a.eje
    c = campo(A=3, forma="raiz", borde="octogonal")

    def altura(x, y):
        return float(map_coordinates(c.H, [[(y - c.y[0]) / c.paso], [(x - c.x[0]) / c.paso]], order=1)[0])

    registro = json.loads((ROOT / "datos/registro_foto_ferrer.json").read_text())
    foto = Image.open(ROOT / "docs/Foto de Ferrer.png").convert("RGB")
    superior = perfil_foto(foto)
    modelos = leer(ROOT / "web/modelos/dos-hermanas.glb.gz")
    piezas = {}
    resultados = []
    for k, q in enumerate(gc.cupulines_medidos()):
        n = f"cupulin_{k:02d}"
        # Medir antes el rango del asiento intersectado en el propio marco.
        v0, _, _ = gc.cupulin_estrellado(q, 0, cota=altura, asiento_intersectado=True)
        o, e1, e2, eje = q.marco()
        v0 = np.asarray(v0)
        t = (v0[:192:2] - o) @ eje
        deseado = a.pasos * PASO_VERTICAL * np.cos(np.arctan(PENDIENTE))
        profundidad = max(deseado, float(t.max() - t.mean()) + .025 / CATETO_M)
        v, f, partes = gc.cupulin_estrellado(q, profundidad, cota=altura, asiento_intersectado=True)
        v = np.asarray(v) * CATETO_M
        nombre = n
        modelos[nombre] = (v, np.asarray(f))
        piezas[nombre + "_v"] = v
        piezas[nombre + "_f"] = np.asarray(f)
        piezas[nombre + "_partes"] = np.array(partes)
        px = np.clip(np.rint(registro["origen_modelo_px"][0] + registro["px_por_m"] * v[:, 0]).astype(int), 0, foto.width - 1)
        limite = (registro["origen_modelo_px"][1] - superior[px]) / registro["px_por_m"]
        peor = int(np.nanargmax(v[:, 2] - limite))
        resultados.append(dict(nombre=n, profundidad_eje_m=profundidad * CATETO_M,
                               z_max_m=float(v[:, 2].max()),
                               exceso_silueta_m=float(np.nanmax(v[:, 2] - limite)),
                               punto_exceso_max_m=v[peor].tolist(), limite_en_punto_m=float(limite[peor]),
                               holgura_techo_sobre_boca_m=float((profundidad + t.mean() - t.max()) * CATETO_M)))
    carpeta = ROOT / "renders/previas/0040_alzado"
    carpeta.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(carpeta / f"cupulines_{a.nombre}.npz", **piezas)
    pintar(modelos, registro, foto.size).save(carpeta / f"modelo_{a.nombre}.png")
    informe = dict(parametros=dict(A=3, forma="raiz", borde="octogonal", eje_grados=a.eje,
                                  pasos_objetivo=a.pasos, holgura_min_m=.025),
                   cupulines=resultados,
                   sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (
                       Path(__file__), ROOT / "granada/campo.py", ROOT / "granada/cupula.py",
                       ROOT / "datos/registro_foto_ferrer.json", ROOT / "web/modelos/dos-hermanas.glb.gz")},
                   limite="La silueta es una cota del alzado, no una medida individual de profundidad")
    (ROOT / f"datos/cupulines_{a.nombre}.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(resultados, indent=2))


if __name__ == "__main__":
    main()
