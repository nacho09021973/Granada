"""Lee los dos GLB y contrasta visibilidad y cobertura con las mismas cámaras."""
import argparse
import gzip
import hashlib
import json
import sys
import tempfile
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from talla_cupulin import medir_boca
from hiladas_ventanas import medir_sector


def examinar(archivo):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    datos = gzip.decompress(archivo.read_bytes())
    with tempfile.TemporaryDirectory() as temporal:
        glb = Path(temporal) / "entrada.glb"
        glb.write_bytes(datos)
        bpy.ops.import_scene.gltf(filepath=str(glb))
    bpy.context.view_layer.update()
    ficha = json.loads(archivo.with_name("dos-hermanas.json").read_text())
    escala = ficha["cateto_m"]
    centro = (np.load(ROOT / "renders/previas/piloto_asiento.npz")["v"][1:192:2] * escala).mean(axis=0)
    suelo = ficha["suelo_m"]
    boca = medir_boca(centro, suelo)
    sector = medir_sector(ficha["sector_00"]["apotema_m"], suelo)
    grafo = bpy.context.evaluated_depsgraph_get()
    cobertura = {}
    for n in (64, 128):
        xy = np.linspace(-3.35, 3.35, n)
        libres, rayos = 0, 0
        for x in xy:
            for y in xy:
                if x * x + y * y > 3.35**2:
                    continue
                hit, _, _, _, obj, _ = bpy.context.scene.ray_cast(grafo, (x, y, -.01), (0, 0, 1), distance=6)
                # El tambor y paredes no cuentan como cubierta del techo.
                libres += not hit or obj.name.startswith(("tambor", "sala_"))
                rayos += 1
        cobertura[str(n)] = dict(rayos=rayos, sin_cubierta=int(libres))
    return dict(archivo=str(archivo), sha256_glb=hashlib.sha256(datos).hexdigest(),
                boca=boca, sector=sector, cobertura=cobertura)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", type=Path, required=True)
    ap.add_argument("--despues", type=Path, required=True)
    ap.add_argument("--informe", type=Path, default=ROOT / "datos/comprobacion_alturas_visita.json")
    # Para cambios que alteran los vanos a propósito (0042, nicho más hondo): la
    # luz de cada vano solo tiene que seguir siendo visible, no conservarse.
    ap.add_argument("--vanos-cambiados", action="store_true")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    antes, despues = examinar(a.antes), examinar(a.despues)
    criterio = "cada vano visible (> 0 rayos)" if a.vanos_cambiados else "cada vano >= 95 % del anterior"
    resultado = dict(antes=antes, despues=despues, criterio_vanos=criterio,
                     sha256_script=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                     limite="Muestreo fijo, no prueba de estanqueidad ni validación histórica")
    a.informe.write_text(json.dumps(resultado, indent=2) + "\n")
    print(json.dumps(resultado), flush=True)
    for vista in antes["boca"]:
        assert despues["boca"][vista] >= .95 * antes["boca"][vista]
    for vista in antes["sector"]:
        assert min(despues["sector"][vista]["piezas_visibles"]) >= 2
        pares = zip(antes["sector"][vista]["cielo_por_ventana"], despues["sector"][vista]["cielo_por_ventana"])
        if a.vanos_cambiados:
            assert all(b > 0 for _, b in pares)
        else:
            assert all(b >= .95 * x for x, b in pares)
    for n in antes["cobertura"]:
        assert despues["cobertura"][n]["sin_cubierta"] <= antes["cobertura"][n]["sin_cubierta"]


if __name__ == "__main__":
    main()
