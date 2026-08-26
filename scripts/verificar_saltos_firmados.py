"""Somete la hipotesis de simetria al primer salto de nivel que llegue firmado.

Uso:
    python3 scripts/verificar_saltos_firmados.py                 # sin datos
    python3 scripts/verificar_saltos_firmados.py saltos.json     # con datos
    python3 scripts/verificar_saltos_firmados.py --ejemplo       # que pasaria si

El fichero de saltos es una lista de objetos con `a`, `b`, `salto` y
`evidencia`. El salto va en niveles, no en unidades: +1 es una adaraja mas
arriba, -1 mas abajo, 0 descanso. La evidencia es obligatoria — un salto sin
procedencia no entra.

    [
      {"a": "c000", "b": "c001", "salto": 1,
       "evidencia": "Almagro, nube de puntos, correo del ..."}
    ]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from granada.falsacion import cociente_de_orbitas, examinar  # noqa: E402
from granada.niveles import RelacionVecindad  # noqa: E402

CARAS = Path("datos/caras_red.json")
ORBITAS = Path("datos/orbitas_caras.json")


def cargar_cociente():
    caras = json.loads(CARAS.read_text(encoding="utf-8"))
    orbitas = json.loads(ORBITAS.read_text(encoding="utf-8"))
    return cociente_de_orbitas(caras["vecindades"], orbitas["orbitas"])


def leer_saltos(ruta: Path) -> list[RelacionVecindad]:
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    return [
        RelacionVecindad(
            origen=str(d["a"]),
            destino=str(d["b"]),
            salto=int(d["salto"]),
            evidencia=str(d.get("evidencia", "")),
        )
        for d in datos
    ]


def describir_cociente(c) -> None:
    print(f"caras                    {len(c.de_orbita)}")
    print(f"vecindades interiores    {c.n_vecindades}")
    print(f"orbitas                  {c.n_orbitas}")
    print(f"clases de vecindad       {c.n_aristas}   <- las 211 colapsan aqui")
    print(f"ciclos de cierre         {c.ciclos_independientes}   <- ecuaciones que refutan")
    print()
    anomalas = c.clases_con_tamano_anomalo()
    if anomalas:
        print("AVISO — clases cuyo tamano no divide al orden del grupo:")
        for clase in anomalas:
            izq, der = c.caras_sin_pareja(clase)
            print(f"   orbitas {clase[0]}-{clase[1]}: {len(c.clases[clase])} vecindades, "
                  f"deberian ser 16")
            print(f"      sin pareja: {', '.join(izq)} (orbita {clase[0]})  y  "
                  f"{', '.join(der)} (orbita {clase[1]})")
        print("   No refuta la simetria: acusa a los datos. Ver docs/decisiones.")
        print()

    print("cuanto rinde cada clase, si se firma una sola de sus vecindades:")
    for clase, vs in sorted(c.clases.items(), key=lambda kv: -len(kv[1])):
        print(f"   orbitas {clase[0]:2d}-{clase[1]:2d}   {len(vs):2d} vecindades   "
              f"ej. {vs[0][0]}->{vs[0][1]}")


def main(argv: list[str]) -> int:
    c = cargar_cociente()

    if "--ejemplo" in argv:
        describir_cociente(c)
        print("\n--- que pasaria con un solo salto firmado (simulacion) ---")
        clase, vs = max(c.clases.items(), key=lambda kv: len(kv[1]))
        a, b = vs[0]
        ficticio = [RelacionVecindad(a, b, 1, "SIMULADO, no es un dato")]
        print(examinar(ficticio, c).resumen())
        print("\n--- y con dos saltos incompatibles de la misma clase ---")
        a2, b2 = vs[1]
        roto = [
            RelacionVecindad(a, b, 1, "SIMULADO"),
            RelacionVecindad(a2, b2, -1, "SIMULADO"),
        ]
        print(examinar(roto, c).resumen())
        return 0

    rutas = [a for a in argv[1:] if not a.startswith("-")]
    saltos = leer_saltos(Path(rutas[0])) if rutas else []
    if not saltos:
        print("No hay ningun salto firmado. El estado sigue siendo")
        print("BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS.\n")
        describir_cociente(c)
        print()

    informe = examinar(saltos, c)
    print(informe.resumen())
    return 2 if informe.esta_refutada else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
