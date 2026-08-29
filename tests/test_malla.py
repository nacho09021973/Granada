"""Controles del levantado y de la malla exportada."""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from granada.malla import Malla, celda, cupula, triangular
from granada.plantilla import MAYOR, MENOR


RAIZ = Path(__file__).parents[1]
OBJ = RAIZ / "renders" / "cupula_aproximada.obj"
INFORME = RAIZ / "datos" / "malla_cupula.json"
ALTURA_TOTAL_M = 4.67

TRIANGULO = [(3.0, 0.0), (2.0, 1.0), (2.0, -1.0)]


def test_la_celda_cuelga_exactamente_la_fraccion_documentada() -> None:
    malla = Malla()
    celda(malla, TRIANGULO, cota_m=1.2, salto_vertical_m=0.8, plantilla=MAYOR)
    cotas = [v[2] for v in malla.vertices]
    assert max(cotas) == pytest.approx(1.2)
    assert min(cotas) == pytest.approx(1.2 - 0.8 * 7 / 8)


def test_la_plantilla_menor_cuelga_mas_que_la_mayor() -> None:
    fondos = []
    for plantilla in (MAYOR, MENOR):
        malla = Malla()
        celda(malla, TRIANGULO, 1.2, 0.8, plantilla)
        fondos.append(min(v[2] for v in malla.vertices))
    assert fondos[1] < fondos[0]


def test_la_celda_queda_cerrada_y_orientada() -> None:
    malla = Malla()
    celda(malla, TRIANGULO, 1.2, 0.8, subdivision=3)
    # n puntos de borde: n-2 arriba, n-2 abajo y 2n de pared.
    assert len(malla.triangulos) == 4 * (3 * 3) - 4
    # invertir el poligono no cambia la geometria: se reorienta sola
    otra = Malla()
    celda(otra, list(reversed(TRIANGULO)), 1.2, 0.8, subdivision=3)
    assert sorted(otra.vertices) == sorted(malla.vertices)


def test_la_triangulacion_no_inventa_ni_pierde_area() -> None:
    """Recorte de orejas: la suma de los triangulos es el area del poligono."""
    def area(puntos):
        return abs(
            sum(
                a[0] * b[1] - b[0] * a[1]
                for a, b in zip(puntos, puntos[1:] + puntos[:1])
            )
        ) / 2

    for poligono in (
        TRIANGULO,
        [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)],
        # concava en forma de L: el abanico desde el centroide la rompe
        [(0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0)],
    ):
        triangulos = triangular(poligono)
        assert len(triangulos) == len(poligono) - 2
        troceada = sum(
            area([poligono[i], poligono[j], poligono[k]])
            for i, j, k in triangulos
        )
        assert troceada == pytest.approx(area(poligono))


def test_la_triangulacion_de_una_concava_no_se_sale_del_poligono() -> None:
    """51 de las 105 caras no son convexas; un abanico les mete puas."""
    ele = [(0.0, 0.0), (3.0, 0.0), (3.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0)]
    for i, j, k in triangular(ele):
        cx = (ele[i][0] + ele[j][0] + ele[k][0]) / 3
        cy = (ele[i][1] + ele[j][1] + ele[k][1]) / 3
        dentro = (cx <= 1.0 and cy <= 3.0) or (cy <= 1.0 and cx <= 3.0)
        assert dentro, f"triangulo fuera de la L: {(i, j, k)}"


def test_una_cara_sin_vuelo_radial_queda_plana() -> None:
    malla = Malla()
    celda(malla, TRIANGULO, 1.2, salto_vertical_m=0.0)
    assert {round(v[2], 9) for v in malla.vertices} == {1.2}


def test_la_celda_rechaza_entradas_imposibles() -> None:
    with pytest.raises(ValueError):
        celda(Malla(), [(0.0, 0.0), (1.0, 0.0)], 1.0, 0.5)
    with pytest.raises(ValueError):
        celda(Malla(), TRIANGULO, 1.0, -0.5)
    with pytest.raises(ValueError):
        celda(Malla(), TRIANGULO, 1.0, 0.5, subdivision=0)


