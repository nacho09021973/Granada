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
- en cada hilada el numero de piezas se redondea a multiplo de 16 (orden 8 con
  la alternancia intacta en cada sector) y las piezas se
  estiran a lo ancho lo necesario para cerrar la vuelta (`estiramiento`);
- **la planta**: cada hilada sigue el contorno r = F * g(phi, F). En el
  arranque g es el octogono de la sala (lados planos a 0 y 45 grados, como en la
  ortoimagen de AA-415_23); en el cierre, la estrella de ocho puntas de dos
  cuadrados, con las puntas a 0 y 45 grados como los 8 medios cuadrados de la
  estrella central (`docs/teselado.md`, orbita C8). Entre ambos, mezcla en F
  que completa la estrella al 60 % del recorrido (`ESTRELLA_COMPLETA`). La forma de las hiladas intermedias **no** esta leida de la cupula;
- las piezas se colocan en coordenadas (phi, F): el frente sobre su contorno,
  repartidas por longitud de arco, y la profundidad a lo largo de phi constante.
  Asi la trasera de cada hilada cae exactamente en el frente de la anterior; a
  cambio las piezas se tuercen donde el contorno no es perpendicular al radio.
  El oficio usa piezas rectas;
- la cupulilla de cierre y el tambor son superficies de relleno.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

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

MUESTRAS_CONTORNO = 2880

ESTRELLA_COMPLETA = 0.6
"""Fraccion del recorrido del arranque al cierre en la que la estrella ya esta
formada del todo. A ojo sobre la ortoimagen, donde el trazado estrellado ocupa
mas o menos el 60 % interior. La transicion es un smoothstep."""


def _octogono(phi):
    """Octogono de apotema 1 con lados planos mirando a 0, 45, 90... grados."""
    u = np.mod(phi + math.pi / 8, math.pi / 4) - math.pi / 8
    return 1.0 / np.cos(u)


def _estrella(phi):
    """Estrella de ocho puntas: union de dos cuadrados de apotema 1, girados 45
    grados. Puntas a 0, 45, 90... grados; entrantes a 22,5."""
    a = 1.0 / np.maximum(np.abs(np.cos(phi)), np.abs(np.sin(phi)))
    b = 1.0 / np.maximum(np.abs(np.cos(phi - math.pi / 4)), np.abs(np.sin(phi - math.pi / 4)))
    return np.maximum(a, b)


_PHI = np.linspace(0, 2 * math.pi, MUESTRAS_CONTORNO, endpoint=False)
_MEDIA_OCT = float(_octogono(_PHI).mean())
_MEDIA_EST = float(_estrella(_PHI).mean())


@dataclass(frozen=True)
class Planta:
    """Familia de contornos r = F * g(phi, F), con F el radio medio."""

    radio_base: float
    radio_cierre: float
    estrella: bool = True

    def mezcla(self, F):
        if not self.estrella:
            return np.zeros_like(np.asarray(F, dtype=float))
        t = (self.radio_base - np.asarray(F, dtype=float)) / (self.radio_base - self.radio_cierre)
        u = np.clip(t / ESTRELLA_COMPLETA, 0.0, 1.0)
        return u * u * (3 - 2 * u)

    def forma(self, phi, F):
        if not self.estrella:
            return np.ones_like(np.asarray(phi, dtype=float))
        lam = self.mezcla(F)
        return (1 - lam) * _octogono(phi) / _MEDIA_OCT + lam * _estrella(phi) / _MEDIA_EST

    def punto(self, phi, F):
        r = np.asarray(F) * self.forma(phi, F)
        return r * np.cos(phi), r * np.sin(phi)

    def arco(self, F):
        """Tabla (longitud acumulada, phi) del contorno F, y su longitud."""
        phi = np.append(_PHI, 2 * math.pi)
        x, y = self.punto(phi, np.full_like(phi, F))
        seg = np.hypot(np.diff(x), np.diff(y))
        s = np.concatenate([[0.0], np.cumsum(seg)])
        return s, phi, float(s[-1])


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


def planta_por_defecto(radio_base: float = RADIO_BASE, estrella: bool = True) -> Planta:
    """La planta cuyo cierre es la ultima hilada que cabe con `RADIO_CIERRE`."""
    circulo = plan_de_hiladas(radio_base, planta=Planta(radio_base, RADIO_CIERRE, False))
    return Planta(radio_base, circulo[-1].radio_frente, estrella)


