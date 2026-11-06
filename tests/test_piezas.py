"""Controles de los siete prismas de `granada.piezas`."""

from collections import Counter

import pytest

from granada.piezas import ALTURA_PRISMA, NIVELES, PASO_NIVEL, TIPOS, etiquetas, malla, pieza


def test_son_siete_y_dos_ascienden_dos_niveles():
    assert TIPOS == ("A1", "A2", "A3", "B", "C1", "C2", "C3")
    assert sorted(t for t in TIPOS if NIVELES[t] == 2) == ["A3", "C3"]


@pytest.mark.parametrize("tipo", TIPOS)
def test_malla_cerrada(tipo):
    """Cada arista la comparten dos triangulos, con sentidos opuestos."""
    _, F = malla(pieza(tipo), n=12)
    dirigidas = Counter()
    for a, b, c in F:
        for u, v in ((a, b), (b, c), (c, a)):
            dirigidas[(u, v)] += 1
    for (u, v), k in dirigidas.items():
        assert k == 1, f"{tipo}: arista {u}-{v} repetida"
        assert dirigidas[(v, u)] == 1, f"{tipo}: arista {u}-{v} sin pareja"


@pytest.mark.parametrize("tipo", TIPOS)
def test_cuelga_hasta_la_pata_y_no_atraviesa_la_tapa(tipo):
    V, _ = malla(pieza(tipo), n=12)
    zs = [z for _, _, z in V]
    assert min(zs) == pytest.approx(0.0)
    assert max(zs) == pytest.approx(ALTURA_PRISMA)


@pytest.mark.parametrize("tipo", ["A3", "C3"])
def test_el_nicho_sube_al_segundo_nivel(tipo):
    V, _ = malla(pieza(tipo), n=24)
    fondo = [z for _, _, z in V if z < ALTURA_PRISMA - 1e-9]
    assert max(fondo) > PASO_NIVEL


@pytest.mark.parametrize("tipo", TIPOS)
def test_la_malla_del_fondo_sigue_las_patas(tipo):
    """Con la rejilla en abanico la pata, donde el fondo sube casi en vertical,
    cruzaba los triangulos en oblicuo y se veia en diente de sierra. Error
    maximo a n = 8, en fraccion de la altura, medido el 2026-11-06: antes
    A1 0.146, C1 0.107, A2 0.076, B 0.068, C2 0.060, A3 0.309, C3 0.427;
    con la rejilla por columnas, de 0.007 a 0.030 en las piezas de un nivel,
    A3 0.077 y C3 0.123 (queda en el costado del nicho, que no sigue)."""
    p = pieza(tipo)
    V, F = malla(p, 8)
    pesos = [(i / 6, j / 6, 1 - (i + j) / 6) for i in range(7) for j in range(7 - i)]
    peor = 0.0
    for tri, e in zip(F, etiquetas(p, V, F)):
        if e != "fondo":
            continue
        A, B, C = (V[k] for k in tri)
        for l0, l1, l2 in pesos:
            x = l0 * A[0] + l1 * B[0] + l2 * C[0]
            y = l0 * A[1] + l1 * B[1] + l2 * C[1]
            z = l0 * A[2] + l1 * B[2] + l2 * C[2]
            peor = max(peor, abs(z - p.fondo(x, y)))
    tope = 0.15 if NIVELES[tipo] == 2 else 0.035
    assert peor < tope * ALTURA_PRISMA, f"{tipo}: {peor / ALTURA_PRISMA:.3f} de la altura"
