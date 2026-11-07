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
- la cupulilla de cierre y el tambor son superficies de relleno; el tambor
  lleva un friso azul entre filetes de oro (`FRISO_TAMBOR`), por estetica;
- **los 16 cupulines**: posicion y diametro medidos en la ortoimagen
  (`datos/cupulines.json`, `scripts/medir_cupulines.py`, con escala supuesta).
  Cada cupulin tiene el eje vertical (`EJE_CUPULIN_GRADOS`; hasta 2026-11-06,
  normal al cono, 52 grados: eleccion, no medida). Se quitan las piezas de la trama cuyo
  centroide cae en su cilindro, se pone un pocillo poco profundo que tapa el
  corte y encima una cupula pequena con piezas a escala 0,4. Un marco de yeso
  (`MARCO_CUPULIN`) tapa el borde del corte; la boca es un octogono con pico
  hacia el centro (`PICO_CUPULIN`). Su interior no esta leido; la forma real es una cupulita de
  mocarabes que aqui solo se imita.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from granada.piezas import C22, R2, S22, Punto3, etiquetas, malla, oclusion, pieza

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


FRISO_TAMBOR = (
    # (cota inferior, cota superior, color, luz) en unidades del cateto,
    # con 0 en el arranque de la cupula. Eleccion estetica.
    (-6.0, -1.5, "yeso", 0.95),
    (-1.5, -1.35, "oro", 1.0),
    (-1.35, -0.45, "azul", 0.9),
    (-0.45, -0.3, "oro", 1.0),
    (-0.3, None, "yeso", 0.95),
)


def _tambor_friso(planta: Planta, radio: float, arriba: float, n: int = 384):
    """Tambor en bandas horizontales: zocalo, filetes de oro y friso."""
    V: list[Punto3] = []
    F = []
    C: list[str] = []
    S: list[float] = []
    for z0, z1, color, luz in FRISO_TAMBOR:
        Vb, Fb = _tambor(planta, radio, z0, arriba if z1 is None else z1, n)
        b = len(V)
        V.extend(Vb)
        F.extend((p + b, q + b, r + b) for p, q, r in Fb)
        C.extend([color] * len(Fb))
        S.extend([luz] * len(Fb))
    return V, F, C, S


def _corona(radio_in: float, radio_out: float, z: float, n: int = 64):
    """Corona plana en el plano z del marco local."""
    V: list[Punto3] = []
    F = []
    for i in range(n):
        a = 2 * math.pi * i / n
        V.append((radio_in * math.cos(a), radio_in * math.sin(a), z))
        V.append((radio_out * math.cos(a), radio_out * math.sin(a), z))
    for i in range(n):
        a, b = 2 * i, 2 * ((i + 1) % n)
        F.append((a, b, b + 1))
        F.append((a, b + 1, a + 1))
    return V, F


MARCO_CUPULIN = 1.18
"""Radio exterior del marco de yeso de cada cupulin, respecto al hueco. Era 1,45;
bajado el 2026-11-07 porque en la ortoimagen el marco es una moldura fina."""
PICO_CUPULIN = 1.55
"""Largo del pico de la boca, respecto al radio del octogono. En la
ortoimagen la boca de cada cupulin es un octogono con un vertice estirado en
pico hacia el centro de la cupula, como una gota (lo mismo en el render
Ferrer_3, sin asignar). Medida a ojo sobre la ortoimagen: eleccion."""
EJE_CUPULIN_GRADOS = 0.0
"""Inclinacion del eje de cada cupulin desde la vertical. Hasta el 2026-11-06
era la normal al cono (52 grados), eleccion no medida: desde abajo el pozo
ensenaba su pared y la cupulita apenas asomaba. En la ortoimagen las bocas se
ven redondas, y con 52 grados se verian como elipses de razon cos 52 = 0,62:
eso apunta a un eje casi vertical. Sigue siendo eleccion, no medida."""


