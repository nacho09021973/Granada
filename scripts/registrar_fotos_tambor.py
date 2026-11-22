"""Registra seis fotografías de Wikimedia Commons del tambor de Dos Hermanas.

Las aportó el usuario el 2026-11-22 a `docs/`, descargadas desde las páginas
de Commons. Autor, licencia y SHA-1 se consultaron ese día en la API de
Commons (`prop=imageinfo&iiprop=sha1|size|extmetadata`) y se copian aquí. El
script comprueba que cada fichero local coincide con ese SHA-1 y escribe
`datos/fotos_tambor_commons.json`. No accede a la red.

Uso: .venv/bin/python scripts/registrar_fotos_tambor.py
"""

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SALIDA = ROOT / "datos/fotos_tambor_commons.json"

FOTOS = [
    {
        "archivo": "docs/Granada_trip82.jpg",
        "commons": "File:Granada trip82.jpg",
        "autor": "Tibor Kovacs",
        "licencia": "CC BY 2.0",
        "sha1": "ce7d7ccc2bab09260c94843f45cc96073c9d3c22",
        "uso": "cinco caras del tambor con oblicuidad creciente; candidata para medir",
    },
    {
        "archivo": "docs/Hall_of_the_Two_Sisters_-_Alhambra_(3).jpg",
        "commons": "File:Hall of the Two Sisters - Alhambra (3).JPG",
        "autor": "José Luiz",
        "licencia": "CC BY-SA 3.0",
        "sha1": "676a037786091084b192b21dbbc2cfdc311e326a",
        "uso": "par de vanos casi de frente, desde abajo; control de forma",
    },
    {
        "archivo": "docs/Hall_of_the_Two_Sisters_-_Alhambra_(2).jpg",
        "commons": "File:Hall of the Two Sisters - Alhambra (2).JPG",
        "autor": "José Luiz",
        "licencia": "CC BY-SA 3.0",
        "sha1": "0e41e55c22b70e5b63fe25553de8f59ae11e7ecd",
        "uso": "una cara de frente y las vecinas en oblicuo",
    },
    {
        "archivo": "docs/Alhambra_of_Granada_(8139873808).jpg",
        "commons": "File:Alhambra of Granada (8139873808).jpg",
        "autor": "Olivier Bruchez",
        "licencia": "CC BY-SA 2.0",
        "sha1": "8b84bf82f29e785d22b2c8204d835e0deca73076",
        "uso": "tambor completo en oblicuo desde la sala",
    },
    {
        "archivo": "docs/AlhambraD_22_(6851003210).jpg",
        "commons": "File:AlhambraD 22 (6851003210).jpg",
        "autor": "michael clarke stuff (Flickr)",
        "licencia": "CC BY-SA 2.0",
        "sha1": "9209350d42883f0bb348d39dbdf6c29cef681b04",
        "uso": "caras del tambor en oblicuo desde una esquina",
    },
    {
        "archivo": "docs/Alhambra_Aug._2010_15.jpg",
        "commons": "File:Alhambra Aug. 2010 15.JPG",
        "autor": "ElenaGissi",
        "licencia": "CC BY-SA 3.0 es",
        "sha1": "2d7d17ca0ed0be83981e2ebab478dd4e684979fc",
        "uso": "tambor y trompas desde el eje de un muro",
    },
]


def main():
    registro = []
    for foto in FOTOS:
        datos = (ROOT / foto["archivo"]).read_bytes()
        sha1 = hashlib.sha1(datos).hexdigest()
        if sha1 != foto["sha1"]:
            raise SystemExit(f"{foto['archivo']}: SHA-1 {sha1} distinto del de Commons")
        with Image.open(ROOT / foto["archivo"]) as im:
            ancho, alto = im.size
        registro.append(
            dict(
                foto,
                pagina="https://commons.wikimedia.org/wiki/" + foto["commons"].replace(" ", "_"),
                sha256=hashlib.sha256(datos).hexdigest(),
                bytes=len(datos),
                px=[ancho, alto],
            )
        )
    SALIDA.write_text(
        json.dumps(
            {
                "consulta_commons": "2026-11-22, API imageinfo (sha1, size, extmetadata)",
                "script": "scripts/registrar_fotos_tambor.py",
                "fotos": registro,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    print(f"{len(registro)} fotos coinciden con Commons -> {SALIDA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
