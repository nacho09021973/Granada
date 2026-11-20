"""Láminas locales de los pilotos de clave y acabado, tras los renders.

La referencia fotográfica permanece en previas locales, no se redistribuye.
Ejecutar con .venv/bin/python scripts/laminas_clave_y_acabado.py
"""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "renders/previas"


def lamina(nombre, titulo, paneles, pie):
    lado = 560
    imagen = Image.new("RGB", (len(paneles)*580+20, 690), "#f4f1e9")
    d = ImageDraw.Draw(imagen)
    font = ImageFont.truetype("DejaVuSans.ttf", 19)
    d.text((20, 12), titulo, font=font, fill="black")
    for i, (label, panel) in enumerate(paneles):
        d.text((20+580*i, 48), label, font=font, fill="black")
        imagen.paste(panel.convert("RGB").resize((lado, lado)), (20+580*i, 80))
    d.text((20, 655), pie, font=font, fill="black")
    imagen.save(OUT / nombre)


def main():
    for vista in ("detalle", "visitante"):
        lamina(f"clave_comparacion_{vista}.png", "Clave central · misma cámara, material y luz", [
            ("Actual", Image.open(OUT/f"clave_{vista}_actual.png")),
            ("Ensayo · cotas supuestas", Image.open(OUT/f"clave_{vista}_candidato.png")),
        ], "Yeso neutro para evaluar geometría. No es una entrega fotorrealista.")
    lamina("comparacion_acabado.png", "Acabado · misma malla, cámara, luz, resolución y muestras", [
        ("Actual · alabeo, desgaste y suciedad", Image.open(OUT/"cupula_cycles_cupula_acabado_actual.png")),
        ("Obra nueva · opción de ensayo", Image.open(OUT/"cupula_cycles_cupula_acabado_obra_nueva.png")),
    ], "560 px y 16 muestras. Cambiar el acabado no valida ni completa la geometría.")
    rutas = [ROOT/"scripts/render_cycles.py", ROOT/"scripts/ensayar_clave_estrellada.py",
             ROOT/"scripts/laminas_clave_y_acabado.py", OUT/"cupula_campo_vigente_1400.obj",
             OUT/"cupula_campo_vigente_1400.mtl", ROOT/"docs/AA-415_23_seccion.jpg",
             ROOT/"docs/AA-415_23_orto_techo.jpg"]
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in rutas}
    (ROOT/"datos/procedencia_clave_y_acabado.json").write_text(
        json.dumps(dict(sha256=hashes, acabado=dict(lado=560, muestras=16, vista="cupula",
                   perfiles=["actual", "obra-nueva"], dispositivo="cpu")), indent=2)+"\n")


if __name__ == "__main__":
    main()