MUESTRAS_POLIGONO = 720


def radios_desde(P: np.ndarray, c: np.ndarray, n: int = MUESTRAS_POLIGONO) -> np.ndarray:
    """r(phi) del contorno P visto desde c, en n angulos (P estrellado en c)."""
    phi = np.linspace(0, 2 * math.pi, n, endpoint=False)
    u = np.stack([np.cos(phi), np.sin(phi)], axis=1)
    A, B = P - c, np.roll(P, -1, axis=0) - c
    D = B - A
    r = np.full(n, np.inf)
    for a, dd in zip(A, D):
        den = u[:, 0] * dd[1] - u[:, 1] * dd[0]
        ok = np.abs(den) > 1e-12
        t = np.where(ok, (a[0] * dd[1] - a[1] * dd[0]) / np.where(ok, den, 1), np.inf)
        s = np.where(ok, (a[0] * u[:, 1] - a[1] * u[:, 0]) / np.where(ok, den, 1), -1)
        valido = ok & (t > 1e-9) & (s >= -1e-9) & (s <= 1 + 1e-9)
        r = np.where(valido & (t < r), t, r)
    return r


@dataclass(frozen=True)
class PlantaPoligono:
    """Contorno estrellado como r(phi) desde un punto de su nucleo.

    Misma interfaz que Planta (forma, punto, arco), con los contornos
    interiores homoteticos: r = F * rho(phi) / radio_base.
    """

    rho: tuple[float, ...]
    radio_base: float
    radio_cierre: float
    estrella: bool = False

    def forma(self, phi, F):
        phi = np.mod(np.asarray(phi, dtype=float), 2 * math.pi)
        tabla = np.asarray(self.rho)
        malla = np.linspace(0, 2 * math.pi, len(tabla), endpoint=False)
        return np.interp(phi, malla, tabla, period=2 * math.pi) / self.radio_base

    def punto(self, phi, F):
        r = np.asarray(F) * self.forma(phi, F)
        return r * np.cos(phi), r * np.sin(phi)

    def arco(self, F):
        phi = np.linspace(0, 2 * math.pi, MUESTRAS_POLIGONO + 1)
        x, y = self.punto(phi, np.full_like(phi, F))
        s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
        return s, phi, float(s[-1])


def _forma_cupulin() -> np.ndarray:
    """r(phi) de la boca, en radios del octogono: octogono con un vertice a 90
    grados (hacia el centro de la cupula en el marco del cupulin) estirado en pico."""
    a = np.radians(90 + 45 * np.arange(8))
    P = np.stack([np.cos(a), np.sin(a)], axis=1)
    P[0] *= PICO_CUPULIN
    return radios_desde(P, np.zeros(2))


FORMA_CUPULIN = _forma_cupulin()


def _contorno_cupulin(escala: float, n: int = 96) -> list[tuple[float, float]]:
    phi = np.linspace(0, 2 * math.pi, n, endpoint=False)
    r = escala * np.interp(phi, np.linspace(0, 2 * math.pi, len(FORMA_CUPULIN), endpoint=False), FORMA_CUPULIN,
                           period=2 * math.pi)
    return list(zip((r * np.cos(phi)).tolist(), (r * np.sin(phi)).tolist()))


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
        b = math.radians(EJE_CUPULIN_GRADOS)
        n = u * math.sin(b) + np.array([0.0, 0.0, 1.0]) * math.cos(b)
        e2 = np.cross(n, t)
        origen = np.array([self.x, self.y, cota_del_cono(self.x, self.y, radio_base)])
        return origen, t, e2, n

    def contiene(self, punto, radio_base: float = RADIO_BASE, radio: float | None = None) -> bool:
        """El punto cae dentro del prisma del cupulin (boca en gota), medido en
        su plano. `radio` escala la boca (por defecto, la del pocillo)."""
        o, e1, e2, n = self.marco(radio_base)
        d = np.asarray(punto, dtype=float) - o
        r = self.radio if radio is None else radio
        x, y = d @ e1, d @ e2
        phi = math.atan2(y, x) % (2 * math.pi)
        borde = r * float(np.interp(phi, np.linspace(0, 2 * math.pi, len(FORMA_CUPULIN), endpoint=False),
                                    FORMA_CUPULIN, period=2 * math.pi))
        return math.hypot(x, y) < borde and -4.0 < d @ n < 7.0


