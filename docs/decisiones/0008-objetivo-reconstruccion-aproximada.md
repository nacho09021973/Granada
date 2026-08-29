# 0008 — El objetivo es la mejor reconstrucción posible, no la exacta

**Estado:** aceptada — 2026-08-29

## Decisión

El objetivo del proyecto deja de ser la reconstrucción **exacta** en 3D de la
cúpula de la Sala de las Dos Hermanas. Pasa a ser la **mejor reconstrucción
posible con los datos disponibles**: no exacta, sí muy aproximada, y explícita
sobre en qué se apoya cada parte.

El motivo es material, no de conveniencia: **las fuentes no coinciden entre
sí**. El recuento de niveles da 23 hiladas medidas sobre la sección, 24 en el
recuento rápido de Ferrer y 7 en la divulgación del PMAA. La pauta de 8
unidades entre niveles es reconstrucción moderna documentada, no regla escrita.
No existe en el dominio público ninguna tabla que asocie cada pieza a una cota
(entrada 8 de `fuentes.md`). Una reconstrucción exacta exigiría un dato que no
está, y esperar a que aparezca ha dejado el modelo 3D parado.

## Lo que cambia

- El entregable es un modelo completo y renderizable. Ya no queda supeditado a
  que se firmen las 227 vecindades.
- `datos/niveles_aproximados.json` (decisión 0007) pasa de hipótesis paralela a
  **entrada normal del levantamiento**, con su etiqueta intacta.
- Se admite material de reconstrucción de terceros —las maquetas y el render de
  la entrada 12— como referencia de cómo se resuelve la geometría, cosa que el
  objetivo anterior no permitía.

## Lo que no cambia

- **La separación (A)/(B) del README se mantiene.** Sigue habiendo una
  afirmación matemática exacta y una afirmación empírica sujeta a evidencia.
  Lo que cambia es el techo declarado de (B), no que (B) se dé por buena.
- **`BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` sigue vigente sobre el dato
  histórico.** Los 227 saltos de `datos/caras_red.json` siguen sin firmar.
  Ahora acota la etiqueta del resultado, no la existencia del resultado.
- Los tres atajos refutados en la decisión 0006 siguen refutados. «Aproximado»
  no reabre lo que tiene ciclo testigo.
- Las cautelas de `PROXIMOS-PASOS.md` siguen en pie, en especial que la cúpula
  real está deformada y que la red espejada nunca sirve como evidencia de
  simetría.

## Cómo se etiqueta a partir de ahora

Toda salida lleva, junto al modelo, la procedencia de sus tres decisiones
independientes:

| decisión | estado hoy | procedencia |
|---|---|---|
| planta y topología | medida | red de medinas sobre la figura 128, decisión 0004 |
| nivel de cada tesela | **aproximado** | distancia de grafo, decisión 0007 |
| altura del salto | **parámetro** | 8P, pauta moderna de Saseta y Ferrer |

Ninguna salida se presenta como reconstrucción verificada. La fórmula admitida
es «reconstrucción aproximada, con niveles inferidos por topología»; la
prohibida sigue siendo cualquiera que sugiera lectura directa del monumento.

## Qué mejora la aproximación, por orden de coste

1. Pedir a Ferrer **la malla de su modelo del cuarto de maqueta de Contreras**,
   el que aparece en la grabación `Ferrer_6`. Es obra suya y la conserva. Sus
   vistas oblicuas permiten leer el sentido de ascenso pieza a pieza y
   sustituir la inferencia por distancia de grafo de la decisión 0007 por
   orientaciones observadas, con la etiqueta «observado sobre la maqueta de
   Contreras». Detrás, la maqueta física: empezar por los inventarios 006601 y
   006091 del Museo.
2. Contrastar el perfil de las maquetas seccionadas (`Ferrer_1`, `Ferrer_2`)
   contra la sección medida, para rehacer `adaraja.py` con doble plantilla.
3. Fotografías oblicuas de la cúpula real, que sustituirían inferencias por
   observaciones vecindad a vecindad.

Cada una sustituye una parte inferida por una medida. La etiqueta baja de
«aproximado» a «medido» solo en la parte sustituida.
