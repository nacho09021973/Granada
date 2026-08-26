"""Pruebas de la extraccion de caras y de su clasificacion en figuras planas.

Toda comprobacion positiva lleva su control: una figura ajena al sistema
documentado que debe quedar sin clasificar con la misma tolerancia.
"""

from __future__ import annotations

import math

import pytest

from granada.caras import (
    CONTORNO,
    Cara,
    centroide,
    corta_al_eje,
    margen_al_eje,
    orbitas_por_simetria,
    FiguraPlana,
    GrafoNoAdmisible,
    PLANTILLAS,
    Plantilla,
    ajuste_a_plantilla,
    clasificar,
    cruces_de_aristas,
    extraer_caras,
    tolerancia_por_resolucion,
)


TOLERANCIA = 3.0


def poligono_regular(lados: int, radio: float = 1.0, giro: float = 0.0):
    return [
        (
            radio * math.cos(giro + 2 * math.pi * i / lados),
            radio * math.sin(giro + 2 * math.pi * i / lados),
        )
        for i in range(lados)
    ]


def ciclo(n: int) -> list[tuple[int, int]]:
    return [(i, (i + 1) % n) for i in range(n)]


def unica_cara(nodos, aristas) -> Cara:
    resultado = extraer_caras(nodos, aristas)
    assert resultado.numero_de_caras == 1
    return resultado.caras[0]


# --- extraccion ------------------------------------------------------------


def test_un_cuadrado_da_una_cara_interior_y_un_contorno() -> None:
    nodos = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    resultado = extraer_caras(nodos, ciclo(4))

    assert resultado.numero_de_caras == 1
    cara = resultado.caras[0]
    assert cara.numero_de_lados == 4
    assert math.isclose(cara.area, 1.0)
    assert math.isclose(resultado.area_contorno, 1.0)
    assert all(math.isclose(a, 90.0) for a in cara.angulos)
    assert cara.es_convexa
    assert math.isclose(cara.perimetro, 4.0)


def test_la_cara_interior_se_recorre_en_sentido_antihorario() -> None:
    nodos = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    cara = unica_cara(nodos, ciclo(4))
    orden = cara.vertices
    desplazado = orden.index(0)
    assert tuple(orden[(desplazado + i) % 4] for i in range(4)) == (0, 1, 2, 3)


def test_dos_cuadrados_contiguos_comparten_una_vecindad() -> None:
    nodos = [
        (0.0, 0.0), (1.0, 0.0), (2.0, 0.0),
        (2.0, 1.0), (1.0, 1.0), (0.0, 1.0),
    ]
    aristas = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (1, 4)]
    resultado = extraer_caras(nodos, aristas)

    assert resultado.numero_de_caras == 2
    assert math.isclose(resultado.area_total, 2.0)
    interiores = [v for v in resultado.vecindades if not v.es_de_borde]
    assert len(interiores) == 1
    assert interiores[0].aristas == ((1, 4),)
    bordes = resultado.vecindades_de_borde
    assert len(bordes) == 2
    assert all(v.cara_b == CONTORNO for v in bordes)
    assert sum(len(v.aristas) for v in bordes) == 6


def test_una_arista_colgante_es_un_puente_y_no_crea_cara() -> None:
    nodos = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (2.0, 0.5)]
    aristas = ciclo(4) + [(1, 4)]
    resultado = extraer_caras(nodos, aristas)

    assert resultado.numero_de_caras == 1
    assert resultado.aristas_puente == ((1, 4),)
    assert math.isclose(resultado.caras[0].area, 1.0)


def test_las_areas_de_las_caras_suman_el_area_del_contorno() -> None:
    nodos = poligono_regular(8) + [(0.0, 0.0)]
    aristas = ciclo(8) + [(i, 8) for i in range(8)]
    resultado = extraer_caras(nodos, aristas)

    assert resultado.numero_de_caras == 8
    assert math.isclose(resultado.area_total, resultado.area_contorno, rel_tol=1e-12)


def test_una_cara_en_ele_no_es_convexa() -> None:
    nodos = [
        (0.0, 0.0), (2.0, 0.0), (2.0, 1.0),
        (1.0, 1.0), (1.0, 2.0), (0.0, 2.0),
    ]
    cara = unica_cara(nodos, ciclo(6))
    assert not cara.es_convexa
    assert max(cara.angulos) > 180.0
    assert math.isclose(cara.area, 3.0)


def test_el_numero_de_caras_cumple_la_formula_de_euler() -> None:
    nodos = poligono_regular(6) + [(0.0, 0.0)]
    aristas = ciclo(6) + [(i, 6) for i in range(6)]
    resultado = extraer_caras(nodos, aristas)
    caras_totales = resultado.numero_de_caras + 1
    assert len(nodos) - len(aristas) + caras_totales == 2


