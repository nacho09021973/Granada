#!/usr/bin/env python3
"""Digitaliza la red completa de medinas de la figura 128.

La figura contrapone la propuesta de Ferrer Perez-Blanco (mitad superior) al
dibujo de Jones y Goury (mitad inferior). Este script usa solamente la primera
y completa la planta por la simetria especular D8 medida en la cupula.

Dependencias de analisis, fuera del nucleo ``granada/``: Pillow, NumPy, SciPy
y scikit-image. ``pdfimages`` (Poppler) extrae la imagen embebida de la tesis.
La figura original no se copia al repositorio; la salida es geometria derivada.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import tempfile
from collections import Counter, deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage.morphology import thin


PAGINA_PDF = 236
DIMENSION_FIGURA = (547, 546)
EJE_ESPEJO_Y_PX = 273.5
UMBRAL = 200
DILATACION_NUDOS = 3
TOLERANCIA_SIMPLIFICACION_PX = 2.0

# Registro ya validado contra la ortoimagen. Las coordenadas resultantes estan
# en metros y mantienen y positiva hacia la mitad inferior de la planta.
CENTRO_X_PX = 273.44662103
CENTRO_Y_PX = 273.01374651
PX_POR_METRO_X = 72.28971516
PX_POR_METRO_Y = 72.37311179

# Octogono interior: recorta la linea punteada editorial del contorno, pero
# conserva los 24 extremos de medina que llegan al borde.
OCTOGONO_INTERIOR = (
    (166, 9),
    (380, 9),
    (537, 166),
    (537, 380),
    (380, 537),
    (166, 537),
    (9, 380),
    (9, 166),
)
VECINOS_8 = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)


def sha256_archivo(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def sha256_pixeles(imagen: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(imagen).tobytes()).hexdigest()


def extraer_figura(tesis: Path, destino: Path) -> Path:
    """Extrae y selecciona la imagen principal de la pagina 236."""
    prefijo = destino / "figura128"
    subprocess.run(
        [
            "pdfimages",
            "-f",
            str(PAGINA_PDF),
            "-l",
            str(PAGINA_PDF),
            "-png",
            str(tesis),
            str(prefijo),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    candidatos = sorted(destino.glob("figura128-*.png"))
    if not candidatos:
        raise RuntimeError("pdfimages no extrajo ninguna imagen de la pagina 236")
    dimensiones = []
    for ruta in candidatos:
        with Image.open(ruta) as imagen:
            dimensiones.append((imagen.width * imagen.height, imagen.size, ruta))
    _, dimension, figura = max(dimensiones)
    if dimension != DIMENSION_FIGURA:
        raise RuntimeError(
            f"imagen principal inesperada: {dimension}; se esperaba {DIMENSION_FIGURA}"
        )
    return figura


def completar_propuesta(gris: np.ndarray) -> np.ndarray:
    """Refleja la mitad superior sin incorporar el dibujo inferior historico."""
    if gris.shape != (DIMENSION_FIGURA[1], DIMENSION_FIGURA[0]):
        raise ValueError(f"dimension inesperada: {gris.shape}")
    propuesta = np.full_like(gris, 255)
    primera_fila_inferior = math.ceil(EJE_ESPEJO_Y_PX)
    propuesta[:primera_fila_inferior] = gris[:primera_fila_inferior]
    for y in range(primera_fila_inferior, gris.shape[0]):
        origen = round(2 * EJE_ESPEJO_Y_PX - y)
        propuesta[y] = gris[origen]
    return propuesta


def mascara_octogono(forma: tuple[int, int]) -> np.ndarray:
    imagen = Image.new("1", (forma[1], forma[0]), 0)
    ImageDraw.Draw(imagen).polygon(OCTOGONO_INTERIOR, fill=1)
    return np.asarray(imagen, dtype=bool)


def binarizar_red(propuesta: np.ndarray, umbral: int) -> np.ndarray:
    """Aisla el componente conectado principal dentro del contorno."""
    binaria = (propuesta < umbral) & mascara_octogono(propuesta.shape)
    etiquetas, _ = ndi.label(binaria, np.ones((3, 3), dtype=np.uint8))
    tamanos = np.bincount(etiquetas.ravel())
    tamanos[0] = 0
    if not tamanos.any():
        raise RuntimeError("el umbral no encontro la red")
    return etiquetas == int(np.argmax(tamanos))


def simplificar_rdp(puntos: np.ndarray, tolerancia: float) -> np.ndarray:
    """Ramer-Douglas-Peucker para conservar los giros reales del trazado."""
    if len(puntos) < 3:
        return puntos
    inicio = puntos[0]
    fin = puntos[-1]
    vector = fin - inicio
    norma = np.linalg.norm(vector)
    if norma == 0:
        distancias = np.linalg.norm(puntos - inicio, axis=1)
    else:
        delta = puntos - inicio
        distancias = np.abs(
            vector[0] * delta[:, 1] - vector[1] * delta[:, 0]
        ) / norma
    indice = int(np.argmax(distancias))
    if distancias[indice] <= tolerancia:
        return np.vstack((inicio, fin))
    izquierda = simplificar_rdp(puntos[: indice + 1], tolerancia)
    derecha = simplificar_rdp(puntos[indice:], tolerancia)
    return np.vstack((izquierda[:-1], derecha))


def camino_entre_regiones(
    pixeles: set[tuple[int, int]],
    origenes: set[tuple[int, int]],
    destinos: set[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Ordena un tramo de esqueleto por recorrido en anchura."""
    cola = deque(origenes)
    anterior: dict[tuple[int, int], tuple[int, int] | None] = {
        punto: None for punto in origenes
    }
    final = None
    while cola and final is None:
        punto = cola.popleft()
        if punto in destinos:
            final = punto
            break
        for dy, dx in VECINOS_8:
            vecino = (punto[0] + dy, punto[1] + dx)
            if vecino in pixeles and vecino not in anterior:
                anterior[vecino] = punto
                cola.append(vecino)
    if final is None:
        raise RuntimeError("tramo desconectado entre dos regiones de nudo")
    camino = []
    punto: tuple[int, int] | None = final
    while punto is not None:
        camino.append(punto)
        punto = anterior[punto]
    camino.reverse()
    return camino


