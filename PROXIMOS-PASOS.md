# Próximos pasos

Estado a 2026-11-21. Documento de trabajo: se actualiza, no se conserva como
histórico. El registro de decisiones va en `docs/decisiones/`.

---

## Reanudación en el PC NVIDIA — 21 de noviembre de 2026

**Corrección de salientes, 0040.** El usuario identifica `Foto de Ferrer.png`
como control del alzado. Registrada contra la sección por dos recortes.
Rebajados 64 casquetes y los techos de 16 pozos, con clave y bordes
conservados. El GLB corregido está en la visita y la comparación a escala
común en `web/alzado-cupulines.html`. Pasan 791 tests, cobertura a dos
resoluciones, controles de ventanas/cupulín y navegación. Alcance y
reproducción en [0040](docs/decisiones/0040-salientes-y-alzado-de-ferrer.md).
El ajuste es propuesto: el alzado aún no coincide pieza por pieza y los
asientos antiguos de quince pozos siguen limitando su rebaja. La iluminación
por vértice conserva la del control anterior. Para regenerar la visita hay
que aplicar la corrección 0040 al GLB de control que genera el exportador.

**Revisión visual posterior, 0039.** Preparado un encuadre en Cycles con la
misma cámara del paño y comparación deslizante en `web/estudio-yeseria.html`.
Fuentes, parámetros y alcance en [0039](docs/decisiones/0039-estudio-de-luz-y-yeso.md).
No se considera logrado el hiperrealismo ni se aplica el ensayo al conjunto.
La prueba de talla adicional se descarta por demasiado esquemática. El GLB
y el acabado de la visita principal se conservan para contrastar el ensayo.

Rama vigente: `cierres-y-cupulines`. RTX 5060 reconocida por Blender con
`LD_LIBRARY_PATH=/usr/lib/wsl/lib` y `--dispositivo cuda`. Completadas las
tres vistas del OBJ auditado a 1400 px, 48 muestras, en
`renders/previas/2026-11-21_gpu/`. No son renders del GLB detallado.
Pasan 784 tests y la comprobación automatizada de la visita web.

Desfase del paño reproducido por dos vías y corregido en el piloto: las 33
crestas usan el origen de la sección. Se ajusta el fondo al borde interior
de la cornisa y se recortan los encuentros que lo atravesaban. El control
del GLB pasa de 150 a 0 pares de triángulos con cruce transversal entre el
paño y las superficies vecinas examinadas. Las 33 piezas se alcanzan desde
tres vistas y el cupulín conserva sus controles. Visita local actualizada.
Diagnóstico en [0037](docs/decisiones/0037-reanudacion-en-nvidia-y-desfase-del-pano.md)
y corrección, procedencia y límites en [0038](docs/decisiones/0038-encaje-del-pano-con-la-seccion.md).

**Pendiente de contraste histórico:** la profundidad de 32,05 cm es un
encaje propuesto, no una medida; registrar una vista oblicua del mismo tramo
y distinguir cúspide exterior de abertura luminosa antes de repetir el paño.
El usuario ha separado la mejora del aspecto de videojuego: se revisará
después de este trabajo de encaje local. No extender todavía las hiladas a
los otros paños.

---

## Traslado al otro PC — 20 de noviembre de 2026

La rama de trabajo es `cierres-y-cupulines`. Para descargarla por primera vez:

```bash
git clone --branch cierres-y-cupulines https://github.com/nacho09021973/Granada.git
cd Granada
python3 -m http.server 8765 --bind 127.0.0.1
```

Abrir `http://localhost:8765/web/visita.html#hiladas`. El modelo comprimido,
la textura y las librerías del navegador están incluidos. Para una copia
ya existente, cambiar a esa rama y ejecutar `git pull --ff-only` después
de comprobar que el trabajo local está guardado.

Para trabajar en geometría, instalar Python y Blender 4.5 LTS y preparar:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

En Windows, usar el Python de `.venv/Scripts/`. El exportador se ejecuta
desde la raíz con `blender -b -t 2 --python-exit-code 1 -P scripts/exportar_visita_web.py`.
Se incluyen el OBJ auditado, su MTL y los dos NPZ que necesita. Las fuentes
documentales excluidas por derechos deben recuperarse del archivo privado
de referencia antes de contrastar nuevas medidas.

Orden para esta tarde:

1. Abrir la visita y comprobar sala, cupulín, hiladas, zoom y giro.
2. Revisar la comparación 0036 y resolver el desfase vertical de 35,5 cm
   con la sección antes de extender el paño.
3. Registrar una vista oblicua del mismo tramo y ajustar fondos y apoyos.
4. Completar los macizos tallados entre ventanas y corregir las rendijas
   del borde superior que se ven al girar.
5. Repetir la comparación desde la sala y dos vistas cercanas. Extender
   a otros paños cuando los encuentros estén contrastados.
6. Medir carga y fluidez en un móvil físico y decidir la carga por zonas.

El resultado sigue siendo una reconstrucción aproximada con profundidades,
motivos y policromía propuestos. La decisión 0036 documenta su alcance.

---

## Entrega final acordada el 20 de noviembre — visita web en 3D

El objetivo es recorrer con zoom una reconstrucción de Dos Hermanas como en la
inauguración y apreciar las piezas desde distintos ángulos. Las fotografías y
las láminas de Cycles sirven para comparar el modelo con las fuentes.

La [visita](web/visita.html) permite partir desde la sala, escoger un punto
visible y rodearlo con el ratón o con gestos táctiles. La versión 0035
incorpora un remate central, el asiento recortado del cupulín 00, diez frentes
en su entorno y vanos con celosías en el tambor. La luz se atenúa según qué
ventanas son visibles desde cada vértice. La malla de campo de 0032 sigue
siendo la referencia de las hiladas. [Prueba y alcance](docs/decisiones/0035-detalle-de-la-visita.md).

**Piloto del sector 00, 0036.** La visita incorpora dos hiladas contiguas
de 16 y 17 piezas sobre las dos ventanas del paño. El botón **Hiladas**
acerca el visitante a la junta con el vano. La comprobación de los cantos
del archivo web y el contraste en tres perspectivas figuran en la
[decisión 0036](docs/decisiones/0036-hiladas-sobre-las-ventanas.md).

**Antes de repetir el paño.** Resolver la diferencia vertical de 35,5 cm
entre el ápice de referencia en la sección y la ventana del modelo. Contrastar
la profundidad de las dos hiladas con una vista oblicua registrada del mismo
tramo. El resultado actual queda como piloto local.

La versión actual carga toda la malla de una vez. Al incorporar el relieve
y los motivos de superficie, medir la carga y la fluidez en un móvil físico
y cargar por zona el detalle que necesite la cámara.

## Para el 2026-11-19 (anotado a petición del usuario)

Defecto actual (decisiones 0029 y 0030, rama `cierres-y-cupulines`, commit
`d252cd6`): paleta «ferrer» en penumbra, oscuro por celdas de la red
(`ferrer_red`, umbral 0,40) y cupulines con el eje a 30°.

1. **Las tres vistas a 1400 px** con ese defecto (cúpula, visitante, sala),
   como las `*_ferrer.png` de `renders/previas/`. En este equipo, solo CPU y
   4 hilos (no hay NVIDIA; `.wslconfig` se queda en 4 por decisión del
   usuario): unos 35-40 min [UNVERIFIED]. Lanzarlas cuando el usuario no esté
   usando el equipo. Malla: `render_hilada_campo.py --hiladas todas --color
   inauguracion --obj …`; render: `~/.local/opt/blender/blender -b -P
   scripts/render_cycles.py -- --obj … --vistas cupula,visitante,sala --lado
   1400`. Comparar con `scripts/comparar_con_ferrer.py`.
2. **Las rendijas entre piezas**, la tercera diferencia frente a Ferrer_5; se
   notan más sobre el fondo claro.
   Diagnóstico 0031: con el modelo vigente, 69 componentes en planta a paso
   0,06 y 42 a 0,03 catetos, con igual área mínima. El recuento no es estable;
   los 48 del modelo anterior no describen el actual. No se añaden parches.
   Siguiente: localizar juntas visibles en el render y contrastar los bordes
   de la malla en 3D; la cobertura en planta no mide esas juntas.

Revisión geométrica del OBJ a 1400 px: [decisión 0032](docs/decisiones/0032-revision-geometrica-del-obj.md). Prioridades: asiento y encuentros de un cupulín piloto, clave estrellada con altura contrastada y agrupación de las piezas de un sector.

