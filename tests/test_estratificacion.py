"""Tests de la estratificacion de la cupula.

La vertical se lleva en Fraction: exacta y racional. Los unicos numeros en
coma flotante aparecen en la seccion final, que comprueba la frontera
numerica y el contraste con lo medido en el plano.
"""

from __future__ import annotations

import ast
import inspect
import pathlib
from fractions import Fraction

import pytest

from granada import estratificacion as mod_estrato
from granada.celda import Celda
from granada.cyclotomic import CyclotomicRing
from granada.estratificacion import (
    HILADAS_MEDIDAS,
    RAZON_MEDIDA,
    Estratificacion,
    numeric_embedding_hilada,
)

ORDENES = [16, 20, 24]


# --------------------------------------------------------------------------
# Radios: enteros que decrecen de uno en uno
# --------------------------------------------------------------------------


@pytest.mark.parametrize("m", ORDENES)
def test_los_radios_decrecen_de_uno_en_uno_hasta_cero(m: int) -> None:
    e = Estratificacion(CyclotomicRing(m), hiladas=10)
    assert e.radio_base() == 10
    for k in range(10):
        assert e.radio_exterior(k) == 10 - k
        assert e.radio_interior(k) == 9 - k
        assert isinstance(e.radio_exterior(k), int)
        assert e.radio_exterior(k) - e.radio_interior(k) == 1
    assert e.radio_interior(9) == 0  # el apice cierra


@pytest.mark.parametrize("m", ORDENES)
def test_hilada_fuera_de_rango(m: int) -> None:
    e = Estratificacion(CyclotomicRing(m), hiladas=5)
    for k in (-1, 5, 99):
        with pytest.raises(IndexError):
            e.radio_exterior(k)
        with pytest.raises(IndexError):
            e.altura(k)
        with pytest.raises(IndexError):
            e.celdas(k)


# --------------------------------------------------------------------------
# Alturas: racionales exactas
# --------------------------------------------------------------------------


@pytest.mark.parametrize("m", ORDENES)
def test_las_alturas_son_fracciones_exactas(m: int) -> None:
    e = Estratificacion(CyclotomicRing(m), hiladas=8, razon=Fraction(5, 4))
    for k in range(8):
        assert isinstance(e.altura(k), Fraction)
        assert e.altura(k) == Fraction(5, 4) * k
    assert e.altura(0) == 0
    assert e.altura_total() == Fraction(10)  # 5/4 * 8, exacto


@pytest.mark.parametrize("m", ORDENES)
def test_las_alturas_forman_progresion_aritmetica_exacta(m: int) -> None:
    e = Estratificacion(CyclotomicRing(m), hiladas=12)
    saltos = {e.altura(k + 1) - e.altura(k) for k in range(11)}
    assert len(saltos) == 1  # todos identicos, sin deriva de redondeo
    assert saltos.pop() == e.razon


def test_la_razon_debe_ser_exacta() -> None:
    ring = CyclotomicRing(16)
    with pytest.raises(TypeError):
        Estratificacion(ring, razon=1.279)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        Estratificacion(ring, razon=Fraction(-1, 2))
    with pytest.raises(ValueError):
        Estratificacion(ring, hiladas=0)


# --------------------------------------------------------------------------
# Celdas de cada hilada
# --------------------------------------------------------------------------


