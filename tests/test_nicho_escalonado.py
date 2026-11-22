"""Boca escalonada y encaje «silueta» (0043) contra sus medidas."""

import json
from pathlib import Path

import numpy as np
import pytest

from scripts.hiladas_ventanas import CENTROS_VANOS, DESCENSO_SILUETA_M, perfil_pano
from scripts.nicho_escalonado import (
    BANDA, ESCALONES, FONDO_BOCA, MOLDURA, SEMIANCHO_MARCO, arco_celosia, contorno, nudos, tope_exterior,
)

ROOT = Path(__file__).resolve().parents[1]
APOTEMA = 3.8657066822052
ORDEN = ("merlon", "hombro", "entrante", "pinaculo", "esquina")


@pytest.fixture
def alzado():
    return json.loads((ROOT / "datos/alzado_sala.json").read_text())


def test_escalones_son_los_medidos():
    r = json.loads((ROOT / "datos/remate_nichos.json").read_text())
    for (s, z), e in zip(ESCALONES, ORDEN):
        p = r["perfil"][e]
        assert s == pytest.approx(p["s_ext"], abs=1e-4)
        assert z == pytest.approx(p["z_modelo"], abs=1e-4)
        # Segunda vía: la vista frontal de la sección, dentro de 3 cm.
        assert abs(p["z_modelo"] - p["z_seccion_frontal"]) < 0.03
    assert BANDA == pytest.approx(r["semiancho_marco_m"]["media"] - r["semiancho_boca_m"]["media"], abs=0.002)


def test_descenso_sale_de_la_silueta_lateral(alzado):
    vs = json.loads((ROOT / "datos/vuelo_seccion.json").read_text())
    fin = np.mean([min(z for z, d in sorted(l["perfil"]) if d is not None and d > 0.02 and z > -0.3)
                   for u in vs["umbrales"].values() for l in u.values()])
    semi, _, us, junta = perfil_pano(APOTEMA, alzado, "seccion")
    fuera = [u for u in np.linspace(-semi, semi, 4001) if all(abs(u - cx) > SEMIANCHO_MARCO for cx in CENTROS_VANOS)]
    assert DESCENSO_SILUETA_M == pytest.approx(max(junta(u, 0) for u in fuera) - fin, abs=0.001)


def test_silueta_fuera_y_dentro_de_los_marcos(alzado):
    semi, _, us, junta = perfil_pano(APOTEMA, alzado, "silueta")
    _, _, _, seccion = perfil_pano(APOTEMA, alzado, "seccion")
    for u in sorted(set(us) | set(np.linspace(-semi, semi, 1201))):
        cx = min(CENTROS_VANOS, key=lambda c: abs(u - c))
        if abs(u - cx) <= SEMIANCHO_MARCO + 1e-12:
            assert junta(u, 0) == tope_exterior(u - cx)
        else:
            assert junta(u, 0) == pytest.approx(seccion(u, 0) - DESCENSO_SILUETA_M)
            assert junta(u, 0) <= -0.148
        assert junta(u, 1) - junta(u, 0) >= 0.061 - 1e-12
    # Los nudos del marco son estaciones: el muro comparte vértices con las adarajas.
    for cx in CENTROS_VANOS:
        for s, _ in nudos(0.0):
            assert min(abs(u - (cx + s)) for u in us) < 1e-9


def test_anillos_con_la_misma_topologia_y_sin_retroceso():
    muestras = list(np.linspace(-SEMIANCHO_MARCO, SEMIANCHO_MARCO, 57))
    for tope in (None, -0.012):
        largos = set()
        for f, _, _ in MOLDURA + [(FONDO_BOCA / BANDA, 0, "")]:
            lazo = contorno(0.0, f * BANDA, -1.346, tope, muestras)
            largos.add(len(lazo))
            s = np.array([p[0] for p in lazo[2:]])
            assert np.all(np.diff(s) <= 1e-12), "el tope debe avanzar de derecha a izquierda"
            assert lazo[2][0] == lazo[1][0] and lazo[-1][0] == lazo[0][0]
        assert len(largos) == 1


def test_la_celosia_cabe_bajo_la_boca():
    alf = -1.346
    for tope in (None, -0.012):
        lazo = contorno(0.0, FONDO_BOCA, alf, tope)
        top = lazo[2:][::-1]
        arco = np.array(arco_celosia(0.0, alf))
        techo = np.interp(arco[2:, 0], [p[0] for p in top], [p[1] for p in top])
        # Mínimo del techo bajo cada tramo del arco, para no saltar un diente.
        assert np.all(arco[2:, 1] < techo - 0.005)
        for s in np.linspace(arco[:, 0].min(), arco[:, 0].max(), 400):
            z_arco = np.interp(s, *zip(*sorted(map(tuple, arco[2:]))))
            assert z_arco < np.interp(s, [p[0] for p in top], [p[1] for p in top]) - 0.005
        assert arco[0, 1] > lazo[0][1] and abs(arco[0, 0]) < abs(lazo[0][0])
