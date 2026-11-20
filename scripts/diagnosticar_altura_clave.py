"""Acotar una sustitución local de la clave sin modificar la malla vigente.

Ejecutar desde la raíz: .venv/bin/python scripts/diagnosticar_altura_clave.py
La cota objetivo es la calibración del modelo, no una nueva medida histórica.
"""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from granada.cupula import CATETO_M

OBJ = ROOT / "renders/previas/cupula_campo_vigente_1400.obj"
OBJETIVO_M = 4.67
TOLERANCIA_M = 1e-6  # Redondeo de coordenadas del OBJ, no tolerancia histórica.


def main():
    grupos = {}
    actual = None
    with OBJ.open() as entrada:
        for linea in entrada:
            if linea.startswith("g "):
                actual = linea.split()[1]
            elif linea.startswith("v ") and actual is not None:
                if actual.startswith(("hilada_", "cupulin_", "cupulilla_")):
                    grupos.setdefault(actual, []).append(list(map(float, linea.split()[1:])))
    resumen = []
    for nombre, puntos in grupos.items():
        v = np.asarray(puntos) * CATETO_M
        altos = v[:, 2] > OBJETIVO_M + TOLERANCIA_M
        r = np.linalg.norm(v[:, :2], axis=1)
        resumen.append(dict(grupo=nombre, vertices=len(v),
                            z_min_m=float(v[:, 2].min()), z_max_m=float(v[:, 2].max()),
                            radio_min_m=float(r.min()), radio_max_m=float(r.max()),
                            vertices_sobre_objetivo=int(altos.sum()),
                            radio_max_sobre_objetivo_m=float(r[altos].max()) if altos.any() else None))
    # Segunda vía: máximo global directo y reducción de máximos por grupo.
    todos = np.concatenate([np.asarray(v) for v in grupos.values()]) * CATETO_M
    maximo = float(todos[:, 2].max())
    assert abs(maximo - max(g["z_max_m"] for g in resumen)) < 1e-12
    auditoria = json.loads((ROOT / "datos/auditoria_geometria_obj.json").read_text())
    sha = hashlib.sha256(OBJ.read_bytes()).hexdigest()
    assert sha == auditoria["sha256_obj"]
    assert abs(maximo - auditoria["maximo_vertices_m"]) < 1e-5
    resto = [g for g in resumen if g["grupo"] != "cupulilla_25"]
    resultado = dict(
        procedencia=dict(script="scripts/diagnosticar_altura_clave.py",
                         obj=str(OBJ.relative_to(ROOT)), sha256_obj=sha,
                         cateto_m=CATETO_M),
        objetivo_m=OBJETIVO_M, tolerancia_exportacion_m=TOLERANCIA_M, maximo_m=maximo,
        maximo_sin_cupulilla_25_m=max(g["z_max_m"] for g in resto),
        grupos_sobre_objetivo=[g for g in resumen if g["vertices_sobre_objetivo"]],
        clave=next(g for g in resumen if g["grupo"] == "cupulilla_25"),
        alcance="Cotas de vértices del OBJ antes de modificadores; no mide visibilidad ni alturas históricas.",
    )
    destino = ROOT / "datos/diagnostico_altura_clave.json"
    destino.write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
