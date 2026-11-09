"""Controles analiticos del diagnostico; no son validacion historica."""
import numpy as np

from granada.campo import Campo, campo
from granada.cupula import PENDIENTE, RADIO_BASE
from granada.hiladas_campo import frente, frentes
from scripts.diagnosticar_colocacion_campo import banda, probar_flujo


def test_banda_del_cono_no_invierte_y_llega_a_la_fila_anterior():
    c = campo(A=0)
    f = frentes(c, filas_por_hilada=2)[15]
    detalle = (f, *banda(c, f))
    _, _, xy, areas, residuo = detalle[1:]
    assert (areas > 0).all()
    assert np.max(np.abs(residuo)) < f.paso * .001
    assert np.max(np.abs(np.hypot(*xy[-1].T) - (RADIO_BASE - f.cota/PENDIENTE))) < c.paso
    registros, paths, invertidos = probar_flujo(c, detalle, muestras=5)
    assert all(r["alcanza_cota"] for r in registros)
    assert max(abs(r["error_cota_en_pasos"]) for r in registros) < 1e-6
    assert invertidos == 0


def test_el_flujo_declara_fallo_si_la_cota_no_existe():
    # H=r²+1 tiene minimo 1; la cota previa de la primera fila es 0.
    x = np.linspace(-3, 3, 401)
    X, Y = np.meshgrid(x, x)
    c = Campo(x, x, X*X+Y*Y+1, 0, "sintetico", 1)
    theta = np.linspace(0, 2*np.pi, 129)
    f = frente(1, np.column_stack([np.cos(theta), np.sin(theta)]), 2)
    detalle = (f, *banda(c, f))
    registros, _, invertidos = probar_flujo(c, detalle, muestras=3)
    assert not any(r["alcanza_cota"] for r in registros)
    assert all(r["error_cota_en_pasos"] > 1 for r in registros)
    assert invertidos is None