Reanudación 2026-11-20: el ensayo articulado del cupulín queda local según
0032. Diagnóstico de la clave en [0033](docs/decisiones/0033-alcance-local-de-la-clave.md):
solo `cupulilla_25` excede la cota de calibración de 4,67 m; sin ella, el
máximo del resto es 4,670000034 m. Siguiente: ensayar el remate estrellado
local, conservando el encuentro y comprobando cobertura, altura y lectura
desde el visitante. **Ensayo ejecutado, 0034:** altura 4,67 m y cobertura
muestreada conservadas; no se promueve porque la estrella queda escalonada
y el encuentro sigue circular. Se añade `--acabado obra-nueva` como opción
de comparación, sin cambiar el defecto. La siguiente malla de clave debe
alinear sus aristas con los quiebros; el sector de hiladas y el relieve del
tambor siguen pendientes. Véase [0034](docs/decisiones/0034-pilotos-de-clave-y-acabado.md).

Pendientes que quedan abiertos frente a Ferrer_5: el oscuro sale en trazos
finos, no en manchas compactas (probar a pintar enteras las piezas del
centro de cada celda).

---

## Hecho el 2026-11-18 y siguiente

- Decisiones del usuario: el color sigue el criterio estético, declarando lo
  supuesto; el rojo se pinta como hipótesis de Jones; permiso para buscar en
  internet sin pedirlo cada vez. Enviar texto a terceros sigue pidiendo permiso.
- Cierres, clave, lazos que colapsan y cupulines: decisión 0027 (propuesta).
  Renders: `renders/previas/cupula_cycles_{visitante,cenital}_campo_cupulines.png`.
- Investigación: `reports/Cupulines y policromía de Dos Hermanas.md`, con las
  notas en `research_notes/`. El encargo a Gemini quedó preparado y no se envió
  (`investigaciones/2026-11-18-policromia-mocarabes/`).
- Cupulín estrellado (0027, añadido): pozo liso, techo plano y estrella de 8
  puntas, como en la ortoimagen. Faltan las trompillas y el arco mixtilíneo
  de Pavón. Desde la vista visitante las bocas siguen pareciendo alargadas.
- Color (0028): variante C, «Jones sobre yeso», elegida por Claude a petición
  del usuario («elige la opción más estética»). Render:
  `renders/previas/cupula_cycles_{visitante,cenital}_campo_inauguracion.png`.
  Corregida la frase de pigmentos de `docs/policromia.md`.
- **Siguiente, a elegir:**
  - rendijas (48 en planta);
  - trompillas de los cupulines;
  - la estrella de la red, que apenas se lee;
  - comprobar la reconstrucción de 1537–1547 [UNVERIFIED];
  - render 8k en el ordenador con GPU.
---

## Plan para el 2026-11-18 — cierres y color de la inauguración

**Punto de partida.** Rama `colocacion-suavizada` (3 commits, sin push ni merge).
Colocación suavizada σ=1 por defecto (0026). El usuario aprobó el render
Cycles `renders/previas/cupula_cycles_{visitante,cenital}_campo_suavizada.png`.
Esta máquina no tiene GPU: Cycles en CPU, ~9 min por vista a 1400 px y 48
muestras.

### Decisiones del usuario al empezar

1. **Merge** de `colocacion-suavizada` a `main`.
2. **Criterio de color.** El 2026-11-05 se pidió «reluciente como el día de
   la inauguración, colores apagados y artísticos, estética por delante»
   (`granada/color.py`). Hoy se pide «según los historiadores, que luzca igual
   que cuando se inauguró». ¿Manda la evidencia aunque el resultado sea más
   vivo o más pobre de lo que guste? ¿O se mantiene la estética por delante,
   declarando lo supuesto?
3. **El rojo.** Jones (lámina XXXIX) y la maqueta de Contreras lo traen. La
   ortoimagen no lo sostiene (`docs/policromia.md`). ¿Se pinta como hipótesis
   de Jones o se deja fuera?
4. **Permiso para buscar fuera.** ¿Encargo a `investigacion-gemini` sobre la
   policromía nazarí de mocárabes? Envía texto a terceros: solo con permiso.

### Bloque 1 — cierres (mañana temprano, acotado a medio día)

Paso 4 de la 0017, antes del color, porque las cupulillas también se pintan.

- Tapar con cupulilla los lazos de menos de `PIEZAS_MINIMAS`, los 16 huecos
  del anillo exterior y los 8 brazos de la estrella junto a la clave.
- Hacer la clave.
- **Criterio de cierre:** no queda ningún hueco negro en las vistas cenital y
  visitante de Cycles.
- No tocar la colocación.
- Las rendijas sueltas solo se miden: cuántas hay y en qué filas. Arreglarlas
  queda para otro día.

### Bloque 2 — color según las fuentes (lo principal)

**Paso 2.1 — Tabla de evidencia**, en `docs/policromia.md` o en una
decisión 0027. Una fila por fuente: qué dice, de qué parte de la sala, y si
es registro o restitución. Nada se usa sin comprobarlo en el original.

| Fuente | Qué aporta | Naturaleza | Estado |
|---|---|---|---|
| Patronato de la Alhambra | azul, rojo, negro, verde, oro, plata | texto general, no de esta cúpula | cita textual en `policromia.md`; falta la referencia exacta `[UNVERIFIED]` |
| Análisis por microscopía de luz polarizada | lapislázuli, bermellón, negro carbón; azul sintético del XIX | yeserías de la Alhambra, no esta cúpula | sin referencia en el repo `[UNVERIFIED]` |
| Ortoimagen AA-415_23 (`policromia.md`) | yeso 68 %, verde sostenido, azul débil, rojo no; oro y negro no medibles | medida del estado de 2021 | hecho |
| Jones, tomo II, lámina XXXIX | color celda a celda en mocárabes de la propia sala (cornisa de la Ventana), oro de fondo | restitución hacia 1845 | fichero en `docs/gri_33125008608388_jp2.zip`; sin medir |
| Jones, tomo I, lámina 38, «Estado actual de los colores» | cuánto se separa la restitución de lo que tenía delante | registro | sin localizar el fichero |
| Maqueta de Contreras (`Ferrer_5`, `Ferrer_6`) | rojo, dorado, nervios azul grisáceo | restitución del XIX | hipótesis fechada, no medida |
| Foto de Commons (entrada 19) | triángulos verdes y azules y cuadrados florales en las caras planas | estado actual, con dominante cálida | solo aspecto, no sirve para medir color |

**Paso 2.2 — Medir la lámina XXXIX.** Es la única fuente que reparte el
color por celda en esta sala. Medir la paleta y la proporción por tipo de
cara (fondo cóncavo, pared, tapa, caras planas) con un script permanente.
Salida en `datos/` con hash del fichero de origen.

**Paso 2.3 — Reglas de color** (decisión 0027): qué color lleva cada tipo de
cara y en qué posición (fila, familia A o C, cupulines, cupulillas, clave).
Cada regla lleva su fuente y su fuerza: *medido*, *restituido por Jones*,
*Contreras* o *supuesto*. Revisar los tonos de `granada/color.py` contra la
lámina; hoy salen de la ortoimagen limpiada.

**Paso 2.4 — Implementar.** `montar` ya devuelve la etiqueta de cada cara
(pared, tapa o fondo). Hay que conectarla a `colorear` en la exportación
`--obj` de `render_hilada_campo.py`. `render_cycles.py` ya lee los colores
del `.mtl` y trata el oro como metálico. Al hacerlo, revisar la sombra de los
cupulines (memoria del 2026-11-05: se quedaron claros a la espera del color).

**Paso 2.5 — Render Cycles** en CPU, vistas visitante y cenital (~18 min).
Comparar el aspecto con la foto de Commons y con la lámina XXXIX, sin
presentarlo como medida.

### Fuera de mañana

Las rendijas, la estrella de la red (punto 4) y la calibración de A y del
alzado (puntos 5 y 6). Los renders de 8k, en el otro ordenador.

---

## Hiladas continuas por campo de alturas (2026-11-08)

**Por qué.** El modelo por celdas (`granada/celdas.py`) no se parece a las
maquetas de Ferrer ni a la foto de Commons (entrada 19 de `docs/fuentes.md`):
rellena cada una de las 105 caras como una cupulita propia y ninguna hilada
cruza de una celda a otra. Los arreglos del 2026-11-08 (mesetas, caballetes y
rosetas en cuña, pata más estrecha) eran acabado, no estructura. El usuario
acepta suponer las cotas siguiendo un orden lógico: no habrá medición por
puntos.

