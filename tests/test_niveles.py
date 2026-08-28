"""Tests del nivel topologico de cada tesela."""

from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from granada import niveles as mod_niveles
from granada.niveles import (
    AsignacionNivel,
    InconsistenciaNiveles,
    RelacionVecindad,
    RestriccionNivel,
    RestriccionSinFirmar,
    ResultadoNiveles,
    TopologiaAscenso,
    TipoMocarabe,
    admite_salto_unitario,
    resolver_desde_vecindades,
    resolver_niveles,
    restricciones_firmadas,
)


def test_la_familia_documentada_tiene_siete_piezas() -> None:
    assert {tipo.value for tipo in TipoMocarabe} == {
        "A1",
        "A2",
        "A3",
        "B4",
        "C1",
        "C2",
        "D3",
    }


@pytest.mark.parametrize("tipo", [TipoMocarabe.A3, TipoMocarabe.D3])
def test_a3_y_d3_salvan_dos_niveles(tipo: TipoMocarabe) -> None:
    pieza = AsignacionNivel(tipo, nivel_base=4)
    assert tipo.salto_niveles == 2
    assert pieza.nivel_cima == 6
    assert pieza.niveles_cubiertos == (4, 5)


@pytest.mark.parametrize(
    "tipo",
    [
        TipoMocarabe.A1,
        TipoMocarabe.A2,
        TipoMocarabe.B4,
        TipoMocarabe.C1,
        TipoMocarabe.C2,
    ],
)
def test_las_otras_piezas_salvan_un_nivel(tipo: TipoMocarabe) -> None:
    pieza = AsignacionNivel(tipo, nivel_base=4)
    assert tipo.salto_niveles == 1
    assert pieza.nivel_cima == 5
    assert pieza.niveles_cubiertos == (4,)


def test_tipo_separa_figura_y_topologia() -> None:
    assert TipoMocarabe.C2.figura == "C"
    assert TipoMocarabe.C2.topologia == 2
    assert TipoMocarabe.B4.figura == "B"
    assert TipoMocarabe.B4.topologia == 4


@pytest.mark.parametrize(
    ("tipos", "esperada"),
    [
        ((TipoMocarabe.A1, TipoMocarabe.C1), TopologiaAscenso.DIVERGENTE),
        ((TipoMocarabe.A2, TipoMocarabe.C2), TopologiaAscenso.CONVERGENTE),
        ((TipoMocarabe.A3, TipoMocarabe.D3), TopologiaAscenso.MIXTA),
        ((TipoMocarabe.B4,), TopologiaAscenso.NEUTRA),
    ],
)
def test_topologia_de_ascenso_documentada_por_ferrer(
    tipos: tuple[TipoMocarabe, ...], esperada: TopologiaAscenso
) -> None:
    assert all(tipo.topologia_ascenso is esperada for tipo in tipos)


