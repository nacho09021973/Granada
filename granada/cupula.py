"""Cupula de mocarabes apilando hiladas de piezas de `granada.piezas`.

Cada hilada es un anillo de piezas alternas (frente / vertice) de una familia:
A1/A2 o C1/C2. La hilada k+1 sube un nivel y entra hacia el centro lo justo
para que su trasera coincida con el frente de la hilada k: asi tapa la banda
vertical de la de abajo y deja a la vista su fondo curvo, como en la cupula
real.

Que es dato y que es modelo
---------------------------
Dato (de `datos/niveles_aproximados.json`, calibrado contra la seccion medida,
decision 0009):
- radio de arranque, 3,64 m;
- pendiente del cono, paso vertical / paso horizontal por hilada = 1,28.

Modelo, declarado:
- **la secuencia de familias** (`SECUENCIA`, A A C repetida) y **las A3
  intercaladas** cada 8 piezas en las hiladas A son eleccion de demostracion.
  La secuencia real de Dos Hermanas no esta leida;
- **el tamano de pieza**: el cateto se fija para que una hilada A entre en
  planta lo mismo que una hilada medida (0,158 m), lo que da 0,224 m. Con eso
  caben unas 145 piezas por vuelta en el arranque y salen del orden de 1700 en
  total, contra las 5416 contadas en la lamina X: mismo orden de magnitud, no
  la misma cifra;
- **la altura de nivel** de cada hilada es pendiente * fondo de su familia, para
  que el perfil sea el cono medido. La proporcion del grabado (paso 1,6 cateto)
  daria pendiente 2,26; las piezas salen mas bajas que en el dibujo de Jones;
- en cada hilada el numero de piezas se redondea a multiplo de 8 y las piezas se
  estiran a lo ancho lo necesario para cerrar la vuelta (`estiramiento`);
- las piezas se curvan para seguir el anillo: el frente sobre la circunferencia
  y la profundidad en radial. El oficio usa piezas rectas;
- la cupulilla de cierre y el tambor son superficies de relleno.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

from granada.piezas import C22, R2, S22, Punto3, malla, pieza

RAIZ = Path(__file__).resolve().parents[1]
NIVELES = RAIZ / "datos" / "niveles_aproximados.json"


def _medidas() -> dict:
    return json.loads(NIVELES.read_text(encoding="utf-8"))["metodo"]


_M = _medidas()
PENDIENTE = _M["paso_vertical_hilada_m"] / _M["paso_horizontal_hilada_m"]
RADIO_BASE_M = _M["radio_base_m"]
CATETO_M = _M["paso_horizontal_hilada_m"] / R2
RADIO_BASE = RADIO_BASE_M / CATETO_M
"""Radio de arranque en unidades del cateto."""

RADIO_CIERRE = 2.2
"""Por debajo de este radio de frente no se pone otra hilada: se cierra."""

SECUENCIA = ("A", "A", "C")
CADA_A3 = 8


@dataclass(frozen=True)
class Familia:
    frente: str
    vertice: str
    fondo: float
    """Profundidad radial de la hilada."""
    paso_tangencial: float
    """Distancia entre piezas consecutivas a lo largo del frente."""


FAMILIAS = {
    "A": Familia("A1", "A2", R2, R2),
    "C": Familia("C1", "C2", C22, S22),
}


@dataclass(frozen=True)
class Hilada:
    indice: int
    familia: str
    radio_frente: float
    cota: float
    paso: float
    piezas: int
    estiramiento: float

    def tipos(self) -> list[str]:
        f = FAMILIAS[self.familia]
        fuera = []
        for i in range(self.piezas):
            if i % 2:
                fuera.append(f.vertice)
            elif self.familia == "A" and i % CADA_A3 == 0:
                fuera.append("A3")
            else:
                fuera.append(f.frente)
        return fuera


def plan_de_hiladas(radio_base: float = RADIO_BASE, secuencia=SECUENCIA) -> list[Hilada]:
    """Radios, cotas y numero de piezas de cada hilada, de abajo arriba."""
    hiladas = []
    cota = 0.0
    trasera = radio_base
    k = 0
    while True:
        nombre = secuencia[k % len(secuencia)]
        f = FAMILIAS[nombre]
        radio = trasera - f.fondo
        if radio < RADIO_CIERRE:
            break
        exacto = 2 * math.pi * radio / f.paso_tangencial
        n = max(8, 8 * round(exacto / 8))
        paso = PENDIENTE * f.fondo
        hiladas.append(Hilada(k, nombre, radio, cota, paso, n, exacto / n))
        cota += paso
        trasera = radio
        k += 1
    return hiladas


def doblar(V, angulo: float, radio: float, estiramiento: float, cota: float) -> list[Punto3]:
    """Del marco local de la pieza al anillo, curvandola.

    x (a lo ancho) pasa a longitud de arco sobre el frente; y (hacia el frente)
    a radio, `radio - y`; z sube `cota`.
    """
    fuera = []
    for x, y, z in V:
        a = angulo + x * estiramiento / radio
        r = radio - y
        fuera.append((r * math.cos(a), r * math.sin(a), z + cota))
    return fuera


def _cupulilla(radio: float, cota: float, paso: float, n: int = 96, m: int = 16):
    """Casquete que cierra el hueco central, abierto hacia abajo."""
    V: list[Punto3] = []
    F = []
    arranque = cota + paso * 0.875
    alto = 0.9 * radio
    for j in range(m + 1):
        t = j / m * math.pi / 2
        r = radio * math.cos(t)
        z = arranque + alto * math.sin(t)
        for i in range(n):
            a = 2 * math.pi * i / n
            V.append((r * math.cos(a), r * math.sin(a), z))
    for j in range(m):
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n
            c, d = a + n, b + n
            F.append((a, b, d))
            F.append((a, d, c))
    return V, F


def _tambor(radio: float, abajo: float, arriba: float, n: int = 192):
    V: list[Punto3] = []
    F = []
    for i in range(n):
        a = 2 * math.pi * i / n
        V.append((radio * math.cos(a), radio * math.sin(a), abajo))
        V.append((radio * math.cos(a), radio * math.sin(a), arriba))
    for i in range(n):
        a, b = 2 * i, 2 * ((i + 1) % n)
        F.append((a, b, b + 1))
        F.append((a, b + 1, a + 1))
    return V, F


def cupula(subdivision: int = 8, radio_base: float = RADIO_BASE):
    """Grupos (nombre, V, F): una por hilada, la cupulilla y el tambor."""
    hiladas = plan_de_hiladas(radio_base)
    plantillas: dict[tuple[str, float], tuple] = {}
    grupos = []
    for h in hiladas:
        V: list[Punto3] = []
        F = []
        paso_t = FAMILIAS[h.familia].paso_tangencial
        for i, tipo in enumerate(h.tipos()):
            clave = (tipo, h.paso)
            if clave not in plantillas:
                plantillas[clave] = malla(pieza(tipo, h.paso), subdivision)
            Vp, Fp = plantillas[clave]
            angulo = i * paso_t * h.estiramiento / h.radio_frente
            base = len(V)
            V.extend(doblar(Vp, angulo, h.radio_frente, h.estiramiento, h.cota))
            F.extend((a + base, b + base, c + base) for a, b, c in Fp)
        grupos.append((f"hilada_{h.indice:02d}_{h.familia}", V, F))
    ultima = hiladas[-1]
    grupos.append(("cupulilla", *_cupulilla(ultima.radio_frente, ultima.cota, ultima.paso)))
    # El tambor sube hasta la tapa de la primera hilada: si acabara en su
    # arranque, por las celdillas de esa hilada se veria el vacio.
    grupos.append(("tambor", *_tambor(radio_base, -6.0, 2 * hiladas[0].paso)))
    return hiladas, grupos
