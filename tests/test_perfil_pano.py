"""Cotas del piloto respecto a la sección y control del encaje anterior."""

import json
from pathlib import Path

import numpy as np
import pytest

from scripts.hiladas_ventanas import perfil_pano, APICE_MODELO, FILA_APICE

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def alzado():
    return json.loads((ROOT / "datos/alzado_sala.json").read_text())


def test_las_33_crestas_conservan_su_cota_de_seccion(alzado):
    _, ordenes, _, junta = perfil_pano(3.8657, alzado, "seccion")
    # Formular la altura desde el suelo, en vez de reutilizar la expresión
    # del generador. El JSON redondea la cota del suelo a milímetros.
    suelo_px = alzado["niveles"]["suelo"]["fila_px"]
    suelo_m = alzado["niveles"]["suelo"]["z_m"]
    for i, orden in enumerate(ordenes):
        for _, eje, _, fila in orden:
            esperado = suelo_m + (suelo_px - fila) / alzado["px_por_m"]
            assert abs(junta(eje, i) - esperado) < 0.0005


def test_los_dos_ordenes_no_se_cruzan_en_la_junta(alzado):
    semi, _, estaciones, junta = perfil_pano(3.8657, alzado, "seccion")
    for u in sorted(set(estaciones) | set(np.linspace(-semi, semi, 1001))):
        assert junta(u, 1) - junta(u, 0) >= 0.061 - 1e-12
        assert junta(u, 2) == 0


def test_el_control_0036_conserva_el_apice_y_el_limite(alzado):
    _, ordenes, estaciones, junta = perfil_pano(3.8657, alzado, "0036")
    arco = next(t for t in ordenes[0] if t[3] == FILA_APICE)
    assert junta(arco[1], 0) == pytest.approx(APICE_MODELO)
    assert max(junta(u, 1) for u in estaciones) <= -0.013


def test_encaje_desconocido_no_se_interpreta_como_seccion(alzado):
    with pytest.raises(ValueError):
        perfil_pano(3.8657, alzado, "otro")
