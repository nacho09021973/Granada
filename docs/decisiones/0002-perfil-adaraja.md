# 0002 — El perfil de la adaraja como cónica racional

Fecha: 2026-08-24
Estado: **obsoleta** desde 2026-08-24; se conserva como registro

La lectura posterior de la tesis de Ferrer Pérez-Blanco documentó una
plantilla de doble perfil (7P / 7,5P, nivel siguiente a 8P) y el paralelismo
entre perfiles vecinos. La cónica única de esta decisión no debe alimentar un
nuevo render histórico. El reemplazo aún no está decidido ni implementado.

## Contexto

La estratificación (`docs/estratificacion.md`) da el esqueleto escalonado: 23
hiladas, cada una avanzando una unidad de planta hacia el eje y subiendo 1.279.
Eso es un cono de escalones. Lo que lo convierte en mocárabes es el **perfil
vertical de cada celda**.

Había dos caminos:

**(a) Extraer un perfil medio de la silueta del plano.** Fiel a la medición,
pero pobre: la silueta solo muestra el contorno, cada tipo de adaraja tiene el
suyo, y no queda ningún mando que tocar.

**(b) Modelar el perfil como un arco parametrizable y ajustarlo a ojo.** Menos
atado a la medición, pero es lo que pide un ejercicio en el que la gracia está
en jugar con formas.

Se eligió **(b)**, en coherencia con el alcance fijado: esto es una pieza de
curiosidad, no una reconstrucción, y la afirmación (B) del README queda fuera
por diseño.

## Decisión: cónica racional cuadrática

El perfil vive en el plano meridiano (radio, altura), normalizado al cuadrado
unidad de la celda:

    P0 = (1, 0)          exterior abajo: el labio
    P1 = (tiro, tiro)    control, sobre la diagonal
    P2 = (0, 1)          interior arriba: engancha con la hilada de encima

Bézier cuadrática racional de pesos 1, `peso`, 1.

**Por qué esta familia y no una spline o un arco de circunferencia:**

1. **Es exacta en racionales.** Con puntos de control y peso en `Fraction`,
   evaluar en un `t` racional da coordenadas racionales. Ninguna llamada a
   `cos`, ningún float. El proyecto entero sigue sin redondeo: la planta en
   Z[ζ_m], la vertical y el perfil en Q.
2. **Reproduce lo que se ve en la sección.** Con tiro = 0 las tangentes salen
   perpendiculares: vertical en P2, horizontal en P0. Es exactamente la adaraja
   del plano — cara casi vertical arriba, labio redondeado volando hacia fuera
   abajo.
3. **Dos mandos bastan**, y uno de ellos tiene un punto notable comprobable:
   - `tiro` ∈ [0,1] es la profundidad. 0 = cuenco hondo; **1/2 = el control cae
     sobre la cuerda y la curva degenera exactamente en el segmento recto**, o
     sea el cono liso sin mocárabes; 1 = abombado hacia fuera.
   - `peso` es la forma de la cónica: 1 parábola, menos elipse, más hipérbola.

   Que tiro = 1/2 dé la recta *exacta* (radio + altura = 1 en toda la curva, con
   igualdad de racionales) es una comprobación fuerte de que la
   parametrización está bien puesta. Tiene test.

## El arco circular exacto no es racional

El cuarto de circunferencia pide peso = √2/2 = 0.70710678…, irracional.
`PESO_CIRCULO` usa **70/99**, el convergente clásico de √2, con error relativo
5.1e-5. A efectos de dibujo es una circunferencia; en rigor es una elipse, y
así está documentado y testeado (hay un test que comprueba que se aproxima *y*
que no es igual).

Queda apuntado, sin implementar, algo que puede aprovecharse:

> √2 **sí** vive en el subanillo real de Z[ζ₁₆] y de Z[ζ₂₄] — es λ²−2 y λ³−3λ
> respectivamente. Para esos dos órdenes el arco circular exacto sería
> representable sin salir del cuerpo del propio anillo. Para m=20 no: allí no
> hay √2, hay √5.

Es decir, la elección del orden de simetría condiciona qué perfiles son
exactamente representables. Bonito, pero no hace falta ahora.

## Lo que este modelo no pretende

- **No** afirma que los alarifes trazaran cónicas. Es una familia de curvas
  elegida porque cubre lo que se ve y es exacta en racionales.
- **No** distingue tipos de adaraja. Todas las celdas comparten perfil. Los
  mocárabes reales tienen varios tipos por hilada; eso queda fuera.
- **No** modela la decoración de la celda, ni la epigrafía, ni la policromía.

## Comprobación visual

Se dibujó la sección meridiana completa con el perfil por defecto y sale la
silueta escalonada y festoneada característica, comparable con el borde de la
sección del plano. Barriendo `tiro` de 0 a 4/5 se pasa del cuenco hondo a la
recta y de ahí al abombado, con la recta apareciendo en 1/2 como estaba
previsto.

## Implementación

`granada/adaraja.py`. La malla de una celda son (n_perfil+1) × (n_ancho+1)
vértices exactos. La sección transversal es la **cuerda** entre los dos bordes
angulares de la celda, no el arco: la celda es un polígono en planta, así que
la cuerda es lo correcto y además mantiene todo racional.

Un vértice es un `PuntoMalla`: planta en Q(ζ_m) — coeficientes racionales en la
misma base que Z[ζ_m], porque interpolar dentro de una celda sale del anillo
entero pero no del cuerpo — y altura en Q.
