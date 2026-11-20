# 0035 — Detalle de la visita interactiva desde la sala y junto al cupulín 00

20 de noviembre de 2026. El visitante puede elegir una pieza, acercarse y
rodearla. El defecto apreciado en la primera visita era el aspecto de
maqueta, sobre todo en la clave, las bocas y las hiladas repetidas.

## Qué se ha modelado

- La clave conserva los 266 vértices del borde del cierre central de la malla
  de trabajo. Se triangula su interior alrededor de ocho entrantes, una
  estrella con molduras y un botón dorado. El exportador comprueba la
  cobertura proyectada y limita la cota a 4,67 m sobre el arranque. El borde
  de la estrella cae en aristas de la malla.
- En el cupulín 00 se reutilizan el asiento y las adarajas recortadas de
  0032. Se interpretan la garganta y el techo con cuatro arcos y una estrella.
  En torno a su boca se identificaron a mano posibles frentes en la
  ortoimagen. Se toma como referencia el recorte local de Almagro,
  AA-415_23, p. 1, entre (3210, 1440) y (3830, 2060) píxeles de la imagen
  cenital extraída del PDF. El registro y la escala aproximada proceden de
  `datos/cupulines.json`. Se interviene donde hay apoyo en la malla y la
  boca queda despejada. Las hojas, sus nervios, la profundidad y el giro de
  las caras son propuestas para examinar en perspectiva.
- En los ocho paños del tambor se abren dos vanos por paño. Se parte de la
  cota del alféizar de la sección. El ancho, el perfil de las molduras y
  la celosía romboidal son hipótesis de presentación.
- Para cada punto de la malla se comprueba la visibilidad de dieciséis focos
  situados ante los vanos. Esa fracción modula la luz con un relleno mínimo
  de escena. La textura sintética de yeso aporta grano y rugosidad a escala
  métrica. La luz de reflejo, el acabado nuevo y los pigmentos son decisiones
  de presentación. La web distribuye geometría y una textura generada.
  Las fotografías de la obra quedan en el archivo local de referencia.

## Comprobación en el navegador

Las capturas se repiten con el mismo tamaño de ventana, la misma posición
inicial y los mismos gestos en las dos versiones. La comparación abarca la
vista desde la sala, el cupulín y un giro alrededor de él. Además, el
exportador proyecta 4.225 rayos desde la sala y otros tantos desde un lado.
Cuenta los primeros impactos en el cupulín antes y después de encajar las
caras vecinas. El detalle de esos dos controles está en la
[ficha de la exportación](../../web/modelos/dos-hermanas.json).

Las demás bocas conservan su interior simplificado y las hiladas fuera del
sector aún enseñan series de superficies curvadas y puntas. Faltan el
contraste de dos hiladas completas con sus apoyos, documentación de las
profundidades locales y prueba de rendimiento en un teléfono físico.

## Reproducción

Con el OBJ auditado y los dos NPZ de asiento y recorte de 0032 presentes en
`renders/previas/`, ejecutar desde la raíz del proyecto.

```bash
.venv/bin/python scripts/textura_yeso_visita.py
nice -n 15 taskset -c 0,1 ~/.local/opt/blender/blender -b -t 2 --python-exit-code 1 -P scripts/exportar_visita_web.py
python3 -m http.server 8765 --bind 127.0.0.1
```

Desde otra terminal, con Puppeteer Core y Chromium disponibles para Node
en `NODE_PATH` o en `node_modules`, reproducir la visita anterior conservada
en esta estación y la actual. En otros equipos, pasar la URL de la copia
archivada correspondiente como primer argumento.

```bash
node scripts/comprobar_visita_web.cjs http://127.0.0.1:8765/build/visita-o1G60P/index.html renders/previas/0035_original
node scripts/comprobar_visita_web.cjs
.venv/bin/python scripts/comparar_visita_web.py renders/previas/0035_original renders/previas renders/previas/0035_comparacion_web.png
bash scripts/publicar_web.sh --preparar
```
