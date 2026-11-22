"""Boca escalonada, marco y nicho de los vanos del tambor (decisión 0043).

Contorno medido en `datos/remate_nichos.json` (`scripts/medir_remate_fotos.py`):
lecturas en Granada_trip82.jpg, cara B, retroproyectadas al plano del muro con
la cámara de 0041, y contrastadas con la vista frontal de la sección
AA-415_23 (diferencias de 0 a 3 cm). De dentro afuera, para cada lado del eje:
merlón, hombro, entrante, pináculo y esquina; cada tramo con su límite
exterior |s| y su cota (z = 0 en el arranque). El marco es una banda de
BANDA entre el contorno exterior y la boca (semiancho de la boca medido
0,404 m, del marco 0,464 m).

El remate se trata como plano: la vista frontal de la sección da las mismas
cotas que la retroproyección al plano del muro, lo que no deja sitio a un
vuelo apreciable. El pinjante que remata el merlón en las fotos no se
modela. La celosía tiene arco propio al fondo del nicho; su semiancho es el
de 0041 y su ápice se limita para que quepa bajo la boca.

Cada anillo del marco y del nicho se obtiene desplazando el contorno
exterior una distancia u hacia el hueco: los tramos bajan u y cada canto
vertical se mueve hacia el lado del tramo más bajo. Los tramos que se
quedan sin anchura (merlón y pináculo) se reducen a un diente de 4 mm para
conservar la topología. Los cantos verticales tienen 2·TAU de anchura para
que el contorno sea una función de s y pueda servir de junta.
"""

from math import cos, pi, sin

import numpy as np

try:
    from hiladas_ventanas import PROFUNDIDAD_NICHO_M
except ModuleNotFoundError:  # importado como paquete desde tests/
    from scripts.hiladas_ventanas import PROFUNDIDAD_NICHO_M

# (límite exterior |s| m, cota z m) de merlón, hombro, entrante, pináculo, esquina.
# datos/remate_nichos.json, perfil.*.s_ext y z_modelo (media de los vanos B1 y B2).
ESCALONES = ((0.0431, 0.1707), (0.1738, 0.0571), (0.2611, -0.1473), (0.3472, 0.031), (0.4642, -0.148))
SEMIANCHO_MARCO = ESCALONES[-1][0]
BANDA = 0.06  # 0,4642 - 0,4043 (semiancho del marco menos el de la boca)
TAU = 0.001
SEMIANCHO_CELOSIA = 0.29  # 0041, ajuste conjunto (h)
APICE_CELOSIA = -0.205  # cabe bajo la boca con 1 cm; [UNVERIFIED] medida directa
# Moldura del marco: (fracción de BANDA recorrida hacia el hueco, vuelo, tono).
# Perfil propuesto heredado del arco de 0035, escalado de 0,095 a BANDA.
MOLDURA = [
    (0.0, 0.0, "yeso"), (0.116, 0.027, "crema"), (0.189, 0.031, "yeso"),
    (0.274, 0.020, "yeso"), (0.347, 0.021, "ocre"), (0.432, 0.030, "yeso"),
    (0.684, 0.046, "crema"), (0.853, 0.055, "yeso"), (1.0, 0.052, "yeso"),
]
FONDO_BOCA = BANDA + 0.008


def cantos(u, tope=None):
    """Cotas de los tramos y posición |s| de sus cantos para el anillo u."""
    zs = [z if tope is None else min(z, tope) for _, z in ESCALONES]
    c = [s - u if zs[i] > zs[i + 1] else s + u for i, (s, _) in enumerate(ESCALONES[:-1])]
    c.append(SEMIANCHO_MARCO - u)
    minimo = 2 * TAU + 0.002
    colapsados = set()
    if c[0] < TAU + 0.001:
        c[0] = TAU + 0.001
        colapsados.add(0)
    for i in range(1, len(c)):
        if c[i] - c[i - 1] < minimo:
            medio = (c[i] + c[i - 1]) / 2
            c[i - 1], c[i] = medio - minimo / 2, medio + minimo / 2
            colapsados.add(i)
    if any(b - a < 2 * TAU for a, b in zip(c, c[1:])):
        raise ValueError(f"Contorno escalonado degenerado para u={u}")
    # Un tramo sin anchura baja a la cota del vecino más alto: diente plano.
    for i in sorted(colapsados):
        vecinos = [zs[j] for j in (i - 1, i + 1) if 0 <= j < len(zs) and j not in colapsados]
        if vecinos:
            zs[i] = min(zs[i], max(vecinos))
    return c, [z - u for z in zs]


def nudos(u, tope=None):
    """Tope del contorno de la jamba derecha a la izquierda: (s relativo, z)."""
    c, z = cantos(u, tope)
    derecha = [(c[4], z[4])]
    for i in (3, 2, 1, 0):
        derecha += [(c[i] + TAU, z[i + 1]), (c[i] - TAU, z[i])]
    return derecha + [(-s, zz) for s, zz in reversed(derecha)]


def tope_exterior(s, tope=None):
    """Cota del contorno exterior (u = 0) en s relativo al eje, |s| <= SEMIANCHO_MARCO."""
    n = nudos(0.0, tope)[::-1]
    return float(np.interp(s, [p[0] for p in n], [p[1] for p in n]))