def extraer_grafo(
    propuesta: np.ndarray,
    *,
    umbral: int = UMBRAL,
    dilatacion: int = DILATACION_NUDOS,
    tolerancia: float = TOLERANCIA_SIMPLIFICACION_PX,
) -> tuple[list[np.ndarray], list[tuple[int, int]]]:
    """Convierte la linea raster en nudos y tramos rectos."""
    esqueleto = thin(binarizar_red(propuesta, umbral))
    grado_pixel = ndi.convolve(
        esqueleto.astype(np.uint8),
        np.ones((3, 3), dtype=np.uint8),
        mode="constant",
    ) - esqueleto
    nucleos = esqueleto & (grado_pixel != 2)
    mascara_nudos = esqueleto & ndi.binary_dilation(
        nucleos,
        iterations=dilatacion,
        structure=np.ones((3, 3), dtype=bool),
    )
    etiquetas_nudos, numero_nudos = ndi.label(
        mascara_nudos, np.ones((3, 3), dtype=np.uint8)
    )
    vertices: list[np.ndarray] = []
    for etiqueta in range(1, numero_nudos + 1):
        yy, xx = np.where(etiquetas_nudos == etiqueta)
        vertices.append(np.array((xx.mean(), yy.mean())))

    mascara_tramos = esqueleto & ~mascara_nudos
    etiquetas_tramos, numero_tramos = ndi.label(
        mascara_tramos, np.ones((3, 3), dtype=np.uint8)
    )
    polilineas = []
    for etiqueta in range(1, numero_tramos + 1):
        yy, xx = np.where(etiquetas_tramos == etiqueta)
        pixeles = set(zip(yy.tolist(), xx.tolist()))
        contactos: dict[int, set[tuple[int, int]]] = {}
        for y, x in pixeles:
            for dy, dx in VECINOS_8:
                ny, nx = y + dy, x + dx
                if 0 <= ny < esqueleto.shape[0] and 0 <= nx < esqueleto.shape[1]:
                    nudo = int(etiquetas_nudos[ny, nx])
                    if nudo:
                        contactos.setdefault(nudo - 1, set()).add((y, x))
        if len(contactos) != 2:
            raise RuntimeError(
                f"tramo {etiqueta} toca {len(contactos)} nudos; "
                "revise umbral y dilatacion"
            )
        inicio, fin = sorted(contactos)
        camino = camino_entre_regiones(
            pixeles, contactos[inicio], contactos[fin]
        )
        puntos = np.vstack(
            (
                vertices[inicio],
                np.asarray([(x, y) for y, x in camino]),
                vertices[fin],
            )
        )
        polilineas.append((inicio, fin, simplificar_rdp(puntos, tolerancia)))

    aristas = []
    for inicio, fin, puntos in polilineas:
        indices = [inicio]
        for punto in puntos[1:-1]:
            indices.append(len(vertices))
            vertices.append(punto)
        indices.append(fin)
        for a, b in zip(indices, indices[1:]):
            if np.linalg.norm(vertices[a] - vertices[b]) >= 2:
                aristas.append((a, b))

    # Un giro puede coincidir con un nudo ya detectado en un tramo adyacente.
    unicos: list[np.ndarray] = []
    remapeo = {}
    for indice, punto in enumerate(vertices):
        coincidencia = next(
            (
                nuevo
                for nuevo, existente in enumerate(unicos)
                if np.linalg.norm(punto - existente) < 1.0
            ),
            None,
        )
        if coincidencia is None:
            coincidencia = len(unicos)
            unicos.append(punto)
        remapeo[indice] = coincidencia
    aristas_unicas = sorted(
        {
            tuple(sorted((remapeo[a], remapeo[b])))
            for a, b in aristas
            if remapeo[a] != remapeo[b]
        }
    )
    return unicos, aristas_unicas


