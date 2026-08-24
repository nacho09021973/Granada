"""Granada: generador de cupulas de mocarabes con geometria algebraicamente exacta.

Estado actual: solo el nucleo aritmetico. Ver README.md.
"""

from granada.adaraja import (
    PESO_CIRCULO,
    PESO_PARABOLA,
    TIRO_CUENCO,
    TIRO_RECTO,
    PerfilArco,
    PuntoMalla,
    malla_adaraja,
    numeric_embedding_punto,
)
from granada.celda import (
    Celda,
    anillo,
    cuna,
    numeric_embedding_celda,
    pasos_maximos,
    rombo,
    trapecio,
)
from granada.estratificacion import (
    HILADAS_MEDIDAS,
    RAZON_MEDIDA,
    Estratificacion,
    numeric_embedding_hilada,
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
    "PerfilArco",
    "PuntoMalla",
    "PESO_CIRCULO",
    "PESO_PARABOLA",
    "TIRO_CUENCO",
    "TIRO_RECTO",
    "Estratificacion",
    "HILADAS_MEDIDAS",
    "RAZON_MEDIDA",
    "CyclotomicInteger",
    "CyclotomicRing",
    "RealCyclotomicInteger",
    "anillo",
    "cuna",
    "cyclotomic_polynomial",
    "divisors",
    "euler_phi",
    "malla_adaraja",
    "numeric_embedding_celda",
    "numeric_embedding_hilada",
    "numeric_embedding_punto",
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
    "trapecio",
    "__version__",
]
