"""Vuelo de los mocárabes sobre el muro del tambor en la silueta de AA-415_23.

La sección norte-sur (`docs/AA-415_23_seccion.jpg`) es una ortofoto del
modelo fotogramétrico cortado por el centro de la sala. En sus bordes
izquierdo y derecho la silueta es el corte de las dos caras del tambor
paralelas a la vista, por el centro de cada cara: entre sus dos vanos, en el
machón. Por debajo del arranque la silueta es el plano del muro; por encima,
el perfil de lo que vuela hacia dentro.

Mide, a cada lado y con tres umbrales (los de
`scripts/medir_estratificacion.py`):

- x0: plano del muro, mediana de la silueta en la banda de los vanos
  (entre `pie_ventanas_tambor` y 0,25 m por debajo de `arranque_cupula`);
- el vuelo hacia dentro, (x - x0) / escala, fila a fila desde 0,6 m por
  debajo del arranque hasta 0,6 m por encima;
- la apotema que implica x0 respecto al eje del paño 00 (`EJE_PX` de
  `scripts/hiladas_ventanas.py`), como control de la escala.

Compara con el modelo: fondo del paño 00 de 0,3205 m a la cota del arranque
(decisión 0038) y la cara del muro a la apotema del modelo.

Supuestos: el corte pasa por el centro de las caras laterales; la ortofoto no
deforma la silueta; el umbral separa yeso de fondo blanco. La silueta es la
envolvente de toda la profundidad de la vista, no solo del plano de corte:
cualquier pieza que vuele más en otra parte de la cara lateral la ensancha.

Salida: `datos/vuelo_seccion.json` y `renders/previas/0043/vuelo_seccion.png`.

Con `--modelo datos/vuelo_modelo_<v>.json` (de `scripts/perfil_vuelo_glb.py`)
superpone en la lámina el perfil equivalente del GLB, en gris.

Uso: .venv/bin/python scripts/medir_vuelo_seccion.py [--modelo datos/vuelo_modelo_0042.json]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from hiladas_ventanas import EJE_PX  # noqa: E402
from medir_estratificacion import UMBRALES, silueta  # noqa: E402

IMAGEN = ROOT / "docs/AA-415_23_seccion.jpg"
SALIDA = ROOT / "datos/vuelo_seccion.json"
PREVIA = ROOT / "renders/previas/0043/vuelo_seccion.png"
APOTEMA_MODELO = 3.8657066822052  # web/modelos/dos-hermanas.json
FONDO_MODELO = 0.3205  # decisión 0038, borde interior de la cornisa
VENTANA = 0.6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modelo", type=Path, action="append", default=[])
    args = ap.parse_args()
    alzado = json.loads((ROOT / "datos/alzado_sala.json").read_text())
    escala = alzado["px_por_m"]
    f0 = alzado["niveles"]["arranque_cupula"]["fila_px"]
    fa = alzado["niveles"]["pie_ventanas_tambor"]["fila_px"]
    Image.MAX_IMAGE_PIXELS = None
    gris = np.asarray(Image.open(IMAGEN).convert("L"), dtype=np.int16)
    filas = np.arange(int(f0 - VENTANA * escala), int(f0 + VENTANA * escala) + 1)
    muro = np.arange(int(f0 + 0.25 * escala), fa)
    res = dict(
        imagen=str(IMAGEN.relative_to(ROOT)),
        sha256_imagen=hashlib.sha256(IMAGEN.read_bytes()).hexdigest(),
        px_por_m=escala,
        fila_arranque=f0,
        fondo_modelo_m=FONDO_MODELO,
        apotema_modelo_m=APOTEMA_MODELO,
        umbrales={},
    )
    perfiles = {}
    for u in UMBRALES:
        izq, der = silueta(gris[: fa + 1], u)
        lados = {}
        for nombre, borde, signo in (("izquierdo", izq, 1), ("derecho", der, -1)):
            x0 = float(np.nanmedian(borde[muro]))
            desv = float(np.nanstd(borde[muro]))
            vuelo = signo * (borde[filas] - x0) / escala
            i0 = int(np.where(filas == f0)[0][0])
            # Máximo del vuelo por debajo y por encima del arranque.
            lados[nombre] = dict(
                x0_px=x0,
                desv_muro_px=round(desv, 2),
                apotema_m=round(signo * (EJE_PX - x0) / escala, 4),
                vuelo_en_arranque_m=round(float(vuelo[i0]), 4),
                vuelo_max_bajo_arranque_m=round(float(np.nanmax(vuelo[i0:])), 4),
                vuelo_a_10cm_sobre_arranque_m=round(float(vuelo[i0 - int(0.10 * escala)]), 4),
                vuelo_a_20cm_sobre_arranque_m=round(float(vuelo[i0 - int(0.20 * escala)]), 4),
                perfil=[
                    [round((f0 - int(f)) / escala, 4), None if np.isnan(v) else round(float(v), 4)]
                    for f, v in zip(filas[::4], vuelo[::4])
                ],
            )
            perfiles[(u, nombre)] = vuelo
        res["umbrales"][str(u)] = lados
        print(u, {k: {a: b for a, b in v.items() if a != "perfil"} for k, v in lados.items()}, flush=True)

    # Lámina: perfil de vuelo frente a cota, los dos lados y tres umbrales.
    W, H, m = 900, 900, 60
    img = Image.new("RGB", (W, H), "white")
    dib = ImageDraw.Draw(img)
    sx = (W - 2 * m) / 1.2  # vuelo de -0,2 a 1,0 m
    sz = (H - 2 * m) / (2 * VENTANA)
    px = lambda v, z: (m + (v + 0.2) * sx, H / 2 - z * sz)
    for v in np.arange(-0.2, 1.01, 0.1):
        dib.line([px(v, -VENTANA), px(v, VENTANA)], fill=(225, 225, 225))
        dib.text(px(v, -VENTANA - 0.03), f"{v:.1f}", fill="black")
    for z in np.arange(-VENTANA, VENTANA + 0.01, 0.1):
        dib.line([px(-0.2, z), px(1.0, z)], fill=(225, 225, 225))
        dib.text((5, px(0, z)[1] - 5), f"{z:+.1f}", fill="black")
    dib.line([px(0, -VENTANA), px(0, VENTANA)], fill="black")
    dib.line([px(-0.2, 0), px(1.0, 0)], fill="black")
    dib.line([px(FONDO_MODELO, -0.05), px(FONDO_MODELO, 0.05)], fill=(0, 140, 0), width=3)
    colores = {"izquierdo": (200, 0, 0), "derecho": (0, 0, 200)}
    zs = (f0 - filas) / escala
    for (u, nombre), vuelo in perfiles.items():
        pts = [px(v, z) for v, z in zip(vuelo, zs) if not np.isnan(v)]
        dib.line(pts, fill=colores[nombre], width=1 if u != 245 else 2)
    for ruta, gris_m in zip(args.modelo, ((90, 90, 90), (0, 160, 160), (200, 120, 0))):
        mod = json.loads((ruta if ruta.is_absolute() else ROOT / ruta).read_text())
        res.setdefault("modelos", []).append(dict(ruta=str(ruta), sha256_glb=mod["sha256_glb_descomprimido"]))
        for perfil in mod["perfiles"].values():
            pts = [px(v, z) for z, v in perfil if v is not None]
            dib.line(pts, fill=gris_m, width=2)
    dib.text((m, 10), "vuelo hacia dentro (m) frente a cota sobre el arranque (m); rojo izq., azul der.; verde: fondo 0,3205; gris/cian/naranja: GLB", fill="black")
    PREVIA.parent.mkdir(parents=True, exist_ok=True)
    img.save(PREVIA)
    SALIDA.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(SALIDA, PREVIA)


if __name__ == "__main__":
    main()
