"""Piezas a lo largo de las curvas de nivel del campo (decision 0017, paso 3).

Cada curva de nivel cerrada de `granada.campo` a la cota z_j es el **frente**
de una hilada. Se reproduce la colocacion del modelo de anillos
(`granada.cupula.en_contorno` y `plan_de_hiladas`), generalizada a una curva
cualquiera:

- x local (a lo ancho) pasa a longitud de arco sobre la curva;
- y local (hacia el frente; la pieza queda en y <= 0) pasa a un desplazamiento
  hacia fuera, en la direccion de bajada del campo, -grad H / |grad H|. La
  profundidad local de la hilada es la distancia hasta la curva de la cota
  anterior, PASO_VERTICAL / |grad H|; la pieza se estira para llenarla. Con
  A = 0 sale PASO_VERTICAL / PENDIENTE, el paso horizontal medido, que es el
  fondo de la familia A: el modelo de anillos;
- z: la pieza cuelga con la pata una hilada por debajo de su frente,
  cota = z_j - PASO_VERTICAL, como en el modelo de anillos.

Se desplaza por el gradiente y no por la normal de la polilinea porque el
campo es mas suave que su curva: en las esquinas de la estrella la normal
salta y el gradiente no tanto. Aun asi, en las esquinas concavas las piezas
vecinas se solapan o se separan: es el riesgo declarado del paso 3.

Con filas_por_hilada=2 (opcion B, decision 0018), se dividen por dos altura
y fondo de la pieza, conservando su ancho tangencial. Cada par de filas
conserva la familia de la hilada original. El campo no cambia; las nuevas
cotas son supuestas. No se reduce el ancho: eso duplicaria tambien el numero
de piezas por fila, y no corresponde a dividir cada hilada en dos filas.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import map_coordinates

from granada.campo import PASO_VERTICAL, Campo, cotas_de_hilada, curvas, es_cerrada
from granada.cupula import FAMILIAS, SECUENCIA, Hilada
from granada.piezas import etiquetas, malla, oclusion, pieza

PROFUNDIDAD_RELATIVA = (0.35, 1.6)
"""Limites de la profundidad local respecto al fondo de la familia. Donde el
campo es casi plano (|grad H| -> 0) la profundidad se dispararia; se recorta.
Eleccion."""


@dataclass(frozen=True)
class Frente:
    """Curva cerrada que hace de frente de una hilada."""

    indice: int
    """Fila j, a cota j * paso; no equivale necesariamente a hilada medida."""
    puntos: np.ndarray
    """Polilinea cerrada (n x 2), el ultimo punto repite el primero."""
    s: np.ndarray
    """Longitud acumulada en cada punto."""
    filas_por_hilada: int = 1
    """Subdivisiones elegidas de la hilada de referencia; 2 es la opcion B."""

    @property
    def escala(self) -> float:
        return 1 / self.filas_por_hilada

    @property
    def paso(self) -> float:
        return PASO_VERTICAL * self.escala

    @property
    def largo(self) -> float:
        return float(self.s[-1])

    @property
    def cota(self) -> float:
        """Cota de la pata: una hilada por debajo del frente."""
        return (self.indice - 1) * self.paso


def frente(indice: int, P: np.ndarray, filas_por_hilada: int = 1) -> Frente:
    if type(filas_por_hilada) is not int or filas_por_hilada < 1:
        raise ValueError("filas_por_hilada debe ser un entero positivo")
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
    return Frente(indice, P, s, filas_por_hilada)


PIEZAS_MINIMAS = 6
"""Un lazo con menos piezas no se monta: las piezas se deforman en pegotes
(comprobado el 2026-11-08). Se cerrara con una cupulilla (paso 4)."""


def frentes(c: Campo, minimo: int = PIEZAS_MINIMAS, filas_por_hilada: int = 1) -> list[Frente]:
    """Frentes cerrados del campo con sitio para `minimo` piezas, de abajo arriba."""
    fuera = []
    for j, z in enumerate(cotas_de_hilada(filas_por_hilada=filas_por_hilada), start=1):
        for P in curvas(c, z):
            if es_cerrada(P):
                f = frente(j, P, filas_por_hilada)
                if hilada_de(f).piezas >= minimo:
                    fuera.append(f)
    return fuera


def _gradiente(c: Campo):
    gy, gx = np.gradient(c.H, c.paso)

    def en(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        col = (x - c.x[0]) / c.paso
        fil = (y - c.y[0]) / c.paso
        return (map_coordinates(gx, [fil, col], order=1, mode="nearest"),
                map_coordinates(gy, [fil, col], order=1, mode="nearest"))

    return en


def colocar(V, f: Frente, gradiente, inicio: float, estiramiento: float, fondo: float):
    """Del marco local de la pieza al frente `f` (ver el docstring del modulo)."""
    P = np.asarray(V, dtype=float)
    s = np.mod(inicio + P[:, 0] * estiramiento, f.largo)
    x = np.interp(s, f.s, f.puntos[:, 0])
    y = np.interp(s, f.s, f.puntos[:, 1])
    gx, gy = gradiente(x, y)
    norma = np.maximum(np.hypot(gx, gy), 1e-9)
    profundidad = np.clip(f.paso / norma, PROFUNDIDAD_RELATIVA[0] * fondo, PROFUNDIDAD_RELATIVA[1] * fondo)
    t = -P[:, 1] / fondo * profundidad
    X = x - gx / norma * t
    Y = y - gy / norma * t
    return list(zip(X.tolist(), Y.tolist(), (P[:, 2] + f.cota).tolist()))


COLOCACIONES = ("rayo", "flujo", "rigida", "suavizada")
"""rayo: desplazamiento recto por el gradiente local (colocar). flujo: lineas
de maxima pendiente hasta la cota anterior (decision 0024, ensayo). rigida:
cada pieza entera sobre un lado del poligono inscrito (decision 0025).
suavizada: frente suavizado a escala de pieza, fondo recto hasta la curva
anterior suavizada (decision 0026)."""

CAPAS_FLUJO = 16
"""Niveles intermedios de H entre el frente y la cota anterior."""

SUBPASOS_FLUJO = 4
"""Pasos RK4 entre dos niveles consecutivos."""


def interpolador_suave(c: Campo):
    """Spline cubico de H sobre la rejilla: gradiente continuo.

    La bilineal tiene valles sobre las aristas de celda donde el descenso se
    atasca (decision 0023). Devuelve H(x, y) y grad H(x, y), vectorizados.
    """
    from scipy.interpolate import RectBivariateSpline
    s = RectBivariateSpline(c.y, c.x, c.H, kx=3, ky=3, s=0)

    def H(x, y):
        return s.ev(y, x)

    def grad(x, y):
        return s.ev(y, x, dy=1), s.ev(y, x, dx=1)

    return H, grad


@dataclass(frozen=True)
class Banda:
    """Tabla (s, q) -> (x, y) de un frente: q=0 en el frente, q=1 en la cota anterior."""

    s: np.ndarray
    q: np.ndarray
    xy: np.ndarray
    """(len(q), len(s), 2); la columna s=largo repite s=0."""
    error_cota: np.ndarray
    """H(fondo) - cota anterior, por muestra s."""


def banda_de_flujo(c: Campo, f: Frente, interpolador=None, ds: float | None = None,
                   capas: int = CAPAS_FLUJO, subpasos: int = SUBPASOS_FLUJO) -> Banda:
    """Sigue -grad H desde el frente bajando H de nivel en nivel.

    Parametro de integracion: la caida de H, dX/dh = -grad/|grad|^2, con RK4.
    Tras cada nivel, un paso de Newton a lo largo del gradiente vuelve a
    poner el punto en su nivel. El paso espacial se limita a una celda, para
    no saltar donde |grad| es casi cero; si eso deja el punto lejos de su
    nivel queda reflejado en error_cota.
    """
    H, grad = interpolador_suave(c) if interpolador is None else interpolador
    ds = c.paso if ds is None else ds
    n = max(32, int(np.ceil(f.largo / ds)))
    s = np.linspace(0, f.largo, n + 1)
    x = np.interp(s[:-1], f.s, f.puntos[:, 0])
    y = np.interp(s[:-1], f.s, f.puntos[:, 1])
    q = np.linspace(0, 1, capas + 1)
    z0 = f.indice * f.paso
    capas_xy = [np.column_stack([x, y])]
    p = capas_xy[0].copy()
    dh = f.paso / capas / subpasos
    tope = c.paso

    def v(p):
        gx, gy = grad(p[:, 0], p[:, 1])
        g = np.column_stack([gx, gy])
        n2 = np.maximum(np.sum(g * g, axis=1), 1e-18)
        w = -g / n2[:, None] * dh
        largo = np.linalg.norm(w, axis=1)
        return w * np.minimum(1, tope / np.maximum(largo, 1e-30))[:, None]

    for k in range(1, capas + 1):
        for _ in range(subpasos):
            k1 = v(p)
            k2 = v(p + k1 / 2)
            k3 = v(p + k2 / 2)
            k4 = v(p + k3)
            p = p + (k1 + 2 * k2 + 2 * k3 + k4) / 6
        nivel = z0 - q[k] * f.paso
        for _ in range(2):
            gx, gy = grad(p[:, 0], p[:, 1])
            n2 = np.maximum(gx * gx + gy * gy, 1e-18)
            e = H(p[:, 0], p[:, 1]) - nivel
            paso = np.clip(e / n2, -tope / np.sqrt(n2), tope / np.sqrt(n2))
            p = p - np.column_stack([gx, gy]) * paso[:, None]
        capas_xy.append(p.copy())
    xy = np.stack(capas_xy)
    xy = np.concatenate([xy, xy[:, :1]], axis=1)
    error = H(xy[-1, :-1, 0], xy[-1, :-1, 1]) - f.cota
    return Banda(s, q, xy, error)


def colocar_en_banda(V, f: Frente, b: Banda, inicio: float, estiramiento: float, fondo: float):
    """Como colocar(), pero (s, profundidad) se lee en la banda de flujo."""
    P = np.asarray(V, dtype=float)
    s = np.mod(inicio + P[:, 0] * estiramiento, f.largo)
    q = np.clip(-P[:, 1] / fondo, 0, 1)
    u = s / f.largo * (len(b.s) - 1)
    i = np.minimum(np.floor(u).astype(int), len(b.s) - 2)
    t = (u - i)[:, None]
    w = q * (len(b.q) - 1)
    j = np.minimum(np.floor(w).astype(int), len(b.q) - 2)
    r = (w - j)[:, None]
    xy = ((1 - r) * ((1 - t) * b.xy[j, i] + t * b.xy[j, i + 1])
          + r * ((1 - t) * b.xy[j + 1, i] + t * b.xy[j + 1, i + 1]))
    return list(zip(xy[:, 0].tolist(), xy[:, 1].tolist(), (P[:, 2] + f.cota).tolist()))


@dataclass(frozen=True)
class Poligono:
    """Un lado por pieza: centro, tangente, normal hacia abajo y fondo."""

    vertices: np.ndarray
    """(n+1, 2), sobre el frente; el ultimo repite el primero."""
    centros: np.ndarray
    tangentes: np.ndarray
    normales: np.ndarray
    fondos: np.ndarray
    """Distancia por la normal hasta la cota anterior, ya recortada."""
    fondo_libre: np.ndarray
    """La misma distancia sin recortar; nan si la normal no cruza la cota."""


def poligono_de(c: Campo, f: Frente, interpolador=None) -> Poligono:
    """Poligono inscrito con un lado por pieza y fondo rigido de cada lado.

    Vertices en s_i - L/2, con s_i = i*L el centro de la pieza i de montar().
    La normal apunta hacia donde baja H. El fondo se busca por biseccion
    sobre el spline a lo largo de la normal, hasta 3 fondos nominales; se
    recorta a PROFUNDIDAD_RELATIVA como en rayo.
    """
    H, grad = interpolador_suave(c) if interpolador is None else interpolador
    h = hilada_de(f)
    fam = FAMILIAS[h.familia]
    L = fam.paso_tangencial * h.estiramiento
    fondo = fam.fondo * f.escala
    s = np.mod(np.arange(h.piezas + 1) * L - L / 2, f.largo)
    V = np.column_stack([np.interp(s, f.s, f.puntos[:, 0]), np.interp(s, f.s, f.puntos[:, 1])])
    V[-1] = V[0]
    C = (V[:-1] + V[1:]) / 2
    T = V[1:] - V[:-1]
    T = T / np.maximum(np.linalg.norm(T, axis=1), 1e-12)[:, None]
    N = np.column_stack([T[:, 1], -T[:, 0]])
    gx, gy = grad(C[:, 0], C[:, 1])
    N = N * np.where(N[:, 0] * gx + N[:, 1] * gy > 0, -1.0, 1.0)[:, None]
    tope = 3 * fondo
    lo, hi = np.zeros(len(C)), np.full(len(C), tope)
    cruza = H(*(C + N * tope).T) <= f.cota
    for _ in range(50):
        m = (lo + hi) / 2
        bajo = H(*(C + N * m[:, None]).T) <= f.cota
        hi = np.where(bajo, m, hi)
        lo = np.where(bajo, lo, m)
    libre = np.where(cruza, hi, np.nan)
    fondos = np.clip(np.where(cruza, hi, tope), PROFUNDIDAD_RELATIVA[0] * fondo,
                     PROFUNDIDAD_RELATIVA[1] * fondo)
    return Poligono(V, C, T, N, fondos, libre)


def colocar_rigida(V, f: Frente, pg: Poligono, i: int, estiramiento: float, fondo: float):
    """La pieza i, sin doblar: x por la tangente de su lado, y por la normal."""
    P = np.asarray(V, dtype=float)
    xy = (pg.centros[i] + np.outer(P[:, 0] * estiramiento, pg.tangentes[i])
          + np.outer(-P[:, 1] / fondo * pg.fondos[i], pg.normales[i]))
    return list(zip(xy[:, 0].tolist(), xy[:, 1].tolist(), (P[:, 2] + f.cota).tolist()))


SIGMA_FRENTE = 1.0
"""Escala (catetos de arco) del suavizado de frentes en la colocacion
'suavizada' (decision 0026). Unico valor del barrido que cumple el criterio previo."""


def suavizar_curva(P: np.ndarray, sigma: float, ds: float = 0.03) -> np.ndarray:
    """Gaussiana a lo largo del arco, compensada; periodica si la curva es cerrada."""
    from scipy.ndimage import gaussian_filter1d
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
    cerrada = es_cerrada(P)
    n = max(8, int(np.ceil(s[-1] / ds)))
    t = np.linspace(0, s[-1], n + 1)
    Q = np.column_stack([np.interp(t, s, P[:, 0]), np.interp(t, s, P[:, 1])])
    if sigma <= 0:
        return Q
    # G Q encoge una curva ~sigma^2 kappa / 2. G Q + (G Q - G G Q) compensa
    # ese termino (queda O(sigma^4)) y sigue atenuando las ondas cortas.
    modo = "wrap" if cerrada else "nearest"
    base = Q[:-1] if cerrada else Q
    G = gaussian_filter1d(base, sigma / (s[-1] / n), axis=0, mode=modo)
    Q = 2 * G - gaussian_filter1d(G, sigma / (s[-1] / n), axis=0, mode=modo)
    return np.vstack([Q, Q[:1]]) if cerrada else Q


def frente_suavizado(f: Frente, sigma: float = SIGMA_FRENTE) -> Frente:
    return frente(f.indice, suavizar_curva(f.puntos, sigma), f.filas_por_hilada)


def _primer_corte(p, n, segmentos, tope):
    """Distancia por el rayo p + t n (t en (0, tope]) al primer segmento; nan si no hay."""
    t_min = np.full(len(p), np.nan)
    if not len(segmentos):
        return t_min
    A, B = segmentos[:, 0], segmentos[:, 1]
    E = B - A
    for k in range(0, len(p), 256):
        pp, nn = p[k:k+256, None, :], n[k:k+256, None, :]
        den = nn[..., 0] * E[None, :, 1] - nn[..., 1] * E[None, :, 0]
        w = A[None] - pp
        with np.errstate(divide="ignore", invalid="ignore"):
            t = (w[..., 0] * E[None, :, 1] - w[..., 1] * E[None, :, 0]) / den
            u = (w[..., 0] * nn[..., 1] - w[..., 1] * nn[..., 0]) / den
        ok = (np.abs(den) > 1e-14) & (t > 1e-9) & (t <= tope) & (u >= 0) & (u <= 1)
        t = np.where(ok, t, np.inf).min(axis=1)
        t_min[k:k+256] = np.where(np.isfinite(t), t, np.nan)
    return t_min


def banda_suavizada(c: Campo, f: Frente, sigma: float = SIGMA_FRENTE, grad=None,
                    ds: float | None = None, capas: int = CAPAS_FLUJO) -> Banda:
    """Banda recta entre un frente ya suavizado y la curva anterior suavizada.

    Normal del frente suavizado, con un unico sentido por frente: el que
    baja H en la mayoria de las muestras. Fondo = primer corte con las
    curvas de la cota anterior (suavizadas con el mismo sigma) hasta tres
    fondos; sin corte, el de rayo. Despues se recorta a PROFUNDIDAD_RELATIVA.
    error_cota lleva aqui el fondo libre en fondos nominales (nan sin corte).
    """
    grad = _gradiente(c) if grad is None else grad
    h = hilada_de(f)
    fondo = FAMILIAS[h.familia].fondo * f.escala
    ds = c.paso if ds is None else ds
    n = max(32, int(np.ceil(f.largo / ds)))
    s = np.linspace(0, f.largo, n + 1)
    P = np.column_stack([np.interp(s[:-1], f.s, f.puntos[:, 0]), np.interp(s[:-1], f.s, f.puntos[:, 1])])
    T = np.roll(P, -1, axis=0) - np.roll(P, 1, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1), 1e-12)[:, None]
    N = np.column_stack([T[:, 1], -T[:, 0]])
    gx, gy = grad(P[:, 0], P[:, 1])
    if np.mean(N[:, 0] * gx + N[:, 1] * gy > 0) > 0.5:
        N = -N
    previas = [suavizar_curva(Q, sigma) for Q in curvas(c, f.cota)]
    segmentos = (np.concatenate([np.stack([Q[:-1], Q[1:]], axis=1) for Q in previas])
                 if previas else np.zeros((0, 2, 2)))
    libre = _primer_corte(P, N, segmentos, 3 * fondo)
    rayo = f.paso / np.maximum(np.hypot(gx, gy), 1e-9)
    d = np.clip(np.where(np.isnan(libre), rayo, libre),
                PROFUNDIDAD_RELATIVA[0] * fondo, PROFUNDIDAD_RELATIVA[1] * fondo)
    q = np.linspace(0, 1, capas + 1)
    xy = P[None] + q[:, None, None] * (d[:, None] * N)[None]
    xy = np.concatenate([xy, xy[:, :1]], axis=1)
    return Banda(s, q, xy, libre / fondo)


def hilada_de(f: Frente) -> Hilada:
    """Plan de la hilada: familia por la secuencia A, A, C del modelo de anillos
    y numero par de piezas para que alternen frente y vertice."""
    familia = SECUENCIA[((f.indice - 1) // f.filas_por_hilada) % len(SECUENCIA)]
    paso_t = FAMILIAS[familia].paso_tangencial
    n = max(2, 2 * round(f.largo / (2 * paso_t)))
    return Hilada(f.indice - 1, familia, float("nan"), f.cota, f.paso, n, f.largo / (n * paso_t))


def admitido_suavizado(f: Frente, sigma: float = SIGMA_FRENTE, minimo: int = PIEZAS_MINIMAS) -> bool:
    """El frente suavizado aun da sitio a `minimo` piezas.

    frentes() mide el lazo sobre la curva cruda; las piezas siguen la
    suavizada, que en lazos pequenos encoge mucho (el de la fila 24 en
    r = 8,7 pasa de 1,93 a 0,02 catetos y sus piezas salian de un punto).
    Un lazo que no pasa se deja al cierre (granada/cierres_campo.py).
    Decidido el 2026-11-18."""
    return hilada_de(frente_suavizado(f, sigma)).piezas >= minimo


def montar(c: Campo, seleccion: list[Frente] | None = None, subdivision: int = 6,
           filas_por_hilada: int = 1, colocacion: str = "suavizada", sigma: float = SIGMA_FRENTE,
           descartar=None):
    """Grupos (nombre, V, F, etiquetas, sombras), uno por frente.

    En la colocacion suavizada se saltan los frentes que no pasan
    admitido_suavizado. `descartar(vertices)` quita las piezas para las que
    devuelve True (el marco de los cupulines, como en granada.cupula)."""
    if colocacion not in COLOCACIONES:
        raise ValueError(f"colocacion debe ser una de {COLOCACIONES}")
    gradiente = _gradiente(c)
    suave = interpolador_suave(c) if colocacion in ("flujo", "rigida") else None
    plantillas: dict = {}
    grupos = []
    for k, f in enumerate(frentes(c, filas_por_hilada=filas_por_hilada) if seleccion is None else seleccion):
        if colocacion == "suavizada":
            f = frente_suavizado(f, sigma)
            if hilada_de(f).piezas < PIEZAS_MINIMAS:
                continue
        h = hilada_de(f)
        fam = FAMILIAS[h.familia]
        if colocacion == "suavizada":
            b = banda_suavizada(c, f, sigma, gradiente)

            def poner(Vp, inicio, est, fondo, f=f, b=b):
                return colocar_en_banda(Vp, f, b, inicio, est, fondo)
        elif colocacion == "flujo":
            b = banda_de_flujo(c, f, suave)

            def poner(Vp, inicio, est, fondo, f=f, b=b):
                return colocar_en_banda(Vp, f, b, inicio, est, fondo)
        elif colocacion == "rigida":
            pg = poligono_de(c, f, suave)
            paso_pieza = fam.paso_tangencial * h.estiramiento

            def poner(Vp, inicio, est, fondo, f=f, pg=pg, paso_pieza=paso_pieza):
                return colocar_rigida(Vp, f, pg, int(round(inicio / paso_pieza)), est, fondo)
        else:
            def poner(Vp, inicio, est, fondo, f=f):
                return colocar(Vp, f, gradiente, inicio, est, fondo)
        V, F, E, S = [], [], [], []
        for i, tipo in enumerate(h.tipos()):
            clave = (tipo, f.filas_por_hilada)
            if clave not in plantillas:
                pz = pieza(tipo, PASO_VERTICAL)
                Vm, Fm = malla(pz, subdivision)
                Em = etiquetas(pz, Vm, Fm)
                plantillas[clave] = (np.asarray(Vm) * (1, f.escala, f.escala), Fm, Em, oclusion(pz, Vm, Fm, Em))
            Vp, Fp, Ep, Sp = plantillas[clave]
            puesta = poner(Vp, i * fam.paso_tangencial * h.estiramiento, h.estiramiento, fam.fondo * f.escala)
            if descartar is not None and descartar(puesta):
                continue
            base = len(V)
            V.extend(puesta)
            F.extend((a + base, b + base, cc + base) for a, b, cc in Fp)
            E.extend(Ep)
            S.extend(Sp)
        grupos.append((f"frente_{f.indice:02d}_{k:03d}_{h.familia}", V, F, E, S))
    return grupos


def resumen(c: Campo, filas_por_hilada: int = 1) -> list[dict]:
    """Por frente: hilada, largo, piezas y si es anillo o lazo."""
    fuera = []
    for f in frentes(c, filas_por_hilada=filas_por_hilada):
        h = hilada_de(f)
        rodea = bool(_contiene_origen(f.puntos))
        fuera.append({"hilada": f.indice, "fila": f.indice,
                      "hilada_de_referencia": f.indice / f.filas_por_hilada,
                      "cota_frente_catetos": f.indice * f.paso,
                      "procedencia": "cota de modelo; subdividida" if f.filas_por_hilada > 1 else "cota de modelo; paso de referencia",
                      "largo": f.largo, "piezas": h.piezas, "familia": h.familia,
                      "anillo": rodea, "estiramiento": h.estiramiento})
    return fuera


def _contiene_origen(P: np.ndarray) -> bool:
    x, y = P[:, 0], P[:, 1]
    cruza = (y[:-1] > 0) != (y[1:] > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        xc = x[:-1] + (0 - y[:-1]) * (x[1:] - x[:-1]) / (y[1:] - y[:-1])
    return bool(np.sum(cruza & (xc > 0)) % 2)


def piezas_totales(c: Campo, filas_por_hilada: int = 1) -> int:
    return sum(r["piezas"] for r in resumen(c, filas_por_hilada))

