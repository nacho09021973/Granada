"""Vacía los contornos de las caras locales en las hiladas trianguladas.

Corte en planta por semiplanos convexos. Se conservan material y posición de
los fragmentos exteriores. Las coordenadas de los contornos se dan en metros.
"""

import numpy as np


def semiplanos(xy):
    normales = np.roll(xy, -1, axis=0) - xy
    normales = normales[:, [1, 0]] * [-1, 1]
    normales /= np.linalg.norm(normales, axis=1)[:, None]
    centro = xy.mean(axis=0)
    normales *= np.sign(((centro - xy) * normales).sum(axis=1))[:, None]
    return normales, (normales * xy).sum(axis=1)


def partir(poligono, normal, nivel):
    dentro, fuera = [], []
    for i, a in enumerate(poligono):
        b = poligono[(i + 1) % len(poligono)]
        da, db = normal @ a[:2] - nivel, normal @ b[:2] - nivel
        if da >= -1e-8:
            dentro.append(a)
        if da <= 1e-8:
            fuera.append(a)
        if (da > 1e-8 and db < -1e-8) or (db > 1e-8 and da < -1e-8):
            cruce = a + (b - a) * (da / (da - db))
            dentro.append(cruce)
            fuera.append(cruce)
    return dentro, fuera


def encajar(objeto, contornos):
    m = objeto.data
    matriz = np.asarray(objeto.matrix_world)
    local = np.empty((len(m.vertices), 3), dtype=np.float32)
    m.vertices.foreach_get("co", local.ravel())
    mundo = local @ matriz[:3, :3].T + matriz[:3, 3]
    faces = np.empty((len(m.polygons), 3), dtype=np.int32)
    m.polygons.foreach_get("vertices", faces.ravel())
    regiones = {}
    tri = mundo[faces, :2]
    bajo, alto = tri.min(axis=1), tri.max(axis=1)
    for xy in contornos:
        candidatos = np.nonzero(
            ((alto >= xy.min(axis=0)) & (bajo <= xy.max(axis=0))).all(axis=1)
        )[0]
        ns, ds = semiplanos(xy)
        # Un triángulo separado por algún lado no alcanza el contorno.
        for i in candidatos[
            ((tri[candidatos] @ ns.T - ds).max(axis=1) > 1e-8).all(axis=1)
        ]:
            regiones.setdefault(i, []).append((ns, ds))
    if not regiones:
        return
    materiales = np.empty(len(faces), dtype=np.int32)
    m.polygons.foreach_get("material_index", materiales)
    conservar = np.ones(len(faces), dtype=bool)
    conservar[list(regiones)] = False
    caras = faces[conservar].tolist()
    tonos = materiales[conservar].tolist()
    vertices = local.tolist()
    nuevos = {}
    inversa = np.linalg.inv(matriz)

    def indice(p):
        clave = tuple(p.round(8))
        if clave not in nuevos:
            nuevos[clave] = len(vertices)
            vertices.append((inversa[:3, :3] @ p + inversa[:3, 3]).tolist())
        return nuevos[clave]

    for i, regiones_cara in regiones.items():
        t = mundo[faces[i]]
        for j, p in zip(faces[i], t):
            nuevos.setdefault(tuple(p.round(8)), int(j))
        recortes = [t]
        for ns, ds in regiones_cara:
            fragmentos = []
            for resto in recortes:
                for normal, nivel in zip(ns, ds):
                    if len(resto) < 3:
                        break
                    resto, fuera = partir(resto, normal, nivel)
                    if len(fuera) >= 3:
                        fragmentos.append(fuera)
            recortes = fragmentos
        for poly in recortes:
            ids = [indice(p) for p in poly]
            for k in range(1, len(ids) - 1):
                cara = (ids[0], ids[k], ids[k + 1])
                if (
                    len(set(cara)) == 3
                    and np.linalg.norm(
                        np.cross(poly[k] - poly[0], poly[k + 1] - poly[0])
                    )
                    > 1e-12
                ):
                    caras.append(cara)
                    tonos.append(materiales[i])
    m.clear_geometry()
    m.from_pydata(vertices, [], caras)
    m.polygons.foreach_set("material_index", tonos)
    m.update()
