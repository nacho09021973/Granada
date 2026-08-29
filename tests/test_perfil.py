"""Controles de la plantilla de doble perfil.

Lo documentado (7P, 7,5P, 8P, quintos y septimos) se comprueba exacto. Lo que
es eleccion de modelo -la curva entre esos puntos- se comprueba coherente, no
verdadero.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from granada.conica import PerfilArco
from granada.perfil import (
    CIMA_MAYOR,
    CIMA_MENOR,
    MAYOR,
    MENOR,
    UNIDADES_ENTRE_NIVELES,
    PlantillaPerfil,
    paralelas,
    vecindades_no_paralelas,
)


def test_las_cifras_documentadas_son_exactas() -> None:
    assert UNIDADES_ENTRE_NIVELES == 8
    assert CIMA_MAYOR == Fraction(7)
    assert CIMA_MENOR == Fraction(15, 2)
    assert MAYOR.division == 5 and MENOR.division == 7
    assert MAYOR.fraccion_util == Fraction(7, 8)
    assert MENOR.fraccion_util == Fraction(15, 16)


def test_la_division_reparte_la_cima_en_quintos_y_septimos() -> None:
    quintos = MAYOR.estaciones()
    septimos = MENOR.estaciones()
    assert len(quintos) == 6 and len(septimos) == 8
    assert quintos[0] == 0 and quintos[-1] == CIMA_MAYOR
    assert septimos[0] == 0 and septimos[-1] == CIMA_MENOR
    assert quintos[1] == CIMA_MAYOR / 5
    assert septimos[1] == CIMA_MENOR / 7
    assert all(isinstance(estacion, Fraction) for estacion in quintos + septimos)


def test_ninguna_cima_alcanza_el_nivel_siguiente() -> None:
    """Entre la cima y 8P queda la junta; si no, las piezas se tocarian."""
    for plantilla in (MAYOR, MENOR):
        assert plantilla.cima < UNIDADES_ENTRE_NIVELES
        assert plantilla.fraccion_util < 1
    with pytest.raises(ValueError):
        PlantillaPerfil("imposible", 5, Fraction(8), PerfilArco())


def test_la_profundidad_conserva_la_proporcion_documentada() -> None:
    salto = Fraction(203, 1000)
    assert MAYOR.profundidad(salto) == salto * Fraction(7, 8)
    assert MENOR.profundidad(salto) == salto * Fraction(15, 16)
    assert MENOR.profundidad(salto) > MAYOR.profundidad(salto)


def test_el_perfil_engancha_arriba_y_cuelga_abajo() -> None:
    for plantilla in (MAYOR, MENOR):
        assert plantilla.altura_normalizada(Fraction(0)) == 0
        assert plantilla.altura_normalizada(Fraction(1)) == 1


def test_el_perfil_es_monotono() -> None:
    """Un perfil que subiera y bajara no seria una adaraja."""
    for plantilla in (MAYOR, MENOR):
        alturas = [
            plantilla.altura_normalizada(Fraction(i, 32)) for i in range(33)
        ]
        assert alturas == sorted(alturas)


def test_el_paralelismo_distingue_las_dos_plantillas() -> None:
    """Perfiles paralelos son trasladados verticalmente: misma plantilla."""
    assert paralelas(MAYOR, MAYOR) and paralelas(MENOR, MENOR)
    assert not paralelas(MAYOR, MENOR)


def test_el_validador_encuentra_las_vecindades_rotas() -> None:
    asignacion = {"a": MAYOR, "b": MAYOR, "c": MENOR}
    vecindades = [
        {"a": "a", "b": "b"},
        {"a": "b", "b": "c"},
        {"a": "a", "b": "contorno"},
    ]
    assert vecindades_no_paralelas(asignacion, vecindades) == [("b", "c")]


def test_el_contorno_no_impone_plantilla() -> None:
    asignacion = {"a": MENOR}
    assert vecindades_no_paralelas(asignacion, [{"a": "a", "b": "contorno"}]) == []
