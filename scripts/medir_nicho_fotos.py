"""Cámaras y nicho común de los vanos del tambor en varias fotos (paso 2 de 2).

Lee los bordes de `datos/bordes_celosias_<clave>.json` (paso 1,
`scripts/detectar_celosias.py`) y ajusta a la vez:

- una cámara por foto: focal, orientación y posición (7 incógnitas; 8 con
  `--distorsion`, que añade la distorsión radial k1);
- un nicho común a todos los vanos: eje ±a respecto al centro de la cara,
  semiancho h de la celosía, profundidad d de la celosía tras el plano del
  muro y semiancho hn de la boca del nicho en ese plano (hn > h es derrame).

Geometría conocida: octógono de apotema APOTEMA (la del modelo, leída de la
sección AA-415_23). En cada foto, caras A, B, C consecutivas; B a 0°, A a
+45°, C a -45°, cada foto en su propio sistema (el octógono es simétrico). El
pie visible de cada celosía es el canto del alféizar: una recta horizontal en
el plano del muro, común a los dos vanos de una cara, a z = 0. Los lados son
verticales. Para cada lado, la celosía se ve si la cámara queda del lado
interior del plano de la jamba; si no, el borde visible es el canto de la
jamba en el plano del muro.

Supuestos: cámara estenopeica, punto principal en el centro, píxel cuadrado;
canto del alféizar en el plano del muro; nichos iguales y simétricos; jambas
planas. La estabilidad se contrasta con cada foto sola y quitando una cara.

Uso: OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/medir_nicho_fotos.py trip82 bruchez
"""

import argparse
import hashlib
import json
from math import radians
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
SALIDA = ROOT / "datos/medida_nicho_fotos.json"
APOTEMA = 3.8657066822052  # web/modelos/dos-hermanas.json, apotema_m
ANGULO_CARA = {"A": 45.0, "B": 0.0, "C": -45.0}
MODELO = dict(a=0.59, h=0.265, d_celosia=0.09)  # scripts/hiladas_ventanas.py
SOBRE_SUELO = 9.926  # datos/alzado_sala.json, pie_ventanas_tambor
NOMBRES_NICHO = ("a", "h", "d", "hn")


def ejes(cara):
    f = radians(ANGULO_CARA[cara])
    return np.array([np.cos(f), np.sin(f), 0.0]), np.array([-np.sin(f), np.cos(f), 0.0])