@pytest.mark.parametrize(
    "aristas, mensaje",
    [
        ([(0, 1), (1, 2), (2, 0), (0, 1)], "repetida"),
        ([(0, 1), (1, 2), (2, 0), (1, 1)], "lazo"),
    ],
)
def test_el_grafo_mal_formado_se_rechaza(aristas, mensaje) -> None:
    nodos = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    with pytest.raises(GrafoNoAdmisible, match=mensaje):
        extraer_caras(nodos, aristas)


def test_un_grafo_desconectado_se_rechaza_en_vez_de_inventar_contorno() -> None:
    nodos = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (5.0, 5.0), (6.0, 5.0), (5.0, 6.0)]
    aristas = [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)]
    with pytest.raises(GrafoNoAdmisible, match="componente"):
        extraer_caras(nodos, aristas)


def test_un_dibujo_con_cruces_no_pasa_por_caras() -> None:
    nodos = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)]
    aristas = ciclo(4) + [(0, 2), (1, 3)]
    assert cruces_de_aristas(nodos, aristas) == (((0, 2), (1, 3)),)
    with pytest.raises(GrafoNoAdmisible, match="Euler"):
        extraer_caras(nodos, aristas)


def test_un_dibujo_plano_no_tiene_cruces() -> None:
    nodos = poligono_regular(8) + [(0.0, 0.0)]
    aristas = ciclo(8) + [(i, 8) for i in range(8)]
    assert cruces_de_aristas(nodos, aristas) == ()


# --- clasificacion ---------------------------------------------------------


def test_las_plantillas_documentadas_son_poligonos_coherentes() -> None:
    for figura, plantilla in PLANTILLAS.items():
        assert isinstance(plantilla, Plantilla)
        assert figura is not FiguraPlana.SIN_CLASIFICAR
    with pytest.raises(ValueError, match="suman"):
        Plantilla((90.0, 45.0, 60.0), (1.0, 1.0, 1.0))


def test_medio_cuadrado_triangulo_rectangulo_isosceles() -> None:
    nodos = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    figura, desviacion_angular, desviacion_lado = clasificar(
        unica_cara(nodos, ciclo(3)), TOLERANCIA
    )
    assert figura is FiguraPlana.MEDIO_CUADRADO
    assert desviacion_angular < 1e-9
    assert desviacion_lado < 1e-9


def test_media_jaira_triangulo_de_45_y_dos_de_67_5() -> None:
    apice = math.radians(22.5)
    nodos = [
        (0.0, 0.0),
        (math.cos(apice), math.sin(apice)),
        (math.cos(apice), -math.sin(apice)),
    ]
    figura, _, _ = clasificar(unica_cara(nodos, ciclo(3)), TOLERANCIA)
    assert figura is FiguraPlana.MEDIA_JAIRA


def test_jaira_rombo_completo_de_45_y_135() -> None:
    lado = math.radians(45)
    nodos = [
        (0.0, 0.0),
        (1.0, 0.0),
        (1 + math.cos(lado), math.sin(lado)),
        (math.cos(lado), math.sin(lado)),
    ]
    figura, _, _ = clasificar(unica_cara(nodos, ciclo(4)), TOLERANCIA)
    assert figura is FiguraPlana.JAIRA


def test_cuadrado_y_octogono_regulares() -> None:
    for lados, esperada in ((4, FiguraPlana.CUADRADO), (8, FiguraPlana.OCTOGONO)):
        cara = unica_cara(poligono_regular(lados), ciclo(lados))
        figura, _, _ = clasificar(cara, TOLERANCIA)
        assert figura is esperada


def test_la_clasificacion_no_depende_del_giro_ni_de_la_escala() -> None:
    for giro in (0.0, 0.31, 1.7, 3.9):
        for escala in (0.05, 1.0, 40.0):
            cara = unica_cara(poligono_regular(4, escala, giro), ciclo(4))
            assert clasificar(cara, TOLERANCIA)[0] is FiguraPlana.CUADRADO


def test_la_clasificacion_no_depende_de_la_reflexion() -> None:
    nodos = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    reflejados = [(x, -y) for x, y in nodos]
    assert clasificar(unica_cara(reflejados, ciclo(3)), TOLERANCIA)[0] is (
        FiguraPlana.MEDIO_CUADRADO
    )


@pytest.mark.parametrize(
    "nombre, nodos",
    [
        ("triangulo equilatero", poligono_regular(3)),
        ("pentagono regular", poligono_regular(5)),
        ("hexagono regular", poligono_regular(6)),
        ("rectangulo 1 a 1.4", [(0.0, 0.0), (1.4, 0.0), (1.4, 1.0), (0.0, 1.0)]),
        (
            "rombo de 60",
            [
                (0.0, 0.0),
                (1.0, 0.0),
                (1.5, math.sqrt(3) / 2),
                (0.5, math.sqrt(3) / 2),
            ],
        ),
    ],
)
def test_control_las_figuras_ajenas_quedan_sin_clasificar(nombre, nodos) -> None:
    cara = unica_cara(nodos, ciclo(len(nodos)))
    figura, _, _ = clasificar(cara, TOLERANCIA)
    assert figura is FiguraPlana.SIN_CLASIFICAR, nombre


