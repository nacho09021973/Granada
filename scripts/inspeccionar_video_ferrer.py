"""Hoja de contacto local del vídeo de Ferrer, con tiempos y procedencia.

No redistribuir los fotogramas: fuente de consulta de terceros.
"""
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def main():
    video = ROOT / "docs/Ferrer_6 maqueta Contreras (grabación 2026-08-29).mp4"
    salida = ROOT / "renders/previas/0040_ferrer"
    salida.mkdir(parents=True, exist_ok=True)
    tiempos = list(range(0, 16, 2))
    hoja = Image.new("RGB", (4 * 300, 2 * 550), "#eeeeea")
    dibujo = ImageDraw.Draw(hoja)
    fotogramas = []
    for k, t in enumerate(tiempos):
        archivo = salida / f"ferrer_{t:02d}s.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(video),
                        "-frames:v", "1", str(archivo)], check=True)
        with Image.open(archivo) as im:
            im.thumbnail((290, 515))
            x, y = (k % 4) * 300, (k // 4) * 550
            hoja.paste(im, (x + 5, y + 25))
            dibujo.text((x + 8, y + 7), f"Ferrer_6 · t={t} s", fill="black")
        fotogramas.append(dict(tiempo_s=t, archivo=str(archivo.relative_to(ROOT)),
                              sha256=hashlib.sha256(archivo.read_bytes()).hexdigest()))
    hoja.save(salida / "contacto.png")
    informe = dict(video=str(video.relative_to(ROOT)),
                   sha256_video=hashlib.sha256(video.read_bytes()).hexdigest(),
                   sha256_script=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   fotogramas=fotogramas,
                   naturaleza="Inspección visual de una grabación de maqueta; sin escala métrica")
    (ROOT / "datos/inspeccion_video_ferrer.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
