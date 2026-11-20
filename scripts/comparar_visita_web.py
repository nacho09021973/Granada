"""Compara dos capturas por vista guardadas por comprobar_visita_web.cjs."""

from argparse import ArgumentParser
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("antes", type=Path)
    parser.add_argument("despues", type=Path)
    parser.add_argument("salida", type=Path)
    parser.add_argument(
        "--hiladas", action="store_true", help="Comparar el paño de las ventanas"
    )
    args = parser.parse_args()
    vistas = [
        ("sala", "Desde la sala"),
        ("cupulin", "Cupulín"),
        ("cupulin_oblicuo", "El mismo cupulín al girar"),
    ]
    if args.hiladas:
        vistas = [
            ("hiladas", "Hiladas sobre las ventanas"),
            ("hiladas_lateral", "Giro alrededor del paño"),
            ("hiladas_detalle", "Detalle desde el lado"),
        ]
    fuente = ImageFont.truetype("DejaVuSans.ttf", 20)
    cabecera = 330 if args.hiladas else 0
    comparacion = Image.new("RGB", (1196, 1304 + cabecera), "#faf8f2")
    rotulo = ImageDraw.Draw(comparacion)
    if args.hiladas:
        docs = Path(__file__).resolve().parents[1] / "docs"
        for x, archivo, caja, tam, titulo in [
            (
                12,
                "AA-415_23_seccion.jpg",
                (1800, 1830, 3310, 2330),
                (830, 275),
                "Sección de Almagro · AA-415_23, p. 1",
            ),
            (
                862,
                "AA-415_23_orto_techo.jpg",
                (3440, 1490, 3920, 1930),
                (320, 275),
                "Planta junto al cupulín",
            ),
        ]:
            with Image.open(docs / archivo) as original:
                recorte = original.crop(caja)
                recorte.thumbnail(tam, Image.Resampling.LANCZOS)
                rotulo.text((x, 9), titulo, font=fuente, fill="#231e18")
                comparacion.paste(recorte, (x, 40))
    for j, (carpeta, titulo) in enumerate(
        [(args.antes, "Visita anterior"), (args.despues, "Visita actual")]
    ):
        x = 12 + j * 592
        rotulo.text((x, cabecera + 10), titulo, font=fuente, fill="#231e18")
        for i, (nombre, vista) in enumerate(vistas):
            y = cabecera + 42 + i * 420
            with Image.open(carpeta / f"web_3d_{nombre}.png") as captura:
                if captura.size != (580, 380):
                    raise ValueError(f"Tamaño de captura inesperado en {carpeta}")
                rotulo.text((x, y), vista, font=fuente, fill="#504a43")
                comparacion.paste(captura, (x, y + 27))
    comparacion.save(args.salida)


if __name__ == "__main__":
    main()