@pytest.mark.parametrize("m", ORDENES)
def test_cada_hilada_es_un_anillo_completo(m: int) -> None:
    e = Estratificacion(CyclotomicRing(m), hiladas=6)
    assert e.celdas_por_hilada() == m // 2
    assert e.total_celdas() == 6 * (m // 2)
    for k in range(6):
        celdas = e.celdas(k)
        assert len(celdas) == m // 2
        assert len(set(celdas)) == len(celdas)
        assert all(isinstance(c, Celda) and len(c) == 4 for c in celdas)


@pytest.mark.parametrize("m", ORDENES)
def test_el_anillo_de_cada_hilada_cierra_exactamente(m: int) -> None:
    e = Estratificacion(CyclotomicRing(m), hiladas=4)
    for k in range(4):
        celdas = e.celdas(k)
        girado = {c.rotate(e.pasos) for c in celdas}
        assert girado == set(celdas)


@pytest.mark.parametrize("m", ORDENES)
def test_las_hiladas_encajan_una_sobre_otra(m: int) -> None:
    """El radio interior de una hilada es el exterior de la siguiente."""
    e = Estratificacion(CyclotomicRing(m), hiladas=9)
    for k in range(8):
        assert e.radio_interior(k) == e.radio_exterior(k + 1)


def test_pasos_que_no_dividen_al_orden() -> None:
    with pytest.raises(ValueError):
        Estratificacion(CyclotomicRing(20), pasos=3)  # 3 no divide a 20


@pytest.mark.parametrize("m", ORDENES)
def test_los_vertices_son_enteros_de_python(m: int) -> None:
    e = Estratificacion(CyclotomicRing(m), hiladas=5)
    for k in range(5):
        for celda in e.celdas(k):
            for v in celda.vertices:
                for coef in v.coeffs:
                    assert isinstance(coef, int)
                    assert not isinstance(coef, bool)


# --------------------------------------------------------------------------
# Ausencia de coma flotante
# --------------------------------------------------------------------------

FRONTERA_NUMERICA = {"numeric_embedding_hilada"}


def test_ninguna_funcion_de_estratificacion_usa_coma_flotante() -> None:
    fuente = pathlib.Path(inspect.getfile(mod_estrato)).read_text(encoding="utf-8")
    arbol = ast.parse(fuente)

    def usa_coma_flotante(nodo: ast.AST) -> list[str]:
        motivos = []
        for hijo in ast.walk(nodo):
            if isinstance(hijo, ast.Constant) and isinstance(hijo.value, float):
                motivos.append(f"literal float {hijo.value!r}")
            elif isinstance(hijo, ast.Attribute):
                valor = hijo.value
                if isinstance(valor, ast.Name) and valor.id == "math":
                    motivos.append(f"math.{hijo.attr}")
            elif isinstance(hijo, ast.Name) and hijo.id == "float":
                motivos.append("float()")
        return motivos

    funciones: list[ast.FunctionDef] = []
    for nodo in arbol.body:
        if isinstance(nodo, ast.FunctionDef):
            funciones.append(nodo)
        elif isinstance(nodo, ast.ClassDef):
            funciones.extend(h for h in nodo.body if isinstance(h, ast.FunctionDef))

    assert len(funciones) > 6
    assert FRONTERA_NUMERICA <= {f.name for f in funciones}

    infracciones = {
        f.name: usa_coma_flotante(f)
        for f in funciones
        if f.name not in FRONTERA_NUMERICA and usa_coma_flotante(f)
    }
    assert infracciones == {}, f"coma flotante fuera de la frontera: {infracciones}"


def test_las_constantes_medidas_son_exactas() -> None:
    assert isinstance(RAZON_MEDIDA, Fraction)
    assert RAZON_MEDIDA == Fraction(1000, 782)
    assert HILADAS_MEDIDAS == 23


# --------------------------------------------------------------------------
# Frontera numerica y contraste con el plano
# --------------------------------------------------------------------------


def test_embedding_de_una_hilada_en_3d() -> None:
    e = Estratificacion(CyclotomicRing(16), hiladas=4, razon=Fraction(5, 4))
    hilada = numeric_embedding_hilada(e, 2)
    assert len(hilada) == 8
    for celda in hilada:
        assert len(celda) == 4
        for x, y, z in celda:
            assert isinstance(x, float) and isinstance(y, float)
            assert z == pytest.approx(2.5)  # 5/4 * 2


def test_el_modelo_reproduce_lo_medido_en_el_plano() -> None:
    """Contraste con AA-415_23: radio 3.64 m y altura 4.67 m.

    Con la unidad de planta de 15.7 cm que se deduce de dividir el radio
    medido entre el numero de hiladas contadas.
    """
    u = 0.157  # metros por unidad de planta
    e = Estratificacion(CyclotomicRing(16))
    assert e.radio_base() * u == pytest.approx(3.64, abs=0.05)
    assert float(e.altura_total()) * u == pytest.approx(4.67, abs=0.10)