def test_asignacion_rechaza_tipo_y_nivel_invalidos() -> None:
    with pytest.raises(TypeError):
        AsignacionNivel("A1", 0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        AsignacionNivel(TipoMocarabe.A1, 0.0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        AsignacionNivel(TipoMocarabe.A1, True)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        AsignacionNivel(TipoMocarabe.A1, -1)


def test_propaga_ascensos_descansos_y_descensos_desde_un_ancla() -> None:
    restricciones = [
        RestriccionNivel("borde", "a", 1),
        RestriccionNivel("a", "b", 0),
        RestriccionNivel("b", "c", 2),
        RestriccionNivel("c", "d", -1),
    ]
    resultado = resolver_niveles(restricciones, {"borde": 0})
    assert resultado.esta_completo
    assert dict(resultado.niveles) == {"borde": 0, "a": 1, "b": 1, "c": 3, "d": 2}
    assert resultado.exigir_completo() == resultado.niveles


def test_la_direccion_de_la_restriccion_es_reversible() -> None:
    resultado = resolver_niveles(
        [RestriccionNivel("alto", "bajo", -2)], {"bajo": 3}
    )
    assert resultado.niveles["alto"] == 5


def test_un_componente_sin_ancla_no_recibe_un_cero_inventado() -> None:
    resultado = resolver_niveles([RestriccionNivel("x", "y", 1)])
    assert dict(resultado.niveles) == {}
    assert resultado.componentes_sin_ancla == (frozenset({"x", "y"}),)
    assert not resultado.esta_completo
    with pytest.raises(ValueError, match="sin ancla"):
        resultado.exigir_completo()


def test_resuelve_un_componente_y_deja_otro_explicito() -> None:
    resultado = resolver_niveles(
        [RestriccionNivel("a", "b", 1), RestriccionNivel("x", "y", 1)],
        {"a": 0},
    )
    assert dict(resultado.niveles) == {"a": 0, "b": 1}
    assert resultado.componentes_sin_ancla == (frozenset({"x", "y"}),)


def test_un_nodo_anclado_aislado_queda_resuelto() -> None:
    resultado = resolver_niveles([], {"borde": 7})
    assert resultado.esta_completo
    assert dict(resultado.niveles) == {"borde": 7}


def test_dos_anclas_coherentes_fijan_el_mismo_componente() -> None:
    resultado = resolver_niveles(
        [RestriccionNivel("a", "b", 2)], {"a": 3, "b": 5}
    )
    assert dict(resultado.niveles) == {"a": 3, "b": 5}


def test_un_ciclo_incompatible_falla_cerrado() -> None:
    with pytest.raises(InconsistenciaNiveles, match="ciclo incompatible"):
        resolver_niveles(
            [
                RestriccionNivel("a", "b", 1),
                RestriccionNivel("b", "c", 1),
                RestriccionNivel("c", "a", 1),
            ],
            {"a": 0},
        )


def test_anclas_incompatibles_fallan_cerrado() -> None:
    with pytest.raises(InconsistenciaNiveles, match="anclas incompatibles"):
        resolver_niveles(
            [RestriccionNivel("a", "b", 1)], {"a": 0, "b": 7}
        )


def test_no_se_acepta_una_solucion_con_niveles_negativos() -> None:
    with pytest.raises(InconsistenciaNiveles, match="niveles negativos"):
        resolver_niveles([RestriccionNivel("a", "b", -1)], {"a": 0})


def test_validacion_de_restricciones_y_anclas() -> None:
    with pytest.raises(ValueError):
        RestriccionNivel("", "b", 1)
    with pytest.raises(ValueError):
        RestriccionNivel("a", "a", 1)
    with pytest.raises(TypeError):
        RestriccionNivel("a", "b", 1.0)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        resolver_niveles([object()])  # type: ignore[list-item]
    with pytest.raises(TypeError):
        resolver_niveles([], {"a": 0.0})  # type: ignore[dict-item]
    with pytest.raises(ValueError):
        resolver_niveles([], {"a": -1})


def test_resultado_es_inmutable_y_valida_solapamientos() -> None:
    resultado = resolver_niveles([], {"a": 0})
    with pytest.raises(TypeError):
        resultado.niveles["a"] = 3  # type: ignore[index]
    with pytest.raises(ValueError):
        ResultadoNiveles({"a": 0}, (frozenset({"a"}),))
    with pytest.raises(ValueError, match="disjuntos"):
        ResultadoNiveles({}, (frozenset({"a", "b"}), frozenset({"b", "c"})))


def test_el_modulo_no_usa_coma_flotante() -> None:
    fuente = pathlib.Path(inspect.getfile(mod_niveles)).read_text(encoding="utf-8")
    arbol = ast.parse(fuente)
    infracciones = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, float):
            infracciones.append(f"literal float {nodo.value!r}")
        elif isinstance(nodo, ast.Name) and nodo.id == "float":
            infracciones.append("float()")
    assert infracciones == []


# --- vecindades sin firmar -------------------------------------------------


def test_una_vecindad_nace_sin_signo_de_nivel() -> None:
    vecindad = RelacionVecindad("c001", "c002")
    assert vecindad.salto is None
    assert not vecindad.esta_firmada
    with pytest.raises(RestriccionSinFirmar, match="no tiene signo"):
        vecindad.como_restriccion()


def test_una_vecindad_firmada_se_convierte_en_restriccion() -> None:
    vecindad = RelacionVecindad("c001", "c002", 1, "figura 29, flecha de ascenso")
    assert vecindad.esta_firmada
    assert vecindad.como_restriccion() == RestriccionNivel("c001", "c002", 1)
    descanso = RelacionVecindad("c002", "c003", 0, "misma cota medida")
    assert descanso.esta_firmada
    assert descanso.como_restriccion().salto == 0


def test_firmar_un_salto_exige_citar_la_evidencia() -> None:
    with pytest.raises(ValueError, match="evidencia"):
        RelacionVecindad("c001", "c002", 1)
    with pytest.raises(TypeError):
        RelacionVecindad("c001", "c002", 1.0, "fuente")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="distintas"):
        RelacionVecindad("c001", "c001")


