# 0036 — Dos hiladas sobre las ventanas del sector 00

20 de noviembre de 2026. El botón **Hiladas** de la visita conduce al paño
del tambor que da al cupulín 00. Abarca las dos ventanas y llega hasta las
bisectrices del octógono. Se ha sustituido una franja de la cornisa plana
por 16 piezas en la hilada inferior y 17 en la superior.

## Referencia y encaje

En la lámina de Antonio Almagro, AA-415_23, p. 1, la sección muestra un
arco alto sobre cada ventana, apoyos intermedios, hileras de piezas a
distintas alturas y celosías con motivos radiales. En la ortoimagen, las dos
franjas junto al borde del paño se ven por el lado exterior del cupulín. La
lectura de la sección se concentra en las columnas 1800–3310 y las filas
1950–2200 del JPEG original. El tramo de planta se ve en las columnas
3740–3910 y las filas 1450–2040 de la ortoimagen. Las dos imágenes locales
coinciden byte a byte con las imágenes extraídas de la página 1 del PDF.
[Fuente local](../AA-415_23.pdf).

Los límites y las cúspides que se tomaron como referencia están en píxeles
en el generador. El número y la separación de las piezas son elecciones de
modelado. Transferir al paño +X el alzado que se ve en la sección es una
hipótesis. Haría falta registrar una fotografía oblicua del mismo paño para
confirmar la correspondencia y ajustar la profundidad.
[Generador de las hiladas](../../scripts/hiladas_ventanas.py).

El modelo conserva los alféizares a −1,346 m respecto al arranque y el
ápice de referencia del vano a −0,165 m. Con el origen de la sección en
la fila 2140, el ápice leído en la fila 2050 estaría a +0,190 m. Para encajar
las piezas se ha bajado el perfil **0,355 m**. La separación entre los
dos órdenes se adapta donde pasa el arco mayor. Los vuelos de 0,134 y
0,251 m, el perfil de los gallones, la talla de las hojas, el dibujo de
ocho pétalos y el acabado del yeso son propuestas para la visita.
[Cotas del alzado](../../datos/alzado_sala.json).

## Comprobación del encuentro

La primera prueba conservaba la moldura semicircular de 0035. Al girar
se veía una parte de esa moldura atravesar el intradós. La versión
incorporada construye el vano y el borde inferior de las adarajas a partir
de las mismas coordenadas. Los 31 encuentros laterales tienen al menos
17 vértices compartidos cada uno. La comprobación lee de nuevo el GLB
que carga el navegador. Cuenta 1370 posiciones coincidentes en el borde
entre los órdenes y otras 1370 en el borde con la pared y los vanos, con
redondeo al micrómetro. [Ficha de exportación](../../web/modelos/dos-hermanas.json).

Desde la sala y desde los dos puntos próximos, los rayos dirigidos al paño
alcanzan las 33 piezas. Se apuntaron además 759 rayos al interior de cada
ventana antes y después de colocar las hiladas, con las nuevas celosías en
ambos casos. Desde la sala alcanzan el fondo luminoso 51 y 45 rayos en
ambas versiones. En la vista lateral el segundo vano pasa de 112 a 111.
Los controles del pozo conservan 883 impactos desde la sala y 928 desde
el lado, sobre 4225 rayos por vista. La comprobación de las celosías
contrasta por separado el área triangulada con el área del vano menos la
de cada calado, con una tolerancia de un milímetro cuadrado.

La comparación visual usa el GLB archivado de 0035 y el actual con los
mismos controles, cámara, iluminación y resolución. Los recortes muestran
el encuadre frontal, el giro y el acercamiento. La copia de 0035 se
identifica por el SHA-256 del GLB descomprimido
`f27e490d2584d427ad7d03f5396ba1c74677ada7be9b9c75b7d32e1781f2f124`.
[Lámina local](../../renders/previas/0036_comparacion_web.png).

En el giro se distinguen el espesor de la celosía y los apoyos bajo los
arcos. En la sección, la talla ocupa también los macizos entre vanos y las
transiciones entre piezas tienen mayor variedad. En la visita esos macizos
siguen siendo lisos y, en el borde superior del paño, se alcanzan a ver
rendijas oscuras de la malla de campo.

## Reproducción

Con el OBJ auditado, los dos NPZ de 0032 y la textura de yeso de 0035,
ejecutar en la raíz del proyecto.

```bash
OPENBLAS_NUM_THREADS=1 nice -n 15 taskset -c 0,1 ~/.local/opt/blender/blender -b -t 2 --python-exit-code 1 -P scripts/exportar_visita_web.py
python3 -m http.server 8765 --bind 127.0.0.1
```

Con el servidor en marcha, ejecutar desde otra terminal con las dependencias
de Chromium y Puppeteer indicadas en 0035. En esta estación la malla
anterior se conserva en el directorio de preparación del sitio.

```bash
url=http://localhost:8765/web/visita.html
previa=http://localhost:8765/build/visita-8e0Quh/modelos/dos-hermanas.glb.gz
node scripts/comprobar_visita_web.cjs "$url" renders/previas/0036_antes "$previa"
node scripts/comprobar_visita_web.cjs "${url}#hiladas" renders/previas/0036
.venv/bin/python scripts/comparar_visita_web.py --hiladas renders/previas/0036_antes renders/previas/0036 renders/previas/0036_comparacion_web.png
```

El GLB comprimido ocupa 16,72 MB. Queda pendiente medir la carga y la
fluidez en un teléfono físico. El desfase con la sección queda abierto
antes de extender las hiladas a otros paños.