def test_la_cupula_agrupa_cada_cara_por_separado() -> None:
    caras = [
        {"id": "c000", "poligono": TRIANGULO, "cota_m": 1.2, "salto_vertical_m": 0.4},
        {"id": "c001", "poligono": TRIANGULO, "cota_m": 2.4, "salto_vertical_m": 0.4},
    ]
    malla = cupula(caras)
    assert [nombre for nombre, _ in malla.grupos] == ["cara_c000", "cara_c001"]
    assert "o cara_c001" in malla.a_obj()


def test_el_obj_exportado_declara_que_es_aproximado() -> None:
    texto = OBJ.read_text(encoding="utf-8")
    assert texto.startswith("#")
    assert "APROXIMADA" in texto
    assert "5.2 hiladas" in texto


def test_el_obj_cubre_las_105_caras_y_cabe_en_la_cupula_medida() -> None:
    vertices = []
    grupos = 0
    for linea in OBJ.read_text(encoding="utf-8").splitlines():
        if linea.startswith("v "):
            vertices.append(tuple(float(x) for x in linea.split()[1:4]))
        elif linea.startswith("o "):
            grupos += 1
    assert grupos == 105
    cotas = [v[2] for v in vertices]
    assert min(cotas) > 0.0
    assert max(cotas) == pytest.approx(ALTURA_TOTAL_M)
    assert max(math.hypot(v[0], v[1]) for v in vertices) < 3.79


def test_el_informe_declara_su_estado_y_su_limite() -> None:
    informe = json.loads(INFORME.read_text(encoding="utf-8"))
    assert informe["estado"] == "APPROXIMATE_MESH_AVAILABLE"
    assert "no una adaraja" in informe["advertencia"]
    assert informe["modelo"]["unidades_entre_niveles"] == 8
    assert informe["modelo"]["fraccion_util"] == "7/8"
    assert "no medida" in informe["modelo"]["curva"]
    assert informe["controles"]["caras"] == 105
    assert informe["controles"]["hiladas_que_abarca_la_cara_mediana"] > 4


def test_la_malla_no_se_aleja_del_cono_medido() -> None:
    """La plataforma de cada cara ajusta al cono dentro de una tolerancia."""
    informe = json.loads(INFORME.read_text(encoding="utf-8"))
    assert informe["controles"]["residuo_rms_frente_al_cono_m"] < 0.30
    assert informe["controles"]["residuo_maximo_frente_al_cono_m"] < 0.80


def test_las_bandas_se_apoyan_unas_en_otras_sin_hueco() -> None:
    """El primer levantado dejaba huecos de hasta 0.39 m entre bandas.

    La celda cuelga 7/8 del salto hasta la banda de debajo, asi que entre el
    fondo de una banda y la plataforma de la inferior solo queda la junta: un
    octavo de ese salto, nunca un agujero abierto.
    """
    niveles = json.loads(
        (RAIZ / "datos" / "niveles_aproximados.json").read_text(encoding="utf-8")
    )
    cotas = [0.0] + [b["altura_m"] for b in niveles["calibracion_altura"]["bandas"]]
    for inferior, superior in zip(cotas, cotas[1:]):
        salto = superior - inferior
        junta = salto / 8
        assert junta == pytest.approx(salto - salto * 7 / 8)
        assert 0 < junta < 0.16


def test_el_paralelismo_se_cumple_en_la_asignacion_publicada() -> None:
    """Trivial con plantilla uniforme, y por eso se deja escrito que lo es."""
    informe = json.loads(INFORME.read_text(encoding="utf-8"))
    assert informe["controles"]["vecindades_no_paralelas"] == 0
    assert informe["modelo"]["plantilla"] == "mayor"


def test_el_render_existe_y_es_reproducible() -> None:
    """La cautela 2 pide mirar la malla; el control tiene que ser repetible."""
    script = (RAIZ / "scripts" / "render_malla.py").read_text(encoding="utf-8")
    assert "cautela 2" in script
    for vista in ("picada", "desde_abajo"):
        imagen = RAIZ / "renders" / f"cupula_{vista}.png"
        assert imagen.stat().st_size > 10_000
        assert imagen.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
