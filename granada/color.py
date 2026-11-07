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
import json
import zlib
from pathlib import Path
from typing import Callable, Mapping

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


PALETA_LIMPIA = {nombre: limpiar(MEDIDOS[nombre], *LIMPIEZA[nombre]) for nombre in MEDIDOS}
# Yeso de obra nueva: el tono crema del yeso medido (H 40-50), casi blanco.
PALETA_LIMPIA["yeso"] = _hex(*colorsys.hsv_to_rgb(42 / 360, 0.10, 0.94))
# Oro apagado: el tono del ocre medido, algo mas saturado y claro.
PALETA_LIMPIA["oro"] = limpiar(MEDIDOS["ocre"], 0.55, 0.78)
"""Paleta del 2026-11-05: la cupula reluciente, con los tonos limpiados."""

# --- Paleta de la fotografia (2026-11-06) ----------------------------------
#
# Pedido por el usuario: el color de la fotografia, no el limpiado. Se toman
# tal cual las medianas de datos/acentos_ortoimagen.json
# (scripts/medir_acentos_ortoimagen.py): el yeso es el cuartil claro de los
# pixeles acromaticos y cada pigmento la mediana de su banda con el filtro de
# docs/paleta.md (S >= 0,20, V >= 0,28). Se comprobo alli que la banda tierra
# no es suciedad de baja saturacion: domina igual con S >= 0,40 y con
# V >= 0,45. El oro no esta en la foto: queda el limpio, solo para filetes.

ACENTOS = Path(__file__).resolve().parents[1] / "datos" / "acentos_ortoimagen.json"
_FILTRO = "S>=0.20 V>=0.28"
_BANDA = {"almagra": "tierra", "ocre": "ocre", "verde": "verde", "granate": "granate", "azul": "azul"}


def _paleta_foto() -> tuple[dict[str, str], dict[str, float]]:
    d = json.loads(ACENTOS.read_text(encoding="utf-8"))
    bandas = d["por_umbral"][_FILTRO]["bandas"]
    paleta = {n: bandas[b]["mediana"] for n, b in _BANDA.items()}
    paleta["yeso"] = d["yeso"]["mediana_cuartil_claro"]
    paleta["oro"] = PALETA_LIMPIA["oro"]
    return paleta, {n: bandas[b]["peso"] for n, b in _BANDA.items()}


PALETA_FOTO, PESOS_FOTO = _paleta_foto()
PALETA = PALETA_FOTO
# Huecos de la sala (arco de entrada, ventana alta), vistos desde dentro.
PALETA["hueco"] = "#16130F"

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


# --- Reparto disperso: yeso blanco con policromia suelta -----------------
#
# Pedido por el usuario el 2026-11-06 tras comparar el render con la
# ortoimagen de AA-415_23: la cupula real es casi toda yeso blanco, con toques
# sueltos de color en celdillas, no anillos saturados. Sigue siendo eleccion
# estetica: que celdilla lleva color no esta documentado (docs/policromia.md).
#
# - Solo se pintan fondos de celdilla; tapas y paredes quedan en yeso.
# - Cada celdilla se pinta o no por un sorteo determinista (crc32), igual en
#   los ocho sectores: el color respeta la rotacion C8 de la planta, sin espejo.
# - Los pesos de cada pigmento son los de la fotografia (PESOS_FOTO), con el
#   mismo filtro que la paleta.

PESOS_DISPERSO = PESOS_FOTO
PROBABILIDAD_DISPERSO = 0.25
"""Fraccion de celdillas que llevan color. Calibrada con
scripts/medir_cobertura_color.py para que la vista cenital tenga una fraccion
de pixeles de pigmento parecida a la de la ortoimagen (17,2 %, filtro de
docs/paleta.md). Con la paleta de la fotografia: 0,20 da 11,2 %, 0,25 da
17,0 % y 0,32 da 24,1 %; sin color, alrededor del 1 %."""


def _sorteo(*clave: object) -> float:
    """Numero en [0, 1) fijo para cada clave."""
    return zlib.crc32("|".join(map(str, clave)).encode()) / 2**32


def _pigmento(u: float) -> str:
    total = sum(PESOS_DISPERSO.values())
    acumulado = 0.0
    for nombre, peso in PESOS_DISPERSO.items():
        acumulado += peso / total
        if u < acumulado:
            return nombre
    return nombre


def _celdilla(tipo: str, etiqueta: str, hilada: int, posicion: int, ambito: str) -> str:
    if etiqueta != "fondo":
        return "yeso"
    if _sorteo(ambito, "pinta", hilada, tipo, posicion) >= PROBABILIDAD_DISPERSO:
        return "yeso"
    return _pigmento(_sorteo(ambito, "pigmento", hilada, tipo, posicion))


def disperso(piezas_por_sector: Mapping[int, int]) -> Callable[[str, str, int, int], str]:
    """Reparto disperso para la cupula principal. `piezas_por_sector[h]` es el
    numero de piezas de la hilada h en un octavo: la posicion dentro del
    sector, no el indice absoluto, decide el sorteo."""

    def colorear_disperso(tipo: str, etiqueta: str, hilada: int, indice: int) -> str:
        return _celdilla(tipo, etiqueta, hilada, indice % piezas_por_sector[hilada], "cupula")

    return colorear_disperso


def colorear_cupulin_disperso(tipo: str, etiqueta: str, hilada: int, indice: int) -> str:
    """Los 16 cupulines son copias: el mismo sorteo en todos."""
    return _celdilla(tipo, etiqueta, hilada, indice, "cupulin")


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