def test_el_rectangulo_se_rechaza_por_los_lados_no_por_los_angulos() -> None:
    cara = unica_cara([(0.0, 0.0), (1.4, 0.0), (1.4, 1.0), (0.0, 1.0)], ciclo(4))
    desviacion_angular, desviacion_lado = ajuste_a_plantilla(
        cara, PLANTILLAS[FiguraPlana.CUADRADO]
    )
    assert desviacion_angular < 1e-9
    assert desviacion_lado > 0.12


def test_una_plantilla_no_ajusta_a_un_numero_distinto_de_lados() -> None:
    cara = unica_cara(poligono_regular(4), ciclo(4))
    desviaciones = ajuste_a_plantilla(cara, PLANTILLAS[FiguraPlana.OCTOGONO])
    assert desviaciones == (math.inf, math.inf)


def test_una_tolerancia_mas_estrecha_deja_de_clasificar_lo_deformado() -> None:
    nodos = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (-0.06, 1.0)]
    cara = unica_cara(nodos, ciclo(4))
    assert clasificar(cara, 6.0)[0] is FiguraPlana.CUADRADO
    assert clasificar(cara, 1.0)[0] is FiguraPlana.SIN_CLASIFICAR


def test_sin_clasificar_informa_de_la_plantilla_mas_proxima() -> None:
    cara = unica_cara(poligono_regular(3), ciclo(3))
    figura, desviacion_angular, desviacion_lado = clasificar(cara, TOLERANCIA)
    assert figura is FiguraPlana.SIN_CLASIFICAR
    # la plantilla mas proxima es la media jaira: 60 grados frente a 45
    assert math.isclose(desviacion_angular, 15.0, abs_tol=1e-9)
    assert math.isfinite(desviacion_lado)


def test_la_tolerancia_por_resolucion_escala_con_el_lado_mas_corto() -> None:
    grande = unica_cara(poligono_regular(4, 1.0), ciclo(4))
    pequena = unica_cara(poligono_regular(4, 0.1), ciclo(4))
    assert tolerancia_por_resolucion(pequena, 0.01) > tolerancia_por_resolucion(
        grande, 0.01
    )
    esperada = math.degrees(2 * 0.01 / grande.lado_minimo)
    assert math.isclose(tolerancia_por_resolucion(grande, 0.01), esperada)
    with pytest.raises(ValueError):
        tolerancia_por_resolucion(grande, 0.0)


def test_una_cara_no_puede_tener_area_nula_ni_dos_vertices() -> None:
    with pytest.raises(ValueError):
        Cara(vertices=(0, 1), angulos=(90.0, 90.0), lados=(1.0, 1.0), area=1.0)
    with pytest.raises(ValueError):
        Cara(vertices=(0, 1, 2), angulos=(60.0,) * 3, lados=(1.0,) * 3, area=0.0)


# --- centroide de area, ejes y orbitas -------------------------------------


