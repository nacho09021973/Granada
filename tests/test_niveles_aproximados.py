"""Controles del modelo operativo de niveles aproximados."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


RAIZ = Path(__file__).parents[1]
RUTA = RAIZ / "datos" / "niveles_aproximados.json"
RUTA_CARAS = RAIZ / "datos" / "caras_red.json"


def cargar() -> dict:
    return json.loads(RUTA.read_text(encoding="utf-8"))


def test_declara_que_es_aproximado_y_trazable() -> None:
    dato = cargar()
    assert dato["estado"] == "APPROXIMATE_LEVELS_AVAILABLE"
    assert "no nivelacion historica" in dato["advertencia"]
    assert dato["fuente"]["sha256"] == hashlib.sha256(RUTA_CARAS.read_bytes()).hexdigest()
    assert dato["metodo"]["hiladas_seccion"] == 23
    assert dato["metodo"]["hiladas_recuento_ferrer"] == 24
    assert dato["metodo"]["niveles_topologicos_operativos"] == 7
    assert dato["metodo"]["niveles_topologicos_sensibilidad"] == 8


def test_cubre_todas_las_caras_y_vecindades_sin_mutar_la_fuente() -> None:
    aproximado = cargar()
    fuente = json.loads(RUTA_CARAS.read_text(encoding="utf-8"))
    assert len(aproximado["caras"]) == len(fuente["caras"]) == 105
    assert len(aproximado["vecindades"]) == len(fuente["vecindades"]) == 227
    assert all(v["salto"] is None for v in fuente["vecindades"])
    assert fuente["estado"] == "BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS"


def test_los_saltos_son_diferencias_de_cotas_y_cierran_ciclos() -> None:
    dato = cargar()
    niveles = {cara["id"]: cara["nivel"] for cara in dato["caras"]}
    niveles8 = {cara["id"]: cara["nivel_8"] for cara in dato["caras"]}
    for v in dato["vecindades"]:
        destino = 0 if v["b"] == "contorno" else niveles[v["b"]]
        destino8 = 0 if v["b"] == "contorno" else niveles8[v["b"]]
        assert v["salto"] == destino - niveles[v["a"]]
        assert v["salto_8"] == destino8 - niveles8[v["a"]]
        assert v["procedencia"].endswith("no observado")
        assert abs(v["salto"]) <= 2
        assert abs(v["salto_8"]) <= 2


def test_la_sensibilidad_7_8_queda_expuesta() -> None:
    dato = cargar()
    assert 0 < dato["controles"]["caras_estables_7_8"] < 105
    assert 0 < dato["controles"]["vecindades_estables_7_8"] < 227
    for cara in dato["caras"]:
        assert cara["intervalo_nivel"] == sorted(
            [cara["nivel"], cara["nivel_8"]]
        )


def test_el_modelo_respeta_las_capas_del_grafo() -> None:
    dato = cargar()
    assert dato["metodo"]["capas_del_grafo"] == 5
    assert dato["controles"]["nivel_minimo"] == 0
    assert dato["controles"]["nivel_maximo"] == 7
