"""Controles estructurales del dato derivado de la red de medinas."""

from __future__ import annotations

import json
import math
from collections import Counter, deque
from pathlib import Path


RUTA = Path(__file__).parents[1] / "datos" / "red_medinas.json"


def cargar() -> dict[str, object]:
    return json.loads(RUTA.read_text(encoding="utf-8"))


def test_red_completa_tiene_proveniencia_y_metodo_explicitos() -> None:
    dato = cargar()
    assert dato["version"] == 2
    assert dato["fuente"]["handle"] == "11441/143321"
    assert dato["fuente"]["pagina_pdf"] == 236
    assert "superior" in dato["fuente"]["mitad_usada"]
    assert "reflexion" in dato["fuente"]["mitad_usada"]
    assert dato["metodo"]["contorno_editorial_punteado"].startswith("excluido")


def test_red_es_un_grafo_simple_conexo() -> None:
    dato = cargar()
    nodos = dato["nodos"]
    aristas = dato["aristas"]
    assert len(nodos) == dato["controles"]["nudos"] == 323
    assert len(aristas) == dato["controles"]["aristas"] == 427

    pares = []
    adyacencia = [set() for _ in nodos]
    for a, b, longitud, angulo in aristas:
        assert isinstance(a, int) and isinstance(b, int)
        assert 0 <= a < b < len(nodos)
        assert longitud > 0
        assert 0 <= angulo < 180
        pares.append((a, b))
        adyacencia[a].add(b)
        adyacencia[b].add(a)
    assert len(pares) == len(set(pares))

    visitados = {0}
    cola = deque([0])
    while cola:
        actual = cola.popleft()
        for vecino in adyacencia[actual] - visitados:
            visitados.add(vecino)
            cola.append(vecino)
    assert len(visitados) == len(nodos)
    assert dato["controles"]["componentes_conexas"] == 1
    assert len(aristas) - len(nodos) + 1 == 105


def test_terminales_de_borde_son_exactamente_los_nudos_de_grado_uno() -> None:
    dato = cargar()
    grados = Counter(indice for arista in dato["aristas"] for indice in arista[:2])
    terminales = sorted(indice for indice, grado in grados.items() if grado == 1)
    assert terminales == dato["nodos_borde"]
    assert len(terminales) == dato["controles"]["nudos_de_borde_grado_1"] == 24
    assert Counter(grados.values()) == {1: 24, 2: 136, 3: 110, 4: 45, 6: 8}


def test_longitud_y_angulo_de_cada_arista_corresponden_a_sus_nudos() -> None:
    dato = cargar()
    nodos = dato["nodos"]
    for a, b, longitud, angulo in dato["aristas"]:
        dx = nodos[b][0] - nodos[a][0]
        dy = nodos[b][1] - nodos[a][1]
        assert math.isclose(longitud, math.hypot(dx, dy), abs_tol=2e-12)
        esperado = math.degrees(math.atan2(dy, dx)) % 180
        assert math.isclose(angulo, esperado, abs_tol=2e-10)


def test_cuatro_direcciones_y_ausencia_de_fragmentos_raster() -> None:
    controles = cargar()["controles"]
    assert controles["desviacion_mediana_cuatro_direcciones_grados"] < 2.3
    assert controles["fraccion_aristas_a_5_grados"] > 0.75
    assert controles["longitud_minima_px"] > 5


def test_topologia_es_estable_en_un_intervalo_amplio_de_umbral() -> None:
    sensibilidad = cargar()["controles"]["sensibilidad_umbral"]
    assert [fila["umbral"] for fila in sensibilidad] == [170, 200, 230]
    assert {
        (fila["nudos"], fila["aristas"], fila["componentes_conexas"])
        for fila in sensibilidad
    } == {(323, 427, 1)}
