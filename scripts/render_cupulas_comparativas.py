#!/usr/bin/env python3
"""Renderiza las cupulas comparativas y compone laminas de alta resolucion.

No usa un motor externo para la geometria: rasteriza con z-buffer el mismo
artefacto que consume el visor. ``rsvg-convert`` solo compone la tipografia de
las laminas finales a partir de los PNG ya renderizados.
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import shutil
import struct
import subprocess
import zlib
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "datos" / "ordenes_sinteticos.json"
RENDERS = RAIZ / "renders"
VISTAS = {
    "general": (34.0, 28.0),
    "intrados": (24.0, -48.0),
}
PALETA = (
    (239, 231, 216),
    (229, 218, 200),
    (216, 202, 181),
    (202, 184, 158),
    (186, 164, 133),
)
FONDO = (234, 229, 219)
LUZ = (0.35, -0.48, 0.80)


def racional(par: list[int]) -> float:
    return par[0] / par[1]


def escribir_png(ruta: Path, ancho: int, alto: int, pixeles: bytearray) -> None:
    raw = b"".join(
        b"\x00" + bytes(pixeles[y * ancho * 3 : (y + 1) * ancho * 3])
        for y in range(alto)
    )

    def chunk(tipo: bytes, datos: bytes) -> bytes:
        contenido = tipo + datos
        return (
            struct.pack(">I", len(datos))
            + contenido
            + struct.pack(">I", zlib.crc32(contenido))
        )

    ruta.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 8))
        + chunk(b"IEND", b"")
    )


def malla(orden: dict) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int, int]]]:
    """Convierte cada pano escalonado en un solido cerrado triangulado."""
    vertices: list[tuple[float, float, float]] = []
    caras: list[tuple[int, int, int, int]] = []
    for celda in orden["celdas"]:
        puntos = celda["vertices_xy"]
        superior = racional(celda["cota_superior"])
        inferior = racional(celda["cota_inferior"])
        base = len(vertices)
        vertices.extend((x, y, superior) for x, y in puntos)
        vertices.extend((x, y, inferior) for x, y in puntos)
        n = len(puntos)
        color = celda["corona"] - 1
        for i in range(1, n - 1):
            caras.append((base, base + i, base + i + 1, color))
            caras.append((base + n, base + n + i + 1, base + n + i, color))
        for i in range(n):
            siguiente = (i + 1) % n
            caras.append((base + n + i, base + n + siguiente, base + siguiente, color))
            caras.append((base + n + i, base + siguiente, base + i, color))
    return vertices, caras


def fondo_gradual(ancho: int, alto: int, con_sombra: bool) -> bytearray:
    pixeles = bytearray(ancho * alto * 3)
    for y in range(alto):
        ny = (y - alto * 0.48) / alto
        for x in range(ancho):
            nx = (x - ancho * 0.5) / ancho
            borde = min(1.0, math.sqrt(nx * nx + ny * ny) * 1.45)
            factor = 1.0 - 0.055 * borde
            if con_sombra:
                ex = (x - ancho * 0.50) / (ancho * 0.30)
                ey = (y - alto * 0.72) / (alto * 0.075)
                distancia = ex * ex + ey * ey
                if distancia < 1:
                    factor -= 0.075 * (1 - distancia) ** 2
            indice = (y * ancho + x) * 3
            pixeles[indice : indice + 3] = bytes(
                max(0, min(255, round(canal * factor))) for canal in FONDO
            )
    return pixeles


def renderizar(
    vertices: list[tuple[float, float, float]],
    caras: list[tuple[int, int, int, int]],
    ruta: Path,
    lado: int,
    azimut: float,
    elevacion: float,
) -> None:
    ca, sa = math.cos(math.radians(azimut)), math.sin(math.radians(azimut))
    ce, se = math.cos(math.radians(elevacion)), math.sin(math.radians(elevacion))

    def camara(punto: tuple[float, float, float]) -> tuple[float, float, float]:
        x, y, z = punto
        x, y = x * ca - y * sa, x * sa + y * ca
        y, z = y * ce - z * se, y * se + z * ce
        return x, y, z

    transformados = [camara(vertice) for vertice in vertices]
    xs = [punto[0] for punto in transformados]
    ys = [punto[2] for punto in transformados]
    centro_x = (min(xs) + max(xs)) / 2
    centro_y = (min(ys) + max(ys)) / 2
    escala = 0.80 * min(
        lado / (max(xs) - min(xs)), lado / (max(ys) - min(ys))
    )

    def proyectar(punto: tuple[float, float, float]) -> tuple[float, float, float]:
        return (
            lado / 2 + (punto[0] - centro_x) * escala,
            lado / 2 - (punto[2] - centro_y) * escala,
            punto[1],
        )

    norma_luz = math.sqrt(sum(componente * componente for componente in LUZ))
    luz = tuple(componente / norma_luz for componente in LUZ)
    pixeles = fondo_gradual(lado, lado, elevacion > 0)
    zbuffer = [1e30] * (lado * lado)

    for ia, ib, ic, indice_color in caras:
        a, b, c = vertices[ia], vertices[ib], vertices[ic]
        ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        longitud = math.sqrt(nx * nx + ny * ny + nz * nz)
        if longitud == 0:
            continue
        incidencia = abs((nx * luz[0] + ny * luz[1] + nz * luz[2]) / longitud)
        brillo = 0.50 + 0.50 * incidencia**0.82
        base = PALETA[indice_color]
        color = tuple(max(0, min(255, round(canal * brillo))) for canal in base)
        p0, p1, p2 = (proyectar(transformados[i]) for i in (ia, ib, ic))
        minx = max(0, int(min(p0[0], p1[0], p2[0])))
        maxx = min(lado - 1, int(max(p0[0], p1[0], p2[0])) + 1)
        miny = max(0, int(min(p0[1], p1[1], p2[1])))
        maxy = min(lado - 1, int(max(p0[1], p1[1], p2[1])) + 1)
        determinante = (
            (p1[1] - p2[1]) * (p0[0] - p2[0])
            + (p2[0] - p1[0]) * (p0[1] - p2[1])
        )
        if abs(determinante) < 1e-12:
            continue
        for py in range(miny, maxy + 1):
            for px in range(minx, maxx + 1):
                l0 = (
                    (p1[1] - p2[1]) * (px - p2[0])
                    + (p2[0] - p1[0]) * (py - p2[1])
                ) / determinante
                if l0 < 0:
                    continue
                l1 = (
                    (p2[1] - p0[1]) * (px - p2[0])
                    + (p0[0] - p2[0]) * (py - p2[1])
                ) / determinante
                if l1 < 0:
                    continue
                l2 = 1 - l0 - l1
                if l2 < 0:
                    continue
                profundidad = l0 * p0[2] + l1 * p1[2] + l2 * p2[2]
                indice = py * lado + px
                if profundidad < zbuffer[indice]:
                    zbuffer[indice] = profundidad
                    pixeles[indice * 3 : indice * 3 + 3] = bytes(color)
    escribir_png(ruta, lado, lado, pixeles)


def imagen_embebida(ruta: Path) -> str:
    return base64.b64encode(ruta.read_bytes()).decode("ascii")


def lamina(documento: dict, vista: str, imagenes: list[Path]) -> tuple[Path, Path]:
    titulo = "Tres familias de trazado · vista general" if vista == "general" else "Tres familias de trazado · lectura desde el intradós"
    subtitulo = (
        "La misma composición contemporánea de cinco coronas; solo cambia el ritmo angular."
    )
    tarjetas = []
    for indice, (orden, imagen) in enumerate(zip(documento["ordenes"], imagenes, strict=True)):
        x = 150 + indice * 1100
        datos = imagen_embebida(imagen)
        tarjetas.append(
            f'<g transform="translate({x} 285)">'
            '<rect width="1020" height="1120" rx="14" fill="#f7f3e9" stroke="#d7d0c2"/>'
            f'<image x="10" y="10" width="1000" height="1000" href="data:image/png;base64,{datos}"/>'
            f'<text x="42" y="1058" font-family="Georgia,serif" font-size="36" fill="#29322e">{orden["nombre"]}</text>'
            f'<text x="42" y="1098" font-family="sans-serif" font-size="22" fill="#68716c">{orden["numero_sectores"]} sectores · {orden["numero_coronas"]} coronas · {orden["numero_celdas"]} paños</text>'
            '</g>'
        )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="3600" height="1600" viewBox="0 0 3600 1600">'
        '<rect width="3600" height="1600" fill="#eae5db"/>'
        '<text x="150" y="105" font-family="Georgia,serif" font-size="64" fill="#252b28">'
        f'{titulo}</text>'
        '<text x="150" y="165" font-family="sans-serif" font-size="28" fill="#68716c">'
        f'{subtitulo}</text>'
        + "".join(tarjetas)
        + '<text x="150" y="1515" font-family="sans-serif" font-size="23" fill="#795b4c">Comparación contemporánea en unidades relativas · no reproduce un monumento ni una tipología histórica concreta</text>'
        '<text x="3450" y="1515" text-anchor="end" font-family="sans-serif" font-size="20" fill="#737974">Granada · decisión 0014</text>'
        '</svg>'
    )
    ruta_svg = RENDERS / f"cupulas_comparativas_{vista}.svg"
    ruta_png = RENDERS / f"cupulas_comparativas_{vista}.png"
    ruta_svg.write_text(svg, encoding="utf-8")
    conversor = shutil.which("rsvg-convert")
    if conversor is None:
        raise RuntimeError("rsvg-convert es necesario para componer la lamina PNG")
    subprocess.run(
        [conversor, "-w", "3600", "-h", "1600", "-o", str(ruta_png), str(ruta_svg)],
        check=True,
    )
    return ruta_svg, ruta_png


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lado", type=int, default=1200)
    parser.add_argument("--vista", choices=["general", "intrados", "todas"], default="todas")
    args = parser.parse_args()
    if args.lado < 600:
        raise ValueError("--lado debe ser al menos 600 para una lamina legible")
    documento = json.loads(DATOS.read_text(encoding="utf-8"))
    vistas = tuple(VISTAS) if args.vista == "todas" else (args.vista,)
    for vista in vistas:
        imagenes = []
        azimut, elevacion = VISTAS[vista]
        for orden in documento["ordenes"]:
            vertices, caras = malla(orden)
            salida = RENDERS / f"cupula_comparativa_{orden['numero_sectores']}_{vista}.png"
            renderizar(vertices, caras, salida, args.lado, azimut, elevacion)
            imagenes.append(salida)
            print(f"{orden['numero_sectores']} sectores · {vista}: {salida}")
        _, salida_lamina = lamina(documento, vista, imagenes)
        print(f"lamina · {vista}: {salida_lamina}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
