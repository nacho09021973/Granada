# 0003 — El nivel pertenece a la instancia y a su topología

Fecha: 2026-08-24
Estado: aceptada para la representación; asignación de la planta real pendiente

## Contexto

La siguiente tarea era convertir la planta registrada de la cúpula de las Dos
Hermanas en una planta con niveles. Antes de programarla se leyeron directamente
las secciones **3.2.5, “Plantas con líneas de nivel”** (pp. 254–256 impresas),
y **3.3.2, “Planta propuesta”** (pp. 269–272) de la tesis de Ignacio Ferrer
Pérez-Blanco.

La primera sección presenta las curvas de nivel como dibujos analíticos. En
Prieto y Vives los descansos ramifican las curvas y forman bucles; en Notkin
una misma planta admite variantes con niveles diferentes y las cotas se anotan
en las líneas y estrellas. Una planta geométricamente idéntica no determina por
sí sola un único alzado.

La segunda propone, a escala media, una o varias flechas dentro de cada figura.
Las flechas codifican **sentido, tipología y niveles de ascenso**. Esto evita
atribuir un único sentido a una arista compartida: hay casos en los que cada
lado necesita su propia indicación.

La figura 128, que contiene la propuesta específica para Dos Hermanas y que ya
estaba registrada sobre la ortoimagen, **no contiene esa codificación de
flechas ni cotas**. Da la red de medinas, no el nivel absoluto de cada tesela.

## Decisión

1. Se representa por separado el `TipoMocarabe` (figura + topología) y la
   `AsignacionNivel` de una instancia concreta.
2. A3 y D3 salvan dos niveles. A1, A2, B4, C1 y C2 salvan uno. Esta propiedad
   no fija el nivel absoluto de la instancia.
3. Las diferencias absolutas se expresan como restricciones dirigidas entre
   nodos: `nivel(destino) = nivel(origen) + salto`. Se admiten ascensos,
   descansos y descensos.
4. Un ciclo incompatible es un error. Un componente sin ancla queda
   explícitamente sin resolver: no se normaliza a cero ni se une por cercanía.

## Adenda — clasificación de ascendencia (2026-08-28)

La primera imagen del ejercicio docente de Ferrer de 2023 publica la gramática
genérica de las siete piezas: A1/C1 divergentes, A2/C2 convergentes, A3/C3
mixtas y B neutra. La nomenclatura de esa lámina es la de Jones y Goury; en la
taxonomía usada por la tesis y este repositorio, C3 corresponde a la jaira D3 y
B a B4.

Se incorpora `TopologiaAscenso` a `granada/niveles.py` y se deriva del número
topológico: 1 divergente, 2 convergente, 3 mixta y 4 neutra. Esto permite
validar una pieza una vez identificados su tipo y orientación. **No asigna el
tipo a ninguna cara de Dos Hermanas, no orienta instancias y no firma ninguna
vecindad.** El bloqueo documental continúa.

Fuente: cuarta y primera imágenes del ejercicio “2023. Muqarnas' compositions
created by students”, <https://ignaciofpb.es/muqarnas>, consultadas a resolución
original el 2026-08-28.

Implementación: `granada/niveles.py`; pruebas: `tests/test_niveles.py`.

## Contraste fotométrico barato

Se comprobó si la luminancia contiene al menos señal de profundidad usando un
extremo conocido: los 16 cupulines exteriores, cavidades hondas que el registro
sitúa dentro de sus celdas octogonales. En la ortoimagen de AA-415_23 se comparó
la mediana de luminancia de cada cupulín con un parche intermedio al mismo
radio:

- 15 de 16 cupulines son más oscuros;
- diferencia mediana control − cupulín: **+16,99** en escala 0–255;
- Wilcoxon pareado unilateral: **p = 3,05·10⁻⁵**;
- al barrer la fase, el máximo queda a **1,24°** del eje documentado; la fase
  documentada está en el percentil **90,6** del barrido.

La sensibilidad radial impide convertirlo en calibración: a 1350 px el efecto
cae a +7,36 y 12/16 pares para parches de 90 px. Además quedan como confundidores
la orientación de caras, el pigmento, la suciedad y la iluminación. El resultado
sostiene que la sombra es un **indicio**; no sostiene una función
`luminancia -> nivel entero`.

Script reproducible: `scripts/analizar_sombra_niveles.py`. Resultado completo,
incluidos controles: `datos/contraste_sombra_niveles.json`.

## Alternativas rechazadas

- Asignar niveles por coronas radiales: contradice el teselado documentado.
- Ordenar todas las teselas solo por brillo: no hay calibración ni control de
  orientación/material.
- Dar nivel cero a componentes desconectados: ocultaría que falta topología.

## Consecuencia operativa

La asignación de niveles de Dos Hermanas queda
`BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS`. La red ya se completó en la decisión
0004 y ofrece 24 anclas candidatas de borde. Falta identificar sus caras y
codificar restricciones comprobables de ascenso, descanso o descenso; si no,
hace falta una planta de esta cúpula que incluya flechas o cotas de nivel.
