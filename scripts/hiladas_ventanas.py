"""Dos órdenes de adarajas en el paño +X que contiene el cupulín 00.

AA-415_23, p. 1. Lectura manual sobre el JPEG de la sección a su tamaño
original. Cada entrada indica el extremo derecho de la pieza, la abscisa del
eje del nicho y la fila de su cúspide. La división en piezas, los fondos y la
talla son interpretación. El encaje «seccion» conserva las cotas de la lectura
y apoya el fondo en el borde interior de la cornisa. «0036» reproduce el
encaje anterior, desplazado para conservar el ápice supuesto de 0035.
"""

from math import cos, pi, sin, sqrt, tan

import numpy as np

EJE_PX = 2555
# En los extremos se prolonga la pieza hasta la bisectriz del octógono.
INFERIOR = [
    (1868, 1820, 2128),
    (1964, 1918, 2112),
    (2053, 2010, 2173),
    (2112, 2083, 2138),
    (2188, 2140, 2146),
    (2380, 2284, 2050),
    (2477, 2434, 2141),
    (2552, 2519, 2172),
    (2649, 2618, 2136),
    (2730, 2682, 2137),
    (2918, 2823, 2047),
    (3010, 2975, 2140),
    (3093, 3050, 2170),
    (3166, 3128, 2138),
    (3245, 3203, 2114),
    (None, 3289, 2124),
]
SUPERIOR = [
    (1880, 1844, 2004),
    (1998, 1945, 1994),
    (2093, 2058, 2005),
    (2162, 2129, 1982),
    (2256, 2216, 2000),
    (2345, 2284, 1963),
    (2420, 2381, 2002),
    (2518, 2473, 1987),
    (2605, 2563, 1993),
    (2685, 2650, 2005),
    (2772, 2735, 1996),
    (2873, 2823, 1962),
    (2972, 2920, 1993),
    (3061, 3016, 2006),
    (3156, 3115, 1989),
    (3259, 3204, 1968),
    (None, 3284, 1998),
]
FONDO_M = (0.0, 0.134, 0.251)
# El eje de los vanos de 0035 está a ±0,59 m y su ápice a -0,165 m.
APICE_MODELO = -0.165
FILA_APICE = 2050


def tramos(tabla, semi, escala):
    segmentos = []
    a = -semi
    for extremo, eje, cresta in tabla:
        b = (extremo - EJE_PX) / escala if extremo is not None else semi
        c = (eje - EJE_PX) / escala
        if not a < c < b:
            raise ValueError("El paño no contiene la cúspide de una pieza")
        segmentos.append((a, c, b, cresta))
        a = b
    return segmentos


def arco_tramo(u, tramo):
    a, c, b, _ = tramo
    t = (u - a) / (c - a) if u <= c else (b - u) / (b - c)
    # La sección conserva un macizo entre los nichos y hombros redondeados.
    # El resalte apuntado aparece sobre todo en los dos arcos de ventana.
    t = max(0.0, min(1.0, (t - 0.22) / 0.78))
    punta = 0.30 if b - a > 0.32 else 0.055
    return (1 - punta) * sqrt(t * (2 - t)) + punta * t**4


def perfil_pano(apotema, alzado, encaje="seccion"):
    if encaje not in ("seccion", "0036"):
        raise ValueError("Encaje desconocido")
    escala = alzado["px_por_m"]
    semi = apotema * tan(pi / 8)
    ordenes = [tramos(tabla, semi, escala) for tabla in (INFERIOR, SUPERIOR)]
    # Las dos filas comparten todos los vértices del encuentro aun cuando sus
    # juntas estén contrapeadas. Añadir estaciones a ambos lados de cada junta.
    jambas = {cx + signo * 0.265 for cx in (-0.59, 0.59) for signo in (-1, 1)}
    anclas = set(jambas)
    estaciones = set()
    for orden in ordenes:
        for a, c, b, _ in orden:
            estaciones.update([a, a + 0.002, b - 0.002, b])
            for t in (0.22, 0.225, 0.24, 0.27):
                estaciones.update((a + t * (c - a), b - t * (b - c)))
            anclas.update((a, c, b))
            for lo, hi in ((a, c), (c, b)):
                estaciones.update(np.linspace(lo, hi, 17))
    # Las subdivisiones de ambos órdenes pueden caer en el mismo punto al
    # pasar a float32 en Blender. Conservar las coordenadas exactas de las juntas.
    unicas = {round(u, 7): u for u in sorted(estaciones)}
    unicas.update((round(u, 7), u) for u in sorted(anclas))
    estaciones = sorted(unicas.values())

    def cota(fila):
        if encaje == "0036":
            return APICE_MODELO + (FILA_APICE - fila) / escala
        return (alzado["niveles"]["arranque_cupula"]["fila_px"] - fila) / escala

    def junta(u, fila):
        if fila == 2:
            return 0.0
        orden = ordenes[fila]
        seg = next(s for s in orden if u <= s[2])
        h = arco_tramo(u, seg)
        base = (2197, 2103)[fila]
        z = cota(base + h * (seg[3] - base))
        if fila == 1:
            # El segundo frente tiene que librar el arco mayor del primero.
            z = max(z, junta(u, 0) + 0.061)
            if encaje == "0036":
                z = min(-0.013, z)
        return z

    return semi, ordenes, estaciones, junta


