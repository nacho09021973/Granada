# 0020 — Paradas del flujo y barreras discretas

**Estado:** diagnóstico, 2026-11-17. Continúa 0019 y el punto 2 de
`PROXIMOS-PASOS.md`; no sustituye la colocación.

## Pregunta y descarte previo

¿Las siete paradas interiores de 0019 quedan encerradas por una barrera de
altura, o la parada numérica está impidiendo continuar? Una conexión que
necesite subir H no sirve como transporte descendente. Este diagnóstico no
acepta una ruta solo por conectar sus extremos.

## Método reproducible

`scripts/diagnosticar_paradas_campo.py` reproduce solo las 31 muestras
problemáticas del informe de 0019: 23 paradas de borde, siete interiores y
una llegada con incumplimiento de monotonía. Conserva B, A=2, el muestreo y
el integrador anteriores. No es un nuevo barrido ni aumenta su cobertura.

Para cada parada interior toma el nodo de rejilla más cercano al extremo y
busca la menor altura máxima necesaria para alcanzar un nodo H≤cota previa.
Usa Dijkstra minimax sobre cuatro vecinos y conserva el camino testigo.
Una segunda vía etiqueta las componentes de los subniveles: conecta en el
umbral calculado y no conecta estrictamente por debajo. Los siete casos
pasan ese contraste.

## Resultado y límites

- Se reproducen las 30 paradas y la llegada con falta de monotonía.
- Seis de las siete paradas interiores tienen barrera adicional **cero desde
  el nodo inicial**. Eso no equivale a un camino monótono: permite bajar y
  volver a subir mientras no se supere la altura inicial.
- La restante, en la fila 18, tiene barrera de **0,000282055 catetos de
  altura**. El desajuste entre H del nodo inicial y H interpolada en el
  extremo es −0,000164111. Esta escala exige estudiar la discretización
  antes de atribuir la barrera al campo continuo.
- Las 23 paradas de borde terminan con H entre 0 y 0,000851577 catetos.
  Sus radios exceden el radio base entre **0,0060 y 0,2109 m**. El campo
  rasterizado tiene una meseta exterior y el término suavizado de la red
  puede extenderse fuera del radio base. Alcanzar H≈0 no selecciona por sí
  solo el círculo arquitectónico de arranque; fijarlo requiere una condición
  de borde explícita.

No se demuestra que las conexiones monótonas existan ni que sean imposibles.
No se ha refinado la rejilla ni probado un transporte alternativo. No se
cuentan intersecciones 3D ni se valida fidelidad histórica.

## Siguiente paso acotado

Separar dos trabajos: definir el dominio y la condición geométrica del
arranque; y ensayar un transporte interior que use una derivada compatible
con la interpolación de H y declare sus fallos. Contrastar las paradas con
rejilla más fina antes de promover una solución. No saltarse una subida de
H, ni tapar con cierres una conexión fallida.

## Reproducción

```bash
/tmp/granada-venv/bin/python scripts/diagnosticar_paradas_campo.py
/tmp/granada-venv/bin/python -m pytest -q
```

Salida: `datos/diagnostico_paradas_campo.json`, con extremos, caminos,
parámetros, versiones y hashes de código, insumos e informe de entrada.
Las pruebas incluyen cuenca sintética, cota inexistente, bajada sin barrera
y contraste con conectividad de subniveles en 84 configuraciones pequeñas.
Suite verificada: **763 tests pasan**.
