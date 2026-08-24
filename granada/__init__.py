"""Granada: generador de cupulas de mocarabes con geometria algebraicamente exacta.

Estado actual: solo el nucleo aritmetico. Ver README.md.
"""

from granada.celda import (
    Celda,
    anillo,
    cuna,
    numeric_embedding_celda,
    pasos_maximos,
    rombo,
)
from granada.cyclotomic import (
    CyclotomicInteger,
    CyclotomicRing,
    RealCyclotomicInteger,
    cyclotomic_polynomial,
    divisors,
    euler_phi,
    numeric_embedding_value,
    numeric_embedding_xy,
    poly_add,
    poly_divide_exact,
    poly_mul,
    poly_sub,
    poly_trim,
    solve_integer_linear,
    solve_rational_linear,
)

__version__ = "0.1.0"

__all__ = [
    "Celda",
    "CyclotomicInteger",
    "CyclotomicRing",
    "RealCyclotomicInteger",
    "anillo",
    "cuna",
    "cyclotomic_polynomial",
    "divisors",
    "euler_phi",
    "numeric_embedding_celda",
    "numeric_embedding_value",
    "numeric_embedding_xy",
    "pasos_maximos",
    "poly_add",
    "poly_divide_exact",
    "poly_mul",
    "poly_sub",
    "poly_trim",
    "rombo",
    "solve_integer_linear",
    "solve_rational_linear",
    "__version__",
]