**Hecho hoy** (decisión 0017, en estado *propuesta*):

- Pasos 1 y 2 — `granada/campo.py`: H = cono medido + signo·A·f(distancia a
  la red), suavizado a escala de pieza, cortado a las 22 cotas de hilada.
  Controles: con A = 0, anillos circulares; con A < PENDIENTE (1,28), ningún
  lazo; por encima, las hiladas altas cierran en lazos por celda.
  `scripts/curvas_de_nivel.py` barre A.
- Paso 3, en parte — `granada/hiladas_campo.py`: piezas a lo largo de cada
  curva, estiradas por el gradiente hasta la curva anterior. Con A = 2 salen
  por primera vez **filas continuas de arquillos** que dan la vuelta a la
  cúpula (`renders/previas/cupula_campo_A2.png`, no versionado; se regenera
  con `scripts/render_hilada_campo.py --A 2 --hiladas todas`).

**Pendiente, en este orden:**

1. **Tamaño decidido: B (2026-11-09, decisión 0018).** Dos filas por hilada,
   mitad de altura y fondo, **mismo ancho**, conservando la familia en cada
   par de filas. Corregida la interpretación errónea de Codex en `9cf2289`,
   que reducía también el ancho y producía 11304 piezas.
   Comparación corregida: **2730 → 5540 piezas** a A=2, sin cierres:
   2730 en cotas originales y 2810 en las nuevas. Dividir literalmente cada
   pieza daría 5460; la diferencia de 80 procede de recalcular contornos.
   Informe: `datos/comparacion_filas_campo.json`. Se conserva A con
   `--filas-por-hilada 1`; B es el defecto del script experimental, sin
   sustituir la malla del visor. **La elección no valida el recuento histórico.**
2. **Zona media e interior arrugada.** Allí las celdas de la red (8-15 cm de
   radio) son menores que el fondo de una hilada (16 cm); las piezas no pueden
   seguir ese detalle. No se arregla suavizando más. El render anterior
   `cupula_campo_B.png` usaba la interpretación errónea con ancho reducido.
   La comparación vigente es con `cupula_campo_B_corregida.png`.
   **Diagnóstico hecho (0019):** el cono A=0 no invierte; con A=2 sí hay
   inversiones locales de la banda. En el anillo de la fila 24, el fondo queda
   hasta ~16 cm del contorno anterior, confirmado al refinar el muestreo.
   Seguir el campo corrige una ventana local (33/33 y 65/65 trayectorias,
   sin inversiones), pero el ensayo repartido por todos los frentes deja
   7 trayectorias interiores sin llegada, además del problema de borde H=0.
   **Continuación 0020 (2026-11-17):** reproducidas las 30 paradas y la
   llegada no monótona. En la rejilla, seis paradas interiores permiten
   escapar sin superar H del nodo inicial; una requiere 0,000282055 catetos.
   Comprobado por caminos minimax y conectividad de subniveles. Esto no
   garantiza descenso monótono ni prueba una obstrucción continua. El borde
   termina hasta 21,1 cm fuera del radio base: H≈0 no fija el arranque.
   Informe: `datos/diagnostico_paradas_campo.json`.
   **Arranque ensayado, 0021 (2026-11-17):** candidato opcional
   `campo(borde="circular")`: dominio r≤RADIO_BASE y atenuación del relieve
   en un paso horizontal de hilada junto al borde. La primera fila B, A=2,
   conecta radialmente sin subidas H ni inversiones en 129 y 257 trayectorias
   con rejillas 0,03 y 0,015. El error de radio del contorno H=0 baja de
   0,063 a 0,016 mm. La fórmula impone el borde; eso no es evidencia histórica.
   El transporte radial del campo libre al círculo falla al refinar.
   Informe: `datos/diagnostico_arranque_campo.json`. El defecto sigue libre;
   no se aplica al visor ni resuelve encuentros con cupulines.
   **Transporte interior ensayado, 0022 (2026-11-17):** descenso con derivada
   bilineal compatible con H, retroceso y comprobación por tramos de celda.
   No resuelve ninguna de las siete paradas, ni con rejilla 0,03 ni 0,015;
   se rechaza como sustitución. En la rejilla fina el control con dirección
   interpolada llega en 1/7 o 2/7 según umbral: no hay obstrucción estable
   demostrada. Se conservan 48 recorridos y contrastes en
   `datos/ensayo_transporte_interior.json`; 769 tests pasan.
   **Direcciones en los extremos, 0023 (2026-11-17):** los 42 extremos
   fallidos tienen dirección descendente con paso aceptable; ninguno es
   mínimo local. Las 16 semillas (7 paradas + control, dos rejillas) tienen
   camino monótono certificado por aristas hasta la cota previa. **Falla el
   método; no hay encierro geométrico desde la semilla** en esta superficie
   discreta. Causa dominante: valle sobre arista de celda (25/42 extremos;
   en 35/42 la dirección del método sube). Informe:
   `datos/direcciones_extremos.json`; 771 tests pasan.
   **Colocación por flujo, 0024 (2026-11-17):** opción
   `colocacion="flujo"` (spline cúbico + RK4 por niveles de H). Inversiones
   de banda 27 390 → 2 556 y fondo en su cota (~1e-3 pasos), salvo en los
   cambios de topología (filas 15, 17, 18, 24). **El render apenas mejora.**
   El desorden visible coincide con frentes que giran 20–60° (mediana) dentro
   de una sola pieza en las filas 13–24 y 30–37: las piezas se doblan.
   **Piezas rígidas, 0025 (2026-11-17): rechazado.** Sin doblarse, las
   piezas quedan desorientadas: 721 de 5540 lados giran >45° respecto al
   siguiente, en las mismas filas. El problema es el frente, no la
   colocación.
   **Frentes suavizados, 0026 (2026-11-17, aceptada; es el defecto):**
   `colocacion="suavizada"`, σ=1,0 catetos (22 cm), gaussiana compensada.
   Cumple el criterio previo por poco (23,9° < 25°). Inversiones 48 947 →
   2 540; las filas se leen continuas
   (`renders/previas/cupula_campo_suavizada_s1.0.png`). Costes: desvío de
   hasta 8 cm de la curva real y 5538 → 5018 piezas. Quedan zonas ásperas
   junto a la estrella de la clave y en los lazos.
   Render Cycles (CPU, ~18 min): `renders/previas/cupula_cycles_{visitante,cenital}_campo_suavizada.png`,
   con `render_hilada_campo.py --obj` y `render_cycles.py --dispositivo cpu`.
   Se ven rendijas oscuras sueltas entre piezas (sin medir).
   **Siguiente:** cierres (paso 4) o rendijas, a elegir por el usuario.
   No se declara resuelto ni se han contado
   intersecciones 3D entre sólidos. Informes y SVG:
   `datos/diagnostico_colocacion_campo*.json`,
   `renders/diagnostico_colocacion_campo*.svg`.
3. **Paso 4, cierres.** Tapar con cupulilla de tamaño de pieza los lazos de
   menos de `PIEZAS_MINIMAS` = 6 piezas (hoy salen huecos negros) y la clave
   (solo hay 22 cotas). Conservar los 16 cupulines del anillo exterior.
4. **La estrella de la red apenas se lee** en el conjunto. Revisar `A`, la
   forma de `f` (lineal o raíz) y el signo en el paso 5 de la decisión 0017,
   contra ortoimagen y foto.
5. **Pasos 5 y 6 de la 0017**: calibrar `A` y validar el alzado (sección
   cortada frente a 24 ± 1 hiladas; vista oblicua comparable a `Ferrer_4`).

**Cautelas:**

- Iterar con renders de 1400 px en GPU (`--dispositivo cuda`, con
  `LD_LIBRARY_PATH=/usr/lib/wsl/lib`): las cuatro vistas tardan ~4 min. **El
  8k (~40 min) y el 16k (horas) solo al final**, con el modelo cerrado.
  `scripts/render_sala_alta.sh` los encadena.
- Los renders de 8k y 16k que hay ahora son del modelo por celdas; el 16k del
  2026-11-08 se paró sin terminar.
- `Ferrer_0` probablemente no es esta cúpula (leyenda de trompas sin asignar):
  vale para la gramática de hiladas, no como alzado de Dos Hermanas.
