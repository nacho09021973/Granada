"""Controles estaticos del visor tridimensional."""

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


def test_la_geometria_procede_de_los_tres_artefactos_del_proyecto() -> None:
    js = (WEB / "viewer.js").read_text(encoding="utf-8")
    for ruta in (
        "../datos/red_medinas.json",
        "../datos/caras_red.json",
        "../datos/niveles_aproximados.json",
    ):
        assert ruta in js
    assert "ExtrudeGeometry" in js
    assert "preserveDrawingBuffer: true" in js
    assert "NaN|-?Infinity" in js