def detector_de_marcos(huecos, radio_base: float = RADIO_BASE, escala: float = MARCO_CUPULIN):
    """Funcion punto -> bool: cae en el marco de algun cupulin (con escala=1,
    en su boca). Precalcula los marcos, que `Cupulin.contiene` recalcula en
    cada llamada."""
    malla = np.linspace(0, 2 * math.pi, len(FORMA_CUPULIN), endpoint=False)
    marcos = [(*c.marco(radio_base), c.radio * escala) for c in huecos]

    def dentro(P) -> bool:
        P = np.asarray(P, dtype=float)
        for o, e1, e2, n, r in marcos:
            d = P - o
            dn = d @ n
            if not -4.0 < dn < 7.0:
                continue
            x, y = d @ e1, d @ e2
            if math.hypot(x, y) > r * PICO_CUPULIN:
                continue
            phi = math.atan2(y, x) % (2 * math.pi)
            if math.hypot(x, y) < r * float(np.interp(phi, malla, FORMA_CUPULIN, period=2 * math.pi)):
                return True
        return False

    return dentro


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


def _montar(planta: Planta, hiladas, subdivision: int, plantillas: dict, descartar=None, colorear=None):
    """Malla de cada hilada. `descartar(vertices)` quita las piezas para las
    que devuelve True; se devuelven tambien las cotas que ocupaban.
    Con `colorear(tipo, etiqueta, hilada, indice)` cada grupo lleva ademas el
    nombre de color y el factor de sombra de cada triangulo."""
    grupos = []
    quitadas: list[tuple[float, float, float, float]] = []
    for h in hiladas:
        V: list[Punto3] = []
        F = []
        C: list[str] = []
        S: list[float] = []
        paso_t = FAMILIAS[h.familia].paso_tangencial
        arco = planta.arco(h.radio_frente)
        for i, tipo in enumerate(h.tipos()):
            clave = (tipo, h.paso)
            if clave not in plantillas:
                pz = pieza(tipo, h.paso)
                Vm, Fm = malla(pz, subdivision)
                Em = etiquetas(pz, Vm, Fm)
                plantillas[clave] = (Vm, Fm, Em, oclusion(pz, Vm, Fm, Em))
            Vp, Fp, Ep, Sp = plantillas[clave]
            inicio = i * paso_t * h.estiramiento
            colocada = en_contorno(Vp, planta, h.radio_frente, arco, inicio, h.estiramiento, h.cota)
            if descartar is not None:
                cx = sum(v[0] for v in colocada) / len(colocada)
                cy = sum(v[1] for v in colocada) / len(colocada)
                cz = sum(v[2] for v in colocada) / len(colocada)
                if descartar(colocada):
                    quitadas.append((cx, cy, h.cota, h.cota + 2 * h.paso))
                    continue
            base = len(V)
            V.extend(colocada)
            F.extend((a + base, b + base, c + base) for a, b, c in Fp)
            if colorear is not None:
                C.extend(colorear(tipo, e, h.indice, i) for e in Ep)
                S.extend(Sp)
        nombre = f"hilada_{h.indice:02d}_{h.familia}"
        grupos.append((nombre, V, F, C, S) if colorear is not None else (nombre, V, F))
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


