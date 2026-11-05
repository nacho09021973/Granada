"""Controles de los siete prismas de `granada.piezas`."""

from collections import Counter

import pytest

from granada.piezas import ALTURA_PRISMA, NIVELES, PASO_NIVEL, TIPOS, malla, pieza


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
