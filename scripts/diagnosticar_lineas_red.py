"""Diagnostico: de que grupo de la malla salen las lineas claras de la red.

En los renders del modelo por celdas (granada/celdas.py) la red de medinas se
lee como lineas blancas anchas que dominan la imagen, y estrechar los
caballetes (CABALLETE_M) apenas las cambio. Este script pinta cada clase de
grupo de un color plano y renderiza con el rasterizador del repositorio
(granada/render3d.py), con la misma camara de visitante que
scripts/render_cupula_piezas.py, para ver a que pertenecen.

Clases y colores:
- primera hilada de cada celda (hilada_00): rojo
- segunda hilada (hilada_01): naranja
- resto de hiladas: gris
- cupulilla de cierre: azul
- caballetes y rosetas de la red (red_nudos): cian
- fondo de yeso detras de las celdas: magenta
- cupulines: amarillo
- sala y lo demas: gris oscuro

Uso:
    .venv/bin/python scripts/diagnosticar_lineas_red.py [--lado 1100] [--png ruta]

Salida por defecto: renders/diagnostico_lineas_red.png (vista visitante a la
izquierda, cenital a la derecha) y un recuento de triangulos por clase.

Segunda prueba, para Cycles: `--sin-grupo red_nudos --obj-salida ruta.obj`
copia renders/cupula_red.obj quitando las caras de ese grupo (los vertices se
dejan, para no renumerar) y no renderiza. Despues:
    blender -b -P scripts/render_cycles.py -- --obj ruta.obj --vistas visitante
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.celdas import cupula_red  # noqa: E402
from granada.render3d import rasterizar  # noqa: E402

COLORES = {
    "hilada_00": (220, 40, 40),
    "hilada_01": (240, 150, 30),
    "hilada": (170, 170, 170),
    "cupulilla": (40, 90, 230),
    "red_nudos": (30, 220, 230),
    "fondo": (230, 40, 220),
    "cupulin": (240, 230, 40),
    "otro": (70, 70, 70),
}


def clase(nombre: str) -> str:
    if nombre == "red_nudos":
        return "red_nudos"
    if nombre == "fondo":
        return "fondo"
    if nombre.startswith("cupulin_"):
        return "cupulin"
    if nombre.endswith("_cupulilla"):
        return "cupulilla"
    if "_hilada_00_" in nombre:
        return "hilada_00"
    if "_hilada_01_" in nombre:
        return "hilada_01"
    if "_hilada_" in nombre:
        return "hilada"
    return "otro"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lado", type=int, default=1100)
    ap.add_argument("--supermuestreo", type=int, default=2)
    ap.add_argument("--png", type=Path, default=RAIZ / "renders" / "diagnostico_lineas_red.png")
    ap.add_argument("--sin-grupo", help="grupo del .obj cuyas caras se quitan")
    ap.add_argument("--obj-salida", type=Path)
    a = ap.parse_args()

    if a.sin_grupo:
        fuente = RAIZ / "renders" / "cupula_red.obj"
        quitadas = 0
        dentro = False
        with fuente.open(encoding="utf-8") as fi, a.obj_salida.open("w", encoding="utf-8") as fo:
            for linea in fi:
                if linea.startswith("g "):
                    dentro = linea[2:].strip() == a.sin_grupo
                elif dentro and linea.startswith("f "):
                    quitadas += 1
                    continue
                elif linea.startswith("mtllib "):
                    linea = f"mtllib {(fuente.with_suffix('.mtl')).resolve()}\n"
                fo.write(linea)
        print(f"{quitadas} caras quitadas del grupo {a.sin_grupo} -> {a.obj_salida}")
        return 0

    _, grupos = cupula_red(8, color=False)
    V, F, colores = [], [], []
    cuenta: Counter = Counter()
    for g in grupos:
        nombre, Vg, Fg = g[:3]
        c = clase(nombre)
        cuenta[c] += len(Fg)
        base = len(V)
        V.extend(Vg)
        F.extend((p + base, q + base, r + base) for p, q, r in Fg)
        colores.extend([COLORES[c]] * len(Fg))

    luces = [((0.55, 0.35, -0.75), 0.75), ((-0.6, -0.45, -0.65), 0.3)]
    visitante = ((0.0, -6.0, -14.0), (0.0, 4.0, 9.0), 80.0)
    cenital = ((0.0, 0.0, -13.0), (0.0, 0.001, 10.0), 90.0)
    L = a.lado
    kw = dict(supermuestreo=a.supermuestreo, luces=luces, colores=colores, ambiente=0.6)
    izq, _ = rasterizar(V, F, L, L, perspectiva=visitante, **kw)
    der, _ = rasterizar(V, F, L, L, perspectiva=cenital, **kw)
    lienzo = Image.new("RGB", (2 * L, L))
    lienzo.paste(izq, (0, 0))
    lienzo.paste(der, (L, 0))
    lienzo.save(a.png)
    for c, n in cuenta.most_common():
        print(f"{c:10s} {n:8d} triangulos")
    print(f"-> {a.png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
