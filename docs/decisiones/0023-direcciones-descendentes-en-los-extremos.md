# 0023 — Direcciones descendentes en los extremos: fallo del método

**Estado:** diagnóstico, 2026-11-17. No cambia la colocación ni el campo.

## Pregunta

En los 42 extremos fallidos de 0022, ¿la parada se debe a la dirección
elegida por el integrador o a que la superficie encierra el punto? Se
estudia la misma superficie bilineal de 0022 (A=2, B, borde libre, rejillas
0,03 y 0,015). No se aumentan límites ni se cambia el campo.

## Método

`scripts/diagnosticar_direcciones_extremos.py`, sobre
`datos/ensayo_transporte_interior.json`:

1. **Local.** Pendiente unilateral en 720 direcciones y en −grad de cada
   celda contigua, usando la celda en la que entra cada dirección. Para la
   más pendiente y para la dirección del método se busca un paso aceptable
   con el criterio de 0022 (32 intentos desde media celda, baja H, subida
   por tramos ≤1e-10).
2. **Camino monótono certificado.** Búsqueda por aristas paralelas a los
   ejes, en la rejilla original (k=1) y subdividida (k=4), solo bajando o a
   igual altura, dentro del límite de recorrido de 0019 (2,96 catetos). En
   esas aristas la bilineal es lineal: la monotonía es exacta. Cada camino
   se recalcula con `valor_gradiente` y `subida_segmento`. Se aplica desde
   el extremo y desde la semilla.
3. **Subnivel.** Barrera minimax de 0020 desde la esquina más baja de la
   celda del extremo, comparada con H del extremo.

Un camino por aristas prueba que existe un descenso monótono. Su ausencia
no prueba encierro. El encierro discreto solo se afirma si, además, no hay
dirección descendente o la barrera minimax supera H del punto.

## Resultado

| Comprobación | Resultado |
|---|---|
| Extremos con alguna dirección descendente | 42/42 |
| … con paso aceptable en la más pendiente | 42/42 |
| Extremos que son mínimo local de la bilineal | 0/42 |
| Dirección del método con pendiente > 0 en la celda donde entra | 35/42 |
| Extremos sobre una arista de celda (<1e-6 celdas) | 25/42 (14/15 bilineales) |
| Extremos con camino certificado hasta la cota previa | 33/42 |
| Semillas con camino certificado (k=1 y k=4, ambas rejillas) | 16/16 |

Los siete extremos restantes en los que la dirección del método sí baja:
cinco son paradas por umbral 0,01 con norma 0,005–0,008, y dos son los
recorridos bilineales que agotan 4000 pasos con pasos de 3e-8 a 6e-8 catetos.

Sin camino certificado desde el extremo quedan nueve casos: semillas 2 y 5
en 0,03, y semilla 0 en 0,015, cada una con los tres métodos. En los tres
bilineales, el escape del subnivel exige superar H del extremo en 2,2e-4,
1,7e-4 y 1,8e-5 catetos (49, 38 y 4 µm). El integrador bajó a una cuenca
cerrada en la rejilla. Los seis interpolados quedan indeterminados. Desde
esas mismas semillas sí hay camino certificado.

Caminos certificados desde las semillas: 0,16–0,37 m, por debajo del límite
de 0,66 m. Ningún nodo sube; la subida por tramos es 0 y los dos evaluadores
coinciden. Ninguna búsqueda toca el borde de su ventana.

## Lectura

En esta superficie discreta, ninguna de las siete paradas de 0019 se debe
a un encierro geométrico desde la semilla. **Falla el método.** El modo
dominante es un valle sobre una arista de celda. El gradiente de una celda
apunta hacia la vecina, donde H sube, y el retroceso no encuentra paso.
Por eso la derivada bilineal de 0022 no ayudó: es exacta en cada celda,
pero no en la arista. Las otras causas son el umbral de gradiente,
pasos que tienden a cero y la entrada en cuencas cerradas de micras.

## Alcance

Los caminos certificados son escalonados por aristas de rejilla. Prueban
existencia, no sirven como trayectorias de pieza. No se ha probado nada
del campo continuo ni se han conectado trayectorias en bandas, contado
inversiones, intersecciones 3D o piezas. No se ha validado fidelidad
histórica. El candidato de arranque 0021 sigue separado.

Controles sintéticos en `tests/test_direcciones_extremos.py`: valle exacto
sobre una arista (0022 se para, aquí hay descenso y camino certificado) y
hoyo rodeado (sin descenso ni camino; barrera positiva → encierro).

## Artefactos

```bash
/tmp/granada-venv/bin/python scripts/diagnosticar_direcciones_extremos.py
/tmp/granada-venv/bin/python -m pytest -q
```

`datos/direcciones_extremos.json`: datos por extremo y por semilla,
caminos testigo, tolerancias, versiones y hashes. Suite: **771 tests
pasan**; `git diff --check` correcto.
