# 0011 — Se retira el código refutado

**Estado:** aceptada — 2026-08-29

## Decisión

`PROXIMOS-PASOS.md` mantenía una sección «Lo que hay que tirar» con la condición
explícita: *«No borrar todavía: hasta que el sustituto funcione, el código muerto
sirve de referencia»*. El sustituto ya funciona —`granada/perfil.py` y
`granada/malla.py`, decisión 0010— así que se retira.

| retirado | por qué | quién lo sustituye |
|---|---|---|
| `granada/estratificacion.py` entero | estratificación por **coronas polares**; el modelo correcto es un teselado, no anillos concéntricos | `granada/caras.py` y `granada/niveles.py` |
| `granada/celda.py::trapecio` | **inventada**: no corresponde a ninguna figura del sistema occidental documentado | `cuna` y `rombo`, que la tesis sí confirma |
| `adaraja.py::PuntoMalla`, `malla_adaraja`, `numeric_embedding_punto` | levantaban geometría desde el modelo de **cónica única**, refutado | `granada/malla.py` |
| `tests/test_estratificacion.py` | probaba el módulo retirado | — |

Con ellos se van sus entradas de `granada/__init__.py`.

## Lo que se conserva, y por qué

**La cónica racional.** `PerfilArco` no era el error: el error era usarla como
*modelo* de la pieza. Como **interpolador exacto en `Fraction`** entre los puntos
que la plantilla sí documenta, sigue siendo útil y no afirma nada. Por eso el
módulo pasa de `adaraja.py` a **`granada/conica.py`**: el nombre viejo prometía
un modelo de adaraja que ya no contiene.

Efecto secundario que merece la pena: al irse `numeric_embedding_punto`, el
módulo se queda **sin frontera numérica**. Es exacto de punta a punta, y su test
lo fija con una lista de excepciones vacía.

## Dos colisiones de nombres, resueltas al pasar

Aparecieron al exportar los módulos nuevos desde `granada/__init__.py`, y las
dos eran ambigüedades reales, no molestias de importación:

1. **`Plantilla`** significaba dos cosas: la figura de planta contra la que se
   clasifica una cara (`granada/caras.py`) y el perfil de la pieza. La segunda
   pasa a **`PlantillaPerfil`**, y su módulo de `plantilla.py` a
   **`granada/perfil.py`**.
2. **`celda`** era a la vez el módulo de la celda de planta (`granada/celda.py`)
   y la función que levanta su sólido. Exportarla **sombreaba el módulo** —lo
   detectó un test que dejó de encontrar las funciones que inspeccionaba—. La
   función pasa a **`pieza`**, que además hace pareja con `corona`.

## Qué no cambia

- La superficie pública por `granada` sigue completa: 65 nombres, todos
  existentes y todos declarados en `__all__`, comprobado.
- Los artefactos se regeneran idénticos: 105 celdas, 6.225 vértices, 12.030
  triángulos, residuo rms 0,234 m.
- La decisión 0002 sigue **obsoleta** y ahora además sin código detrás. Se
  conserva como registro de por qué la cónica única no valía.
