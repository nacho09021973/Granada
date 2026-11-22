"""Contrasta el encaje de 0036 con sus lecturas de sección, sin mover la malla.

Uso: .venv/bin/python scripts/diagnosticar_desfase_ventanas.py
Las lecturas manuales no se convierten aquí en una medición nueva.
"""

import ast
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def main():
    fuentes = ["scripts/hiladas_ventanas.py", "scripts/detalle_visita.py",
               "datos/alzado_sala.json", "web/modelos/dos-hermanas.json",
               "docs/AA-415_23_seccion.jpg", "scripts/diagnosticar_desfase_ventanas.py"]
    arbol = ast.parse((ROOT / fuentes[0]).read_text())
    constantes = {}
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign):
            for destino in nodo.targets:
                if isinstance(destino, ast.Name) and destino.id in {
                    "APICE_MODELO", "FILA_APICE", "INFERIOR", "SUPERIOR"
                }:
                    constantes[destino.id] = ast.literal_eval(nodo.value)
    alzado = json.loads((ROOT / fuentes[2]).read_text())
    ficha = json.loads((ROOT / fuentes[3]).read_text())
    escala = alzado["px_por_m"]
    origen = alzado["niveles"]["arranque_cupula"]["fila_px"]
    alf = alzado["niveles"]["pie_ventanas_tambor"]
    apice = constantes["APICE_MODELO"]
    fila = constantes["FILA_APICE"]
    referencia = (origen - fila) / escala
    desfase = apice - referencia
    # Segunda vía: altura del vano desde el alféizar. Cancela el origen z.
    alto_seccion = (alf["fila_px"] - fila) / escala
    alto_modelo = apice - alf["z_m"]
    desfase_por_alturas = alto_modelo - alto_seccion
    # El JSON de alzado redondea a milímetros.
    assert abs(desfase - desfase_por_alturas) < 0.0005
    encaje_activo = ficha["sector_00"].get("encaje", "0036")
    desfase_activo = ficha["sector_00"]["desplazamiento_vertical_seccion_m"]
    assert abs((0 if encaje_activo == "seccion" else desfase) - desfase_activo) < 1e-12
    filas = {}
    for orden in ("INFERIOR", "SUPERIOR"):
        crestas = [pieza[2] for pieza in constantes[orden]]
        cotas = [(origen - y) / escala for y in crestas]
        filas[orden.lower()] = {
            "crestas_px": crestas,
            "cotas_seccion_m": cotas,
            "crestas_sobre_z_cero": sum(z > 0 for z in cotas),
            "rango_cotas_seccion_m": [min(cotas), max(cotas)],
        }
    salida = {
        "fuente_primaria": "docs/AA-415_23.pdf p.1; imagen de sección local",
        "naturaleza": "Contraste de lecturas manuales existentes, no nueva medición",
        "sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in fuentes},
        "px_por_m": escala,
        "origen_px": origen,
        "fila_apice_px": fila,
        "apice_seccion_m": referencia,
        "apice_modelo_m": apice,
        "desfase_m": desfase,
        "encaje_activo": encaje_activo,
        "desfase_encaje_activo_m": desfase_activo,
        "desfase_por_altura_desde_alfeizar_m": desfase_por_alturas,
        "altura_vano_seccion_m": alto_seccion,
        "altura_vano_modelo_m": alto_modelo,
        "ordenes": filas,
        "conclusion": "El control 0036 hereda el ápice supuesto de 0035 y limita la segunda junta a -0.013 m. El modo seccion usa el origen común del alzado y elimina ese límite; el encaje activo se indica por separado.",
        "pendiente": "Las profundidades y la abertura luminosa siguen propuestas; contrastar con una vista oblicua registrada antes de extender el piloto.",
    }
    destino = ROOT / "datos/diagnostico_desfase_ventanas.json"
    destino.write_text(json.dumps(salida, indent=2, ensure_ascii=False) + "\n")
    # Referencia visual local; no redistribuir la ortoimagen de terceros.
    imagen = Image.open(ROOT / "docs/AA-415_23_seccion.jpg").convert("RGB")
    caja = (1780, 1900, 3340, 2240)
    imagen = imagen.crop(caja)
    dibujo = ImageDraw.Draw(imagen)
    for y, texto, color in [(origen, "z=0 del alzado", "red"),
                             (fila, "apice leido en la seccion", "cyan"),
                             (round(origen - apice * escala), "apice supuesto del control 0036", "yellow")]:
        local = y - caja[1]
        dibujo.line((0, local, imagen.width, local), fill=color, width=2)
        dibujo.text((8, local + 3), texto, fill=color, stroke_width=1, stroke_fill="black")
    for orden in ("INFERIOR", "SUPERIOR"):
        for _, x, y in constantes[orden]:
            x, y = x - caja[0], y - caja[1]
            dibujo.ellipse((x - 4, y - 4, x + 4, y + 4), outline="cyan", width=2)
    previa = ROOT / "renders/previas/2026-11-21_desfase_ventanas.png"
    previa.parent.mkdir(parents=True, exist_ok=True)
    imagen.save(previa)
    print(f"Desfase: {desfase:.6f} m; por alturas: {desfase_por_alturas:.6f} m")
    print(f"Crestas superiores sobre z=0: {filas['superior']['crestas_sobre_z_cero']}")
    print(destino)


if __name__ == "__main__":
    main()
