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
    "CyclotomicRing",
    "CyclotomicInteger",
    "RealCyclotomicInteger",
    "solve_rational_linear",
    "solve_integer_linear",
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


# --------------------------------------------------------------------------
# El anillo Z[zeta_m] = Z[x] / Phi_m(x)
# --------------------------------------------------------------------------


class CyclotomicRing:
    """El anillo de enteros ciclotomicos Z[zeta_m], con zeta_m = e^(2 pi i / m).

    Los elementos son instancias de :class:`CyclotomicInteger`, expresados en
    la base 1, zeta, ..., zeta^(phi(m)-1) sobre Z.
    """

    __slots__ = ("m", "degree", "polynomial", "_zeta_powers", "_real_basis")

    def __init__(self, m: int) -> None:
        if m < 1:
            raise ValueError(f"el orden de simetria debe ser >= 1, se recibio {m}")
        self.m = m
        self.polynomial = cyclotomic_polynomial(m)
        self.degree = len(self.polynomial) - 1  # == euler_phi(m)
        self._zeta_powers: tuple[CyclotomicInteger, ...] | None = None
        self._real_basis: tuple[CyclotomicInteger, ...] | None = None

    # -- construccion de elementos -----------------------------------------

    def element(self, coeffs: Sequence[int]) -> "CyclotomicInteger":
        """Elemento a partir de coeficientes enteros en la base de potencias.

        Se admiten secuencias mas largas que phi(m): se reducen modulo Phi_m.
        """
        for c in coeffs:
            if not isinstance(c, int) or isinstance(c, bool):
                raise TypeError(
                    f"los coeficientes deben ser enteros de Python, se recibio {c!r}"
                )
        return CyclotomicInteger(self, self.reduce(coeffs))

    @property
    def zero(self) -> "CyclotomicInteger":
        return CyclotomicInteger(self, (0,) * self.degree)

    @property
    def one(self) -> "CyclotomicInteger":
        return self.from_integer(1)

    @property
    def zeta(self) -> "CyclotomicInteger":
        """La raiz primitiva zeta_m: rotacion de 2*pi/m."""
        return self.zeta_power(1)

    def from_integer(self, n: int) -> "CyclotomicInteger":
        if not isinstance(n, int) or isinstance(n, bool):
            raise TypeError(f"se esperaba un entero, se recibio {n!r}")
        coeffs = [0] * self.degree
        coeffs[0] = n
        return CyclotomicInteger(self, tuple(coeffs))

    def zeta_power(self, k: int) -> "CyclotomicInteger":
        """zeta^k para cualquier entero k (se toma k modulo m)."""
        return self._zeta_power_table()[k % self.m]

    def _zeta_power_table(self) -> tuple["CyclotomicInteger", ...]:
        if self._zeta_powers is None:
            # zeta^0 .. zeta^(m-1), construidas por multiplicaciones sucesivas
            # por x seguidas de reduccion modulo Phi_m.
            powers = [self.from_integer(1)]
            for _ in range(1, self.m):
                shifted = (0,) + powers[-1].coeffs
                powers.append(CyclotomicInteger(self, self.reduce(shifted)))
            self._zeta_powers = tuple(powers)
        return self._zeta_powers

    # -- reduccion modulo Phi_m --------------------------------------------

    def reduce(self, coeffs: Sequence[int]) -> tuple[int, ...]:
        """Reduce un vector de coeficientes modulo Phi_m(x).

        Phi_m es monico, asi que x^n = -(c_0 + c_1 x + ... + c_(n-1) x^(n-1))
        con n = phi(m), y la reduccion es puramente entera.
        """
        n = self.degree
        work = list(coeffs)
        if len(work) < n:
            work.extend([0] * (n - len(work)))
        phi_coeffs = self.polynomial
        for i in range(len(work) - 1, n - 1, -1):
            a = work[i]
            if a == 0:
                continue
            work[i] = 0
            base = i - n
            for j in range(n):
                work[base + j] -= a * phi_coeffs[j]
        return tuple(work[:n])

    # -- subanillo real Z[lambda], lambda = zeta + zeta^(-1) ----------------

    @property
    def real_rank(self) -> int:
        """Rango sobre Z del subanillo real: phi(m)/2 para m > 2, si no 1."""
        return self.degree // 2 if self.degree >= 2 else 1

    def real_lambda(self) -> "CyclotomicInteger":
        """lambda = zeta + zeta^(-1) = 2*cos(2*pi/m), como elemento de Z[zeta_m]."""
        return self.zeta_power(1) + self.zeta_power(-1)

    def real_basis(self) -> tuple["CyclotomicInteger", ...]:
        """Base 1, lambda, ..., lambda^(d-1) del subanillo real, en Z[zeta_m]."""
        if self._real_basis is None:
            lam = self.real_lambda()
            basis = [self.one]
            for _ in range(1, self.real_rank):
                basis.append(basis[-1] * lam)
            self._real_basis = tuple(basis)
        return self._real_basis

    def real_element(self, coeffs: Sequence[int]) -> "RealCyclotomicInteger":
        """Elemento del subanillo real a partir de coeficientes en base lambda."""
        values = list(coeffs)
        if len(values) > self.real_rank:
            raise ValueError(
                f"se esperaban como mucho {self.real_rank} coeficientes, "
                f"se recibieron {len(values)}"
            )
        for c in values:
            if not isinstance(c, int) or isinstance(c, bool):
                raise TypeError(
                    f"los coeficientes deben ser enteros de Python, se recibio {c!r}"
                )
        values.extend([0] * (self.real_rank - len(values)))
        return RealCyclotomicInteger(self, tuple(values))

    def to_real(self, element: "CyclotomicInteger") -> "RealCyclotomicInteger":
        """Expresa un elemento real de Z[zeta_m] en la base de lambda.

        Lanza ``ValueError`` si el elemento no es invariante por conjugacion
        (es decir, si no es real) o si, siendolo, no admite coeficientes
        enteros en la base de lambda; esto ultimo no deberia ocurrir, porque
        Z[zeta_m] ∩ R = Z[lambda].
        """
        if element.ring.m != self.m:
            raise ValueError("el elemento pertenece a otro anillo")
        if element.conjugate() != element:
            raise ValueError(
                "el elemento no es real: no coincide con su conjugado complejo"
            )
        columns = [b.coeffs for b in self.real_basis()]
        solution = solve_integer_linear(columns, element.coeffs)
        if solution is None:
            raise ValueError(
                "el elemento real no admite coeficientes enteros en la base de lambda"
            )
        return RealCyclotomicInteger(self, solution)

    # -- protocolo ----------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CyclotomicRing) and other.m == self.m

    def __hash__(self) -> int:
        return hash(("CyclotomicRing", self.m))

    def __repr__(self) -> str:
        return f"CyclotomicRing(m={self.m}, rango={self.degree})"


