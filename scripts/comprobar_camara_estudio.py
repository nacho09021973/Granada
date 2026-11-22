"""Contrasta la cámara Blender con la proyección usada por la visita Three.js.

blender -b renders/previas/0039_cycles/estudio.blend -P scripts/comprobar_camara_estudio.py
"""

import hashlib
import json
import math
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]


def main():
    escena = bpy.context.scene
    camara = escena.camera
    ficha = json.loads((ROOT / "web/modelos/dos-hermanas.json").read_text())
    apa = ficha["sector_00"]["apotema_m"]
    # Contrato de cámara de verHiladas en web/visita.js: Y vertical en Three,
    # Z vertical en Blender. Perspectiva vertical de 46°, viewport 900 x 740.
    origen = Vector((1.75, 0.48, -1.38))
    objetivo = Vector((apa - 0.16, 0.30, -0.26))
    frente = (objetivo - origen).normalized()
    derecha = frente.cross(Vector((0, 0, 1))).normalized()
    arriba = derecha.cross(frente)
    aspecto = 900 / 740
    tangente = math.tan(math.radians(46) / 2)
    errores = []
    for p in [(apa, 0.59, 0.19), (apa, 0.59, -0.8),
              (apa, -0.59, -0.8), (apa - 0.134, 0.3, 0.33)]:
        p = Vector(p)
        delta = p - origen
        z = delta.dot(frente)
        esperado = ((1 + delta.dot(derecha) / (z * tangente * aspecto)) / 2,
                    (1 + delta.dot(arriba) / (z * tangente)) / 2)
        proyectado = world_to_camera_view(escena, camara, p)
        errores.append(max(abs(a - b) for a, b in zip(esperado, proyectado[:2])))
    error = max(errores)
    assert error < 1e-6, f"Las cámaras no coinciden: {error}"
    informe = dict(
        metodo="Proyección perspectiva por productos escalares frente a world_to_camera_view",
        puntos=4, error_max_fraccion_de_imagen=error,
        sha256_script=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        sha256_visita_js=hashlib.sha256((ROOT / "web/visita.js").read_bytes()).hexdigest(),
        sha256_blend=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
    )
    (ROOT / "datos/comprobacion_camara_estudio.json").write_text(json.dumps(informe, indent=2) + "\n")
    print(informe)


if __name__ == "__main__":
    main()
