"""Controles del intento de refutar reglas de nivel sobre la planta.

Lo que se vigila aqui no es que las reglas salgan bien, sino que el test que
las juzga no sea vacuo: los dos controles positivos tienen que pasar y las
candidatas tienen que caer con un testigo comprobable.
"""

from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path


RAIZ = Path(__file__).parents[1]
RUTA = RAIZ / "datos" / "reglas_de_nivel.json"
RUTA_CARAS = RAIZ / "datos" / "caras_red.json"


def cargar() -> dict:
    return json.loads(RUTA.read_text(encoding="utf-8"))


def vecindades_interiores() -> set[frozenset[str]]:
    caras = json.loads(RUTA_CARAS.read_text(encoding="utf-8"))
    return {
        frozenset((v["a"], v["b"]))
        for v in caras["vecindades"]
        if "contorno" not in (v["a"], v["b"])
    }


def test_declara_de_que_dato_procede_y_sobre_que_dual_trabaja() -> None:
    dato = cargar()
    assert dato["version"] == 1
    assert dato["fuente"]["derivado_de"] == "datos/caras_red.json"
    esperado = hashlib.sha256(RUTA_CARAS.read_bytes()).hexdigest()
    assert dato["fuente"]["sha256_caras"] == esperado
    assert dato["metodo"]["ciclos_independientes"] == 107
    assert "contorno" in dato["metodo"]["dual"]
    assert dato["estado"] == "BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS"


def test_los_dos_controles_positivos_pasan() -> None:
    reglas = cargar()["reglas"]
    controles = {k: v for k, v in reglas.items() if v["tipo"] == "control"}
    assert len(controles) == 2
    assert all(control["consistente"] for control in controles.values())
    # Si estos fallaran, el que estaria roto seria el test, no la planta.
    assert controles["C1_todo_descanso"]["ciclos_fundamentales_violados"] == 0
    assert controles["C2_coronas_cuantizadas"]["ciclos_fundamentales_violados"] == 0


def test_las_tres_candidatas_quedan_refutadas() -> None:
    reglas = cargar()["reglas"]
    candidatas = {k: v for k, v in reglas.items() if v["tipo"] == "candidata"}
    assert len(candidatas) == 3
    assert not any(regla["consistente"] for regla in candidatas.values())
    assert candidatas["R2_ascenso_hacia_el_centro"][
        "ciclos_fundamentales_violados"
    ] == 67
    assert candidatas["R3_ortogonales_suben_diagonales_descansan"][
        "ciclos_fundamentales_violados"
    ] == 67


def test_los_testigos_son_ciclos_reales_del_grafo_de_vecindades() -> None:
    dato = cargar()
    aristas = vecindades_interiores()
    for nombre, regla in dato["reglas"].items():
        testigo = regla["testigo"]
        if not testigo:
            assert regla["consistente"], nombre
            continue
        assert len(set(testigo)) == len(testigo), nombre
        pasos = list(zip(testigo, testigo[1:] + testigo[:1]))
        assert all(frozenset(paso) in aristas for paso in pasos), nombre


def test_el_testigo_de_la_regla_del_salto_unitario_es_impar() -> None:
    regla = cargar()["reglas"]["R1_toda_medina_salva_un_nivel"]
    assert not regla["consistente"]
    assert len(regla["testigo"]) % 2 == 1


def test_los_triangulos_son_teselas_mutuamente_vecinas() -> None:
    dato = cargar()
    aristas = vecindades_interiores()
    triangulos = dato["teorema_del_triangulo"]["lista"]
    assert len(triangulos) == dato["teorema_del_triangulo"]["triangulos"] == 54
    for triangulo in triangulos:
        assert len(set(triangulo)) == 3
        for par in combinations(triangulo, 2):
            assert frozenset(par) in aristas


def test_la_refutacion_no_vive_de_las_medinas_cortas() -> None:
    dato = cargar()
    barrido = {
        fila["umbral_px"]: fila
        for fila in dato["robustez"]["barrido_de_longitud_compartida"]
    }
    # Descartando toda vecindad cuya medina compartida no llegue a 30 px
    # -mediana 31 px- siguen quedando triangulos y R2 sigue rota.
    assert barrido[30]["triangulos"] == 16
    assert not barrido[30]["admite_salto_unitario"]
    assert barrido[30]["ciclos_violados_por_R2"] > 0
    # A 40 px el dual se deshace: el test pierde potencia y deja de decir nada.
    assert barrido[40]["vecindades"] < len(vecindades_interiores()) / 4
    assert barrido[40]["admite_salto_unitario"]


def test_las_medinas_de_los_triangulos_son_mas_cortas_que_la_media() -> None:
    """Por eso el barrido de longitud, y no la media, es el control que vale."""

    robustez = cargar()["robustez"]
    todas = robustez["longitud_compartida_px"]
    en_triangulos = robustez["longitud_compartida_en_triangulos_px"]
    assert todas["minima"] > 5
    # 20,7 px de mediana frente a 31,4: los triangulos se apoyan en las medinas
    # cortas, asi que la refutacion solo vale si sobrevive al barrido.
    assert en_triangulos["mediana"] < todas["mediana"]
    barrido = {
        fila["umbral_px"]: fila
        for fila in robustez["barrido_de_longitud_compartida"]
    }
    assert barrido[30]["triangulos"] == 16