def pared_piloto(forma, apotema, bajo, alzado, encaje="seccion"):
    """Las jambas, la bóveda y el intradós comparten el mismo borde exterior."""
    from detalle_visita import caras_con_huecos
    _, _, us, junta = perfil_pano(apotema, alzado, encaje)
    alf = alzado["niveles"]["pie_ventanas_tambor"]["z_m"]
    for a, b in zip(us, us[1:]):
        u = (a + b) / 2
        dentro = min(abs(u - 0.59), abs(u + 0.59)) < 0.265
        za, zb = (alf, alf) if dentro else (junta(a, 0), junta(b, 0))
        forma.cara(
            forma.puntos(
                [
                    (apotema, a, bajo),
                    (apotema, a, za),
                    (apotema, b, zb),
                    (apotema, b, bajo),
                ]
            ),
            "yeso",
        )

    for cx in (-0.59, 0.59):
        a, b = cx - 0.265, cx + 0.265
        arco = [(u, junta(u, 0)) for u in reversed(us) if a <= u <= b]
        boca = np.array([(a, alf), (b, alf), *arco])
        previo = None
        for fondo, factor, tono in (
            (0, 1, "yeso"),
            (0.008, 0.986, "crema"),
            (0.017, 0.990, "yeso"),
            (0.028, 1, "yeso"),
            (0.09, 0.964, "crema"),
        ):
            contorno = (boca - [cx, alf + 0.51]) * factor + [cx, alf + 0.51]
            sig = forma.puntos((apotema + fondo, y, z) for y, z in contorno)
            if previo is not None:
                forma.banda(previo, sig, tono)
            previo = sig
        celosia(forma, apotema + 0.09, contorno, cx)
        # El fondo luminoso llega hasta el perímetro incluso en la vista oblicua.
        posterior = forma.puntos((apotema + 0.17, y, z) for y, z in contorno)
        forma.banda(previo, posterior, "yeso")
        for f in caras_con_huecos(contorno, []):
            forma.cara([posterior[i] for i in f], "cielo")