- El color no se toca (decidido el 2026-11-08): la foto de Commons tiene
  dominante cálida y no sirve para medir color.
- Las vistas previas para el usuario van en `renders/previas/` (ruta Windows
  `\\wsl.localhost\Ubuntu\home\adnac\Granada\renders\previas`).

---

## Cúpulas comparativas para una lectura histórica — 2026-08-30

**Paso 5 cerrado y primera composición completa del paso 6.** El visor separa
dos afirmaciones que no deben mezclarse: «Dos Hermanas» conserva la malla
histórica aproximada; «Comparar trazados» muestra tres cúpulas contemporáneas
de **8, 10 y 12 sectores**, con 40, 50 y 60 paños respectivamente.

Las tres usan la misma regla —cinco coronas y el mismo perfil escalonado— para
que la comparación aísle el ritmo angular. Esa composición no viene de una
fuente: es una elección expositiva registrada en la decisión 0014, con cotas
racionales y unidades relativas. No se atribuye a un taller, un monumento ni
una tipología histórica.

La interfaz habla primero al historiador: «familia de trazado», «corona»,
«sector», «paño», procedencia y límites. La notación ciclotómica queda en la
metodología, no en los controles. Hay vista general y lectura desde el intradós.
El acabado es sobrio y la ficha distingue lo documentado, lo calibrado, lo
propuesto y lo estrictamente comparativo.

Por debajo, `scripts/exportar_ordenes_sinteticos.py` conserva la auditoría:
planta exacta en Z[ζₘ], coeficientes enteros vértice a vértice, alturas
racionales y embedding numérico separado. Suite en **659 tests**; el artefacto
se regenera de forma idéntica.

La entrega estática acompaña al visor: `cupulas_comparativas_general.png` y
`cupulas_comparativas_intrados.png`, ambas a 3600 × 1600 px, más seis renders
individuales a 1200 × 1200. Las láminas llevan título, recuento de sectores,
coronas y paños, y la advertencia de alcance en el propio gráfico; no dependen
de que quien las reciba haya leído el repositorio.

---

## Yeso por defecto y color analítico separado — 2026-08-30

Hecha la base no especulativa de los pasos 4 y 5. El visor abre ahora en **yeso
blanco de obra nueva**, sin asignar pigmentos a ninguna pieza. La paleta que ya
existía se conserva como capa **analítica por niveles inferidos**, no como
policromía, y solo en esa capa aparecen los escenarios 7/8 y la incertidumbre.

El selector de tono es una ayuda de visualización y lo dice en la ficha: en
cuanto se aparta del blanco por defecto queda **sin atribución histórica**. No
se han incorporado el verde medido ni la lectura roja y dorada de Contreras,
porque repartirlos entre piezas sigue necesitando una decisión con procedencia.

El selector de orden se resuelve en la entrada superior como vista sintética
separada, sin deformar la malla de Dos Hermanas.

---

## Paso 2 dado: qué plantilla usa cada banda — 2026-08-29

**Decisión 0013.** Es la primera vez que el proyecto **elige** algo que ninguna
fuente dice, y por eso va con las cuatro garantías de la hoja de ruta puestas.

**Bandas 0, 1 y 2 —88 caras— con el perfil menor; bandas 3, 4 y 5 —17— con el
mayor.** La frontera de módulo cae entre la banda 2 y la 3.

La elección se hace con **seis criterios en orden**, y el orden es lo que
importa: lo documentado por delante de lo nuestro. Pesa primero romper el
paralelismo en las menos vecindades posibles —el paralelismo es lo único aquí
que sale de una observación de la tesis—, y eso deja **16 vecindades rotas de
211**, todas cruzando la frontera y ninguna dentro de un grupo. El empate entre
las dos fronteras que rompen 16 lo deshace la planta: entre la banda 2 y la 3 la
subdivisión angular pasa de **40 caras a 8**, el mayor cambio de la cúpula,
mientras que entre la 3 y la 4 no cambia nada.

**Y una corrección a la hoja de ruta.** Proponía alternar plantilla entre bandas
anchas y estrechas. Esa alternancia es la que mejor iguala las juntas —
dispersión 1,5 frente a 4— y a la vez la que **más** rompe el paralelismo: 115
vecindades de 211. Es exactamente la clase de atajo que cuadra bonito y se aleja
de la fuente, así que queda en el catálogo de la decisión como rival descartado,
no fuera de él. La constancia de la junta, que es argumento nuestro y no una
fuente, solo decidió de qué lado va cada plantilla.

Lo que hay que mirar con desconfianza, dicho aquí y en la decisión:

- **el defecto de `exportar_malla.py` es ahora el reparto**, no la plantilla
  única. Es una lectura discutible de la regla 3 de la hoja de ruta: se defiende
  porque la plantilla única tampoco es «no inventar» —afirma un módulo único que
  la tesis y el residuo del 18–23 % contradicen—, pero se revierte con
  `--plantilla mayor`, que reproduce exacto el modelo de la decisión 0010;
- **el umbral sigue sin cruzarse**: 105 piezas, las mismas caras de la planta
  publicada. Esto no añade ni una pieza, solo cambia la profundidad de 88 de
  ellas un 7,1 %.

Suite en 636 tests. Renders regenerados y mirados, que es la cautela 2.

---

## Órbitas C8 y las maquetas de Contreras — 2026-08-29

**Decidido propagar por rotación, no por espejo** (decisión 0012), y corregida de
paso una afirmación mía de la hoja de ruta que era demasiado estricta: dije que
extender por simetría sería circular, y confundía dos cosas. La entrada 7 **mide**
la simetría rotacional por Fourier sobre la ortoimagen, independiente de la red,
así que usarla no es circular. Lo que esa misma entrada dice literalmente es que
**«no se ha analizado la simetría especular»**. Ahí está el corte.

Lo que sale: la rotación de 45° es **biyectiva y de orden exactamente 8**, con
**14 órbitas de caras** —13 de tamaño 8 más el octógono central fijo— y **27
órbitas de vecindades propagables** que cubren 216 de las 227. **El dominio
fundamental es 14 caras y 27 vecindades**: el trabajo del paso 1 pasa de 227
lecturas a 27.

Control que lo sostiene: con giros que no son de simetría —22,5°, 30°, 60°— el
desajuste máximo se multiplica por 3 a 5 y las caras con margen holgado caen de
99 a 29–51. El fallo de 22,5° es significativo: es la retícula C16, y confirma la
separación que hace la entrada 7 entre andamiaje angular de orden 16 y simetría
exacta de orden 8.

Cinco vecindades (2,2 %) no cierran. Residuo del dibujo, no fallo estructural,
pero **por ahí no se propaga**: sus órbitas quedan marcadas y once vecindades sin
cubrir. **Propagar no multiplica el N**: observadas 27 son 27, no 216.

### El artículo sobre Contreras aprieta la etiqueta

Entrada 13: González Pérez (2017), *Art in Translation* 9:1. Cierra tres cosas y
aprieta una cuarta.

- **La maqueta de Dos Hermanas existe y está localizada.** Es la que le valió a
  Contreras el nombramiento de restaurador adornista: yeso, papel y madera,
  194 × 109 cm, **1847, Museo Arqueológico Nacional de Madrid**, seccionada
  —«vista exterior e interior»—. Candidato fuerte para la del vídeo, y vía
  concreta para los inventarios 006601 y 006091 que arrastrábamos sin verificar.
- **Escala habitual 1:12**, y los modelos podían ir con color o sin él.
- **No son copias exactas.** Verbatim: el taller «rellenaba los huecos para dar
  una visión más completa» y «la mayoría de los modelos no son copias exactas del
  monumento original». La entrada 12 lo decía como reproche sin verificar; queda
  verificado y **es más fuerte**.

Consecuencia: leer sentidos de ascenso sobre esa maqueta es leer **la compleción
de Contreras**. La etiqueta correcta no es «observado sobre una maqueta del siglo
XIX» sino «observado sobre una reconstrucción decimonónica que rellena lagunas
por diseño». Y corolario incómodo: si rellenaba hacia lo regular, su modelo será
más simétrico que la fábrica, así que confirmarle simetría no informa de nada.

---

## Si Ferrer no contesta — hoja de ruta

Escrita en [`docs/hoja-de-ruta.md`](docs/hoja-de-ruta.md). Fija cómo se toman las
decisiones que ninguna fuente decide, para que se tomen **a la vista** y no por
acumulación de atajos: decisión escrita, `procedencia` en el artefacto,
interruptor en el código con lo defendible por defecto, y condición de muerte.

