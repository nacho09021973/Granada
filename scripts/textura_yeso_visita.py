"""Textura mineral periódica para Three.js. RG = pendientes métricas, B = tono."""

from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image

LADO_M = 0.32
N = 512
ROOT = Path(__file__).resolve().parents[1]


def main():
    rng = np.random.default_rng(3501)

    def ruido(s, t):
        a = gaussian_filter(rng.standard_normal((N, N)), (s, t), mode="wrap")
        return a / a.std()

    # Relieve de llana, grano y poros. Todo está en metros, sin desgaste pintado.
    llana, arido, fino = ruido(17, 35), ruido(2.4, 3.3), ruido(0.75, 0.9)
    poros = np.minimum(0, fino + 1.35)
    alto = 0.00019 * llana + 0.00009 * arido + 0.000042 * fino + 0.00013 * poros
    dydx = [
        (np.roll(alto, -1, axis=k) - np.roll(alto, 1, axis=k)) / (2 * LADO_M / N)
        for k in (1, 0)
    ]
    tono = 0.5 + 0.095 * llana + 0.10 * arido + 0.045 * fino + 0.055 * poros
    tile = np.stack([0.5 + dydx[0], 0.5 + dydx[1], tono], axis=-1)
    Image.fromarray(np.uint8(np.rint(np.clip(tile, 0, 1) * 255))).save(
        ROOT / "web/modelos/yeso.png"
    )


if __name__ == "__main__":
    main()
