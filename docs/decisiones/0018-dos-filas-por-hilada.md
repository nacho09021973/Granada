# 0018 — Dos filas por hilada de referencia

**Estado:** opción B elegida por el usuario el 2026-11-09; implementación
experimental, sin validación histórica.

## Elección y alcance

Se divide el paso vertical de la calibración vigente en dos. Las piezas se
reducen a media escala en las tres coordenadas; también su ancho tangencial.
El campo, A=2, signo positivo, función lineal y suavizado se conservan.
Las cotas originales permanecen entre las nuevas; las intermedias son una
elección, no mediciones adicionales. Hay 45 cotas interiores frente a 22:
se añade también la media hilada anterior a la clave excluida.

`--filas-por-hilada 2` es el defecto del script experimental
`scripts/render_hilada_campo.py`; `1` reproduce la variante previa.
Las funciones de biblioteca conservan `1` por compatibilidad. La malla del
visor y el modelo por celdas no se sustituyen.

## Corrección de la previsión

La hoja de ruta suponía que B acercaría 2730 piezas a las 5416 atribuidas a
Jones y Goury. Esa previsión no es correcta al reducir las piezas en todas
las direcciones: hay aproximadamente el doble de filas y el doble de piezas
por fila. La comparación reproducida da **2730 frente a 11304 piezas**.
El recuento incluye solo los frentes admitidos; faltan lazos pequeños, clave
y cupulines. No es comparable como total completo de una restitución.

No se ha reajustado A, el ancho ni la secuencia para forzar un total. Reducir
solo altura y fondo conservando ancho sería otra decisión, no la media escala
uniforme implementada aquí.

## Procedencia y comprobaciones

El generador permanente guarda parámetros, entorno, hashes de entradas y
código, y recuentos por frente en `datos/comparacion_filas_campo.json`:

```bash
/tmp/granada-venv/bin/python scripts/render_hilada_campo.py --A 2 \
  --informe datos/comparacion_filas_campo.json
/tmp/granada-venv/bin/python scripts/render_hilada_campo.py --A 2 \
  --filas-por-hilada 2 --hiladas todas --lado 650 --subdivision 2 \
  --png renders/previas/cupula_campo_B.png
```

El entorno temporal contiene dependencias instaladas; el JSON registra sus
versiones efectivas, que no coinciden todas con `requirements.txt`.
Las pruebas contrastan las cotas originales y las intermedias, el fondo de
las piezas contra la solución analítica del cono (A=0), y una malla a media
escala con índices válidos y vértices finitos. No prueban ausencia de solapes.

Verificación en esta sesión: **757 tests pasan**. Se generaron y miraron
`renders/previas/cupula_campo_A.png` y `cupula_campo_B.png` con las mismas dos
cámaras, 650 px por vista y subdivisión 2. B muestra filas más finas y
continuas; persisten irregularidades en la zona media e interior y huecos
sin cierre. Es una lectura visual de baja resolución, no una medición de
solapes ni una validación histórica. No se considera resuelto el punto 2.
La variante A se regenera con el mismo comando de render, cambiando
`--filas-por-hilada 1` y `--png renders/previas/cupula_campo_A.png`.

## Condiciones de rechazo

- La pretensión de que esta opción aproxima el total a 5416 queda rechazada
  por el propio recuento; no se usa como calibración histórica.
- Si persisten pliegues o solapes, se rechaza que reducir piezas baste para
  corregirlos. Pasar pruebas de cotas no autoriza promover la geometría.
- Una fuente con tamaño o distribución incompatibles obligaría a revisar la
  subdivisión. La elección del usuario no la convierte en dato histórico.
