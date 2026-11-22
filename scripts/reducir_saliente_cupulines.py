"""Deforma solo la altura de los pozos, conservando boca y marco.

Los contornos vienen del OBJ auditado; el grupo 00 usa el asiento corregido.
La transformación es monótona a lo largo del eje de cada cupulín.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from granada.cupula import CATETO_M, PENDIENTE
from granada.campo import PASO_VERTICAL
from alzado_ferrer_cupulines import leer, perfil_foto
from PIL import Image


def bocas():
    from contrastar_geometria_campo import bordes
    b = {n: v[::2] * CATETO_M for n, v in bordes().items()}
    b["cupulin_00"] = np.load(ROOT / "renders/previas/piloto_asiento.npz")["v"][:192:2] * CATETO_M
    return b


def transformar(vertices, boca, eje, techo_nuevo):
    origen = boca.mean(axis=0)
    e1 = np.cross([0, 0, 1], eje)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(eje, e1)
    uv = (vertices - origen) @ np.array([e1, e2]).T
    ab = (boca - origen) @ np.array([e1, e2]).T
    tb = (boca - origen) @ eje
    t = (vertices - origen) @ eje
    viejo = float(t.max())
    # 2 cm junto a la boca se conservan sin deformar. El suelo del pozo
    # nunca puede rebasar el nuevo techo.
    margen = 0.02
    minimo = float(tb.max() + margen + 0.005)
    nuevo = max(float(techo_nuevo), minimo)
    nuevo = min(nuevo, viejo)
    interpolador = LinearNDInterpolator(ab, tb)
    base = np.asarray(interpolador(uv))
    fuera = ~np.isfinite(base)
    base[fuera] = NearestNDInterpolator(ab, tb)(uv[fuera])
    rho = np.linalg.norm(uv, axis=1)
    phi = np.arctan2(uv[:, 1], uv[:, 0])
    pb = np.arctan2(ab[:, 1], ab[:, 0])
    limite = np.interp(phi, pb, np.linalg.norm(ab, axis=1), period=2 * np.pi)
    dentro = rho <= limite + 1e-5
    peso = np.clip((t - base - margen) / np.maximum(viejo - base - margen, .005), 0, 1)
    peso[~dentro] = 0
    salida = vertices - peso[:, None] * (viejo - nuevo) * eje
    anclados = (t <= base + margen + 1e-6) | ~dentro
    assert np.max(np.linalg.norm(salida[anclados] - vertices[anclados], axis=1)) < 1e-6
    return salida, dict(techo_anterior_sobre_boca_media_m=viejo,
                       techo_nuevo_sobre_boca_media_m=nuevo, limite_por_boca_m=minimo,
                       reduccion_eje_m=viejo - nuevo, vertices_fijos=int(anclados.sum()),
                       desplazamiento_max_m=float(np.linalg.norm(salida - vertices, axis=1).max()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pasos", type=float, default=2.0)
    ap.add_argument("--entrada", type=Path, default=ROOT / "build/0040_original/modelos/dos-hermanas.glb.gz")
    a = ap.parse_args()
    mallas = leer(a.entrada)
    bb = bocas()
    fase = json.loads((ROOT / "datos/cupulines.json").read_text())["resultado"]["fase_grados"]
    registro = json.loads((ROOT / "datos/registro_foto_ferrer.json").read_text())
    foto = Image.open(ROOT / "docs/Foto de Ferrer.png").convert("RGB")
    superior = perfil_foto(foto)
    resultados = []
    salida_npz = {}
    for k in range(16):
        nombre = f"cupulin_{k:02d}"
        v, _ = mallas[nombre]
        theta = np.radians(fase + k * 22.5)
        eje = np.array([.5 * np.cos(theta), .5 * np.sin(theta), np.cos(np.pi / 6)])
        objetivo = a.pasos * PASO_VERTICAL * CATETO_M * np.cos(np.arctan(PENDIENTE))
        p, d = transformar(v, bb[nombre], eje, objetivo)
        x0, y0 = registro["origen_modelo_px"]
        escala = registro["px_por_m"]
        for etiqueta, puntos in (("antes", v), ("despues", p)):
            x = np.clip(np.rint(x0 + escala * puntos[:, 0]).astype(int), 0, foto.width - 1)
            exceso = puntos[:, 2] - (y0 - superior[x]) / escala
            d[f"exceso_silueta_{etiqueta}_m"] = float(np.nanmax(exceso))
        resultados.append(dict(nombre=nombre, **d))
        salida_npz[nombre] = p
    carpeta = ROOT / "renders/previas/0040_alzado"
    carpeta.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(carpeta / "cupulines_reducidos.npz", **salida_npz)
    informe = dict(pasos_objetivo=a.pasos, cupulines=resultados,
                   sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (
                       a.entrada, Path(__file__),
                       ROOT / "datos/registro_foto_ferrer.json", ROOT / "renders/previas/piloto_asiento.npz")},
                   limite="Dos pasos es un candidato, no una medida obtenida de la fotografía; el perfil y el asiento acotan la corrección")
    (ROOT / "datos/reduccion_saliente_cupulines.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(resultados, indent=2))


if __name__ == "__main__":
    main()