Dos cosas de ahí que conviene no perder de vista:

- **El umbral.** Hoy son 105 piezas, todas de una planta publicada. Subdividir a
  hilada las llevaría a ~500, y cuatro de cada cinco no vendrían de ninguna
  fuente. Cruzarlo obliga a renombrar: de «reconstrucción aproximada de la cúpula
  de las Dos Hermanas» a «cúpula compuesta en el sistema de las Dos Hermanas».
- **Segundo aviso el 2026-09-19.** Hasta esa fecha no se toca el vídeo; después
  deja de ser un desperdicio y pasa a ser lo que hay.

---

## La pieza de cierre, resuelta — 2026-08-29

El **octógono central** ya no remata en una tapa plana de 1,28 m: es una
**cupulilla**. Su centroide está en el eje, así que la cota de banda lo llevaba
entero al ápice; su borde, en cambio, está a radio 0,65 m, que por la sección es
la hilada 18,9 ≈ 19 —la banda de debajo—, y del borde al ápice hay 0,812 m
frente a los **0,825 m que sube el cono medido** en ese radio. Un 1,6 %: la
cupulilla es el cono continuado hasta el eje, no una invención.

`granada.malla.corona` la levanta con el mismo perfil de la plantilla, y
`contiene_el_eje` la detecta por punto-en-polígono sobre el origen, así que la
regla sirve para cualquier planta. Se nota desde abajo, que es como se mira una
cúpula de mocárabes. Suite en **655 tests**.

---

## El visor muestra ya la malla — 2026-08-29

Mientras llega la respuesta de Ferrer —que vale como **perfeccionamiento**, no
como requisito— se cierran dos cosas que no dependían de él.

**El visor cargaba un modelo obsoleto.** Levantaba prismas planos por su cuenta
mientras el OBJ llevaba las celdas: dos geometrías distintas en el repositorio, la
pública peor que la exportada, y ninguna prueba que lo detectara. Ahora
`web/viewer.js` carga `renders/cupula_aproximada.obj` y no reconstruye nada, así
que página y malla no pueden divergir. La ficha de cada cara muestra su hilada y
su cota en metros; el escenario 7/8 colorea la sensibilidad y ya no decide altura.

**Refutada la asignación de hilada cara a cara.** Parecía la mejora obvia sobre
las 6 bandas. Da 10 hiladas distintas, pero **invierte el orden topológico en 32
de 147 vecindades** (21,8 %): la cara más interior quedaría más baja que la
exterior. Es la estratificación por coronas por la puerta de atrás. El control se
regenera con los datos, en `inversiones_si_se_asignara_cara_a_cara`.

Con eso, **el modelo de bandas de la decisión 0009 aguanta** el ataque más
natural que se le podía hacer.

---

## Doble perfil y malla — 2026-08-29

Hecha la segunda vía. **La cúpula ya sale como malla 3D exportable**
(decisión 0010): `renders/cupula_aproximada.obj`, 105 celdas, 6.225 vértices y
12.030 triángulos, cotas de 0,152 m a 4,670 m.

`granada/plantilla.py` codifica lo documentado y exacto en `Fraction`: perfil
**mayor** en quintos a 7P, **menor** en séptimos a 7,5P, nivel siguiente a 8P.
`granada/malla.py` da a cada cara un sólido cerrado —plataforma a la cota de su
banda y frente colgando— y `scripts/exportar_malla.py` escribe el OBJ y
`datos/malla_cupula.json`. Ajuste al cono medido: **rms 0,234 m** sobre 4,67 m,
un 5 %. Suite en **645 tests**.

El modelo de cónica única quedó obsoleto, pero su `PerfilArco` se reutiliza como
interpolador: es la primitiva de curva exacta, no un modelo de la pieza. El
módulo se retiró y renombró después, en la decisión 0011.

### El paralelismo fuerza plantilla única, y eso es un hallazgo

Perfiles paralelos son trasladados verticalmente, luego dos piezas vecinas han
de compartir plantilla. El grafo dual es **conexo**, así que exigir paralelismo
en las 227 vecindades **obliga a una sola plantilla en toda la cúpula** y la
segunda sobra. Como la tesis documenta dos, el paralelismo no puede valer en
todas a la vez: hay fronteras donde se rompe. Encaja con lo que la tesis
advierte de esta cúpula —frente de 7P a 10P, «mocárabes de distinto módulo»—
pero **ninguna fuente dice cuáles son esas fronteras**.

Por eso todas las caras usan el perfil mayor y el validador da 0 vecindades
rotas **de forma trivial**. Está escrito que es trivial para que nadie lo lea
como validación. La plantilla menor está implementada y probada, sin asignar.

### El render destapó dos fallos que los números no veían

Mirar la malla —cautela 2— encontró lo que el rango de cotas y el residuo
frente al cono daban por bueno:

- **huecos abiertos de hasta 0,390 m entre todas las bandas**, por colgar cada
  celda su propio vuelo radial en vez del salto hasta la banda de abajo. La
  corrección es más fiel a la plantilla: 7/8 del salto real, y el octavo
  restante como junta;
- **púas por triangular en abanico** desde el centroide, inválido para las 51
  caras no convexas. Sustituido por recorte de orejas.

El rasterizador queda como `scripts/render_malla.py` y sus salidas en
`renders/cupula_picada.png` y `renders/cupula_desde_abajo.png`. El control
visual tiene que ser reproducible.

### Lo que hay que decir al presentar la malla

- **Una celda por cara, y una cara no es una adaraja.** La cara mediana abarca
  **5,2 hiladas**: se reproduce el escalonado de las 6 bandas, no el de las 23.
- El residuo máximo (0,71 m) está en el borde exterior: la planta no llega al
  arranque de la cúpula.
- El **trasdós no es una afirmación.** El modelo describe el intradós, que es
  lo que se ve y lo único documentado. Desde arriba parece un escalonado de
  bandejas; eso es subproducto de la construcción por plataformas, no una forma
  exterior sostenida por ninguna fuente.

### Siguiente

Subdividir las 80 caras sin figura es lo único que baja de banda a hilada, y la
figura 128 no las subdivide. Es tarea de fuente, no de código. Mientras tanto,
la mejora barata es la que ya está pedida a Ferrer: la malla de su modelo del
cuarto de maqueta de Contreras.

---

## Altura calibrada — 2026-08-29

Hecha la primera de las dos vías acordadas para avanzar en el 3D. **La cota ya
no sale del recuento de niveles, sino de la sección medida** (decisión 0009).

El modelo anterior repartía 4,67 m entre 7 niveles uniformes y desfasaba hasta
**1,51 m**, un 32 %. Dos defectos concretos: la banda exterior se clavaba en
cota 0 cuando su radio mediano la sitúa ya a **seis hiladas** —se perdía 1,22 m
de cúpula por abajo—, y los niveles 2 y 5 salían vacíos por estirar las 5 capas
reales del grafo a 7 etiquetas.

Ahora la topología agrupa y la sección sitúa: las 6 bandas caen en las hiladas
**6, 11, 13, 17, 19 y 23**. Control: banda y radio medido, que son fuentes
independientes, **coinciden en el orden**, y la cima cierra exacta en 4,67 m.
No es la estratificación refutada: asigna cotas absolutas de banda, no saltos
por radio, así que los ciclos cierran por construcción.

`datos/niveles_aproximados.json` gana `hilada`, `altura_m` e
`iqr_hiladas_de_su_banda` por cara y `salto_hiladas` por vecindad; el visor usa
`altura_m`. Suite en **625 tests**.

**Lo que hay que decir al presentarlo**: el teselado no cubre 23 hiladas, cubre
**6 bandas**; cada banda vale entre 2 y 5 hiladas reales y no hay caras entre
las hiladas 6-11, 13-17 y 19-23. Además las bandas 0 y 2 mezclan hiladas
distintas (IQR 2,0 y 2,8 frente a menos de 0,25 en las otras cuatro): la banda
2, con 40 caras, casi seguro contiene piezas de dos hiladas.

**Siguiente**: la vía 2 — sustituir el perfil de cónica única por la plantilla de
doble perfil y sacar malla exportable. Es lo que convierte las bandas en mocárabes;
hoy siguen siendo prismas planos.

---

## Cambio de objetivo — 2026-08-29