def _tubo_contorno(contorno, abajo, arriba: float):
    """Pocillo vertical sobre un contorno cerrado; `abajo(x, y)` da su borde inferior."""
    V: list[Punto3] = []
    F = []
    n = len(contorno)
    for x, y in contorno:
        V.extend([(x, y, abajo(x, y)), (x, y, arriba)])
    for i in range(n):
        a, b = 2 * i, 2 * ((i + 1) % n)
        F.append((a, b, b + 1))
        F.append((a, b + 1, a + 1))
    return V, F


def _corona_contorno(dentro, fuera, z):
    """Banda entre dos contornos cerrados con el mismo numero de puntos."""
    V: list[Punto3] = []
    F = []
    n = len(dentro)
    for (xi, yi), (xo, yo) in zip(dentro, fuera):
        V.extend([(xi, yi, z), (xo, yo, z)])
    for i in range(n):
        a, b = 2 * i, 2 * ((i + 1) % n)
        F.append((a, b, b + 1))
        F.append((a, b + 1, a + 1))
    return V, F


def cupulin(c: Cupulin, profundidad: float, subdivision: int = 5, plantillas=None, radio_base: float = RADIO_BASE, colorear=None):
    """Pocillo de `profundidad` con boca en gota (FORMA_CUPULIN) y, encima, una
    cupula pequena de piezas a escala `ESCALA_CUPULIN`, con la misma planta,
    cerrada con su cupulilla. Marco de yeso alrededor de la boca."""
    if plantillas is None:
        plantillas = {}
    e = ESCALA_CUPULIN
    base = c.radio / e
    rho = FORMA_CUPULIN * base
    planta = PlantaPoligono(tuple(rho.tolist()), float(rho.mean()), CIERRE_CUPULIN)
    hiladas = plan_de_hiladas(planta.radio_base, planta=planta, cierre=CIERRE_CUPULIN, multiplo=8)
    grupos, _ = _montar(planta, hiladas, subdivision, plantillas, colorear=colorear)
    if hiladas:
        u = hiladas[-1]
        Vc, Fc = _cupulilla(planta, u.radio_frente, u.cota, u.paso, n=48, m=8)
        # Yeso, no oro: en la ortoimagen el centro de los cupulines es gris
        # (cambio pedido el 2026-11-07).
        grupos.append(("cupulilla", Vc, Fc, ["yeso"] * len(Fc), [0.8] * len(Fc)))
    o, e1, e2, n = c.marco(radio_base)

    def superficie(x: float, y: float) -> float:
        """Cota local del cono bajo (x, y) del marco, medida a lo largo de n."""
        q = o + x * e1 + y * e2
        return (cota_del_cono(q[0], q[1], radio_base) - q[2]) / n[2]

    boca = _contorno_cupulin(c.radio)
    # La cupulita arranca por encima del punto mas alto de la boca: asi, vista
    # a lo largo del eje, se ve entera.
    fondo = max(superficie(x, y) for x, y in boca) + profundidad
    local: list[Punto3] = []
    F = []
    C: list[str] = []
    S: list[float] = []
    for g in grupos:
        _, Vg, Fg = g[:3]
        b = len(local)
        local.extend((e * x, e * y, fondo + e * z) for x, y, z in Vg)
        F.extend((p + b, q + b, r + b) for p, q, r in Fg)
        C.extend(g[3] if len(g) > 3 else ["yeso"] * len(Fg))
        S.extend(g[4] if len(g) > 4 else [1.0] * len(Fg))
    Vt, Ft = _tubo_contorno(boca, superficie, fondo + 2 * e * hiladas[0].paso)
    b = len(local)
    local.extend(Vt)
    F.extend((p + b, q + b, r + b) for p, q, r in Ft)
    C.extend(["yeso"] * len(Ft))
    S.extend([0.55] * len(Ft))
    # Marco de yeso con la forma de la boca, justo por debajo de las patas de
    # las piezas vecinas: tapa el corte de la trama. Sin filete de oro: en la
    # ortoimagen el marco es yeso (cambio del 2026-11-07).
    Vr, Fr = _corona_contorno(boca, _contorno_cupulin(c.radio * MARCO_CUPULIN), -0.03)
    b = len(local)
    local.extend((x, y, z + superficie(x, y)) for x, y, z in Vr)
    F.extend((p + b, q + b, r + b) for p, q, r in Fr)
    C.extend(["yeso"] * len(Fr))
    S.extend([0.95] * len(Fr))
    L = np.asarray(local)
    G = o + L[:, :1] * e1 + L[:, 1:2] * e2 + L[:, 2:3] * n
    V = [tuple(v) for v in G.tolist()]
    return (V, F, C, S) if colorear is not None else (V, F)


