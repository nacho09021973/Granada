#!/usr/bin/env python3
"""Contraste fotometrico de la sombra como indicio de profundidad.

Usa los 16 cupulines exteriores, ya identificados en la planta registrada,
como cavidades hondas conocidas. Compara su luminancia con 16 parches
intermedios al mismo radio. Es una prueba de senal, no una asignacion de nivel
por tesela: pigmento, suciedad, orientacion de caras e iluminacion siguen
siendo confundidores.

Dependencias de analisis (fuera del nucleo ``granada/``): Pillow, NumPy y
SciPy. ``pdfimages`` (Poppler) se usa para extraer la ortoimagen embebida.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.stats import wilcoxon


def extraer_ortoimagen(plano: Path, destino: Path) -> Path:
    """Extrae la primera imagen de la primera pagina del PDF."""
    prefijo = destino / "aa415"
    subprocess.run(
        ["pdfimages", "-f", "1", "-l", "1", "-j", str(plano), str(prefijo)],
        check=True,
        capture_output=True,
        text=True,
    )
    candidatos = sorted(destino.glob("aa415-*"))
    if not candidatos:
        raise RuntimeError("pdfimages no extrajo ninguna imagen")
    tamanos = []
    for ruta in candidatos:
        with Image.open(ruta) as imagen:
            tamanos.append((imagen.width * imagen.height, ruta))
    return min(tamanos)[1]


def luminancia_rec709(ruta: Path) -> np.ndarray:
    """Luma sRGB Rec. 709 en el rango 0..255."""
    rgb = np.asarray(Image.open(ruta).convert("RGB"), dtype=np.float64)
    return 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]


def mediana_disco(
    luminancia: np.ndarray,
    centro_x: float,
    centro_y: float,
    radio: int,
) -> float:
    """Mediana dentro de un disco, sin construir una mascara de toda la foto."""
    x0 = int(round(centro_x)) - radio
    y0 = int(round(centro_y)) - radio
    x1 = x0 + 2 * radio + 1
    y1 = y0 + 2 * radio + 1
    if x0 < 0 or y0 < 0 or x1 > luminancia.shape[1] or y1 > luminancia.shape[0]:
        raise ValueError("el parche sale de la ortoimagen")
    yy, xx = np.ogrid[: 2 * radio + 1, : 2 * radio + 1]
    mascara = (xx - radio) ** 2 + (yy - radio) ** 2 <= radio**2
    return float(np.median(luminancia[y0:y1, x0:x1][mascara]))


def muestras_angulares(
    luminancia: np.ndarray,
    centro: tuple[int, int],
    radio_orbita: int,
    radio_parche: int,
    fase_grados: float,
    copias: int = 16,
) -> list[float]:
    cx, cy = centro
    paso = 360 / copias
    valores = []
    for k in range(copias):
        angulo = math.radians(fase_grados + k * paso)
        x = cx + radio_orbita * math.cos(angulo)
        y = cy + radio_orbita * math.sin(angulo)
        valores.append(mediana_disco(luminancia, x, y, radio_parche))
    return valores


def contraste(
    luminancia: np.ndarray,
    centro: tuple[int, int],
    radio_orbita: int,
    radio_parche: int,
    fase_grados: float = 0,
) -> dict[str, object]:
    cupulines = muestras_angulares(
        luminancia, centro, radio_orbita, radio_parche, fase_grados
    )
    controles = muestras_angulares(
        luminancia, centro, radio_orbita, radio_parche, fase_grados + 11.25
    )
    diferencias = np.asarray(controles) - np.asarray(cupulines)
    prueba = wilcoxon(cupulines, controles, alternative="less")
    return {
        "cupulines": cupulines,
        "controles_intermedios": controles,
        "diferencias_control_menos_cupulin": diferencias.tolist(),
        "mediana_cupulines": float(np.median(cupulines)),
        "mediana_controles": float(np.median(controles)),
        "mediana_diferencia": float(np.median(diferencias)),
        "iqr_diferencia": float(np.percentile(diferencias, 75) - np.percentile(diferencias, 25)),
        "pares_con_cupulin_mas_oscuro": int(np.count_nonzero(diferencias > 0)),
        "wilcoxon_unilateral_p": float(prueba.pvalue),
    }


def sha256(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def analizar(plano: Path) -> dict[str, object]:
    centro = (2048, 2035)
    radio_principal = 1300
    parche_principal = 90

    with tempfile.TemporaryDirectory(prefix="granada-sombra-") as temporal:
        orto = extraer_ortoimagen(plano, Path(temporal))
        luminancia = luminancia_rec709(orto)

    principal = contraste(
        luminancia, centro, radio_principal, parche_principal, fase_grados=0
    )

    sensibilidad = []
    for radio in (1250, 1300, 1350):
        for parche in (70, 90, 110):
            resultado = contraste(luminancia, centro, radio, parche)
            sensibilidad.append(
                {
                    "radio_orbita_px": radio,
                    "radio_parche_px": parche,
                    "mediana_diferencia": resultado["mediana_diferencia"],
                    "pares_con_cupulin_mas_oscuro": resultado[
                        "pares_con_cupulin_mas_oscuro"
                    ],
                    "wilcoxon_unilateral_p": resultado["wilcoxon_unilateral_p"],
                }
            )

    fases = np.linspace(0, 22.5, 181, endpoint=False)
    contrastes_fase = []
    for fase in fases:
        resultado = contraste(
            luminancia,
            centro,
            radio_principal,
            parche_principal,
            fase_grados=float(fase),
        )
        contrastes_fase.append(float(resultado["mediana_diferencia"]))
    indice_maximo = int(np.argmax(contrastes_fase))
    contraste_conocido = float(principal["mediana_diferencia"])

    return {
        "fuente": {
            "ruta": str(plano),
            "sha256": sha256(plano),
            "imagen_extraida_px": [int(luminancia.shape[1]), int(luminancia.shape[0])],
        },
        "metodo": {
            "centro_px": list(centro),
            "radio_orbita_principal_px": radio_principal,
            "radio_parche_principal_px": parche_principal,
            "copias": 16,
            "paso_angular_grados": 22.5,
            "desfase_control_grados": 11.25,
            "estadistico": "mediana de luminancia Rec. 709 por disco",
        },
        "resultado_principal": principal,
        "sensibilidad": sensibilidad,
        "control_fase": {
            "muestras": len(fases),
            "contraste_en_fase_documentada": contraste_conocido,
            "contraste_maximo": contrastes_fase[indice_maximo],
            "fase_del_maximo_grados": float(fases[indice_maximo]),
            "percentil_fase_documentada": float(
                100 * np.mean(np.asarray(contrastes_fase) <= contraste_conocido)
            ),
        },
        "alcance": {
            "sostiene": "la luminancia separa cavidades hondas conocidas de controles al mismo radio",
            "no_sostiene": "una conversion calibrada de luminancia a nivel entero por tesela",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plano", type=Path, default=Path("docs/AA-415_23.pdf"))
    parser.add_argument(
        "--salida", type=Path, default=Path("datos/contraste_sombra_niveles.json")
    )
    args = parser.parse_args()
    resultado = analizar(args.plano)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    principal = resultado["resultado_principal"]
    print(
        f"cupulines mas oscuros en {principal['pares_con_cupulin_mas_oscuro']}/16; "
        f"mediana delta={principal['mediana_diferencia']:.2f}; "
        f"p={principal['wilcoxon_unilateral_p']:.6g}"
    )


if __name__ == "__main__":
    main()
