"""Controles estructurales del render de niveles aproximados."""

import json

from pathlib import Path


RUTA = Path(__file__).parents[1] / "renders" / "niveles_aproximados.svg"
RUTA_NIVELES = Path(__file__).parents[1] / "datos" / "niveles_aproximados.json"


def test_el_render_declara_alcance_y_contiene_todas_las_caras() -> None:
    svg = RUTA.read_text(encoding="utf-8")
    assert "Planta hipsométrica aproximada" in svg
    assert "no es una restitución histórica verificada" in svg
    assert svg.count("<title>c") == 105


def test_el_render_muestra_niveles_e_incertidumbre() -> None:
    svg = RUTA.read_text(encoding="utf-8")
    assert 'id="incierto"' in svg
    assert "cambia en el escenario de 8 niveles" in svg
    dato = json.loads(RUTA_NIVELES.read_text(encoding="utf-8"))
    niveles_presentes = {cara["nivel"] for cara in dato["caras"]}
    assert niveles_presentes == {0, 1, 3, 4, 6, 7}
    for nivel in niveles_presentes:
        assert f"nivel {nivel}, intervalo" in svg