**El objetivo ya no es la reconstrucción exacta de Dos Hermanas, sino la mejor
posible con los datos disponibles.** Queda escrito en la decisión 0008. No es
una rebaja del rigor: las fuentes no coinciden entre sí, no hay tabla pública
de cotas por pieza, y esperar a que aparezca tenía el modelo 3D parado. Lo que
cambia es el techo declarado del resultado; lo que no cambia es que cada parte
diga si está medida, inferida o parametrizada.

Consecuencia operativa inmediata: **`datos/niveles_aproximados.json` deja de
ser una vía paralela y pasa a ser la entrada normal del levantamiento**, con su
etiqueta intacta. `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` sigue vigente
sobre el dato histórico —los 227 saltos de `datos/caras_red.json` siguen sin
firmar— pero ya no bloquea el entregable.

Estado de reanudación: `APPROXIMATE_RECONSTRUCTION_TARGET`.

### Material de Ferrer, recibido el 2026-08-29

Registrado en la entrada 12 de `docs/fuentes.md` y trasladado de `renders/` a
`docs/`, que es donde vive la fuente: seis imágenes y una grabación de pantalla.
**Nada de ello muestra la cúpula construida.**

Leyendas suyas: `Ferrer_5` es «4 x Cuarto de maqueta de la cúpula de Dos
Hermanas de Rafael Contreras — s. XIX»; las demás imágenes son **trompas de
mocárabes de la Alhambra** («squinches head to head»), leyenda que cubre el
bloque y que **no se ha repartido fichero a fichero** — encaja en `Ferrer_1` y
`Ferrer_2`, peor en `Ferrer_0`, `Ferrer_3` y `Ferrer_4`.

Lo que aportan las maquetas impresas: el **apilado vertical de hiladas** y el
frente en arco de cada celda a escala legible, cómo mantienen las piezas
vecinas un sentido coherente, y una **sección construida** que contrasta contra
las 23 hiladas de `docs/estratificacion.md` sin pasar por el alzado de Almagro.
Lo que no aportan: ni flechas, ni cotas, ni escala, ni punto de vista declarado.

#### `Ferrer_6` (vídeo): la pieza que más rinde

No es un vídeo de la maqueta física, sino una **grabación de pantalla de un
visor 3D** con un modelo navegable —con toda la pinta de fotogrametría— del
cuarto de maqueta de Contreras. Audio en silencio digital, sin narración. **El
modelo 3D es obra del propio Ferrer**, confirmado por él el 2026-08-29 — no es
el escaneado de la cúpula de la entrada 11, al que ya no tiene acceso, sino un
levantamiento suyo de la maqueta, que sí conserva.

Da por primera vez **vistas oblicuas de un cuarto completo**, con el sentido de
ascenso legible pieza a pieza y sin la simetría impuesta del montaje. Es lo que
pedía la vía 1 de «dónde puede salir el signo», con una salvedad que no se
puede perder: lo observado es **la maqueta de Contreras, no la cúpula**. Sirve
para sustituir la inferencia por distancia de grafo de la decisión 0007 por
orientaciones observadas, bajo la etiqueta «observado sobre la maqueta de
Contreras» — nunca como restricción firmada de la entrada histórica.

`Ferrer_5` es **muy probablemente un cenital de este mismo modelo** montado
cuatro veces: misma paleta, mismo aspecto fundido de textura, mismo objeto. Sin
confirmar. Si lo es, el vídeo lo sustituye como fuente.

#### `Ferrer_5`: maqueta de Rafael Contreras, no fábrica

Las líneas oscuras en aspa que se veían son **las costuras del montaje**:
cuatro copias de un cuarto unidas por las diagonales. Tres límites, todos
vinculantes:

- **La simetría de orden 4 está impuesta, no observada** — la trampa exacta de
  la cautela 5. Esta imagen nunca sirve como evidencia de simetría.
- **Solo un cuarto es dato independiente.** Todo recuento sobre la imagen
  completa se divide entre cuatro antes de dar un N.
- **Es fuente terciaria**: media un intérprete del siglo XIX y la reducción a
  escala de maqueta.

**El rojo no se reabre**: el pigmento visible es policromía de Contreras, no
nazarí, y no toca lo que descarta `docs/policromia.md`. Queda como lectura
coloreada del siglo XIX, fechada y atribuida — hipótesis, nunca medida.

Comprobar si **los inventarios 006601 y 006091 del Museo**, que ya arrastramos
sin verificar más abajo, son maquetas de Contreras. Sería la vía al objeto en
lugar de a una grabación de un modelo de un cuarto de él.

**Qué pedirle**, por rendimiento: **la malla del modelo** (OBJ o PLY) del
cuarto de maqueta, con su método y las condiciones de uso — es suya, así que
falta el fichero y el permiso, no la información. Después: dónde se conserva la
maqueta de Contreras y si el cuarto es de origen o lo conservado; si `Ferrer_5`
sale de ese mismo modelo; qué trompa concreta es cada imagen; y qué
proporciones y escala usan sus maquetas impresas.

Mientras no llegue la malla, la grabación sirve para leer sentidos de ascenso a
ojo; con la malla se leerían con geometría. No adelantar trabajo fino sobre
480×856 comprimidos si el original está a una petición de distancia.

---

## Actualización — respuesta de Ferrer, 2026-08-28

La comunicación personal registrada en `docs/fuentes.md`, entrada 11, no
levanta `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` como afirmación histórica:
la captura permite contrastar el número global de niveles, pero no firma
ninguna de las 227 vecindades de la planta. La decisión 0007 sí habilita una
salida paralela `APPROXIMATE_LEVELS_AVAILABLE` para continuar el modelo 3D con
una hipótesis radial explícita y reemplazable.

Sí identifica la vía documental correcta. Ferrer indica que el sentido de
ascenso debe deducirse de fotografías y que las piezas vecinas han de mantener
un sentido coherente. El siguiente trabajo ya no es buscar una regla radial
universal, sino reunir fotografías oblicuas de resolución suficiente,
registrarlas contra la planta y anotar orientaciones observables con su
procedencia. La coherencia entre vecinas será una validación de esas
observaciones, no una fuente para inventar las que falten.

Su recuento rápido de **24 niveles** sobre el alzado de Almagro es compatible,
dentro de la incertidumbre del método, con las **~23 hiladas** medidas en
`docs/estratificacion.md`. No se fusionan aún ambas cifras: primero hay que
igualar la definición de nivel y los límites de la cuenta.

Ferrer aclara además que las **ocho unidades entre niveles no constan en los
manuscritos**. El 8P queda como pauta de reconstrucción moderna documentada por
Saseta y usada en los modelos de Ferrer, no como regla histórica transmitida
por Fray Andrés de San Miguel o López de Arenas.

---

## Cierre de jornada — 2026-08-25

Hecha la tarea que quedaba señalada: **las caras de la red están
identificadas, medidas y clasificadas**, y cada vecindad lleva su salto
explícitamente sin firmar.

105 caras interiores (Euler `V − E + F = 2`, cero cruces, área de caras = área
de contorno = 30,690 m²). Clasifican **25**: 8 medios cuadrados y 1 octógono
regular confirmados, 16 cuadrados marcados al límite de resolución. Las otras
**80 quedan sin figura**, 51 de ellas ni siquiera convexas. Las **227
vecindades** llevan todas `"salto": null`. Suite en **588 tests superados** y
`git diff --check` limpio.

**La propagación histórica sigue bloqueada.** El bloqueo ya no es la topología
—está completa— sino documental: falta la evidencia del signo de cada paso.
Desde la decisión 0007 existe además una nivelación aproximada separada, apta
para prototipos y explícitamente no verificada.

Estado de reanudación: `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS`.

---

## Dónde estamos

**Objetivo actual**: la **mejor reconstrucción posible** de la cúpula de
mocárabes de la Sala de las Dos Hermanas **como el día de su inauguración**
—yeso blanco de obra nueva y policromía original— con los datos que hay. Muy
aproximada, no exacta, porque las fuentes no coinciden entre sí (decisión
0008). Sigue siendo una afirmación (B) del README: empírica, sobre un estado
perdido, y por tanto sujeta a evidencia; lo que se declara más bajo es su
precisión, no su exigencia de prueba.

### Lo que está hecho y se sostiene

