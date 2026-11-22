"""Contorno del marco y remate escalonado de los nichos, retroproyectado desde trip82.

Lee las lecturas manuales de `datos/lecturas_remate_trip82.json` y las lleva
al plano del muro de su cara con la cámara ajustada en 0041
(`datos/medida_nicho_fotos.json`, ajuste principal): rayo por el píxel e
intersección con el plano n·P = APOTEMA. Supone que el marco y su remate
están en el plano del muro (el relieve de la moldura, unos centímetros, se
ignora) y la cámara sin distorsión, como en 0041.

Para cada vano: eje (centro del merlón; se anota también el punto medio de
los cantos exteriores del marco),
semiancho exterior del marco L, semiancho de la boca, y para cada escalón
del remate sus límites |s - eje| y su cota. Junta los dos vanos y los dos
lados: media, mínimo y máximo. Cotas sobre el canto del alféizar y en el
sistema del modelo (z = 0 en el arranque, `datos/alzado_sala.json`).

Segunda vía, independiente de la cámara: la vista frontal de la sección
AA-415_23 es una ortofoto y da la cota real del contorno superior del vano
del paño 00 (`contraste_seccion` en las lecturas). Si el remate volase
hacia dentro, la retroproyección al plano del muro lo subiría respecto a
esa cota; la diferencia se anota por tramo.

Tercera comprobación, solo cualitativa: proyecta el contorno medio, simétrico, en el plano del muro, sobre los seis vanos de cada foto ajustada (caras A, B y C de trip82 y bruchez) con eje ±a del
ajuste de 0041, y lo dibuja sobre la foto. Las caras A y C y la foto bruchez
no intervienen en la lectura.

Salida: `datos/remate_nichos.json`; láminas en `renders/previas/0043/remate_<clave>.jpg`.

Uso: .venv/bin/python scripts/medir_remate_fotos.py
"""

import hashlib
import json
import sys
from math import radians
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
LECTURAS = ROOT / "datos/lecturas_remate_trip82.json"
MEDIDA = ROOT / "datos/medida_nicho_fotos.json"
SALIDA = ROOT / "datos/remate_nichos.json"
APOTEMA = 3.8657066822052  # web/modelos/dos-hermanas.json
ANGULO_CARA = {"A": 45.0, "B": 0.0, "C": -45.0}  # scripts/medir_nicho_fotos.py
ORDEN = ("merlon", "hombro", "entrante", "pinaculo", "esquina")


def ejes(cara):
    f = radians(ANGULO_CARA[cara])
    return np.array([np.cos(f), np.sin(f), 0.0]), np.array([-np.sin(f), np.cos(f), 0.0])


class Camara:
    def __init__(self, cam):
        self.f = cam["focal_px"]
        self.R = np.array(cam["rotacion"])
        self.C = np.array(cam["posicion_m"])
        self.c = np.array(cam["imagen_px"], float) / 2

    def plano(self, px, cara):
        n, t = ejes(cara)
        d = self.R.T @ np.array([(px[0] - self.c[0]) / self.f, (px[1] - self.c[1]) / self.f, 1.0])
        lam = (APOTEMA - self.C @ n) / (d @ n)
        P = self.C + lam * d
        return float(P @ t), float(P[2])

    def proyectar(self, P):
        Pc = (np.atleast_2d(P) - self.C) @ self.R.T
        return self.f * Pc[:, :2] / Pc[:, 2:3] + self.c


def resumen(valores):
    v = np.array(valores, float)
    return dict(media=round(float(v.mean()), 4), min=round(float(v.min()), 4), max=round(float(v.max()), 4), n=int(v.size))


def contorno(perfil, L):
    """Contorno simétrico (s, z, vuelo) en posición real, del alféizar izquierdo al derecho."""
    medio = []
    for e in reversed(ORDEN):  # de la esquina al merlón, lado izquierdo
        p = perfil[e]
        medio += [(-p["s_ext"], p["z_modelo"], 0.0), (-p["s_int"], p["z_modelo"], 0.0)]
    der = [(-s, z, d) for s, z, d in reversed(medio)]
    return medio, der


