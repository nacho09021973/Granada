# 0033 — Alcance local de la sustitución de la clave

Diagnóstico ejecutado el 2026-11-20. No cambia la geometría vigente.

## Pregunta y criterio previo

¿Basta sustituir `cupulilla_25` para eliminar el exceso sobre la cota de
calibración de 4,67 m? Si otros grupos también la exceden más allá del
redondeo de exportación, se descarta una corrección de altura limitada a
ese cierre. La forma histórica de la clave es una pregunta distinta.

## Resultado

En el OBJ identificado por SHA-256 en la salida, solo `cupulilla_25` supera
4,67 m con una tolerancia numérica de 0,000001 m. Su máximo es 5,481433 m;
el máximo de todos los otros grupos de la cúpula es 4,670000034 m.
El cierre tiene radio máximo 0,545383 m y alturas entre 4,394125 y
5,481433 m. Por tanto, eliminar el exceso de altura admite un ensayo local.
Esto no demuestra que una clave nueva encaje con las piezas vecinas.

Se contrastó el máximo por dos reducciones de los vértices y con el valor
de la auditoría 0032, comprobando también el hash de su OBJ. La comprobación
es interna a la misma malla; no es una medición independiente de la bóveda.

## Continuación acotada

El ensayo articulado de cupulín descrito en 0032 permanece local: su propia
evaluación no recupera las grandes caras rectangulares de la referencia.
No se extiende a los otros quince cupulines.

Para la clave, conservar el perímetro de encuentro, proponer un remate con
quiebros estrellados y declarar sus alturas intermedias como elecciones.
Comparar planta y sección con AA-415_23 p. 1 y las vistas de visitante con
igual cámara e iluminación. Rechazar el candidato si abre juntas nuevas,
supera la cota objetivo o necesita ocultar las hiladas vecinas para leerse.
El diseño y esa comparación siguen pendientes; el diagnóstico no los sustituye.

## Reproducción

```bash
.venv/bin/python scripts/diagnosticar_altura_clave.py
```

Código permanente: `scripts/diagnosticar_altura_clave.py`.
Salida: `datos/diagnostico_altura_clave.json`, con hash, escala y alcance.