| pieza | estado |
|---|---|
| Núcleo aritmético en Z[ζ_m] | **sólido**, cero dependencias |
| Perfiles de celda `cuna` y `rombo` | **correctos** — la tesis los confirma como figuras A, C y D |
| Estratificación medida de la sección | **válida** — 23 hiladas, paso ~20 cm, cono de 38° ± 0.6° |
| Orden de simetría | **medido** — retícula angular 16, simetría exacta C8, espejo → D8 |
| Paleta y policromía | **medida**, con verde sostenido y rojo descartado |
| Planta de la tesis registrada | **validada** — contraste +5.43 frente a +0.16 desplazada |
| Red de medinas completa | **323 nudos, 427 aristas, 1 componente**, 24 terminales de borde |
| Representación de niveles | **implementada** — siete tipos, A3/D3 a dos niveles, propagación fail-closed |
| Sombra como indicio | **validada solo en el extremo** — 15/16 cupulines más oscuros; no calibra niveles enteros |
| Caras del teselado | **105 caras**, Euler 2, cero cruces; 9 figuras confirmadas, 16 al límite, 80 sin figura |
| Vecindades entre teselas | **227**, todas con salto sin firmar y sin conversión parcial posible |
| Reglas de nivel candidatas | **tres refutadas** con testigo sobre la propuesta de Ferrer, no sobre la cúpula |
| Tamaño del salto de nivel | **8 unidades**, pauta moderna documentada por Saseta y usada por Ferrer; no consta en los manuscritos |
| Teorema del triángulo | **54 triángulos** (16 robustos = 8 pares espejo, N estricto 6): la planta exige descansos o piezas de dos niveles |
| Nivelación aproximada | **disponible** — 105 caras, 227 saltos, niveles 0–7 y sensibilidad 7/8 explícita |
| Altura de cada banda | **calibrada** contra la sección — 6 bandas en las hiladas 6, 11, 13, 17, 19 y 23; cima exacta en 4,67 m |
| Plantilla de doble perfil | **implementada** — mayor 7P en quintos, menor 7,5P en séptimos, nivel a 8P; exacta en `Fraction` |
| Malla 3D | **exportable y mirada** — `renders/cupula_aproximada.obj`, 105 celdas, rms 0,234 m frente al cono |

### Lo que había que tirar — hecho

Retirado el 2026-08-29 en la decisión 0011, una vez que el sustituto funciona:
la estratificación por **coronas polares** entera, la celda **`trapecio`** que me
inventé, y la geometría que colgaba del **perfil de cónica única**
(`PuntoMalla`, `malla_adaraja`, `numeric_embedding_punto`), con sus tests.

Sobrevive la **cónica racional**, que no era el error: el error era usarla como
modelo de la pieza. Como interpolador exacto sigue valiendo, así que el módulo
pasa de `adaraja.py` a `granada/conica.py` —el nombre viejo prometía un modelo
que ya no contiene— y se queda **sin frontera numérica**: exacto de punta a
punta.

Dos colisiones de nombres resueltas al pasar, y las dos eran ambigüedades
reales: `Plantilla` significaba figura de planta y perfil de pieza a la vez —la
segunda es ahora `PlantillaPerfil` en `granada/perfil.py`—, y la función `celda`
**sombreaba el módulo `granada.celda`** al exportarla; lo cazó un test que dejó
de encontrar lo que inspeccionaba. Es `pieza`, que hace pareja con `corona`.

## Tarea del nivel de cada tesela: estado

Es lo que convierte una planta en cúpula, y es lo que falta.

**Dificultad conocida**: las piezas **A3 y D3 abarcan dos niveles** (medios
cuadrados y jairas «de dos niveles»). El nivel no es una función de la tesela;
es una función de la tesela *y* su topología.

Vías posibles, por orden de coste:

1. **Deducirlo de la sombra en la ortoimagen.** La profundidad de cada celda se
   correlaciona con su luminancia: las celdas hondas están en sombra. Con las
   16 copias simétricas agrupadas hay señal suficiente para intentarlo. Barato
   y usa datos que ya tengo.
2. **Deducirlo de la topología de la red.** Si las medinas separan niveles
   consecutivos, el nivel se propaga por el grafo desde el borde. La red está
   completa y las caras y vecindades ya están identificadas; lo que falta —y
   la topología por sí sola no da— es el signo/salto de cada paso.
3. **Leerlo de la tesis.** El capítulo 3 propone una representación de plantas
   con líneas de nivel y con puntos, precisamente para esto. Mirar
   `3.2.5 Plantas con líneas de nivel` y `3.3.2 Planta propuesta`.

### Hecho

- Identificadas las **caras** por rotación de semiaristas (`granada/caras.py`,
  sin dependencias): 105 caras, Euler `V − E + F = 2`, cero cruces en los
  90 951 pares de aristas y área de caras igual a la del contorno. Clasificadas
  solo contra las plantillas documentadas y con la tolerancia que impone la
  resolución del dibujo: 8 medios cuadrados y 1 octógono confirmados (órbita
  C8 exacta, margen 3,9× y 6,5× frente a las plantillas de control), 16
  cuadrados al límite de resolución y 80 caras sin figura. Decisión y controles
  en `docs/decisiones/0005-caras-y-vecindades.md`.
- Refutadas tres reglas de nivel candidatas sobre el dual de 105 caras, 211
  vecindades y 107 ciclos: «toda medina salva un nivel» es imposible porque el
  grafo no es bipartito; «se sube uno hacia el centro» rompe 67 ciclos;
  «ortogonales suben, diagonales descansan», otros 67. Los dos controles
  positivos pasan, así que el test no rechaza por costumbre. Aguanta descartar
  toda medina compartida de menos de 30 px. Decisión 0006.
- **Teorema del triángulo**: en tres teselas mutuamente vecinas los tres saltos
  no pueden valer ±1, porque una suma impar no cierra en cero. Hay 54
  triángulos, 16 de ellos robustos. La planta exige por sí sola descansos o
  piezas de dos niveles — justo lo que la tesis documenta como A3, D3 y
  descansos. Es topología pura: ni fotometría, ni radio, ni suposición de
  altura.
- Representadas las **227 vecindades** con `salto = None`. Firmar exige citar
  evidencia y `restricciones_firmadas` falla mientras quede una sin firmar: no
  hay propagación parcial que aparente una planta resuelta.
- Leídas directamente `3.2.5 Plantas con líneas de nivel` y `3.3.2 Planta
  propuesta`, incluidas las figuras 28–29. La planta propuesta codifica
  sentido, tipología y niveles de ascenso con **una o varias flechas dentro de
  cada figura**; una arista compartida no tiene por qué tener un sentido único.
- Implementado `granada/niveles.py`: separa tipo/topología, nivel absoluto y
  restricciones entre nodos. Detecta ciclos contradictorios y deja componentes
  sin ancla sin resolver. A3 y D3 salvan dos niveles.
- Contrastada la sombra sobre los 16 cupulines conocidos: 15/16 son más oscuros
  que controles al mismo radio, diferencia mediana +16,99, p=3,05·10⁻⁵. La
  señal existe, pero la sensibilidad radial y los confundidores impiden una
  función brillo → nivel.
- Completada la red desde la mitad superior de la figura 128 —la propuesta de
  la tesis— y reflexión D8, sin mezclar la mitad inferior de Jones y Goury:
  323 nudos, 427 aristas, una componente, 105 ciclos y 24 terminales de borde.
  El resultado es idéntico para umbrales 170–230. Procedimiento y techo de
  afirmación en `docs/decisiones/0004-red-medinas-completa.md`.

### Bloqueo documental de las restricciones

La figura 128 específica de Dos Hermanas **no contiene las flechas ni cotas**
de la representación propuesta. La red ya es conexa, pero conectividad no
equivale a una diferencia de nivel: falta identificar las caras y codificar en
cada paso si hay ascenso, descanso o descenso.

`BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS`

No presentar niveles por brillo, radio o distancia de grafo como datos
observados. Las teselas ya están identificadas y sus 227 vecindades listadas:
lo único que falta para la versión histórica es el signo de cada paso. La
decisión 0007 autoriza la distancia de grafo únicamente como hipótesis de
trabajo separada en `datos/niveles_aproximados.json`.

**Atajos ya cerrados por escrito** (decisión 0006): un nivel por medina, el
ascenso hacia el centro y el reparto ortogonal/diagonal son imposibles sobre
esta planta, con ciclo testigo cada uno. No volver a proponerlos.

**Confirmación externa del bloqueo (2026-08-25).** El informe documental de la
entrada 8 de `docs/fuentes.md` vació Dialnet, TESEO, Digibug, RiuNet, APAG,
RABASF e IAPH y concluye que **no existe en el dominio público ninguna tabla
que asocie cada pieza a una cota**. El bloqueo no es un fallo de búsqueda.

