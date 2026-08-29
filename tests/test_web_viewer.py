"""Controles estaticos del visor tridimensional."""

import json
from pathlib import Path


RAIZ = Path(__file__).parents[1]
WEB = RAIZ / "web"


def test_el_visior_es_autocontenido_y_fija_threejs() -> None:
    html = (WEB / "index.html").read_text(encoding="utf-8")
    assert '"three": "./vendor/three.module.min.js"' in html
    assert (WEB / "vendor" / "three.module.min.js").stat().st_size > 300_000
    assert (WEB / "vendor" / "three.core.min.js").stat().st_size > 300_000
    assert (WEB / "vendor" / "OrbitControls.js").stat().st_size > 30_000


def test_el_visior_declara_su_alcance_y_los_dos_escenarios() -> None:
    html = (WEB / "index.html").read_text(encoding="utf-8")
    assert "no es una restitución histórica verificada" in html
    assert 'data-scenario="7"' in html
    assert 'data-scenario="8"' in html
    assert 'id="uncertainty"' in html


def test_el_visor_muestra_la_misma_malla_que_se_exporta() -> None:
    """Una sola geometria en el repositorio, no dos que puedan divergir.

    El visor levantaba prismas planos por su cuenta mientras el OBJ llevaba las
    celdas: dos modelos distintos y ninguna prueba que lo detectara. Ahora carga
    el OBJ exportado, asi que pagina y malla no pueden separarse.
    """
    js = (WEB / "viewer.js").read_text(encoding="utf-8")
    assert "../renders/cupula_aproximada.obj" in js
    assert "../datos/niveles_aproximados.json" in js
    assert "ExtrudeGeometry" not in js
    assert "preserveDrawingBuffer: true" in js
    assert "NaN|-?Infinity" in js


def test_el_visor_lee_un_grupo_por_cara_del_obj() -> None:
    """Los grupos del OBJ y las caras del modelo tienen que casar uno a uno."""
    obj = (RAIZ / "renders" / "cupula_aproximada.obj").read_text(encoding="utf-8")
    grupos = [
        linea[2:].strip().removeprefix("cara_")
        for linea in obj.splitlines()
        if linea.startswith("o ")
    ]
    niveles = json.loads(
        (RAIZ / "datos" / "niveles_aproximados.json").read_text(encoding="utf-8")
    )
    assert len(grupos) == 105
    assert set(grupos) == {cara["id"] for cara in niveles["caras"]}