def celosia(forma, x, borde, cx):
    """Calados con ocho pétalos y un ojo central. Dibujo y espesor propuestos."""
    from detalle_visita import caras_con_huecos
    paso = 0.168
    alto = borde[2:][::-1]
    a, b = borde[:2, 0]
    alf = borde[0, 1]
    huecos = []

    def area(p):
        y, z = p.T
        return (y @ np.roll(z, -1) - z @ np.roll(y, -1)) / 2

    def abrir(c, poligono):
        p = c + paso * np.asarray(poligono)
        # Reservar yeso en el perímetro. También comprobar el mínimo de todo
        # el arco que cubre el hueco por si cae sobre un pico entre dos vértices.
        lo, hi = p[:, 0].min(), p[:, 0].max()
        interior = alto[(alto[:, 0] >= lo) & (alto[:, 0] <= hi), 1]
        techo = min([*np.interp([lo, hi], alto[:, 0], alto[:, 1]), *interior])
        if (
            lo > a + 0.003
            and hi < b - 0.003
            and p[:, 1].min() > alf + 0.004
            and p[:, 1].max() < techo - 0.003
        ):
            # CDT identifica el interior a la izquierda de cada contorno.
            huecos.append(p if area(p) > 0 else p[::-1])

    for z in np.arange(alf + 0.50 * paso, alto[:, 1].max() + paso, paso):
        for y in (cx - paso, cx, cx + paso):
            centro = np.array([y, z])
            abrir(
                centro,
                [
                    (r * cos(k * pi / 8), r * sin(k * pi / 8))
                    for k in range(16)
                    for r in [(0.129, 0.097)[k % 2]]
                ],
            )
            for k in range(8):
                ang = k * pi / 4
                radial = np.array([cos(ang), sin(ang)])
                normal = np.array([-sin(ang), cos(ang)])
                punta = 0.46 if k % 2 == 0 else 0.59
                abrir(
                    centro,
                    [
                        r * radial + t * normal
                        for r, t in [
                            (0.15, 0),
                            (0.22, -0.067),
                            (0.345, -0.111),
                            (punta, 0),
                            (0.345, 0.111),
                            (0.22, 0.067),
                        ]
                    ],
                )
            for sy in (-1, 1):
                for sz in (-1, 1):
                    abrir(
                        centro,
                        [
                            (sy * y, sz * z)
                            for y, z in [(0.385, 0.477), (0.476, 0.386), (0.476, 0.477)]
                        ],
                    )
    frontal = [
        i for lazo in [borde, *huecos] for i in forma.puntos((x, y, z) for y, z in lazo)
    ]
    caras = caras_con_huecos(borde, huecos)
    tri = np.vstack([borde, *huecos])[caras]
    v, w = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    neta = abs(v[:, 0] * w[:, 1] - v[:, 1] * w[:, 0]).sum() / 2
    esperada = abs(area(borde)) - sum(map(area, huecos))
    if abs(neta - esperada) > 1e-6:
        raise ValueError("La celosía no cubre el vano descontados los calados")
    for f in caras:
        forma.cara([frontal[i] for i in f], "crema")
    reverso = forma.puntos((x + 0.010, y, z) for y, z in borde)
    offset = len(borde)
    for h in huecos:
        centro = h.mean(axis=0)
        tras = forma.puntos((x + 0.010, y, z) for y, z in centro + 0.97 * (h - centro))
        forma.banda(frontal[offset : offset + len(h)], tras, "yeso")
        reverso.extend(tras)
        offset += len(h)
    for f in caras:
        forma.cara([reverso[i] for i in reversed(f)], "yeso")


