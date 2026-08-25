"""Controles del dato derivado de las caras de la red de medinas.

El dato no asigna niveles. Estas pruebas vigilan justo eso: que la geometria
cuadre, que lo clasificado lleve margen frente a los controles y que ninguna
vecindad aparezca firmada mientras no haya evidencia del signo.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path


RAIZ = Path(__file__).parents[1]
RUTA = RAIZ / "datos" / "caras_red.json"
RUTA_RED = RAIZ / "datos" / "red_medinas.json"

FIGURAS = ("medio_cuadrado", "media_jaira", "jaira", "cuadrado", "octogono")


def cargar() -> dict:
    return json.loads(RUTA.read_text(encoding="utf-8"))


def cargar_red() -> dict:
    return json.loads(RUTA_RED.read_text(encoding="utf-8"))


def test_el_dato_declara_de_que_red_procede_y_con_que_metodo() -> None:
    dato = cargar()
    assert dato["version"] == 1
    assert dato["fuente"]["derivado_de"] == "datos/red_medinas.json"
    assert dato["fuente"]["version_red"] == 2
    assert dato["fuente"]["handle"] == "11441/143321"
    esperado = hashlib.sha256(RUTA_RED.read_bytes()).hexdigest()
    assert dato["fuente"]["sha256_red"] == esperado
    assert dato["metodo"]["resolucion_px"] == 2.0
    assert dato["metodo"]["signo_de_nivel"].startswith("sin firmar")


def test_las_caras_cumplen_euler_y_no_hay_cruces() -> None:
    controles = cargar()["controles"]
    assert controles["nudos"] == 323
    assert controles["aristas"] == 427
    assert controles["caras_interiores"] == 105
    assert controles["euler_v_menos_e_mas_f"] == 2
    assert controles["cruces_de_aristas"] == 0


def test_las_caras_recubren_el_contorno_sin_solapes() -> None:
    dato = cargar()
    suma = math.fsum(cara["area_m2"] for cara in dato["caras"])
    assert math.isclose(suma, dato["contorno"]["area_m2"], rel_tol=1e-12)
    assert math.isclose(suma, dato["controles"]["area_caras_m2"], rel_tol=1e-12)


def test_cada_cara_es_un_ciclo_real_de_la_red() -> None:
    dato = cargar()
    red = cargar_red()
    aristas = {(min(a, b), max(a, b)) for a, b, _, _ in red["aristas"]}
    semiaristas = Counter()
    for cara in dato["caras"]:
        vertices = cara["vertices"]
        assert len(vertices) == cara["lados"] >= 3
        assert len(set(vertices)) == len(vertices)
        for u, v in zip(vertices, vertices[1:] + vertices[:1]):
            assert (min(u, v), max(u, v)) in aristas
            semiaristas[(u, v)] += 1
    # Ninguna cara interior repite una semiarista: el recorrido es una particion.
    assert set(semiaristas.values()) == {1}


def test_las_aristas_puente_son_los_terminales_de_borde() -> None:
    dato = cargar()
    red = cargar_red()
    puentes = {tuple(par) for par in dato["contorno"]["aristas_puente"]}
    assert len(puentes) == dato["controles"]["aristas_puente"] == 24
    terminales = set(red["nodos_borde"])
    assert {u for par in puentes for u in par} & terminales == terminales


def test_la_clasificacion_es_la_medida_y_deja_ochenta_caras_sin_figura() -> None:
    controles = cargar()["controles"]
    assert controles["conteo_por_figura"] == {
        "cuadrado": 16,
        "jaira": 0,
        "media_jaira": 0,
        "medio_cuadrado": 8,
        "octogono": 1,
    }
    assert controles["clasificadas"] == 25
    assert controles["sin_clasificar"] == 80
    assert controles["clasificadas"] + controles["sin_clasificar"] == 105


def test_la_mayoria_de_lo_no_clasificado_ni_siquiera_es_convexo() -> None:
    dato = cargar()
    sin_figura = [cara for cara in dato["caras"] if cara["figura"] is None]
    assert len(sin_figura) == 80
    no_convexas = [cara for cara in sin_figura if not cara["convexa"]]
    assert len(no_convexas) == dato["controles"]["sin_clasificar_no_convexas"] == 51
    # Las figuras documentadas son convexas: una cara no convexa no es una pieza.
    assert all(cara["figura"] is None for cara in dato["caras"] if not cara["convexa"])


def test_control_ninguna_plantilla_ajena_gana_a_la_documentada() -> None:
    dato = cargar()
    assert len(dato["metodo"]["plantillas_de_control"]) >= 5
    for cara in dato["caras"]:
        if cara["figura"] is None:
            continue
        propia = max(
            cara["desviacion_angular_grados"] / cara["tolerancia_grados"],
            cara["desviacion_lado_relativa"] / 0.12,
        )
        ajena = max(
            cara["desviacion_ajena_angular_grados"] / cara["tolerancia_grados"],
            cara["desviacion_ajena_lado_relativa"] / 0.12,
        )
        assert ajena > propia, cara["id"]
    # Una sola cara admite ademas una plantilla de control dentro de su ventana.
    assert dato["controles"]["caras_que_admiten_plantilla_ajena"] == 1


def test_solo_se_confirman_las_caras_grandes_y_con_margen() -> None:
    dato = cargar()
    metodo = dato["metodo"]
    for cara in dato["caras"]:
        if cara["figura"] is None:
            assert cara["firmeza"] is None
            continue
        firme = (
            cara["lado_minimo_px"] >= metodo["lado_minimo_firme_px"]
            and cara["margen_frente_a_ajena"] is not None
            and cara["margen_frente_a_ajena"] >= metodo["margen_firme"]
        )
        assert cara["firmeza"] == ("confirmada" if firme else "al_limite_de_resolucion")
    assert dato["controles"]["clasificadas_confirmadas"] == 9
    assert dato["controles"]["clasificadas_al_limite"] == 16
    confirmadas = Counter(
        cara["figura"] for cara in dato["caras"] if cara["firmeza"] == "confirmada"
    )
    assert confirmadas == {"medio_cuadrado": 8, "octogono": 1}


def test_los_cuadrados_pequenos_quedan_marcados_al_limite_de_resolucion() -> None:
    dato = cargar()
    cuadrados = [cara for cara in dato["caras"] if cara["figura"] == "cuadrado"]
    assert len(cuadrados) == 16
    assert all(cara["firmeza"] == "al_limite_de_resolucion" for cara in cuadrados)
    # Todos caen por debajo del suelo de resolucion, y el peor de ellos no se
    # distingue de un rombo de 60 grados: 1.16 veces mejor, no 2.
    assert max(cara["lado_minimo_px"] for cara in cuadrados) < 10
    assert min(cara["margen_frente_a_ajena"] for cara in cuadrados) < 1.2


def test_las_familias_clasificadas_caen_en_orbitas_de_ocho() -> None:
    dato = cargar()
    for figura, esperadas in (("medio_cuadrado", 1), ("cuadrado", 2)):
        azimuts = sorted(
            cara["azimut_grados"] for cara in dato["caras"] if cara["figura"] == figura
        )
        assert len(azimuts) == 8 * esperadas
        for inicio in range(esperadas):
            orbita = azimuts[inicio::esperadas] if esperadas > 1 else azimuts
            saltos = [
                (b - a) % 360 for a, b in zip(orbita, orbita[1:] + orbita[:1])
            ]
            assert all(abs(salto - 45.0) < 2.0 for salto in saltos), (figura, saltos)


def test_la_clasificacion_no_se_mueve_al_variar_la_resolucion_supuesta() -> None:
    barrido = cargar()["controles"]["barrido_de_resolucion"]
    estables = [fila for fila in barrido if fila["resolucion_px"] >= 1.0]
    assert len(estables) >= 4
    conteos = {tuple(fila[clave] for clave in FIGURAS) for fila in estables}
    assert conteos == {(8, 0, 0, 16, 1)}


def test_ninguna_vecindad_lleva_salto_firmado() -> None:
    dato = cargar()
    vecindades = dato["vecindades"]
    assert len(vecindades) == dato["controles"]["vecindades"] == 227
    assert all(vecindad["salto"] is None for vecindad in vecindades)
    assert all(vecindad["evidencia"] is None for vecindad in vecindades)
    assert dato["controles"]["vecindades_con_salto_firmado"] == 0
    assert dato["estado"] == "BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS"


def test_las_vecindades_referencian_caras_y_aristas_existentes() -> None:
    dato = cargar()
    red = cargar_red()
    aristas = {(min(a, b), max(a, b)) for a, b, _, _ in red["aristas"]}
    identificadores = {cara["id"] for cara in dato["caras"]}
    de_borde = 0
    compartidas = 0
    vistas = set()
    for vecindad in dato["vecindades"]:
        assert vecindad["a"] in identificadores
        assert vecindad["b"] in identificadores or vecindad["b"] == "contorno"
        assert vecindad["a"] != vecindad["b"]
        par = (vecindad["a"], vecindad["b"])
        assert par not in vistas
        vistas.add(par)
        assert vecindad["aristas"]
        for u, v in vecindad["aristas"]:
            assert (min(u, v), max(u, v)) in aristas
        compartidas += len(vecindad["aristas"])
        de_borde += vecindad["b"] == "contorno"
    assert de_borde == dato["controles"]["vecindades_de_borde"] == 16
    assert compartidas + dato["controles"]["aristas_puente"] == len(red["aristas"])


def test_toda_cara_tiene_al_menos_una_vecina() -> None:
    dato = cargar()
    tocadas = Counter()
    for vecindad in dato["vecindades"]:
        for extremo in (vecindad["a"], vecindad["b"]):
            if extremo != "contorno":
                tocadas[extremo] += 1
    assert len(tocadas) == len(dato["caras"])
    assert min(tocadas.values()) >= 2