def cupula(
    subdivision: int = 8,
    radio_base: float = RADIO_BASE,
    estrella: bool = True,
    con_cupulines: bool = True,
    color: bool = False,
    reparto: str = "disperso",
):
    """Grupos (nombre, V, F): una por hilada, los cupulines, la cupulilla y el tambor.

    Con `color=True` cada grupo es (nombre, V, F, colores, sombras), con el
    reparto de `granada.color` (eleccion estetica, no dato): `"disperso"`, yeso
    con color suelto en celdillas, o `"anillos"`, el de 2026-11-05."""
    from granada.color import colorear, colorear_cupulin, colorear_cupulin_disperso, disperso

    planta = planta_por_defecto(radio_base, estrella)
    hiladas = plan_de_hiladas(radio_base, planta=planta)
    if reparto == "disperso":
        por_sector = {h.indice: len(h.tipos()) // 8 for h in hiladas}
        pintar, pintar_cupulin = disperso(por_sector), colorear_cupulin_disperso
    elif reparto == "anillos":
        pintar, pintar_cupulin = colorear, colorear_cupulin
    else:
        raise ValueError(f"reparto desconocido: {reparto!r}")
    if not color:
        pintar = pintar_cupulin = None
    plantillas: dict[tuple[str, float], tuple] = {}
    huecos = cupulines_medidos() if con_cupulines else []

    en_marco = detector_de_marcos(huecos, radio_base)

    def en_hueco(vertices) -> bool:
        # Fuera las piezas con el centroide sobre el marco, no solo sobre el
        # pocillo: si no, sus patas tapan el marco y el cupulin se ve a medio
        # hacer. Quitar toda pieza que lo toque deja huecos fuera del marco.
        return en_marco(np.asarray(vertices, dtype=float).mean(axis=0))

    grupos, quitadas = _montar(planta, hiladas, subdivision, plantillas, en_hueco if huecos else None, pintar)
    mini: dict = {}
    for k, c in enumerate(huecos):
        # El pocillo llega a la tapa de las piezas quitadas, medida a lo largo
        # de la normal; ahi arranca la cupula pequena.
        profundidad = 2 * hiladas[0].paso * math.cos(math.atan(PENDIENTE))
        grupos.append((f"cupulin_{k:02d}", *cupulin(c, profundidad, plantillas=mini, radio_base=radio_base, colorear=pintar_cupulin)))
    ultima = hiladas[-1]
    Vc, Fc = _cupulilla(planta, ultima.radio_frente, ultima.cota, ultima.paso)
    # El tambor sube hasta la tapa de la primera hilada: si acabara en su
    # arranque, por las celdillas de esa hilada se veria el vacio.
    Vt, Ft = _tambor(planta, radio_base, -6.0, 2 * hiladas[0].paso)
    if color:
        grupos.append(("cupulilla", Vc, Fc, ["oro"] * len(Fc), [0.95] * len(Fc)))
        grupos.append(("tambor", *_tambor_friso(planta, radio_base, 2 * hiladas[0].paso)))
    else:
        grupos.append(("cupulilla", Vc, Fc))
        grupos.append(("tambor", Vt, Ft))
    return hiladas, grupos
