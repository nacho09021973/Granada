"""Recupera únicamente las piezas descartadas por el marco del cupulín 00."""
from importlib import import_module
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from granada.campo import campo
from granada.hiladas_campo import montar
from scripts.render_hilada_campo import EJE_CUPULIN_CAMPO

gc = import_module("granada.cupula")
gc.EJE_CUPULIN_GRADOS = EJE_CUPULIN_CAMPO
en_marco = gc.detector_de_marcos(gc.cupulines_medidos()[:1])
seleccionadas = []


def excluir(v):
    dentro = en_marco(np.asarray(v).mean(axis=0))
    if dentro:
        seleccionadas.append(len(v))
    return not dentro


grupos = montar(campo(A=3, forma="raiz", borde="octogonal"), filas_por_hilada=2,
                descartar=excluir)
vertices, caras = [], []
for _, v, f, *_ in grupos:
    if f:
        caras.extend(np.asarray(f) + len(vertices))
        vertices.extend(v)
np.savez("renders/previas/piezas_marco_00.npz", v=vertices, f=caras, piezas=len(seleccionadas), longitudes=seleccionadas)