**El tamaño del salto ya está como hipótesis moderna, el signo no.** Saseta
Velázquez (2016) da «la pauta para la elevación entre un nivel y otro de
adarajas es de 8 unidades», que coincide con el 8P usado en la plantilla de
doble perfil de Ferrer. Ferrer aclara en su respuesta del 2026-08-28 que ese
número no está escrito en los manuscritos: procede de deducciones posteriores
o medidas empíricas. Por tanto, 8P es un parámetro documentado de
reconstrucción, no una constante histórica demostrada. Y el tamaño de un salto
no es su signo.

**Dónde puede salir el signo**, por orden de coste:

1. **Fotografías oblicuas de alta resolución**, registradas contra la planta.
   Ferrer confirma que el sentido se deduce eficazmente de fotografías y que
   las piezas vecinas han de ser coherentes. Cada orientación anotada deberá
   conservar imagen, región y criterio de lectura; la coherencia solo valida,
   no rellena observaciones ausentes.
2. Una planta de Dos Hermanas —de la tesis o de otro autor— que traiga flechas
   o cotas. Es lo que la sección 3.3.2 propone y la figura 128 no aplica. La
   cuarta imagen del ejercicio docente de Ferrer de 2023 muestra el método de
   flechas y líneas de nivel, pero no aporta la solución de Dos Hermanas.
3. La sección medida: `docs/estratificacion.md` da 23 hiladas y paso ~20 cm.
   Una cara cuyo radio y cota se puedan casar con una hilada firmaría su ancla,
   no sus vecindades. Cuidado: es la propagación por coronas por otro camino.
4. La capa vectorial de AA-415_23. Comprobado que existe —AutoCAD 2010, A0,
   con `/OCProperties` y `/OCGs`— pero el plano **no lleva cotas escritas**: 20
   palabras de texto en todo el A0. Da un perfil medible contra la escala 1/25,
   no niveles por tesela; y una sección no puede firmar 211 vecindades en
   planta.
5. **Las 104 adarajas de estrella del PMAA — localizadas** (entrada 10 de
   `fuentes.md`). No están en el impreso de *Revista PH* 106 sino en la versión
   web del mismo artículo, como **pie de una figura**: 104 piezas sobre
   ortofotografía cenital, en 5 tipos. Es imagen, no tabla, y sin método
   publicado. Y *Revista PH* va con licencia **CC BY-NC-ND**: se puede citar,
   **no derivar geometría**. Si hiciera falta como dato, se pide permiso al
   autor.

---

## Después

- **Completar la red — hecho.** El seguimiento de esqueleto conserva los giros
  y elimina el contorno punteado: 323 nudos y 427 aristas en una componente.
- **Identificar caras y restricciones — hecho.** 105 caras, 25 clasificadas
  (9 confirmadas), 227 vecindades con el salto explícitamente sin firmar.
  Ninguna cara recibe `TipoMocarabe`: de la planta se lee la figura, no la
  topología.
- **Firmar los saltos — siguiente tarea.** Es documental, no de código: hace
  falta una fuente que diga, para cada paso, si asciende, descansa o
  desciende.
- **Módulos mixtos.** Confirmado que esta cúpula no tiene módulo único
  (residuo del 18–23 % con el mejor módulo). El modelo tiene que admitir
  piezas de distinto módulo, no forzar uno.
- **Doble perfil.** Rehacer `adaraja.py` con las dos plantillas y la regla de
  paralelismo entre vecinas.
- **Levantar y renderizar.** Ya puede hacerse un prototipo con
  `datos/niveles_aproximados.json`, rotulado como aproximado y mostrando la
  sensibilidad 7/8. La versión histórica seguirá esperando validación sobre
  fotografías. **No presentar el prototipo como reconstrucción verificada.**
- **Página interactiva.** Es el destino acordado: cúpula girable, selector de
  orden y controles de color. Queda para el final.

---

## TODO abiertos, sin inventar

- **Los «siete niveles» de Martínez Sevilla.** La prensa de la exposición del
  PMAA le atribuye el hallazgo de que la cúpula tiene siete niveles, que
  evocarían los del Salón del Trono. No hay publicación con método detrás, no
  se dice si cuenta niveles de adarajas de estrella o del mocárabe completo, y
  la sección medida da 23 hiladas. Queda anotado en la entrada 10 como
  afirmación de terceros, fechada y localizada; **no se usa como cota**.
- **El oro.** Documentado en yeserías nazaríes —letras doradas sobre fondo azul
  lapislázuli en el Mexuar, 1362— pero **nada específico de esta cúpula**. Su
  tono (40–60°) es indistinguible de la suciedad en la ortoimagen. Haría falta
  una fuente con análisis de pigmento in situ.
- **El rojo.** Descartado con *esta* imagen: su periodicidad angular queda por
  debajo de la línea base del propio yeso. Que el bermellón formaba parte de la
  paleta nazarí está documentado; que estuviera *aquí*, y dónde, no.
- **El negro carbón.** Indistinguible de la sombra de las cavidades.
- **Referencias del informe de altimetría, verificación parcial hecha**
  (2026-08-25). Comprobadas: la tesis de Ferrer, Saseta Velázquez 2016 —leída
  entera, ahora entrada 9—, Roldán-Medina 2018 y *Revista PH* 106, que existe
  pero **no contiene lo que se le atribuía**. Quedan las signaturas P-000159 y
  D-0353 del APAG, los inventarios 006601 y 006091 del Museo y MakerWorld
  3150958.
- **Las 80 caras sin figura.** Se agrupan por área en familias de 16, 24, 8, 8,
  8 y 16 copias, así que son regiones reales del dibujo, no ruido. La figura
  128 no las subdivide; una planta más fina de esta cúpula las resolvería.
- **Las nueve filas restantes** de la tabla de planos del APAG en
  `docs/investigacion-preliminar.md`, sin verificar.
- **La capa vectorial** de AA-415_23, sin extraer. Daría geometría en vez de
  fotometría para la medición del orden de simetría.
- **Heritage 6(12) 388** (cúpula de la Sala de los Reyes): existencia
  verificada, contenido sin leer — MDPI devuelve 403.

---

## Cautelas que no hay que perder

1. **Z[ζ₁₆] es denso en el plano.** No es una retícula. Cualquier test de
   «ajuste a la retícula» sin acotar coeficientes es vacío: comprobado que con
   coeficientes de hasta 40 unos puntos aleatorios ajustan igual de bien que
   los reales. **Todo test lleva control.**
2. **Validar la planta antes de renderizar.** El primer render salió feo por
   modelar una superficie de revolución corrugada en vez de un teselado, y se
   descubrió tarde porque nunca se comparó la planta contra la ortoimagen.
3. **La razón diagonal/ortogonal medida (0.7679 contra √(2−√2) = 0.7654)** es
   más precisa de lo que el método merece. Defendible: vale ~0.77, no 1 ni √2.
4. **Derechos.** Las figuras de la tesis son obra de su autor y **no se
   redistribuyen** aquí; se citan y se usan como referencia para construir
   geometría propia. El plano AA-415_23 es material de la RABASF: leerlo para
   verificar es legítimo, derivar geometría para un repo MIT exige revisar sus
   condiciones **antes**.
5. **El espejo de la red se impuso, no se midió.** La mitad inferior de
   `datos/red_medinas.json` es reflexión de la superior. De ahí dos reglas: la
   red **nunca** sirve como evidencia de la simetría especular —sería
   circular—, y al contar instancias hay que clasificarlas **por vértices**
   antes de dar un N: una cara que cruza el eje depende del pegado. Los 16
   triángulos robustos son 8 pares, y solo **6** tienen las tres caras
   digitalizadas: N estricto = 6. De las 8 caras de medio cuadrado, 3. De los
   16 cuadrados, 8. El octógono central, ninguna.
6. **Lo refutado lo es sobre el dibujo de Ferrer, no sobre la cúpula.** Si el
   autor replicó un sector en CAD, las 16 apariciones son una decisión del
   dibujante y ningún tratamiento del ráster lo distingue. La refutación de las
   tres reglas hereda el techo de la decisión 0004, no uno más fuerte.
7. **La cúpula real está deformada.** Los escaneos láser lo documentan en otras
   salas, y aquí se nota en el emborronamiento al promediar las 16 copias.
   Cualquier afirmación (B) es «ajusta dentro de una tolerancia», nunca
   «reproduce».