class CyclotomicInteger:
    """Un elemento de Z[zeta_m]. Inmutable, con aritmetica entera exacta."""

    __slots__ = ("ring", "coeffs")

    def __init__(self, ring: CyclotomicRing, coeffs: tuple[int, ...]) -> None:
        self.ring = ring
        self.coeffs = coeffs

    # -- utilidades internas ------------------------------------------------

    def _check_same_ring(self, other: "CyclotomicInteger") -> None:
        if self.ring.m != other.ring.m:
            raise ValueError(
                f"elementos de anillos distintos: m={self.ring.m} y m={other.ring.m}"
            )

    def _coerce(self, other: object) -> "CyclotomicInteger | None":
        if isinstance(other, CyclotomicInteger):
            self._check_same_ring(other)
            return other
        if isinstance(other, int) and not isinstance(other, bool):
            return self.ring.from_integer(other)
        return None

    # -- aritmetica ---------------------------------------------------------

    def __add__(self, other: object) -> "CyclotomicInteger":
        rhs = self._coerce(other)
        if rhs is None:
            return NotImplemented
        return CyclotomicInteger(
            self.ring, tuple(a + b for a, b in zip(self.coeffs, rhs.coeffs))
        )

    __radd__ = __add__

    def __sub__(self, other: object) -> "CyclotomicInteger":
        rhs = self._coerce(other)
        if rhs is None:
            return NotImplemented
        return CyclotomicInteger(
            self.ring, tuple(a - b for a, b in zip(self.coeffs, rhs.coeffs))
        )

    def __rsub__(self, other: object) -> "CyclotomicInteger":
        lhs = self._coerce(other)
        if lhs is None:
            return NotImplemented
        return lhs - self

    def __neg__(self) -> "CyclotomicInteger":
        return CyclotomicInteger(self.ring, tuple(-a for a in self.coeffs))

    def __mul__(self, other: object) -> "CyclotomicInteger":
        rhs = self._coerce(other)
        if rhs is None:
            return NotImplemented
        product = poly_mul(self.coeffs, rhs.coeffs)
        return CyclotomicInteger(self.ring, self.ring.reduce(product))

    __rmul__ = __mul__

    def __pow__(self, exponent: int) -> "CyclotomicInteger":
        if not isinstance(exponent, int) or isinstance(exponent, bool):
            raise TypeError(f"exponente no entero: {exponent!r}")
        if exponent < 0:
            raise ValueError(
                "exponente negativo: Z[zeta_m] no es cerrado bajo inversion"
            )
        result = self.ring.one
        base = self
        e = exponent
        while e:
            if e & 1:
                result = result * base
            e >>= 1
            if e:
                base = base * base
        return result

    # -- simetrias ----------------------------------------------------------

    def rotate(self, k: int = 1) -> "CyclotomicInteger":
        """Rotacion de k * 2*pi/m: multiplicacion por zeta^k. Exacta."""
        return self * self.ring.zeta_power(k)

    def conjugate(self) -> "CyclotomicInteger":
        """Conjugacion compleja: zeta -> zeta^(-1) = zeta^(m-1).

        Es la reflexion respecto del eje real. Como automorfismo del anillo,
        envia sum a_k zeta^k a sum a_k zeta^(-k).
        """
        m = self.ring.m
        result = self.ring.zero
        for k, a in enumerate(self.coeffs):
            if a == 0:
                continue
            result = result + a * self.ring.zeta_power((-k) % m)
        return result

    def norm_squared(self) -> "RealCyclotomicInteger":
        """|z|^2 = z * conj(z), en el subanillo real Z[2*cos(2*pi/m)].

        El resultado es exacto: coeficientes enteros en la base de potencias
        de lambda = zeta + zeta^(-1).
        """
        return self.ring.to_real(self * self.conjugate())

    # -- protocolo ----------------------------------------------------------

    def is_zero(self) -> bool:
        return all(a == 0 for a in self.coeffs)

    def __eq__(self, other: object) -> bool:
        rhs = self._coerce(other) if not isinstance(other, CyclotomicInteger) else other
        if rhs is None:
            return NotImplemented
        if isinstance(rhs, CyclotomicInteger) and rhs.ring.m != self.ring.m:
            return False
        return self.coeffs == rhs.coeffs

    def __hash__(self) -> int:
        return hash((self.ring.m, self.coeffs))

    def __repr__(self) -> str:
        return f"CyclotomicInteger(m={self.ring.m}, {list(self.coeffs)})"

    def __str__(self) -> str:
        terms = []
        for k, a in enumerate(self.coeffs):
            if a == 0:
                continue
            if k == 0:
                terms.append(str(a))
            elif k == 1:
                terms.append(f"{a}*z")
            else:
                terms.append(f"{a}*z^{k}")
        return " + ".join(terms) if terms else "0"


