"""Una hilada de mocarabes en anillo, montada con las piezas de `granada.piezas`.

Composicion: A1 y A2 alternas, el frente mirando al centro. Es la combinacion
mas sencilla del alfabeto que forma una franja continua: A1 tiene la hipotenusa
al frente y A2 el vertice, y encajan por los catetos. En esa arista comun las
dos superficies inferiores coinciden exactamente (misma curva, mismo argumento:
ver `test_hilada.py`), que es lo que Jones y Goury dicen en la lamina X: «a
piece may be combined with any one of the others by either of its sides».

Que es modelo
-------------
- Que esta hilada sea A1/A2 alternas es una **eleccion de demostracion**, no una
  lectura de la cupula de Dos Hermanas. La secuencia real de cada hilada no
  esta leida (decision 0008 de la rama `cotas-z-y-falsacion`).
- Las piezas son rectas y se colocan sobre una circunferencia: entre las
  traseras de dos piezas vecinas queda una cuna de 360/N grados que tapa la
  losa superior. Con N = 64 son 5,6 grados.
- La losa superior y el muro trasero son relleno para que la hilada se lea como
  techo; no modelan nada documentado.
"""

from __future__ import annotations

import math

from granada.piezas import ALTURA_PRISMA, R2, Punto3, malla, pieza

PIEZAS_POR_VUELTA = 64
"""Multiplo de 16 para respetar la simetria de orden 8 de la planta y la
alternancia A1/A2."""

CANTO_LOSA = 0.35
VUELO_LOSA = 0.6


def radio_frente(n: int = PIEZAS_POR_VUELTA, paso: float = R2) -> float:
    """Radio del frente: n piezas separadas `paso` a lo largo de la vuelta."""
    return n * paso / (2 * math.pi)


def colocar(V: list[Punto3], angulo: float, radio: float) -> list[Punto3]:
    """Lleva una pieza de su marco local al anillo.

    Local: x tangente, y hacia el frente (el centro), z arriba. El frente
    (y = 0) queda a distancia `radio` del eje.
    """
    c, s = math.cos(angulo), math.sin(angulo)
    fuera = []
    for x, y, z in V:
        r = radio - y
        fuera.append((r * c - x * s, r * s + x * c, z))
    return fuera


def _losa(r_in: float, r_out: float, z0: float, z1: float, n: int):
    """Corona circular maciza, cerrada, con n tramos."""
    V: list[Punto3] = []
    F = []
    for k in range(n):
        a = 2 * math.pi * k / n
        c, s = math.cos(a), math.sin(a)
        V.extend([(r_in * c, r_in * s, z0), (r_out * c, r_out * s, z0),
                  (r_out * c, r_out * s, z1), (r_in * c, r_in * s, z1)])
    for k in range(n):
        a0, a1 = 4 * k, 4 * ((k + 1) % n)
        for i in range(4):
            p, q = a0 + i, a0 + (i + 1) % 4
            p2, q2 = a1 + i, a1 + (i + 1) % 4
            F.append((p, q, q2))
            F.append((p, q2, p2))
    return V, F


def hilada(n: int = PIEZAS_POR_VUELTA, subdivision: int = 24):
    """Grupos (nombre, V, F): las n piezas y la losa que las cubre."""
    radio = radio_frente(n)
    a1 = malla(pieza("A1"), subdivision)
    a2 = malla(pieza("A2"), subdivision)
    grupos = []
    for k in range(n):
        tipo, (V, F) = ("A1", a1) if k % 2 == 0 else ("A2", a2)
        angulo = 2 * math.pi * k / n
        grupos.append((f"{tipo}_{k:02d}", colocar(V, angulo, radio), F))
    fondo = radio + R2
    grupos.append(("losa", *_losa(radio - CANTO_LOSA, fondo + VUELO_LOSA,
                                   ALTURA_PRISMA, ALTURA_PRISMA + CANTO_LOSA, 4 * n)))
    return grupos
