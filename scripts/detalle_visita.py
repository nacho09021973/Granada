"""Superficies de presentación de la visita. Coordenadas Blender en metros.

Los perfiles, colores y la celosía son propuestas del modelo. La clave conserva
el borde del cierre del OBJ. El cupulín 00 reutiliza el asiento y el recorte 0032.
"""

from collections import defaultdict
from math import cos, sin, pi, sqrt
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.geometry import delaunay_2d_cdt

from hiladas_ventanas import PROFUNDIDAD_NICHO_M


class Superficie:
    def __init__(self):
        self.v = []
        self.f = []
        self.tonos = []

    def puntos(self, puntos):
        inicio = len(self.v)
        self.v.extend(tuple(p) for p in puntos)
        return list(range(inicio, len(self.v)))

    def cara(self, indices, tono):
        for i in range(1, len(indices) - 1):
            self.f.append((indices[0], indices[i], indices[i + 1]))
            self.tonos.append(tono)

    def banda(self, a, b, tono):
        for i in range(len(a)):
            j = (i + 1) % len(a)
            self.cara((a[i], a[j], b[j], b[i]), tono)

    def objeto(self, nombre, paleta, reemplazar=None):
        mesh = bpy.data.meshes.new(nombre)
        mesh.from_pydata(self.v, [], self.f)
        materiales = list(dict.fromkeys(self.tonos))
        for m in materiales:
            mesh.materials.append(paleta[m])
        mesh.polygons.foreach_set(
            "material_index", [materiales.index(c) for c in self.tonos]
        )
        mesh.update()
        if reemplazar is not None:
            reemplazar.data = mesh
            reemplazar.matrix_world = Matrix.Identity(4)
            return reemplazar
        obj = bpy.data.objects.new(nombre, mesh)
        bpy.context.collection.objects.link(obj)
        return obj


def caras_con_huecos(exterior, huecos):
    """Triangulación con bordes obligatorios. Devuelve índices en los lazos de entrada."""
    lazos = [exterior, *huecos]
    xy, regiones = [], []
    for lazo in lazos:
        regiones.append(list(range(len(xy), len(xy) + len(lazo))))
        xy.extend(Vector((p[0], p[1])) for p in lazo)
    _, _, caras, ids, _, regiones_cara = delaunay_2d_cdt(xy, [], regiones, 1, 1e-7)
    if any(len(i) != 1 for i in ids):
        raise ValueError("Intersección inesperada en los contornos")
    return [
        [ids[i][0] for i in cara]
        for cara, origen in zip(caras, regiones_cara)
        if origen == [0]
    ]


def contorno(obj):
    vecinos = defaultdict(list)
    aristas = defaultdict(int)
    for f in obj.data.polygons:
        for edge in f.edge_keys:
            aristas[edge] += 1
    for (a, b), n in aristas.items():
        if n == 1:
            vecinos[a].append(b)
            vecinos[b].append(a)
    assert all(len(v) == 2 for v in vecinos.values())
    orden = [min(vecinos)]
    anterior = None
    while True:
        a = orden[-1]
        b = next(i for i in vecinos[a] if i != anterior)
        if b == orden[0]:
            break
        orden.append(b)
        anterior = a
    assert len(orden) == len(vecinos)
    return np.array([tuple(obj.matrix_world @ obj.data.vertices[i].co) for i in orden])