# --------------------------------------------------------------------------
# Algebra lineal exacta sobre Q (auxiliar, sin coma flotante)
# --------------------------------------------------------------------------


def solve_rational_linear(
    columns: Sequence[Sequence[int]], target: Sequence[int]
) -> tuple[Fraction, ...] | None:
    """Resuelve ``sum_j c_j * columns[j] == target`` sobre Q.

    Devuelve los coeficientes como ``Fraction`` (aritmetica racional exacta,
    no coma flotante), o ``None`` si el sistema es incompatible. Se asume
    que las columnas son linealmente independientes; si no lo son, a las
    variables libres se les asigna cero.
    """
    rows = len(target)
    ncols = len(columns)
    for col in columns:
        if len(col) != rows:
            raise ValueError("columnas y objetivo de dimensiones distintas")

    matrix = [
        [Fraction(columns[j][i]) for j in range(ncols)] + [Fraction(target[i])]
        for i in range(rows)
    ]

    pivot_cols: list[int] = []
    pivot_row = 0
    for col in range(ncols):
        found = None
        for i in range(pivot_row, rows):
            if matrix[i][col] != 0:
                found = i
                break
        if found is None:
            continue
        matrix[pivot_row], matrix[found] = matrix[found], matrix[pivot_row]
        pivot = matrix[pivot_row][col]
        matrix[pivot_row] = [v / pivot for v in matrix[pivot_row]]
        for i in range(rows):
            if i != pivot_row and matrix[i][col] != 0:
                factor = matrix[i][col]
                matrix[i] = [
                    a - factor * b for a, b in zip(matrix[i], matrix[pivot_row])
                ]
        pivot_cols.append(col)
        pivot_row += 1
        if pivot_row == rows:
            break

    for i in range(pivot_row, rows):
        if matrix[i][ncols] != 0:
            return None  # incompatible

    solution = [Fraction(0)] * ncols
    for i, col in enumerate(pivot_cols):
        solution[col] = matrix[i][ncols]
    return tuple(solution)


def solve_integer_linear(
    columns: Sequence[Sequence[int]], target: Sequence[int]
) -> tuple[int, ...] | None:
    """Como :func:`solve_rational_linear` pero exige solucion entera.

    Devuelve ``None`` si el sistema es incompatible sobre Q o si la solucion
    racional tiene denominadores distintos de 1.
    """
    rational = solve_rational_linear(columns, target)
    if rational is None:
        return None
    if any(c.denominator != 1 for c in rational):
        return None
    return tuple(int(c) for c in rational)


