"""Direcciones descendentes en los extremos fallidos de 0022.

Separa dos causas de parada sobre la MISMA superficie bilineal de 0022:
- fallo de direccion: en el extremo existe alguna direccion que baja H, o
  existe un camino monotono certificado hasta la cota previa;
- encierro: el extremo es minimo local y, ademas, no hay escape del subnivel
  {H <= H(inicio)} en la rejilla (barrera minimax de 0020).

Certificado positivo: caminos por aristas paralelas a los ejes, en la rejilla
original (k=1) y subdividida (k=4). Sobre esas aristas la bilineal es lineal,
asi que la monotonia se comprueba exactamente con los extremos. La ausencia
de camino por aristas NO prueba que no exista otro camino monotono.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from collections import deque
from pathlib import Path

import numpy as np
import scipy

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from granada.campo import Campo, campo
from granada.cupula import CATETO_M, FAMILIAS
from granada.hiladas_campo import frentes, hilada_de
from scripts.diagnosticar_paradas_campo import barrera_minimax
from scripts.ensayar_transporte_interior import subida_segmento, valor_gradiente

TOL_PENDIENTE = 1e-12   # catetos de H por cateto horizontal
TOL_SUBIDA = 1e-10      # misma tolerancia por tramos que 0022
DIRECCIONES = 720


def gradiente_en_celda(c: Campo, p, i: int, j: int) -> np.ndarray:
    """Derivada de la bilineal de la celda (i, j) evaluada en p (puede estar en su borde)."""
    u = (p[0]-c.x[j])/c.paso
    v = (p[1]-c.y[i])/c.paso
    a, b = c.H[i, j], c.H[i, j+1]
    d, e = c.H[i+1, j], c.H[i+1, j+1]
    return np.array([(1-v)*(b-a)+v*(e-d), (1-u)*(d-a)+u*(e-b)])/c.paso


def celda_hacia(c: Campo, p, d, delta=1e-9):
    """Celda en la que entra p+t*d para t>0 pequeno; None si sale de la rejilla."""
    u = (p[0]-c.x[0])/c.paso+delta*d[0]
    v = (p[1]-c.y[0])/c.paso+delta*d[1]
    if not (0 <= u <= len(c.x)-1 and 0 <= v <= len(c.y)-1):
        return None
    return min(int(np.floor(v)), len(c.y)-2), min(int(np.floor(u)), len(c.x)-2)


def paso_aceptable(c: Campo, p, d):
    """Mayor paso paso/2*2^-k, k<32 (los 32 intentos de 0022), que baja H sin subida por tramos."""
    h = valor_gradiente(c, p)[0]
    s = c.paso/2
    for _ in range(32):
        q = p+s*d
        try:
            if valor_gradiente(c, q)[0] < h and subida_segmento(c, p, q) <= TOL_SUBIDA:
                return s
        except ValueError:
            pass
        s /= 2
    return None


def direcciones(c: Campo, p, g_metodo=None):
    """Pendiente unilateral en DIRECCIONES angulos y en -grad de cada celda contigua."""
    angulos = list(np.linspace(0, 2*np.pi, DIRECCIONES, endpoint=False))
    for d0 in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        celda = celda_hacia(c, p, np.array(d0, float))
        if celda is not None:
            g = gradiente_en_celda(c, p, *celda)
            if np.linalg.norm(g) > 0:
                angulos.append(float(np.arctan2(-g[1], -g[0]) % (2*np.pi)))
    filas = []
    for t in angulos:
        d = np.array([np.cos(t), np.sin(t)])
        celda = celda_hacia(c, p, d)
        if celda is None:
            continue
        filas.append((t, float(gradiente_en_celda(c, p, *celda) @ d), celda))
    descendentes = [f for f in filas if f[1] < -TOL_PENDIENTE]
    mejor = min(filas, key=lambda f: f[1])
    d_mejor = np.array([np.cos(mejor[0]), np.sin(mejor[0])])
    r = {"direcciones_evaluadas": len(filas),
         "direcciones_descendentes": len(descendentes),
         "fraccion_descendente": len(descendentes)/len(filas),
         "pendiente_minima": mejor[1], "angulo_pendiente_minima_grados": float(np.degrees(mejor[0])),
         "paso_aceptable_en_pendiente_minima": paso_aceptable(c, p, d_mejor) if mejor[1] < -TOL_PENDIENTE else None,
         "celdas_contiguas": sorted({tuple(map(int, f[2])) for f in filas}),
         "celdas_con_descenso": sorted({tuple(map(int, f[2])) for f in descendentes})}
    if g_metodo is not None and np.linalg.norm(g_metodo) > 0:
        d = -g_metodo/np.linalg.norm(g_metodo)
        celda = celda_hacia(c, p, d)
        r["pendiente_direccion_metodo"] = (float(gradiente_en_celda(c, p, *celda) @ d)
                                           if celda is not None else None)
        r["paso_aceptable_direccion_metodo"] = paso_aceptable(c, p, d)
    return r


def posicion_en_rejilla(c: Campo, p):
    u = (p[0]-c.x[0])/c.paso
    v = (p[1]-c.y[0])/c.paso
    return {"distancia_nodo_celdas": float(np.hypot(u-round(u), v-round(v))),
            "distancia_arista_celdas": float(min(abs(u-round(u)), abs(v-round(v))))}


def nodos_iniciales(c: Campo, p, k: int):
    """Nodos de la rejilla subdividida k veces alcanzables desde p por segmento monotono."""
    h = valor_gradiente(c, p)[0]
    u = (p[0]-c.x[0])/c.paso*k
    v = (p[1]-c.y[0])/c.paso*k
    salida = []
    for i in {int(np.floor(v)), int(np.ceil(v))}:
        for j in {int(np.floor(u)), int(np.ceil(u))}:
            q = np.array([c.x[0]+j*c.paso/k, c.y[0]+i*c.paso/k])
            try:
                if valor_gradiente(c, q)[0] <= h and subida_segmento(c, p, q) <= TOL_SUBIDA:
                    salida.append((i, j))
            except ValueError:
                pass
    return salida


def alcance_monotono(c: Campo, p, cota, k: int, semiancho: float):
    """BFS por aristas de la rejilla subdividida: solo se baja o se sigue a igual altura.

    Ventana cuadrada de semiancho dado (catetos) centrada en p. Devuelve el
    camino testigo si alcanza un nodo con H<=cota (la ultima arista cruza la
    cota de forma lineal y monotona).
    """
    paso = c.paso/k
    ic = int(round((p[1]-c.y[0])/paso))
    jc = int(round((p[0]-c.x[0])/paso))
    m = int(np.ceil(semiancho/paso))
    imax, jmax = (len(c.y)-1)*k, (len(c.x)-1)*k
    i0, i1 = max(0, ic-m), min(imax, ic+m)
    j0, j1 = max(0, jc-m), min(jmax, jc+m)
    ys = c.y[0]+np.arange(i0, i1+1)*paso
    xs = c.x[0]+np.arange(j0, j1+1)*paso
    # Valores exactos de la bilineal en la subrejilla (map por celdas originales).
    U = (xs-c.x[0])/c.paso
    V = (ys-c.y[0])/c.paso
    J = np.minimum(np.floor(U).astype(int), len(c.x)-2)
    I = np.minimum(np.floor(V).astype(int), len(c.y)-2)
    fu, fv = U-J, V-I
    H00 = c.H[np.ix_(I, J)]
    H01 = c.H[np.ix_(I, J+1)]
    H10 = c.H[np.ix_(I+1, J)]
    H11 = c.H[np.ix_(I+1, J+1)]
    FU, FV = np.meshgrid(fu, fv)
    W = (1-FV)*((1-FU)*H00+FU*H01)+FV*((1-FU)*H10+FU*H11)
    inicio = [(i-i0, j-j0) for i, j in nodos_iniciales(c, p, k) if i0 <= i <= i1 and j0 <= j <= j1]
    padres = {n: None for n in inicio}
    cola = deque(inicio)
    llegada = None
    while cola:
        n = cola.popleft()
        if W[n] <= cota:
            llegada = n
            break
        for q in ((n[0]-1, n[1]), (n[0]+1, n[1]), (n[0], n[1]-1), (n[0], n[1]+1)):
            if 0 <= q[0] < W.shape[0] and 0 <= q[1] < W.shape[1] and q not in padres and W[q] <= W[n]:
                padres[q] = n
                cola.append(q)
    alcanzados = np.array(list(padres)) if padres else np.zeros((0, 2), int)
    r = {"k": k, "semiancho_catetos": semiancho, "nodos_iniciales": len(inicio),
         "nodos_alcanzados": len(padres), "alcanza_cota": llegada is not None,
         "toca_borde_ventana": bool(len(alcanzados) and (alcanzados.min(0).min() == 0 or
                                     alcanzados[:, 0].max() == W.shape[0]-1 or
                                     alcanzados[:, 1].max() == W.shape[1]-1)),
         "H_minimo_alcanzado": float(min(W[tuple(a)] for a in alcanzados)) if len(alcanzados) else None}
    if llegada is not None:
        camino = [llegada]
        while padres[camino[-1]] is not None:
            camino.append(padres[camino[-1]])
        camino.reverse()
        xy = np.array([[xs[j], ys[i]] for i, j in camino])
        hs = np.array([W[n] for n in camino])
        # Contraste independiente: valor_gradiente y subida por tramos en cada arista.
        hs2 = np.array([valor_gradiente(c, q)[0] for q in xy])
        subidas = [subida_segmento(c, p, xy[0])]+[subida_segmento(c, a, b) for a, b in zip(xy, xy[1:])]
        r.update(camino_nodos=len(camino),
                 longitud_camino_m=float((np.linalg.norm(xy[0]-p)+np.sum(np.linalg.norm(np.diff(xy, axis=0), axis=1)))*CATETO_M),
                 max_incremento_nodos=float(max(0., np.diff(hs).max())) if len(hs) > 1 else 0.,
                 max_diferencia_evaluadores=float(np.abs(hs-hs2).max()),
                 max_subida_tramos=float(max(subidas)),
                 camino_xy=xy.tolist())
    return r


def barrera_subnivel(c: Campo, p, cota):
    """Barrera minimax de 0020 desde el nodo mas bajo de la celda de p.

    La compara con H(p): si escapar exige superar H(p), hay encierro del
    subnivel en la rejilla (discreto, no prueba de campo continuo).
    """
    u = (p[0]-c.x[0])/c.paso
    v = (p[1]-c.y[0])/c.paso
    esquinas = [(i, j) for i in {int(np.floor(v)), int(np.ceil(v))} for j in {int(np.floor(u)), int(np.ceil(u))}]
    n = min(esquinas, key=lambda t: c.H[t])
    b = barrera_minimax(c.H, n, cota)
    h = valor_gradiente(c, p)[0]
    return {"nodo": list(n), "H_nodo": float(c.H[n]), "H_punto": h,
            "altura_escape": b["altura_escape"] if b else None,
            "exceso_sobre_H_punto": (b["altura_escape"]-h) if b else None}


def clasificar(local, alcances, barrera):
    certificado = any(a["alcanza_cota"] for a in alcances)
    if certificado and local["direcciones_descendentes"]:
        return "fallo_de_direccion_con_camino_certificado"
    if certificado:
        return "minimo_local_con_camino_certificado"
    if barrera["exceso_sobre_H_punto"] is not None and barrera["exceso_sobre_H_punto"] > 0:
        return ("encierro_del_subnivel_discreto" if not local["direcciones_descendentes"]
                else "descenso_local_pero_subnivel_cerrado")
    return "indeterminado_sin_camino_por_aristas"


def main():
    entrada = RAIZ/"datos/ensayo_transporte_interior.json"
    previo = json.loads(entrada.read_text())
    paradas = json.loads((RAIZ/"datos/diagnostico_paradas_campo.json").read_text())
    semillas_0019 = [t for t in paradas["casos"] if t["fila"] > 1]
    referencia = frentes(campo(A=2), filas_por_hilada=2)
    limites = [4*1.6*FAMILIAS[hilada_de(referencia[t["indice_frente"]]).familia].fondo
               * referencia[t["indice_frente"]].escala for t in semillas_0019]
    campos = {r: campo(A=2, resolucion=r) for r in (.03, .015)}
    extremos, semillas = [], []
    for caso in previo["casos"]:
        c = campos[caso["resolucion"]]
        camino = np.asarray(caso["camino_xy"])
        cota, limite = caso["cota_previa"], limites[caso["semilla"]]
        if caso["metodo"] == "bilineal" and caso["umbral"] == 1e-8:
            inicio = camino[0]
            semillas.append({"resolucion": caso["resolucion"], "semilla": caso["semilla"], "fila": caso["fila"],
                             "fallo_original": caso["fallo_original"], "inicio_xy": inicio.tolist(),
                             "alcances": [alcance_monotono(c, inicio, cota, k, limite) for k in (1, 4)],
                             "barrera": barrera_subnivel(c, inicio, cota)})
        if caso["alcanza_cota"]:
            continue
        p = camino[-1]
        h, g = valor_gradiente(c, p)
        if abs(h-cota-caso["error_cota_catetos"]) > 1e-12:
            raise ValueError("el extremo no reproduce la altura de 0022")
        if caso["metodo"] == "interpolado":
            from granada.hiladas_campo import _gradiente
            gx, gy = _gradiente(c)(np.array([p[0]]), np.array([p[1]]))
            g = np.array([gx[0], gy[0]])
        local = direcciones(c, p, g)
        alcances = [alcance_monotono(c, p, cota, k, limite) for k in (1, 4)]
        barrera = barrera_subnivel(c, p, cota)
        r = {"resolucion": caso["resolucion"], "semilla": caso["semilla"], "fila": caso["fila"],
             "fallo_original": caso["fallo_original"], "metodo": caso["metodo"], "umbral": caso["umbral"],
             "parada_0022": caso["parada"], "extremo_xy": p.tolist(), "H_sobre_cota": h-cota,
             "norma_gradiente_metodo": float(np.linalg.norm(g)),
             "posicion": posicion_en_rejilla(c, p), "local": local,
             "alcances": alcances, "barrera": barrera}
        r["clase"] = clasificar(local, alcances, barrera)
        extremos.append(r)
        print(r["resolucion"], r["semilla"], r["metodo"], r["umbral"], r["parada_0022"], r["clase"],
              local["direcciones_descendentes"], [a["alcanza_cota"] for a in alcances],
              barrera["exceso_sobre_H_punto"], flush=True)
    for s in semillas:
        print("semilla", s["resolucion"], s["semilla"], [a["alcanza_cota"] for a in s["alcances"]],
              s["barrera"]["exceso_sobre_H_punto"], flush=True)
    resumen = {}
    for r in extremos:
        resumen[r["clase"]] = resumen.get(r["clase"], 0)+1
    fuentes = ["scripts/diagnosticar_direcciones_extremos.py", "scripts/ensayar_transporte_interior.py",
               "scripts/diagnosticar_paradas_campo.py", "granada/campo.py", "granada/hiladas_campo.py",
               "granada/cupula.py", "datos/diagnostico_paradas_campo.json"]
    informe = {
        "alcance": "Extremos fallidos de 0022 (42) y sus semillas; A=2, B, borde libre. Sin bandas, piezas ni solidos.",
        "metodo": ("Pendiente unilateral en 720 direcciones y -grad de cada celda contigua; paso aceptable con el "
                   "criterio de 0022; BFS monotono por aristas de rejilla k=1 y k=4 dentro del limite de recorrido; "
                   "barrera minimax de 0020 desde la esquina mas baja"),
        "tolerancias": {"pendiente": TOL_PENDIENTE, "subida_tramos": TOL_SUBIDA},
        "advertencia": ("Camino por aristas = certificado de existencia. Su ausencia no prueba encierro; "
                        "el encierro discreto solo se afirma si la barrera minimax supera H del extremo."),
        "entorno": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "entrada_sha256": hashlib.sha256(entrada.read_bytes()).hexdigest(),
        "sha256": {p: hashlib.sha256((RAIZ/p).read_bytes()).hexdigest() for p in fuentes},
        "resumen_clases": resumen, "extremos": extremos, "semillas": semillas}
    (RAIZ/"datos/direcciones_extremos.json").write_text(json.dumps(informe, ensure_ascii=False, indent=2)+"\n")


if __name__ == "__main__":
    main()
