"""Controles de la calibracion de altura contra la seccion medida.

La decision 0009 sustituye el reparto uniforme de 4.67 m entre niveles
topologicos por una cota de banda situada contra la seccion de Almagro.
"""

from __future__ import annotations

import json
from pathlib import Path


RAIZ = Path(__file__).parents[1]
RUTA = RAIZ / "datos" / "niveles_aproximados.json"
HILADAS_SECCION = 23
ALTURA_TOTAL_M = 4.67
RADIO_BASE_M = 3.64


def cargar() -> dict:
    return json.loads(RUTA.read_text(encoding="utf-8"))


def test_la_calibracion_declara_su_modelo_y_su_supuesto() -> None:
    calibracion = cargar()["calibracion_altura"]
    assert "no da altura" in calibracion["problema"]
    assert "revolucion" in calibracion["supuesto"]
    assert "decision 0006" in calibracion["no_es_la_estratificacion_refutada"]
    assert len(calibracion["bandas"]) == 6


def test_cada_banda_cae_en_una_hilada_entera_dentro_de_la_seccion() -> None:
    calibracion = cargar()["calibracion_altura"]
    for banda in calibracion["bandas"]:
        assert isinstance(banda["hilada"], int)
        assert 0 <= banda["hilada"] <= HILADAS_SECCION
        esperada = banda["hilada"] * ALTURA_TOTAL_M / HILADAS_SECCION
        assert abs(banda["altura_m"] - esperada) < 1e-9


def test_la_topologia_y_el_radio_medido_coinciden_en_el_orden() -> None:
    """Dos fuentes independientes ordenan las bandas igual.

    La banda sale del grafo dual; la hilada, de la seccion medida a traves del
    radio. Que coincidan es el control de que la calibracion no violenta la
    topologia: si una banda mas interior cayera mas baja, el modelo estaria mal.
    """
    calibracion = cargar()["calibracion_altura"]
    hiladas = [banda["hilada"] for banda in calibracion["bandas"]]
    radios = [banda["radio_mediano_m"] for banda in calibracion["bandas"]]
    assert hiladas == sorted(hiladas) and len(set(hiladas)) == len(hiladas)
    assert radios == sorted(radios, reverse=True)
    assert cargar()["controles"]["bandas_ordenadas_como_las_hiladas"] is True


def test_la_cima_cierra_contra_la_altura_medida() -> None:
    controles = cargar()["controles"]
    assert controles["hiladas_de_las_bandas"] == [6, 11, 13, 17, 19, 23]
    assert abs(controles["desfase_cima_frente_a_seccion_m"]) < 1e-9
    assert abs(controles["altura_de_la_banda_mas_alta_m"] - ALTURA_TOTAL_M) < 1e-9


def test_la_banda_del_borde_no_arranca_en_cero() -> None:
    """El teselado no llega al arranque: su banda exterior ya esta a 6 hiladas.

    El modelo anterior la ponia a cota 0 y perdia 1.22 m de cupula por abajo.
    """
    bandas = cargar()["calibracion_altura"]["bandas"]
    exterior = bandas[0]
    assert exterior["hilada"] == 6
    assert exterior["altura_m"] > 1.2
    assert exterior["radio_mediano_m"] < RADIO_BASE_M


def test_la_dispersion_de_cada_banda_queda_expuesta() -> None:
    """Dos bandas mezclan caras de hiladas distintas y hay que poder verlo."""
    dato = cargar()
    bandas = {b["banda"]: b for b in dato["calibracion_altura"]["bandas"]}
    apretadas = [b for b in bandas.values() if b["iqr_hiladas"] < 0.5]
    sueltas = [b for b in bandas.values() if b["iqr_hiladas"] >= 1.5]
    assert len(apretadas) == 4
    assert {b["banda"] for b in sueltas} == {0, 2}
    assert dato["controles"]["iqr_maximo_de_banda_hiladas"] > 2.5
    for cara in dato["caras"]:
        assert cara["iqr_hiladas_de_su_banda"] == bandas[cara["capa_desde_borde"]]["iqr_hiladas"]


def test_toda_cara_lleva_altura_y_coincide_con_la_de_su_banda() -> None:
    dato = cargar()
    bandas = {b["banda"]: b for b in dato["calibracion_altura"]["bandas"]}
    assert len(dato["caras"]) == 105
    for cara in dato["caras"]:
        banda = bandas[cara["capa_desde_borde"]]
        assert cara["hilada"] == banda["hilada"]
        assert cara["altura_m"] == banda["altura_m"]


def test_los_saltos_en_hiladas_cierran_los_ciclos() -> None:
    """Se derivan de cotas absolutas, asi que ningun ciclo puede contradecir."""
    dato = cargar()
    hiladas = {cara["id"]: cara["hilada"] for cara in dato["caras"]}
    borde = dato["calibracion_altura"]["bandas"][0]["hilada"]
    for vecindad in dato["vecindades"]:
        destino = borde if vecindad["b"] == "contorno" else hiladas[vecindad["b"]]
        assert vecindad["salto_hiladas"] == destino - hiladas[vecindad["a"]]


def test_el_visor_usa_la_altura_calibrada_y_no_el_reparto_uniforme() -> None:
    viewer = (RAIZ / "web" / "viewer.js").read_text(encoding="utf-8")
    assert "info.altura_m" in viewer
    assert "4.67 / 7" not in viewer
    assert "4.67 / 8" not in viewer
