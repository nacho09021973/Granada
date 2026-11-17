# 0022 — Ensayo de transporte interior: candidato rechazado

**Estado:** ensayo numérico fallido, 2026-11-17. No cambia la colocación.

## Pregunta y criterio previo

¿Sustituir la dirección interpolada de `np.gradient(H)` por la derivada
de la propia interpolación bilineal permite resolver las siete paradas
interiores de 0019 sin subir H? Se descarta como sustitución si no alcanza
la cota anterior, si sube H por encima de la tolerancia o sale de la rejilla.

## Ensayo acotado

`scripts/ensayar_transporte_interior.py` toma las siete semillas fallidas y
la llegada no monótona de `datos/diagnostico_paradas_campo.json`. No hace un
barrido nuevo. A=2, B y borde libre: se aísla el interior del candidato de
arranque 0021. No se modifica el campo para forzar una llegada.

En rejilla 0,03 se mantienen las coordenadas originales. En 0,015 se
proyectan sobre el segmento más cercano del mismo nivel de altura, sin
emparejar frentes por un índice que podría cambiar. El desplazamiento
máximo observado es 0,0215662 catetos, inferior al límite previo de dos
celdas originales (0,06). Esta comparación sigue semillas cercanas del
mismo nivel, no trayectorias matemáticamente idénticas.

Los tres controles comparten un integrador de descenso discreto: paso
máximo de media celda, hasta 32 retrocesos, límite de recorrido de 0019 y
4000 pasos. Se comparan dirección interpolada con umbral de gradiente
0,01, la misma dirección con umbral 1e-8 y derivada bilineal con umbral
1e-8. Se separa así el efecto del umbral del cambio de derivada dentro de
este integrador; no se identifica este método con `solve_ivp` de 0019.

Para aceptar un segmento no basta con comparar sus extremos. Se divide
por los cruces de celda; H es cuadrática en cada tramo y sus derivadas
extremas deben ser ≤1e-10 en el parámetro local. No se permite extrapolar,
saltar una subida ni añadir desvíos laterales. La llegada exige
|H−cota previa|≤1e-9. Son tolerancias numéricas, no monotonía exacta probada.

## Resultado

| Rejilla | Dirección | Umbral | Llegadas de las siete paradas | Llegada del control no monótono |
|---:|---|---:|---:|---:|
| 0,03 | interpolada | 0,01 | 0/7 | 0/1 |
| 0,03 | interpolada | 1e-8 | 0/7 | 0/1 |
| 0,03 | bilineal | 1e-8 | 0/7 | 0/1 |
| 0,015 | interpolada | 0,01 | 1/7 | 1/1 |
| 0,015 | interpolada | 1e-8 | 2/7 | 1/1 |
| 0,015 | bilineal | 1e-8 | 0/7 | 1/1 |

Las 48 trayectorias respetan el criterio de descenso, pero la dirección
bilineal no resuelve ninguna de las siete paradas. En la rejilla fina dos
casos bilineales alcanzan el límite de 4000 pasos; los otros cinco terminan
sin paso descendente aceptable. **Se rechaza este candidato como sustitución
de la colocación.** No se aumentan límites para perseguir el resultado.

Las llegadas con dirección interpolada cambian con rejilla y umbral. Esto
impide atribuir las siete paradas a una obstrucción geométrica estable.
También impide concluir que una derivada compatible baste para resolverlas.
No se ha probado la existencia ni la imposibilidad de otras rutas monótonas.

## Contrastes y alcance

La fórmula bilineal y su derivada se contrastan con un polinomio conocido,
diferencias centradas e interpolación de SciPy. Un caso H=x(1−y) comprueba
que se detecta la subida interior de un segmento con extremos iguales.
Otros controles incluyen descenso sobre un plano y cota inexistente.

En los recorridos reales, un segundo evaluador (`map_coordinates`, el de
0019) difiere como máximo 3,56e-15 catetos de la fórmula local. Muestreando
cinco puntos por segmento, su aumento máximo es 9,74e-11, dentro de la
tolerancia. Las seis llegadas de los controles quedan a menos de 1,2 mm de
muestras del contorno previo; es una comprobación geométrica aproximada.

No se han conectado trayectorias vecinas en bandas ni contado inversiones
de bandas, intersecciones 3D o piezas. No se ha validado fidelidad histórica.

## Artefactos y siguiente paso

```bash
/tmp/granada-venv/bin/python scripts/ensayar_transporte_interior.py
/tmp/granada-venv/bin/python -m pytest -q
```

`datos/ensayo_transporte_interior.json` conserva los 48 recorridos completos,
fallos, cotas, proyecciones, contrastes, parámetros, versiones y hashes.
Suite: **769 tests pasan**; `git diff --check` correcto.

Siguiente paso acotado: diagnosticar las direcciones descendentes disponibles
en los puntos finales y sus celdas vecinas. Separar un fallo de la dirección
elegida de un encierro del subnivel. Solo después decidir si procede otro
transporte. El candidato de arranque 0021 queda separado; cierres y cambio
del generador siguen pendientes.
