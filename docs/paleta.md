# Paleta medida sobre la ortoimagen de AA-415_23

Extraída el 2026-08-24 de la ortoimagen cenital del techo del plano de Almagro
(entrada 3 de `fuentes.md`), recortando al octógono interior para evitar el
fondo y los bordes de la lámina.

**Esto son valores de color, no la imagen.** El plano es material de la RABASF
y no se redistribuye aquí. Una lista de valores hexadecimales medidos no es la
fotografía, y es lo único que el proyecto necesita.

## Yeso (base) — 50 % de los píxeles

Tonos casi acromáticos, todos en H≈40–50° (crema cálido), S≈0.07–0.09.

| hex | cobertura | V |
|---|---|---|
| `#C3BFB6` | 11 % | 0.76 |
| `#B6B2A9` | 15 % | 0.71 |
| `#AFAAA0` | 13 % | 0.69 |
| `#A6A49A` | 16 % | 0.65 |
| `#9A968D` | 25 % | 0.60 |
| `#79766E` | 20 % | 0.47 |

El rango de valor 0.47–0.76 es esencialmente el sombreado del propio relieve:
sirve como referencia de cuánto contraste produce la geometría de las adarajas
bajo la iluminación del levantamiento.

## Policromía (acentos) — 17 % de los píxeles

Filtrado por saturación ≥ 0.20 y valor ≥ 0.28, para excluir la suciedad y las
cavidades en sombra de los cupulines, que si no se comen la muestra.

| banda | % del pigmento | tonos |
|---|---|---|
| naranja / tierra | 58 % | `#5F4E3F` `#7F6C5C` `#9C8877` |
| ocre / amarillo | 25 % | `#554E3D` `#68604E` `#877C66` |
| verde / turquesa | 8 % | `#324D44` `#3D5B4D` `#4E6D5E` |
| rojo / granate | 8 % | `#554039` `#6D5850` `#8F776E` |
| azul | 0.3 % | `#1A354C` `#2E4250` `#485864` |

## Advertencia sobre «fidelidad» del color

Estos son los colores del **estado actual**: yeso envejecido, sucio, con la
policromía perdida en su mayor parte. No son los colores originales. El azul
aparece en el 0.3 % del pigmento y muy desaturado; en origen era un pigmento
deliberado y presumiblemente mucho más intenso.

Es la misma distinción del README aplicada al color: reproducir esta paleta es
una afirmación sobre **una fotografía de 2021**, no sobre la obra del siglo XIV.
Para un ejercicio de curiosidad da igual, pero conviene no llamarlo fidelidad
histórica.

## Método

Recorte al 20–80 % de la ortoimagen, remuestreo a 1400², conversión a HSV,
separación por saturación y por bandas de tono, y cuantización por corte de
mediana dentro de cada banda. Usa Pillow, así que **no entra en `granada/`**:
el paquete mantiene cero dependencias.
