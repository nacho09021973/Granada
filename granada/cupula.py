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
- la cupulilla de cierre y el tambor son superficies de relleno;
- **los 16 cupulines**: posicion y diametro medidos en la ortoimagen
  (`datos/cupulines.json`, `scripts/medir_cupulines.py`, con escala supuesta).
  Cada cupulin tiene el eje normal al cono (inclinado atan(1,28) = 52 grados
  de la vertical: eleccion, no medida). Se quitan las piezas de la trama cuyo
  centroide cae en su cilindro, se pone un pocillo poco profundo que tapa el
  corte y encima una cupula pequena con piezas a escala 0,4. Su interior no esta leido; la forma real es una cupulita de
  mocarabes que aqui solo se imita.
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


def plan_de_hiladas(
    radio_base: float = RADIO_BASE,
    secuencia=SECUENCIA,
    planta: Planta | None = None,
    cierre: float = RADIO_CIERRE,
    multiplo: int = 16,
) -> list[Hilada]:
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
        if radio < cierre:
            break
        exacto = planta.arco(radio)[2] / f.paso_tangencial
        n = max(multiplo, multiplo * round(exacto / multiplo))
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


@dataclass(frozen=True)
class Cupulin:
    """Una de las 16 cupulas pequenas del anillo exterior, en unidades del cateto."""

    x: float
    y: float
    radio: float

    def marco(self, radio_base: float = RADIO_BASE):
        """Origen sobre el cono y ejes (e1 tangente, e2, n normal al cono).

        El eje del cupulin es la normal a la superficie del cono, que apunta
        hacia arriba y hacia fuera: inclinada atan(PENDIENTE) desde la vertical.
        """
        d = math.hypot(self.x, self.y)
        u = np.array([self.x / d, self.y / d, 0.0])
        t = np.array([-u[1], u[0], 0.0])
        b = math.atan(PENDIENTE)
        n = u * math.sin(b) + np.array([0.0, 0.0, 1.0]) * math.cos(b)
        e2 = np.cross(n, t)
        origen = np.array([self.x, self.y, cota_del_cono(self.x, self.y, radio_base)])
        return origen, t, e2, n

    def contiene(self, punto, radio_base: float = RADIO_BASE) -> bool:
        """El punto cae dentro del cilindro del cupulin, medido en su plano."""
        o, e1, e2, n = self.marco(radio_base)
        d = np.asarray(punto, dtype=float) - o
        return math.hypot(d @ e1, d @ e2) < self.radio and -1.0 < d @ n < 4.0


CUPULINES = RAIZ / "datos" / "cupulines.json"
ESCALA_CUPULIN = 0.4
"""Tamano de las piezas de un cupulin respecto a las de la cupula. Eleccion:
con piezas de tamano normal no cabe ni una hilada en 0,55 m de diametro."""
CIERRE_CUPULIN = 1.2


def cupulines_medidos(ruta: Path = CUPULINES) -> list[Cupulin]:
    """Las 16 posiciones de `datos/cupulines.json` (scripts/medir_cupulines.py)."""
    r = json.loads(ruta.read_text(encoding="utf-8"))["resultado"]
    radio = r["radio_m"] / CATETO_M
    media = r["diametro_m"] / 2 / CATETO_M
    fuera = []
    for k in range(r["copias"]):
        a = math.radians(r["fase_grados"] + k * 360 / r["copias"])
        fuera.append(Cupulin(radio * math.cos(a), radio * math.sin(a), media))
    return fuera


def _montar(planta: Planta, hiladas, subdivision: int, plantillas: dict, descartar=None):
    """Malla de cada hilada. `descartar(cx, cy, cz)` quita las piezas cuyo
    centroide devuelve True; se devuelven tambien las cotas que ocupaban."""
    grupos = []
    quitadas: list[tuple[float, float, float, float]] = []
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
            colocada = en_contorno(Vp, planta, h.radio_frente, arco, inicio, h.estiramiento, h.cota)
            if descartar is not None:
                cx = sum(v[0] for v in colocada) / len(colocada)
                cy = sum(v[1] for v in colocada) / len(colocada)
                cz = sum(v[2] for v in colocada) / len(colocada)
                if descartar(cx, cy, cz):
                    quitadas.append((cx, cy, h.cota, h.cota + 2 * h.paso))
                    continue
            base = len(V)
            V.extend(colocada)
            F.extend((a + base, b + base, c + base) for a, b, c in Fp)
        grupos.append((f"hilada_{h.indice:02d}_{h.familia}", V, F))
    return grupos, quitadas


