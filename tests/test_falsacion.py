"""El examen que espera al primer salto firmado, y los datos reales de hoy."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from granada.falsacion import (
    CONSISTENTE,
    REFUTADA,
    SIN_DATOS,
    Cociente,
    cociente_de_orbitas,
    examinar,
)
from granada.niveles import RelacionVecindad

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cociente() -> Cociente:
    caras = json.loads((RAIZ / "datos/caras_red.json").read_text(encoding="utf-8"))
    orbitas = json.loads((RAIZ / "datos/orbitas_caras.json").read_text(encoding="utf-8"))
    return cociente_de_orbitas(caras["vecindades"], orbitas["orbitas"])


# --- la estructura, que es lo que hace barato el primer dato -----------------


def test_las_211_vecindades_colapsan_en_16_clases(cociente: Cociente) -> None:
    assert cociente.n_orbitas == 11
    assert cociente.n_vecindades == 211
    assert cociente.n_aristas == 16


def test_el_contorno_no_entra(cociente: Cociente) -> None:
    """Las 227 vecindades del fichero incluyen 16 con el contorno, que no es cara."""
    caras = json.loads((RAIZ / "datos/caras_red.json").read_text(encoding="utf-8"))
    assert len(caras["vecindades"]) == 227
    assert cociente.n_vecindades == 211


def test_seis_ciclos_de_cierre(cociente: Cociente) -> None:
    """16 aristas - 11 nodos + 1 componente. Seis ecuaciones que pueden refutar."""
    assert cociente.ciclos_independientes == 6


def test_ninguna_vecindad_es_interna_a_una_orbita(cociente: Cociente) -> None:
    """Si la hubiera, la hipotesis la obligaria a salto 0 y seria un test gratis."""
    for (i, j) in cociente.clases:
        assert i != j


# --- la auditoria de los datos ----------------------------------------------


def test_la_clase_2_7_esta_incompleta_y_se_delata_sola(cociente: Cociente) -> None:
    """Un tamano que no divide al orden del grupo acusa a los datos, no a la teoria.

    Registrado tal cual: no se corrige el dato desde aqui. `c078` y `c068` estan
    a azimuts contiguos (236,5 y 240,9 grados) y son las unicas caras de sus
    orbitas sin pareja; el resto tiene grado exactamente 1.
    """
    anomalas = cociente.clases_con_tamano_anomalo()
    assert anomalas == ((2, 7),)
    assert len(cociente.clases[(2, 7)]) == 15
    izq, der = cociente.caras_sin_pareja((2, 7))
    assert izq == ("c078",)
    assert der == ("c068",)


def test_las_demas_clases_dividen_al_orden(cociente: Cociente) -> None:
    for clase, vs in cociente.clases.items():
        if clase == (2, 7):
            continue
        assert 16 % len(vs) == 0, clase


# --- el examen ---------------------------------------------------------------


def test_sin_datos_no_finge_saber_nada(cociente: Cociente) -> None:
    informe = examinar([], cociente)
    assert informe.veredicto == SIN_DATOS
    assert informe.orbitas_libres == 11
    assert informe.vecindades_determinadas == 0
    assert not informe.esta_refutada


def test_un_solo_salto_determina_su_clase_entera(cociente: Cociente) -> None:
    a, b = cociente.clases[(0, 1)][0]
    informe = examinar([RelacionVecindad(a, b, 1, "prueba")], cociente)
    assert informe.veredicto == CONSISTENTE
    assert informe.vecindades_determinadas == 16
    assert informe.orbitas_libres == 10


def test_dos_saltos_incompatibles_de_la_misma_clase_refutan(cociente: Cociente) -> None:
    (a1, b1), (a2, b2) = cociente.clases[(0, 1)][:2]
    informe = examinar(
        [
            RelacionVecindad(a1, b1, 1, "prueba"),
            RelacionVecindad(a2, b2, -1, "prueba"),
        ],
        cociente,
    )
    assert informe.esta_refutada
    assert informe.veredicto == REFUTADA
    assert len(informe.contradicciones) == 1
    assert informe.contradicciones[0].clase == (0, 1)


def test_el_sentido_del_salto_se_orienta_solo(cociente: Cociente) -> None:
    """Firmar b->a con -s es lo mismo que firmar a->b con +s: no es contradiccion."""
    a, b = cociente.clases[(0, 1)][0]
    informe = examinar(
        [
            RelacionVecindad(a, b, 1, "prueba"),
            RelacionVecindad(b, a, -1, "prueba"),
        ],
        cociente,
    )
    assert not informe.esta_refutada
    assert len(informe.saltos_por_clase) == 1


def test_un_ciclo_coherente_no_refuta_nada(cociente: Cociente) -> None:
    """0->1->3 y 0->2->3 dan lo mismo con estos signos: el ciclo cierra."""
    firmas = []
    for clase, salto in (((0, 1), 1), ((1, 3), 1), ((2, 3), 1), ((0, 2), 1)):
        a, b = cociente.clases[clase][0]
        if cociente.de_orbita[a] > cociente.de_orbita[b]:
            a, b = b, a
        firmas.append(RelacionVecindad(a, b, salto, "prueba"))
    informe = examinar(firmas, cociente)
    assert not informe.esta_refutada
    assert informe.orbitas_libres == 8  # las cuatro atadas cuentan como una


def test_un_ciclo_que_no_cierra_refuta(cociente: Cociente) -> None:
    """Mismo ciclo, un salto cambiado: 0->1->3 da 2 y 0->2->3 da 6."""
    firmas = []
    for clase, salto in (((0, 1), 1), ((1, 3), 1), ((2, 3), 1), ((0, 2), 5)):
        a, b = cociente.clases[clase][0]
        # orientar de la orbita menor a la mayor, como hace el modulo
        if cociente.de_orbita[a] > cociente.de_orbita[b]:
            a, b = b, a
        firmas.append(RelacionVecindad(a, b, salto, "prueba"))
    informe = examinar(firmas, cociente)
    assert informe.esta_refutada
    assert "ciclo" in informe.ciclo_roto.lower() or informe.ciclo_roto


def test_un_arbol_generador_deja_una_sola_incognita(cociente: Cociente) -> None:
    """Diez diferencias independientes fijan las once orbitas salvo la cota absoluta."""
    vistos: set[int] = set()
    firmas = []
    for clase in sorted(cociente.clases, key=lambda c: (c[0], c[1])):
        i, j = clase
        if i in vistos and j in vistos:
            continue  # cerraria un ciclo; el arbol no los necesita
        a, b = cociente.clases[clase][0]
        if cociente.de_orbita[a] > cociente.de_orbita[b]:
            a, b = b, a
        firmas.append(RelacionVecindad(a, b, 1, "prueba"))
        vistos.update((i, j))
    assert len(firmas) == 10
    informe = examinar(firmas, cociente)
    assert not informe.esta_refutada
    assert informe.orbitas_libres == 1  # solo falta la cota absoluta


def test_una_cara_desconocida_falla_en_vez_de_ignorarse(cociente: Cociente) -> None:
    with pytest.raises(KeyError):
        examinar([RelacionVecindad("c999", "c000", 1, "prueba")], cociente)


def test_un_salto_sin_evidencia_no_se_puede_ni_construir() -> None:
    with pytest.raises(ValueError, match="evidencia"):
        RelacionVecindad("c000", "c001", 1, "")
