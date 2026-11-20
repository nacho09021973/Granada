"""Lámina para leer el piloto sin colores de diagnóstico. Ejecutar tras ver_marco_en_yeso.py."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

out=Path(__file__).resolve().parents[1]/"renders/previas"
general=Image.open(out/"cupula_cycles_visitante_vigente_1400.png").convert("RGB").resize((340,340))
a,b=[Image.open(out/f"marco_yeso_{s}.png").convert("RGB") for s in ("antes","despues")]
x,y=[round(v*340) for v in json.loads((out/"marco_localizacion.json").read_text())]
d=ImageDraw.Draw(general)
for r,color in [(25,"black"),(23,"#ffcb3c")]:
    d.ellipse((x-r,y-r,x+r,y+r),outline=color,width=3)
im=Image.new("RGB",(1350,674),"#f6f4ed")
d=ImageDraw.Draw(im)
def titulo(x,y,s,n=22):
    d.text((x,y),s,font=ImageFont.truetype("DejaVuSans.ttf",n),fill="#27221b")
titulo(18,14,"Cómo llegan las piezas al borde de un cupulín",32)
titulo(18,80,"Dónde mirar")
titulo(374,80,"Antes · piezas retiradas")
titulo(864,80,"Después · piezas recortadas")
im.paste(general,(18,121))
for x0,panel in [(374,a),(864,b)]:
    im.paste(panel.resize((465,465),Image.Resampling.LANCZOS),(x0,121))
titulo(18,475,"El círculo señala el cupulín",18)
titulo(18,500,"en la vista del visitante.",18)
for x0 in (374,864):
    x,y=x0+367,121+184
    d.line((x+30,y-38,x+3,y-5),fill="#9d3615",width=3)
    d.polygon([(x,y),(x+3,y-13),(x+11,y-7)],fill="#9d3615")
titulo(374,610,"La flecha marca la rendija a la derecha de la boca.",21)
im.save(out/"comparacion_marco_en_yeso.png")