def main():
    lect = json.loads(LECTURAS.read_text())
    medida = json.loads(MEDIDA.read_text())
    alzado = json.loads((ROOT / "datos/alzado_sala.json").read_text())
    z_alf = alzado["niveles"]["pie_ventanas_tambor"]["z_m"]
    cam = Camara(medida["principal"]["camaras"][lect["clave"]])
    a_ajuste = medida["principal"]["nicho_m"]["a"]
    por_vano, acum = {}, {e: dict(s_int=[], s_ext=[], z=[]) for e in ORDEN}
    acum_L, acum_hn, acum_tip = [], [], []
    for nombre, v in lect["vanos"].items():
        cara = v["cara"]
        izq = [cam.plano(p, cara) for p in v["marco_exterior_izq"]]
        der = [cam.plano(p, cara) for p in v["marco_exterior_der"]]
        # Eje: centro del merlón, eje de simetría del remate. El punto medio de
        # los cantos del marco queda asimétrico por la lectura de los cantos.
        m = next(e for e in v["escalones"] if e["elemento"] == "merlon")
        eje = (cam.plano((m["x0"], m["y"]), cara)[0] + cam.plano((m["x1"], m["y"]), cara)[0]) / 2
        eje_marco = float(np.mean([s for s, _ in izq + der]))
        L = [abs(s - eje) for s, _ in izq + der]
        hn = [abs(cam.plano(p, cara)[0] - eje) for p in v["boca_izq"] + v["boca_der"]]
        tip = cam.plano(v["remate_merlon"], cara)[1]
        esc = []
        for e in v["escalones"]:
            s0, z0 = cam.plano((e["x0"], e["y"]), cara)
            s1, z1 = cam.plano((e["x1"], e["y"]), cara)
            r = sorted((abs(s0 - eje), abs(s1 - eje)))
            if e["elemento"] == "merlon":
                r = [0.0, abs(s1 - s0) / 2]
            z = (z0 + z1) / 2
            esc.append(dict(elemento=e["elemento"], lado=e["lado"], s_int=round(r[0], 4), s_ext=round(r[1], 4), z_alfeizar=round(z, 4)))
            acum[e["elemento"]]["s_int"].append(r[0])
            acum[e["elemento"]]["s_ext"].append(r[1])
            acum[e["elemento"]]["z"].append(z)
        acum_L += L
        acum_hn += hn
        acum_tip.append(tip)
        por_vano[nombre] = dict(
            eje_s_m=round(eje, 4), eje_marco_s_m=round(eje_marco, 4), semiancho_marco_m=resumen(L), semiancho_boca_m=resumen(hn),
            remate_merlon_z_alfeizar=round(tip, 4), escalones=esc,
        )
    perfil = {}
    for e in ORDEN:
        perfil[e] = dict(
            s_int=round(float(np.mean(acum[e]["s_int"])), 4) if e != "merlon" else 0.0,
            s_ext=round(float(np.mean(acum[e]["s_ext"])), 4),
            z=round(float(np.mean(acum[e]["z"])), 4),
            z_modelo=round(float(np.mean(acum[e]["z"])) + z_alf, 4),
            z_rango=[round(float(min(acum[e]["z"])), 4), round(float(max(acum[e]["z"])), 4)],
            s_ext_rango=[round(float(min(acum[e]["s_ext"])), 4), round(float(max(acum[e]["s_ext"])), 4)],
        )

    # Los tramos se tocan: cada límite interior es el exterior del anterior.
    for i in range(1, len(ORDEN)):
        perfil[ORDEN[i]]["s_int"] = perfil[ORDEN[i - 1]]["s_ext"]
    L = float(np.mean(acum_L))
    perfil["esquina"]["s_ext"] = round(L, 4)
    hn = float(np.mean(acum_hn))
    cs = lect["contraste_seccion"]
    from hiladas_ventanas import EJE_PX
    eje_col = EJE_PX - 0.59 * alzado["px_por_m"]
    f0 = alzado["niveles"]["arranque_cupula"]["fila_px"]
    seccion = {}
    for q in cs["puntos"]:
        e = q["elemento"]
        seccion.setdefault(e, []).append(dict(
            s_m=round((q["col"] - eje_col) / alzado["px_por_m"], 4),
            z_modelo=round((f0 - q["fila"]) / alzado["px_por_m"], 4)))
    for e in ORDEN:
        zs_ = [p["z_modelo"] for p in seccion.get(e, [])]
        perfil[e]["z_seccion_frontal"] = round(float(np.mean(zs_)), 4) if zs_ else None
        perfil[e]["diferencia_foto_menos_seccion_m"] = round(perfil[e]["z_modelo"] - float(np.mean(zs_)), 4) if zs_ else None
    res = dict(
        lecturas=str(LECTURAS.relative_to(ROOT)),
        sha256_lecturas=hashlib.sha256(LECTURAS.read_bytes()).hexdigest(),
        camara=f"datos/medida_nicho_fotos.json, principal, {lect['clave']}",
        z_alfeizar_modelo_m=z_alf,
        eje_ajuste_0041_m=a_ajuste,
        semiancho_marco_m=resumen(acum_L),
        semiancho_boca_m=resumen(acum_hn),
        remate_merlon=dict(z_alfeizar=resumen(acum_tip), z_modelo=round(float(np.mean(acum_tip)) + z_alf, 4)),
        perfil=perfil,
        seccion_frontal=seccion,
        por_vano=por_vano,
    )
    print(json.dumps({k: res[k] for k in ("semiancho_marco_m", "semiancho_boca_m", "remate_merlon")}, ensure_ascii=False))
    for e in ORDEN:
        print(e, perfil[e])
    for n, v in por_vano.items():
        print(n, "eje", v["eje_s_m"], "marco", v["eje_marco_s_m"], "(0041: ±%.3f)" % a_ajuste)

    # Comprobación cualitativa: contorno medio proyectado en las fotos ajustadas.
    izq, der = contorno(perfil, L)
    tip = float(np.mean(acum_tip))
    salida_previas = ROOT / "renders/previas/0043"
    salida_previas.mkdir(parents=True, exist_ok=True)
    for clave, c in medida["principal"]["camaras"].items():
        camk = Camara(c)
        bordes = json.loads((ROOT / f"datos/bordes_celosias_{clave}.json").read_text())
        img = Image.open(ROOT / bordes["foto"]).convert("RGB")
        dib = ImageDraw.Draw(img)
        for nombre, v in bordes["vanos"].items():
            n, t = ejes(v["cara"])
            s0 = a_ajuste if v["vano"] == 1 else -a_ajuste
            # Cotas del modelo -> sistema del ajuste (z = 0 en el alféizar).
            punto = lambda s, z, d: (APOTEMA - d) * n + (s0 + s) * t + [0, 0, z - z_alf]
            jamba = [(-L, z_alf, 0.0), (-L, perfil["esquina"]["z_modelo"], 0.0)]
            tramo = jamba + izq + der + [(L, perfil["esquina"]["z_modelo"], 0.0), (L, z_alf, 0.0)]
            pts = [tuple(p) for p in camk.proyectar(np.array([punto(*q) for q in tramo]))]
            dib.line(pts, fill=(0, 255, 255), width=3)
        img.thumbnail((2600, 2600))
        img.save(salida_previas / f"remate_{clave}.jpg", quality=88)
    SALIDA.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    print(SALIDA)


if __name__ == "__main__":
    main()
