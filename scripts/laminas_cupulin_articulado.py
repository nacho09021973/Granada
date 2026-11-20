"""Comparaciones locales, incluida la referencia de Almagro. No redistribuir el recorte."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

root=Path(__file__).resolve().parents[1]
out=root/"renders/previas"
font=lambda n:ImageFont.truetype("DejaVuSans.ttf",n)
def abrir(s): return Image.open(out/f"articulado_{s}.png").convert("RGB")
def lamina(nombre,titulo,paneles,lado,pie):
    im=Image.new("RGB",(len(paneles)*(lado+14)+14,lado+146),"#f6f4ed")
    d=ImageDraw.Draw(im)
    d.text((14,10),titulo,font=font(26),fill="#251f19")
    for i,(label,p) in enumerate(paneles):
        x=14+i*(lado+14)
        d.text((x,60),label,font=font(19),fill="#251f19")
        im.paste(p.resize((lado,lado),Image.Resampling.LANCZOS),(x,90))
    d.text((14,lado+104),pie,font=font(17),fill="#251f19")
    im.save(out/f"articulado_{nombre}.png")

foto=Image.open(root/"docs/AA-415_23_orto_techo.jpg").convert("RGB").crop((3210,1440,3830,2060))
lamina("comparacion","El encuentro con las hiladas, visto desde abajo",[
    ("Obra · ortoimagen",foto),
    ("Modelo actual · piloto recortado",ImageOps.mirror(abrir("planta_actual"))),
    ("Candidato · dos filas y pozo",ImageOps.mirror(abrir("planta_candidato")))],460,
    "Referencia: A. Almagro / RABASF, AA-415_23, p. 1. Regiones comparables a escala aproximada.")
for vista,n in [("detalle",520),("visitante",700)]:
    lamina("par_"+vista,"La misma cámara y la misma luz",[
        ("Modelo actual",abrir(vista+"_actual")),("Candidato",abrir(vista+"_candidato"))],n,
        "Desde el visitante. El cupulín intervenido está en el extremo derecho de la vista completa.")
# Marcas de lectura sobre esquinas y juntas visibles en la fotografía original.
marcada=foto.copy()
d=ImageDraw.Draw(marcada)
for puntos in [[(169,335),(180,311),(214,283)],[(267,294),(294,259),(329,231)],
               [(481,292),(480,362),(523,363)],[(194,411),(237,379),(265,402)]]:
    d.line(puntos,fill="#ef9a34",width=3)
lamina("lectura","Aristas visibles en el entorno de la boca",[("Original",foto),("Cuatro trazos de lectura",marcada)],520,
       "Anotación visual local. Los trazos señalan cambios de dirección y caras planas.")
