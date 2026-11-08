#!/usr/bin/env bash
# Renders de alta resolucion de la vista "sala" del modelo por celdas:
#   renders/cupula_cycles_sala_red_8k.png   (8192 px, de una pieza)
#   renders/cupula_cycles_sala_red_16k.png  (16384 px, por cuadrantes)
#
# El de 16k se hace en cuatro cuadrantes de 8192 px (el fotograma entero, con
# los pases del eliminador de ruido, puede pasar de 10 GB), se unen con
# scripts/unir_cuadrantes.py y se tapan las costuras con dos franjas de 512 px
# de una sola pieza (scripts/coser_franjas.py).
#
# Entrada: renders/cupula_red.obj y .mtl, que escribe
#   .venv/bin/python scripts/render_cupula_piezas.py --modelo red
# Usa la GPU (cuda); en WSL2 hace falta LD_LIBRARY_PATH=/usr/lib/wsl/lib (ver
# scripts/render_cycles.py). Los PNG van excluidos en .gitignore por tamano.
#
# Uso: scripts/render_sala_alta.sh [8k|16k|todo]   (por defecto, todo)
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ"
BLENDER="${BLENDER:-$HOME/.local/opt/blender/blender}"
PY="$RAIZ/.venv/bin/python"
OBJ="renders/cupula_red.obj"
MUESTRAS="${MUESTRAS:-128}"
PARTES="renders/partes_16k"
export LD_LIBRARY_PATH="/usr/lib/wsl/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

cycles() {  # lado sufijo salida [recorte]
    local extra=()
    [[ $# -ge 4 ]] && extra=(--recorte "$4")
    "$BLENDER" -b -P scripts/render_cycles.py -- --obj "$OBJ" --vistas sala \
        --lado "$1" --sufijo "$2" --salida "$3" --muestras "$MUESTRAS" \
        --dispositivo cuda "${extra[@]}" 2>&1 | grep -E "^->|Error|error" || true
    [[ -f "$3/cupula_cycles_sala$2.png" ]] || { echo "falta $3/cupula_cycles_sala$2.png" >&2; exit 1; }
}

modo="${1:-todo}"

if [[ $modo == 8k || $modo == todo ]]; then
    cycles 8192 _red_8k renders
fi

if [[ $modo == 16k || $modo == todo ]]; then
    mkdir -p "$PARTES"
    cycles 16384 _si "$PARTES" 0,0,0.5,0.5
    cycles 16384 _sd "$PARTES" 0.5,0,1,0.5
    cycles 16384 _ii "$PARTES" 0,0.5,0.5,1
    cycles 16384 _id "$PARTES" 0.5,0.5,1,1
    cycles 16384 _franja_v "$PARTES" 0.484375,0,0.515625,1
    cycles 16384 _franja_h "$PARTES" 0,0.484375,1,0.515625
    "$PY" scripts/unir_cuadrantes.py "$PARTES/unido.png" \
        "$PARTES/cupula_cycles_sala_si.png" "$PARTES/cupula_cycles_sala_sd.png" \
        "$PARTES/cupula_cycles_sala_ii.png" "$PARTES/cupula_cycles_sala_id.png"
    "$PY" scripts/coser_franjas.py "$PARTES/unido.png" \
        "$PARTES/cupula_cycles_sala_franja_v.png" "$PARTES/cupula_cycles_sala_franja_h.png" \
        renders/cupula_cycles_sala_red_16k.png
    rm -rf "$PARTES"
fi
