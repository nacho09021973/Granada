"""Barrido del suavizado de frentes para la colocacion 'suavizada' (decision 0026).

Criterio fijado antes de mirar: en los anillos de las filas desordenadas
(13-24 y 30-37) la mediana del giro por paso tangencial debe bajar por
debajo de 25 grados, como en las filas ordenadas, con la menor desviacion
respecto a la curva de nivel real. Mide ademas inversiones de banda, fondos
sin corte y recortados, y piezas. Sin solidos 3D ni validacion historica.

Uso: /tmp/granada-venv/bin/python scripts/barrer_suavizado_frentes.py
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.spatial import cKDTree

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from granada.campo import campo
from granada.cupula import CATETO_M, FAMILIAS
from granada.hiladas_campo import (_contiene_origen, _gradiente, banda_suavizada, frente_suavizado,
                                   frentes, hilada_de, suavizar_curva)
from scripts.comparar_colocacion_flujo import areas_con_signo, giro_por_pieza

SIGMAS = (0.0, 0.35, 0.7, 1.0)
DESORDENADAS = set(range(13, 25)) | set(range(30, 38))
UMBRAL_GIRO = 25.0


def main():
    c = campo(A=2)
    g = _gradiente(c)
    originales = frentes(c, filas_por_hilada=2)
    barrido = []
    for sigma in SIGMAS:
        filas = []
        for k, f0 in enumerate(originales):
            f = frente_suavizado(f0, sigma)
            h = hilada_de(f)
            fondo = FAMILIAS[h.familia].fondo*f.escala
            b = banda_suavizada(c, f, sigma, g)
            areas = areas_con_signo(f, b.xy)
            desvio = cKDTree(suavizar_curva(f0.puntos, 0)).query(f.puntos)[0]
            libre = b.error_cota
            filas.append({"indice_frente": k, "fila": f.indice, "anillo": _contiene_origen(f0.puntos),
                          "piezas": h.piezas,
                          "giro_p50_p95_max_grados": giro_por_pieza(f, FAMILIAS[h.familia].paso_tangencial*h.estiramiento),
                          "desvio_curva_real_max_m": float(desvio.max()*CATETO_M),
                          "desvio_curva_real_p95_m": float(np.quantile(desvio, .95)*CATETO_M),
                          "invertidos": int(np.count_nonzero(areas < -1e-10)), "triangulos": int(areas.size),
                          "fondos_sin_corte": int(np.count_nonzero(np.isnan(libre))),
                          "fondos_recortados": int(np.count_nonzero(np.isnan(libre) | (libre < .35) | (libre > 1.6))),
                          "muestras": int(len(libre))})
        an = [r for r in filas if r["anillo"]]
        des = [r["giro_p50_p95_max_grados"][0] for r in an if r["fila"] in DESORDENADAS]
        orden = [r["giro_p50_p95_max_grados"][0] for r in an if r["fila"] not in DESORDENADAS]
        resumen = {"sigma_catetos": sigma, "sigma_m": sigma*CATETO_M,
                   "giro_p50_max_anillos_desordenados": float(max(des)),
                   "giro_p50_mediana_anillos_desordenados": float(np.median(des)),
                   "giro_p50_mediana_anillos_ordenados": float(np.median(orden)),
                   "cumple_criterio": bool(max(des) < UMBRAL_GIRO),
                   "desvio_max_m": max(r["desvio_curva_real_max_m"] for r in filas),
                   "desvio_p95_max_anillos_m": max(r["desvio_curva_real_p95_m"] for r in an),
                   "invertidos": sum(r["invertidos"] for r in filas),
                   "triangulos": sum(r["triangulos"] for r in filas),
                   "fondos_sin_corte": sum(r["fondos_sin_corte"] for r in filas),
                   "fondos_recortados": sum(r["fondos_recortados"] for r in filas),
                   "muestras": sum(r["muestras"] for r in filas),
                   "piezas": sum(r["piezas"] for r in filas)}
        print(resumen, flush=True)
        barrido.append({"resumen": resumen, "frentes": filas})
    fuentes = ["scripts/barrer_suavizado_frentes.py", "scripts/comparar_colocacion_flujo.py",
               "granada/campo.py", "granada/hiladas_campo.py", "granada/cupula.py"]
    informe = {"alcance": "A=2, B, borde libre; 63 frentes; banda en planta, sin solidos 3D",
               "criterio_previo": f"anillos filas 13-24 y 30-37: mediana de giro por paso tangencial < {UMBRAL_GIRO} grados; menor desvio",
               "entorno": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
               "sha256": {p: hashlib.sha256((RAIZ/p).read_bytes()).hexdigest() for p in fuentes},
               "barrido": barrido}
    (RAIZ/"datos/barrido_suavizado_frentes.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2)+"\n")


if __name__ == "__main__":
    main()
