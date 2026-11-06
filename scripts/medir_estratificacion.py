"""Mide la estratificacion de la cupula sobre la seccion de AA-415_23.

Rehace la medicion del 2026-08-24, que se hizo ad hoc sobre un render de la
pagina A0 a 150 ppi (236.2 px/m). Ahora se mide sobre la **ortoimagen nativa**
extraida del PDF, a 300 ppi: 472.5 px/m, el doble de resolucion, y con la
escala fijada por los vectores del propio autor en vez de medida sobre raster.

Calibracion (ver docs/fuentes.md, entrada 3)
-------------------------------------------
La escala grafica de la lamina son vectores exactos: 9449 unidades de flujo
para 10 m, y la matriz global del flujo es 0.12. De ahi 113.388 pt/m. La
ortoimagen de la seccion ocupa 1492.44 pt con 6219 px, luego

    472.488 px por metro real,   1 px = 2.116 mm

No se calibra midiendo la escala sobre la imagen: el numero viene del PDF.

Advertencia que sigue vigente
-----------------------------
Esto es fotometria sobre una ortofoto. La silueta depende de un umbral y la
cupula real esta deformada. Vale para construir un modelo verosimil, no para
afirmar como la trazo nadie en el siglo XIV.

Uso:  python3 scripts/medir_estratificacion.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

IMAGEN = Path("docs/AA-415_23_seccion.jpg")
SALIDA = Path("datos/estratificacion_medida.json")

# Calibracion derivada del PDF, no medida sobre la imagen.
UNIDADES_POR_METRO = 9449 / 10.0
CTM = 0.12
PT_POR_METRO = UNIDADES_POR_METRO * CTM
ANCHO_PX, ANCHO_PT = 6219, 12437 * CTM
PX_POR_METRO = ANCHO_PX / ANCHO_PT * PT_POR_METRO

UMBRALES = (240, 245, 250)


def silueta(gris: np.ndarray, umbral: int) -> tuple[np.ndarray, np.ndarray]:
    """Primer y ultimo pixel con tinta de cada fila. NaN si la fila esta vacia."""
    tinta = gris < umbral
    izq = np.full(gris.shape[0], np.nan)
    der = np.full(gris.shape[0], np.nan)
    for y in range(gris.shape[0]):
        col = np.nonzero(tinta[y])[0]
        if col.size:
            izq[y], der[y] = col[0], col[-1]
    return izq, der


def fin_del_cono(radio: np.ndarray, px_por_m: float) -> int:
    """Fila donde el radio deja de crecer y empieza el tambor de radio constante.

    Se busca el primer punto a partir del cual el radio ya no supera su maximo
    previo en mas de un pixel durante hilada y media seguida. No se elige a ojo.

    La ventana tiene que ser **mayor que un paso de hilada**: el perfil es
    escalonado, y la meseta de una hilada legitima dura un paso entero. Con
    media hilada el detector se para en la primera huella y da 1.4 m de cupula.
    """
    ventana = int(0.30 * px_por_m)  # 30 cm = hilada y media
    maximo = np.fmax.accumulate(np.nan_to_num(radio, nan=-1.0))
    for y in range(ventana, len(radio) - ventana):
        tramo = radio[y : y + ventana]
        if np.all(np.nan_to_num(tramo, nan=-1.0) <= maximo[y] + 1.0):
            return y
    return len(radio) - 1


def ajustar_cono(h: np.ndarray, r: np.ndarray, n_hiladas: int) -> dict:
    """Minimos cuadrados de radio(h), con el error reescalado a las hiladas.

    Los residuos de un perfil escalonado estan fuertemente correlacionados: el
    error nominal de un ajuste con miles de filas es ficticio. Se reescala al
    numero de hiladas independientes, que es la cautela del 2026-08-24.
    """
    A = np.vstack([h, np.ones_like(h)]).T
    (m, b), *_ = np.linalg.lstsq(A, r, rcond=None)
    residuo = r - (m * h + b)
    rms = float(np.sqrt(np.mean(residuo**2)))
    n = len(h)
    sxx = float(np.sum((h - h.mean()) ** 2))
    err_nominal = rms / np.sqrt(sxx)
    # N filas no son N observaciones independientes: solo hay n_hiladas peldanos.
    err = float(err_nominal * np.sqrt(n / max(n_hiladas, 2)))
    return {
        "pendiente": float(m),
        "ordenada": float(b),
        "rms": rms,
        "error": err,
        "error_nominal": float(err_nominal),
        "n_filas": n,
    }


def paso_por_autocorrelacion(gris: np.ndarray, y0: int, y1: int, cx: int) -> dict:
    """Autocorrelacion del perfil vertical de luminancia en una franja central."""
    ancho = int(0.60 * PX_POR_METRO)  # 60 cm, la franja de 280 px a 150 ppi
    franja = gris[y0:y1, cx - ancho // 2 : cx + ancho // 2].mean(axis=1)
    t = np.arange(franja.size)
    tendencia = np.polyval(np.polyfit(t, franja, 3), t)  # quita la tendencia lenta
    s = franja - tendencia
    s -= s.mean()
    ac = np.correlate(s, s, mode="full")[s.size - 1 :]
    ac /= ac[0]
    lo = int(0.10 * PX_POR_METRO)
    hi = int(0.40 * PX_POR_METRO)
    k = lo + int(np.argmax(ac[lo:hi]))
    return {"paso_px": k, "paso_m": k / PX_POR_METRO, "r": float(ac[k])}


def escalones_de_un_lado(h: np.ndarray, x: np.ndarray, salto_min: float) -> list[float]:
    """Alturas a las que un borde de la silueta da un salto hacia afuera."""
    alturas = []
    ultimo = x[0]
    for i in range(1, len(x)):
        if x[i] - ultimo >= salto_min:
            alturas.append(h[i])
            ultimo = x[i]
    return alturas


def escalones(h: np.ndarray, izq: np.ndarray, der: np.ndarray, salto_min: float) -> dict:
    """Cuenta los escalones **por lado**, no sobre el radio combinado.

    El radio es (der - izq)/2, y los dos bordes no escalonan a la vez: la
    seccion real no es simetrica al milimetro. Cada hilada aparece entonces como
    dos medios escalones en el radio, y contarlos ahi infla el numero y hunde el
    paso medio. A 236 px/m eso se disimulaba; a 472 px/m ya no.
    """
    d = escalones_de_un_lado(h, -izq, salto_min)   # el borde izquierdo se aleja hacia -x
    i = escalones_de_un_lado(h, der, salto_min)
    salida = {}
    for nombre, alturas in (("izquierdo", d), ("derecho", i)):
        pasos = np.diff(alturas)
        salida[nombre] = {
            "n_escalones": len(alturas),
            "paso_medio_m": float(pasos.mean()) if pasos.size else float("nan"),
            "paso_sd_m": float(pasos.std()) if pasos.size else float("nan"),
            "primero_m": float(alturas[0]) if alturas else float("nan"),
            "ultimo_m": float(alturas[-1]) if alturas else float("nan"),
        }
    n = [salida[k]["n_escalones"] for k in salida]
    p = [salida[k]["paso_medio_m"] for k in salida]
    salida["n_medio"] = float(np.mean(n))
    salida["paso_medio_m"] = float(np.nanmean(p))
    return salida


def main() -> None:
    gris = np.asarray(Image.open(IMAGEN).convert("L"), dtype=np.uint8)
    print(f"imagen  {gris.shape[1]} x {gris.shape[0]} px")
    print(f"escala  {PX_POR_METRO:.3f} px/m   (1 px = {1000 / PX_POR_METRO:.3f} mm)")
    print(f"        el 2026-08-24 fueron 236.2 px/m -> factor {PX_POR_METRO / 236.2:.3f}\n")

    res = {"px_por_metro": PX_POR_METRO, "umbrales": {}}
    for u in UMBRALES:
        izq, der = silueta(gris, u)
        radio_px = (der - izq) / 2.0
        cx = int(np.nanmedian((der + izq) / 2.0))
        y_fin = fin_del_cono(radio_px, PX_POR_METRO)

        # tramo conico, con los margenes del 2026-08-24: 0.25 m < h < h_fin - 5 cm
        y0 = int(0.25 * PX_POR_METRO)
        y1 = y_fin - int(0.05 * PX_POR_METRO)
        ys = np.arange(y0, y1)
        h = ys / PX_POR_METRO
        r = radio_px[y0:y1] / PX_POR_METRO
        ok = ~np.isnan(r)
        h, r = h[ok], r[ok]

        auto = paso_por_autocorrelacion(gris, y0, y1, cx)
        alt = y_fin / PX_POR_METRO
        # hiladas sobre la cupula entera, no sobre el tramo recortado del ajuste
        n_hil = max(int(round(alt / auto["paso_m"])), 2)
        salto_min = 0.6 * auto["paso_m"] * 0.78 * PX_POR_METRO  # 60 % del avance de una hilada
        esc = escalones(h, izq[y0:y1][ok], der[y0:y1][ok], salto_min)
        fit = ajustar_cono(h, r, n_hil)
        radio_tambor = float(np.nanmedian(radio_px[y_fin : y_fin + int(0.3 * PX_POR_METRO)]) / PX_POR_METRO)

        res["umbrales"][u] = {
            "altura_cupula_m": alt,
            "radio_arranque_m": float(fit["pendiente"] * alt + fit["ordenada"]),
            "radio_tambor_m": radio_tambor,
            "n_hiladas": n_hil,
            "paso_autocorrelacion": auto,
            "escalones": esc,
            "ajuste": fit,
            "angulo_cono_grados": float(np.degrees(np.arctan(fit["pendiente"]))),
        }
        d = res["umbrales"][u]
        print(f"umbral {u}")
        print(f"  altura de la cupula      {alt:.3f} m      (y_fin = {y_fin} px)")
        print(f"  radio en el arranque     {d['radio_arranque_m']:.3f} m")
        print(f"  radio del tambor         {radio_tambor:.3f} m")
        print(f"  paso por autocorrelacion {auto['paso_m'] * 100:.1f} cm  ({auto['paso_px']} px, r = {auto['r']:+.3f})")
        print(f"  paso por escalones       {esc['paso_medio_m'] * 100:.1f} cm  "
              f"({esc['izquierdo']['n_escalones']} izq / {esc['derecho']['n_escalones']} der)")
        print(f"  n hiladas                {n_hil}")
        print(f"  pendiente dr/dh          {fit['pendiente']:.4f} +/- {fit['error']:.4f}   (rms {fit['rms'] * 100:.1f} cm)")
        print(f"  angulo del cono          {d['angulo_cono_grados']:.2f} grados\n")

    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"escrito {SALIDA}")


if __name__ == "__main__":
    main()
