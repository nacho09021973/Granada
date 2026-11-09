"""Diagnostico reproducible de la banda parametrizada por colocar().

No cuenta intersecciones 3D entre solidos. Busca inversiones locales de la
banda (s, profundidad), error H respecto a la cota anterior y, por otra via,
distancia geometrica a sus contornos. Control independiente: cono A=0.
Produce JSON y SVG permanentes, sin cambiar el modelo ni calibrar A.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.ndimage import map_coordinates
from scipy.spatial import cKDTree

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from granada.campo import campo, curvas
from granada.cupula import CATETO_M, FAMILIAS
from granada.hiladas_campo import _contiene_origen, _gradiente, colocar, frentes, hilada_de
from granada.piezas import pieza


def alturas(c, xy):
    xy = np.asarray(xy)
    return map_coordinates(c.H, [(xy[..., 1] - c.y[0]) / c.paso,
                                 (xy[..., 0] - c.x[0]) / c.paso], order=1, mode="nearest")


def banda(c, f, ds=0.06, capas=20):
    h = hilada_de(f)
    fondo = FAMILIAS[h.familia].fondo * f.escala
    s = np.linspace(0, f.largo, max(32, int(np.ceil(f.largo / ds))) + 1)
    q = np.linspace(0, 1, capas + 1)
    S, Q = np.meshgrid(s, q)
    V = np.column_stack([S.ravel(), -Q.ravel() * fondo, np.zeros(S.size)])
    xy = np.asarray(colocar(V, f, _gradiente(c), 0, 1, fondo))[:, :2].reshape(*S.shape, 2)
    # Dos triangulos por rectangulo. El signo esperado se obtiene del sentido
    # del frente, no de su imagen deformada: tangente x exterior = -area.
    p = f.puntos
    orientacion = -np.sign(np.sum(p[:-1, 0] * p[1:, 1] - p[1:, 0] * p[:-1, 1]))
    a, b, d, e = xy[:-1, :-1], xy[:-1, 1:], xy[1:, :-1], xy[1:, 1:]
    def det(u, v):
        return u[..., 0] * v[..., 1] - u[..., 1] * v[..., 0]
    areas = np.stack([det(b-a, d-a), det(e-b, d-b)]) * orientacion
    residuo = alturas(c, xy[-1]) - f.cota
    return s, q, xy, areas, residuo


def diagnosticar(c, ds=0.06, capas=20):
    filas, detalles = [], []
    for k, f in enumerate(frentes(c, filas_por_hilada=2)):
        s, q, xy, areas, residuo = banda(c, f, ds, capas)
        # Muestras de los contornos de la cota previa: comprobacion geometrica
        # que no depende del gradiente usado para colocar las piezas.
        anteriores = curvas(c, f.cota) if f.cota > 0 else []
        distancia = cKDTree(np.vstack(anteriores)).query(xy[-1])[0] if anteriores else None
        r = {"indice_frente": k, "fila": f.indice, "familia": hilada_de(f).familia,
             "anillo": _contiene_origen(f.puntos),
             "piezas": hilada_de(f).piezas, "triangulos_banda": areas.size,
             "triangulos_invertidos": int(np.count_nonzero(areas < -1e-10)),
             "error_cota_max_en_pasos": float(np.max(np.abs(residuo)) / f.paso),
             "error_cota_p95_en_pasos": float(np.quantile(np.abs(residuo), .95) / f.paso),
             "distancia_a_contorno_previo_max_m": None if distancia is None else float(distancia.max() * CATETO_M),
             "tolerancia_distancia_m": 2 * c.paso * CATETO_M,
             "extremos_lejos_de_contorno_previo": None if distancia is None else int(np.count_nonzero(distancia > 2*c.paso))}
        filas.append(r)
        detalles.append((f, s, q, xy, areas, residuo))
    return filas, detalles


def probar_flujo(c, detalle, muestras=33, ventana=True):
    """Ensayo local: seguir -grad H normalizado hasta H=cota previa.

    Se conserva cada fallo; el limite de recorrido es cuatro veces el fondo
    maximo admitido por la colocacion actual. No se sustituyen las piezas.
    El error de cota se contrasta con distancia a los contornos previos.
    """
    f, s, q, xy, areas, residuo = detalle
    g = _gradiente(c)
    limite = 4 * 1.6 * FAMILIAS[hilada_de(f).familia].fondo * f.escala
    anteriores = curvas(c, f.cota)
    arbol = cKDTree(np.vstack(anteriores)) if anteriores else None
    trayectorias, registros = [], []
    centro = int(np.argmax(np.abs(residuo)))
    # Ventana contigua alrededor del peor extremo, separacion <= ds.
    objetivos_s = ((s[centro] + np.linspace(-.96, .96, muestras)) % f.largo
                   if ventana else np.linspace(0, f.largo, muestras, endpoint=False))
    indices = np.minimum(np.searchsorted(s, objetivos_s), len(s)-2)
    bandas = []
    for i in indices:
        def rhs(t, p):
            gx, gy = g(np.array([p[0]]), np.array([p[1]]))
            v = np.array([gx[0], gy[0]])
            return -v / max(np.linalg.norm(v), 1e-9)
        def llegada(t, p):
            return float(alturas(c, np.asarray(p)[None, :])[0] - f.cota)
        llegada.terminal = True
        llegada.direction = -1
        def estacionario(t, p):
            gx, gy = g(np.array([p[0]]), np.array([p[1]]))
            return float(np.hypot(gx[0], gy[0]) - .01)
        estacionario.terminal = True
        estacionario.direction = -1
        sol = solve_ivp(rhs, (0, limite), xy[0, i], events=(llegada, estacionario),
                        max_step=c.paso/2, rtol=1e-5, atol=1e-7)
        fin = sol.y[:, -1]
        exito = bool(len(sol.t_events[0]))
        hs = alturas(c, sol.y.T)
        registros.append({"s": float(s[i]), "alcanza_cota": exito,
                          "error_cota_en_pasos": float(llegada(0, fin) / f.paso),
                          "distancia_contorno_m": None if arbol is None else float(arbol.query(fin)[0] * CATETO_M),
                          "H_decrece": bool(np.all(np.diff(hs) <= 1e-8)),
                          "aumento_H_max_en_pasos": float(max(0, np.diff(hs).max()) / f.paso),
                          "recorrido_m": float(sol.t[-1] * CATETO_M),
                          "parada": "cota" if exito else "estacionario" if len(sol.t_events[1]) else "limite_o_error",
                          "integrador_exito": bool(sol.success)})
        trayectorias.append(sol.y.T)
        objetivos = f.indice * f.paso - q * f.paso
        bandas.append(np.column_stack([np.interp(objetivos, hs[::-1], sol.y[d, ::-1]) for d in (0, 1)]))
    # Solo se evalua la banda si todas las trayectorias llegan y H decrece.
    # Esto no prueba inyectividad global ni ausencia de intersecciones 3D.
    invertidos = None
    if ventana and all(r["alcanza_cota"] and r["H_decrece"] for r in registros):
        B = np.asarray(bandas).transpose(1, 0, 2)
        a, b, d, e = B[:-1, :-1], B[:-1, 1:], B[1:, :-1], B[1:, 1:]
        P = f.puntos
        signo = -np.sign(np.sum(P[:-1, 0]*P[1:, 1]-P[1:, 0]*P[:-1, 1]))
        def det(u, v):
            return u[..., 0]*v[..., 1]-u[..., 1]*v[..., 0]
        areas = np.stack([det(b-a, d-a), det(e-b, d-b)])*signo
        invertidos = int(np.count_nonzero(areas < -1e-10))
    return registros, trayectorias, invertidos


def dibujar(c, detalle, salida, trayectorias=()):
    f, s, q, xy, areas, residuo = detalle
    i = int(np.argmax(np.abs(residuo)))
    centro = xy[-1, i]
    W, H = 1200, 640
    def punto(p):
        return (300 + (p[0] - centro[0]) * 170, 335 - (p[1] - centro[1]) * 170)
    def polilinea(P, color, grosor=1):
        pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in map(punto, P))
        return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{grosor}"/>'
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           '<rect width="1200" height="640" fill="white"/>',
           f'<text x="20" y="25">Diagnostico A={c.A}; fila {f.indice}; franja local, no intersecciones 3D</text>',
           '<defs><clipPath id="planta"><rect x="20" y="65" width="560" height="540"/></clipPath></defs>',
           '<g clip-path="url(#planta)">']
    for P in curvas(c, f.cota):
        out.append(polilinea(P, "#20934a", 2))
    out.append(polilinea(f.puntos, "#245fbc", 2))
    out.append(polilinea(xy[-1], "#d03532", 2))
    for j in range(max(0, i-12), min(len(s), i+13), 2):
        out.append(polilinea(xy[:, j], "#999"))
    for P in trayectorias:
        out.append(polilinea(P, "#d58400", 1.5))
    # Plantas individuales de cinco piezas contiguas, con sus bordes
    # muestreados antes de deformar: las rectas locales dejan de ser rectas.
    h = hilada_de(f)
    fam = FAMILIAS[h.familia]
    paso = fam.paso_tangencial * h.estiramiento
    centro_pieza = int(s[i] / paso)
    for j in range(centro_pieza-2, centro_pieza+3):
        tipo = h.tipos()[j % h.piezas]
        P = np.asarray(pieza(tipo).planta)
        vs = []
        for a, b in zip(P, np.roll(P, -1, axis=0)):
            for t in np.linspace(0, 1, 16, endpoint=False):
                v = a*(1-t) + b*t
                vs.append((v[0], v[1]*f.escala, 0))
        vs.append(vs[0])
        mapped = np.asarray(colocar(vs, f, _gradiente(c), j*paso,
                                    h.estiramiento, fam.fondo*f.escala))
        out.append(polilinea(mapped[:, :2], "#a34c9d", 1.5))
    out.extend(['</g>', '<text x="20" y="625">Azul: frente; verde: cota previa; rojo: fondo; naranja: flujo</text>'])
    # Seccion por una trayectoria: H real frente a la bajada lineal esperada.
    valores = (alturas(c, xy[:, i]) - f.cota) / f.paso
    out.append('<text x="650" y="65">Seccion por la trayectoria de mayor error</text>')
    lo, hi = min(-.2, valores.min()), max(1.2, valores.max())
    def graf(v):
        return " ".join(f"{650+500*t:.2f},{540-420*(z-lo)/(hi-lo):.2f}" for t,z in zip(q,v))
    for v, color in [(1-q, "#20934a"), (valores, "#d03532")]:
        out.append(f'<polyline points="{graf(v)}" fill="none" stroke="{color}" stroke-width="2"/>')
    out.append('<text x="650" y="585">Horizontal: profundidad 0 a 1. Verde: H esperado; rojo: H real.</text>')
    out.append(f'<text x="650" y="610">Error final: {residuo[i]/f.paso:.3f} pasos de fila</text></svg>')
    salida.write_text("\n".join(out), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--salida", type=Path, default=RAIZ / "datos/diagnostico_colocacion_campo.json")
    ap.add_argument("--svg", type=Path, default=RAIZ / "renders/diagnostico_colocacion_campo.svg")
    ap.add_argument("--ds", type=float, default=.06)
    ap.add_argument("--capas", type=int, default=20)
    ap.add_argument("--flujo-muestras", type=int, default=33)
    ap.add_argument("--flujo-todos", action="store_true", help="comprueba alcance en 33 puntos repartidos por cada frente; no prueba ausencia de solapes")
    a = ap.parse_args()
    informe = {"parametros": {"ds": a.ds, "capas": a.capas, "filas_por_hilada": 2,
                              "flujo_muestras": a.flujo_muestras, "ventana_flujo_catetos": 1.92},
               "criterio": "Inversion: area orientada < -1e-10; error: H del fondo menos cota previa; distancia > dos celdas de rejilla",
               "limites": "Banda auxiliar muestreada; no cuenta intersecciones 3D ni valida arquitectura historica",
               "python": platform.python_version(), "casos": {}}
    for A in (0, 2):
        c = campo(A=A)
        rs, ds = diagnosticar(c, a.ds, a.capas)
        informe["casos"][str(A)] = {"frentes": rs,
            "triangulos_banda": sum(r["triangulos_banda"] for r in rs),
            "triangulos_invertidos": sum(r["triangulos_invertidos"] for r in rs),
            "error_cota_max_en_pasos": max(r["error_cota_max_en_pasos"] for r in rs)}
        if A == 2:
            # Zona media/interior: anillos de filas 20 a 38. Evita confundir
            # el problema general con el cierre de un lazo minimo.
            candidatos = [k for k,r in enumerate(rs) if 20 <= r["fila"] <= 38 and r["anillo"]]
            k = max(candidatos, key=lambda k: rs[k]["error_cota_max_en_pasos"])
            informe["detalle_svg"] = rs[k]
            registros, trayectorias, inversiones = probar_flujo(c, ds[k], a.flujo_muestras)
            informe["ensayo_flujo"] = {"metodo": "gradiente normalizado, solve_ivp, ventana en el peor extremo del anillo seleccionado; no aplicado al modelo",
                                        "trayectorias": registros,
                                        "triangulos_invertidos_ventana": inversiones,
                                        "triangulos_ventana": 2 * a.capas * (len(registros)-1),
                                        "alcanzan_cota": sum(r["alcanza_cota"] for r in registros)}
            if a.flujo_todos:
                survey = []
                for r, detalle in zip(rs, ds):
                    rr, _, _ = probar_flujo(c, detalle, a.flujo_muestras, ventana=False)
                    survey.append({"indice_frente": r["indice_frente"], "fila": r["fila"],
                                   "muestras": len(rr), "alcanzan_cota": sum(t["alcanza_cota"] for t in rr),
                                   "H_decrece": sum(t["H_decrece"] for t in rr),
                                   "error_cota_max_en_pasos": max(abs(t["error_cota_en_pasos"]) for t in rr),
                                   "fallos": [t for t in rr if not t["alcanza_cota"] or not t["H_decrece"]]})
                informe["flujo_por_frente"] = survey
                informe["resumen_flujo"] = {
                    "muestras": sum(r["muestras"] for r in survey),
                    "alcanzan_cota": sum(r["alcanzan_cota"] for r in survey),
                    "sin_llegada_arranque": sum(r["muestras"]-r["alcanzan_cota"] for r in survey if r["fila"] == 1),
                    "sin_llegada_interior": sum(r["muestras"]-r["alcanzan_cota"] for r in survey if r["fila"] > 1),
                    "violan_monotonia": sum(r["muestras"]-r["H_decrece"] for r in survey),
                }
                print("flujo todos:", sum(r["alcanzan_cota"] for r in survey), "/", sum(r["muestras"] for r in survey))
            a.svg.parent.mkdir(parents=True, exist_ok=True)
            dibujar(c, ds[k], a.svg, trayectorias)
    fuentes = ["scripts/diagnosticar_colocacion_campo.py", "granada/hiladas_campo.py",
               "granada/campo.py", "granada/cupula.py", "granada/piezas.py",
               "datos/red_medinas.json", "datos/registro_red.json", "datos/caras_red.json",
               "datos/niveles_aproximados.json"]
    informe["sha256"] = {p: hashlib.sha256((RAIZ/p).read_bytes()).hexdigest() for p in fuentes}
    import scipy, skimage
    informe["entorno"] = {"numpy": np.__version__, "scipy": scipy.__version__, "skimage": skimage.__version__}
    a.salida.parent.mkdir(parents=True, exist_ok=True)
    a.salida.write_text(json.dumps(informe, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    for A, r in informe["casos"].items():
        print(A, r["triangulos_invertidos"], r["error_cota_max_en_pasos"])
    print("detalle", informe["detalle_svg"])
    print("flujo", informe["ensayo_flujo"]["alcanzan_cota"], "/", a.flujo_muestras,
          "inversiones", informe["ensayo_flujo"]["triangulos_invertidos_ventana"])


if __name__ == "__main__":
    main()
