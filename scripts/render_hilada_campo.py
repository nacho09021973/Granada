"""Monta unas pocas hiladas del modelo por campo de alturas y las renderiza.

Decision 0017, paso 3: comprobar a ojo como se colocan las piezas a lo largo
de una curva de nivel cualquiera (esquinas concavas, lazos) antes de montar la
cupula entera. Rasterizador propio (granada/render3d.py), en yeso.

Uso:
    .venv/bin/python scripts/render_hilada_campo.py [--A 2] [--hiladas 6,10] \
        [--png renders/previas/hilada_campo.png]

Salida: dos vistas en un PNG, cenital desde abajo a la izquierda y oblicua a
la derecha, y el recuento de frentes y piezas por hilada.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from granada.campo import SUAVIZADO, campo  # noqa: E402
from granada.hiladas_campo import frentes, hilada_de, montar  # noqa: E402
from granada.render3d import rasterizar  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    # A=3 raiz desde el 2026-11-18 (decision 0029): 98 % de las 5416 piezas;
    # A=2 lineal daba el 92 % (datos/barrido_estrella.json).
    ap.add_argument("--A", type=float, default=3.0)
    ap.add_argument("--forma", default="raiz")
    ap.add_argument("--signo", type=int, default=1)
    ap.add_argument("--borde", choices=("libre", "octogonal"), default="octogonal",
                    help="octogonal: la trama llena el octogono del tambor (2026-11-18); libre: cono circular")
    ap.add_argument("--filas-por-hilada", type=int, choices=(1, 2), default=2,
                    help="2: opcion B, mitad de altura y fondo, mismo ancho; 1: modelo anterior")
    ap.add_argument("--informe", type=Path, help="guarda el recuento sin renderizar")
    ap.add_argument("--hiladas", default="6,10", help="indices de FILA j, o 'todas'; B tiene dos por hilada")
    ap.add_argument("--lado", type=int, default=1000)
    ap.add_argument("--subdivision", type=int, default=6)
    ap.add_argument("--colocacion", choices=("rayo", "flujo", "rigida", "suavizada"), default="suavizada",
                    help="rayo: desplazamiento recto; flujo: lineas de maxima pendiente (0024); rigida: piezas sin doblar (0025); suavizada: frente suavizado (0026)")
    ap.add_argument("--sigma", type=float, default=1.0, help="suavizado del frente en catetos (solo suavizada)")
    ap.add_argument("--obj", type=Path,
                    help="escribe .obj/.mtl para scripts/render_cycles.py (piezas en yeso + sala medida) y termina")
    ap.add_argument("--sin-cierres", action="store_true",
                    help="no tapa los huecos con cupulillas (granada/cierres_campo.py); solo cuenta con --hiladas todas")
    ap.add_argument("--sin-cupulines", action="store_true",
                    help="no pone los 16 cupulines medidos (datos/cupulines.json); solo cuenta con --hiladas todas")
    ap.add_argument("--forma-cupulin", choices=("estrellado", "piezas"), default="estrellado",
                    help="estrellado: pozo liso con techo de estrella (ortoimagen, 2026-11-18); piezas: cupulita de piezas")
    ap.add_argument("--color", choices=("yeso", "inauguracion"), default="yeso",
                    help="inauguracion: reparto de granada/color.py (Jones lam. XXXIX, estetico; 2026-11-18)")
    ap.add_argument("--umbral-red", type=float, default=None,
                    help="ferrer_red: fondo oscuro desde esta distancia relativa a la red (granada.color.UMBRAL_RED)")
    ap.add_argument("--umbral-pared-red", type=float, default=None,
                    help="ferrer_red: paredes oscuras desde esta distancia relativa; sin el, paredes en crema")
    ap.add_argument("--variante", choices=("jones", "suave", "yeso", "ferrer", "ferrer_red"), default="ferrer",
                    help="variante del reparto inauguracion (granada.color.VARIANTES_INAUGURACION)")
    ap.add_argument("--informe-cierres", type=Path,
                    help="guarda huecos tapados y rendijas por fila (JSON) y termina")
    ap.add_argument("--png", type=Path, default=RAIZ / "renders" / "previas" / "hilada_campo.png")
    a = ap.parse_args()

    c = campo(A=a.A, forma=a.forma, signo=a.signo, borde=a.borde)
    todos = frentes(c, filas_por_hilada=a.filas_por_hilada)
    if a.informe:
        from granada.hiladas_campo import resumen
        import numpy, scipy, skimage
        fuentes = ["granada/campo.py", "granada/hiladas_campo.py", "granada/cupula.py",
                   "granada/piezas.py", "scripts/render_hilada_campo.py",
                   "datos/red_medinas.json", "datos/registro_red.json",
                   "datos/caras_red.json", "datos/niveles_aproximados.json"]
        informe = {
            "procedencia": "Eleccion B del usuario, 2026-11-09; diagnostico, no restitucion validada",
            "parametros": {"A": a.A, "forma": a.forma, "signo": a.signo,
                           "resolucion": c.paso, "suavizado": SUAVIZADO},
            "entorno": {"python": platform.python_version(), "numpy": numpy.__version__,
                        "scipy": scipy.__version__, "scikit-image": skimage.__version__},
            "sha256": {p: hashlib.sha256((RAIZ / p).read_bytes()).hexdigest() for p in fuentes},
            "variantes": {},
            "limites": "Solo piezas en frentes admitidos; faltan cierres, clave y cupulines. No valida el total historico.",
        }
        for filas in (1, 2):
            rs = resumen(c, filas_por_hilada=filas)
            informe["variantes"][str(filas)] = {
                "filas_por_hilada": filas, "escala_pieza_xyz": [1, 1 / filas, 1 / filas],
                "piezas": sum(r["piezas"] for r in rs), "frentes": rs,
                "piezas_en_cotas_originales": sum(r["piezas"] for r in rs if r["fila"] % filas == 0),
                "piezas_en_cotas_intermedias": sum(r["piezas"] for r in rs if r["fila"] % filas != 0),
            }
        a.informe.parent.mkdir(parents=True, exist_ok=True)
        a.informe.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n")
        print({k: v["piezas"] for k, v in informe["variantes"].items()})
        return 0
    if a.hiladas == "todas":
        sel = todos
    else:
        quiero = {int(j) for j in a.hiladas.split(",")}
        sel = [f for f in todos if f.indice in quiero]
    for j in sorted({f.indice for f in sel}):
        fs = [f for f in sel if f.indice == j]
        print(f"fila {j:2d}: {len(fs):3d} frentes, {sum(hilada_de(f).piezas for f in fs):5d} piezas")
    cierres, huecos = [], None
    if (a.hiladas == "todas" and not a.sin_cierres) or a.informe_cierres:
        if a.colocacion != "suavizada":
            ap.error("los cierres se calculan sobre las bandas de la colocacion suavizada")
        from granada.cierres_campo import bandas, cierres as tapar
        cierres, huecos = tapar(c, bandas(c, sel, a.filas_por_hilada, a.sigma))
        print(f"{huecos.n} huecos tapados con cupulilla")
    if a.informe_cierres:
        return escribir_informe_cierres(a, c, huecos)
    con_cupulines = a.hiladas == "todas" and not a.sin_cupulines
    descartar, cupulines = None, []
    if con_cupulines:
        descartar, cupulines = cupulines_en_campo(c, a.forma_cupulin, a.color == "inauguracion", a.variante)
    pintar = None
    if a.color == "inauguracion":
        from granada.color import reparto_inauguracion
        if a.variante == "ferrer_red":
            from granada.color import ferrer_red
            from granada.color import UMBRAL_RED
            pintar = ferrer_red(c.x, c.y, UMBRAL_RED if a.umbral_red is None else a.umbral_red, a.umbral_pared_red)
        else:
            pintar = reparto_inauguracion(a.variante)
    grupos = montar(c, sel, subdivision=a.subdivision, colocacion=a.colocacion, sigma=a.sigma,
                    descartar=descartar, colorear=pintar)
    if con_cupulines:
        print(f"{len(cupulines)} cupulines")
    V, F = [], []
    for _, Vg, Fg, *_ in grupos:
        base = len(V)
        V.extend(Vg)
        F.extend((p + base, q + base, r + base) for p, q, r in Fg)
    for _, Vg, Fg, *_ in cierres + cupulines:
        base = len(V)
        V.extend(Vg)
        F.extend((p + base, q + base, r + base) for p, q, r in Fg)

    if a.obj:
        from granada.color import material, paleta_materiales
        from granada.piezas import escribir_obj
        from granada.sala import sala
        # La sala es la medida de granada/sala.py.
        if a.color == "inauguracion":
            from granada.color import CIERRE_INAUGURACION, CIERRE_POR_VARIANTE, CLAVE_INAUGURACION
            CIERRE_INAUGURACION = CIERRE_POR_VARIANTE.get(a.variante, CIERRE_INAUGURACION)
            salida = [(f"hilada_{n}", Vg, Fg, [material(cc, x) for cc, x in zip(Cg, Sg)]) for n, Vg, Fg, Cg, Sg in grupos]
        else:
            # Piezas en yeso (sin color, decidido el 2026-11-17).
            salida = [(f"hilada_{n}", Vg, Fg, [material("yeso", x) for x in Sg]) for n, Vg, Fg, _, Sg in grupos]

        def tono_cierre(Vg):
            # La clave es la cupulilla que contiene el eje.
            if a.color != "inauguracion":
                return "yeso"
            import numpy as np
            return CLAVE_INAUGURACION if np.hypot(*np.asarray(Vg)[:, :2].mean(axis=0)) < 1 else CIERRE_INAUGURACION
        salida += [(n, Vg, Fg, [material(tono_cierre(Vg), 0.8)] * len(Fg)) for n, Vg, Fg in cierres]
        if a.hiladas == "todas" and a.borde != "octogonal":
            from granada.cierres_campo import corona_arranque
            Vk, Fk = corona_arranque()
            salida.append(("corona_arranque", Vk, Fk, [material("yeso", 0.9)] * len(Fk)))
        salida += [(n, Vg, Fg, [material(cc, 0.8) for cc in Cg]) for n, Vg, Fg, Cg in cupulines]
        salida += [(n, Vg, Fg, [material(cc, x) for cc, x in zip(Cg, Sg)]) for n, Vg, Fg, Cg, Sg in sala()]
        a.obj.parent.mkdir(parents=True, exist_ok=True)
        escribir_obj(a.obj, salida, paleta=paleta_materiales())
        print(f"-> {a.obj}")
        return 0

    luces = [((0.55, 0.35, -0.75), 0.75), ((-0.6, -0.45, -0.65), 0.3)]
    L = a.lado
    abajo, _ = rasterizar(V, F, L, L, supermuestreo=2, luces=luces, perspectiva=((0.0, 0.0, -13.0), (0.0, 0.001, 10.0), 90.0))
    oblicua, _ = rasterizar(V, F, L, L, supermuestreo=2, luces=luces, perspectiva=((0.0, -9.0, -9.0), (0.0, 2.0, 4.0), 70.0))
    lienzo = Image.new("RGB", (2 * L, L))
    lienzo.paste(abajo, (0, 0))
    lienzo.paste(oblicua, (L, 0))
    dibujo = ImageDraw.Draw(lienzo)
    dibujo.rectangle((0, 0, 2 * L, 38), fill=(20, 19, 20))
    dibujo.text((8, 4), f"Modelo supuesto: {a.filas_por_hilada} filas/hilada; A={a.A}; filas {a.hiladas}; colocacion {a.colocacion}" + (f" sigma={a.sigma}" if a.colocacion == "suavizada" else ""), fill="white")
    dibujo.text((8, 20), ("Cierres y clave: cupulillas supuestas" if cierres else "Sin cierres ni clave")
                + ("; cupulines medidos" if cupulines else "; sin cupulines") + "; no es una restitucion validada", fill="white")
    a.png.parent.mkdir(parents=True, exist_ok=True)
    lienzo.save(a.png)
    print(f"{len(F)} triangulos -> {a.png}")
    return 0


PROFUNDIDAD_CUPULIN = 5.0
"""Profundidad del pozo del cupulin sobre la cota media de la boca, en pasos
verticales por cos(atan PENDIENTE). Era 2 (como el modelo de anillos); con 2
las ventanas de debajo iluminan el pozo y se lee como un petalo blanco, y en
Ferrer_5 y la ortoimagen el interior se ve en penumbra (2026-11-18).
Eleccion: la profundidad real no esta medida."""


def cupulines_en_campo(c, forma: str = "estrellado", color: bool = False, variante: str = "yeso"):
    """Los 16 cupulines de datos/cupulines.json sobre la superficie del campo.

    Igual que en granada.cupula.cupula: se quitan las piezas con el centroide
    en el marco del cupulin y el pocillo baja dos hiladas medidas por la
    normal. La boca y el marco se apoyan en H, no en el cono.
    Devuelve (descartar, grupos)."""
    import math
    import numpy as np
    from scipy.ndimage import map_coordinates
    from granada.campo import PASO_VERTICAL, PENDIENTE
    from granada.cupula import cupulin, cupulin_estrellado, cupulines_medidos, detector_de_marcos

    def cota(x, y):
        return float(map_coordinates(c.H, [[(y - c.y[0]) / c.paso], [(x - c.x[0]) / c.paso]], order=1)[0])

    huecos = cupulines_medidos()
    en_marco = detector_de_marcos(huecos)

    def descartar(vertices) -> bool:
        return en_marco(np.asarray(vertices, dtype=float).mean(axis=0))

    profundidad = PROFUNDIDAD_CUPULIN * PASO_VERTICAL * math.cos(math.atan(PENDIENTE))
    mini: dict = {}
    if forma == "estrellado":
        from granada.color import CUPULIN_INAUGURACION, CUPULIN_POR_VARIANTE
        tonos = CUPULIN_POR_VARIANTE.get(variante, CUPULIN_INAUGURACION)
        grupos = []
        for k, q in enumerate(huecos):
            V, F, partes = cupulin_estrellado(q, profundidad, cota=cota)
            grupos.append((f"cupulin_{k:02d}", V, F, [tonos[p] if color else "yeso" for p in partes]))
    else:
        grupos = []
        for k, q in enumerate(huecos):
            V, F = cupulin(q, profundidad, plantillas=mini, cota=cota, arranque="medio")
            grupos.append((f"cupulin_{k:02d}", V, F, ["yeso"] * len(F)))
    return descartar, grupos


def escribir_informe_cierres(a, c, huecos) -> int:
    """Huecos tapados y rendijas por fila: medida, no arreglo (PROXIMOS-PASOS 2026-11-18)."""
    import numpy
    from granada import cierres_campo as cc
    from granada.hiladas_campo import PASO_VERTICAL
    fuentes = ["granada/campo.py", "granada/hiladas_campo.py", "granada/cierres_campo.py",
               "scripts/render_hilada_campo.py", "datos/red_medinas.json", "datos/registro_red.json"]
    paso_fila = PASO_VERTICAL / a.filas_por_hilada
    rendijas = cc.rendijas_por_fila(huecos, paso_fila)
    informe = {
        "procedencia": "Diagnostico de cobertura en planta; los cierres son eleccion de acabado, no dato",
        "parametros": {"A": a.A, "forma": a.forma, "signo": a.signo, "filas_por_hilada": a.filas_por_hilada,
                       "colocacion": a.colocacion, "sigma": a.sigma,
                       "rejilla_catetos": huecos.rejilla.paso, "radio_rendija": cc.RADIO_RENDIJA,
                       "area_minima": cc.AREA_MINIMA, "solape": cc.SOLAPE,
                       "altura_relativa": cc.ALTURA_RELATIVA, "margen_arranque": cc.MARGEN_ARRANQUE},
        "sha256": {p: hashlib.sha256((RAIZ / p).read_bytes()).hexdigest() for p in fuentes},
        "entorno": {"python": platform.python_version(), "numpy": numpy.__version__},
        "huecos": cc.resumen_huecos(huecos),
        "rendijas": {"nudos_minimos": cc.NUDOS_RENDIJA, "componentes": sum(rendijas.values()), "por_fila": rendijas,
                     "componentes_sin_filtrar": sum(cc.rendijas_por_fila(huecos, paso_fila, 1).values()),
                     "area_catetos2": float(huecos.rendijas.sum() * huecos.rejilla.paso ** 2)},
        "limites": ("Cobertura de la huella en planta de las bandas, no de los solidos: no ve las rendijas "
                    "entre piezas dentro de una banda ni las que solo se abren en alzado."),
    }
    a.informe_cierres.parent.mkdir(parents=True, exist_ok=True)
    a.informe_cierres.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + "\n")
    print(f"-> {a.informe_cierres}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
