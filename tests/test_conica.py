"""Tests de la conica racional, la primitiva de curva del proyecto.

Puntos de control y peso en Fraction, y evaluar en un t racional da coordenadas
racionales. Sin trigonometria ni coma flotante salvo en la seccion final.

Fue `test_adaraja.py`. Los tests de `malla_adaraja` y `PuntoMalla` se fueron con
el modelo de perfil unico (decision 0011); el levantado se prueba ahora en
`test_malla.py` y la plantilla en `test_perfil.py`.
"""

from __future__ import annotations

import ast
import inspect
import pathlib
from fractions import Fraction

import pytest

from granada import conica as mod_conica
from granada.conica import (
    PESO_CIRCULO,
    PESO_PARABOLA,
    TIRO_CUENCO,
    TIRO_RECTO,
    PerfilArco,
)

TIROS = [Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(4, 5), Fraction(1)]


# --------------------------------------------------------------------------
# El perfil
# --------------------------------------------------------------------------


@pytest.mark.parametrize("tiro", TIROS)
def test_el_perfil_empieza_fuera_abajo_y_acaba_dentro_arriba(tiro: Fraction) -> None:
    p = PerfilArco(tiro=tiro)
    assert p.punto(Fraction(0)) == (Fraction(1), Fraction(0))
    assert p.punto(Fraction(1)) == (Fraction(0), Fraction(1))


@pytest.mark.parametrize("tiro", TIROS)
def test_todas_las_coordenadas_son_fracciones_exactas(tiro: Fraction) -> None:
    p = PerfilArco(tiro=tiro)
    for radio, altura in p.muestrear(12):
        assert isinstance(radio, Fraction)
        assert isinstance(altura, Fraction)
        assert 0 <= radio <= 1
        assert 0 <= altura <= 1


@pytest.mark.parametrize("tiro", TIROS)
def test_el_perfil_es_monotono(tiro: Fraction) -> None:
    """El radio no crece y la altura no decrece: el perfil no se pliega."""
    puntos = PerfilArco(tiro=tiro).muestrear(16)
    for (r0, a0), (r1, a1) in zip(puntos, puntos[1:]):
        assert r1 <= r0
        assert a1 >= a0


def test_tiro_un_medio_degenera_en_recta() -> None:
    """El control sobre la cuerda da el cono liso, sin mocarabes."""
    p = PerfilArco(tiro=TIRO_RECTO)
    assert p.es_recto()
    for radio, altura in p.muestrear(20):
        assert radio + altura == 1  # exacto, la cuerda de (1,0) a (0,1)


def test_el_cuenco_es_simetrico() -> None:
    """Con el control en la diagonal, el perfil es simetrico al invertirlo."""
    puntos = PerfilArco(tiro=TIRO_CUENCO).muestrear(10)
    for (r, a), (r2, a2) in zip(puntos, reversed(puntos)):
        assert r == a2
        assert a == r2


@pytest.mark.parametrize("peso", [PESO_PARABOLA, PESO_CIRCULO, Fraction(3, 2)])
def test_el_peso_no_mueve_los_extremos(peso: Fraction) -> None:
    p = PerfilArco(peso=peso)
    assert p.punto(Fraction(0)) == (Fraction(1), Fraction(0))
    assert p.punto(Fraction(1)) == (Fraction(0), Fraction(1))


def test_la_parabola_da_valores_limpios() -> None:
    """Con peso 1 los denominadores son potencias de dos: es una parabola."""
    p = PerfilArco(peso=PESO_PARABOLA)
    assert p.punto(Fraction(1, 2)) == (Fraction(1, 4), Fraction(1, 4))
    assert p.punto(Fraction(1, 4)) == (Fraction(9, 16), Fraction(1, 16))


def test_el_perfil_rechaza_coma_flotante_y_valores_imposibles() -> None:
    with pytest.raises(TypeError):
        PerfilArco(tiro=0.5)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        PerfilArco(peso=0.7)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        PerfilArco(tiro=Fraction(3, 2))
    with pytest.raises(ValueError):
        PerfilArco(peso=Fraction(0))
    p = PerfilArco()
    with pytest.raises(TypeError):
        p.punto(0.5)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        p.punto(Fraction(2))
    with pytest.raises(ValueError):
        p.muestrear(0)


def test_muestrear_devuelve_n_mas_uno() -> None:
    for n in (1, 2, 7, 30):
        assert len(PerfilArco().muestrear(n)) == n + 1


# --------------------------------------------------------------------------
# La malla
# --------------------------------------------------------------------------


# Al irse `numeric_embedding_punto` con el modelo de perfil unico, este modulo se
# quedo SIN frontera numerica: es exacto de punta a punta. La lista vacia no es un
# descuido, es el estado del modulo.
FRONTERA_NUMERICA: frozenset[str] = frozenset()


def test_ninguna_funcion_de_conica_usa_coma_flotante() -> None:
    fuente = pathlib.Path(inspect.getfile(mod_conica)).read_text(encoding="utf-8")
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

    # Guarda de que el recorrido AST encontro algo, no la asercion real.
    assert len(funciones) > 5
    assert FRONTERA_NUMERICA <= {f.name for f in funciones}

    infracciones = {
        f.name: usa_coma_flotante(f)
        for f in funciones
        if f.name not in FRONTERA_NUMERICA and usa_coma_flotante(f)
    }
    assert infracciones == {}, f"coma flotante fuera de la frontera: {infracciones}"


def test_las_constantes_son_exactas() -> None:
    for constante in (PESO_CIRCULO, PESO_PARABOLA, TIRO_CUENCO, TIRO_RECTO):
        assert isinstance(constante, Fraction)
    assert PESO_CIRCULO == Fraction(70, 99)
    assert TIRO_RECTO == Fraction(1, 2)


# --------------------------------------------------------------------------
# Frontera numerica
# --------------------------------------------------------------------------


def test_el_peso_circulo_aproxima_el_cuarto_de_circunferencia() -> None:
    """PESO_CIRCULO da una elipse muy proxima al arco circular, no el arco."""
    import math

    medio = PerfilArco(peso=PESO_CIRCULO).punto(Fraction(1, 2))
    exacto = 1 - math.sqrt(2) / 2
    assert float(medio[0]) == pytest.approx(exacto, rel=1e-4)
    # pero NO es exactamente el circulo: la diferencia existe y es medible
    assert float(medio[0]) != exacto
