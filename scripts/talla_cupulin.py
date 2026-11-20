"""Frentes locales del cupulín 00. Los contornos se leen a mano en AA-415_23 p.1.
Las alturas intermedias y la talla son interpretación para la visita.
"""

from math import pi, sin
import bpy
import numpy as np
from encajar_frentes_visita import encajar


# Coordenadas sobre el recorte (3210,1440)-(3830,2060) de la ortoimagen,
# reducido a 520 px de lado en la lámina de lectura del piloto 0032.
# Cada cuadrilátero se enumera alrededor de la cara visible.
FRENTES = [
    ("verde", [(404, 235), (444, 231), (449, 298), (407, 302)]),
    ("liso", [(405, 304), (448, 303), (422, 332), (396, 323)]),
    ("tostado", [(313, 109), (372, 106), (372, 146), (309, 147)]),
    ("liso", [(313, 149), (371, 151), (343, 180), (294, 176)]),
    ("verde", [(95, 106), (142, 101), (147, 166), (100, 166)]),
    ("liso", [(103, 169), (147, 169), (148, 210), (105, 214)]),
    ("tostado", [(237, 15), (279, 9), (285, 73), (241, 77)]),
    ("crema", [(157, 95), (202, 49), (234, 70), (188, 126)]),
    ("tostado", [(319, 400), (384, 398), (388, 438), (323, 441)]),
    ("crema", [(72, 377), (109, 347), (157, 389), (120, 423)]),
    ("liso", [(116, 346), (137, 318), (156, 338), (152, 371)]),
    ("verde", [(63, 477), (102, 475), (106, 518), (64, 518)]),
]


def construir_frentes(forma, registro):
    grafo = bpy.context.evaluated_depsgraph_get()
    escena = bpy.context.scene
    contornos = []
    for tono, esquinas in FRENTES:
        pixeles = np.array([3210, 1440]) + np.asarray(esquinas) * (620 / 520)
        xy = (pixeles - registro["centro_px"]) * [1, -1] / registro["px_por_m_supuesto"]
        a, b, c, d = xy

        def planta(u, v):
            return (1 - v) * ((1 - u) * a + u * b) + v * ((1 - u) * d + u * c)

        # Asentar cada frente sobre la superficie existente. La altura del
        # frente sale del ajuste local; el canto vuelve al relieve de alrededor.
        muestras = []
        pozo = 0
        for u in np.linspace(0, 1, 7):
            for v in np.linspace(0, 1, 7):
                x, y = planta(u, v)
                toca, punto, _, _, objeto, _ = escena.ray_cast(
                    grafo, (x, y, -3), (0, 0, 1), distance=9
                )
                if toca and objeto.name == "cupulin_00":
                    pozo += 1
                if toca and (
                    objeto.name.startswith("hilada_")
                    or objeto.name.startswith("Adarajas")
                ):
                    muestras.append((u, v, punto.z))
        if pozo > 5 or len(muestras) < 12:
            continue
        muestras = np.array(muestras)
        uv = np.column_stack((muestras[:, :2] - 0.5, np.ones(len(muestras))))
        plano = np.linalg.lstsq(uv, muestras[:, 2], rcond=None)[0]
        plano[2] += np.median(muestras[:, 2] - uv @ plano)
        # Limitar el giro de una cara si las muestras caen en dos pisos distintos.
        for i, lado in enumerate((b - a, d - a)):
            plano[i] = np.clip(
                plano[i], -1.3 * np.linalg.norm(lado), 1.3 * np.linalg.norm(lado)
            )

        def punto(u, v, relieve):
            # Relieve positivo hacia el visitante.
            return (*planta(u, v), plano @ [u - 0.5, v - 0.5, 1.0] - relieve)

        # El muro devuelve el contorno al relieve de la hilada. Cada vano se
        # recorta en las piezas antiguas para que ningún canto atraviese la talla.
        perfil = []
        for inicio, fin in zip(
            [(0, 0), (1, 0), (1, 1), (0, 1)], [(1, 0), (1, 1), (0, 1), (0, 0)]
        ):
            for t in np.arange(16) / 16:
                u, v = (1 - t) * np.array(inicio) + t * np.array(fin)
                x, y, z = punto(u, v, 0)
                toca, hit, _, _, obj, _ = escena.ray_cast(
                    grafo, (x, y, -3), (0, 0, 1), distance=9
                )
                h = (
                    hit.z
                    if toca
                    and obj.name.startswith(("hilada_", "Adarajas", "cupulilla_"))
                    else z
                )
                perfil.append((u, v, h))
        previo = forma.puntos((*planta(u, v), h + 0.055) for u, v, h in perfil)
        for margen, mezcla, vuelo in [
            (0, 0, 0),
            (0.075, 0.45, 0.005),
            (0.14, 0.88, -0.008),
            (0.166, 1.0, -0.014),
            (0.177, 1.0, -0.011),
        ]:
            anillo = []
            for u, v, h in perfil:
                x, y, z = punto(
                    margen + (1 - 2 * margen) * u, margen + (1 - 2 * margen) * v, vuelo
                )
                anillo.append((x, y, h * (1 - mezcla) + mezcla * z))
            sig = forma.puntos(anillo)
            forma.banda(previo, sig, "yeso")
            previo = sig
        forma.cara(
            [previo[i] for i in (0, 16, 32, 48)], "yeso" if tono == "liso" else tono
        )
        if tono != "liso":
            tallar_ataurique(
                forma,
                lambda u, v, h: punto(0.177 + 0.646 * u, 0.177 + 0.646 * v, h - 0.011),
            )
        contornos.append(xy)
    if len(contornos) < 4:
        raise ValueError("Muy pocos apoyos para identificar la zona tallada")
    for obj in escena.objects:
        if (
            obj.name.startswith(("hilada_", "Adarajas", "cupulilla_"))
            and obj.name != "cupulilla_25"
        ):
            encajar(obj, contornos)
    return len(contornos)


