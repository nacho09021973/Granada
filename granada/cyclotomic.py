"""Aritmetica exacta en el anillo de enteros ciclotomicos Z[zeta_m].

Los vertices del plano de un mocarabe con simetria de orden ``m`` viven en
Z[zeta_m] visto como subconjunto de C = R^2, donde zeta_m = exp(2*pi*i/m).

Todo en este modulo es aritmetica entera exacta. Los unicos floats del
paquete aparecen en las funciones cuyo nombre empieza por
``numeric_embedding_``; estan aisladas al final del fichero y no las usa
ningun otro punto del nucleo.

Representacion
--------------
Un elemento es un polinomio con coeficientes enteros modulo el m-esimo
polinomio ciclotomico Phi_m(x). El rango sobre Z es phi(m) y la base es
1, zeta, zeta^2, ..., zeta^(phi(m)-1).

Los polinomios se representan como tuplas de enteros en orden ascendente
de grado: ``(-1, 0, 1)`` es ``x^2 - 1``.
"""

from __future__ import annotations

import math
from fractions import Fraction
from functools import lru_cache
from typing import Iterable, Sequence

__all__ = [
    "euler_phi",
    "divisors",
    "poly_trim",
    "poly_add",
    "poly_sub",
    "poly_mul",
    "poly_divide_exact",
    "cyclotomic_polynomial",
]


# --------------------------------------------------------------------------
# Teoria de numeros elemental
# --------------------------------------------------------------------------


@lru_cache(maxsize=None)
def divisors(n: int) -> tuple[int, ...]:
    """Divisores positivos de ``n``, en orden creciente."""
    if n < 1:
        raise ValueError(f"se esperaba un entero positivo, se recibio {n}")
    small: list[int] = []
    large: list[int] = []
    d = 1
    while d * d <= n:
        if n % d == 0:
            small.append(d)
            if d != n // d:
                large.append(n // d)
        d += 1
    return tuple(small + large[::-1])


@lru_cache(maxsize=None)
def euler_phi(n: int) -> int:
    """Funcion indicatriz de Euler, calculada por factorizacion por prueba."""
    if n < 1:
        raise ValueError(f"se esperaba un entero positivo, se recibio {n}")
    result = n
    remaining = n
    p = 2
    while p * p <= remaining:
        if remaining % p == 0:
            while remaining % p == 0:
                remaining //= p
            result -= result // p
        p += 1 if p == 2 else 2
    if remaining > 1:
        result -= result // remaining
    return result


# --------------------------------------------------------------------------
# Polinomios con coeficientes enteros
# --------------------------------------------------------------------------


def poly_trim(coeffs: Iterable[int]) -> tuple[int, ...]:
    """Elimina los ceros de cabecera. El polinomio nulo es ``()``."""
    out = list(coeffs)
    while out and out[-1] == 0:
        out.pop()
    return tuple(out)


def poly_add(a: Sequence[int], b: Sequence[int]) -> tuple[int, ...]:
    n = max(len(a), len(b))
    return poly_trim(
        (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)
    )


def poly_sub(a: Sequence[int], b: Sequence[int]) -> tuple[int, ...]:
    n = max(len(a), len(b))
    return poly_trim(
        (a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0) for i in range(n)
    )


def poly_mul(a: Sequence[int], b: Sequence[int]) -> tuple[int, ...]:
    if not a or not b:
        return ()
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            out[i + j] += ai * bj
    return poly_trim(out)


def poly_divide_exact(num: Sequence[int], den: Sequence[int]) -> tuple[int, ...]:
    """Division exacta en Z[x]: devuelve ``q`` con ``num == q * den``.

    Lanza ``ValueError`` si la division no es exacta sobre los enteros. No
    interviene ninguna division en coma flotante: se usa ``divmod`` entero y
    se exige resto nulo en cada paso.
    """
    numerator = list(poly_trim(num))
    divisor = list(poly_trim(den))
    if not divisor:
        raise ZeroDivisionError("division de polinomios por cero")
    if not numerator:
        return ()

    deg_d = len(divisor) - 1
    lead = divisor[-1]
    if len(numerator) - 1 < deg_d:
        raise ValueError("division no exacta: el grado del numerador es menor")

    quotient = [0] * (len(numerator) - deg_d)
    for i in range(len(numerator) - 1, deg_d - 1, -1):
        coeff, remainder = divmod(numerator[i], lead)
        if remainder != 0:
            raise ValueError("division no exacta sobre Z")
        quotient[i - deg_d] = coeff
        if coeff == 0:
            continue
        for j in range(deg_d + 1):
            numerator[i - deg_d + j] -= coeff * divisor[j]

    if any(numerator[:deg_d]):
        raise ValueError("division no exacta: resto no nulo")
    return poly_trim(quotient)


@lru_cache(maxsize=None)
def cyclotomic_polynomial(m: int) -> tuple[int, ...]:
    """Phi_m(x) con coeficientes enteros exactos.

    Se calcula a partir de la identidad

        x^m - 1 = producto de Phi_d(x) sobre los divisores d de m

    dividiendo x^m - 1 por Phi_d para cada divisor propio d. Todas las
    divisiones son exactas sobre Z porque los Phi_d son monicos.
    """
    if m < 1:
        raise ValueError(f"se esperaba un entero positivo, se recibio {m}")
    if m == 1:
        return (-1, 1)  # x - 1

    # x^m - 1
    result: tuple[int, ...] = (-1,) + (0,) * (m - 1) + (1,)
    for d in divisors(m):
        if d < m:
            result = poly_divide_exact(result, cyclotomic_polynomial(d))
    return result