def numero_componentes(numero_vertices: int, aristas: list[tuple[int, int]]) -> int:
    adyacencia = [set() for _ in range(numero_vertices)]
    for a, b in aristas:
        adyacencia[a].add(b)
        adyacencia[b].add(a)
    pendientes = set(range(numero_vertices))
    componentes = 0
    while pendientes:
        componentes += 1
        cola = [pendientes.pop()]
        while cola:
            for vecino in adyacencia[cola.pop()]:
                if vecino in pendientes:
                    pendientes.remove(vecino)
                    cola.append(vecino)
    return componentes


def controles_grafo(
    vertices: list[np.ndarray], aristas: list[tuple[int, int]]
) -> dict[str, object]:
    grados = Counter(indice for arista in aristas for indice in arista)
    desviaciones = []
    longitudes = []
    for a, b in aristas:
        dx, dy = vertices[b] - vertices[a]
        angulo = math.degrees(math.atan2(dy, dx)) % 180
        desviaciones.append(min(abs(angulo - 45 * k) for k in range(5)))
        longitudes.append(math.hypot(dx, dy))
    componentes = numero_componentes(len(vertices), aristas)
    return {
        "nudos": len(vertices),
        "aristas": len(aristas),
        "componentes_conexas": componentes,
        "numero_ciclos_independientes": len(aristas) - len(vertices) + componentes,
        "nudos_de_borde_grado_1": sum(grado == 1 for grado in grados.values()),
        "distribucion_grados": {
            str(grado): cantidad
            for grado, cantidad in sorted(Counter(grados.values()).items())
        },
        "desviacion_mediana_cuatro_direcciones_grados": float(
            np.median(desviaciones)
        ),
        "fraccion_aristas_a_5_grados": float(
            np.mean(np.asarray(desviaciones) <= 5)
        ),
        "longitud_minima_px": min(longitudes),
    }


def coordenadas_metricas(punto: np.ndarray) -> list[float]:
    return [
        round((float(punto[0]) - CENTRO_X_PX) / PX_POR_METRO_X, 12),
        round((float(punto[1]) - CENTRO_Y_PX) / PX_POR_METRO_Y, 12),
    ]


