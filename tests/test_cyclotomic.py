"""Tests del nucleo aritmetico exacto.

Regla que atraviesa todo el fichero: salvo en la seccion final, marcada
como tal, no aparece ninguna tolerancia numerica. Las comprobaciones son
igualdades exactas entre enteros.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from granada import cyclotomic as cyc
from granada.cyclotomic import (
    CyclotomicInteger,
    CyclotomicRing,
    RealCyclotomicInteger,
    cyclotomic_polynomial,
    euler_phi,
    numeric_embedding_value,
    numeric_embedding_xy,
    poly_mul,
    solve_rational_linear,
)

ORDENES = list(range(3, 31))


# --------------------------------------------------------------------------
# Polinomios ciclotomicos
# --------------------------------------------------------------------------


@pytest.mark.parametrize("m", ORDENES)
def test_grado_de_phi_m_es_euler_phi(m: int) -> None:
    grado = len(cyclotomic_polynomial(m)) - 1
    assert grado == euler_phi(m)


def test_valores_conocidos_de_phi() -> None:
    # Coeficientes en orden ascendente de grado.
    assert cyclotomic_polynomial(8) == (1, 0, 0, 0, 1)  # x^4 + 1
    assert cyclotomic_polynomial(12) == (1, 0, -1, 0, 1)  # x^4 - x^2 + 1
    # x^8 - x^4 + 1
    assert cyclotomic_polynomial(24) == (1, 0, 0, 0, -1, 0, 0, 0, 1)


@pytest.mark.parametrize("m", ORDENES)
def test_producto_de_los_phi_d_reconstruye_x_m_menos_1(m: int) -> None:
    producto: tuple[int, ...] = (1,)
    for d in cyc.divisors(m):
        producto = poly_mul(producto, cyclotomic_polynomial(d))
    assert producto == (-1,) + (0,) * (m - 1) + (1,)


@pytest.mark.parametrize("m", ORDENES)
def test_phi_m_es_monico(m: int) -> None:
    assert cyclotomic_polynomial(m)[-1] == 1


def test_phi_105_tiene_un_coeficiente_menos_2() -> None:
    # Primer orden en el que aparece un coeficiente fuera de {-1, 0, 1}.
    # Sirve de canario: una division inexacta lo estropearia.
    assert -2 in cyclotomic_polynomial(105)


def test_division_no_exacta_lanza_error() -> None:
    with pytest.raises(ValueError):
        cyc.poly_divide_exact((1, 1, 1), (2,))


# --------------------------------------------------------------------------
# Estructura del anillo
# --------------------------------------------------------------------------


@pytest.mark.parametrize("m", ORDENES)
def test_rango_del_anillo_es_euler_phi(m: int) -> None:
    assert CyclotomicRing(m).degree == euler_phi(m)


@pytest.mark.parametrize("m", ORDENES)
def test_zeta_elevado_a_m_es_uno_exactamente(m: int) -> None:
    anillo = CyclotomicRing(m)
    assert anillo.zeta**m == anillo.one
    assert (anillo.zeta**m).coeffs == anillo.one.coeffs


@pytest.mark.parametrize("m", ORDENES)
def test_zeta_no_es_uno_antes_de_m(m: int) -> None:
    anillo = CyclotomicRing(m)
    for k in range(1, m):
        assert anillo.zeta**k != anillo.one


@pytest.mark.parametrize("m", ORDENES)
def test_rotar_m_veces_devuelve_el_original(m: int) -> None:
    anillo = CyclotomicRing(m)
    # Un elemento arbitrario pero fijo, con coeficientes de ambos signos.
    original = anillo.element([(-1) ** k * (k + 3) for k in range(anillo.degree)])
    girado = original
    for _ in range(m):
        girado = girado.rotate()
    assert girado == original
    assert girado.coeffs == original.coeffs


@pytest.mark.parametrize("m", ORDENES)
def test_conjugacion_es_involutiva_y_es_un_homomorfismo(m: int) -> None:
    anillo = CyclotomicRing(m)
    a = anillo.element([k + 1 for k in range(anillo.degree)])
    b = anillo.element([(-1) ** k for k in range(anillo.degree)])
    assert a.conjugate().conjugate() == a
    assert (a * b).conjugate() == a.conjugate() * b.conjugate()
    assert (a + b).conjugate() == a.conjugate() + b.conjugate()


@pytest.mark.parametrize("m", ORDENES)
def test_el_anillo_es_asociativo_y_distributivo(m: int) -> None:
    anillo = CyclotomicRing(m)
    a = anillo.element([1, -2] + [0] * (anillo.degree - 2))
    b = anillo.element([3, 1] + [0] * (anillo.degree - 2))
    c = anillo.zeta_power(3)
    assert (a * b) * c == a * (b * c)
    assert a * (b + c) == a * b + a * c


# --------------------------------------------------------------------------
# Norma al cuadrado
# --------------------------------------------------------------------------


@pytest.mark.parametrize("m", ORDENES)
def test_modulo_al_cuadrado_de_zeta_k_es_uno(m: int) -> None:
    anillo = CyclotomicRing(m)
    for k in range(2 * m):
        assert anillo.zeta_power(k).norm_squared() == 1


@pytest.mark.parametrize("m", ORDENES)
def test_la_norma_es_multiplicativa(m: int) -> None:
    anillo = CyclotomicRing(m)
    a = anillo.element([2, -1] + [0] * (anillo.degree - 2))
    b = anillo.element([1, 3] + [0] * (anillo.degree - 2))
    assert (a * b).norm_squared() == a.norm_squared() * b.norm_squared()


@pytest.mark.parametrize("m", ORDENES)
def test_la_norma_es_invariante_por_rotacion(m: int) -> None:
    anillo = CyclotomicRing(m)
    a = anillo.element([1, 2] + [0] * (anillo.degree - 2))
    for k in range(m):
        assert a.rotate(k).norm_squared() == a.norm_squared()


def test_to_real_rechaza_elementos_no_reales() -> None:
    anillo = CyclotomicRing(8)
    with pytest.raises(ValueError):
        anillo.to_real(anillo.zeta)


# --------------------------------------------------------------------------
# Irracionales cuadraticos reproducidos exactamente
# --------------------------------------------------------------------------


def test_m8_zeta_mas_zeta7_al_cuadrado_es_exactamente_2() -> None:
    """zeta_8 + zeta_8^7 = 2*cos(45 grados) = sqrt(2)."""
    anillo = CyclotomicRing(8)
    raiz_de_dos = anillo.zeta + anillo.zeta_power(7)
    assert raiz_de_dos * raiz_de_dos == 2
    assert (raiz_de_dos * raiz_de_dos).coeffs == (2, 0, 0, 0)


def test_m12_zeta_mas_zeta11_al_cuadrado_es_exactamente_3() -> None:
    """zeta_12 + zeta_12^11 = 2*cos(30 grados) = sqrt(3)."""
    anillo = CyclotomicRing(12)
    raiz_de_tres = anillo.zeta + anillo.zeta_power(11)
    assert raiz_de_tres * raiz_de_tres == 3
    assert (raiz_de_tres * raiz_de_tres).coeffs == (3, 0, 0, 0)


def test_m16_existe_un_elemento_con_norma_2_menos_raiz_de_2() -> None:
    """En m=16, |zeta^2 - 1|^2 = 2 - sqrt(2), en representacion exacta.

    Es el cuadrado de la cuerda de 45 grados, 2*sin(pi/8) = 0.7653...

    En la base de lambda = zeta_16 + zeta_16^(-1) = 2*cos(pi/8) se tiene
    lambda^2 = 2 + sqrt(2), luego 2 - sqrt(2) = 4 - lambda^2.
    """
    anillo = CyclotomicRing(16)
    cuerda = anillo.zeta_power(2) - 1
    norma = cuerda.norm_squared()
    assert isinstance(norma, RealCyclotomicInteger)
    assert norma.coeffs == (4, 0, -1, 0)  # 4 - lambda^2

    # Y la misma cantidad construida desde el subanillo real:
    raiz_de_dos = anillo.to_real(anillo.zeta_power(2) + anillo.zeta_power(-2))
    assert norma == 2 - raiz_de_dos
    assert raiz_de_dos * raiz_de_dos == 2


def test_2_menos_raiz_de_2_tambien_existe_en_m8() -> None:
    """Contraste explicito: 2 - sqrt(2) NO distingue m=16 de m=8.

    El subanillo real de Z[zeta_8] es Z[sqrt(2)], que contiene 2 - sqrt(2):
    lo realiza |zeta_8 - 1|^2. Este test documenta el hecho para que nadie
    use 2 - sqrt(2) como criterio de separacion entre ordenes.
    """
    anillo = CyclotomicRing(8)
    assert (anillo.zeta - 1).norm_squared().coeffs == (2, -1)  # 2 - lambda


def test_m16_realiza_una_longitud_imposible_en_m8() -> None:
    """La separacion real entre m=16 y m=8: la cuerda de 22.5 grados.

    |zeta_16 - 1|^2 = 2 - 2*cos(2*pi/16) = 2 - sqrt(2 + sqrt(2)), cuya raiz
    es 2*sin(pi/16) = 0.3902...

    Z[zeta_8] se sumerge en Z[zeta_16] via zeta_8 = zeta_16^2, y su
    subanillo real es el Z-modulo generado por 1 y zeta_16^2 + zeta_16^(-2).
    Comprobamos que la cuerda de 22.5 grados ni siquiera esta en el
    Q-espacio generado por ellos, lo que excluye tambien el Z-modulo.
    """
    anillo = CyclotomicRing(16)
    generadores = [
        anillo.one.coeffs,
        (anillo.zeta_power(2) + anillo.zeta_power(-2)).coeffs,
    ]

    cuerda_22_5 = (anillo.zeta - 1).norm_squared()
    assert cuerda_22_5.coeffs == (2, -1, 0, 0)  # 2 - lambda
    assert solve_rational_linear(generadores, cuerda_22_5.to_cyclotomic().coeffs) is None

    # Control: la cuerda de 45 grados si esta, con coeficientes enteros.
    cuerda_45 = (anillo.zeta_power(2) - 1).norm_squared()
    solucion = solve_rational_linear(generadores, cuerda_45.to_cyclotomic().coeffs)
    assert solucion is not None
    assert all(c.denominator == 1 for c in solucion)
    assert tuple(int(c) for c in solucion) == (2, -1)


@pytest.mark.parametrize("m", ORDENES)
def test_lambda_genera_el_subanillo_real(m: int) -> None:
    anillo = CyclotomicRing(m)
    lam = anillo.real_lambda()
    assert lam.conjugate() == lam
    assert anillo.to_real(lam * lam) == anillo.to_real(lam) * anillo.to_real(lam)


# --------------------------------------------------------------------------
# Ausencia de coma flotante en el nucleo
# --------------------------------------------------------------------------

# Unicas funciones del paquete autorizadas a usar coma flotante.
FRONTERA_NUMERICA = {"numeric_embedding_xy", "numeric_embedding_value"}


@pytest.mark.parametrize("m", ORDENES)
def test_los_coeficientes_son_enteros_de_python(m: int) -> None:
    anillo = CyclotomicRing(m)
    a = anillo.element([k * 2 - 5 for k in range(anillo.degree)])
    b = anillo.zeta_power(3) - 7

    muestras: list[CyclotomicInteger] = [
        a,
        b,
        a + b,
        a - b,
        a * b,
        a**5,
        a.conjugate(),
        a.rotate(3),
        anillo.zero,
        anillo.one,
        anillo.real_lambda(),
    ]
    for elemento in muestras:
        assert len(elemento.coeffs) == euler_phi(m)
        for c in elemento.coeffs:
            assert isinstance(c, int)
            assert not isinstance(c, bool)

    for real in (a.norm_squared(), b.norm_squared(), (a * b).norm_squared()):
        assert len(real.coeffs) == anillo.real_rank
        for c in real.coeffs:
            assert isinstance(c, int)
            assert not isinstance(c, bool)


def test_el_anillo_rechaza_coeficientes_en_coma_flotante() -> None:
    anillo = CyclotomicRing(8)
    with pytest.raises(TypeError):
        anillo.element([1.0, 0, 0, 0])
    with pytest.raises(TypeError):
        anillo.real_element([2.5, 0])
    with pytest.raises(TypeError):
        anillo.from_integer(1.0)


def test_ninguna_funcion_del_nucleo_usa_coma_flotante() -> None:
    """Analiza el AST del modulo: floats y `math` solo en la frontera numerica.

    Es un test estructural, no de comportamiento: impide que un float se
    cuele en el nucleo en una futura edicion.
    """
    fuente = pathlib.Path(inspect.getfile(cyc)).read_text(encoding="utf-8")
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
            funciones.extend(
                h for h in nodo.body if isinstance(h, ast.FunctionDef)
            )

    # La comprobacion solo tiene valor si el AST ve realmente las funciones.
    assert len(funciones) > 20
    nombres = {f.name for f in funciones}
    assert FRONTERA_NUMERICA <= nombres

    infracciones = {
        f.name: usa_coma_flotante(f)
        for f in funciones
        if f.name not in FRONTERA_NUMERICA and usa_coma_flotante(f)
    }
    assert infracciones == {}, f"coma flotante fuera de la frontera: {infracciones}"


# --------------------------------------------------------------------------
# Frontera numerica (unica seccion con tolerancias)
# --------------------------------------------------------------------------


def test_embedding_numerico_coincide_con_el_valor_esperado() -> None:
    import math

    anillo = CyclotomicRing(16)
    x, y = numeric_embedding_xy(anillo.zeta)
    assert x == pytest.approx(math.cos(2 * math.pi / 16))
    assert y == pytest.approx(math.sin(2 * math.pi / 16))

    cuerda_45 = (anillo.zeta_power(2) - 1).norm_squared()
    assert numeric_embedding_value(cuerda_45) == pytest.approx(
        (2 * math.sin(math.pi / 8)) ** 2
    )

    cuerda_22_5 = (anillo.zeta - 1).norm_squared()
    assert numeric_embedding_value(cuerda_22_5) == pytest.approx(
        (2 * math.sin(math.pi / 16)) ** 2
    )
