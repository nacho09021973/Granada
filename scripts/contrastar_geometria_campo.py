"""Contraste local tras auditar_geometria_obj.py, desde la raíz, con la venv.

Usa la ortoimagen en la lámina privada de previas. Los recortes comparten
escala aproximada y región, no constituyen un registro punto a punto.
"""

import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.interpolate import RegularGridInterpolator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from granada.campo import campo
from granada.cupula import CATETO_M
from medir_estratificacion import PX_POR_METRO, UMBRALES, silueta, fin_del_cono

OUT = ROOT / "renders/previas"
OBJ = OUT / "cupula_campo_vigente_1400.obj"
ORTO = ROOT / "docs/AA-415_23_orto_techo.jpg"
SECCION = ROOT / "docs/AA-415_23_seccion.jpg"


def bordes():
    bocas = {}
    boca = None
    with OBJ.open() as stream:
        for line in stream:
            if line.startswith("g "):
                nombre = line.split()[1]
                boca = [] if nombre.startswith("cupulin_") else None
                if boca is not None:
                    bocas[nombre] = boca
            elif line.startswith("v ") and boca is not None and len(boca) < 192:
                boca.append([float(a) for a in line.split()[1:]])
    assert len(bocas) == 16 and all(len(b) == 192 for b in bocas.values())
    # Primer tubo de cupulin_estrellado: alterna base y techo.
    return {k: np.array(b) for k, b in bocas.items()}


def lamina(d):
    escala = json.loads((ROOT / "datos/cupulines.json").read_text())["metodo"]
    orto = Image.open(ORTO).convert("RGB")
    relieve = Image.open(OUT / "auditoria_relieve.pgm").convert("RGB")
    paso = d["lado_px"] / d["ancho_vista_m"]
    imagen = Image.new("RGB", (1000, 824), "#f7f5ef")
    draw = ImageDraw.Draw(imagen)
    letra = ImageFont.truetype("DejaVuSans.ttf", 17)
    draw.text(
        (12, 8),
        "Dos Hermanas   |   ortoimagen y geometría exportada",
        font=letra,
        fill="black",
    )
    for fila, (titulo, im, cx, cy, ppm) in enumerate(
        [
            (
                "A. Almagro / RABASF · AA-415_23, p. 1",
                orto,
                *escala["centro_px"],
                escala["px_por_m_supuesto"],
            ),
            (
                "OBJ · luz sobre las normales · negro = rayo sin impacto",
                relieve,
                relieve.width / 2,
                relieve.height / 2,
                paso,
            ),
        ]
    ):
        y = 42 + fila * 385
        draw.text((12, y), titulo, font=letra, fill="black")
        for i, (key, (x, y_m, lado)) in enumerate(d["regiones_m"].items()):
            zona = {
                "clave": "Clave",
                "hiladas": "Hiladas intermedias",
                "cupulin": "Cupulín exterior",
            }[key]
            xc, yc = cx + x * ppm, cy - y_m * ppm
            r = lado * ppm / 2
            crop = im.crop(tuple(round(v) for v in (xc - r, yc - r, xc + r, yc + r)))
            if fila == 1:
                crop = Image.open(OUT / f"auditoria_detalle_{key}.pgm").convert("RGB")
            imagen.paste(
                crop.resize((316, 316), Image.Resampling.LANCZOS),
                (12 + 330 * i, y + 26),
            )
            draw.text((12 + 330 * i, y + 346), zona, font=letra, fill="black")
    imagen.save(OUT / "auditoria_geometria_detalles.png")


def auditar_bandas(c):
    from granada.cierres_campo import bandas
    from granada.cupula import FAMILIAS
    from granada.hiladas_campo import hilada_de, _contiene_origen
    from scripts.comparar_colocacion_flujo import areas_con_signo, giro_por_pieza

    frentes = []
    for f, b in bandas(c):
        h = hilada_de(f)
        ancho = FAMILIAS[h.familia].paso_tangencial * h.estiramiento
        giro = giro_por_pieza(f, ancho)
        areas = areas_con_signo(f, b.xy)
        frentes.append(
            {
                "fila": f.indice,
                "anillo": bool(_contiene_origen(f.puntos)),
                "piezas_previas_al_recorte": h.piezas,
                "giro_p50_p95_max_grados": giro,
                "triangulos_banda": areas.size,
                "invertidos": int((areas < -1e-10).sum()),
            }
        )
    return {
        "frentes": frentes,
        "invertidos": sum(f["invertidos"] for f in frentes),
        "triangulos_banda": sum(f["triangulos_banda"] for f in frentes),
        "peor_mediana_anillo_filas_13_24_y_30_37": max(
            (f["giro_p50_p95_max_grados"][0], f["fila"])
            for f in frentes
            if f["anillo"] and (13 <= f["fila"] <= 24 or 30 <= f["fila"] <= 37)
        ),
    }


