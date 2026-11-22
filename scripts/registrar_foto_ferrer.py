"""Registra la captura de Ferrer sobre la sección nativa, por dos recortes.

No infiere alturas de cupulines. Conserva el registro para comparar alzados.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from skimage.feature import match_template

ROOT = Path(__file__).resolve().parents[1]


def buscar(original, foto, caja, escalas):
    plantilla = np.asarray(foto.crop(caja).convert("L"), dtype=np.float32) / 255
    mejor = None
    for s in escalas:
        ancho = round(original.width * s)
        s = ancho / original.width
        im = original.crop((0, 0, original.width, 3300)).resize((ancho, round(3300 * s)), Image.Resampling.LANCZOS)
        correlacion = match_template(np.asarray(im.convert("L"), dtype=np.float32) / 255, plantilla)
        y, x = np.unravel_index(np.argmax(correlacion), correlacion.shape)
        resultado = dict(escala=s, tx_px=float(caja[0] - x), ty_px=float(caja[1] - y),
                         correlacion=float(correlacion[y, x]))
        if mejor is None or resultado["correlacion"] > mejor["correlacion"]:
            mejor = resultado
    return mejor


def main():
    fuente = ROOT / "docs/AA-415_23_seccion.jpg"
    captura = ROOT / "docs/Foto de Ferrer.png"
    original, foto = Image.open(fuente).convert("RGB"), Image.open(captura).convert("RGB")
    a = buscar(original, foto, (280, 210, 920, 550), np.arange(.18, .281, .002))
    a = buscar(original, foto, (280, 210, 920, 550), np.arange(a["escala"] - .003, a["escala"] + .0031, .0001))
    b = buscar(original, foto, (400, 80, 740, 330), np.arange(a["escala"] - .002, a["escala"] + .0021, .0001))
    assert min(a["correlacion"], b["correlacion"]) > .75, (a, b)
    alzado = json.loads((ROOT / "datos/alzado_sala.json").read_text())
    informe = dict(
        metodo="Correlación normalizada; semejanza isotrópica sin estirar el modelo",
        transformacion="pixel_foto = escala * pixel_seccion + (tx,ty)",
        registro=a, control_otro_recorte=b,
        px_por_m=a["escala"] * alzado["px_por_m"],
        origen_modelo_px=[a["escala"] * 2555 + a["tx_px"],
                          a["escala"] * alzado["niveles"]["arranque_cupula"]["fila_px"] + a["ty_px"]],
        sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (fuente, captura, ROOT / "datos/alzado_sala.json", Path(__file__))},
        limite="Registro de imágenes, no de cada pieza 3D; la captura no resuelve todas las profundidades",
    )
    (ROOT / "datos/registro_foto_ferrer.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(informe, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
