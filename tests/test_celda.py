"""Tests de los perfiles de celda en planta.

Como en el nucleo: sin tolerancias. El cierre de un anillo de celdas es una
igualdad de enteros.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from granada import celda as mod_celda
from granada.celda import (
    Celda,
    anillo,
    cuna,
    numeric_embedding_celda,
    pasos_maximos,
    rombo,
)
from granada.cyclotomic import CyclotomicRing

# Los tres ordenes del proyecto: mismo rango real, mundos cuadraticos distintos.
ORDENES = [16, 20, 24]


# --------------------------------------------------------------------------
# Los tres ordenes elegidos
# --------------------------------------------------------------------------


@pytest.mark.parametrize("m", ORDENES)
def test_los_tres_ordenes_tienen_el_mismo_rango(m: int) -> None:
    anillo_ciclo = CyclotomicRing(m)
    assert anillo_ciclo.degree == 8
    assert anillo_ciclo.real_rank == 4


def test_cada_orden_vive_en_un_mundo_cuadratico_distinto() -> None:
    """La razon de elegir 16, 20 y 24 y no multiplos de un mismo orden."""
    R16 = CyclotomicRing(16)
    lam = R16.to_real(R16.real_lambda())
    assert (lam * lam - 2) * (lam * lam - 2) == 2  # sqrt(2)

    R20 = CyclotomicRing(20)
    lam = R20.to_real(R20.real_lambda())
    raiz5 = 2 * (lam * lam) - 5
    assert raiz5 * raiz5 == 5  # sqrt(5)

    R24 = CyclotomicRing(24)
    lam = R24.to_real(R24.real_lambda())
    assert (lam**3 - 3 * lam) * (lam**3 - 3 * lam) == 2  # sqrt(2)
    assert (lam * lam - 2) * (lam * lam - 2) == 3  # sqrt(3)


# --------------------------------------------------------------------------
# El perfil canonico de Lopez de Arenas
# --------------------------------------------------------------------------


def test_cuna_de_2_pasos_en_m16_es_el_triangulo_del_tratado() -> None:
    """Apice de 45 grados, lados 1, base al cuadrado exactamente 2 - sqrt(2).

    Es el "triangulo isosceles con angulo de 45 grados y lados mayores de 5"
    de Lopez de Arenas. La base es 2*sin(pi/8) = 0.7653...
    """
    ring = CyclotomicRing(16)
    c = cuna(ring, 2)
    lados = c.lados_al_cuadrado()
    assert len(lados) == 3
    assert lados[0] == 1  # 0 -> 1
    assert lados[2] == 1  # zeta^2 -> 0
    assert lados[1].coeffs == (4, 0, -1, 0)  # 4 - lambda^2 = 2 - sqrt(2)

    raiz2 = ring.to_real(ring.zeta_power(2) + ring.zeta_power(-2))
    assert lados[1] == 2 - raiz2


def test_cuna_de_4_pasos_en_m16_da_la_hipotenusa_raiz_de_2() -> None:
    """Catetos 1, hipotenusa al cuadrado exactamente 2. El segundo perfil."""
    ring = CyclotomicRing(16)
    lados = cuna(ring, 4).lados_al_cuadrado()
    assert lados[0] == 1 and lados[2] == 1
    assert lados[1] == 2


@pytest.mark.parametrize("m", ORDENES)
def test_las_cunas_tienen_siempre_dos_lados_unidad(m: int) -> None:
    ring = CyclotomicRing(m)
    for pasos in range(1, pasos_maximos(ring) + 1):
        lados = cuna(ring, pasos).lados_al_cuadrado()
        assert lados[0] == 1
        assert lados[2] == 1


@pytest.mark.parametrize("m", ORDENES)
def test_el_rombo_es_equilatero(m: int) -> None:
    ring = CyclotomicRing(m)
    for pasos in range(1, pasos_maximos(ring) + 1):
        r = rombo(ring, pasos)
        assert len(r) == 4
        assert r.es_equilatera()
        assert all(l == 1 for l in r.lados_al_cuadrado())


def test_pasos_fuera_de_rango() -> None:
    ring = CyclotomicRing(16)
    assert pasos_maximos(ring) == 7
    with pytest.raises(ValueError):
        cuna(ring, 8)
    with pytest.raises(ValueError):
        cuna(ring, 0)
    with pytest.raises(ValueError):
        rombo(ring, 8)


# --------------------------------------------------------------------------
# Simetrias, exactas
# --------------------------------------------------------------------------


@pytest.mark.parametrize("m", ORDENES)
def test_girar_m_pasos_devuelve_la_celda_original(m: int) -> None:
    ring = CyclotomicRing(m)
    c = cuna(ring, 2)
    girada = c
    for _ in range(m):
        girada = girada.rotate()
    assert girada == c
    assert girada.vertices == c.vertices


@pytest.mark.parametrize("m", ORDENES)
def test_la_reflexion_es_involutiva_y_conserva_la_metrica(m: int) -> None:
    ring = CyclotomicRing(m)
    c = rombo(ring, 3)
    assert c.conjugate().conjugate() == c
    assert c.conjugate().lados_al_cuadrado() == c.lados_al_cuadrado()


@pytest.mark.parametrize("m", ORDENES)
def test_girar_y_trasladar_conservan_la_metrica(m: int) -> None:
    ring = CyclotomicRing(m)
    c = cuna(ring, 3)
    original = c.lados_al_cuadrado()
    for k in range(m):
        assert c.rotate(k).lados_al_cuadrado() == original
    assert c.translate(ring.zeta_power(5)).lados_al_cuadrado() == original


# --------------------------------------------------------------------------
# Cierre exacto del anillo
# --------------------------------------------------------------------------


@pytest.mark.parametrize("m", ORDENES)
def test_el_anillo_cierra_exactamente(m: int) -> None:
    ring = CyclotomicRing(m)
    for pasos in (1, 2, 4):
        if m % pasos:
            continue
        celdas = anillo(cuna(ring, pasos), pasos)
        assert len(celdas) == m // pasos
        # girar el anillo `pasos` pasos lo deja invariante como conjunto
        girado = {c.rotate(pasos) for c in celdas}
        assert girado == set(celdas)
        # y una celda vuelve a si misma tras dar la vuelta entera
        assert celdas[0].rotate(pasos * (m // pasos)) == celdas[0]


@pytest.mark.parametrize("m", ORDENES)
def test_las_celdas_de_un_anillo_son_distintas(m: int) -> None:
    ring = CyclotomicRing(m)
    celdas = anillo(cuna(ring, 2), 2)
    assert len(set(celdas)) == len(celdas)


def test_el_anillo_rechaza_pasos_que_no_dividen() -> None:
    ring = CyclotomicRing(20)
    with pytest.raises(ValueError, match="no cierra"):
        anillo(cuna(ring, 3), 3)  # 3 no divide a 20
    with pytest.raises(ValueError):
        anillo(cuna(ring, 2), 0)


def test_cuentas_de_celdas_por_orden() -> None:
    """Con cunas de 2 pasos: la estrella de m/2 puntas."""
    assert len(anillo(cuna(CyclotomicRing(16), 2), 2)) == 8
    assert len(anillo(cuna(CyclotomicRing(20), 2), 2)) == 10
    assert len(anillo(cuna(CyclotomicRing(24), 2), 2)) == 12


# --------------------------------------------------------------------------
# Ausencia de coma flotante
# --------------------------------------------------------------------------

FRONTERA_NUMERICA = {"numeric_embedding_celda"}


@pytest.mark.parametrize("m", ORDENES)
def test_los_vertices_son_enteros_de_python(m: int) -> None:
    ring = CyclotomicRing(m)
    muestras = [
        cuna(ring, 2),
        rombo(ring, 3),
        cuna(ring, 2).rotate(5),
        rombo(ring, 3).conjugate(),
        cuna(ring, 4).translate(ring.zeta_power(7)),
    ]
    for c in muestras:
        for v in c.vertices:
            for coef in v.coeffs:
                assert isinstance(coef, int)
                assert not isinstance(coef, bool)
        for lado in c.lados_al_cuadrado():
            for coef in lado.coeffs:
                assert isinstance(coef, int)
                assert not isinstance(coef, bool)


def test_celda_rechaza_vertices_de_otro_anillo() -> None:
    R16, R20 = CyclotomicRing(16), CyclotomicRing(20)
    with pytest.raises(ValueError):
        Celda(R16, (R16.zero, R16.one, R20.one))
    with pytest.raises(ValueError):
        Celda(R16, (R16.zero, R16.one))


def test_ninguna_funcion_de_celda_usa_coma_flotante() -> None:
    fuente = pathlib.Path(inspect.getfile(mod_celda)).read_text(encoding="utf-8")
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
    assert len(funciones) > 6
    assert FRONTERA_NUMERICA <= {f.name for f in funciones}

    infracciones = {
        f.name: usa_coma_flotante(f)
        for f in funciones
        if f.name not in FRONTERA_NUMERICA and usa_coma_flotante(f)
    }
    assert infracciones == {}, f"coma flotante fuera de la frontera: {infracciones}"


# --------------------------------------------------------------------------
# Frontera numerica
# --------------------------------------------------------------------------


def test_embedding_de_la_cuna_canonica() -> None:
    import math

    ring = CyclotomicRing(16)
    puntos = numeric_embedding_celda(cuna(ring, 2))
    assert puntos[0] == pytest.approx((0.0, 0.0))
    assert puntos[1] == pytest.approx((1.0, 0.0))
    assert puntos[2] == pytest.approx((math.cos(math.pi / 4), math.sin(math.pi / 4)))

    # la base mide 2*sin(pi/8)
    bx = puntos[2][0] - puntos[1][0]
    by = puntos[2][1] - puntos[1][1]
    assert math.hypot(bx, by) == pytest.approx(2 * math.sin(math.pi / 8))
