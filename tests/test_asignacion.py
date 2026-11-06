"""Controles de la asignacion de plantilla por banda (decision 0013).

Lo que se prueba aqui no es que la frontera sea la verdadera -no hay fuente que
lo diga-, sino que **se elige con los criterios escritos**, que el artefacto
declara que esta decidida, y que los rivales quedan a la vista.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from granada.asignacion import (
    CRITERIOS,
    Asignacion,
    catalogo,
    elegir,
    evaluar,
    junta_en_P,
    procedencia,
)
from granada.perfil import MAYOR, MENOR, UNIDADES_ENTRE_NIVELES


RAIZ = Path(__file__).parents[1]
NIVELES = RAIZ / "datos" / "niveles_aproximados.json"
CARAS = RAIZ / "datos" / "caras_red.json"
INFORME = RAIZ / "datos" / "malla_cupula.json"
OBJ = RAIZ / "renders" / "cupula_aproximada.obj"


def planta() -> tuple[dict[str, int], list[int], list[dict]]:
    niveles = json.loads(NIVELES.read_text(encoding="utf-8"))["caras"]
    bandas = {cara["id"]: cara["capa_desde_borde"] for cara in niveles}
    hiladas = sorted({cara["hilada"] for cara in niveles})
    saltos = [
        hilada - (hiladas[indice - 1] if indice else 0)
        for indice, hilada in enumerate(hiladas)
    ]
    vecindades = json.loads(CARAS.read_text(encoding="utf-8"))["vecindades"]
    return bandas, saltos, vecindades


def test_la_junta_es_exacta_y_completa_el_salto() -> None:
    """Frente mas junta son las 8P por hilada del salto, sin redondeo."""
    for salto in (1, 2, 4, 5, 6):
        for plantilla in (MAYOR, MENOR):
            frente = plantilla.cima * salto
            junta = junta_en_P(salto, plantilla)
            assert frente + junta == UNIDADES_ENTRE_NIVELES * salto
    assert junta_en_P(4, MAYOR) == Fraction(4)
    assert junta_en_P(4, MENOR) == Fraction(2)
    assert junta_en_P(0, MAYOR) == 0
    with pytest.raises(ValueError):
        junta_en_P(-1, MAYOR)


def test_la_asignacion_reparte_por_banda_y_la_uniforme_no_rompe_nada() -> None:
    bandas = {"a": 0, "b": 1, "c": 2}
    partida = Asignacion(MENOR, MAYOR, frontera=2)
    assert partida.por_cara(bandas) == {"a": MENOR, "b": MENOR, "c": MAYOR}
    assert not partida.uniformizada
    uniforme = Asignacion.uniforme(MAYOR)
    assert uniforme.uniformizada
    assert set(uniforme.por_cara(bandas).values()) == {MAYOR}
    with pytest.raises(ValueError):
        Asignacion(MENOR, MAYOR, frontera=-1)


def test_la_uniforme_sigue_dando_cero_vecindades_rotas() -> None:
    """Regresion de la decision 0010: con una sola plantilla el control es trivial."""
    bandas, saltos, vecindades = planta()
    for plantilla in (MAYOR, MENOR):
        candidato = evaluar(
            Asignacion.uniforme(plantilla), bandas, saltos, vecindades
        )
        assert candidato.rotas == ()


def test_la_elegida_es_la_de_la_decision_0013() -> None:
    bandas, saltos, vecindades = planta()
    elegida = elegir(bandas, saltos, vecindades)
    assert saltos == [6, 5, 2, 4, 2, 4]
    assert elegida.asignacion == Asignacion(MENOR, MAYOR, frontera=3)
    assert elegida.caras_por_grupo == (88, 17)
    assert len(elegida.rotas) == 16


def test_todo_lo_que_rompe_el_paralelismo_cruza_la_frontera() -> None:
    """Si algo se rompiera dentro de un grupo, la asignacion no seria por banda."""
    bandas, saltos, vecindades = planta()
    elegida = elegir(bandas, saltos, vecindades)
    frontera = elegida.asignacion.frontera
    for a, b in elegida.rotas:
        assert {bandas[a], bandas[b]} == {frontera - 1, frontera}


def test_lo_que_descarta_a_las_asignaciones_que_rompen_menos() -> None:
    """Las que rompen 8 vecindades dejan sola a la pieza de cierre: criterio 3."""
    bandas, saltos, vecindades = planta()
    elegida = elegir(bandas, saltos, vecindades)
    mejores = [
        candidato
        for candidato in catalogo(bandas, saltos, vecindades)
        if len(candidato.rotas) < len(elegida.rotas)
        and not candidato.asignacion.uniformizada
    ]
    assert mejores, "sin rivales mejores el criterio 4 no estaria decidiendo nada"
    assert all(candidato.degenerado for candidato in mejores)
    assert all(candidato.caras_por_grupo[1] == 1 for candidato in mejores)


def test_el_empate_lo_deshace_la_subdivision_de_la_planta() -> None:
    """Criterio 5: dos fronteras rompen 16 vecindades; solo una cambia la planta."""
    bandas, saltos, vecindades = planta()
    empatadas = [
        candidato
        for candidato in catalogo(bandas, saltos, vecindades)
        if len(candidato.rotas) == 16 and candidato.asignacion.abajo == MENOR
    ]
    assert len(empatadas) == 2
    por_frontera = {c.asignacion.frontera: c.cambio_de_subdivision for c in empatadas}
    # 40 caras en la banda 2 y 8 en la 3; entre la 3 y la 4 no cambia nada.
    assert por_frontera == {3: Fraction(5), 4: Fraction(1)}


def test_la_elegida_no_es_la_que_mas_iguala_las_juntas() -> None:
    """La junta es argumento nuestro y va la ultima: queda escrito que pierde."""
    bandas, saltos, vecindades = planta()
    elegida = elegir(bandas, saltos, vecindades)
    mejor_junta = min(
        catalogo(bandas, saltos, vecindades),
        key=lambda candidato: candidato.dispersion_de_junta,
    )
    assert mejor_junta.dispersion_de_junta < elegida.dispersion_de_junta
    assert len(mejor_junta.rotas) > len(elegida.rotas)


def test_la_procedencia_dice_que_la_frontera_esta_decidida() -> None:
    texto = procedencia("c000", Asignacion(MENOR, MAYOR, 3), banda=0)
    assert "documentada" in texto and "DECIDIDA" in texto and "2|3" in texto
    uniforme = procedencia("c000", Asignacion.uniforme(MAYOR), banda=0)
    assert "sin evidencia" in uniforme


def test_los_criterios_van_escritos_y_en_orden() -> None:
    assert len(CRITERIOS) == 6
    assert [criterio[:2] for criterio in CRITERIOS] == [
        f"{i}." for i in range(1, 7)
    ]


def test_el_informe_declara_la_asignacion_cara_a_cara() -> None:
    informe = json.loads(INFORME.read_text(encoding="utf-8"))
    asignacion = informe["modelo"]["asignacion"]
    assert asignacion["etiqueta"] == "menor|mayor@3"
    assert "DECIDIDA" in asignacion["procedencia"]
    assert asignacion["caras_por_plantilla"] == {"menor": 88, "mayor": 17}
    assert len(asignacion["criterios"]) == 6
    assert len(asignacion["alternativas"]) >= 10
    filas = informe["caras"]
    assert len(filas) == 105
    for fila in filas:
        assert fila["plantilla"] in {"mayor", "menor"}
        assert "DECIDIDA" in fila["procedencia"]
        if fila["pieza_de_cierre"]:
            # La cupulilla apoya en la banda de abajo: no tiene junta, y el
            # campo queda vacio en vez de llevar un valor que nadie sostiene.
            assert fila["junta_m"] is None and "sin junta" in fila["procedencia"]
        else:
            assert fila["junta_m"] > 0
    # Una banda, una plantilla: si una banda mezclara, no seria una asignacion
    # por banda sino una cara a cara, que es otra decision y mas invencion.
    por_banda = {}
    for fila in filas:
        por_banda.setdefault(fila["banda"], set()).add(fila["plantilla"])
    assert all(len(plantillas) == 1 for plantillas in por_banda.values())


def test_el_control_de_la_frontera_esta_en_el_informe() -> None:
    controles = json.loads(INFORME.read_text(encoding="utf-8"))["controles"]
    assert controles["vecindades_no_paralelas"] == 16
    assert controles["vecindades_no_paralelas_fuera_de_la_frontera"] == 0
    assert controles["cota_minima_m"] > 0


def test_el_obj_avisa_de_que_la_frontera_se_decide() -> None:
    cabecera = [
        linea for linea in OBJ.read_text(encoding="utf-8").splitlines()[:8]
        if linea.startswith("#")
    ]
    texto = "\n".join(cabecera)
    assert "menor" in texto and "mayor" in texto
    assert "DECIDE" in texto and "0013" in texto


def test_el_coste_de_equivocarse_es_el_declarado() -> None:
    """La roadmap lo tasaba en un 6 %: es la razon entre 15/16 y 7/8."""
    salto = Fraction(1)
    cambio = MENOR.profundidad(salto) / MAYOR.profundidad(salto)
    assert cambio == Fraction(15, 14)
    assert 1.07 < float(cambio) < 1.072
