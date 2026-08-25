# 0004 — Red de medinas completa antes de propagar niveles

**Estado:** aceptada — 2026-08-24

## Contexto

`datos/red_medinas.json` contenía 71 nudos y 48 aristas de una detección
parcial. El grafo tenía 24 componentes conexas y 11 nudos aislados: no era una
base admisible para propagar niveles desde el borde.

La figura 128 de Ferrer Pérez-Blanco no es una planta homogénea: contrapone la
propuesta del autor en la mitad superior al dibujo de Jones y Goury en la
inferior. Mezclar las dos mitades produciría una topología sin fuente única.

## Decision

1. Extraer la imagen embebida de la página 236 del PDF con `pdfimages`.
2. Usar solo la mitad superior, propuesta por el autor, y generar la inferior
   por reflexión sobre `y = 273.5 px`. Esta operación se apoya en la simetría
   especular D8 medida independientemente en la cupula.
3. Excluir el octógono punteado editorial, adelgazar el componente principal a
   un esqueleto y agrupar las vecindades de cruce.
4. Seguir cada camino entre cruces y conservar sus giros mediante
   Ramer-Douglas-Peucker con tolerancia de 2 px. Por tanto, cada arista del dato
   es un tramo aproximadamente recto, no una cuerda que atraviesa un giro.
5. Guardar como `nodos_borde` los terminales de grado uno. Son candidatos a
   ancla para la fase de niveles, no niveles asignados.

El procedimiento reproducible está en `scripts/completar_red_medinas.py`. Las
dependencias raster permanecen en el área de análisis; el núcleo `granada/`
continúa sin dependencias.

## Controles aceptados

- 323 nudos y 427 aristas;
- una sola componente conexa y 105 ciclos independientes;
- 24 terminales de borde, sin nudos aislados;
- misma topología con umbrales de gris 170, 200 y 230;
- tramo mínimo de 5.02 px, sin fragmentos ultracortos de cruce;
- desviación mediana de 2.20 grados respecto de las cuatro direcciones de
  medina; 77.3 % de los tramos queda a 5 grados o menos.

## Techo de afirmacion

El dato representa la **red de medinas de la propuesta publicada**, completada
por una simetría medida. No identifica por sí solo las caras/teselas, su tipo,
el sentido de ascenso ni su salto de nivel, y no convierte la propuesta en una
reconstrucción histórica demostrada.

La conectividad deja de ser el bloqueo. La propagación sigue cerrada hasta que
cada paso tenga una restricción firmada y auditable (ascenso, descanso o
descenso); el mero hecho de cruzar una medina no determina ese signo.
