"""Color de la cupula por piezas: paleta y reparto. Restitucion, no medida.

Pigmentos: los que documenta el Patronato para las yeserias de la Alhambra
(`docs/policromia.md`): azul (lazurita, lapislazuli), rojo (bermellon o
minio), verde y negro, con oro y plata. Sobre la ortoimagen de esta cupula, el
verde se sostiene, el azul debilmente y el rojo no se distingue de la suciedad;
el reparto por celdas **no esta establecido** en ninguna fuente localizada.

Por eso todo lo que sigue es eleccion para una imagen de obra nueva:
- los valores hexadecimales son tonos saturados de esos pigmentos, no medidos;
  la paleta medida de `docs/paleta.md` es la del estado actual, sucio y perdido;
- el reparto: fondos curvos de las celdillas en azul, rojo y verde alternando
  por tipo de pieza y por hilada; caras verticales y tapas en yeso; nichos de
  A3 y cupulillas en oro.
"""

from __future__ import annotations

PALETA = {
    "yeso": "#F2EBDD",
    "azul": "#1E4D9B",
    "rojo": "#B8372C",
    "verde": "#2E7A55",
    "oro": "#C9A43A",
}

_ROTACION = ("azul", "rojo", "verde")
_DESFASE = {"A1": 0, "A2": 1, "C1": 2, "C2": 0, "B": 1, "C3": 2}


def rgb(nombre: str) -> tuple[int, int, int]:
    h = PALETA[nombre].lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def colorear(tipo: str, etiqueta: str, hilada: int, indice: int) -> str:
    """Color de una cara de una pieza de la trama principal."""
    if etiqueta != "fondo":
        return "yeso"
    if tipo == "A3":
        return "oro"
    return _ROTACION[(_DESFASE[tipo] + hilada) % len(_ROTACION)]


def colorear_cupulin(tipo: str, etiqueta: str, hilada: int, indice: int) -> str:
    """Los cupulines: fondos en azul, lo demas en yeso."""
    return "azul" if etiqueta == "fondo" else "yeso"