def tallar_ataurique(forma, punto):
    """Dos tallos, hojas en pares y una palmeta axial en bajorrelieve.
    Las nervaduras y el bisel son geometría que proyecta sombra al girar.
    """

    def cinta(curva, ancho, alto):
        filas = []
        for t in np.linspace(0, 1, 19):
            p = np.asarray(curva(t))
            dp = np.subtract(curva(min(t + 0.001, 1)), curva(max(t - 0.001, 0)))
            normal = np.array([-dp[1], dp[0]]) / max(np.linalg.norm(dp), 1e-8)
            perfil = 0.025 + 0.975 * sin(t * pi) ** 0.67
            filas.append(
                forma.puntos(
                    punto(
                        *(p + normal * (s * ancho * perfil)), 0.0004 + h * alto * perfil
                    )
                    for s, h in [(-1, 0), (-0.55, 0.68), (0, 1), (0.55, 0.48), (1, 0)]
                )
            )
        for a, b in zip(filas, filas[1:]):
            for i in range(4):
                forma.cara((a[i], a[i + 1], b[i + 1], b[i]), "crema")

    cinta(lambda t: (0.5 + 0.013 * sin(2 * pi * t), 0.13 + 0.75 * t), 0.025, 0.005)
    for lado in (-1, 1):
        for altura in (0.17, 0.46):
            # Hojas hendidas de un tallo que se abre y vuelve hacia el eje.
            cinta(
                lambda t: (0.5 + lado * (0.27 * sin(0.81 * pi * t)), altura + 0.31 * t),
                0.043,
                0.006,
            )
            cinta(
                lambda t: (
                    0.5 + lado * (0.12 + 0.16 * sin(0.89 * pi * t)),
                    altura + 0.085 + 0.17 * t,
                ),
                0.046,
                0.0045,
            )
            cinta(
                lambda t: (
                    0.5 + lado * (0.04 + 0.12 * sin(0.63 * pi * t)),
                    altura + 0.075 + 0.23 * t,
                ),
                0.045,
                0.005,
            )
        cinta(
            lambda t: (
                0.5 + lado * (0.14 * (1 - t) + 0.03 * sin(pi * t)),
                0.68 + 0.17 * t,
            ),
            0.040,
            0.005,
        )


def medir_boca(centro, suelo):
    """Primer impacto en una ventana de 1,10 m centrada en el cupulín."""
    grafo = bpy.context.evaluated_depsgraph_get()
    conteos = {}
    for nombre, origen in [
        ("sala", np.array([0.0, -0.8, suelo + 1.6])),
        ("oblicua", centro + [-0.9, 1.05, -1.55]),
    ]:
        direccion = centro - origen
        direccion /= np.linalg.norm(direccion)
        u = np.cross([0, 1, 0], direccion)
        u /= np.linalg.norm(u)
        v = np.cross(direccion, u)
        visibles = 0
        for dx in np.linspace(-0.55, 0.55, 65):
            for dy in np.linspace(-0.55, 0.55, 65):
                destino = centro + dx * u + dy * v
                toca, _, _, _, obj, _ = bpy.context.scene.ray_cast(
                    grafo, origen, destino - origen
                )
                visibles += bool(toca and obj.name == "cupulin_00")
        conteos[nombre] = visibles
    return conteos