def clave(obj, paleta):
    borde = contorno(obj)
    forma = Superficie()
    phi = np.arange(128) * 2 * pi / 128
    x, y = np.cos(phi), np.sin(phi)
    # Cociente radial de la unión de dos cuadrados. Las esquinas caen en vértices.
    ro = cos(pi / 8) / np.cos((phi % (pi / 4)) - pi / 8)
    estrella = (1 / sqrt(2)) / np.minimum(
        np.maximum(abs(x), abs(y)),
        np.maximum(abs((x + y) / sqrt(2)), abs((x - y) / sqrt(2))),
    )

    def anillo(r, z):
        return np.column_stack((x * r, y * r, np.broadcast_to(z, x.shape)))

    exterior = anillo(0.465 * ro, 4.425)
    assert np.linalg.norm(borde[:, :2], axis=1).min() > 0.465
    a = forma.puntos(borde)
    b = forma.puntos(exterior)
    for cara in caras_con_huecos(borde, [exterior]):
        forma.cara(cara, "yeso")
    # Ocho trompillas con garganta y enjuta. El arco cierra en sus extremos.
    nicho = np.sqrt(np.maximum(0, 1 - ((phi % (pi / 4)) / (pi / 8) - 1) ** 2))
    for r, z, tono in [
        (0.452 * ro, 4.416, "crema"),
        (0.443 * ro, 4.421, "yeso"),
        (0.421 * ro, 4.427 + 0.035 * nicho, "yeso"),
        (0.391 * ro, 4.436 + 0.078 * nicho, "crema"),
        (0.357 * ro, 4.453 + 0.078 * nicho, "yeso"),
        (0.325 * ro, 4.47 + 0.041 * nicho, "yeso"),
        (0.302 * ro, 4.512, "crema"),
        (0.292 * estrella, 4.535, "lapislazuli"),
        (0.282 * estrella, 4.522, "yeso"),
        (0.272 * estrella, 4.520, "crema"),
        (0.261 * estrella, 4.535, "yeso"),
        (0.251 * estrella, 4.536, "ocre"),
        (0.237 * estrella, 4.556, "yeso"),
        (0.212 * estrella, 4.589, "crema"),
        (0.180 * estrella, 4.611, "yeso"),
        (0.169 * estrella, 4.603, "pizarra"),
        (0.156 * estrella, 4.612, "crema"),
        (0.130 * estrella, 4.637, "yeso"),
        (0.095 * estrella, 4.659, "crema"),
        (0.071 * ro, 4.670, "yeso"),
        (0.056 * ro, 4.664, "ocre"),
        (0.048 * ro, 4.650, "oro"),
        (0.036 * ro, 4.638, "oro"),
        (0.015 * ro, 4.627, "oro"),
    ]:
        c = forma.puntos(anillo(r, z))
        forma.banda(b, c, tono)
        b = c
    centro = forma.puntos([(0, 0, 4.626)])[0]
    for i in range(len(b)):
        forma.cara((b[i - 1], b[i], centro), "oro")
    # Verificar que la proyección cubre el mismo disco una sola vez.
    tri = np.array(forma.v)[np.array(forma.f), :2]
    u, v = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    area = abs(u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]).sum() / 2
    px, py = borde[:, 0], borde[:, 1]
    assert abs(area - abs(px @ np.roll(py, 1) - py @ np.roll(px, 1)) / 2) < 1e-6
    assert max(p[2] for p in forma.v) <= 4.670001
    forma.objeto("Clave con trompillas", paleta, obj)
    return len(a)


