"""Controles sinteticos: fallo de direccion en un valle sobre arista y encierro en un hoyo."""
import numpy as np

from granada.campo import Campo
from scripts.diagnosticar_direcciones_extremos import (alcance_monotono, barrera_subnivel, clasificar,
                                                       direcciones)
from scripts.ensayar_transporte_interior import descender


def _valle_sobre_arista():
    # Valle exacto sobre la linea de rejilla y=0: el gradiente de la celda superior
    # empuja hacia la inferior, donde H sube. El descenso real va por la arista (+x).
    x = np.linspace(-1, 1, 21)
    X, Y = np.meshgrid(x, x)
    return Campo(x, x, 1-.2*X+np.abs(Y), 0, "sintetico", 1)


def test_valle_sobre_arista_es_fallo_de_direccion():
    c = _valle_sobre_arista()
    p, cota = np.array([0., 0.]), .85
    r = descender(c, p, cota, 10)
    assert r["parada"] == "sin_paso_descendente"
    local = direcciones(c, p, np.array([-.2, 1.]))
    assert local["direcciones_descendentes"] > 0
    assert local["paso_aceptable_en_pendiente_minima"] is not None
    assert abs(local["angulo_pendiente_minima_grados"]) < 1e-9
    a = alcance_monotono(c, p, cota, 1, 1.)
    assert a["alcanza_cota"] and a["max_subida_tramos"] <= 1e-10 and a["max_incremento_nodos"] == 0
    assert clasificar(local, [a], barrera_subnivel(c, p, cota)) == "fallo_de_direccion_con_camino_certificado"


def test_hoyo_rodeado_es_encierro_del_subnivel():
    x = np.linspace(-3, 3, 61)
    X, Y = np.meshgrid(x, x)
    H = np.where(X > 2.5, 0., 1+X**2+Y**2)
    c = Campo(x, x, H, 0, "sintetico", 1)
    p, cota = np.array([0., 0.]), .5
    local = direcciones(c, p)
    assert local["direcciones_descendentes"] == 0
    alcances = [alcance_monotono(c, p, cota, k, 3.) for k in (1, 4)]
    assert not any(a["alcanza_cota"] for a in alcances)
    b = barrera_subnivel(c, p, cota)
    assert b["exceso_sobre_H_punto"] > 0
    assert clasificar(local, alcances, b) == "encierro_del_subnivel_discreto"