def main():
    d = json.loads((ROOT / "datos/auditoria_geometria_obj.json").read_text())
    assert d["sha256_obj"] == hashlib.sha256(OBJ.read_bytes()).hexdigest()
    c = campo(A=3, forma="raiz", signo=1, borde="octogonal")
    H = RegularGridInterpolator((c.y, c.x), c.H)
    raw = []
    por_boca = {}
    from granada import cupula as gc
    from scripts.render_hilada_campo import EJE_CUPULIN_CAMPO

    gc.EJE_CUPULIN_GRADOS = EJE_CUPULIN_CAMPO
    anclas = gc.cupulines_medidos()
    residuo_antes = []
    paredes_invertidas = 0
    candidato = []
    cruces = []
    # Ensayo de asiento sobre el mismo eje. Intervalo en catetos, no medida
    # histórica. Solo aceptar la bisección si se detecta un cruce por vértice.
    pasos = np.linspace(-3, 7, 501)
    for nombre, tubo in bordes().items():
        V, techo = tubo[::2], tubo[1::2]
        # Reconstruir el punto q en el plano local original proyectando el
        # vértice exportado. La fórmula antigua ajusta z a H(q.xy).
        o, _, _, normal = anclas[int(nombre.split("_")[1])].marco()
        q = V - ((V - o) @ normal)[:, None] * normal
        residuo_antes.extend((V[:, 2] - H(q[:, [1, 0]])) * CATETO_M)
        paredes_invertidas += int((((techo - V) @ normal) < 0).sum())

        def error(t):
            P = q + np.asarray(t)[..., None] * normal
            return P[..., 2] - H(P[..., [1, 0]])

        # El dominio del interpolador incluye todos los centros pero algunos
        # extremos del segmento de búsqueda pueden caer fuera de la rejilla.
        tray = q[None, :, :] + pasos[:, None, None] * normal
        interpolar = RegularGridInterpolator(
            (c.y, c.x), c.H, bounds_error=False, fill_value=np.nan
        )
        valores = tray[..., 2] - interpolar(tray[..., [1, 0]])
        cambios = valores[:-1] * valores[1:] < 0
        cruces.extend(cambios.sum(axis=0).tolist())
        if np.all(cambios.sum(axis=0) == 1):
            i = cambios.argmax(axis=0)
            lo, hi = pasos[i], pasos[i + 1]
            for _ in range(30):
                medio = (lo + hi) / 2
                izquierda = error(lo) * error(medio) <= 0
                hi = np.where(izquierda, medio, hi)
                lo = np.where(izquierda, lo, medio)
            candidato.extend(abs(error((hi + lo) / 2)) * CATETO_M)
        dz = (V[:, 2] - H(V[:, [1, 0]])) * CATETO_M
        raw.extend(dz)
        por_boca[nombre] = float(max(abs(dz)))
    gris = np.asarray(Image.open(SECCION).convert("L"))
    alturas = {}
    for u in UMBRALES:
        izq, der = silueta(gris, u)
        alturas[u] = fin_del_cono((der - izq) / 2, PX_POR_METRO) / PX_POR_METRO
    res = {
        "procedencia": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (
                OBJ,
                ORTO,
                SECCION,
                Path(__file__),
                ROOT / "scripts/auditar_geometria_obj.py",
            )
        },
        "altura_segun_umbral_m": alturas,
        "bandas": auditar_bandas(c),
        "ensayo_interseccion_eje": {
            "intervalo_catetos": [-3, 7],
            "paso_catetos": 0.02,
            "histograma_cruces": {str(k): cruces.count(k) for k in sorted(set(cruces))},
            "n_vertices_bocas_con_un_cruce_por_vertice": len(candidato),
            "max_residuo_m": float(max(candidato)) if candidato else None,
        },
        "paredes_con_techo_bajo_borde": paredes_invertidas,
        "max_abs_borde_menos_H_antes_de_inclinar_m": float(max(np.abs(residuo_antes))),
        "borde_menos_campo_m": {
            "n": len(raw),
            "min": float(min(raw)),
            "max": float(max(raw)),
            "mediana_abs": float(np.median(np.abs(raw))),
            "max_abs_por_cupulin": por_boca,
        },
    }
    (ROOT / "datos/contraste_geometria_campo.json").write_text(
        json.dumps(res, indent=2) + "\n"
    )
    lamina(d)


if __name__ == "__main__":
    main()
