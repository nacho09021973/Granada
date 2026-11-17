"""Ensayo del borde circular: conexiones radiales de primera fila, no piezas.

Compara el campo libre con una condicion opcional H=0 en r=RADIO_BASE.
Muestrea H por interpolacion bilineal, con control A=0 y dos resoluciones.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
import skimage

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from granada.campo import PASO_VERTICAL, campo, curvas
from granada.cupula import CATETO_M, PENDIENTE, RADIO_BASE
from granada.hiladas_campo import frentes
from scripts.diagnosticar_colocacion_campo import alturas


def diagnosticar(c, muestras=129, capas=200):
    primero = [f for f in frentes(c, filas_por_hilada=2) if f.indice == 1]
    resultados = []
    for f in primero:
        s = np.linspace(0, f.largo, muestras, endpoint=False)
        inicio = np.column_stack([np.interp(s, f.s, f.puntos[:, d]) for d in (0, 1)])
        radios = np.hypot(*inicio.T)
        fin = inicio / radios[:, None] * RADIO_BASE
        q = np.linspace(0, 1, capas+1)
        xy = inicio[None, :, :]*(1-q[:, None, None]) + fin[None, :, :]*q[:, None, None]
        H = alturas(c, xy)
        aumentos = np.diff(H, axis=0)
        # Areas de la banda completa, incluida la junta periodica.
        a = xy[:-1]
        b = np.roll(a, -1, axis=1)
        d = xy[1:]
        e = np.roll(d, -1, axis=1)
        def det(u, v):
            return u[..., 0]*v[..., 1]-u[..., 1]*v[..., 0]
        P = f.puntos
        signo = -np.sign(np.sum(P[:-1, 0]*P[1:, 1]-P[1:, 0]*P[:-1, 1]))
        areas = np.stack([det(b-a, d-a), det(e-b, d-b)])*signo
        resultados.append({"trayectorias": muestras, "capas": capas,
            "aumentan_H": int(np.count_nonzero(np.any(aumentos > 1e-8, axis=0))),
            "aumento_max_catetos": float(max(0, aumentos.max())),
            "H_borde_max_abs_catetos": float(np.max(np.abs(H[-1]))),
            "error_cota_inicial_max_catetos": float(np.max(np.abs(H[0]-f.paso))),
            "extremos_fuera_radio_tolerancia_1e_9": int(np.count_nonzero(np.abs(np.hypot(*fin.T)-RADIO_BASE)>1e-9)),
            "frentes_fuera_dominio": int(np.count_nonzero(radios>RADIO_BASE)),
            "triangulos_invertidos": int(np.count_nonzero(areas < -1e-10)),
            "fondo_max_m": float(np.max(np.abs(RADIO_BASE-radios))*CATETO_M)})
    ceros = curvas(c, 0)
    return {"frentes_primera_fila": len(primero), "bandas": resultados,
            "contornos_H0": len(ceros),
            "error_radio_contorno_H0_max_m": None if not ceros else
                float(max(np.max(np.abs(np.hypot(*p.T)-RADIO_BASE)) for p in ceros)*CATETO_M)}


def main():
    casos = []
    for paso, muestras, capas in ((.03, 129, 200), (.015, 257, 400)):
        for A in (0, 2):
            for borde in ("libre", "circular"):
                c = campo(A=A, resolucion=paso, borde=borde)
                r = diagnosticar(c, muestras, capas)
                r.update(A=A, borde=borde, resolucion=paso)
                r["pasa_criterio_muestreado"] = (
                    r["frentes_primera_fila"] == r["contornos_H0"] == 1
                    and r["error_radio_contorno_H0_max_m"] <= paso*CATETO_M
                    and all(b["aumentan_H"] == b["triangulos_invertidos"]
                            == b["frentes_fuera_dominio"] == 0
                            and b["H_borde_max_abs_catetos"] <= PENDIENTE*paso
                            for b in r["bandas"]))
                casos.append(r)
                print(A, borde, paso, r, flush=True)
    fuentes = ["scripts/diagnosticar_arranque_campo.py", "scripts/diagnosticar_colocacion_campo.py",
               "granada/campo.py", "granada/hiladas_campo.py", "granada/cupula.py",
               "granada/celdas.py", "granada/piezas.py", "datos/red_medinas.json",
               "datos/registro_red.json", "datos/caras_red.json", "datos/niveles_aproximados.json"]
    informe = {"alcance": "Primera fila B; banda radial auxiliar, no colocacion de solidos ni validacion historica",
               "eleccion": "Dominio circular; relieve atenuado por smoothstep tras suavizar en un paso horizontal de hilada; cono firmado fuera solo como extension numerica",
               "criterio": "Sin aumento H >1e-8 por segmento; sin triangulos invertidos; error H borde y radio H0 <= una celda (altura: PENDIENTE*resolucion)",
               "parametros": {"radio_base_catetos": RADIO_BASE, "ancho_atenuacion_catetos": PASO_VERTICAL/PENDIENTE, "filas_por_hilada": 2},
               "entorno": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "skimage": skimage.__version__},
               "sha256": {p: hashlib.sha256((RAIZ/p).read_bytes()).hexdigest() for p in fuentes},
               "casos": casos}
    (RAIZ/"datos/diagnostico_arranque_campo.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2)+"\n")


if __name__ == "__main__":
    main()
