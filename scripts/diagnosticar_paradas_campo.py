"""Reproduce las paradas de 0019 y mide barreras en la rejilla, sin colocar piezas.

La barrera minimax usa caminos de cuatro vecinos. Es un diagnostico del
campo discreto: no demuestra una obstruccion del campo continuo ni historica.
"""
from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.ndimage import label

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from granada.campo import campo
from granada.cupula import CATETO_M, RADIO_BASE
from granada.hiladas_campo import frentes
from scripts.diagnosticar_colocacion_campo import alturas, banda, probar_flujo


def barrera_minimax(H, inicio, cota):
    """Menor altura maxima necesaria para llegar a un nodo H<=cota.

    Dijkstra con coste maximo, sin diagonales ni extrapolacion. Se devuelve
    tambien un camino testigo y su nodo de altura maxima para auditarlo.
    """
    H = np.asarray(H)
    costes = np.full(H.shape, np.inf)
    costes[inicio] = H[inicio]
    padres = {}
    cola = [(float(H[inicio]), inicio)]
    while cola:
        coste, p = heapq.heappop(cola)
        if coste != costes[p]:
            continue
        if H[p] <= cota:
            camino = [p]
            while camino[-1] != inicio:
                camino.append(padres[camino[-1]])
            camino.reverse()
            cima = max(camino, key=lambda t: H[t])
            return {"altura_escape": coste, "altura_nodo_inicial": float(H[inicio]),
                    "barrera_desde_nodo": float(coste-H[inicio]),
                    "nodo_escape": list(cima), "camino_nodos": [list(t) for t in camino]}
        for q in ((p[0]-1, p[1]), (p[0]+1, p[1]), (p[0], p[1]-1), (p[0], p[1]+1)):
            if not (0 <= q[0] < H.shape[0] and 0 <= q[1] < H.shape[1]):
                continue
            nuevo = max(coste, float(H[q]))
            if nuevo < costes[q]:
                costes[q] = nuevo
                padres[q] = p
                heapq.heappush(cola, (nuevo, q))
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entrada", type=Path, default=RAIZ/"datos/diagnostico_colocacion_campo.json")
    ap.add_argument("--salida", type=Path, default=RAIZ/"datos/diagnostico_paradas_campo.json")
    a = ap.parse_args()
    previo = json.loads(a.entrada.read_text())
    c = campo(A=2)
    fs = frentes(c, filas_por_hilada=2)
    casos = []
    for r in previo["flujo_por_frente"]:
        if not r["fallos"]:
            continue
        f = fs[r["indice_frente"]]
        assert f.indice == r["fila"]
        detalle = (f, *banda(c, f, previo["parametros"]["ds"], previo["parametros"]["capas"]))
        rr, _, _ = probar_flujo(c, detalle, ventana=False,
                                posiciones_s=[t["s"] for t in r["fallos"]])
        for t in rr:
            p = np.asarray(t["fin_xy"])
            nodo = (int(np.clip(round((p[1]-c.y[0])/c.paso), 0, len(c.y)-1)),
                    int(np.clip(round((p[0]-c.x[0])/c.paso), 0, len(c.x)-1)))
            t.update(indice_frente=r["indice_frente"], fila=f.indice, cota_previa=f.cota)
            if f.indice == 1:
                t["distancia_radio_arranque_m"] = float((np.linalg.norm(p)-RADIO_BASE)*CATETO_M)
                t["H_fin_interpolada"] = float(alturas(c, p[None, :])[0])
            # H=0 es una meseta exterior; se estudia aparte del interior.
            if f.indice > 1 and not t["alcanza_cota"]:
                b = barrera_minimax(c.H, nodo, f.cota)
                t["escape_rejilla"] = b
                t["H_fin_interpolada"] = float(alturas(c, p[None, :])[0])
                t["desajuste_nodo_fin"] = float(c.H[nodo]-t["H_fin_interpolada"])
                if b is not None:
                    # Segunda via: componentes conexas justo en el umbral y
                    # por debajo, sin usar los padres ni costes de Dijkstra.
                    def conecta(mascara):
                        L, _ = label(mascara)
                        return bool(L[nodo] and np.any((L == L[nodo]) & (c.H <= f.cota)))
                    b["contraste_subniveles"] = {
                        "conecta_en_escape": conecta(c.H <= b["altura_escape"]),
                        "conecta_por_debajo": conecta(c.H < b["altura_escape"])}
                    assert b["contraste_subniveles"] == {
                        "conecta_en_escape": True, "conecta_por_debajo": False}
            casos.append(t)
    fuentes = ["scripts/diagnosticar_paradas_campo.py", "scripts/diagnosticar_colocacion_campo.py",
               "granada/campo.py", "granada/hiladas_campo.py", "granada/cupula.py",
               "granada/piezas.py", "granada/celdas.py",
               "datos/red_medinas.json", "datos/registro_red.json", "datos/caras_red.json",
               "datos/niveles_aproximados.json"]
    informe = {"alcance": "Solo reproduce los fallos y la violacion de monotonia del muestreo 0019; no es barrido nuevo ni sustitucion de colocacion",
               "limites": "Barreras sobre cuatro vecinos de la rejilla. Barrera cero permite subidas por debajo de H inicial: no garantiza monotonia. No prueba continua ni intersecciones 3D",
               "parametros": {"A": 2, "filas_por_hilada": 2, "paso_rejilla": c.paso},
               "entorno": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
               "entrada_sha256": hashlib.sha256(a.entrada.read_bytes()).hexdigest(),
               "sha256": {p: hashlib.sha256((RAIZ/p).read_bytes()).hexdigest() for p in fuentes},
               "casos": casos}
    a.salida.write_text(json.dumps(informe, ensure_ascii=False, indent=2)+"\n")
    for t in casos:
        b = t.get("escape_rejilla")
        print(t["fila"], t["parada"], "barrera:", None if b is None else b["barrera_desde_nodo"])


if __name__ == "__main__":
    main()