def construir_sector(apotema, paleta, alzado, encaje="seccion"):
    import bpy
    from detalle_visita import Superficie
    from talla_cupulin import tallar_ataurique
    from encajar_frentes_visita import encajar
    escala = alzado["px_por_m"]
    semi, ordenes, estaciones, junta = perfil_pano(apotema, alzado, encaje)

    def punto(d, u, z):
        x = apotema - d
        return (x, u * x / apotema, z)

    cornisa = bpy.data.objects["sala_cornisa"]
    fondos = FONDO_M
    if encaje == "seccion":
        # El apoyo termina en el borde interior real de la cornisa, no en
        # una profundidad independiente que dejaría una chapa delante del paño.
        coords = np.array([tuple(cornisa.matrix_world @ v.co) for v in cornisa.data.vertices])
        sector = (coords[:, 0] > 0) & (abs(coords[:, 1]) <= coords[:, 0] * tan(pi / 8) + 1e-6)
        xinterior = coords[sector, 0].min()
        fondos = (0.0, FONDO_M[1], float(apotema - xinterior))
    xint = apotema - fondos[-1]
    huella = np.array(
        [
            (apotema, -semi),
            (apotema, semi),
            (xint, xint * tan(pi / 8)),
            (xint, -xint * tan(pi / 8)),
        ]
    )
    # El fondo y los extremos se apoyan en la cornisa existente, plana a z=0.
    # Cortar solo la chapa que antes cerraba este paño.
    grafo = bpy.context.evaluated_depsgraph_get()
    for d in np.linspace(0.004, fondos[-1] - 0.001, 7):
        for u in np.linspace(-semi + 0.008, semi - 0.008, 41):
            hit, p, _, _, obj, _ = bpy.context.scene.ray_cast(
                grafo, punto(d, u, -2), (0, 0, 1), distance=4
            )
            # La moldura del vano se adelanta hasta 55 mm en el borde exterior.
            primero_recortable = encaje == "seccion" and hit and obj.name.startswith("hilada_frente_01_")
            if d > 0.055 and not primero_recortable and (not hit or obj != cornisa or abs(p.z) > 1e-5):
                raise ValueError(f"La cornisa no está libre a fondo {d:.3f}, u={u:.3f}: {obj.name if hit else 'sin impacto'}")
    encajar(cornisa, [huella])
    apoyo = dict(aristas=0, objetos=[])
    if encaje == "seccion":
        from encajar_frentes_visita import cerrar_corte_x
        for obj in list(bpy.context.scene.objects):
            if obj.name.startswith(("hilada_frente_01_", "Frentes tallados junto al cupulín 00")):
                encajar(obj, [huella])
                cierre, cantidad = cerrar_corte_x(obj, xint)
                if cantidad:
                    cierre.objeto(f"Apoyo del paño 00 en {obj.name}", paleta)
                    apoyo["aristas"] += cantidad
                    apoyo["objetos"].append(obj.name)

    for fila, orden in enumerate(ordenes):
        for i, tramo in enumerate(orden, start=1):
            a, c, b, _ = tramo
            us = [u for u in estaciones if a <= u <= b]
            forma = Superficie()
            previo = None

            # El labio tiene dos quiebros cortos. El casco se abre en gallones
            # y vuelve a un apoyo continuo en la fila siguiente.
            def superficie(u, t):
                h = arco_tramo(u, tramo)
                v = (u - a) / (c - a) - 1 if u <= c else (u - c) / (b - c)
                d = (1 - t) * fondos[fila] + t * fondos[fila + 1]
                dentro = sin(pi * t)
                # Nervios en abanico. La altura central se disipa al llegar
                # al canto. El bisel deja una junta de yeso de 2 mm.
                lobulo = cos(pi * (2.2 - 0.8 * t) * v) ** 2
                d -= 0.033 * dentro * h * (0.62 + 0.38 * lobulo)
                z = (1 - t) * junta(u, fila) + t * junta(u, fila + 1)
                z += dentro * h * (0.032 + 0.021 * lobulo)
                z += dentro * max(0.0, 1 - min(u - a, b - u) / 0.002) * 0.003
                z -= max(0.0, 1 - abs(t - 0.068) / 0.033) * 0.005 * h
                return punto(d, u, z)

            for t in (
                0,
                0.035,
                0.068,
                0.092,
                0.116,
                0.16,
                0.22,
                0.30,
                0.40,
                0.5,
                0.60,
                0.7,
                0.78,
                0.86,
                0.92,
                0.96,
                1.0,
            ):
                vs = [superficie(u, t) for u in us]
                sig = forma.puntos(vs)
                if previo is not None:
                    for j in range(len(us) - 1):
                        tono = "crema" if 0.068 < t <= 0.092 else "yeso"
                        forma.cara((previo[j + 1], previo[j], sig[j], sig[j + 1]), tono)
                # Cierre vertical del corte contra las dos caras octogonales contiguas.
                if previo is not None and (i == 1 or i == len(orden)):
                    lado = 0 if i == 1 else -1
                    p, q = forma.v[previo[lado]], forma.v[sig[lado]]
                    p0, q0 = forma.puntos([(*p[:2], 0), (*q[:2], 0)])
                    if abs(p[2]) > 1e-8:
                        forma.cara((previo[lado], p0, sig[lado]), "yeso")
                    if abs(q[2]) > 1e-8:
                        forma.cara((p0, q0, sig[lado]), "yeso")
                previo = sig
            if i in ((3, 5, 8, 10, 13, 15) if fila == 0 else (2, 5, 8, 11, 14, 16)):

                def talla(u, v, h):
                    x, y, z = superficie(
                        a + (b - a) * (0.15 + 0.70 * u), 0.18 + 0.70 * v
                    )
                    return (x - h * 0.77, y, z - h * 0.64)

                tallar_ataurique(forma, talla)
            forma.objeto(f"adaraja_00_{fila + 1}_{i:02d}", paleta)

    return dict(
        piezas_por_hilada=list(map(len, ordenes)),
        fondos_m=fondos,
        apoyo=apoyo,
        encaje=encaje,
        desplazamiento_vertical_seccion_m=(APICE_MODELO
        - (alzado["niveles"]["arranque_cupula"]["fila_px"] - FILA_APICE) / escala)
        if encaje == "0036" else 0.0,
        apotema_m=apotema,
    )