def cupulin_piloto(obj, paleta, previas, escala):
    asiento = np.load(previas / "piloto_asiento.npz")
    # El importador de OBJ puede soldar y reordenar vértices.
    originales = np.array([tuple(obj.matrix_world @ v.co) for v in obj.data.vertices])

    # El hash del OBJ se verifica en el exportador. Verificar también el grupo.
    def caja(v):
        return np.array([v.min(axis=0), v.max(axis=0)])

    assert np.allclose(caja(originales), caja(asiento["original"] * escala), atol=1e-6)
    from mathutils.kdtree import KDTree

    def verificar_vertices(origen, destino):
        arbol = KDTree(len(destino))
        for i, punto in enumerate(destino):
            arbol.insert(punto, i)
        arbol.balance()
        assert max(arbol.find(punto)[2] for punto in origen) < 2e-6

    referencia = asiento["original"] * escala
    verificar_vertices(originales, referencia)
    verificar_vertices(referencia, originales)
    p = asiento["v"] * escala
    base, techo = p[:192:2], p[1:192:2]
    centro = techo.mean(axis=0)
    radial = techo - centro
    forma = Superficie()
    previo = forma.puntos(p[-191::2])
    n = len(base)
    fase = np.arange(n) * 2 * pi / n
    arco = np.sqrt(np.maximum(0, 1 - ((fase % (pi / 2)) / (pi / 4) - 1) ** 2))

    # Cuatro arcos con enjutas. Su apoyo queda en la boca intersectada,
    # y la parte superior converge en el remate poligonal.
    def registro(t, r):
        return (
            base
            + (techo - base) * np.broadcast_to(t, (n,))[:, None]
            + radial * (np.broadcast_to(r, (n,))[:, None] - 1)
        )

    for puntos, tono in [
        (p[-192::2], "crema"),
        (base, "yeso"),
        (registro(0.10, 0.98), "crema"),
        (registro(0.15, 0.965), "yeso"),
        (registro(0.26 + 0.24 * arco, 0.955), "yeso"),
        (registro(0.28 + 0.24 * arco, 0.92), "crema"),
        (registro(0.30 + 0.24 * arco, 0.915), "yeso"),
        (registro(0.315 + 0.24 * arco, 0.94), "ocre"),
        (registro(0.46 + 0.23 * arco, 0.93), "yeso"),
        (registro(0.65 + 0.10 * arco, 0.82), "crema"),
        (registro(0.77, 0.78), "yeso"),
    ]:
        siguiente = forma.puntos(puntos)
        forma.banda(previo, siguiente, tono)
        previo = siguiente
    # Techo de ocho puntas con filete. Las paredes son superficies continuas.
    est = cos(pi / 4) / np.minimum(
        np.maximum(abs(np.cos(fase)), abs(np.sin(fase))),
        np.maximum(abs(np.cos(fase - pi / 4)), abs(np.sin(fase - pi / 4))),
    )
    for t, r, tono in [
        (0.84, 0.69 * est, "yeso"),
        (0.85, 0.66 * est, "lapislazuli"),
        (0.86, 0.62 * est, "crema"),
        (0.91, 0.52 * est, "yeso"),
        (0.97, 0.36 * est, "crema"),
        (1, 0.15 * est, "yeso"),
    ]:
        siguiente = forma.puntos(registro(t, r))
        forma.banda(previo, siguiente, tono)
        previo = siguiente
    cap = forma.puntos([centro])[0]
    for i in range(n):
        forma.cara((previo[i - 1], previo[i], cap), "ocre")
    forma.objeto("Pozo con cuatro arcos", paleta, obj)
    recorte = np.load(previas / "piezas_recortadas_00.npz")
    piezas = Superficie()
    piezas.puntos(recorte["v"] * escala)
    piezas.f = recorte["f"].tolist()
    piezas.tonos = ["yeso"] * len(piezas.f)
    piezas.objeto("Adarajas recortadas del cupulín 00", paleta)
    return asiento["centro"] * escala


