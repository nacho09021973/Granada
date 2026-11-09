# 0018 — Dos filas por hilada de referencia

**Estado:** opción B elegida por el usuario el 2026-11-09; implementación
experimental, sin validación histórica.

## Elección y alcance

Se divide el paso vertical de la calibración vigente en dos. Las piezas
conservan su ancho tangencial y reducen altura y fondo a la mitad. Las dos
filas de cada hilada conservan la familia original (A o C).
El campo, A=2, signo positivo, función lineal y suavizado se conservan.
Las cotas originales permanecen entre las nuevas; las intermedias son una
elección, no mediciones adicionales. Hay 45 cotas interiores frente a 22:
se añade también la media hilada anterior a la clave excluida.

`--filas-por-hilada 2` es el defecto del script experimental
`scripts/render_hilada_campo.py`; `1` reproduce la variante previa.
Las funciones de biblioteca conservan `1` por compatibilidad. La malla del
visor y el modelo por celdas no se sustituyen.

## Corrección de la implementación tras la objeción del usuario

Codex implementó inicialmente una reducción uniforme en `9cf2289`, incluido
el ancho: obtuvo 11304 piezas. Fue una interpretación incorrecta de B;
el usuario señaló que dividir 2730 piezas en dos debe dar **5460**, cerca de
las 5416 de referencia. No era un fallo de esa cuenta.

Se corrige conservando el ancho y la familia por par de filas. La comparación
reproducida da **2730 frente a 5540 piezas**: 2730 en las cotas originales y
2810 en las intermedias. Las 80 piezas de diferencia respecto a 5460 proceden
de volver a teselar contornos distintos, incluida la última media hilada:
esto no es una división literal de cada pieza ya existente.
El recuento incluye solo los frentes admitidos; faltan lazos pequeños, clave
y cupulines. No es comparable como total completo de una restitución.

No se reajusta A para forzar el total. La variante uniforme errónea queda
trazada por el commit anterior, no se mantiene como opción activa.

## Procedencia y comprobaciones

El generador permanente guarda parámetros, entorno, hashes de entradas y
código, y recuentos por frente en `datos/comparacion_filas_campo.json`:

```bash
/tmp/granada-venv/bin/python scripts/render_hilada_campo.py --A 2 \
  --informe datos/comparacion_filas_campo.json
/tmp/granada-venv/bin/python scripts/render_hilada_campo.py --A 2 \
  --filas-por-hilada 2 --hiladas todas --lado 650 --subdivision 2 \
  --png renders/previas/cupula_campo_B_corregida.png
```

El entorno temporal contiene dependencias instaladas; el JSON registra sus
versiones efectivas, que no coinciden todas con `requirements.txt`.
Las pruebas contrastan las cotas originales y las intermedias, el fondo de
las piezas contra la solución analítica del cono (A=0), y una malla a media
altura y fondo con índices válidos y vértices finitos. Otra prueba divide cada
contorno original en dos y comprueba por separado que conserva familia y
número de piezas por fila. No prueban ausencia de solapes.

Verificación de la corrección: **758 tests pasan**. El render
`cupula_campo_B.png` pertenece a la interpretación anterior con ancho reducido;
no se usa para evaluar la corrección. La vista corregida se genera a 650 px
por vista y subdivisión 2. No se considera resuelto el punto 2 ni validada la
geometría por pasar pruebas de cotas.
La variante A se regenera con el mismo comando de render, cambiando
`--filas-por-hilada 1` y `--png renders/previas/cupula_campo_A.png`.

## Condiciones de rechazo

- Acercarse al total de referencia no valida la distribución ni la fidelidad
  histórica. El recuento sigue siendo parcial, sin cierres.
- Si persisten pliegues o solapes, se rechaza que reducir piezas baste para
  corregirlos. Pasar pruebas de cotas no autoriza promover la geometría.
- Una fuente con tamaño o distribución incompatibles obligaría a revisar la
  subdivisión. La elección del usuario no la convierte en dato histórico.
