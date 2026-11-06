"""Artefacto exacto que alimenta el selector de orden del visor."""

import json
from pathlib import Path

import pytest

from granada.cyclotomic import CyclotomicRing, numeric_embedding_xy
from scripts.exportar_ordenes_sinteticos import (
    COTAS,
    NUMERO_CORONAS,
    construir_documento,
    construir_orden,
    vertices_de_celda,
)


RAIZ = Path(__file__).parents[1]
ARTEFACTO = RAIZ / "datos" / "ordenes_sinteticos.json"


def test_los_tres_ordenes_del_selector_salen_del_nucleo_exacto() -> None:
    documento = construir_documento()
    assert [fila["orden"] for fila in documento["ordenes"]] == [16, 20, 24]
    assert documento["afirmacion"] == "A"
    assert "embedding numerico" in documento["procedencia"]["vertices_xy"]
    assert "no reproduce un monumento" in documento["alcance"]
    assert "decision 0014" in documento["procedencia"]["volumen"]


@pytest.mark.parametrize(("m", "sectores"), [(16, 8), (20, 10), (24, 12)])
def test_cada_cupula_cierra_exactamente_y_exporta_sus_coeficientes(
    m: int, sectores: int
) -> None:
    fila = construir_orden(m)
    ring = CyclotomicRing(m)
    assert fila["numero_sectores"] == sectores
    assert fila["simetria_rotacional"] == sectores
    assert fila["numero_coronas"] == NUMERO_CORONAS
    assert fila["numero_celdas"] == sectores * NUMERO_CORONAS
    assert len(fila["celdas"]) == sectores * NUMERO_CORONAS

    for exportada in fila["celdas"]:
        exactos = vertices_de_celda(
            ring, exportada["corona"] - 1, exportada["sector"] - 1
        )
        assert exportada["vertices_exactos"] == [
            list(vertice.coeffs) for vertice in exactos
        ]
        for exportado, exacto in zip(
            exportada["vertices_xy"], exactos, strict=True
        ):
            assert exportado == pytest.approx(numeric_embedding_xy(exacto))

    # Rotar una celda un sector da exactamente la siguiente de su corona.
    for corona in range(NUMERO_CORONAS):
        primera = vertices_de_celda(ring, corona, 0)
        segunda = vertices_de_celda(ring, corona, 1)
        assert tuple(vertice.rotate(2) for vertice in primera) == segunda


def test_el_perfil_escalonado_es_comun_y_estrictamente_descendente() -> None:
    assert len(COTAS) == NUMERO_CORONAS + 1
    assert all(superior > inferior for superior, inferior in zip(COTAS, COTAS[1:]))
    for fila in construir_documento()["ordenes"]:
        assert fila["perfil_cotas"] == [
            [cota.numerator, cota.denominator] for cota in COTAS
        ]


@pytest.mark.parametrize("m", [16, 20, 24])
def test_las_coronas_empalman_sin_huecos_en_planta(m: int) -> None:
    """El borde exterior de una corona es el interior de la siguiente."""
    ring = CyclotomicRing(m)
    sectores = m // 2
    for corona in range(NUMERO_CORONAS - 1):
        for sector in range(sectores):
            interior = vertices_de_celda(ring, corona, sector)
            exterior = vertices_de_celda(ring, corona + 1, sector)
            borde_exterior = {interior[1], interior[2]}
            borde_interior = {exterior[0], exterior[-1]}
            assert borde_exterior == borde_interior


def test_el_artefacto_versionado_esta_regenerado() -> None:
    guardado = json.loads(ARTEFACTO.read_text(encoding="utf-8"))
    assert guardado == construir_documento()


@pytest.mark.parametrize("m", [5, 7, 15])
def test_el_exportador_rechaza_ordenes_que_no_cierran_esta_composicion(m: int) -> None:
    with pytest.raises(ValueError, match="par y >= 6"):
        construir_orden(m)
