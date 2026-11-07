"""Niveles de la sala de Dos Hermanas leidos sobre la seccion de AA-415_23.

Lectura A OJO, el 2026-11-07, sobre docs/AA-415_23_seccion.jpg (6219 x 7809
px) a resolucion completa: recortes de la franja central x 600-5000 en
y 1700-4400 y 4200-7809, reducidos por 4,889, y comprobacion con lineas
dibujadas sobre el recorte x 1700-3500, y 4200-6300. Cada fila de abajo es la fila
de pixel de la imagen completa donde se ve el borde indicado. Margen de
lectura: unos +-20 px (+-4 cm), mas la ambiguedad de cada borde (molduras),
que puede llegar a 10 cm.

Escala: 472,488 px por metro, la de los vectores de la propia lamina
(docs/estratificacion.md). El marco del modelo tiene z = 0 en el arranque de
la cupula y unidades del cateto (granada.cupula.CATETO_M).

Uso:  python3 scripts/leer_alzado_sala.py
Salida: datos/alzado_sala.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.cupula import CATETO_M  # noqa: E402

PX_POR_M = 472.488
FILAS = {
    # nombre: (fila de pixel, que borde es)
    "arranque_cupula": (2140, "remate de la arqueria del tambor, donde empiezan los mocarabes"),
    "pie_ventanas_tambor": (2776, "alfeizar de las ventanas del tambor, techo de la banda de friso"),
    "pie_friso_tambor": (3582, "pie de la banda de friso del tambor octogonal, techo de las trompas"),
    "pie_trompas": (4396, "pie de los arcos de mocarabes de las esquinas, techo de los muros del cuadrado"),
    "remate_ventana_alta": (4273, "clave de la ventana alta de cada muro"),
    "pie_ventana_alta": (5080, "alfeizar de la ventana alta"),
    "remate_alfiz_arco": (5447, "remate del alfiz (recuadro) del arco de entrada"),
    "clave_arco_grande": (5618, "clave interior del arco de entrada de cada muro"),
    "remate_zocalo": (6767, "remate del zocalo de azulejo"),
    "suelo": (7466, "suelo"),
}
ANCHOS_PX = {
    "arco_grande": (2016, 3168, "luz interior del arco de entrada, en la fila 5911"),
    "ventana_alta": (2287, 2898, "luz de la ventana alta, en la fila 4689"),
    "sala": (680, 4500, "ancho interior de la sala: muro del fondo entre los cortes de los laterales, filas 5000-7400"),
}


def main() -> int:
    suelo = FILAS["suelo"][0]
    arranque = FILAS["arranque_cupula"][0]
    niveles = {}
    for nombre, (fila, que) in FILAS.items():
        sobre_suelo = (suelo - fila) / PX_POR_M
        z_m = (arranque - fila) / PX_POR_M
        niveles[nombre] = {
            "fila_px": fila,
            "borde": que,
            "sobre_suelo_m": round(sobre_suelo, 3),
            "z_m": round(z_m, 3),
            "z_cateto": round(z_m / CATETO_M, 3),
        }
    anchos = {
        nombre: {"px": b - a, "m": round((b - a) / PX_POR_M, 3), "cateto": round((b - a) / PX_POR_M / CATETO_M, 3), "donde": que}
        for nombre, (a, b, que) in ANCHOS_PX.items()
    }
    salida = {
        "version": 1,
        "fuente": "docs/AA-415_23_seccion.jpg, lectura a ojo (ver docstring de scripts/leer_alzado_sala.py)",
        "px_por_m": PX_POR_M,
        "z": "0 en el arranque de la cupula, positivo hacia arriba",
        "niveles": niveles,
        "anchos": anchos,
    }
    destino = RAIZ / "datos" / "alzado_sala.json"
    destino.write_text(json.dumps(salida, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for nombre, n in niveles.items():
        print(f"{nombre:22s} {n['sobre_suelo_m']:6.2f} m sobre el suelo   z = {n['z_cateto']:7.2f}")
    for nombre, a in anchos.items():
        print(f"{nombre:22s} ancho {a['m']:.2f} m = {a['cateto']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
