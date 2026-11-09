# 0019 — El desplazamiento recto no conecta las filas; ensayo de flujo

**Estado:** diagnóstico local y ensayo numérico, 2026-11-09. No se sustituye
la colocación ni se da por resuelto el punto 2 de la hoja de ruta.

## Pregunta y criterio previo

Con B, A=2 y el resto de parámetros fijos: ¿el fondo de cada pieza alcanza
el contorno de la cota anterior sin invertir localmente la banda?
Si el control A=0 fallaba, había que rehacer la colocación antes de continuar.
Los ensayos de conexión tampoco se aceptan globalmente si no llegan a la
cota o si el campo deja de decrecer en la trayectoria.

## Método y alcance

`scripts/diagnosticar_colocacion_campo.py` muestrea la banda auxiliar definida
por longitud de arco y profundidad normalizada. Cuenta triángulos cuyo signo
se invierte respecto al sentido del frente; no cuenta intersecciones 3D de
piezas ni traduce cada triángulo a una pieza defectuosa.

Dos comprobaciones de llegada independientes del desplazamiento empleado:

- evaluar H en el fondo y restar la cota anterior;
- medir distancia a los contornos de esa cota con un árbol espacial. Es
  distancia a muestras del contorno, con tolerancia de dos celdas (~1,34 cm).

El SVG muestra plantas de cinco piezas, sus trayectorias y un perfil del
campo a lo largo de la trayectoria de mayor error. Este perfil no es una
sección del sólido arquitectónico.

## Resultado reproducido

| Control | muestreo ds / capas | inversiones de la banda | máximo error de llegada, en pasos de fila |
|---|---|---:|---:|
| A=0 | 0,06 / 20 | 0 | 0,0212 |
| A=0 | 0,03 / 40 | 0 | 0,0212 |
| A=2 | 0,06 / 20 | 27390 | 3,6803 |
| A=2 | 0,03 / 40 | 110408 | 3,6807 |

Las cifras de inversiones son conteos de triángulos de dos muestreos distintos,
no son comparables como número de defectos: al refinar se cuadruplica
aproximadamente el número de triángulos. El pequeño residuo de A=0 se concentra
en el arranque, donde el cono rasterizado se aplana en H=0.

Se selecciona el anillo de mayor error entre las filas 20 y 38: fila 24,
familia C, 142 piezas. El fondo del desplazamiento actual queda hasta
**15,95 cm** del contorno anterior; con muestreo fino, **15,88 cm**. La banda
del anillo tiene 306 y 1245 triángulos invertidos, respectivamente.
La aproximación recta por el gradiente no basta para esta geometría.

## Ensayo de corrección y límite encontrado

Se sigue la dirección de bajada del campo, actualizándola durante el recorrido,
con `solve_ivp` hasta H=cota anterior. Se para también cerca de gradiente nulo
(norma <0,01) o al alcanzar un recorrido máximo declarado en el código.
No se rellenan ni se esconden las trayectorias que no llegan.

En una ventana de 1,92 catetos alrededor del peor extremo del anillo de la
fila 24, llegan **33/33**, y **65/65** con muestreo fino. La banda de esa
ventana no presenta inversiones en ninguno de los dos muestreos.

La extensión a 33 puntos repartidos por cada uno de los 63 frentes da
**2049/2079 llegadas**. De las 30 sin llegada, 23 pertenecen al arranque H=0,
que requiere tratamiento de borde; **7 son interiores**, con parada cerca
de gradiente nulo, en las filas 17, 18 y 24. Una trayectoria adicional llega
pero incumple la tolerancia de monotonía. Estas paradas numéricas no prueban
por sí solas una obstrucción matemática del campo continuo.

Por tanto, **el flujo no se aplica como sustitución global**. La mejora local
no resuelve el transporte cerca de puntos críticos ni autoriza a tapar los
defectos con cierres. El siguiente cambio estructural necesita tratar por
separado el arranque y las conexiones entre ramas cerca de esos puntos.

## Reproducción y pruebas

```bash
/tmp/granada-venv/bin/python scripts/diagnosticar_colocacion_campo.py --flujo-todos
/tmp/granada-venv/bin/python scripts/diagnosticar_colocacion_campo.py \
  --ds 0.03 --capas 40 --flujo-muestras 65 \
  --salida datos/diagnostico_colocacion_campo_fino.json \
  --svg renders/diagnostico_colocacion_campo_fino.svg
```

Los dos JSON guardan parámetros, versiones y hashes de código e insumos.
Las pruebas nuevas contrastan el cono con su radio analítico y comprueban
que una cota inexistente produce fallo explícito. Suite: **760 tests pasan**.
No se ha cambiado el generador, el recuento B (5540), el color ni el visor.