def test_no_hay_conversion_parcial_de_vecindades_sin_firmar() -> None:
    relaciones = [
        RelacionVecindad("c001", "c002", 1, "flecha"),
        RelacionVecindad("c002", "c003"),
    ]
    with pytest.raises(RestriccionSinFirmar, match="sin signo de nivel"):
        restricciones_firmadas(relaciones)
    with pytest.raises(RestriccionSinFirmar):
        resolver_desde_vecindades(relaciones, {"c001": 0})
    with pytest.raises(TypeError):
        # type: ignore[list-item]
        restricciones_firmadas([RestriccionNivel("a", "b", 1)])


def test_con_todas_firmadas_la_propagacion_funciona_igual() -> None:
    relaciones = [
        RelacionVecindad("c001", "c002", 1, "flecha"),
        RelacionVecindad("c002", "c003", 0, "descanso"),
        RelacionVecindad("c003", "c004", -1, "descenso"),
    ]
    assert len(restricciones_firmadas(relaciones)) == 3
    resultado = resolver_desde_vecindades(relaciones, {"c001": 2})
    esperado = {"c001": 2, "c002": 3, "c003": 3, "c004": 2}
    assert dict(resultado.niveles) == esperado
    assert resultado.esta_completo


def test_una_vecindad_firmada_incoherente_sigue_fallando() -> None:
    relaciones = [
        RelacionVecindad("c001", "c002", 1, "flecha"),
        RelacionVecindad("c002", "c003", 1, "flecha"),
        RelacionVecindad("c003", "c001", 1, "flecha"),
    ]
    with pytest.raises(InconsistenciaNiveles):
        resolver_desde_vecindades(relaciones, {"c001": 0})


# --- que ciclos permite un salto unitario ----------------------------------


def aristas_de(relaciones) -> set[frozenset[str]]:
    return {frozenset((r.origen, r.destino)) for r in relaciones}


def anillo(nombres: list[str]) -> list[RelacionVecindad]:
    return [
        RelacionVecindad(uno, otro)
        for uno, otro in zip(nombres, nombres[1:] + nombres[:1])
    ]


def test_un_ciclo_par_admite_que_toda_vecindad_salve_un_nivel() -> None:
    posible, testigo = admite_salto_unitario(anillo(["a", "b", "c", "d"]))
    assert posible
    assert testigo == ()


def test_un_triangulo_no_admite_salto_unitario_en_las_tres_medinas() -> None:
    relaciones = anillo(["a", "b", "c"])
    posible, testigo = admite_salto_unitario(relaciones)
    assert not posible
    assert set(testigo) == {"a", "b", "c"}


def test_el_testigo_es_un_ciclo_impar_de_verdad() -> None:
    relaciones = anillo(["a", "b", "c", "d", "e"]) + [RelacionVecindad("a", "c")]
    posible, testigo = admite_salto_unitario(relaciones)
    assert not posible
    assert len(testigo) % 2 == 1
    aristas = aristas_de(relaciones)
    pasos = list(zip(testigo, testigo[1:] + testigo[:1]))
    assert all(frozenset(paso) in aristas for paso in pasos)
    assert len(set(testigo)) == len(testigo)


def test_la_pregunta_es_estructural_e_ignora_lo_ya_firmado() -> None:
    firmadas = [
        RelacionVecindad("a", "b", 1, "flecha"),
        RelacionVecindad("b", "c", 2, "jaira de dos niveles"),
        RelacionVecindad("c", "a", -1, "descenso"),
    ]
    posible, testigo = admite_salto_unitario(firmadas)
    assert not posible
    assert set(testigo) == {"a", "b", "c"}


def test_basta_un_componente_impar_para_que_no_lo_admita() -> None:
    relaciones = anillo(["a", "b", "c", "d"]) + anillo(["x", "y", "z"])
    posible, testigo = admite_salto_unitario(relaciones)
    assert not posible
    assert set(testigo) == {"x", "y", "z"}
    sueltas, _ = admite_salto_unitario(anillo(["a", "b", "c", "d"]))
    assert sueltas


def test_sin_vecindades_no_hay_nada_que_impida_el_salto_unitario() -> None:
    assert admite_salto_unitario([]) == (True, ())
    with pytest.raises(TypeError):
        admite_salto_unitario([RestriccionNivel("a", "b", 1)])  # type: ignore[list-item]