def tambor_con_vanos(obj, paleta, alzado, pano_piloto=None, boca="arco"):
    """Reemplaza los paños ciegos. La luz y la tracería son propuestas de escena.

    boca="escalonada" (0043): marco y boca escalonados medidos
    (`scripts/nicho_escalonado.py`), recortados bajo el canto superior del
    muro, que aquí no lleva adarajas encima. "arco" conserva el vano de 0035.
    """
    coords = np.array([tuple(obj.matrix_world @ v.co) for v in obj.data.vertices])
    apotema = coords[:, 0].max()
    bajo, alto = coords[:, 2].min(), coords[:, 2].max()
    semilado = apotema * np.tan(pi / 8)
    alf = alzado["niveles"]["pie_ventanas_tambor"]["z_m"]
    arranque = -0.43
    radio = 0.265
    sol = bpy.data.materials.new("Luz de patio")
    sol.use_nodes = True
    shader = sol.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Emission Color"].default_value = (1, 0.91, 0.72, 1)
    shader.inputs["Emission Strength"].default_value = 2.2
    sol.use_backface_culling = False
    paleta["cielo"] = sol
    forma = Superficie()

    def arco(cx, ampliar=0):
        r = radio + ampliar
        return [(cx - r, alf - ampliar), (cx + r, alf - ampliar)] + [
            (cx + r * cos(a), arranque + r * sin(a)) for a in np.linspace(0, pi, 33)
        ]

    for k in range(8):
        a = k * pi / 4

        def xyz(x, z, vuelo=0):
            d = apotema - vuelo
            return (d * cos(a) - x * sin(a), d * sin(a) + x * cos(a), z)

        rect = [
            (-semilado, bajo),
            (semilado, bajo),
            (semilado, alto),
            (-semilado, alto),
        ]
        centros = [-0.59, 0.59]
        if k == 0 and pano_piloto:
            pano_piloto(forma, apotema, bajo, alzado)
            centros = []
        elif boca == "escalonada":
            from nicho_escalonado import construir_nicho, contorno as contorno_boca
            # Sin adarajas encima, el remate no puede pasar del canto del muro.
            tope = alto - 0.012
            huecos = [contorno_boca(cx, 0.0, alf, tope) for cx in centros]
            ids = forma.puntos(xyz(x, z) for x, z in rect + huecos[0] + huecos[1])
            for cara in caras_con_huecos(rect, huecos):
                forma.cara([ids[i] for i in cara], "yeso")
            for cx in centros:
                construir_nicho(forma, xyz, cx, alf, "nervios", tope=tope)
            centros = []
        else:
            huecos = [arco(cx, 0.095) for cx in centros]
            todos = rect + huecos[0] + huecos[1]
            ids = forma.puntos(xyz(x, z) for x, z in todos)
            for cara in caras_con_huecos(rect, huecos):
                forma.cara([ids[i] for i in cara], "yeso")
        for cx in centros:
            previo = None
            for ancho, vuelo, tono in [
                (0.095, 0, "yeso"),
                (0.084, 0.027, "crema"),
                (0.077, 0.031, "yeso"),
                (0.069, 0.020, "yeso"),
                (0.062, 0.021, "ocre"),
                (0.054, 0.030, "yeso"),
                (0.030, 0.046, "crema"),
                (0.014, 0.055, "yeso"),
                (0, 0.052, "yeso"),
                # Nicho hasta la celosía (0041); antes -0,09 y -0,12.
                (-0.008, -(PROFUNDIDAD_NICHO_M - 0.03), "crema"),
                (-0.008, -PROFUNDIDAD_NICHO_M, "yeso"),
            ]:
                siguiente = forma.puntos(xyz(x, z, vuelo) for x, z in arco(cx, ancho))
                if previo is not None:
                    forma.banda(previo, siguiente, tono)
                previo = siguiente
            # Nervios diagonales con sección romboidal. Recortar contra el arco
            # por intersección de cada recta con el polígono convexo.
            lazo = np.array(arco(cx, -0.001))
            for sentido in (-1, 1):
                for nivel in np.arange(alf - radio, arranque + 2 * radio, 0.086):
                    alturas = lazo[:, 1] - sentido * (lazo[:, 0] - cx) - nivel
                    cruces = []
                    for i, j in zip(range(-1, len(lazo) - 1), range(len(lazo))):
                        if (alturas[i] > 0) != (alturas[j] > 0):
                            cruces.append(
                                lazo[i]
                                + (lazo[j] - lazo[i])
                                * alturas[i]
                                / (alturas[i] - alturas[j])
                            )
                    if len(cruces) != 2:
                        continue
                    tramo = []
                    for x, z in cruces:
                        tramo.append(
                            forma.puntos(
                                xyz(x + dx, z - sentido * dx, -(PROFUNDIDAD_NICHO_M - 0.035) + prof)
                                for dx, prof in [
                                    (-0.005, 0),
                                    (0, 0.008),
                                    (0.005, 0),
                                    (0, -0.008),
                                ]
                            )
                        )
                    forma.banda(*tramo, "crema")
            panel = forma.puntos(xyz(x, z, -(PROFUNDIDAD_NICHO_M + 0.07)) for x, z in arco(cx))
            forma.cara(panel, "cielo")
        # Perfil continuo del friso y la imposta. Los fondos quedan retranqueados.
        for z in (alf - 0.14, bajo + 0.13):
            previo = None
            for dz, vuelo in [
                (-0.055, 0),
                (-0.042, 0.026),
                (-0.028, 0.030),
                (-0.019, 0.017),
                (0.014, 0.016),
                (0.025, 0.040),
                (0.040, 0.044),
                (0.055, 0),
            ]:
                ancho = (apotema - vuelo) * np.tan(pi / 8)
                linea = forma.puntos(
                    [xyz(-ancho, z + dz, vuelo), xyz(ancho, z + dz, vuelo)]
                )
                if previo:
                    forma.cara([*previo, *reversed(linea)], "crema")
                previo = linea
    forma.objeto("Tambor con vanos", paleta, obj)
    return apotema


