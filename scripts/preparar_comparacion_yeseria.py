"""Prepara el mismo recorte del render y del control web para revisión local.

No calcula una medida de realismo. La comparación visual la decide una persona.
"""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", type=Path, default=ROOT / "renders/previas/0039_cycles")
    ap.add_argument("--control", type=Path, default=ROOT / "renders/previas/0038_final/web_3d_hiladas.png")
    ap.add_argument("--salida", type=Path, default=ROOT / "web/estudio")
    args = ap.parse_args()
    fuente = args.render / "pano_completo.png"
    procedencia = json.loads((args.render / "procedencia.json").read_text())
    assert hashlib.sha256(fuente.read_bytes()).hexdigest() == procedencia["imagen_sha256"]
    imagen = Image.open(fuente).convert("RGB")
    control = Image.open(args.control).convert("RGB")
    assert control.size == (580, 380)
    ancho, alto = imagen.size
    assert abs(alto / ancho - 740 / 900) < 0.001
    caja = tuple(round(v) for v in (160 * ancho / 900, 140 * alto / 740,
                                    740 * ancho / 900, 520 * alto / 740))
    recorte = imagen.crop(caja)
    args.salida.mkdir(parents=True, exist_ok=True)
    recorte.save(args.salida / "yeseria_cycles.png")
    control.save(args.salida / "yeseria_web.png")
    fuente_rotulo = ImageFont.truetype("DejaVuSans.ttf", 22)
    comparacion = Image.new("RGB", (1196, 468), "#f5f2eb")
    dibujo = ImageDraw.Draw(comparacion)
    for x, titulo, im in [(12, "Visita actual", control), (604, "Estudio de luz y yeso", recorte)]:
        dibujo.text((x, 12), titulo, fill="#282620", font=fuente_rotulo)
        comparacion.paste(im.resize((580, 380), Image.Resampling.LANCZOS), (x, 50))
    dibujo.text((12, 440), "Misma geometría y cámara. Iluminación y acabado propuestos.",
                fill="#48443b", font=ImageFont.truetype("DejaVuSans.ttf", 16))
    comparacion.save(args.salida / "comparacion.png")
    informe = dict(
        procedencia_render=procedencia,
        sha256_control=hashlib.sha256(args.control.read_bytes()).hexdigest(),
        archivo_control=str(args.control.relative_to(ROOT)),
        sha256_script=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        recorte_px=caja,
        sha256_salidas={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in args.salida.glob("*.png")},
        limite="Comparación visual subjetiva; no certifica hiperrealismo ni fidelidad histórica",
    )
    (ROOT / "datos/estudio_acabado_yeseria.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n")
    print(args.salida / "comparacion.png")


if __name__ == "__main__":
    main()