def medir_sector(apotema, suelo):
    """Primer impacto dirigido a cada vano y a la cornisa desde tres cámaras."""
    import bpy
    grafo = bpy.context.evaluated_depsgraph_get()
    resultado = {}
    for nombre, origen in (
        ("sala", (0, -0.8, suelo + 1.6)),
        ("frontal", (1.75, 0.48, -1.38)),
        ("lateral", (2.45, -1.18, -0.95)),
    ):

        def impacto(x, y, z):
            hit, _, _, f, obj, _ = bpy.context.scene.ray_cast(
                grafo, origen, np.subtract((x, y, z), origen)
            )
            return (obj, f) if hit else (None, None)

        ventanas = []
        for cx in (-0.59, 0.59):
            # Parte interior de la abertura, evitando el canto de la jambas.
            libres = 0
            for u in np.linspace(-0.21, 0.21, 23):
                for z in np.linspace(-1.23, -0.38, 33):
                    obj, f = impacto(apotema, cx + u, z)
                    if obj and obj.name == "tambor":
                        mat = obj.data.materials[obj.data.polygons[f].material_index]
                        libres += mat.name.startswith("Luz de patio")
            ventanas.append(libres)
        piezas = set()
        for y in np.linspace(-1.55, 1.55, 141):
            for z in np.linspace(-0.52, 0.18, 49):
                obj, _ = impacto(apotema - 0.16, y, z)
                if obj and obj.name.startswith("adaraja_00_"):
                    piezas.add(obj.name)
        resultado[nombre] = dict(
            rayos_por_ventana=23 * 33,
            cielo_por_ventana=ventanas,
            piezas_visibles=[
                sum(p.startswith(f"adaraja_00_{i}_") for p in piezas) for i in (1, 2)
            ],
        )
    return resultado


def verificar_juntas_glb(escena, datos, inicio_bin, sector):
    """Lee POSITION en el GLB final (eje Y vertical); coteja los cantos en micras."""

    def vertices(nombre):
        nodo = next(n for n in escena["nodes"] if n["name"] == nombre)
        if any(k in nodo for k in ("matrix", "translation", "rotation", "scale")):
            raise ValueError(f"Transformación inesperada en {nombre}")
        partes = []
        for prim in escena["meshes"][nodo["mesh"]]["primitives"]:
            acc = escena["accessors"][prim["attributes"]["POSITION"]]
            vista = escena["bufferViews"][acc["bufferView"]]
            if acc["componentType"] != 5126 or vista.get("byteStride", 12) != 12:
                raise ValueError("Formato inesperado de POSITION")
            offset = inicio_bin + vista.get("byteOffset", 0) + acc.get("byteOffset", 0)
            p = np.frombuffer(datos, dtype="<f4", count=3 * acc["count"], offset=offset)
            partes.append(np.rint(p.reshape(-1, 3).astype(float) * 1e6).astype(int))
        return set(map(tuple, np.vstack(partes)))

    filas = [
        [vertices(f"adaraja_00_{i}_{k + 1:02d}") for k in range(n)]
        for i, n in enumerate(sector["piezas_por_hilada"], 1)
    ]
    laterales = [len(a & b) for fila in filas for a, b in zip(fila, fila[1:])]
    if min(laterales) < 17:
        raise ValueError("Falta un canto entre piezas vecinas")
    apa = sector["apotema_m"]

    def canto(fila, fondo):
        x = round((apa - fondo) * 1e6)
        return {p for pieza in fila for p in pieza if abs(p[0] - x) <= 1 and p[1] != 0}

    union = canto(filas[0], sector["fondos_m"][1])
    if not union or union != canto(filas[1], sector["fondos_m"][1]):
        raise ValueError("Los dos órdenes difieren en el encuentro")
    pared = canto(filas[0], 0)
    if not pared or pared - vertices("tambor"):
        raise ValueError("El vano no conserva el borde inferior de las adarajas")
    return dict(
        juntas_laterales=len(laterales),
        minimo_vertices_por_junta=min(laterales),
        vertices_compartidos_entre_hiladas=len(union),
        vertices_compartidos_con_pared=len(pared),
    )