def luz_de_vanos(objetos, apotema):
    """Fracción de los dieciséis vanos visibles desde cada vértice, en metros."""
    from mathutils.bvhtree import BVHTree

    puntos, triangulos = [], []
    offset = 0
    for o in objetos:
        m = o.data
        p = np.empty(3 * len(m.vertices), dtype=np.float32)
        m.vertices.foreach_get("co", p)
        matriz = np.asarray(o.matrix_world)
        p = p.reshape(-1, 3) @ matriz[:3, :3].T + matriz[:3, 3]
        puntos.append(p)
        m.calc_loop_triangles()
        f = np.empty(3 * len(m.loop_triangles), dtype=np.int32)
        m.loop_triangles.foreach_get("vertices", f)
        triangulos.append(f.reshape(-1, 3) + offset)
        offset += len(p)
    todos = np.vstack(puntos)
    arbol = BVHTree.FromPolygons(todos, np.vstack(triangulos), all_triangles=True)
    # Se repiten muchos vértices exactamente en aristas y cambios de material.
    unicos, inversa = np.unique(np.round(todos, 6), axis=0, return_inverse=True)
    visibles = np.zeros(len(unicos))
    for a in np.arange(8) * pi / 4:
        for s in (-0.59, 0.59):
            foco = np.array(
                [
                    (apotema - 0.10) * cos(a) - s * sin(a),
                    (apotema - 0.10) * sin(a) + s * cos(a),
                    -0.83,
                ]
            )
            delta = foco - unicos
            largo = np.linalg.norm(delta, axis=1)
            dirs = delta / np.maximum(largo[:, None], 1e-8)
            origen = unicos + 0.002 * dirs
            visibles += np.fromiter(
                (
                    arbol.ray_cast(o, d, float(distancia) - 0.003)[0] is None
                    for o, d, distancia in zip(origen, dirs, largo)
                ),
                dtype=bool,
                count=len(unicos),
            )
    # Suelo y paredes aportan relleno. El color de los pigmentos queda aparte.
    intensidad = (0.32 + 0.68 * np.sqrt(visibles / 16))[inversa].ravel()
    offset = 0
    for o, p in zip(objetos, puntos):
        color = o.data.color_attributes.new(
            name="Luz de vanos", type="BYTE_COLOR", domain="POINT"
        )
        rgba = np.ones((len(p), 4), dtype=np.float32)
        rgba[:, :3] = intensidad[offset : offset + len(p), None]
        color.data.foreach_set("color", rgba.ravel())
        o.data.color_attributes.active_color = color
        offset += len(p)
    return len(unicos)
