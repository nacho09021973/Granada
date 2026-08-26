"""Controles del tamano del problema de niveles bajo la simetria medida.

El numero que importa aqui es cuantos niveles distintos habria que fijar si la
nivelacion respetara la simetria de la cupula. Es una hipotesis; estas pruebas
vigilan que el recuento sea correcto y que no dependa de una tolerancia
elegida a conveniencia.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


RAIZ = Path(__file__).parents[1]
RUTA = RAIZ / "datos" / "orbitas_caras.json"
RUTA_CARAS = RAIZ / "datos" / "caras_red.json"


def cargar() -> dict:
    return json.loads(RUTA.read_text(encoding="utf-8"))


def test_declara_de_donde_sale_y_con_que_hipotesis() -> None:
    dato = cargar()
    assert dato["version"] == 1
    assert dato["fuente"]["derivado_de"] == "datos/caras_red.json"
    esperado = hashlib.sha256(RUTA_CARAS.read_bytes()).hexdigest()
    assert dato["fuente"]["sha256_caras"] == esperado
    assert "hipotesis" in dato["metodo"]
    assert "falsable" in dato["metodo"]["hipotesis"]
    assert dato["estado"] == "BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS"


def test_la_cadena_de_reduccion_cuadra() -> None:
    controles = cargar()["controles"]
    assert controles["caras"] == 105
    assert controles["vecindades_interiores"] == 211
    assert controles["ciclos_independientes"] == 107
    # 211 saltos menos 107 ciclos = 104 niveles independientes = 105 - 1.
    assert (
        controles["vecindades_interiores"] - controles["ciclos_independientes"]
        == controles["niveles_independientes_sin_simetria"]
        == 104
    )


def test_hay_once_orbitas_y_todas_de_tamano_admisible() -> None:
    controles = cargar()["controles"]
    assert controles["orbitas"] == 11
    assert controles["tamanos_de_orbita"] == [16, 16, 16, 8, 8, 8, 8, 8, 8, 8, 1]
    assert controles["suma_de_tamanos"] == 105
    # Un tamano de orbita tiene que dividir al orden del grupo, 16.
    assert controles["tamanos_que_no_dividen_al_grupo"] == []


def test_el_once_no_depende_de_la_tolerancia_elegida() -> None:
    barrido = cargar()["controles"]["barrido_de_tolerancias"]
    validas = [fila for fila in barrido if fila["todos_dividen_al_grupo"]]
    assert len(validas) >= 20
    assert {fila["orbitas"] for fila in validas} == {11}
    # La unica combinacion que rompe es la mas estrecha en area, y se delata
    # sola: deja una orbita de tamano que no divide al grupo.
    rotas = [fila for fila in barrido if not fila["todos_dividen_al_grupo"]]
    assert all(fila["tolerancia_area"] == 0.15 for fila in rotas)
    assert all(fila["orbitas"] == 12 for fila in rotas)


def test_las_orbitas_particionan_las_caras_sin_solaparse() -> None:
    dato = cargar()
    caras = json.loads(RUTA_CARAS.read_text(encoding="utf-8"))["caras"]
    identificadores = {c["id"] for c in caras}
    vistas: set[str] = set()
    for orbita in dato["orbitas"]:
        assert orbita["tamano"] == len(orbita["caras"])
        assert not vistas & set(orbita["caras"])
        vistas.update(orbita["caras"])
        assert set(orbita["caras"]) <= identificadores
    assert vistas == identificadores


def test_las_orbitas_de_dieciseis_no_tocan_ningun_eje_por_su_centro() -> None:
    """Estabilizador trivial: ninguna de sus caras esta centrada en un eje."""

    dato = cargar()
    grandes = [o for o in dato["orbitas"] if o["tamano"] == 16]
    assert len(grandes) == 3
    for orbita in grandes:
        azimuts = orbita["azimuts_grados"]
        assert len(azimuts) == 16
        # Ninguna cara centrada en un multiplo de 22,5 grados, que son los ejes.
        assert all(min(a % 22.5, 22.5 - a % 22.5) > 1.0 for a in azimuts)


def test_una_seccion_por_un_eje_toca_seis_o_siete_orbitas() -> None:
    cobertura = cargar()["controles"]["cobertura_por_clase_de_eje"]
    assert cobertura["A"]["orbitas_cortadas"] == 6
    assert cobertura["B"]["orbitas_cortadas"] == 7
    assert cobertura["A"]["caras_cortadas"] == 11
    assert cobertura["B"]["caras_cortadas"] == 13
    # Quedan por determinar 11 - 6 y 11 - 7. No se descuenta ninguna altura
    # libre: la seccion da cotas absolutas.
    assert len(cobertura["A"]["orbitas_sin_cortar"]) == 5
    assert len(cobertura["B"]["orbitas_sin_cortar"]) == 4


def test_pero_solo_cinco_y_cuatro_sobreviven_a_la_resolucion() -> None:
    """El corte de un roce sub-pixel no es un corte del dibujo."""

    dato = cargar()
    cobertura = dato["controles"]["cobertura_por_clase_de_eje"]
    assert cobertura["A"]["orbitas_cortadas_resolubles"] == 5
    assert cobertura["B"]["orbitas_cortadas_resolubles"] == 4
    assert cobertura["A"]["caras_determinadas_resolubles"] == 33
    assert cobertura["B"]["caras_determinadas_resolubles"] == 25
    assert len(cobertura["A"]["orbitas_sin_cortar_resolubles"]) == 6
    assert len(cobertura["B"]["orbitas_sin_cortar_resolubles"]) == 7
    assert dato["metodo"]["resolucion_m"] < 0.015


def test_los_cortes_que_se_caen_son_roces_de_menos_de_medio_pixel() -> None:
    """No hay zona gris: los que caen y los que quedan no se solapan."""

    dato = cargar()
    resolucion = dato["metodo"]["resolucion_m"]
    caidos = []
    for orbita in dato["orbitas"]:
        for clave, margenes in orbita["margen_al_eje_m"].items():
            if orbita["cortada_de_forma_resoluble"][clave]:
                continue
            caidos.extend(margenes.values())
    assert caidos
    assert max(caidos) < 0.5 * resolucion
    supervivientes = [
        m
        for orbita in dato["orbitas"]
        for clave, margenes in orbita["margen_al_eje_m"].items()
        if orbita["cortada_de_forma_resoluble"][clave]
        for m in margenes.values()
    ]
    # Ninguno llega a medio pixel; el mas justo de los que quedan pasa de
    # diecisiete. Entre las dos poblaciones hay un factor de cuarenta: el
    # criterio no parte una nube continua, separa dos cosas distintas.
    assert min(supervivientes) > 15 * resolucion
    assert min(supervivientes) > 40 * max(caidos)


def test_ningun_eje_alcanza_las_tres_orbitas_de_dieciseis() -> None:
    dato = cargar()
    cobertura = dato["controles"]["cobertura_por_clase_de_eje"]
    ninguna = set(cobertura["A"]["orbitas_sin_cortar_resolubles"]) & set(
        cobertura["B"]["orbitas_sin_cortar_resolubles"]
    )
    assert len(ninguna) == 3
    assert sum(dato["orbitas"][i]["tamano"] for i in ninguna) == 48
    for indice in ninguna:
        assert dato["orbitas"][indice]["tamano"] == 16


def test_las_fronteras_del_eje_separan_tantas_bandas_como_orbitas() -> None:
    """El perfil de la planta a lo largo del eje, que es lo que ve la seccion."""

    dato = cargar()
    fronteras = dato["controles"]["fronteras_en_el_eje_m"]
    cobertura = dato["controles"]["cobertura_por_clase_de_eje"]
    for clave in ("A", "B"):
        # Una frontera por cada salto entre bandas: tantas como orbitas
        # cortadas de forma resoluble, contando la ultima contra el borde.
        assert len(fronteras[clave]) == cobertura[clave][
            "orbitas_cortadas_resolubles"
        ]
        assert fronteras[clave] == sorted(fronteras[clave])
        assert 0.0 < fronteras[clave][0]
        assert fronteras[clave][-1] < 3.5


def test_el_recuento_es_de_la_clase_y_no_del_eje_representante() -> None:
    """Los cuatro ejes de una clase tienen que decir lo mismo."""

    invariancia = cargar()["controles"]["invariancia_dentro_de_la_clase"]
    for clave, esperado in (("A", 5), ("B", 4)):
        ejes = invariancia[clave]
        assert len(ejes) == 4
        assert {tuple(e["orbitas_resolubles"]) for e in ejes} == {
            tuple(ejes[0]["orbitas_resolubles"])
        }
        assert len(ejes[0]["orbitas_resolubles"]) == esperado
        assert {e["caras_tocadas"] for e in ejes} == {ejes[0]["caras_tocadas"]}


def test_las_fronteras_no_dependen_de_que_eje_de_la_clase_sea() -> None:
    """Y por eso la proyeccion sobre la seccion no depende de la orientacion."""

    ejes = cargar()["controles"]["invariancia_dentro_de_la_clase"]["A"]
    comunes = min(len(e["fronteras_m"]) for e in ejes)
    for indice in range(comunes):
        valores = [e["fronteras_m"][indice] for e in ejes]
        # La horquilla va de 2,6 a 9,6 mm: del mismo orden que el residuo de
        # 9,5 mm con el que las fronteras casan con los escalones de la
        # seccion. No es despreciable, es el suelo de lo que el dibujo da.
        assert max(valores) - min(valores) < 0.010


def test_la_asimetria_izquierda_derecha_la_explica_el_centro() -> None:
    asimetria = cargar()["controles"]["asimetria_izquierda_derecha"]
    crudo = asimetria["orbitas_con_derecha_mayor"]["centro_del_octogono"]
    ajustado = asimetria["orbitas_con_derecha_mayor"]["centro_ajustado"]
    # Con el centroide del octogono el signo sale diez de diez: parece decisivo.
    assert crudo == [10, 10]
    # Mover el centro 3 mm lo deshace entero. Era un grado de libertad.
    assert asimetria["desplazamiento_del_centro_m"] < 0.005
    assert ajustado[0] * 2 <= ajustado[1]
    assert abs(
        asimetria["mediana_relativa_derecha_menos_izquierda"]["centro_ajustado"]
    ) < 0.001


def test_el_dibujo_es_simetrico_por_debajo_de_su_propia_resolucion() -> None:
    """Y por eso no puede medirse en el la deformacion de la cupula real."""

    dato = cargar()
    rms = dato["controles"]["asimetria_izquierda_derecha"][
        "dispersion_radial_rms_m"
    ]["centro_ajustado"]
    # Menos de medio pixel del dibujo, con una simplificacion RDP de dos.
    assert rms < 0.5 * dato["metodo"]["resolucion_m"]
