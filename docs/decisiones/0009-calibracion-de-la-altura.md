# 0009 — La altura sale de la sección medida, no del recuento de niveles

**Estado:** aceptada — 2026-08-29

## Problema

El modelo tridimensional repartía la altura total entre los niveles
topológicos a pasos iguales: `altura = nivel × 4,67/7`. Eso trata el nivel del
grafo como si fuera una cota, y no lo es. Contrastado contra la sección medida
en `docs/estratificacion.md`, el desfase llegaba a **1,51 m sobre una cúpula de
4,67 m**, un 32 %:

| banda | nivel | altura del reparto uniforme | altura contra la sección | desfase |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0,000 m | 1,218 m | **−1,193 m** |
| 1 | 1 | 0,667 m | 2,233 m | **−1,509 m** |
| 2 | 3 | 2,001 m | 2,640 m | −0,651 m |
| 3 | 4 | 2,669 m | 3,452 m | −0,811 m |
| 4 | 6 | 4,003 m | 3,858 m | +0,217 m |
| 5 | 7 | 4,670 m | 4,670 m | 0,000 m |

Dos defectos concretos detrás de la tabla:

- **La banda exterior no arranca en cero.** Su radio mediano es 2,71 m, no los
  3,64 m del arranque: ya está a **seis hiladas** de altura. El reparto
  uniforme la clavaba en 0 y perdía 1,22 m de cúpula por abajo.
- **Los niveles 2 y 5 estaban vacíos.** El reparto era 16/32/0/40/8/0/8/1,
  artefacto de estirar las **5 capas reales del grafo** a 7 etiquetas con
  `round(capa × 7/5)`. Al extruir dejaba huecos que no corresponden a nada.

## Decisión

La cota deja de derivarse del número de niveles. Se separan dos papeles:

- **La topología agrupa.** Las capas mínimas del dual desde el borde reparten
  las 105 caras en **6 bandas**. Eso no cambia.
- **La sección medida sitúa.** Cada banda cae en una hilada entera de las 23
  medidas, por el radio mediano de sus caras y el paso horizontal medido
  (0,158 m). La altura es esa hilada por el paso vertical medido (0,203 m).

Las bandas caen en las hiladas **6, 11, 13, 17, 19 y 23**. Cada cara lleva
ahora `hilada`, `altura_m` e `iqr_hiladas_de_su_banda`, y cada vecindad su
`salto_hiladas`. El visor usa `altura_m`.

## Por qué esto no es la estratificación refutada

La decisión 0006 refutó «se sube uno hacia el centro» con ciclo testigo, y
`PROXIMOS-PASOS.md` manda tirar la estratificación por coronas polares. Esto no
es ninguna de las dos cosas:

- **No asigna saltos por radio vecindad a vecindad.** Asigna **cotas absolutas
  de banda**, y los saltos se derivan de ellas. Por construcción cierran todos
  los ciclos: no hay contradicción posible que refutar.
- **No sustituye el teselado por anillos.** La planta sigue siendo un teselado
  de 105 caras; el radio solo decide a qué altura está una banda **ya formada
  por la topología**, no qué cara va con cuál.

## Control: dos fuentes independientes coinciden en el orden

La banda sale del grafo dual. La hilada sale de la sección medida a través del
radio. **Coinciden en el orden**, estrictamente: 6 < 11 < 13 < 17 < 19 < 23,
con los radios medianos decrecientes. Si una banda más interior hubiera caído
más baja, el modelo estaría mal y habría que tirarlo.

La cima cierra exacta: la banda 5 cae en la hilada 23 y da **4,67 m**, la altura
medida, con desfase 0. No es sorprendente —el radio de la cara central es casi
cero—, pero confirma que la escala no se ha ido.

## Por banda y no por cara: refutado con números

La objeción evidente es que asignar la hilada **cara a cara**, por el radio de
cada centroide, daría más resolución. Se probó, y no vale:

- da **10 hiladas distintas** en vez de 6, mejora modesta;
- pero **invierte el orden topológico en 32 de 147 vecindades** entre bandas
  distintas (21,8 %): la cara más interior quedaría **más baja** que su vecina
  exterior, que es imposible en una cúpula por ménsulas;
- y produce saltos de hasta **6 hiladas** entre vecinas, contra las piezas de
  uno o dos niveles que documenta la tesis.

Es la estratificación por coronas otra vez, colada por la puerta de atrás: el
radio por sí solo no respeta el teselado. El control queda en el propio artefacto
(`inversiones_si_se_asignara_cara_a_cara`) para que la refutación se regenere
con los datos y no dependa de que alguien recuerde esta sección.

## Límites

- **El teselado no cubre las 23 hiladas: cubre 6 bandas.** Los huecos entre
  hiladas 6-11, 13-17 y 19-23 no tienen caras en la planta. Lo que se levante
  es una **aproximación de 6 bandas de una cúpula de 23 hiladas**, y cada banda
  representa entre 2 y 5 hiladas reales. No se puede afirmar 23 hiladas
  modeladas.
- **Dos bandas mezclan hiladas distintas.** La 0 y la 2 tienen recorrido
  intercuartílico de 2,0 y 2,8 hiladas; las otras cuatro quedan por debajo de
  0,25. Es decir: la banda 2, con 40 caras, casi seguro contiene piezas de dos
  hiladas que la distancia de grafo agrupa en una. Queda expuesto cara a cara
  en `iqr_hiladas_de_su_banda`, no promediado a escondidas.
- **Supone envolvente de revolución**, medida como cono de 38° ± 0,6° sobre la
  sección. Las celdas cuelgan por debajo de esa envolvente; la calibración
  sitúa la envolvente, no el fondo de cada celda.
- **La sección es un meridiano.** La cúpula real está deformada; esto ajusta
  dentro de una tolerancia, no reproduce.
- `nivel`, `nivel_8` y la sensibilidad 7/8 se conservan intactos: siguen
  sirviendo para colorear incertidumbre, pero ya no deciden cota.

Reproducción:

```bash
python3 scripts/inferir_niveles_aproximados.py
```