def test_el_centroide_de_area_no_se_mueve_al_anadir_un_vertice() -> None:
    """Es la razon de no usar la media de vertices para comparar copias."""

    nodos = [(0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0)]
    cuadrado = unica_cara(nodos, ciclo(4))
    # El mismo cuadrado con un vertice de mas en mitad del lado derecho.
    con_extra = [(0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (2.0, 2.0), (0.0, 2.0)]
    remuestreado = unica_cara(con_extra, ciclo(5))

    for eje in (0, 1):
        assert math.isclose(
            centroide(cuadrado, nodos)[eje],
            centroide(remuestreado, con_extra)[eje],
            abs_tol=1e-12,
        )
    media_original = sum(p[0] for p in nodos) / 4
    media_remuestreada = sum(p[0] for p in con_extra) / 5
    assert not math.isclose(media_original, media_remuestreada)


def test_el_centroide_de_area_de_un_poligono_regular_es_su_centro() -> None:
    nodos = poligono_regular(8, 3.0, 0.4)
    cara = unica_cara(nodos, ciclo(8))
    x, y = centroide(cara, nodos)
    assert math.isclose(x, 0.0, abs_tol=1e-12)
    assert math.isclose(y, 0.0, abs_tol=1e-12)


def test_un_eje_corta_la_cara_solo_si_la_atraviesa() -> None:
    nodos = [(1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0)]
    cara = unica_cara(nodos, ciclo(4))
    assert corta_al_eje(cara, nodos, (0.0, 0.0), 0.0)      # el eje horizontal
    assert not corta_al_eje(cara, nodos, (0.0, 0.0), 90.0)  # el vertical, no
    lejos = [(1.0, 2.0), (3.0, 2.0), (3.0, 4.0), (1.0, 4.0)]
    assert not corta_al_eje(unica_cara(lejos, ciclo(4)), lejos, (0.0, 0.0), 0.0)


def test_el_margen_dice_por_cuanto_corta_o_por_cuanto_falla() -> None:
    dentro = [(1.0, -0.25), (3.0, -0.25), (3.0, 1.0), (1.0, 1.0)]
    cara = unica_cara(dentro, ciclo(4))
    assert math.isclose(margen_al_eje(cara, dentro, (0.0, 0.0), 0.0), 0.25)
    fuera = [(1.0, 0.5), (3.0, 0.5), (3.0, 2.0), (1.0, 2.0)]
    cara = unica_cara(fuera, ciclo(4))
    assert math.isclose(margen_al_eje(cara, fuera, (0.0, 0.0), 0.0), -0.5)


def test_un_roce_por_debajo_del_margen_no_cuenta_como_corte() -> None:
    """Una cara que asoma una milesima al otro lado no la corta la seccion."""

    roce = [(1.0, -0.001), (3.0, -0.001), (3.0, 1.0), (1.0, 1.0)]
    cara = unica_cara(roce, ciclo(4))
    assert corta_al_eje(cara, roce, (0.0, 0.0), 0.0)
    assert not corta_al_eje(cara, roce, (0.0, 0.0), 0.0, margen=0.01)


def construir_corona(copias: int, radio: float, giro: float = 0.0):
    """``copias`` cuadraditos iguales repartidos en circulo, mas sus aristas."""

    nodos = []
    aristas = []
    for k in range(copias):
        angulo = giro + 2 * math.pi * k / copias
        cx, cy = radio * math.cos(angulo), radio * math.sin(angulo)
        base = len(nodos)
        nodos.extend(
            [
                (cx - 0.1, cy - 0.1), (cx + 0.1, cy - 0.1),
                (cx + 0.1, cy + 0.1), (cx - 0.1, cy + 0.1),
            ]
        )
        aristas.extend([(base + i, base + (i + 1) % 4) for i in range(4)])
    return nodos, aristas


def test_las_copias_repartidas_a_45_grados_forman_una_orbita() -> None:
    nodos, aristas = construir_corona(8, 1.0)
    caras = [extraer_caras(n, a).caras[0] for n, a in
             [(nodos[i * 4:(i + 1) * 4], [(0, 1), (1, 2), (2, 3), (3, 0)])
              for i in range(8)]]
    puntos_por_cara = [nodos[i * 4:(i + 1) * 4] for i in range(8)]
    # Reconstruye indices globales para pasar un unico conjunto de puntos.
    globales = [
        Cara(
            vertices=tuple(i * 4 + v for v in cara.vertices),
            angulos=cara.angulos,
            lados=cara.lados,
            area=cara.area,
        )
        for i, (cara, _) in enumerate(zip(caras, puntos_por_cara))
    ]
    orbitas = orbitas_por_simetria(globales, nodos, (0.0, 0.0), 8)
    assert len(orbitas) == 1
    assert len(orbitas[0]) == 8


def test_dos_coronas_de_radio_distinto_son_dos_orbitas() -> None:
    nodos = []
    caras = []
    for radio in (1.0, 2.0):
        base = len(nodos)
        trozos, _ = construir_corona(8, radio)
        nodos.extend(trozos)
        for k in range(8):
            inicio = base + k * 4
            caras.append(
                Cara(
                    vertices=tuple(range(inicio, inicio + 4)),
                    angulos=(90.0,) * 4,
                    lados=(0.2,) * 4,
                    area=0.04,
                )
            )
    orbitas = orbitas_por_simetria(caras, nodos, (0.0, 0.0), 8)
    assert len(orbitas) == 2
    assert sorted(len(o) for o in orbitas) == [8, 8]


def test_una_cara_centrada_es_su_propia_orbita() -> None:
    nodos = poligono_regular(8, 0.5)
    centrada = Cara(
        vertices=tuple(range(8)),
        angulos=(135.0,) * 8,
        lados=(0.38,) * 8,
        area=0.7,
    )
    orbitas = orbitas_por_simetria([centrada], nodos, (0.0, 0.0), 8)
    assert orbitas == ((0,),)


def test_las_tolerancias_de_orbita_se_validan() -> None:
    nodos = poligono_regular(4)
    cara = unica_cara(nodos, ciclo(4))
    with pytest.raises(ValueError):
        orbitas_por_simetria([cara], nodos, (0.0, 0.0), 0)
    with pytest.raises(ValueError):
        orbitas_por_simetria([cara], nodos, (0.0, 0.0), 8, tolerancia=0.0)
