"""Controles estaticos del visor tridimensional."""

import json
from html.parser import HTMLParser
from pathlib import Path


RAIZ = Path(__file__).parents[1]
WEB = RAIZ / "web"


class _RecolectorIds(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        atributos = dict(attrs)
        if atributos.get("id"):
            self.ids.append(atributos["id"])


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


def test_el_visor_usa_yeso_blanco_por_defecto_y_separa_la_capa_analitica() -> None:
    """El color de niveles no puede parecer una propuesta de policromia."""
    html = (WEB / "index.html").read_text(encoding="utf-8")
    js = (WEB / "viewer.js").read_text(encoding="utf-8")
    assert '<option value="plaster" selected>Yeso blanco</option>' in html
    assert '<option value="levels">Lectura de niveles</option>' in html
    assert 'id="plaster-color"' in html
    assert 'let colorMode = "plaster"' in js
    assert "sin pigmentos asignados" in js
    assert "sin atribución histórica" in js


def test_los_controles_de_nivel_solo_se_muestran_en_la_capa_analitica() -> None:
    html = (WEB / "index.html").read_text(encoding="utf-8")
    js = (WEB / "viewer.js").read_text(encoding="utf-8")
    assert 'id="scenario-control" class="segmented"' in html
    assert 'id="uncertainty-control" class="toggle"' in html
    assert "#scenario-control\").hidden = !(historical && analytical)" in js
    assert "#uncertainty-control\").hidden = !(historical && analytical)" in js


def test_el_selector_de_orden_abre_una_vista_sintetica_separada() -> None:
    """Cambiar m no puede deformar cosmeticamante la malla historica."""
    html = (WEB / "index.html").read_text(encoding="utf-8")
    js = (WEB / "viewer.js").read_text(encoding="utf-8")
    assert '<option value="historical" selected>Dos Hermanas</option>' in html
    assert '<option value="synthetic">Comparar trazados</option>' in html
    for m in (16, 20, 24):
        assert f'<option value="{m}"' in html
    assert "../datos/ordenes_sinteticos.json" in js
    assert "function buildHistoricalModel()" in js
    assert "function buildSyntheticModel()" in js
    assert 'viewMode === "historical"' in js
    assert "coordenadas decimales solo sirven para dibujarla" in js


def test_la_vista_sintetica_es_una_cupula_completa_no_un_anillo_plano() -> None:
    dato = json.loads(
        (RAIZ / "datos" / "ordenes_sinteticos.json").read_text(encoding="utf-8")
    )
    js = (WEB / "viewer.js").read_text(encoding="utf-8")
    assert dato["modelo"] == "cupulas-comparativas-escalonadas"
    assert {fila["numero_coronas"] for fila in dato["ordenes"]} == {5}
    assert [fila["numero_celdas"] for fila in dato["ordenes"]] == [40, 50, 60]
    assert "steppedCellGeometry" in js
    assert "cell.cota_superior" in js
    assert "cell.cota_inferior" in js


def test_la_interfaz_habla_a_una_audiencia_historica() -> None:
    html = (WEB / "index.html").read_text(encoding="utf-8")
    js = (WEB / "viewer.js").read_text(encoding="utf-8")
    assert "Estado de la evidencia" in html
    assert "Procedencia y límites" in html
    assert "Ocho sectores · 45°" in html
    assert "Desde abajo" in html
    assert "No reproduce un edificio" in js
    assert "composición contemporánea" in js
    assert "Z[ζ" not in html
    assert "C8" not in html


def test_la_interfaz_no_repite_ids_y_rotula_sus_grupos_de_control() -> None:
    html = (WEB / "index.html").read_text(encoding="utf-8")
    recolector = _RecolectorIds()
    recolector.feed(html)
    assert len(recolector.ids) == len(set(recolector.ids))
    assert 'role="toolbar" aria-label="Controles del modelo"' in html
    assert 'role="group" aria-label="Punto de vista"' in html
    assert 'aria-live="polite"' in html


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


def test_el_visor_dice_que_la_plantilla_de_cada_cara_esta_decidida() -> None:
    """La ficha no puede callar lo unico del modelo que no viene de una fuente.

    La geometria del OBJ ya lleva dentro el reparto de plantillas de la decision
    0013. Mirandola no se distingue de lo documentado, asi que la pagina lo dice
    cara a cara.
    """
    js = (WEB / "viewer.js").read_text(encoding="utf-8")
    assert "../datos/malla_cupula.json" in js
    assert "decisión 0013" in js
    assert "reparto por bandas propuesto" in js
    assert "info.plantilla" in js


def test_los_tres_ficheros_que_carga_el_visor_hablan_de_las_mismas_caras() -> None:
    """Si un id se descolgara, la ficha mostraria la plantilla de otra cara."""
    informe = json.loads(
        (RAIZ / "datos" / "malla_cupula.json").read_text(encoding="utf-8")
    )
    niveles = json.loads(
        (RAIZ / "datos" / "niveles_aproximados.json").read_text(encoding="utf-8")
    )
    obj = (RAIZ / "renders" / "cupula_aproximada.obj").read_text(encoding="utf-8")
    grupos = {
        linea[2:].strip().removeprefix("cara_")
        for linea in obj.splitlines()
        if linea.startswith("o ")
    }
    assert {fila["id"] for fila in informe["caras"]} == grupos
    assert {cara["id"] for cara in niveles["caras"]} == grupos