def serializar_aristas(
    nodos: list[list[float]], aristas: list[tuple[int, int]]
) -> list[list[float | int]]:
    salida = []
    for a, b in aristas:
        dx = nodos[b][0] - nodos[a][0]
        dy = nodos[b][1] - nodos[a][1]
        salida.append(
            [
                a,
                b,
                round(math.hypot(dx, dy), 12),
                round(math.degrees(math.atan2(dy, dx)) % 180, 12),
            ]
        )
    return salida


def construir_dato(tesis: Path, figura: Path) -> dict[str, object]:
    pixeles = np.asarray(Image.open(figura).convert("L"))
    propuesta = completar_propuesta(pixeles)
    vertices, aristas = extraer_grafo(propuesta)
    controles = controles_grafo(vertices, aristas)
    if controles["componentes_conexas"] != 1:
        raise RuntimeError("la red extraida no es conexa")
    if controles["nudos_de_borde_grado_1"] != 24:
        raise RuntimeError("no se detectaron los 24 terminales de borde esperados")

    sensibilidad = []
    for umbral in (170, 200, 230):
        v_sensible, a_sensible = extraer_grafo(propuesta, umbral=umbral)
        sensibilidad.append(
            {
                "umbral": umbral,
                "nudos": len(v_sensible),
                "aristas": len(a_sensible),
                "componentes_conexas": numero_componentes(
                    len(v_sensible), a_sensible
                ),
            }
        )

    grados = Counter(indice for arista in aristas for indice in arista)
    nodos = [coordenadas_metricas(punto) for punto in vertices]
    return {
        "version": 2,
        "fuente": {
            "referencia": (
                "Ferrer Perez-Blanco (2023), Mocárabes de La Alhambra, "
                "figura 128"
            ),
            "handle": "11441/143321",
            "pagina_pdf": PAGINA_PDF,
            "mitad_usada": "superior: propuesta del autor; inferior generada por reflexion",
            "sha256_pdf": sha256_archivo(tesis),
            "sha256_imagen_pixeles": sha256_pixeles(pixeles),
        },
        "registro": {
            "centro_figura_px": [CENTRO_X_PX, CENTRO_Y_PX],
            "px_por_metro": [PX_POR_METRO_X, PX_POR_METRO_Y],
            "eje_y": "positivo hacia la mitad inferior de la planta",
        },
        "metodo": {
            "umbral_gris": UMBRAL,
            "conectividad_raster": 8,
            "dilatacion_regiones_nudo_px": DILATACION_NUDOS,
            "tolerancia_rdp_px": TOLERANCIA_SIMPLIFICACION_PX,
            "eje_espejo_y_px": EJE_ESPEJO_Y_PX,
            "contorno_editorial_punteado": "excluido mediante octogono interior",
        },
        "controles": {**controles, "sensibilidad_umbral": sensibilidad},
        "nodos_borde": sorted(
            indice for indice in range(len(vertices)) if grados[indice] == 1
        ),
        "nodos": nodos,
        "aristas": serializar_aristas(nodos, aristas),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tesis",
        type=Path,
        default=Path("docs/Ferrer Pérez-Blanco, Ignacio Tesis.pdf"),
    )
    parser.add_argument(
        "--imagen",
        type=Path,
        help="imagen 547x546 ya extraida; evita ejecutar pdfimages",
    )
    parser.add_argument(
        "--salida", type=Path, default=Path("datos/red_medinas.json")
    )
    args = parser.parse_args()

    if args.imagen is not None:
        resultado = construir_dato(args.tesis, args.imagen)
    else:
        with tempfile.TemporaryDirectory(prefix="granada-medinas-") as temporal:
            figura = extraer_figura(args.tesis, Path(temporal))
            resultado = construir_dato(args.tesis, figura)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    controles = resultado["controles"]
    print(
        f"{controles['nudos']} nudos, {controles['aristas']} aristas, "
        f"{controles['componentes_conexas']} componente, "
        f"{controles['nudos_de_borde_grado_1']} terminales de borde"
    )


if __name__ == "__main__":
    main()
