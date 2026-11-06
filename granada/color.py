"""Color de la cupula por piezas: paleta y reparto. Prima la estetica.

Criterio, dicho por el usuario el 2026-11-05: la cupula reluciente, como el dia
de su inauguracion, sin la suciedad de los siglos, con colores apagados y
artisticos, y la estetica por delante de la exactitud.

De donde salen los colores
--------------------------
Los **tonos** (H) son los medidos sobre la ortoimagen de AA-415_23 en
`docs/paleta.md`: los de esta cupula, no colores de caja. Lo que se cambia es
la saturacion y el valor, para quitar la suciedad: el yeso y los pigmentos
envejecidos de la foto son mas grises y oscuros que el dia de la obra. Cuanto
se limpia es eleccion estetica (`LIMPIEZA`), no medida.

El reparto tampoco esta documentado (`docs/policromia.md`). Se elige para que
domine el yeso marfil y el color vaya a anillos, en los fondos de las
celdillas arqueadas.
"""

from __future__ import annotations

import colorsys

MEDIDOS = {
    "almagra": "#9C8877",
    "ocre": "#877C66",
    "verde": "#4E6D5E",
    "granate": "#8F776E",
    "azul": "#485864",
}
"""Tonos medios de cada banda de pigmento en `docs/paleta.md`."""

LIMPIEZA = {
    # nombre: (saturacion, valor) de destino; el tono es el medido
    "almagra": (0.45, 0.66),
    "ocre": (0.45, 0.74),
    "verde": (0.32, 0.55),
    "granate": (0.45, 0.52),
    "azul": (0.42, 0.55),
}


def _hex(r: float, g: float, b: float) -> str:
    return "#{:02X}{:02X}{:02X}".format(*(round(c * 255) for c in (r, g, b)))


def limpiar(medido: str, saturacion: float, valor: float) -> str:
    """Mismo tono que `medido`, con la saturacion y el valor dados."""
    r, g, b = (int(medido.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, _, _ = colorsys.rgb_to_hsv(r, g, b)
    return _hex(*colorsys.hsv_to_rgb(h, saturacion, valor))


PALETA = {nombre: limpiar(MEDIDOS[nombre], *LIMPIEZA[nombre]) for nombre in MEDIDOS}
# Yeso de obra nueva: el tono crema del yeso medido (H 40-50), casi blanco.
PALETA["yeso"] = _hex(*colorsys.hsv_to_rgb(42 / 360, 0.10, 0.94))
# Oro apagado: el tono del ocre medido, algo mas saturado y claro.
PALETA["oro"] = limpiar(MEDIDOS["ocre"], 0.55, 0.78)

# Ciclo de anillos para las celdillas arqueadas de las hiladas A, con yeso
# entre medias para que el color respire.
ANILLOS_A = ("azul", "yeso", "almagra", "yeso", "verde", "yeso")
ANILLOS_C = ("ocre", "granate")

NIVELES_SOMBRA = 6
"""Escalones de oclusion que se exportan como materiales distintos."""


def rgb(nombre: str) -> tuple[int, int, int]:
    h = PALETA[nombre].lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def colorear(tipo: str, etiqueta: str, hilada: int, indice: int) -> str:
    """Color de una cara de una pieza de la trama principal."""
    if etiqueta != "fondo":
        return "yeso"
    if tipo == "A3":
        return "oro"
    if tipo == "A2":
        return ANILLOS_A[(hilada // 1) % len(ANILLOS_A)]
    if tipo == "C2":
        return ANILLOS_C[(hilada // 3) % len(ANILLOS_C)]
    return "yeso"


def colorear_cupulin(tipo: str, etiqueta: str, hilada: int, indice: int) -> str:
    """Los cupulines: celdillas en azul, lo demas en yeso."""
    return "azul" if etiqueta == "fondo" and tipo in ("A2", "C2") else "yeso"


def material(nombre: str, sombra: float) -> str:
    """Nombre de material para el OBJ: color y escalon de sombra."""
    nivel = round((1 - sombra) / (1 - SOMBRA_MINIMA) * (NIVELES_SOMBRA - 1))
    return f"{nombre}_{max(0, min(NIVELES_SOMBRA - 1, nivel))}"


SOMBRA_MINIMA = 0.45


def paleta_materiales() -> dict[str, str]:
    """Cada color en `NIVELES_SOMBRA` escalones, para el .mtl del visor."""
    fuera = {}
    for nombre in PALETA:
        r, g, b = rgb(nombre)
        for k in range(NIVELES_SOMBRA):
            f = 1 - k / (NIVELES_SOMBRA - 1) * (1 - SOMBRA_MINIMA)
            fuera[f"{nombre}_{k}"] = _hex(r * f / 255, g * f / 255, b * f / 255)
    return fuera