def contorno(cx, u, alf, tope=None, muestras=None):
    """Lazo [pie izq., pie der., tope de derecha a izquierda] del anillo u.

    `muestras`, en s relativo y dentro del marco, añade vértices al tope en
    las mismas posiciones paramétricas en todos los anillos: así el anillo
    exterior comparte vértices con las adarajas del paño 00.
    """
    base = nudos(0.0, tope)
    actual = nudos(u, tope)
    puntos = list(actual)
    if muestras is not None:
        sb = np.array([p[0] for p in base])  # decreciente
        puntos = []
        extra = sorted({round(float(s), 9) for s in muestras} | {round(p[0], 9) for p in base}, reverse=True)
        for s in extra:
            k = int(np.searchsorted(-sb, -s, side="right")) - 1
            k = min(max(k, 0), len(sb) - 2)
            t = 0.0 if sb[k] == sb[k + 1] else (sb[k] - s) / (sb[k] - sb[k + 1])
            t = min(max(t, 0.0), 1.0)
            (s0, z0), (s1, z1) = actual[k], actual[k + 1]
            puntos.append((s0 + t * (s1 - s0), z0 + t * (z1 - z0)))
    zb = alf - (BANDA - u)
    j = SEMIANCHO_MARCO - u
    return [(cx - j, zb), (cx + j, zb)] + [(cx + s, z) for s, z in puntos]


def arco_celosia(cx, alf):
    r = SEMIANCHO_CELOSIA
    arranque = APICE_CELOSIA - r
    pie = alf + 0.012
    return [(cx - r, pie), (cx + r, pie)] + [(cx + r * cos(a), arranque + r * sin(a)) for a in np.linspace(0, pi, 33)]


def construir_nicho(forma, xyz, cx, alf, traceria, tope=None, muestras=None, x_plano=None):
    """Marco con moldura, nicho escalonado, muro de fondo y celosía en arco.

    `xyz(s, z, vuelo)` pasa a coordenadas de mundo (vuelo > 0 hacia la sala).
    `traceria`: "celosia" (paño 00, `hiladas_ventanas.celosia`, necesita
    `x_plano` = apotema) o "nervios" (resto de paños).
    """
    from detalle_visita import caras_con_huecos

    P = PROFUNDIDAD_NICHO_M
    anillos = [(f * BANDA, vuelo, tono) for f, vuelo, tono in MOLDURA]
    anillos += [(FONDO_BOCA, -(P - 0.03), "crema"), (FONDO_BOCA, -P, "yeso")]
    previo = None
    for u, vuelo, tono in anillos:
        lazo = contorno(cx, u, alf, tope, muestras)
        ids = forma.puntos(xyz(s, z, vuelo) for s, z in lazo)
        if previo is not None:
            forma.banda(previo, ids, tono)
        previo = ids
    fondo = contorno(cx, FONDO_BOCA, alf, tope, muestras)
    hueco = arco_celosia(cx, alf)
    ids_hueco = forma.puntos(xyz(s, z, -P) for s, z in hueco)
    todos = previo + ids_hueco
    for cara in caras_con_huecos(fondo, [hueco]):
        forma.cara([todos[i] for i in cara], "yeso")
    if traceria == "celosia":
        from hiladas_ventanas import celosia
        celosia(forma, x_plano + P, np.array(hueco), cx)
        posterior = forma.puntos(xyz(s, z, -(P + 0.08)) for s, z in hueco)
        forma.banda(ids_hueco, posterior, "yeso")
        for f in caras_con_huecos(hueco, []):
            forma.cara([posterior[i] for i in f], "cielo")
        return
    tras = forma.puntos(xyz(s, z, -(P + 0.07)) for s, z in hueco)
    forma.banda(ids_hueco, tras, "yeso")
    # Nervios diagonales de sección romboidal, recortados contra el arco
    # (convexo), justo detrás del plano del fondo.
    lazo = np.array(hueco)
    lazo[:2, 1] += 0.001
    lazo[:, 0] = cx + (lazo[:, 0] - cx) * 0.996
    for sentido in (-1, 1):
        for nivel in np.arange(alf - SEMIANCHO_CELOSIA, APICE_CELOSIA + SEMIANCHO_CELOSIA, 0.086):
            alturas = lazo[:, 1] - sentido * (lazo[:, 0] - cx) - nivel
            cruces = []
            for i, j in zip(range(-1, len(lazo) - 1), range(len(lazo))):
                if (alturas[i] > 0) != (alturas[j] > 0):
                    cruces.append(lazo[i] + (lazo[j] - lazo[i]) * alturas[i] / (alturas[i] - alturas[j]))
            if len(cruces) != 2:
                continue
            tramo = []
            for x, z in cruces:
                tramo.append(forma.puntos(
                    xyz(x + dx, z - sentido * dx, -(P + 0.02) + prof)
                    for dx, prof in [(-0.005, 0), (0, 0.008), (0.005, 0), (0, -0.008)]
                ))
            forma.banda(*tramo, "crema")
    forma.cara(tras, "cielo")
