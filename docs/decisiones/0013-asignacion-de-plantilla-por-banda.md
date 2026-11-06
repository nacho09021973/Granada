# 0013 — Qué plantilla usa cada banda

**Estado:** aceptada — 2026-08-29. Es el **paso 2** de
[`docs/hoja-de-ruta.md`](../hoja-de-ruta.md), y la primera decisión del
proyecto en la que **elegimos algo que ninguna fuente dice**.

## Decisión

Las **bandas 0, 1 y 2** —88 caras, hasta la hilada 13— usan el **perfil
menor**. Las **bandas 3, 4 y 5** —17 caras, hiladas 17 a 23— usan el **perfil
mayor**. La frontera de módulo cae **entre la banda 2 y la 3**.

`granada/asignacion.py` la construye, `scripts/exportar_malla.py --plantilla
por-banda` la aplica —y es lo que corre por defecto—, y
`datos/malla_cupula.json` la declara **cara a cara**, con su procedencia.

## De dónde viene el problema

La decisión 0010 dejó el callejón montado: la tesis documenta **dos** perfiles y
observa que las piezas vecinas mantienen los suyos **paralelos**; el grafo dual
de esta planta es **conexo**; luego exigir paralelismo en las 227 vecindades
obligaría a una sola plantilla y la segunda sobraría. Como la fuente documenta
dos, el paralelismo **tiene que romperse en alguna frontera de módulo**. Ninguna
fuente dice cuál, y por eso hasta hoy las 105 caras llevaban la mayor y el
control de paralelismo daba 0 vecindades rotas **de forma trivial**.

## Los criterios, en su orden

Están en `granada.asignacion.CRITERIOS`, se aplican en ese orden y el orden es
la parte que importa: **lo documentado va por delante de lo nuestro.**

1. **Se usan las dos plantillas.** La tesis documenta dos, y el residuo del
   18–23 % del mejor módulo único dice que esta cúpula no tiene uno solo.
2. **Los dos grupos de bandas son contiguos.** Un grupo de módulo es una región
   seguida de la cúpula, no bandas sueltas.
3. **Ningún grupo se queda con una sola cara.** La pieza de cierre va aparte
   desde la decisión 0010; aislarla no es una frontera de módulo.
4. **Se rompe el paralelismo en las menos vecindades posibles.** Es el único
   criterio que sale de una **observación de la fuente**.
5. **Entre empates, la frontera cae donde más cambia la subdivisión angular de
   la planta** —las caras por banda—, que es donde se vería un cambio de módulo.
6. **Entre empates, la junta queda lo más constante posible.** Es un argumento
   físico nuestro, no una fuente: va el último.

## El catálogo entero, para que la elegida se lea al lado de sus rivales

Junta en unidades P: una banda que abarca `h` hiladas tiene `8h` P de salto, el
frente ocupa `cima·h` y la junta es `h(8−cima)` —`h` P con la mayor, `h/2` con
la menor—. Los saltos de las seis bandas son **6, 5, 2, 4, 2 y 4 hiladas**.

| asignación | vecindades rotas | cambio de subdivisión | dispersión de junta | caras por grupo | descartada por |
|---|---:|---:|---:|---|---|
| uniforme mayor | 0 | — | 3 | 105 | criterio 1 |
| uniforme menor | 0 | — | 3 | 105 | criterio 1 |
| mayor \| menor @5 | 8 | ×8 | 3 | 104 + 1 | criterio 3 |
| menor \| mayor @5 | 8 | ×8 | 4 | 104 + 1 | criterio 3 |
| **menor \| mayor @3** | **16** | **×5** | **4** | **88 + 17** | **elegida** |
| mayor \| menor @3 | 16 | ×5 | 6 | 88 + 17 | criterio 6 |
| menor \| mayor @4 | 16 | ×1 | 4 | 96 + 9 | criterio 5 |
| mayor \| menor @4 | 16 | ×1 | 6 | 96 + 9 | criterio 5 |
| menor \| mayor @1 | 32 | ×2 | 5/2 | 16 + 89 | criterio 4 |
| mayor \| menor @1 | 32 | ×2 | 6 | 16 + 89 | criterio 4 |
| menor \| mayor @2 | 75 | ×1,25 | 2 | 48 + 57 | criterio 4 |
| mayor \| menor @2 | 75 | ×1,25 | 6 | 48 + 57 | criterio 4 |

Y un rival que ni siquiera entra en el catálogo porque no es contiguo: alternar
plantilla entre bandas anchas y estrechas —menor en 0, 1 y 3; mayor en 2 y 4—
deja las juntas casi iguales, con **dispersión 1,5**, la mejor de todas. Rompe
**115 de 211** vecindades. Se descarta por el criterio 2 y, aunque se admitiera,
por el 4. Queda escrito porque es la asignación que más «cuadra» y la que más
lejos está de lo que la fuente observa: es exactamente la clase de atajo bonito
contra el que existe la hoja de ruta.