def plan_de_hiladas(radio_base: float = RADIO_BASE, secuencia=SECUENCIA, planta: Planta | None = None) -> list[Hilada]:
    """Radios medios, cotas y numero de piezas de cada hilada, de abajo arriba."""
    if planta is None:
        planta = planta_por_defecto(radio_base)
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
        exacto = planta.arco(radio)[2] / f.paso_tangencial
        n = max(16, 16 * round(exacto / 16))
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


def en_contorno(V, planta: Planta, radio: float, arco, inicio: float, estiramiento: float, cota: float):
    """Del marco local de la pieza a la hilada de radio medio `radio`.

    x pasa a longitud de arco sobre el contorno desde `inicio`; y (hacia el
    frente) a F = radio - y, con phi constante; z sube `cota`.
    """
    s_tabla, phi_tabla, largo = arco
    P = np.asarray(V, dtype=float)
    s = np.mod(inicio + P[:, 0] * estiramiento, largo)
    phi = np.interp(s, s_tabla, phi_tabla)
    F = radio - P[:, 1]
    x, y = planta.punto(phi, F)
    return list(zip(x.tolist(), y.tolist(), (P[:, 2] + cota).tolist()))


def _cupulilla(planta: Planta, radio: float, cota: float, paso: float, n: int = 192, m: int = 16):
    """Casquete con la planta del ultimo contorno, abierto hacia abajo."""
    V: list[Punto3] = []
    F = []
    arranque = cota + paso * 0.875
    alto = 0.9 * radio
    phi = 2 * math.pi * np.arange(n) / n
    borde = radio * planta.forma(phi, np.full(n, radio))
    for j in range(m + 1):
        t = j / m * math.pi / 2
        z = arranque + alto * math.sin(t)
        for i in range(n):
            r = borde[i] * math.cos(t)
            V.append((r * math.cos(phi[i]), r * math.sin(phi[i]), z))
    for j in range(m):
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n
            c, d = a + n, b + n
            F.append((a, b, d))
            F.append((a, d, c))
    return V, F


def _tambor(planta: Planta, radio: float, abajo: float, arriba: float, n: int = 384):
    """Muro vertical sobre el contorno de arranque."""
    V: list[Punto3] = []
    F = []
    phi = 2 * math.pi * np.arange(n) / n
    x, y = planta.punto(phi, np.full(n, radio))
    for i in range(n):
        V.append((float(x[i]), float(y[i]), abajo))
        V.append((float(x[i]), float(y[i]), arriba))
    for i in range(n):
        a, b = 2 * i, 2 * ((i + 1) % n)
        F.append((a, b, b + 1))
        F.append((a, b + 1, a + 1))
    return V, F


def cupula(subdivision: int = 8, radio_base: float = RADIO_BASE, estrella: bool = True):
    """Grupos (nombre, V, F): una por hilada, la cupulilla y el tambor."""
    planta = planta_por_defecto(radio_base, estrella)
    hiladas = plan_de_hiladas(radio_base, planta=planta)
    plantillas: dict[tuple[str, float], tuple] = {}
    grupos = []
    for h in hiladas:
        V: list[Punto3] = []
        F = []
        paso_t = FAMILIAS[h.familia].paso_tangencial
        arco = planta.arco(h.radio_frente)
        for i, tipo in enumerate(h.tipos()):
            clave = (tipo, h.paso)
            if clave not in plantillas:
                plantillas[clave] = malla(pieza(tipo, h.paso), subdivision)
            Vp, Fp = plantillas[clave]
            inicio = i * paso_t * h.estiramiento
            base = len(V)
            V.extend(en_contorno(Vp, planta, h.radio_frente, arco, inicio, h.estiramiento, h.cota))
            F.extend((a + base, b + base, c + base) for a, b, c in Fp)
        grupos.append((f"hilada_{h.indice:02d}_{h.familia}", V, F))
    ultima = hiladas[-1]
    grupos.append(("cupulilla", *_cupulilla(planta, ultima.radio_frente, ultima.cota, ultima.paso)))
    # El tambor sube hasta la tapa de la primera hilada: si acabara en su
    # arranque, por las celdillas de esa hilada se veria el vacio.
    grupos.append(("tambor", *_tambor(planta, radio_base, -6.0, 2 * hiladas[0].paso)))
    return hiladas, grupos
