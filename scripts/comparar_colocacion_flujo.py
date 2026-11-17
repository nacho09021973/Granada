"""Compara la colocacion por rayo (actual) y por flujo (decision 0024).

Para cada frente de A=2, B, borde libre: triangulos invertidos de la banda,
error de cota en el fondo, profundidad relativa al fondo nominal y razon de
anchos fondo/frente (convergencia de las lineas de flujo). No cuenta
intersecciones 3D de piezas ni valida fidelidad historica.

Uso: /tmp/granada-venv/bin/python scripts/comparar_colocacion_flujo.py
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from granada.campo import campo
from granada.cupula import CATETO_M, FAMILIAS
from granada.hiladas_campo import (_contiene_origen, banda_de_flujo, frentes, hilada_de,
                                   interpolador_suave, poligono_de)
from scripts.diagnosticar_colocacion_campo import alturas, banda


def areas_con_signo(f, xy):
    p = f.puntos
    orientacion = -np.sign(np.sum(p[:-1, 0]*p[1:, 1]-p[1:, 0]*p[:-1, 1]))
    a, b, d, e = xy[:-1, :-1], xy[:-1, 1:], xy[1:, :-1], xy[1:, 1:]

    def det(u, v):
        return u[..., 0]*v[..., 1]-u[..., 1]*v[..., 0]
    return np.stack([det(b-a, d-a), det(e-b, d-b)])*orientacion


def medir(c, f, xy, fondo):
    areas = areas_con_signo(f, xy)
    residuo = alturas(c, xy[-1]) - f.cota
    profundidad = np.linalg.norm(xy[-1]-xy[0], axis=1)/fondo
    ancho0 = np.linalg.norm(np.diff(xy[0], axis=0), axis=1)
    ancho1 = np.linalg.norm(np.diff(xy[-1], axis=0), axis=1)
    razon = ancho1/np.maximum(ancho0, 1e-12)
    return {"triangulos": int(areas.size), "invertidos": int(np.count_nonzero(areas < -1e-10)),
            "error_cota_max_pasos": float(np.abs(residuo).max()/f.paso),
            "error_cota_p95_pasos": float(np.quantile(np.abs(residuo), .95)/f.paso),
            "profundidad_relativa_p05_p50_p95_max": [float(v) for v in np.quantile(profundidad, [.05, .5, .95, 1])],
            "razon_anchos_p05_p50_p95_max": [float(v) for v in np.quantile(razon, [.05, .5, .95, 1])]}


def giro_por_pieza(f, ancho, muestras=8):
    """Cambio de rumbo del frente (grados) a lo largo de un paso tangencial de pieza.

    Las piezas se doblan siguiendo la curva: un giro grande dentro de una
    pieza la arruga, con independencia de como se rellene la banda.
    """
    s = np.arange(0, f.largo, ancho/muestras)
    P = np.column_stack([np.interp(s, f.s, f.puntos[:, 0]), np.interp(s, f.s, f.puntos[:, 1])])
    d = np.roll(P, -1, axis=0)-P
    a = np.unwrap(np.arctan2(d[:, 1], d[:, 0]))
    vuelta = a[-1]-a[0]+(a[1]-a[0])
    a = np.concatenate([a, a[:muestras]+vuelta])
    giro = np.degrees(np.abs(a[muestras:muestras+len(s)]-a[:len(s)]))
    return [float(v) for v in np.quantile(giro, [.5, .95, 1])]


def medir_rigida(c, f, suave, fondo):
    """Giro entre lados consecutivos del poligono y fondos recortados (0025)."""
    pg = poligono_de(c, f, suave)
    T = pg.tangentes
    giro = np.degrees(np.abs(np.arctan2(T[:, 0]*np.roll(T, -1, axis=0)[:, 1]-T[:, 1]*np.roll(T, -1, axis=0)[:, 0], np.sum(T*np.roll(T, -1, axis=0), axis=1))))
    libre = pg.fondo_libre/fondo
    return {"giro_entre_lados_p50_p95_max_grados": [float(v) for v in np.quantile(giro, [.5, .95, 1])],
            "lados_con_giro_mayor_45": int(np.count_nonzero(giro > 45)), "lados": int(len(giro)),
            "fondos_sin_cruce": int(np.count_nonzero(np.isnan(libre))),
            "fondos_recortados": int(np.count_nonzero(np.isnan(libre) | (libre < .35) | (libre > 1.6)))}


def main():
    c = campo(A=2)
    suave = interpolador_suave(c)
    filas = []
    for k, f in enumerate(frentes(c, filas_por_hilada=2)):
        h = hilada_de(f)
        fondo = FAMILIAS[h.familia].fondo*f.escala
        _, _, xy_rayo, _, _ = banda(c, f)
        b = banda_de_flujo(c, f, suave)
        filas.append({"indice_frente": k, "fila": f.indice, "familia": h.familia,
                      "anillo": _contiene_origen(f.puntos), "piezas": h.piezas,
                      "rayo": medir(c, f, xy_rayo, fondo), "flujo": medir(c, f, b.xy, fondo),
                      "rigida": medir_rigida(c, f, suave, fondo),
                      "giro_frente_por_paso_tangencial_p50_p95_max_grados":
                          giro_por_pieza(f, FAMILIAS[h.familia].paso_tangencial*h.estiramiento)})
        r, q = filas[-1]["rayo"], filas[-1]["flujo"]
        print(f"{k:3d} fila {f.indice:2d} {'anillo' if filas[-1]['anillo'] else 'lazo  '} "
              f"inv {r['invertidos']:5d}/{r['triangulos']:6d} -> {q['invertidos']:5d}/{q['triangulos']:6d}  "
              f"err {r['error_cota_max_pasos']:.3f} -> {q['error_cota_max_pasos']:.2e}  "
              f"prof max {r['profundidad_relativa_p05_p50_p95_max'][3]:.2f} -> {q['profundidad_relativa_p05_p50_p95_max'][3]:.2f}  "
              f"razon {q['razon_anchos_p05_p50_p95_max'][0]:.2f}..{q['razon_anchos_p05_p50_p95_max'][3]:.2f}", flush=True)
    total = {m: {"invertidos": sum(r[m]["invertidos"] for r in filas),
                 "triangulos": sum(r[m]["triangulos"] for r in filas),
                 "frentes_con_inversion": sum(r[m]["invertidos"] > 0 for r in filas),
                 "frentes_error_cota_mayor_1e-3_pasos": sum(r[m]["error_cota_max_pasos"] > 1e-3 for r in filas)}
             for m in ("rayo", "flujo")}
    total["rigida"] = {k: sum(r["rigida"][k] for r in filas)
                       for k in ("lados", "lados_con_giro_mayor_45", "fondos_sin_cruce", "fondos_recortados")}
    for anillo in (True, False):
        g = np.array([r["giro_frente_por_paso_tangencial_p50_p95_max_grados"][0] for r in filas if r["anillo"] == anillo])
        total[f"giro_p50_mediana_{'anillos' if anillo else 'lazos'}_grados"] = float(np.median(g))
    print(total)
    fuentes = ["scripts/comparar_colocacion_flujo.py", "scripts/diagnosticar_colocacion_campo.py",
               "granada/campo.py", "granada/hiladas_campo.py", "granada/cupula.py"]
    informe = {"alcance": "A=2, B, borde libre; todos los frentes admitidos. Banda en planta; sin solidos 3D.",
               "metodo": {"rayo": "banda() de 0019: ds 0,06, 20 capas, desplazamiento recto",
                          "flujo": "banda_de_flujo(): spline cubico, dX/dh=-g/|g|^2, RK4, ds = paso de rejilla, 16 capas",
                          "rigida": "poligono_de(): un lado por pieza, fondo por biseccion en la normal, recorte 0,35-1,6"},
               "tolerancias": {"inversion_area": 1e-10},
               "entorno": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
               "sha256": {p: hashlib.sha256((RAIZ/p).read_bytes()).hexdigest() for p in fuentes},
               "cateto_m": CATETO_M, "total": total, "frentes": filas}
    (RAIZ/"datos/comparacion_colocacion_flujo.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2)+"\n")


if __name__ == "__main__":
    main()
