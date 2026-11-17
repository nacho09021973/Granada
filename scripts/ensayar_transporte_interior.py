"""Ensayo acotado de descenso para los fallos interiores de 0019.

Gradiente de la interpolacion bilineal, descenso con retroceso y comprobacion
de monotonia por tramos de celda. No sustituye colocar() ni resuelve bandas.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.ndimage import map_coordinates
from scipy.optimize import brentq
from scipy.spatial import cKDTree

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from granada.campo import campo, curvas
from granada.cupula import CATETO_M, FAMILIAS
from granada.hiladas_campo import _gradiente, frentes, hilada_de


def valor_gradiente(c, p):
    """Valor y derivada de la MISMA celda bilineal; sin extrapolacion."""
    u = (p[0]-c.x[0])/c.paso
    v = (p[1]-c.y[0])/c.paso
    if not (0 <= u <= len(c.x)-1 and 0 <= v <= len(c.y)-1):
        raise ValueError("fuera de la rejilla")
    j = min(int(np.floor(u)), len(c.x)-2)
    i = min(int(np.floor(v)), len(c.y)-2)
    u, v = u-j, v-i
    a, b = c.H[i, j], c.H[i, j+1]
    d, e = c.H[i+1, j], c.H[i+1, j+1]
    h = (1-v)*((1-u)*a+u*b)+v*((1-u)*d+u*e)
    g = np.array([(1-v)*(b-a)+v*(e-d), (1-u)*(d-a)+u*(e-b)])/c.paso
    return float(h), g


def subida_segmento(c, p, q):
    """Maximo incremento de derivada dH/dt positiva en cada tramo de celda.

    H sobre un segmento es cuadratica en cada celda. Basta evaluar las dos
    derivadas extremas reconstruidas con H(0), H(1/2), H(1).
    """
    ts = [0., 1.]
    for eje, origen in ((0, c.x[0]), (1, c.y[0])):
        if q[eje] == p[eje]:
            continue
        lo, hi = sorted(((p[eje]-origen)/c.paso, (q[eje]-origen)/c.paso))
        for k in range(int(np.floor(lo))+1, int(np.ceil(hi))):
            t = (origen+k*c.paso-p[eje])/(q[eje]-p[eje])
            if 0 < t < 1:
                ts.append(t)
    ts = sorted(set(ts))
    subida = 0.
    for a, b in zip(ts, ts[1:]):
        ha, hm, hb = [valor_gradiente(c, p+t*(q-p))[0] for t in (a, (a+b)/2, b)]
        subida = max(subida, 4*hm-3*ha-hb, 3*hb+ha-4*hm)
    return float(subida)


def descender(c, inicio, cota, limite, metodo="bilineal", umbral=1e-8):
    p = np.asarray(inicio, dtype=float)
    recorrido = 0.
    camino = [p.tolist()]
    g_interpolado = _gradiente(c) if metodo == "interpolado" else None
    parada = "iteraciones"
    for _ in range(4000):
        h, g = valor_gradiente(c, p)
        if abs(h-cota) <= 1e-9:
            parada = "cota"
            break
        if h < cota:
            parada = "inicio_bajo_cota"
            break
        if g_interpolado is not None:
            gx, gy = g_interpolado(np.array([p[0]]), np.array([p[1]]))
            g = np.array([gx[0], gy[0]])
        norma = np.linalg.norm(g)
        if norma < umbral:
            parada = "gradiente_pequeno"
            break
        paso = min(c.paso/2, limite-recorrido)
        if paso <= 1e-12:
            parada = "limite_recorrido"
            break
        aceptado = False
        for _ in range(32):
            q = p-paso*g/norma
            try:
                hq, _ = valor_gradiente(c, q)
                if hq <= cota:
                    t = brentq(lambda t: valor_gradiente(c, p+t*(q-p))[0]-cota, 0, 1,
                               xtol=1e-13)
                    q = p+t*(q-p)
                    hq = valor_gradiente(c, q)[0]
                if hq < h and subida_segmento(c, p, q) <= 1e-10:
                    aceptado = True
                    break
            except ValueError:
                pass
            paso /= 2
        if not aceptado or np.linalg.norm(q-p) < 1e-12:
            parada = "sin_paso_descendente"
            break
        recorrido += float(np.linalg.norm(q-p))
        p = q
        camino.append(p.tolist())
    H = [valor_gradiente(c, np.asarray(p))[0] for p in camino]
    max_subida = max((subida_segmento(c, np.asarray(p), np.asarray(q))
                      for p, q in zip(camino, camino[1:])), default=0.)
    return {"parada": parada, "alcanza_cota": parada == "cota",
            "error_cota_catetos": H[-1]-cota,
            "H_decrece": bool(max_subida <= 1e-10),
            "max_subida_tramos": max_subida, "recorrido_m": recorrido*CATETO_M,
            "iteraciones": len(camino)-1, "camino_xy": camino}


def proyectar(c, p, cota):
    """Proyeccion euclidea sobre segmentos del mismo nivel, sin usar indices."""
    mejor, distancia = None, np.inf
    for P in curvas(c, cota):
        a, d = P[:-1], np.diff(P, axis=0)
        normas = np.sum(d*d, axis=1)
        t = np.clip(np.sum((p-a)*d, axis=1)/np.maximum(normas, 1e-30), 0, 1)
        q = a+t[:, None]*d
        ds = np.linalg.norm(q-p, axis=1)
        k = int(np.argmin(ds))
        if ds[k] < distancia:
            mejor, distancia = q[k], float(ds[k])
    if mejor is None:
        raise ValueError("sin contorno para proyectar semilla")
    return mejor, distancia


def main():
    entrada = RAIZ/"datos/diagnostico_paradas_campo.json"
    previo = json.loads(entrada.read_text())
    semillas = [t for t in previo["casos"] if t["fila"] > 1]
    referencia = frentes(campo(A=2), filas_por_hilada=2)
    casos = []
    for resolucion in (.03, .015):
        c = campo(A=2, resolucion=resolucion)  # Borde libre: aislar el interior de 0021.
        for k, t in enumerate(semillas):
            f = referencia[t["indice_frente"]]
            inicio_original = np.asarray(t["inicio_xy"])
            inicio, desplazamiento = (inicio_original, 0.) if resolucion == .03 else proyectar(c, inicio_original, f.indice*f.paso)
            if desplazamiento > 2*.03:
                raise ValueError("proyeccion supera dos celdas originales")
            limite = 4*1.6*FAMILIAS[hilada_de(f).familia].fondo*f.escala
            for metodo, umbral in (("interpolado", .01), ("interpolado", 1e-8), ("bilineal", 1e-8)):
                r = descender(c, inicio, f.cota, limite, metodo, umbral)
                # Segunda evaluacion: interpolador anterior, sin usar la
                # formula ni las derivadas de valor_gradiente().
                P = np.asarray(r["camino_xy"])
                Q = ((P[:-1, None, :]*(1-np.linspace(0, 1, 5)[None, :, None])
                      + P[1:, None, :]*np.linspace(0, 1, 5)[None, :, None]).reshape(-1, 2)
                     if len(P)>1 else P)
                hs = map_coordinates(c.H, [(Q[:, 1]-c.y[0])/c.paso,
                                           (Q[:, 0]-c.x[0])/c.paso], order=1, mode="nearest")
                r["contraste_interpolador"] = {
                    "max_diferencia_H": float(np.max(np.abs(hs-np.array([valor_gradiente(c, p)[0] for p in Q])))),
                    "max_subida_muestras": float(max(0, np.diff(hs).max())) if len(hs)>1 else 0.}
                anteriores = curvas(c, f.cota)
                r["distancia_contorno_previo_m"] = (float(cKDTree(np.vstack(anteriores)).query(P[-1])[0])*CATETO_M
                                                       if anteriores else None)
                r.update(semilla=k, fila=t["fila"], fallo_original=t["parada"],
                         resolucion=resolucion, metodo=metodo, umbral=umbral,
                         desplazamiento_semilla_catetos=desplazamiento,
                         inicio_original_xy=t["inicio_xy"], cota_previa=f.cota,
                         error_cota_inicial=valor_gradiente(c, inicio)[0]-f.indice*f.paso)
                casos.append(r)
                print(resolucion, k, metodo, umbral, r["parada"], r["error_cota_catetos"], flush=True)
    fuentes = ["scripts/ensayar_transporte_interior.py", "granada/campo.py",
               "granada/hiladas_campo.py", "granada/cupula.py", "granada/celdas.py", "granada/piezas.py",
               "datos/red_medinas.json", "datos/registro_red.json", "datos/caras_red.json", "datos/niveles_aproximados.json"]
    resumen = []
    for resolucion in (.03, .015):
        for metodo, umbral in (("interpolado", .01), ("interpolado", 1e-8), ("bilineal", 1e-8)):
            grupo = [r for r in casos if r["resolucion"] == resolucion and r["metodo"] == metodo and r["umbral"] == umbral]
            resumen.append({"resolucion": resolucion, "metodo": metodo, "umbral": umbral,
                "llegadas_siete_paradas": sum(r["alcanza_cota"] for r in grupo if r["fallo_original"] != "cota"),
                "llegada_control_no_monotono": sum(r["alcanza_cota"] for r in grupo if r["fallo_original"] == "cota"),
                "trayectorias_monotonas": sum(r["H_decrece"] for r in grupo),
                "max_desplazamiento_semilla_catetos": max(r["desplazamiento_semilla_catetos"] for r in grupo)})
    informe = {"alcance": "Siete paradas interiores y una llegada no monotona de 0019; no barrido global ni banda ni solidos",
               "criterio": "Llegada |H-cota|<=1e-9; sin subida por tramos >1e-10; sin extrapolacion; limite recorrido de 0019 y 4000 pasos",
               "metodo": "Descenso normalizado con paso <= media celda y hasta 32 retrocesos; derivadas bilineal e interpolada con mismo integrador; sin saltos ni desvio lateral",
               "parametros": {"A": 2, "borde": "libre", "filas_por_hilada": 2,
                              "proyeccion_fina": "Segmento mas cercano del mismo nivel; maximo dos celdas originales"},
               "entorno": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
               "entrada_sha256": hashlib.sha256(entrada.read_bytes()).hexdigest(),
               "sha256": {p: hashlib.sha256((RAIZ/p).read_bytes()).hexdigest() for p in fuentes},
               "resumen": resumen, "casos": casos}
    (RAIZ/"datos/ensayo_transporte_interior.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2)+"\n")


if __name__ == "__main__":
    main()