**La elegida no es la que mejor iguala las juntas** —su dispersión es 4, peor
que la 3 de las uniformes—, y hay un test que lo deja fijado. El argumento de
la junta solo decidió **de qué lado** va cada plantilla, nunca dónde cae la
frontera.

## Por qué la frontera cae entre la banda 2 y la 3

Dos fronteras rompen 16 vecindades, el mínimo entre las no degeneradas: 2\|3 y
3\|4. Las separa el criterio 5. Las caras por banda son **16, 32, 40, 8, 8 y 1**:
al cruzar de la banda 2 a la 3 la subdivisión angular pasa de **40 caras a 8**
—×5, el mayor cambio de la cúpula—, mientras que entre la 3 y la 4 **no cambia
nada** (8 y 8). Una frontera de módulo donde la planta no cambia es peor
candidata que una donde cambia por cinco.

Es una medida del dibujo publicado, no una preferencia. Pero es **nuestra
lectura** de esa medida: que un cambio de módulo tenga que verse en el número de
caras por banda es una suposición razonable, no una fuente.

## El interruptor, y por qué el defecto es el reparto

La regla 3 de la hoja de ruta pide una bandera con **lo defendible por
defecto**. Aquí lo defendible no es lo uniforme:

- la plantilla **única** no es «no inventar»: es afirmar que esta cúpula tiene
  un módulo, y eso lo contradicen la tesis —que documenta dos perfiles y «un
  frente que pasa de 7P a 10P en el grupo siguiente»— y el residuo del 18–23 %
  del mejor módulo único;
- el reparto no contradice nada documentado: **añade** una elección de dónde.

Por eso `--plantilla por-banda` es el defecto y `--plantilla mayor` o `menor`
reproducen exactamente el modelo de la decisión 0010, a una palabra de
distancia. Es una lectura discutible de la regla 3 y queda dicha aquí para que
se pueda revertir con una línea.

## Controles

- **16 vecindades rotas, y las 16 cruzan la frontera.** Ninguna dentro de un
  grupo: si la hubiera, esto no sería una asignación por banda.
- **Una banda, una plantilla.** Ninguna banda mezcla; mezclar sería una
  asignación cara a cara, que es otra decisión y mucha más invención.
- **La junta y el frente suman las 8P por hilada**, en `Fraction`, sin
  redondeo. Juntas por banda: 3, 5/2, 1 | 4, 2, 4 P.
- **Ninguna junta se cierra ni se abre**: la mínima es 1P = 25,4 mm y la
  máxima 4P = 101,5 mm; la cota más baja de la malla baja de 0,152 m a
  **0,076 m** y sigue por encima del arranque.
- **La pieza de cierre no lleva junta**, y su fila la deja **vacía** en vez de
  inventarle un valor: la cupulilla apoya en la banda de abajo (decisión 0010) y
  de su plantilla solo usa la curva. Comprobado contra el OBJ pieza a pieza.
- **Mirado, no solo contado** (cautela 2): `scripts/render_malla.py` en las dos
  vistas. Sin púas nuevas, sin huecos, misma silueta con las piezas exteriores
  un 7 % más profundas.
- Suite en **636 tests**.

## Coste si es falsa

Bajo y acotado: cambiar una cara de mayor a menor mueve su profundidad en
**15/14, un 7,1 %** —la hoja de ruta lo tasaba en un 6 %—. Afecta a las 88 caras
de las bandas 0, 1 y 2. No mueve ninguna cota de banda, ninguna planta y ninguna
vecindad: la topología no se toca.

## Condición de muerte

Se cae, y se retira como se retiró el código de la decisión 0011, si:

- una fuente sitúa la frontera de módulo en otro sitio —2\|3 es la apuesta, y
  3\|4 empataba en el criterio que más pesa—;
- una fuente dice que el paralelismo se mantiene **también** entre las bandas 2
  y 3, porque entonces no hay frontera ahí;
- una fuente dice que las plantillas no se reparten por bandas sino por tipo de
  pieza, por sector o cara a cara;
- la malla de Ferrer permite **leer** los perfiles, en cuyo caso esto sobra
  entero.

Y por la regla de higiene de la hoja de ruta: **si Ferrer contesta, esta capa se
revisa entera**, no se conserva porque ya estaba.

## Lo que esta decisión no afirma

- No afirma que la cúpula tenga **dos** módulos. Afirma que tiene más de uno y
  que con dos plantillas documentadas lo mínimo que se puede montar es una
  frontera. Si hubiera tres módulos, esto es una simplificación.
- No afirma que las bandas sean grupos de módulo. Afirma que la banda es la
  unidad más fina que esta planta permite distinguir sin subdividir caras, que
  es el paso 3 y no se ha dado.
- No afirma nada **observado** sobre la cúpula. Nada de esto se ha visto: se ha
  elegido.

Reproducción:

```bash
python3 scripts/exportar_malla.py                    # por-banda, el defecto
python3 scripts/exportar_malla.py --plantilla mayor  # el modelo de la 0010
python3 scripts/render_malla.py
```
