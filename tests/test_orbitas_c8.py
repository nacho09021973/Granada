"""Controles de las orbitas bajo la rotacion C8.

Lo que se comprueba no es que la cupula sea simetrica -eso lo mide la entrada 7
de fuentes.md por Fourier, y seria circular comprobarlo sobre la red espejada-,
sino que la rotacion de 45 grados **empareja caras con caras** de forma
inequivoca. Si no lo hiciera, ninguna observacion se podria propagar.
"""

from __future__ import annotations

import json
from pathlib import Path


RAIZ = Path(__file__).parents[1]
RUTA = RAIZ / "datos" / "orbitas_c8.json"
CARAS = RAIZ / "datos" / "caras_red.json"


def cargar() -> dict:
    return json.loads(RUTA.read_text(encoding="utf-8"))


def test_declara_que_es_solo_rotacion() -> None:
    dato = cargar()
    assert dato["estado"] == "C8_ORBITS_AVAILABLE"
    assert "especular no se ha analizado" in dato["advertencia"]
    assert "no multiplica el N" in dato["advertencia"]
    assert "no circular" in dato["fuente"]["simetria"]
    assert dato["metodo"]["giro_grados"] == 45.0


def test_la_rotacion_es_una_permutacion_de_orden_ocho() -> None:
    controles = cargar()["controles"]
    assert controles["es_biyectiva"] is True
    assert controles["orden_de_la_permutacion"] == 8


def test_las_orbitas_reparten_las_105_caras() -> None:
    """13 orbitas de 8 mas el octogono central, que la rotacion deja fijo."""
    dato = cargar()
    orbitas = dato["orbitas"]
    assert len(orbitas) == 14
    assert sum(o["tamano"] for o in orbitas) == 105
    assert sorted(o["tamano"] for o in orbitas) == [1] + [8] * 13
    fijas = [o["representante"] for o in orbitas if o["tamano"] == 1]
    assert fijas == ["c042"], "la unica cara fija tiene que ser la del eje"


def test_el_emparejamiento_no_es_ambiguo() -> None:
    controles = cargar()["controles"]
    assert controles["desajuste_maximo_mm"] < 120
    assert controles["desajuste_mediano_mm"] < 20
    assert controles["margen_mediano"] > 5
    # Seis caras quedan ajustadas y por eso van nombradas una a una.
    assert len(controles["caras_con_margen_ajustado"]) == 6


def test_los_angulos_que_no_son_de_simetria_ajustan_mucho_peor() -> None:
    """Control: si 45 grados no fuera especial, cualquier giro emparejaria igual."""
    controles = cargar()["controles"]
    for control in controles["angulos_de_control"]:
        assert control["grados"] != 45.0
        assert control["desajuste_maximo_mm"] > 3 * controles["desajuste_maximo_mm"]
        assert control["caras_con_margen_holgado"] < 60


def test_la_propagacion_de_vecindades_excluye_las_que_no_cierran() -> None:
    """5 de 227 no cierran. Por ahi no se propaga: quedan fuera, no se fuerzan."""
    dato = cargar()
    controles = dato["controles"]
    assert controles["vecindades"] == 227
    assert len(controles["vecindades_que_no_cierran"]) == 5
    assert controles["orbitas_de_vecindades_propagables"] == 27
    assert controles["vecindades_cubiertas_por_orbitas_propagables"] == 216
    rotas = {tuple(par) for par in controles["vecindades_que_no_cierran"]}
    cubiertas = {
        tuple(par)
        for orbita in dato["orbitas_vecindades"]
        if orbita["propagable"]
        for par in orbita["vecindades"]
    }
    assert not (rotas & cubiertas), "una vecindad rota no puede ir en una orbita buena"


def test_el_dominio_fundamental_es_lo_minimo_que_hay_que_observar() -> None:
    dato = cargar()
    dominio = dato["dominio_fundamental"]
    assert len(dominio["caras"]) == 14
    assert len(dominio["vecindades"]) == 27
    representantes = {o["representante"] for o in dato["orbitas"]}
    assert set(dominio["caras"]) == representantes


def test_la_permutacion_cubre_exactamente_las_caras_del_teselado() -> None:
    dato = cargar()
    fuente = json.loads(CARAS.read_text(encoding="utf-8"))
    ids = {cara["id"] for cara in fuente["caras"]}
    assert set(dato["permutacion"]) == ids
    assert set(dato["permutacion"].values()) == ids