class Foto:
    def __init__(self, clave, distorsion):
        self.clave = clave
        self.ruta_bordes = ROOT / f"datos/bordes_celosias_{clave}.json"
        self.datos = json.loads(self.ruta_bordes.read_text())
        lect = ROOT / self.datos["lecturas"]
        if self.datos["sha256_lecturas"] != hashlib.sha256(lect.read_bytes()).hexdigest():
            raise SystemExit(f"{clave}: bordes desfasados de las lecturas; repetir el paso 1")
        self.excluir = json.loads(lect.read_text()).get("excluir", {})
        with Image.open(ROOT / self.datos["foto"]) as im:
            self.ancho, self.alto = im.size
        self.c = np.array([self.ancho / 2, self.alto / 2])
        self.semidiagonal = 0.5 * np.hypot(self.ancho, self.alto)
        self.nc = 8 if distorsion else 7

    def camara(self, x):
        return x[0], Rotation.from_rotvec(x[1:4]).as_matrix(), x[4:7]

    def k1(self, x):
        return x[7] if self.nc == 8 else 0.0

    def proyectar(self, x, P):
        f, R, C = self.camara(x)
        Pc = (np.atleast_2d(P) - C) @ R.T
        return np.stack([f * Pc[:, 0] / Pc[:, 2], f * Pc[:, 1] / Pc[:, 2]], 1) + self.c

    def corregir(self, pts, x):
        q = (np.asarray(pts, float) - self.c) / self.semidiagonal
        return self.c + q / (1 + self.k1(x) * (q**2).sum(1, keepdims=True)) * self.semidiagonal

    def recta(self, x, P0, P1):
        p0, p1 = self.proyectar(x, np.array([P0, P1]))
        l = np.cross([*p0, 1.0], [*p1, 1.0])
        return l / np.linalg.norm(l[:2])

    def lados(self, x, cara, vano, nicho):
        a, h, d, hn = nicho
        n, t = ejes(cara)
        _, _, C = self.camara(x)
        s0 = a if vano == 1 else -a
        cam = (C @ n, C @ t)
        cruz = lambda o, p, q: (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
        out = []
        for sig in (1, -1):
            Q = (APOTEMA + d, s0 + sig * h)
            F = (APOTEMA, s0 + sig * hn)
            I = (APOTEMA + d, s0)
            visible = np.sign(cruz(Q, F, cam)) == np.sign(cruz(Q, F, I))
            r, s = Q if visible else F
            base = r * n + s * t
            (p,) = self.proyectar(x, base)
            out.append((p[0], self.recta(x, base, base + [0, 0, 1.0]), "celosia" if visible else "jamba"))
        out.sort(key=lambda o: o[0])
        return dict(izquierdo=out[0][1:], derecho=out[1][1:])

    def residuos(self, x, nicho, caras, por_borde=False):
        res, detalle = [], {}
        for nombre, v in self.datos["vanos"].items():
            if v["cara"] not in caras:
                continue
            n, t = ejes(v["cara"])
            b = v["bordes"]
            lados = self.lados(x, v["cara"], v["vano"], nicho)
            for lado in ("inferior", "izquierdo", "derecho"):
                if b.get(lado) is None or f"{nombre}.{lado}" in self.excluir:
                    continue
                if lado == "inferior":
                    l = self.recta(x, APOTEMA * n, APOTEMA * n + t)
                else:
                    l = lados[lado][0]
                pts = self.corregir(b[lado]["puntos"], x)
                e = np.c_[pts, np.ones(len(pts))] @ l
                res.extend(e.tolist())
                if por_borde:
                    detalle[f"{nombre}.{lado}"] = dict(
                        media_px=round(float(e.mean()), 2),
                        desv_px=round(float(e.std()), 2),
                        tipo=lados[lado][1] if lado != "inferior" else "alfeizar",
                    )
        return (res, detalle) if por_borde else res

    def inicios(self):
        salida = []
        for f in (0.6, 0.9, 1.3, 1.8):
            for cx in (-3.0, -1.0, 1.0):
                for cz in (-9.0, -7.5):
                    C = np.array([cx, 0.0, cz])
                    eje = np.array([APOTEMA, 0.0, 0.3]) - C
                    eje /= np.linalg.norm(eje)
                    abajo = np.array([0, 0, -1.0]) + eje * eje[2]
                    abajo /= np.linalg.norm(abajo)
                    R = np.stack([np.cross(abajo, eje), abajo, eje])
                    x = np.r_[f * self.ancho, Rotation.from_matrix(R).as_rotvec(), C]
                    salida.append(np.r_[x, 0.0] if self.nc == 8 else x)
        return salida


def residuos_conjuntos(z, fotos, caras):
    res, i = [], 0
    nicho = z[-4:]
    for foto in fotos:
        x = z[i : i + foto.nc]
        i += foto.nc
        res.extend(foto.residuos(x, nicho, caras[foto.clave]))
    a, h, d, hn = nicho
    res.extend([100 * min(0.0, hn - h), 100 * min(0.0, d)])
    return np.array(res)


def ajustar(fotos, caras, z0=None):
    if z0 is not None:
        candidatos = [z0]
    else:
        # Cámara de cada foto por separado con nicho del modelo, luego conjunto.
        xs = []
        for foto in fotos:
            mejor = None
            for x0 in foto.inicios():
                for nicho0 in ([0.59, 0.265, 0.09, 0.265], [0.57, 0.29, 0.35, 0.33]):
                    r = least_squares(
                        lambda x: residuos_conjuntos(np.r_[x, nicho0], [foto], caras),
                        x0, x_scale="jac", max_nfev=2000,
                    )
                    if mejor is None or r.cost < mejor.cost:
                        mejor = r
            xs.append(mejor.x)
        candidatos = [np.r_[np.concatenate(xs), n0] for n0 in ([0.59, 0.265, 0.09, 0.265], [0.57, 0.29, 0.35, 0.33], [0.57, 0.29, 0.25, 0.29])]
    mejor = None
    for z in candidatos:
        r = least_squares(residuos_conjuntos, z, args=(fotos, caras), x_scale="jac", max_nfev=6000)
        if mejor is None or r.cost < mejor.cost:
            mejor = r
    return mejor


def resumen(r, fotos, caras):
    res = residuos_conjuntos(r.x, fotos, caras)[:-2]
    J = r.jac[:-2]
    try:
        cov = np.linalg.inv(J.T @ J) * np.sum(res**2) / max(1, len(res) - len(r.x))
        sigma = np.sqrt(np.diag(cov))
    except np.linalg.LinAlgError:
        sigma = np.full(len(r.x), np.nan)
    nicho = r.x[-4:]
    out = dict(
        caras={k: sorted(v) for k, v in caras.items()},
        rms_px=float(np.sqrt(np.mean(res**2))),
        n_puntos=int(len(res)),
        nicho_m=dict(zip(NOMBRES_NICHO, nicho.round(4).tolist())),
        sigma_nicho_m=dict(zip(NOMBRES_NICHO, sigma[-4:].round(4).tolist())),
        camaras={},
    )
    i = 0
    for foto in fotos:
        x = r.x[i : i + foto.nc]
        f, R, C = foto.camara(x)
        _, detalle = foto.residuos(x, nicho, caras[foto.clave], por_borde=True)
        out["camaras"][foto.clave] = dict(
            focal_px=round(float(f), 1),
            posicion_m=C.round(3).tolist(),
            # Mundo -> cámara; cámara con x derecha, y abajo, z adelante.
            rotacion=R.round(8).tolist(),
            imagen_px=[foto.ancho, foto.alto],
            altura_sobre_suelo_m=round(float(SOBRE_SUELO + C[2]), 3),
            k1=float(foto.k1(x)),
            bordes=detalle,
        )
        i += foto.nc
    return out


def corto(s):
    return dict(rms=round(s["rms_px"], 2), nicho=s["nicho_m"], camaras={k: (v["focal_px"], v["posicion_m"]) for k, v in s["camaras"].items()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("claves", nargs="+")
    ap.add_argument("--distorsion", action="store_true")
    args = ap.parse_args()
    fotos = [Foto(c, args.distorsion) for c in args.claves]
    todas = {f.clave: {"A", "B", "C"} for f in fotos}
    r = ajustar(fotos, todas)
    principal = resumen(r, fotos, todas)
    print("conjunto", corto(principal))
    variantes = {}
    if len(fotos) > 1:
        for foto in fotos:
            rs = ajustar([foto], {foto.clave: todas[foto.clave]})
            variantes[f"solo_{foto.clave}"] = resumen(rs, [foto], {foto.clave: todas[foto.clave]})
            print(f"solo_{foto.clave}", corto(variantes[f"solo_{foto.clave}"]))
    for foto in fotos:
        for quitar in ("A", "B", "C"):
            caras = {k: (v - {quitar} if k == foto.clave else v) for k, v in todas.items()}
            rv = ajustar(fotos, caras, z0=r.x)
            variantes[f"{foto.clave}_sin_{quitar}"] = resumen(rv, fotos, caras)
            print(f"{foto.clave}_sin_{quitar}", corto(variantes[f"{foto.clave}_sin_{quitar}"]))
    ds = [v["nicho_m"]["d"] for v in variantes.values()]
    SALIDA.write_text(
        json.dumps(
            dict(
                fotos=args.claves,
                distorsion=args.distorsion,
                sha256_script=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                sha256_bordes={f.clave: hashlib.sha256(f.ruta_bordes.read_bytes()).hexdigest() for f in fotos},
                apotema_m=APOTEMA,
                modelo_vigente_m=MODELO,
                principal=principal,
                variantes=variantes,
                intervalo_d_variantes_m=[min(ds + [principal["nicho_m"]["d"]]), max(ds + [principal["nicho_m"]["d"]])],
            ),
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
