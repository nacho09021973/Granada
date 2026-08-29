#!/usr/bin/env python3
"""Rasteriza la malla exportada para poder MIRARLA.

Existe por la cautela 2 de `PROXIMOS-PASOS.md`: el primer render del proyecto
salio mal y se descubrio tarde porque nunca se comparo contra la imagen. Este
script hace ese control reproducible.

Ya ha servido: destapo dos defectos que los controles numericos no veian
-huecos abiertos entre bandas y puas por triangular caras concavas en abanico-,
ninguno de los cuales alteraba el rango de cotas ni el residuo frente al cono.

Sin dependencias: z-buffer y sombreado plano con la biblioteca estandar.
"""

from __future__ import annotations

import argparse
import math
import struct
import zlib
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
MALLA = RAIZ / "renders" / "cupula_aproximada.obj"
VISTAS = {
    "picada": (35.0, 28.0),
    "desde_abajo": (20.0, -55.0),
}
def leer_obj(ruta):
    V, F = [], []
    for ln in open(ruta):
        if ln.startswith('v '): V.append(tuple(map(float, ln.split()[1:4])))
        elif ln.startswith('f '): F.append(tuple(int(p.split('/')[0])-1 for p in ln.split()[1:4]))
    return V, F

def escribir_png(ruta, W, H, buf):
    raw = b''.join(b'\x00' + bytes(buf[y*W*3:(y+1)*W*3]) for y in range(H))
    def ch(t, d):
        c = t+d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c))
    open(ruta,'wb').write(b'\x89PNG\r\n\x1a\n'
        + ch(b'IHDR', struct.pack('>IIBBBBB', W,H,8,2,0,0,0))
        + ch(b'IDAT', zlib.compress(bytes(raw),6)) + ch(b'IEND', b''))

def render(V, F, ruta, W=900, H=900, azim=35.0, elev=25.0, fondo=(18, 18, 20), luz=(0.4, 0.5, 0.75)):
    ca, sa = math.cos(math.radians(azim)), math.sin(math.radians(azim))
    ce, se = math.cos(math.radians(elev)), math.sin(math.radians(elev))
    def cam(p):
        x, y, z = p
        x, y = x*ca - y*sa, x*sa + y*ca
        y, z = y*ce - z*se, y*se + z*ce
        return (x, y, z)
    P = [cam(v) for v in V]
    xs=[p[0] for p in P]; ys=[p[2] for p in P]
    cx,cy=(min(xs)+max(xs))/2,(min(ys)+max(ys))/2
    esc = 0.86*min(W/(max(xs)-min(xs)), H/(max(ys)-min(ys)))
    proj = lambda p: (W/2+(p[0]-cx)*esc, H/2-(p[2]-cy)*esc, p[1])
    n=math.sqrt(sum(c*c for c in luz)); luz=tuple(c/n for c in luz)
    buf = bytearray()
    for _ in range(W*H): buf += bytes(fondo)
    zb = [1e30]*(W*H)
    for f in F:
        a,b,c = (V[i] for i in f)
        ux,uy,uz = b[0]-a[0], b[1]-a[1], b[2]-a[2]
        vx,vy,vz = c[0]-a[0], c[1]-a[1], c[2]-a[2]
        nx,ny,nz = uy*vz-uz*vy, uz*vx-ux*vz, ux*vy-uy*vx
        ln = math.sqrt(nx*nx+ny*ny+nz*nz)
        if ln == 0: continue
        d = abs((nx*luz[0]+ny*luz[1]+nz*luz[2])/ln)
        col = tuple(min(255, int(28 + 210*(0.18+0.82*d**0.9))) for _ in range(3))
        p0,p1,p2 = (proj(P[i]) for i in f)
        minx=max(0,int(min(p0[0],p1[0],p2[0]))); maxx=min(W-1,int(max(p0[0],p1[0],p2[0]))+1)
        miny=max(0,int(min(p0[1],p1[1],p2[1]))); maxy=min(H-1,int(max(p0[1],p1[1],p2[1]))+1)
        if minx>maxx or miny>maxy: continue
        det=(p1[1]-p2[1])*(p0[0]-p2[0])+(p2[0]-p1[0])*(p0[1]-p2[1])
        if abs(det)<1e-12: continue
        for py in range(miny,maxy+1):
            for px in range(minx,maxx+1):
                l0=((p1[1]-p2[1])*(px-p2[0])+(p2[0]-p1[0])*(py-p2[1]))/det
                if l0<0: continue
                l1=((p2[1]-p0[1])*(px-p2[0])+(p0[0]-p2[0])*(py-p2[1]))/det
                if l1<0: continue
                l2=1-l0-l1
                if l2<0: continue
                z=l0*p0[2]+l1*p1[2]+l2*p2[2]
                i=py*W+px
                if z<zb[i]:
                    zb[i]=z; buf[i*3:i*3+3]=bytes(col)
    escribir_png(ruta, W, H, buf)
    return ruta


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--malla", type=Path, default=MALLA)
    parser.add_argument("--vista", choices=sorted(VISTAS) + ["todas"], default="todas")
    parser.add_argument("--lado", type=int, default=900)
    args = parser.parse_args()

    vertices, caras = leer_obj(args.malla)
    nombres = sorted(VISTAS) if args.vista == "todas" else [args.vista]
    for nombre in nombres:
        azimut, elevacion = VISTAS[nombre]
        salida = RAIZ / "renders" / f"cupula_{nombre}.png"
        render(vertices, caras, salida, args.lado, args.lado, azimut, elevacion)
        print(f"{nombre}: {len(caras)} triangulos -> {salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
