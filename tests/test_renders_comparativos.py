"""Laminas estaticas de las cupulas comparativas."""

import json
import struct
from pathlib import Path

import pytest

from scripts.render_cupulas_comparativas import malla


RAIZ = Path(__file__).parents[1]
RENDERS = RAIZ / "renders"
DATOS = json.loads(
    (RAIZ / "datos" / "ordenes_sinteticos.json").read_text(encoding="utf-8")
)


def dimensiones_png(ruta: Path) -> tuple[int, int]:
    cabecera = ruta.read_bytes()[:24]
    assert cabecera[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", cabecera[16:24])


@pytest.mark.parametrize(("sectores", "celdas"), [(8, 40), (10, 50), (12, 60)])
def test_cada_render_individual_es_grande_y_sale_de_toda_la_malla(
    sectores: int, celdas: int
) -> None:
    orden = next(fila for fila in DATOS["ordenes"] if fila["numero_sectores"] == sectores)
    vertices, caras = malla(orden)
    assert len(orden["celdas"]) == celdas
    assert len(vertices) > celdas * 6
    assert len(caras) == sectores * 56
    for vista in ("general", "intrados"):
        ruta = RENDERS / f"cupula_comparativa_{sectores}_{vista}.png"
        assert dimensiones_png(ruta) == (1200, 1200)
        assert ruta.stat().st_size > 25_000


@pytest.mark.parametrize("vista", ["general", "intrados"])
def test_las_laminas_finales_tienen_rotulo_y_advertencia(vista: str) -> None:
    png = RENDERS / f"cupulas_comparativas_{vista}.png"
    svg = RENDERS / f"cupulas_comparativas_{vista}.svg"
    texto = svg.read_text(encoding="utf-8")
    assert dimensiones_png(png) == (3600, 1600)
    assert png.stat().st_size > 100_000
    assert "Trazado de ocho sectores" in texto
    assert "Trazado de diez sectores" in texto
    assert "Trazado de doce sectores" in texto
    assert "no reproduce un monumento" in texto
    assert "decisión 0014" in texto
