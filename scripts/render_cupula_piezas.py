#!/usr/bin/env python3
"""Apila las hiladas de piezas en cupula y la renderiza.

Salidas:
- `renders/cupula_piezas.png`: vista de un visitante bajo la cupula y vista
  cenital desde el centro, en yeso;
- `renders/cupula_color.png`: las mismas vistas con el color de
  `granada/color.py` (restitucion, no dato);
- `renders/cupula_piezas.obj` y `.mtl`: la malla con su color por cara, para
  el visor web. Es grande y se regenera con este script, por eso esta en
  `.gitignore`;
- `datos/cupula_piezas.json`: el plan de hiladas y los controles.

Supuestos en `granada/cupula.py`.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.color import material, paleta_materiales, rgb  # noqa: E402
from granada.cupula import CATETO_M, PENDIENTE, RADIO_BASE, cupula  # noqa: E402
from granada.piezas import escribir_obj  # noqa: E402
from granada.render3d import rasterizar  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--subdivision", type=int, default=8)
    ap.add_argument("--lado", type=int, default=1100)
    ap.add_argument("--supermuestreo", type=int, default=3, help="muestras por lado de pixel (antialiasing)")
    ap.add_argument("--obj", type=Path, default=RAIZ / "renders" / "cupula_piezas.obj")
    ap.add_argument("--png", type=Path, default=RAIZ / "renders" / "cupula_piezas.png")
    ap.add_argument("--png-color", type=Path, default=RAIZ / "renders" / "cupula_color.png")
    ap.add_argument("--informe", type=Path, default=RAIZ / "datos" / "cupula_piezas.json")
    ap.add_argument("--reparto", default="disperso", choices=("disperso", "anillos"),
                    help="color: yeso con policromia suelta (defecto) o anillos (2026-11-05)")
    ap.add_argument("--solo-obj", action="store_true", help="escribe solo el .obj (para Cycles), sin renders ni informe")
    args = ap.parse_args()

    t0 = time.time()
    hiladas, grupos = cupula(args.subdivision, color=True, reparto=args.reparto)
    escribir_obj(
        args.obj,
        [(n, Vg, Fg, [material(c, s) for c, s in zip(Cg, Sg)]) for n, Vg, Fg, Cg, Sg in grupos],
        paleta=paleta_materiales(),
    )
    if args.solo_obj:
        print(f"-> {args.obj} ({sum(len(g[2]) for g in grupos)} triangulos, {time.time() - t0:.0f} s)")
        return 0
    V, F, colores, sombras = [], [], [], []
    for _, Vg, Fg, Cg, Sg in grupos:
        base = len(V)
        V.extend(Vg)
        F.extend((a + base, b + base, c + base) for a, b, c in Fg)
        colores.extend(rgb(c) for c in Cg)
        sombras.extend(Sg)

    L = args.lado
    # La luz de la sala entra por las ventanas del tambor: de lado y desde abajo.
    luces = [((0.55, 0.35, -0.75), 0.75), ((-0.6, -0.45, -0.65), 0.3)]
    visitante = ((0.0, -6.0, -14.0), (0.0, 4.0, 9.0), 80.0)
    cenital = ((0.0, 0.0, -13.0), (0.0, 0.001, 10.0), 90.0)
    a, _ = rasterizar(V, F, L, L, supermuestreo=args.supermuestreo, luces=luces, perspectiva=visitante)
    b, _ = rasterizar(V, F, L, L, supermuestreo=args.supermuestreo, luces=luces, perspectiva=cenital)
    lienzo = Image.new("RGB", (2 * L, L))
    lienzo.paste(a, (0, 0))
    lienzo.paste(b, (L, 0))
    lienzo.save(args.png)
    # Obra recien acabada: mas luz ambiente para que el yeso llegue a blanco.
    claro = dict(luces=luces, colores=colores, tono=sombras, ambiente=0.6)
    a, _ = rasterizar(V, F, L, L, supermuestreo=args.supermuestreo, perspectiva=visitante, **claro)
    b, _ = rasterizar(V, F, L, L, supermuestreo=args.supermuestreo, perspectiva=cenital, **claro)
    lienzo = Image.new("RGB", (2 * L, L))
    lienzo.paste(a, (0, 0))
    lienzo.paste(b, (L, 0))
    lienzo.save(args.png_color)

    informe = {
        "version": 1,
        "estado": "APPROXIMATE_PIECE_DOME",
        "advertencia": (
            "Cupula de demostracion: secuencia de familias y A3 intercaladas elegidas, "
            "no leidas de Dos Hermanas. Pendiente y radio de arranque, medidos."
        ),
        "modelo": {
            "modulo": "granada/cupula.py",
            "subdivision": args.subdivision,
            "pendiente_medida": PENDIENTE,
            "cateto_m": CATETO_M,
            "radio_base_cateto": RADIO_BASE,
        },
        "controles": {
            "hiladas": len(hiladas),
            "piezas": sum(h.piezas for h in hiladas),
            "estiramiento_min": min(h.estiramiento for h in hiladas),
            "estiramiento_max": max(h.estiramiento for h in hiladas),
            "altura_hiladas_m": (hiladas[-1].cota + hiladas[-1].paso) * CATETO_M,
            "vertices": len(V),
            "triangulos": len(F),
        },
        "hiladas": [asdict(h) for h in hiladas],
    }
    args.informe.write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{informe['controles']['piezas']} piezas, {len(F)} triangulos, {time.time() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
