#!/usr/bin/env bash
# Tres vistas vigentes; dos CPU logicas y prioridad baja para convivir con Windows.
# Ejecutar desde la raiz del repositorio. El limite se hereda en todos los hijos.
set -euo pipefail
if [[ ${1:-} != --limitado ]]; then
    exec nice -n 15 taskset -c 0,1 bash "$0" --limitado
fi
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
export NUMEXPR_NUM_THREADS=2
salida=renders/previas
malla="$salida/cupula_campo_vigente_1400.obj"
date -Is
git rev-parse HEAD
sha256sum scripts/render_hilada_campo.py scripts/render_cycles.py
.venv/bin/python -u scripts/render_hilada_campo.py --hiladas todas \
    --color inauguracion --obj "$malla"
sha256sum "$malla" "${malla%.obj}.mtl"
"$HOME/.local/opt/blender/blender" -b -t 2 -P scripts/render_cycles.py -- \
    --obj "$malla" --vistas cupula,visitante,sala --lado 1400 \
    --muestras 128 --dispositivo cpu --luz penumbra \
    --salida "$salida" --sufijo _vigente_1400
.venv/bin/python scripts/comparar_con_ferrer.py \
    "$salida/comparativa_ferrer_vigente_1400.png" \
    "Vigente, cupula=$salida/cupula_cycles_cupula_vigente_1400.png" \
    "Vigente, visitante=$salida/cupula_cycles_visitante_vigente_1400.png" \
    "Vigente, sala=$salida/cupula_cycles_sala_vigente_1400.png"
date -Is