def cota_del_cono(x: float, y: float, radio_base: float = RADIO_BASE) -> float:
    """Arranque de las hiladas a la distancia del eje de (x, y), sobre el cono medido."""
    return max(0.0, (radio_base - math.hypot(x, y)) * PENDIENTE)


def _tubo(cx: float, cy: float, radio: float, abajo, arriba: float, n: int = 48):
    """Pocillo vertical; `abajo(x, y)` da la cota de su borde inferior."""
    V: list[Punto3] = []
    F = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = cx + radio * math.cos(a), cy + radio * math.sin(a)
        V.extend([(x, y, abajo(x, y)), (x, y, arriba)])
    for i in range(n):
        a, b = 2 * i, 2 * ((i + 1) % n)
        F.append((a, b, b + 1))
        F.append((a, b + 1, a + 1))
    return V, F


def cupulin(c: Cupulin, profundidad: float, subdivision: int = 5, plantillas=None, radio_base: float = RADIO_BASE):
    """Pocillo cilindrico de `profundidad` con eje normal al cono y, encima,
    una cupula pequena de piezas a escala `ESCALA_CUPULIN` con su cupulilla."""
    if plantillas is None:
        plantillas = {}
    e = ESCALA_CUPULIN
    base = c.radio / e
    planta = Planta(base, CIERRE_CUPULIN, False)
    hiladas = plan_de_hiladas(base, planta=planta, cierre=CIERRE_CUPULIN, multiplo=8)
    grupos, _ = _montar(planta, hiladas, subdivision, plantillas)
    if hiladas:
        u = hiladas[-1]
        grupos.append(("cupulilla", *_cupulilla(planta, u.radio_frente, u.cota, u.paso, n=48, m=8)))
    local: list[Punto3] = []
    F = []
    for _, Vg, Fg in grupos:
        b = len(local)
        local.extend((e * x, e * y, profundidad + e * z) for x, y, z in Vg)
        F.extend((p + b, q + b, r + b) for p, q, r in Fg)
    Vt, Ft = _tubo(0.0, 0.0, c.radio, lambda x, y: 0.0, profundidad + 2 * e * hiladas[0].paso)
    b = len(local)
    local.extend(Vt)
    F.extend((p + b, q + b, r + b) for p, q, r in Ft)
    o, e1, e2, n = c.marco(radio_base)
    L = np.asarray(local)
    G = o + L[:, :1] * e1 + L[:, 1:2] * e2 + L[:, 2:3] * n
    return [tuple(v) for v in G.tolist()], F


def cupula(
    subdivision: int = 8,
    radio_base: float = RADIO_BASE,
    estrella: bool = True,
    con_cupulines: bool = True,
):
    """Grupos (nombre, V, F): una por hilada, los cupulines, la cupulilla y el tambor."""
    planta = planta_por_defecto(radio_base, estrella)
    hiladas = plan_de_hiladas(radio_base, planta=planta)
    plantillas: dict[tuple[str, float], tuple] = {}
    huecos = cupulines_medidos() if con_cupulines else []

    def en_hueco(x: float, y: float, z: float) -> bool:
        return any(c.contiene((x, y, z), radio_base) for c in huecos)

    grupos, quitadas = _montar(planta, hiladas, subdivision, plantillas, en_hueco if huecos else None)
    mini: dict = {}
    for k, c in enumerate(huecos):
        # El pocillo llega a la tapa de las piezas quitadas, medida a lo largo
        # de la normal; ahi arranca la cupula pequena.
        profundidad = 2 * hiladas[0].paso * math.cos(math.atan(PENDIENTE))
        grupos.append((f"cupulin_{k:02d}", *cupulin(c, profundidad, plantillas=mini, radio_base=radio_base)))
    ultima = hiladas[-1]
    grupos.append(("cupulilla", *_cupulilla(planta, ultima.radio_frente, ultima.cota, ultima.paso)))
    # El tambor sube hasta la tapa de la primera hilada: si acabara en su
    # arranque, por las celdillas de esa hilada se veria el vacio.
    grupos.append(("tambor", *_tambor(planta, radio_base, -6.0, 2 * hiladas[0].paso)))
    return hiladas, grupos