# --------------------------------------------------------------------------
# El subanillo real Z[2*cos(2*pi/m)]
# --------------------------------------------------------------------------


class RealCyclotomicInteger:
    """Un elemento del subanillo real Z[lambda], con lambda = zeta + zeta^(-1).

    lambda = 2*cos(2*pi/m). Los coeficientes son enteros en la base de
    potencias 1, lambda, lambda^2, ..., lambda^(d-1), donde d es el rango del
    subanillo real (phi(m)/2 para m > 2).

    Es aqui donde aterrizan las normas al cuadrado |z|^2.
    """

    __slots__ = ("ring", "coeffs")

    def __init__(self, ring: CyclotomicRing, coeffs: tuple[int, ...]) -> None:
        self.ring = ring
        self.coeffs = coeffs

    # -- conversion ---------------------------------------------------------

    def to_cyclotomic(self) -> CyclotomicInteger:
        """Reinterpreta el elemento dentro de Z[zeta_m]."""
        result = self.ring.zero
        for power, coeff in zip(self.ring.real_basis(), self.coeffs):
            if coeff != 0:
                result = result + coeff * power
        return result

    # -- aritmetica ---------------------------------------------------------
    #
    # Se delega en Z[zeta_m] y se vuelve a expresar en la base de lambda. El
    # subanillo real es cerrado bajo suma y producto, asi que la vuelta
    # siempre existe y es entera.

    def _coerce(self, other: object) -> "RealCyclotomicInteger | None":
        if isinstance(other, RealCyclotomicInteger):
            if other.ring.m != self.ring.m:
                raise ValueError(
                    f"elementos de anillos distintos: m={self.ring.m} y m={other.ring.m}"
                )
            return other
        if isinstance(other, int) and not isinstance(other, bool):
            coeffs = [0] * len(self.coeffs)
            coeffs[0] = other
            return RealCyclotomicInteger(self.ring, tuple(coeffs))
        return None

    def __add__(self, other: object) -> "RealCyclotomicInteger":
        rhs = self._coerce(other)
        if rhs is None:
            return NotImplemented
        return RealCyclotomicInteger(
            self.ring, tuple(a + b for a, b in zip(self.coeffs, rhs.coeffs))
        )

    __radd__ = __add__

    def __sub__(self, other: object) -> "RealCyclotomicInteger":
        rhs = self._coerce(other)
        if rhs is None:
            return NotImplemented
        return RealCyclotomicInteger(
            self.ring, tuple(a - b for a, b in zip(self.coeffs, rhs.coeffs))
        )

    def __rsub__(self, other: object) -> "RealCyclotomicInteger":
        lhs = self._coerce(other)
        if lhs is None:
            return NotImplemented
        return lhs - self

    def __neg__(self) -> "RealCyclotomicInteger":
        return RealCyclotomicInteger(self.ring, tuple(-a for a in self.coeffs))

    def __mul__(self, other: object) -> "RealCyclotomicInteger":
        rhs = self._coerce(other)
        if rhs is None:
            return NotImplemented
        product = self.to_cyclotomic() * rhs.to_cyclotomic()
        return self.ring.to_real(product)

    __rmul__ = __mul__

    def __pow__(self, exponent: int) -> "RealCyclotomicInteger":
        if not isinstance(exponent, int) or isinstance(exponent, bool):
            raise TypeError(f"exponente no entero: {exponent!r}")
        if exponent < 0:
            raise ValueError("exponente negativo: Z[lambda] no es cerrado bajo inversion")
        return self.ring.to_real(self.to_cyclotomic() ** exponent)

    # -- protocolo ----------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        rhs = (
            other
            if isinstance(other, RealCyclotomicInteger)
            else self._coerce(other)
        )
        if rhs is None:
            return NotImplemented
        if rhs.ring.m != self.ring.m:
            return False
        return self.coeffs == rhs.coeffs

    def __hash__(self) -> int:
        return hash((self.ring.m, "real", self.coeffs))

    def __repr__(self) -> str:
        return f"RealCyclotomicInteger(m={self.ring.m}, {list(self.coeffs)})"

    def __str__(self) -> str:
        terms = []
        for k, a in enumerate(self.coeffs):
            if a == 0:
                continue
            if k == 0:
                terms.append(str(a))
            elif k == 1:
                terms.append(f"{a}*L")
            else:
                terms.append(f"{a}*L^{k}")
        return " + ".join(terms) if terms else "0"
