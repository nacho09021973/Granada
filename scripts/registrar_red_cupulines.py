"""Registra la red de medinas en el marco de la cupula por piezas.

La red (datos/red_medinas.json) esta en metros, en el marco del dibujo de la
tesis de Ferrer (figura 128). La cupula por piezas y los cupulines
(datos/cupulines.json) estan en el marco de la ortoimagen.

Metodo:
- Giro 0. El registro original de la red sobre la ortoimagen (commit ea9393e)
  solo tenia centro, escala y eje de espejo, sin giro: el dibujo de la tesis y
  la ortoimagen tienen los lados del octogono en los ejes, igual que el
  octogono de arranque del modelo (`granada.cupula`).
- Escala: la que lleva el radio exterior del contorno en las ocho direcciones
  de los lados (0, 45, 90... grados) a la apotema del modelo,
  RADIO_BASE / media del octogono.

Criterios automaticos de giro probados y descartados el 2026-11-06, porque no
discriminan en un contorno casi de orden 16: la envolvente en las ocho
direcciones de los lados (igual para cualquier giro: dio 20,2 grados), los
vertices apoyados en el octogono (empate 0 / -21,5 grados) y el perfil completo
con escala por mediana (los entrantes dominan: dio -22,5 grados con el 72 % de
direcciones fuera del 2 %).

Comprobacion independiente: los entrantes del contorno deben estar donde la
ortoimagen tiene los cupulines (fase medida 10,75 + k 22,5 grados), y los 16
cupulines deben caer fuera de la red y dentro del octogono.

Historia (2026-11-06): una primera version supuso, siguiendo la nota del
commit ea9393e, que cada cupulin caia DENTRO de una celda de la red, y ajusto
con eso. Salian giros de +-10 grados que ninguna prueba sobre la ortoimagen
confirmaba, y el contorno quedaba girado respecto al tambor. Con estos datos la
premisa es falsa: los cupulines estan en entrantes del contorno, a
10,75 + k 22,5 grados, donde el contorno baja a 2,80 m. Se rehizo con el
contorno.

Uso:  python3 scripts/registrar_red_cupulines.py
Salida: datos/registro_red.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.cupula import _MEDIA_OCT, CATETO_M, RADIO_BASE_M, cupulines_medidos  # noqa: E402

RED = RAIZ / "datos" / "red_medinas.json"
CARAS = RAIZ / "datos" / "caras_red.json"
SALIDA = RAIZ / "datos" / "registro_red.json"


def transformar(P: np.ndarray, giro: float, escala: float) -> np.ndarray:
    c, s = math.cos(giro), math.sin(giro)
    return escala * P @ np.array([[c, s], [-s, c]])


def radio_octogono(P: np.ndarray, apotema: float) -> np.ndarray:
    """Radio del octogono (lados a 0, 45...) en la direccion de cada punto."""
    a = np.degrees(np.arctan2(P[:, 1], P[:, 0]))
    return apotema / np.cos(np.radians((a + 22.5) % 45 - 22.5))


def radio_exterior(P: np.ndarray, rayos: np.ndarray) -> np.ndarray:
    """Distancia a la interseccion mas lejana del contorno P con cada rayo desde el origen."""
    r = np.zeros(len(rayos))
    for a, b in zip(P, np.roll(P, -1, axis=0)):
        d = b - a
        den = rayos[:, 0] * d[1] - rayos[:, 1] * d[0]
        ok = np.abs(den) > 1e-12
        t = np.where(ok, (a[0] * d[1] - a[1] * d[0]) / np.where(ok, den, 1), 0)
        s = np.where(ok, (a[0] * rayos[:, 1] - a[1] * rayos[:, 0]) / np.where(ok, den, 1), -1)
        valido = ok & (t > 0) & (s >= 0) & (s <= 1)
        r = np.where(valido & (t > r), t, r)
    return r


def dentro(p, P) -> bool:
    ins = False
    for a, b in zip(P, np.roll(P, -1, axis=0)):
        if (a[1] > p[1]) != (b[1] > p[1]) and p[0] < a[0] + (p[1] - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            ins = not ins
    return ins


def main() -> int:
    nodos = np.array(json.loads(RED.read_text(encoding="utf-8"))["nodos"], dtype=float)
    caras = json.loads(CARAS.read_text(encoding="utf-8"))
    contorno = nodos[caras["contorno"]["vertices"]]
    apotema = RADIO_BASE_M / _MEDIA_OCT
    phi = np.radians(np.arange(0, 360, 0.25))
    rayos = np.stack([np.cos(phi), np.sin(phi)], axis=1)
    giro_g = 0.0
    exterior = radio_exterior(transformar(contorno, 0.0, 1.0), rayos)
    lados = [int(round(k * 45 / 0.25)) % len(phi) for k in range(8)]
    escala = apotema / float(np.mean(exterior[lados]))
    # Entrantes: minimos locales del radio exterior en cada octavo.
    entrantes = []
    for k in range(16):
        a0 = k * 22.5
        sel = (np.degrees(phi) >= a0) & (np.degrees(phi) < a0 + 22.5)
        i_min = np.flatnonzero(sel)[int(np.argmin(exterior[sel]))]
        entrantes.append(float(np.degrees(phi[i_min])))
    fase_entrantes = float(np.median([e % 22.5 for e in entrantes]))
    N = transformar(nodos, math.radians(giro_g), escala)
    C = N[caras["contorno"]["vertices"]]
    cupulines = [(c.x * CATETO_M, c.y * CATETO_M) for c in cupulines_medidos()]
    fuera_de_la_red = sum(not dentro(p, C) for p in cupulines)
    limite = radio_octogono(np.array(cupulines), apotema)
    dentro_del_octogono = int(sum(math.hypot(x, y) < r for (x, y), r in zip(cupulines, limite)))

    salida = {
        "version": 2,
        "de": "datos/red_medinas.json (metros, marco del dibujo de la tesis)",
        "a": "marco de la cupula por piezas y de la ortoimagen (metros)",
        "transformacion": "p' = escala * R(giro) * p",
        "espejo_y": False,
        "giro_grados": round(giro_g, 2),
        "escala": round(escala, 4),
        "ajuste": {
            "apotema_modelo_m": round(apotema, 4),
            "radio_exterior_en_los_lados_sin_escalar_m": [round(float(exterior[i]), 4) for i in lados],
            "giro": "0, del registro original (ea9393e), no ajustado",
        },
        "comprobacion_cupulines": {
            "fase_de_los_entrantes_grados": round(fase_entrantes, 2),
            "fase_de_los_cupulines_grados": json.loads((RAIZ / "datos" / "cupulines.json").read_text(encoding="utf-8"))["resultado"]["fase_grados"],
            "fuera_de_la_red": fuera_de_la_red,
            "dentro_del_octogono": dentro_del_octogono,
            "de": len(cupulines),
        },
        "nota": "Los cupulines caen en entrantes del contorno, no en celdas: no se usan para el ajuste.",
    }
    SALIDA.write_text(json.dumps(salida, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(salida, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
